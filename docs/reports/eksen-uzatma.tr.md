# Eksen uzatma raporu — "deney koşulamaz"dan "32B'de koşulabilir"e

**Tek soruyu yanıtlıyor:** ilan edilen ölçek ekseni sıfır verdiğinde deney
durmuştu; hangi ölçümler hangi sırayla yapıldı da eksen 32B'ye kadar uzatıldı.

Bu rapor bir sonuç raporu değil. Mekanizmaların işe yarayıp yaramadığını
söylemiyor; deneyin **koşulabilir hâle gelmesine** kadar olan yolu anlatıyor.

---

## 1. Ön koşul kapısı: ilan ve ateşleme

Kapı tasarımdan önce ilan edildi (K-58): mekanizmaların etkisi ancak ölçülecek
bir **bant** varsa ölçülebilir. Bant, ajanın bazı görevleri çözüp bazılarını
çözemediği aralık. Her şey sıfırsa, mekanizma sıfırı sıfır yapar ve ölçüm
mekanizma hakkında hiçbir şey söylemez.

**Kapı ateşledi.** İlan edilen eksende — `qwen2.5-coder` 1.5B / 3B / 7B, yerel,
`q4_K_M` — otuz görevde ikili başarı sıfır çıktı.

---

## 2. İlan edilen eksende sıfır: üç koşu, ve üçünün eşit olmadığı

| Koşu | Model | Epizot | Geçen | Tavana çarpma |
|---|---|---|---|---|
| `bant2` | 7B | 30 | 0 | **kayıtta yok** |
| `bant3` | 7B | 30 | 0 | **%0,0** |
| `bant3-kapali` | 7B | 26 | 0 | **%96,2** |

Üçüncüsünde **durma kuralı tamamen kapalıydı**: sıfırın sebebi kuralın erken
kesmesi değil.

**Bu üçünün eşit ağırlıkta olmadığı sonradan ölçüldü (S-63).** K-60 bir sıfır
yorumlanmadan önce tavanın bağlayıcı olmadığının gösterilmesini istiyor ve eşik
%10. Üç koşu bu eşiğe karşı hiç ölçülmemişti. Ölçülünce: `bant3` temiz,
`bant3-kapali` **alt sınır** (kural kapalıyken epizodu durduran tek şey tavan),
`bant2` ise **belirlenemedi** — sonlanma sebebi hiç yazılmamış.

Bulgu ayakta duruyor, çünkü bir tavan sıfırı **gizleyebilir ama üretemez**.
Değişen şey gücü: üç temiz ölçüm değil, bir temiz ölçüm, bir alt sınır, bir
belirsiz.

---

## 3. Elenenler — her biri kendi ölçümüyle

Sıfırın sebebi arandı. Sırasıyla elenenler:

### 3.1 Tabakalama bant açmadı

Görevleri zorluk bandına ayırmanın **üç ayrı biçimi** denendi. Hiçbiri sıfırın
üstünde bir aralık üretmedi.

### 3.2 Dereceli skor kullanılamadı

İkili başarı sıfırken kısmi kredi bir bant açabilirdi. `bant3`'te dereceli skor
**5/152** ve bu **iki göreve** yığılmış (`1150ed6_1` 4, `59fae45_2` 1). Yirmi
sekiz görevde tam sıfır. Böyle bir dağılım üzerinde koşul karşılaştırması
kurulamaz.

### 3.3 Hat elendi — görevler çözülebilir

Aynı otuz görevde:

| Model | Geçen |
|---|---|
| `deepseek-v4-flash` (barındırılan) | **20/30** |
| `gpt-4o-2024-05-13` | **15/30** |
| `qwen2.5-coder:7b` | 0/30 |

**Kayda geçen cümle bu, ve iki niteliği de taşıyor:**

> Otuz görevin **yirmisi** bu hatla çözülebiliyor; **on üçü** durma kuralı
> açıkken, **yedisi** kuralın kestiği görevler kural kapalıyken tekrar
> koşulduğunda. Ve o koşularda **düşünme açıktı**, ki ilan edilen koşul
> değildi (S-34).

Ölçüm: `sinir3` otuz görevi kural açıkken koştu, 13 geçti, 16'sı `no_progress`
ile kesildi. `sinir3-kapali` o **aynı on altı** görevi kural kapalıyken tekrar
koştu, 7'si daha geçti. İki geçen kümenin kesişimi boş, birleşimi yirmi.

Kısaltılmış hâli savunmada eksik kalır: "20/30" tek bir koşunun tek bir
koşuldaki sonucu değil.

Ve gpt-4o'nun çözdüğü on beş görevlik alt kümede 7B yeniden koşuldu: **0/15**,
anlamlı test 5/67.

