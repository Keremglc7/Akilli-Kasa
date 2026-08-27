"""
Roboflow istemcisi ve tahmin filtreleme.

Model ham tahmin dondurur; bu modul onlari uygulamanin her yerinde ayni
sekilde temizler. Hem web arayuzu hem masaustu surumu bunu kullanir, boylece
guven esigi veya alan adlari iki yerde ayri ayri degismez.
"""

from inference_sdk import InferenceHTTPClient

from kasa import ayarlar, urunler


def istemci_olustur() -> InferenceHTTPClient:
    """Yapilandirmadaki adres ve anahtarla Roboflow istemcisi kurar."""
    return InferenceHTTPClient(
        api_url=ayarlar.API_ADRESI,
        api_key=ayarlar.API_ANAHTARI,
    )


def tespitleri_filtrele(sonuclar: dict) -> list:
    """
    Roboflow yanitini temiz tespit listesine cevirir.

    Iki tahmin elenir:
      - guveni MIN_GUVEN esiginin altinda kalanlar,
      - fiyat listesinde bulunmayan siniflar (beyaz liste disi).

    Donen her tespit su alanlari icerir:
        sinif, guven, x, y, genislik, yukseklik, fiyat

    x ve y kutunun MERKEZ koordinatlaridir (Roboflow bu bicimde dondurur);
    kose koordinatlari icin kasa.cizim.kose_koordinatlari kullanin.
    """
    temiz = []

    for tahmin in sonuclar.get("predictions", []):
        sinif = tahmin.get("class", "")
        guven = tahmin.get("confidence", 0.0)

        if guven < ayarlar.MIN_GUVEN:
            continue
        if not urunler.taniniyor_mu(sinif):
            continue

        temiz.append({
            "sinif":     sinif,
            "guven":     guven,
            "x":         int(tahmin["x"]),
            "y":         int(tahmin["y"]),
            "genislik":  int(tahmin["width"]),
            "yukseklik": int(tahmin["height"]),
            "fiyat":     urunler.fiyat_al(sinif),
        })

    return temiz


def sepet_toplami(tespitler: list) -> float:
    """Tespit listesindeki urunlerin fiyat toplamini dondurur."""
    return sum(tespit["fiyat"] for tespit in tespitler)
