"""
Tum yapilandirma tek yerden okunur.

Gizli bilgiler koda gomulmez; proje kokundeki .env dosyasindan gelir.
Kurulum: .env.example dosyasini .env olarak kopyalayip anahtarinizi yazin.
"""

import os

from dotenv import load_dotenv

# Paket kasa/ icinde oldugu icin proje koku iki seviye yukarida.
ANA_DIZIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(ANA_DIZIN, ".env"))

# ── Roboflow baglantisi ──────────────────────────────────────────────
API_ANAHTARI = os.environ.get("ROBOFLOW_API_KEY", "").strip()
MODEL_ID     = os.environ.get("ROBOFLOW_MODEL_ID", "akilli_kasa/1")
API_ADRESI   = os.environ.get("ROBOFLOW_API_URL", "https://detect.roboflow.com")

# ── Web sunucusu ─────────────────────────────────────────────────────
# Varsayilan 127.0.0.1: arayuz ve kamera akisi yalnizca bu makineden
# erisilebilir. 0.0.0.0 yapmak, kimlik dogrulamasi olmayan /video_feed
# ucundaki canli kamera goruntusunu tum yerel aga acar.
SUNUCU_HOST = os.environ.get("KASA_HOST", "127.0.0.1")
SUNUCU_PORT = int(os.environ.get("KASA_PORT", "5000"))

# ── Tespit ───────────────────────────────────────────────────────────
MIN_GUVEN = 0.65  # Bu degerin altindaki tahminler sepete girmez.

# ── Kamera ───────────────────────────────────────────────────────────
KAMERA_INDEKSI   = 0     # 0 = isletim sisteminin varsayilan kamerasi
KAMERA_GENISLIK  = 1280
KAMERA_YUKSEKLIK = 720
# Surucu tamponunda tek kare tutulur: boylece okunan kare her zaman en
# yenisidir. Buyuk tampon, cikarim yavasladiginda eski kareleri biriktirip
# goruntunun gercekten gerisinde kalmasina yol acar.
KAMERA_TAMPON_BOYUTU = 1

# ── Zamanlama ────────────────────────────────────────────────────────
# Henuz kare yokken bosa donmemek icin kisa bekleme.
KARE_BEKLEME_SN = 0.1
# Cikarim dongusunun API'yi asiri yuklememesi icin iki istek arasi bekleme.
CIKARIM_ARALIGI_SN = 0.05
# MJPEG akis hizi: ~30 FPS.
AKIS_KARE_ARALIGI_SN = 1 / 30
# Akistaki JPEG sikistirma kalitesi (0-100). 85 boyut/kalite dengesi icin.
JPEG_KALITESI = 85

# ── Arayuz ───────────────────────────────────────────────────────────
# Tarayicinin /api/sepet ucunu ne siklikta sorguladigi.
# DIKKAT: arayuz/static/js/kasa.js icindeki SEPET_SORGU_MS ile ayni olmali.
SEPET_SORGU_MS = 500


def anahtari_dogrula() -> None:
    """
    ROBOFLOW_API_KEY tanimli degilse programi acik bir mesajla sonlandirir.

    Uygulama girisinde cagrilir. Anahtar olmadan Roboflow'a istek atmak
    sessizce basarisiz olacagi icin, sorunu en basta ve gorunur sekilde
    bildiriyoruz.
    """
    if not API_ANAHTARI:
        raise SystemExit(
            "[HATA] ROBOFLOW_API_KEY tanimli degil. "
            ".env.example dosyasini .env olarak kopyalayin ve kendi "
            "Roboflow anahtarinizi yazin:  cp .env.example .env"
        )