Yani görevler çözülebilir ve düzenek çalışıyor; çözemeyen şey **bu ölçekteki
model**. Bu, sıfırın "görevler imkânsız" ya da "hat bozuk" okumasını eliyor.

### 3.4 İskele uyarlaması kapısı kapandı

İskeleyi uyarlamanın gerekçesi, hataların **kategori 4**'te (biçim/araç
hataları) yoğunlaşmasıydı. Ölçüldü: kategori 4 baskın değil. Gerekçe düştü,
kapı kapandı — iskele referans hâliyle bırakıldı (K-19).

### 3.5 Jetonu öğretmek bandı açmadı

Beceri kütüphanesi ile hata indeksi bağımsız korpuslardan aynı darboğaza
yakınsadı: kimlik doğrulama jetonu. Üç kollu koşuda (temel / kartlı / alakasız
kartlı, beş görev, üç tekrar) **giriş etkisine** — `POST <uygulama>.auth/token`
2xx — on beş hücrenin **üçü ile yedisi arasında** ulaşıldı.

**Tamamlama: 0/45.** Jetonu almak tek bir görevi bile çözdürmedi. Darboğaz jeton
değil; jeton, arkasındaki darboğaza açılan kapı (S-57).

### 3.6 Çıktı bütçesi 400'den 4000'e çıkarıldı, sıfır değişmedi

400'ün seçilmiş bir bütçe olmadığı ölçüldü: `bant3` o değeri, yapılandırmada o
anahtar **hiç yokken** aldı. Kaza, tasarım değil. Eksenin bütün noktaları aynı
bütçede olmalı, yoksa eksen değil iki ayrı ölçüm olur.

Yerel eksen 4000 ile yeniden koşuldu:

| Model | Geçen | Dereceli | Tavana çarpma | `agent_finished` |
|---|---|---|---|---|
| 1.5B | **0/30** | 0/152 | %33,3 | 0 |
| 3B | **0/30** | 2/152 | %33,3 | 1 |
| 7B | **0/30** | 7/152 | %30,0 | 4 |

Bütçe bağlayıcıydı — `agent_finished` sayısı 0 → 1 → 4 ve dereceli skor 0 → 2 →
7 arttı — ama **bandı açan şey değildi.**

---

## 4. Uzatmaya izin veren kural pilottan önce yazılmıştı

Eksen sıfırlar görüldükten sonra uzatılmadı; kural **önce** ilan edilmişti.

**S-14**, pilottan önce: eksenin en küçük noktası taban etkisine yapışırsa eksen
yukarı kaydırılır. Aynı kayıt engelin ne olduğunu da yazmıştı:

> "14B 8 GB'a sığmadığı için yukarı doğru telafi yok."

Yani engel **tasarım değil donanımdı**, ve kural o engel kalkarsa ne
yapılacağını zaten söylüyordu. Bant taraması sonra **üç noktanın birden**
tabanda olduğunu ölçtü; kural en küçük nokta için yazılmıştı, gerçekleşen daha
geniş çıktı.

Kilit tek: *"model yerel donanımda koşuyor"*. Aile kilidi açılmadı — beş nokta
da `qwen2.5-coder`, beşi de `q4_K_M`, ve bu artık bir testle çivili.

