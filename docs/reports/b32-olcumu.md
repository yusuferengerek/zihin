# 32B ölçümü — sonuç

**Seri 3** (`results/zihin-3.sqlite`), önek `b32`, 19 Ağustos 2026, commit
`80459f8`, çalışma ağacı temiz. Yorum ve şartlar koşudan önce
`experiments/setup-protocol.tr.md` §14'te yazıldı ve koşu sırasında
değiştirilmedi.

---

## 1. Ölçülen

| | |
|---|---|
| Model | `qwen/qwen-2.5-coder-32b-instruct`, OpenRouter üzerinden |
| Sağlayıcı — sabitlenen | Cloudflare (`provider.only`, `allow_fallbacks: false`) |
| Sağlayıcı — **gözlenen** | 951 çağrının **949'u** Cloudflare (yanıttan okundu, ilan değil) |
| Bildirilen kuantalama | `unknown` — sağlayıcı bildirmiyor |
| Bildirilen azami bağlam | 32768 (**ilan**, doğrulama değil; `context_verified = 0`) |
| Çıktı bütçesi | 4000, düzeltilmiş sınır kontrolüyle aynı |
| Yazılan epizot | **27** (tavan 29'da durdurdu, 2'si yazılamadı) |
| **Geçen** | **6** |
| Sonlanma | `agent_finished` 10, `no_progress` 11, `step_ceiling` 6 |
| **Tavana çarpma oranı** | **6/27 = %22,2** |
| Gerçek maliyet | **3,0024 dolar** (tavan 3,00; koşu tavanda durdu) |
| Süre | 1,95 saat, epizot başına 260 saniye |

**Geçen altı görev:** `024c982_1` (14 çağrı), `024c982_3` (9), `afc4005_1` (8),
`21abae1_1` (8), `29a7b7e_2` (11), `c77c005_3` (21). Altısı da
`agent_finished` ile bitti.

---

## 2. Önceden ilan edilen yorum, uygulanmış hâli

Gözlem **sıfırdan büyük**. §14.4'ün o satırı şunu diyordu ve aynen geçerli:

> Bant var. Ama hangi hassasiyette olduğunu bilmiyoruz. Yerel Q4_K_M
> eşdeğerinin aynı davranacağı iddia edilemez. Kurulabilir en geniş hâl:
> **"Cloudflare'in sunduğu hâliyle 32B'de bant var."**

**Bu bizim için elverişsiz olan dal, ve öyle raporlanıyor.** Sıfır çıksaydı ön
koşul bulgusu güçlenecek ve "küçük model seçtiniz" itirazı kapanacaktı. Sıfır
çıkmadı: **itiraz açık kalıyor.** Ön koşul kapısının üç yerel model için
ateşlemesi doğru, ama sebebinin ne kadarının kıyaslamanın zorluğu ne kadarının
model boyutu/hassasiyeti olduğu bu ölçümle ayrılmadı — ve bu ölçüm ikincisinin
payı olduğunu gösteriyor.

---

## 3. Kurulamayan cümleler

**"6/30" ya da herhangi bir oran kurulamaz.** İki ayrı sebeple:

1. **Küme eksik.** Otuz görevden 27'si yazıldı; maliyet tavanı koşuyu durdurdu.
   §6 eksik bir epizot kümesinin alıntılanmasını yasaklıyor.
2. **Tavan bağlayıcıydı.** Tavana çarpma oranı %22,2 ve K-60 bunu %10'un
   altında istiyor. Bağlayıcı bir tavanın altındaki sonuç bir **alt sınır**.

**Eksikliğin yönü asimetrik, ve bu bulguyu ayakta tutan şey.** Koşulmamış üç
epizot bir geçişi *gizleyebilir*, ama gözlenmiş bir geçişi *üretemez*. Yani
"bant var" varlık iddiası eksik kümeye rağmen ayakta; "bant şu kadar geniş"
iddiası ayakta değil.

**"Eksen 32B'de bant açıyor" kurulamaz.** 32B yerel 8 GB kısıtının dışında ve
eksene giremez (§14.1).

**Sınır kontrolüyle doğrudan karşılaştırma kurulamaz** — sebebi aşağıda.

---

## 4. İlan edilen iki koşul sapmış

Şartlar "durma kuralı, eşik ve kalkan kipi sınır kontrolüyle aynı" diyordu.
Künyeler karşılaştırıldı ve iki alan farklı çıktı:

| Alan | `sinir3` | `b32` |
|---|---|---|
| `no_progress_limit` | 15 | **40** |
| `shield_mode` | `off` | **shadow** |

**Sebep, ve suç koşucuda değil.** Koşucu `config/recording.yaml`'daki güncel
değeri okudu; yapılandırma sınır kontrolünden bu yana 15'ten 40'a değişmiş.
Şart **göreli** yazılmıştı ("sınır kontrolüyle aynı"), mutlak değil ("15"), ve
gönderme yaptığı şey altından kaydı. Ders: bir koşulu başka bir koşuya atıfla
tanımlamak, o atfın sabit kalmasına bağlı; sayıyı yazmak gerekiyordu.

**Etkisinin yönü ölçülebilir.** Daha gevşek bir eşik (40) epizotları daha uzun
koşturuyor, yani geçiş üretmeyi *kolaylaştırır*, zorlaştırmaz. Dolayısıyla altı
geçiş sıkı bir kuralın artefaktı değil. Ama iki koşu aynı koşulda olmadığı için
`sinir3`'ün 20/30'uyla doğrudan karşılaştırma kurulamıyor.

**Yerel sıfır bu eksende savunmasız değil.** `bant3-kapali` yerel modelleri
**durma kuralı tamamen kapalıyken** 26 epizotta koşturdu ve sonuç yine 0.
Gevşek eşik yerel sıfırı açıklayamıyor, çünkü sıfır eşiksiz de tekrarlandı.
"32B > 0, yerel = 0" karşılaştırması bu eksende ayakta.

---

## 5. Düzeneğin kendisi hakkında

**Sağlayıcı sabitlemesi çalıştı ve gözlemle doğrulandı.** İskele
`provider.only` alanını taşıyamıyor (§14.3'te ölçüldü); alan taşıma
katmanında, `scripts/setup/openrouter_pin.py` ileticisinde gövdeye eklendi.
Hizmet veren sağlayıcı gönderdiğimiz gövdeden değil **yanıttan** okundu: 949/951
Cloudflare. Kalan ikisi ileticinin kendi hata yanıtları (biri maliyet tavanı
402'si, biri ağ kesintisi).

**Maliyet tavanı ateşledi ve doğru davrandı.** 3,0024 dolarda durdu, ve §14.5
bunu "arıza değil sonuç" diye önceden yazmıştı. Tahmin 2,44 dolardı; gerçek
3,00'ı aştı, yani **tahmin düşük çıktı** — 32B, DeepSeek V4 Flash'tan daha çok
jeton harcadı.

**Künye nöbetçisi koşuyu bir kez reddetti ve haklıydı.** `results/zihin-2.sqlite`
`shield_mode` kısıtını taşımıyordu, çünkü sütun `ALTER TABLE` ile eklenmişti ve
SQLite'ın ALTER TABLE'ı kısıt taşımıyor — S-29 tam bunu ölçmüştü. Seri 3 bu
yüzden açıldı.

**İlk epizot koruması da ateşledi.** İlk denemede `MODEL_SERVER_URL` eksikti ve
koşu otuz epizot boyunca tekrarlamak yerine birinci epizotta durdu.
