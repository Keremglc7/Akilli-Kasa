"""
Akilli Kasa Sistemi - Tek tikla baslatici.
arayuz/app.py sunucusunu baslatir ve tarayiciyi otomatik acar.

Kullanim:
    python baslat.py
"""

import os
import socket
import subprocess
import sys
import time
import webbrowser

from kasa import araclar, ayarlar

araclar.gunlugu_kur()
kayit = araclar.gunlukcu("baslat")

ANA_DIZIN  = os.path.dirname(os.path.abspath(__file__))
ARAYUZ_DIR = os.path.join(ANA_DIZIN, "arayuz")
APP_PY     = os.path.join(ARAYUZ_DIR, "app.py")

# Sunucunun ayaga kalkmasi beklenirken kullanilacak degerler.
# Sabit bir bekleme yerine porta baglanmayi deniyoruz: cv2 ve inference_sdk
# import'lari yavas makinelerde saniyeler surebilir ve sabit sure dolduysa
# tarayici "baglanti reddedildi" sayfasinda acilirdi.
BASLAMA_ZAMAN_ASIMI_SN = 30.0
YOKLAMA_ARALIGI_SN     = 0.25
YOKLAMA_BAGLANTI_SN    = 0.5


def sunucu_adresi() -> tuple:
    """
    Tarayicinin baglanacagi (host, port) ciftini dondurur.

    Sunucu 0.0.0.0 dinliyorsa bu bir "tum arayuzler" adresidir, hedef adres
    degil; bu durumda yerel makineye baglaniriz.
    """
    host = ayarlar.SUNUCU_HOST
    if host == "0.0.0.0":
        host = "127.0.0.1"
    return host, ayarlar.SUNUCU_PORT


def sunucuyu_bekle(host: str, port: int, zaman_asimi: float, surec) -> bool:
    """
    Port kabul etmeye baslayana kadar bekler.

    Sunucu zaman asimindan once ayaga kalkarsa True doner. Sunucu surecinin
    kendisi sonlanirsa (ornegin ROBOFLOW_API_KEY tanimli degilse) beklemeye
    devam etmenin anlami yoktur; bu durumda hemen False doner.
    """
    son = time.monotonic() + zaman_asimi

    while time.monotonic() < son:
        if surec.poll() is not None:
            return False

        try:
            with socket.create_connection((host, port), YOKLAMA_BAGLANTI_SN):
                return True
        except OSError:
            time.sleep(YOKLAMA_ARALIGI_SN)

    return False


def main():
    """Flask sunucusunu baslatir, hazir olunca tarayiciyi acar."""
    host, port = sunucu_adresi()
    url = f"http://{host}:{port}"

    kayit.info("Flask sunucusu baslatiliyor...")
    surec = subprocess.Popen([sys.executable, APP_PY], cwd=ARAYUZ_DIR)

    if sunucuyu_bekle(host, port, BASLAMA_ZAMAN_ASIMI_SN, surec):
        kayit.info("Tarayici aciliyor: %s", url)
        webbrowser.open(url)
    elif surec.poll() is not None:
        kayit.error("Sunucu baslatilamadi. Yukaridaki hata mesajina bakin.")
    else:
        kayit.error(
            "Sunucu %.0f saniyede ayaga kalkmadi. Yukaridaki hata mesajlarina bakin.",
            BASLAMA_ZAMAN_ASIMI_SN,
        )

    try:
        surec.wait()
    except KeyboardInterrupt:
        kayit.info("Kapatiliyor...")
        surec.terminate()


if __name__ == "__main__":
    main()
