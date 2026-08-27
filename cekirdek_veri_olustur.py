"""
kareler klasöründeki her alt klasörden her 10. kareyi seçip
cekirdek_veri klasörüne kopyalar (etiketleme başlangıç seti).

Kullanım:
    python cekirdek_veri_olustur.py
"""

import os
import shutil

from kasa import araclar

araclar.gunlugu_kur()
kayit = araclar.gunlukcu("cekirdek_veri")

ANA_DIZIN = os.path.dirname(os.path.abspath(__file__))
KARELER_KLASORU = os.path.join(ANA_DIZIN, "kareler")
CEKIRDEK_KLASORU = os.path.join(ANA_DIZIN, "cekirdek_veri")

# kare_cikar.py kareleri <urun>_001.jpg ... <urun>_150.jpg olarak adlandirir.
# Buradan her 10. kareyi aliyoruz: 150 kareden 15 cekirdek kare.
# Secim dosya adindaki sirayi ayristirarak yapilir; "0.jpg ile biten" gibi bir
# metin numarasi, kare sayisi degistiginde sessizce yanlis sonuc verirdi.
SECIM_ARALIGI = 10


def kare_sirasi(dosya_adi: str):
    """
    Dosya adinin sonundaki kare sirasini dondurur; ayristirilamazsa None.

    Ornek: "dido_070.jpg" -> 70
    """
    govde = os.path.splitext(dosya_adi)[0]
    _, ayirac, sira_metni = govde.rpartition("_")

    if not ayirac or not sira_metni.isdigit():
        return None

    return int(sira_metni)


def cekirdek_kareleri_sec(kaynak_klasor: str) -> list:
    """Klasordeki karelerden her SECIM_ARALIGI'ncisini secip sirali dondurur."""
    secilenler = []

    for dosya_adi in os.listdir(kaynak_klasor):
        if not dosya_adi.lower().endswith(".jpg"):
            continue

        sira = kare_sirasi(dosya_adi)
        if sira is not None and sira % SECIM_ARALIGI == 0:
            secilenler.append(dosya_adi)

    return sorted(secilenler)


def main():
    """kareler/ altindaki her urun klasorunden cekirdek kareleri kopyalar."""
    araclar.baslik_yaz("CEKIRDEK VERI OLUSTURMA ARACI")

    if not os.path.isdir(KARELER_KLASORU):
        kayit.error("kareler klasoru bulunamadi: %s", KARELER_KLASORU)
        return

    alt_klasorler = sorted([
        klasor_adi for klasor_adi in os.listdir(KARELER_KLASORU)
        if os.path.isdir(os.path.join(KARELER_KLASORU, klasor_adi))
    ])

    if not alt_klasorler:
        kayit.error("kareler klasorunde alt klasor bulunamadi.")
        return

    kayit.info("%d alt klasor bulundu.", len(alt_klasorler))

    os.makedirs(CEKIRDEK_KLASORU, exist_ok=True)

    toplam_kopyalanan = 0

    for klasor_adi in alt_klasorler:
        kaynak = os.path.join(KARELER_KLASORU, klasor_adi)
        hedef = os.path.join(CEKIRDEK_KLASORU, klasor_adi)
        os.makedirs(hedef, exist_ok=True)

        dosyalar = cekirdek_kareleri_sec(kaynak)
        kayit.info("[%s] %d kare secildi -> kopyalaniyor...", klasor_adi, len(dosyalar))

        for dosya_adi in dosyalar:
            shutil.copy2(
                os.path.join(kaynak, dosya_adi),
                os.path.join(hedef, dosya_adi),
            )

        toplam_kopyalanan += len(dosyalar)

    araclar.baslik_yaz(
        f"Toplam kopyalanan dosya: {toplam_kopyalanan}",
        f"Hedef klasor: {CEKIRDEK_KLASORU}",
    )


if __name__ == "__main__":
    main()
