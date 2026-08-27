"""
Kasiyersiz Akilli Kasa Sistemi - Masaustu Surumu
Modul C: Canli Tarama  |  Modul D: Fiyatlandirma

Kamerayi acar, Roboflow modeliyle urunleri tespit eder,
filtreyi gecenleri isaretler ve anlik sepet toplamini gosterir.

Web arayuzunun (arayuz/app.py) tek pencerelik karsiligidir; ikisi de ayni
tespit hattini kasa/ paketinden kullanir.

Kullanim:
    python akilli_kasa.py
Cikis:
    'q' tusuna basin.
"""

import cv2

from kasa import araclar, ayarlar, cizim, tespit

ayarlar.anahtari_dogrula()

araclar.gunlugu_kur()
kayit = araclar.gunlukcu("masaustu")

PENCERE_ADI = "Akilli Kasa - Canli Tarama"
CIKIS_TUSU = "q"


def kamera_ac():
    """
    Varsayilan kamerayi acar.

    Acilamazsa None doner; cagiran tarafin bunu kontrol etmesi beklenir.
    """
    kamera = cv2.VideoCapture(ayarlar.KAMERA_INDEKSI)

    if not kamera.isOpened():
        kayit.error(
            "Kamera acilamadi (indeks %s). Kamera baglantisini kontrol edin.",
            ayarlar.KAMERA_INDEKSI,
        )
        return None

    return kamera


def kareyi_isle(kare, istemci) -> float:
    """
    Tek kareyi modele gonderir, tespitleri kare uzerine cizer.

    Kare yerinde degistirilir. Donen deger o karedeki sepet toplamidir.
    """
    sonuclar = istemci.infer(kare, model_id=ayarlar.MODEL_ID)
    tespitler = tespit.tespitleri_filtrele(sonuclar)

    cizim.tespitleri_ciz(kare, tespitler)

    toplam = tespit.sepet_toplami(tespitler)
    cizim.toplam_yaz(kare, toplam)

    return toplam


def main():
    """Kamera dongusunu calistirir; 'q' tusuna basilana kadar surer."""
    kamera = kamera_ac()
    if kamera is None:
        return

    istemci = tespit.istemci_olustur()
    kayit.info("Kamera acildi. Cikmak icin '%s' tusuna basin.", CIKIS_TUSU)

    while True:
        basari, kare = kamera.read()
        if not basari:
            kayit.warning("Kare okunamadi, atlaniyor...")
            continue

        kareyi_isle(kare, istemci)
        cv2.imshow(PENCERE_ADI, kare)

        if cv2.waitKey(1) & 0xFF == ord(CIKIS_TUSU):
            kayit.info("Cikis yapiliyor...")
            break

    kamera.release()
    cv2.destroyAllWindows()
    kayit.info("Kamera kapatildi. Program sonlandi.")


if __name__ == "__main__":
    main()
