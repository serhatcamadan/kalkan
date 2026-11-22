/* KALKAN · demo arayüzü · v1 · 2026-11-22
   Kullanıcı metni DOM'a yalnızca textContent/append ile girer (HTML olarak ayrıştırılmaz): mesajdaki kod çalışamaz. */
"use strict";
const ORNEKLER = [
  "Kestane Kargo: gönderiniz gümrükte bekliyor. 49,90 TL gümrük ücretini 24 saat içinde ödemezseniz iade edilecektir: kstn-kargo.info/ode",
  "Kestane Kargo: KG448812093 numaralı gönderiniz bugün dağıtıma çıktı. Takip: kestanekargo.com.tr/takip",
  "Anne bu benim yeni numaram, telefonum suya düştü. Acil 7.500 TL lazım, şu hesaba atar mısın TR33 0006 1005 1978 6457 8413 26 kimseye söyleme",
];
const SEVIYE = {
  yuksek:   {ad:"Yüksek risk",   renk:"var(--yuksek)"},
  orta:     {ad:"Dikkat",        renk:"var(--orta)"},
  belirsiz: {ad:"Değerlendirilemedi", renk:"var(--belirsiz)"},
  dusuk:    {ad:"Düşük risk", renk:"var(--dusuk)"},
};
const SINYAL = {
  odeme_talebi:"Ödeme talebi", kod_talebi:"Kod talebi", kimlik_talebi:"Şifre veya kimlik talebi", aciliyet:"Acele ettirme",
  kurum_taklidi:"Kurum gibi davranma", yetki_iddiasi:"Yetkili olduğunu iddia etme", odul_vaadi:"Ödül veya kazanç vaadi",
  gizlilik_baskisi:"Kimseye söyleme baskısı", kanal_degistirme:"Başka kanala yönlendirme", yakinlik_iddiasi:"Yakınınız gibi davranma",
  link:"Bağlantı",
};
const ISARET = {
  link:"Bağlantı", kisa_link:"Kısa bağlantı", punycode:"Kodlanmış alan adı", unicode_alan_adi:"Benzer harfli alan adı",
  supheli_tld:"Şüpheli alan uzantısı", marka_iceren_yabanci:"Marka adı geçen yabancı alan adı",
  benzer_alan_adi:"Markaya benzeyen alan adı", resmi_alan_adi:"Resmi alan adı", iban:"IBAN", tutar:"Para tutarı",
  otp:"Tek kullanımlık kod", telefon:"Telefon numarası", paylasma_uyarisi:"\"Paylaşmayın\" uyarısı",
  gizlilik_ifadesi:"Gizlilik ifadesi", gizli_karakter:"Görünmez karakter", ret_mekanizmasi:"Ticari ileti ret satırı",
};
const $ = id => document.getElementById(id);
const el = (tag, ozellik = {}, ...cocuk) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(ozellik)) k === "class" ? e.className = v : e.setAttribute(k, v);
  for (const c of cocuk) e.append(c);
  return e;
};

$("mesaj").addEventListener("input", () => {
  const n = $("mesaj").value.length;
  $("sayac").textContent = n > 1800 ? `${n.toLocaleString("tr-TR")} / 10.000 karakter` : "";
});
document.querySelectorAll("[data-ornek]").forEach(b => b.addEventListener("click", () => {
  $("mesaj").value = ORNEKLER[+b.dataset.ornek];
  $("mesaj").dispatchEvent(new Event("input"));
  $("form").requestSubmit();
}));

$("form").addEventListener("submit", async ev => {
  ev.preventDefault();
  const mesaj = $("mesaj").value.trim();
  $("hata").hidden = true;
  if (!mesaj) { hata("Kontrol etmek için önce bir mesaj yapıştırın."); return; }
  $("gonder").disabled = true; $("gonder").textContent = "Kontrol ediliyor…";
  try {
    const r = await fetch("/analiz", {method:"POST", headers:{"Content-Type":"application/json"},
                                      body: JSON.stringify({mesaj})});
    const d = await r.json().catch(() => ({}));
    if (!r.ok) {
      const metin = {413:"Mesaj çok uzun: en fazla 10.000 karakter kontrol edilebilir.",
                     429:"Kısa sürede çok fazla kontrol yapıldı. Bir dakika sonra tekrar deneyin.",
                     503:"Sistem şu an meşgul. Birkaç saniye sonra tekrar deneyin."}[r.status];
      hata(metin || (typeof d.detail === "string" ? d.detail : `Kontrol yapılamadı (hata ${r.status}).`));
      return;
    }
    goster(d);
  } catch (e) {
    hata("Sunucuya ulaşılamadı. İnternet bağlantınızı kontrol edip tekrar deneyin.");
  } finally {
    $("gonder").disabled = false; $("gonder").textContent = "Mesajı kontrol et";
  }
});

