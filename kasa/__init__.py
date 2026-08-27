"""
Akilli Kasa - ortak cekirdek paketi.

Hem web arayuzu (arayuz/app.py) hem de masaustu surumu (akilli_kasa.py)
tespit hattini bu paketten kullanir. Boylece fiyat listesi, guven esigi ve
cizim kurallari tek yerde tanimlidir.

Alt moduller:
    ayarlar  - .env okuma ve tum sabit yapilandirma
    urunler  - urun fiyatlari ve gorunen isimler
    tespit   - Roboflow istemcisi ve tahmin filtreleme
    cizim    - kare uzerine kutu, etiket ve toplam yazma
    araclar  - gunluk kaydi ve konsol basligi
"""
