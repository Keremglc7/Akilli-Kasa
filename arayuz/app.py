"""
Kasiyersiz Akilli Kasa Sistemi - Flask Web Arayuzu (Backend)
=============================================================
Kamera okuma ve Roboflow cikarimlari ayri thread'lerde calisir.
Video akisi MJPEG olarak sunulur, sepet verisi JSON API uzerinden alinir.

Tespit hatti (fiyatlar, filtreleme, cizim) kasa/ paketinden gelir; bu dosya
yalnizca thread yonetimi ve HTTP uclarindan sorumludur.

Kullanim:
    cd arayuz
    python app.py
"""

import os
import sys
import threading
import time
from collections import Counter

import cv2
from flask import Flask, render_template, Response, jsonify

# Bu dosya arayuz/ altinda calistigi icin proje kokunu import yoluna ekliyoruz;
# aksi halde kardes dizindeki kasa/ paketi bulunamaz.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kasa import araclar, ayarlar, cizim, tespit, urunler  # noqa: E402

ayarlar.anahtari_dogrula()

araclar.gunlugu_kur()
kayit = araclar.gunlukcu("sunucu")

# ═══════════════════════════════════════════════════════════════════════
# PAYLASILAN DURUM (Thread-safe erisim icin kilit kullanilir)
# ═══════════════════════════════════════════════════════════════════════
kare_kilidi   = threading.Lock()  # son_kare icin kilit
tespit_kilidi = threading.Lock()  # guncel_tespitler icin kilit

son_kare         = None  # Kameradan gelen son kare
guncel_tespitler = []    # Filtrelenmis tespit listesi
calisiyor        = True  # Thread'leri durdurmak icin bayrak


def son_kareyi_al():
    """
    Son kamera karesinin kopyasini kilit altinda dondurur.

    Kopya donulur cunku cagiran uzerine cizim yapar; orijinali degistirmek
    kamera thread'i ile yarisa girer. Henuz kare yoksa None doner.
    """
    with kare_kilidi:
        return son_kare.copy() if son_kare is not None else None


def son_tespitleri_al() -> list:
    """Guncel tespit listesinin kopyasini kilit altinda dondurur."""
    with tespit_kilidi:
        return list(guncel_tespitler)


# ═══════════════════════════════════════════════════════════════════════
# THREAD 1: KAMERA OKUMA (Kesintisiz, yuksek FPS)
# ═══════════════════════════════════════════════════════════════════════
def camera_worker():
    """Kamerayi acar ve surekli kare okur. API beklemez, donmaz."""
    global son_kare, calisiyor

    kamera = cv2.VideoCapture(ayarlar.KAMERA_INDEKSI)
    kamera.set(cv2.CAP_PROP_FRAME_WIDTH, ayarlar.KAMERA_GENISLIK)
    kamera.set(cv2.CAP_PROP_FRAME_HEIGHT, ayarlar.KAMERA_YUKSEKLIK)
    kamera.set(cv2.CAP_PROP_BUFFERSIZE, ayarlar.KAMERA_TAMPON_BOYUTU)

    if not kamera.isOpened():
        kayit.error("Kamera acilamadi (indeks %s).", ayarlar.KAMERA_INDEKSI)
        calisiyor = False
        return

    kayit.info("Kamera basariyla acildi.")

    while calisiyor:
        basari, kare = kamera.read()
        if not basari:
            continue
        with kare_kilidi:
            son_kare = kare

    kamera.release()
    kayit.info("Kamera kapatildi.")