function hata(metin) { $("hata").textContent = metin; $("hata").hidden = false; }

function goster(d) {
  const s = SEVIYE[d.risk] || SEVIYE.belirsiz;
  const kutu = $("sonuc");
  kutu.replaceChildren();
  kutu.style.setProperty("--renk", s.renk);

  // 1) karar: kullanıcı mesajı (politika metni) olduğu gibi; "güvenli" asla yazılmaz (ADR-0004)
  const [ilk, ...geri] = d.mesaj.split(/(?<=\.)\s+/);
  kutu.append(el("div", {class:"karar"},
    el("p", {class:"seviye"}, s.ad),
    el("p", {class:"cumle"}, ilk),
    d.tur_adi && !["mesru_islem", "reklam_spam"].includes(d.tur) ? el("p", {class:"tur"}, `Olası tür: ${d.tur_adi}`) : ""));

  // 2) neden: kanıtlar mesajın üzerinde
  kutu.append(el("h2", {}, d.kanitlar.length ? "Neden?" : "Mesaj"));
  kutu.append(isaretli(d.gosterilen_metin, d.kanitlar));
  if (d.kanitlar.length) {
    const ol = el("ol", {class:"kanitlar"});
    d.kanitlar.forEach(k => ol.append(el("li", {}, el("span", {class:"ad"}, SINYAL[k.sinyal] || k.sinyal), `: "${k.alinti}"`)));
    kutu.append(ol);
  } else if (d.risk === "dusuk") {
    kutu.append(el("p", {class:"yok"}, "Mesajda dolandırıcılık işareti olarak işaretlenecek bir ifade bulunmadı."));
  }

  // 3) ne yapmalı
  if (geri.length) { kutu.append(el("h2", {}, "Ne yapmalı?")); kutu.append(el("p", {class:"oneri"}, geri.join(" "))); }
  if (d.girdi_kirpildi) kutu.append(el("p", {class:"uyari"}, "Mesaj çok uzun olduğu için tamamı ayrıntılı incelenemedi."));
  if (!d.model_kullanildi) kutu.append(el("p", {class:"uyari"}, "Dil modeli bu kontrolde yanıt vermedi; sonuç yalnızca kurallara dayanıyor."));
  if (d.dusurulen_kanit) kutu.append(el("p", {class:"uyari"},
    `Modelin önerdiği ${d.dusurulen_kanit} alıntı mesajda birebir bulunamadığı için gösterilmedi.`));

  // 4) ayrıntı
  const isaretler = [...new Set(d.sinyaller.map(x => ISARET[x.tip] || x.tip))];
  kutu.append(el("details", {},
    el("summary", {}, "Teknik ayrıntılar"),
    el("dl", {},
      el("dt", {}, "Bulunan işaretler"), el("dd", {}, isaretler.join(", ") || "yok"),
      el("dt", {}, "Süre"), el("dd", {}, `${(d.sure_ms / 1000).toLocaleString("tr-TR", {maximumFractionDigits:1})} sn`),
      el("dt", {}, "Öneri kodu"), el("dd", {}, d.oneri_kodu),
      el("dt", {}, "Kayıt numarası"), el("dd", {}, d.trace_id))));

  kutu.hidden = false;
  kutu.classList.remove("yeni"); void kutu.offsetWidth; kutu.classList.add("yeni");
  kutu.scrollIntoView({behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block:"start"});
}

function isaretli(metin, kanitlar) {
  // Kanıt aralıkları (bas, bit) gösterilen (maskeli) metne göredir; çakışanlar atlanır.
  const b = el("div", {class:"balon"});
  const sira = kanitlar.map((k, i) => ({...k, no:i + 1})).sort((x, y) => x.bas - y.bas);
  let i = 0;
  for (const k of sira) {
    if (k.bas < i || k.bit > metin.length || metin.slice(k.bas, k.bit) !== k.alinti) continue;
    b.append(metin.slice(i, k.bas));
    const ad = SINYAL[k.sinyal] || k.sinyal;
    b.append(el("mark", {title: ad, "aria-label": `${ad}: ${k.alinti}`}, metin.slice(k.bas, k.bit), el("sup", {}, String(k.no))));
    i = k.bit;
  }
  b.append(metin.slice(i));
  return b;
}
