// ── Zamanlama sabitleri ─────────────────────────────────
// Sepet sorgu araligi sunucudan gelir (kasa/ayarlar.py -> SEPET_SORGU_MS),
// boylece iki tarafta elle senkron tutulmasi gerekmez.
const SEPET_SORGU_MS = KASA_AYAR.sepetSorguMs;
const SAAT_GUNCELLEME_MS = 1000;
// DIKKAT: kasa.css icindeki ".total-value.bump" gecis suresi (0.2s) ile ayni
// olmali; animasyon bitmeden sinif kaldirilirsa efekt yarida kesilir.
const BUMP_SURESI_MS = 200;

// ── Urun renk paleti (her sinifa sabit bir renk) ────────
const RENK_PALETI = {
    biscolata_stix:    '#e91e63',
    burcak_cikolatali: '#9c27b0',
    crax_aci:          '#f44336',
    crax_lime:         '#4caf50',
    dido:              '#2196f3',
    lipton_seftali:    '#ff9800',
    nescafe_vanilya:   '#795548',
    patos_rolls:       '#ff5722',
    ulker_gofret:      '#607d8b',
};

/**
 * Metni HTML'e gomulmeye guvenli hale getirir.
 *
 * Urun adlari sunucudaki sabit sozlukten gelir, ama gorunen_ad() taninmayan
 * bir sinif icin ham model cikti metnine duser. Sablon icine dogrudan
 * gomulmesin diye kacis uyguluyoruz.
 */
function htmlKacis(metin) {
    const kutu = document.createElement('div');
    kutu.textContent = metin;
    return kutu.innerHTML;
}

// ── Saat guncelleme ─────────────────────────────────────
function updateClock() {
    const now = new Date();
    document.getElementById('clock').textContent =
        now.toLocaleTimeString('tr-TR', { hour12: false });
}
setInterval(updateClock, SAAT_GUNCELLEME_MS);
updateClock();

// ── Son veriyi takip (gereksiz DOM guncellemeyi onler) ──
let lastJSON = '';
let lastTotal = -1;

// ── Sepet verisini cek ve arayuzu guncelle ──────────────
async function fetchSepet() {
    try {
        const res = await fetch('/api/sepet');
        const data = await res.json();
        const json = JSON.stringify(data);

        // Ayni veri geldiyse DOM'a dokunma
        if (json === lastJSON) return;
        lastJSON = json;

        const container  = document.getElementById('receipt-items');
        const emptyState = document.getElementById('empty-state');
        const countTag   = document.getElementById('item-count-tag');
        const totalCount = document.getElementById('total-count');
        const totalValue = document.getElementById('total-value');

        // Urun sayisi etiketi
        countTag.textContent = `${data.toplam_adet} ürün`;
        totalCount.textContent = `${data.toplam_adet} ürün`;

        // ── Urun Listesi ────────────────────────────────
        // Onceki satirlar silinir; bos-sepet blogu HTML'de duruyor ve yalnizca
        // gizlenip gosteriliyor, boylece ayni isaretleme iki yerde yazilmiyor.
        container.querySelectorAll('.receipt-item').forEach(satir => satir.remove());

        const sepetBos = data.urunler.length === 0;
        emptyState.hidden = !sepetBos;

        if (!sepetBos) {
            let html = '';
            data.urunler.forEach(item => {
                const renk = RENK_PALETI[item.sinif] || '#666';
                const ad = htmlKacis(item.ad);
                const initials = htmlKacis(item.ad.substring(0, 2).toUpperCase());
                const birimStr = item.birim_fiyat.toFixed(2);
                const toplamStr = item.ara_toplam.toFixed(2);

                html += `
                <div class="receipt-item">
                    <div class="item-icon" style="background:${renk}">
                        ${initials}
                    </div>
                    <div class="item-info">
                        <div class="item-name">${ad}</div>
                        <div class="item-meta">${birimStr} TL / adet</div>
                    </div>
                    <div class="item-qty">x${item.adet}</div>
                    <div class="item-price">${toplamStr} TL</div>
                </div>`;
            });
            container.insertAdjacentHTML('beforeend', html);
        }

        // ── Toplam Tutar ────────────────────────────────
        const toplam = data.toplam.toFixed(2);
        totalValue.innerHTML = `${toplam}<span class="total-currency"> TL</span>`;

        // Toplam degistiyse kucuk bir "bump" animasyonu
        if (data.toplam !== lastTotal) {
            totalValue.classList.add('bump');
            setTimeout(() => totalValue.classList.remove('bump'), BUMP_SURESI_MS);
            lastTotal = data.toplam;
        }

    } catch (err) {
        // Ag hatalarinda sessizce devam et
    }
}

// ── Backend'den periyodik olarak veri cek ───────────────
setInterval(fetchSepet, SEPET_SORGU_MS);
fetchSepet();