**Düzeltme — 25 Eylül 2026: bu bölümün başlığı ve ilk cümlesi yanlıştı.**
Uzatmaya izin veren bir kural pilottan önce yazılmamıştı. `S-14`'ün pilottan
önceki kuralı **aşağı** daralmaydı — "eksen 3B ve 7B'ye iner" — ve yukarı yolu
donanım yüzünden açıkça kapalı yazmıştı. Colab engeli kaldırdı; uzatma sonradan,
kullanıcının açık onayıyla alınmış bir karar (`K-133`'ün 25 Eylül ekleri). "Eksen
sıfırlar görüldükten sonra uzatılmadı" cümlesi de tutmuyor: uzatma sıfırlar
görüldükten **sonra** yapıldı, ve ön kayıt A.11'in ekleri noktaları tam bu yüzden
keşifsel etiketliyor. Metin olduğu gibi duruyor.

---

## 5. İki uzatma koşusu

### 5.1 14B — Colab L4

Şartlar §15.2'de ilan edilmişti, ama koşu **onlarla koşmadı**: ilan edilen
400/15/off yerine 4000/40/shadow ile koştu, çünkü ilan edilen yer ile okunan yer
ayrıydı (S-58 üçüncü örneği). Sonuç **3/30**, tavana çarpma **%20**.

### 5.2 32B — Colab A100

Şartlar §16.2'de, koşudan önce, mutlak değerle. Bu kez bir denetim
(`check_declared_conditions.py`) koşudan önce on alanın onunu çözdü ve onu da
tuttu. Kayıt sonradan bağımsız olarak doğrulandı: `code_commit`, `boot_id`,
`wall_clock_utc` ve sekiz koşul alanı.

Sonuç **11/30**, tavana çarpma **%6,7**, `no_progress` **0**. Yapılandırma
hükmü **COMPARABLE**: 49/49 katman GPU'da, flash attention etkin, KV `q8_0`.

---

## 6. Eksen — alt sınır ve ölçüm ayrı

| Nokta | Sonuç | Tavana çarpma | Etiket |
|---|---|---|---|
| 1.5B | 0/30 | %33,3 | **ALT SINIR** |
| 3B | 0/30 | %33,3 | **ALT SINIR** |
| 7B | 0/30 | %30,0 | **ALT SINIR** |
| 14B | 3/30 | %20,0 | **ALT SINIR** |
| 32B | **11/30** | **%6,7** | **ÖLÇÜM** |

K-60'ın eşiği %10. Dördü aşıyor, biri aşmıyor. **Bu beş sayı aynı ağırlıkta
değil** ve aynı grafikte yan yana çizilirse öyle görünürler.

Alt sınır demek: gerçek değer bu sayıdan **büyük ya da eşit**. Dört noktanın
sıfır ya da düşük olması, o noktalarda bant olmadığını göstermiyor; tavanın
bağlayıcı olduğunu gösteriyor.

---

## 7. Görev tipi ayrımı — manşet sayıdan önemli

Otuz görev, değerlendirme dosyalarının **kendisinden** iki tipe ayrıldı:

- **Cevap tipi (5 görev):** değerlendirme yalnız cevabı ve "hiçbir şey
  değiştirme"yi sınıyor. Tek anlamlı test bir dize eşitliği.
- **Cevap+dünya tipi (25 görev):** değerlendirme dünyada bir değişiklik de
  arıyor.

| Model | Cevap (5) | Cevap+dünya (25) |
|---|---|---|
| 14B | 2/5 | **1/25** |
| 32B | 4/5 | **7/25** |

**Neden manşetten önemli.** Beceri kütüphanesi **API çağrı dizileri** öğretiyor;
hata indeksi hangi çağrının hangi koşulda düştüğünü. İkisi de dünyayı
değiştiren görevlerde işe yarayabilir. Cevap tipinde bir kazanım mekanizmaları
sınamıyor.

Yani asıl soru "32B 11/30 verdi mi" değil, **"cevap+dünya tipinde bir bant var
mı"**. 32B'de 7/25 var; 14B'de 1/25 vardı.

**Bant etiketi ayrıca yanıltıcı (S-62).** Çapa referans çözümün yolunu ölçüyor,
görevin gerektirdiğini değil: `09b0ee6_1` çapa 102 taşıyor, `90+` bandında
görünüyor, ve altı adımda geçildi — çünkü tek anlamlı testi bir dize eşitliği.

---

## 8. Bu raporun kurmadığı şeyler

**Mekanizmalar model çağrısını düşürüyor mu — bilinmiyor.** Bu rapor yalnız
ölçülebilir bir bandın nerede başladığını anlatıyor. Birincil soru henüz
ölçülmedi.

**Yerel sıfırların dördü tavan sınırlı.** 1.5B, 3B, 7B ve 14B'nin sayıları alt
sınır. "Boyut arttıkça başarı artıyor" cümlesi bu tabloyla kurulamaz.

**Uzatma koşuları keşifsel.** Eksen noktaları — 14B ve 32B — **sıfırlar
görüldükten sonra** seçildi. Veri güdümlü bir eksen uzatması onaylayıcı olamaz,
ne kadar iyi çıkarsa çıksın. Ön kayıt A.11'e iki tarihli ek düşüldü ve özgün
ilan değiştirilmedi.

**14B'nin koşulları koşudan sonra düzeltildi.** 14B, §15.2'nin ilan ettiği
değerlerle koşmadı. 32B'nin şartlarıyla uyuşması bir kazanın sonucu; uyuşma
karşılaştırmayı mümkün kılıyor ama **önceden ilan edilmiş bir tasarım değil**.

**Eksenin noktaları üç farklı kartta ölçüldü (S-61).** RTX 4070 (Ada), L4 (Ada),
A100 (**Ampere**). Yapılandırma hükmü üç şeyi karşılaştırıyor; kartlar arasında
ölçülmeyen her fark açık kalıyor.

**Beş nokta bir eğrinin şeklini belirlemez.** Ön kayıttaki dört şekil tablosu
yorum disiplini için duruyor, istatistiksel iddia için değil.
