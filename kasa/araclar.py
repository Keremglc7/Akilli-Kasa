"""
Ortak yardimcilar: gunluk kaydi ve konsol basligi.

Onceden her script kendi print() etiketlerini kullaniyordu ([HATA], [OK],
[KAMERA], [MODEL] ...). Bunlarin bir kismi seviye, bir kismi modul adiydi ve
hicbiri susturulabilir, zaman damgalanabilir ya da dosyaya yonlendirilebilir
degildi. Artik hepsi standart logging uzerinden gecer.
"""

import logging
import sys

BASLIK_GENISLIGI = 60


def gunlugu_kur(seviye: int = logging.INFO) -> None:
    """
    Kok gunlukcuyu tek satirlik, okunakli bir bicimle hazirlar.

    Uygulama girisinde bir kez cagrilir. Zaten yapilandirilmissa
    (ornegin baska bir modul kurmussa) tekrar kurmaz.
    """
    if logging.getLogger().handlers:
        return

    # Windows konsolunda Turkce karakterlerin bozulmamasi icin.
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass

    logging.basicConfig(
        level=seviye,
        format="%(asctime)s  %(levelname)-7s %(name)-14s %(message)s",
        datefmt="%H:%M:%S",
    )


def gunlukcu(ad: str) -> logging.Logger:
    """Modul icin 'kasa.<ad>' adli gunlukcu dondurur."""
    return logging.getLogger(f"kasa.{ad}")


def baslik_yaz(*satirlar: str, genislik: int = BASLIK_GENISLIGI) -> None:
    """
    Konsola cizgiler arasinda bir baslik blogu basar.

    Kullanici arayuzu metni oldugu icin bilerek print() kullanir; gunluk
    kayitlarina karismamasi gerekir.
    """
    print("=" * genislik)
    for satir in satirlar:
        print(f"  {satir}")
    print("=" * genislik)
