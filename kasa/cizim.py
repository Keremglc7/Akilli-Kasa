"""
Kare uzerine tespit kutusu, etiket ve sepet toplami cizimi.

Bu degerler daha once web ve masaustu surumlerinde ayri ayri tanimliydi ve
zamanla birbirinden ayrilmisti (kutu rengi (0,255,0) ve (0,230,118) olmak
uzere iki farkli yesildi). Artik tek kaynak burasi; secilen yesil, arayuzdeki
--accent-green (#00e676) ile ayni tondur.
"""

import cv2

# ── Renkler (OpenCV BGR sirasi kullanir) ─────────────────────────────
KUTU_RENK        = (0, 230, 118)    # Yesil, arayuzdeki #00e676 ile ayni
YAZI_RENK        = (255, 255, 255)  # Beyaz
ETIKET_ZEMIN     = (0, 0, 0)        # Siyah
TOPLAM_YAZI_RENK = (0, 255, 255)    # Sari

# ── Yazi tipi ────────────────────────────────────────────────────────
FONT = cv2.FONT_HERSHEY_SIMPLEX

ETIKET_FONT_OLCEK    = 0.55
ETIKET_FONT_KALINLIK = 2
KUTU_KALINLIK        = 2

TOPLAM_FONT_OLCEK    = 0.9
TOPLAM_FONT_KALINLIK = 2

# ── Yerlesim bosluklari (piksel) ─────────────────────────────────────
ETIKET_IC_BOSLUK_X = 4   # Etiket yazisinin zemine soldan uzakligi
ETIKET_IC_BOSLUK_Y = 6   # Etiket yazisinin zemine alttan uzakligi
ETIKET_ZEMIN_PAY_X = 8   # Zemin dikdortgeninin yazidan genis olma payi
ETIKET_ZEMIN_PAY_Y = 10  # Zemin dikdortgeninin yazidan yuksek olma payi

TOPLAM_KENAR_BOSLUK = 10  # Toplam kutusunun sol ust koseye uzakligi
TOPLAM_IC_BOSLUK    = 10  # Toplam yazisinin zemin icindeki payi


def kose_koordinatlari(tespit: dict) -> tuple:
    """
    Merkez tabanli tespiti kose koordinatlarina cevirir.

    Roboflow kutuyu merkez (x, y) ve genislik/yukseklik olarak dondurur;
    OpenCV ise sol ust ve sag alt koseyi bekler.
    """
    yari_genislik  = tespit["genislik"] // 2
    yari_yukseklik = tespit["yukseklik"] // 2

    x1 = tespit["x"] - yari_genislik
    y1 = tespit["y"] - yari_yukseklik
    x2 = tespit["x"] + yari_genislik
    y2 = tespit["y"] + yari_yukseklik

    return x1, y1, x2, y2


def kutu_ve_etiket_ciz(kare, tespit: dict) -> None:
    """Tek bir tespit icin yesil kutuyu ve uzerindeki fiyat etiketini cizer."""
    x1, y1, x2, y2 = kose_koordinatlari(tespit)

    cv2.rectangle(kare, (x1, y1), (x2, y2), KUTU_RENK, KUTU_KALINLIK)

    etiket = f'{tespit["sinif"]}  {tespit["fiyat"]:.2f} TL'
    (yazi_genislik, yazi_yukseklik), _ = cv2.getTextSize(
        etiket, FONT, ETIKET_FONT_OLCEK, ETIKET_FONT_KALINLIK
    )

    # Yazinin okunabilmesi icin altina siyah zemin cizilir.
    cv2.rectangle(
        kare,
        (x1, y1 - yazi_yukseklik - ETIKET_ZEMIN_PAY_Y),
        (x1 + yazi_genislik + ETIKET_ZEMIN_PAY_X, y1),
        ETIKET_ZEMIN,
        cv2.FILLED,
    )

    cv2.putText(
        kare,
        etiket,
        (x1 + ETIKET_IC_BOSLUK_X, y1 - ETIKET_IC_BOSLUK_Y),
        FONT,
        ETIKET_FONT_OLCEK,
        YAZI_RENK,
        ETIKET_FONT_KALINLIK,
    )


def tespitleri_ciz(kare, tespitler: list) -> None:
    """Listedeki her tespit icin kutu ve etiket cizer. Kareyi yerinde degistirir."""
    for tespit in tespitler:
        kutu_ve_etiket_ciz(kare, tespit)


def toplam_yaz(kare, toplam: float) -> None:
    """Sol ust koseye sari 'TOPLAM SEPET' bandini yazar (masaustu surumu)."""
    metin = f"TOPLAM SEPET: {toplam:.2f} TL"
    (metin_genislik, metin_yukseklik), _ = cv2.getTextSize(
        metin, FONT, TOPLAM_FONT_OLCEK, TOPLAM_FONT_KALINLIK
    )

    cv2.rectangle(
        kare,
        (TOPLAM_KENAR_BOSLUK, TOPLAM_KENAR_BOSLUK),
        (
            TOPLAM_KENAR_BOSLUK + metin_genislik + 2 * TOPLAM_IC_BOSLUK,
            TOPLAM_KENAR_BOSLUK + metin_yukseklik + 2 * TOPLAM_IC_BOSLUK,
        ),
        ETIKET_ZEMIN,
        cv2.FILLED,
    )

    cv2.putText(
        kare,
        metin,
        (
            TOPLAM_KENAR_BOSLUK + TOPLAM_IC_BOSLUK,
            TOPLAM_KENAR_BOSLUK + metin_yukseklik + TOPLAM_IC_BOSLUK,
        ),
        FONT,
        TOPLAM_FONT_OLCEK,
        TOPLAM_YAZI_RENK,
        TOPLAM_FONT_KALINLIK,
    )