# ═══════════════════════════════════════════════════════════════════════
# THREAD 2: ROBOFLOW API CIKARIMI (Arka planda, bagimsiz)
# ═══════════════════════════════════════════════════════════════════════
def inference_worker():
    """Son kareyi alip Roboflow API'ye gonderir, sonuclari gunceller."""
    global guncel_tespitler

    istemci = tespit.istemci_olustur()
    kayit.info("Roboflow istemcisi olusturuldu. Cikarim basliyor...")

    while calisiyor:
        kare = son_kareyi_al()

        if kare is None:
            time.sleep(ayarlar.KARE_BEKLEME_SN)
            continue

        try:
            sonuclar = istemci.infer(kare, model_id=ayarlar.MODEL_ID)
            filtrelenmis = tespit.tespitleri_filtrele(sonuclar)

            with tespit_kilidi:
                guncel_tespitler = filtrelenmis

        except Exception as hata:
            kayit.error("Cikarim basarisiz: %s", hata)

        # API'yi asiri yuklememek icin kucuk bekleme.
        time.sleep(ayarlar.CIKARIM_ARALIGI_SN)


# ═══════════════════════════════════════════════════════════════════════
# MJPEG VIDEO AKISI URETECI
# ═══════════════════════════════════════════════════════════════════════
def generate_frames():
    """Kare + tespit kutularini birlestirip MJPEG olarak akar."""
    while calisiyor:
        kare = son_kareyi_al()

        if kare is None:
            time.sleep(ayarlar.CIKARIM_ARALIGI_SN)
            continue

        cizim.tespitleri_ciz(kare, son_tespitleri_al())

        basari, tampon = cv2.imencode(
            ".jpg", kare, [cv2.IMWRITE_JPEG_QUALITY, ayarlar.JPEG_KALITESI]
        )
        if not basari:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + tampon.tobytes() + b"\r\n"
        )

        time.sleep(ayarlar.AKIS_KARE_ARALIGI_SN)


# ═══════════════════════════════════════════════════════════════════════
# FLASK UYGULAMASI
# ═══════════════════════════════════════════════════════════════════════
app = Flask(__name__)


@app.route("/")
def index():
    """Ana sayfa: web arayuzunu sunar."""
    return render_template("index.html", sepet_sorgu_ms=ayarlar.SEPET_SORGU_MS)


@app.route("/video_feed")
def video_feed():
    """MJPEG video akisi endpoint'i."""
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/api/sepet")
def sepet():
    """
    Anlik sepet verisi (JSON).

    Ayni siniftan birden fazla tespit tek satirda adetlenir. Frontend bu ucu
    ayarlar.SEPET_SORGU_MS araligiyla sorgular.
    """
    tespitler = son_tespitleri_al()
    sayim = Counter(tespit_kaydi["sinif"] for tespit_kaydi in tespitler)

    satirlar = []
    toplam = 0.0

    for sinif, adet in sayim.items():
        birim_fiyat = urunler.fiyat_al(sinif)
        ara_toplam = birim_fiyat * adet
        toplam += ara_toplam

        satirlar.append({
            "sinif":       sinif,
            "ad":          urunler.gorunen_ad(sinif),
            "birim_fiyat": birim_fiyat,
            "adet":        adet,
            "ara_toplam":  round(ara_toplam, 2),
        })

    satirlar.sort(key=lambda satir: satir["ad"])

    return jsonify({
        "urunler":     satirlar,
        "toplam":      round(toplam, 2),
        "toplam_adet": sum(sayim.values()),
    })


# ═══════════════════════════════════════════════════════════════════════
# BASLANGIC
# ═══════════════════════════════════════════════════════════════════════
def main():
    """Arka plan thread'lerini baslatir ve Flask sunucusunu calistirir."""
    # daemon=True: ana program kapaninca thread'ler de durur.
    threading.Thread(target=camera_worker, daemon=True).start()
    threading.Thread(target=inference_worker, daemon=True).start()

    kayit.info(
        "Flask sunucusu baslatiliyor: http://%s:%s",
        ayarlar.SUNUCU_HOST,
        ayarlar.SUNUCU_PORT,
    )
    app.run(
        host=ayarlar.SUNUCU_HOST,
        port=ayarlar.SUNUCU_PORT,
        debug=False,
        threaded=True,
    )


if __name__ == "__main__":
    main()
