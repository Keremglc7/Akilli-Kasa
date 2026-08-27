"""
Veri seti klasöründeki tüm .mp4 videolardan eşit aralıklarla
tam 150 adet kare çıkarıp kaydeden script.

Kullanım:
    python kare_cikar.py
"""

import os
import glob

import numpy as np
import cv2

from kasa import araclar

araclar.gunlugu_kur()
kayit = araclar.gunlukcu("kare_cikar")


# ── Ayarlar ──────────────────────────────────────────────────────────
ANA_DIZIN = os.path.dirname(os.path.abspath(__file__))

HEDEF_KARE_SAYISI = 150
VERI_SETI_KLASORU = os.path.join(ANA_DIZIN, "veri_seti")
KARELER_KLASORU   = os.path.join(ANA_DIZIN, "kareler")

# İlerleme her %5'te bir loglanır: 150 / 20 = 7.5 -> her 7 karede bir.
ILERLEME_ADIMI = max(1, HEDEF_KARE_SAYISI // 20)
# ─────────────────────────────────────────────────────────────────────


def imwrite_unicode(dosya_yolu: str, img: np.ndarray) -> bool:
    """cv2.imwrite Unicode yol destegi olmadigi icin imencode + write kullanir."""
    uzanti = os.path.splitext(dosya_yolu)[1]
    basari, buf = cv2.imencode(uzanti, img)
    if not basari:
        return False
    with open(dosya_yolu, "wb") as f:
        f.write(buf.tobytes())
    return True


def video_bilgisi_al(video_yolu: str) -> tuple:
    """Video dosyasindan FPS, toplam kare sayisi ve sure bilgisini dondurur."""
    cap = cv2.VideoCapture(video_yolu)
    if not cap.isOpened():
        raise IOError(f"Video acilamadi: {video_yolu}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    toplam_kare = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sure_saniye = toplam_kare / fps if fps > 0 else 0

    return cap, fps, toplam_kare, sure_saniye


def kareleri_cikar(video_yolu: str, kayit_klasoru: str) -> None:
    """Bir videodan esit araliklarla HEDEF_KARE_SAYISI kadar kare cikarir."""
    video_adi = os.path.splitext(os.path.basename(video_yolu))[0]

    # Video bilgilerini al
    cap, fps, toplam_kare, sure_saniye = video_bilgisi_al(video_yolu)

    kayit.info(
        "%s | FPS: %.2f | Toplam kare: %d | Sure: %.2f sn",
        video_adi, fps, toplam_kare, sure_saniye,
    )

    # Toplam kare sayisi hedeften azsa uyari ver
    if toplam_kare < HEDEF_KARE_SAYISI:
        kayit.warning(
            "%s: toplam kare sayisi (%d) hedeften (%d) az, atlaniyor.",
            video_adi, toplam_kare, HEDEF_KARE_SAYISI,
        )
        cap.release()
        return

    # Kare atlama degerini hesapla (esit araliklarla dagitim)
    atlama = toplam_kare / HEDEF_KARE_SAYISI

    # Alt klasoru olustur
    os.makedirs(kayit_klasoru, exist_ok=True)

    kaydedilen = 0
    for i in range(HEDEF_KARE_SAYISI):
        # Hedef kare indeksini hesapla
        hedef_indeks = int(i * atlama)
        cap.set(cv2.CAP_PROP_POS_FRAMES, hedef_indeks)

        basari, kare = cap.read()
        if not basari:
            kayit.warning("Kare okunamadi: indeks %d", hedef_indeks)
            continue

        # Dosya adi: video_adi_001.jpg, video_adi_002.jpg, ...
        dosya_adi = f"{video_adi}_{i + 1:03d}.jpg"
        dosya_yolu = os.path.join(kayit_klasoru, dosya_adi)

        # Yazma basarisizsa sayaci artirmiyoruz; aksi halde ozet satiri
        # diske hic inmemis kareleri kaydedilmis gibi gosterirdi.
        if imwrite_unicode(dosya_yolu, kare):
            kaydedilen += 1
        else:
            kayit.warning("Kare diske yazilamadi: %s", dosya_adi)
            continue

        # İlerleme logu (%5 aralıklarla ve son karede)
        if (i + 1) % ILERLEME_ADIMI == 0 or (i + 1) == HEDEF_KARE_SAYISI:
            yuzde = (i + 1) / HEDEF_KARE_SAYISI * 100
            kayit.info(
                "    İlerleme: %%%5.1f  (%d/%d kare)",
                yuzde, kaydedilen, HEDEF_KARE_SAYISI,
            )

    cap.release()
    kayit.info("%s -> %d kare kaydedildi.", video_adi, kaydedilen)


def main():
    """veri_seti/ altindaki her videodan kareleri cikarip kareler/ altina yazar."""
    araclar.baslik_yaz(
        "KARE ÇIKARMA ARACI",
        f"Hedef: Her videodan {HEDEF_KARE_SAYISI} kare",
    )

    # Veri seti klasörü kontrolü
    if not os.path.isdir(VERI_SETI_KLASORU):
        kayit.error("Veri seti klasoru bulunamadi: %s", VERI_SETI_KLASORU)
        return

    # .mp4 dosyalarını bul (büyük/küçük harf duyarsız)
    videolar = sorted(
        glob.glob(os.path.join(VERI_SETI_KLASORU, "*.[mM][pP]4"))
    )

    if not videolar:
        kayit.error("veri_seti klasorunde .mp4 dosyasi bulunamadi.")
        return

    kayit.info("%d adet video bulundu.", len(videolar))

    # Ana kareler klasörünü oluştur
    os.makedirs(KARELER_KLASORU, exist_ok=True)

    for sira, video_yolu in enumerate(videolar, start=1):
        video_adi = os.path.splitext(os.path.basename(video_yolu))[0]
        alt_klasor = os.path.join(KARELER_KLASORU, video_adi)

        kayit.info("[%d/%d] İşleniyor...", sira, len(videolar))
        kareleri_cikar(video_yolu, alt_klasor)

    araclar.baslik_yaz(
        "Tum videolar basariyla islendi!",
        f"Cikti klasoru: {KARELER_KLASORU}",
    )


if __name__ == "__main__":
    main()
