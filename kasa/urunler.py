"""
Taninan urunler: model sinif adi -> fiyat ve gorunen isim.

Model yeni bir sinif ogrendiginde her iki sozluge de eklenmelidir;
FIYATLAR ayni zamanda beyaz liste gorevi gorur (bkz. tespit.py).
"""

# ── Urun fiyatlari (TL) ──────────────────────────────────────────────
FIYATLAR = {
    "biscolata_stix":    15.50,
    "burcak_cikolatali": 18.00,
    "crax_aci":           9.00,
    "crax_lime":          9.00,
    "dido":              12.00,
    "lipton_seftali":    20.00,
    "nescafe_vanilya":   25.00,
    "patos_rolls":       22.50,
    "ulker_gofret":      10.00,
}

# ── Arayuzde gosterilen Turkce isimler ───────────────────────────────
URUN_ISIMLERI = {
    "biscolata_stix":    "Biscolata Stix",
    "burcak_cikolatali": "Burçak Çikolatalı",
    "crax_aci":          "Crax Acı Biber",
    "crax_lime":         "Crax Lime",
    "dido":              "Dido",
    "lipton_seftali":    "Lipton Şeftali",
    "nescafe_vanilya":   "Nescafe Vanilya",
    "patos_rolls":       "Patos Rolls",
    "ulker_gofret":      "Ülker Gofret",
}


def taniniyor_mu(sinif: str) -> bool:
    """Verilen model sinifinin fiyat listesinde olup olmadigini soyler."""
    return sinif in FIYATLAR


def fiyat_al(sinif: str) -> float:
    """Sinifin birim fiyatini dondurur; taninmayan sinif icin 0.0."""
    return FIYATLAR.get(sinif, 0.0)


def gorunen_ad(sinif: str) -> str:
    """
    Sinifin arayuzde gosterilecek Turkce adini dondurur.

    Isim tanimli degilse ham sinif adina duser; boylece modele yeni bir
    urun eklendiginde arayuz bos satir yerine sinif adini gosterir.
    """
    return URUN_ISIMLERI.get(sinif, sinif)
