# Kurulum protokolü

**Bu belge şimdi donuyor.** Deney ön kaydı (`preregistration.md`) ayrı ve kurulum
bittikten sonra, pilottan önce donacak.

## Ayrımın sebebi

Aile seçimi bir ölçüm, yani K-62 gereği yorumlanma kuralı koşudan önce yazılı
olmak zorunda. Ama deney ön kaydının sayıları aile seçilmeden bilinemiyor: hangi
aile, hangi boyutlar, gürültü tabanı ne. Tek belge yapılsaydı deney başlamadan
tadilat kaydı birikmiş olurdu.

Ayrım aynı zamanda dürüst. Kurulum aşamasında veriye bakarak parametre seçmek
meşru; kurallı olması gerekiyor. İkisi tek belgede olsaydı hangi kararın hangi
rejimde alındığı karışırdı.

**Bu belgedeki her şey kurulum rejimine ait.** Buradan çıkan hiçbir sayı sonuç
iddiası taşımıyor.

## 1. Aile seçim ölçütü

Ana eksen şartları K-61'de: tek aile, en az üç yoğun boyut hepsi Q4_K_M ile 32K
bağlam ve q8_0 KV altında 8 GB'a sığmalı, akıl yürütme modu olmayan ya da
tamamen kapatılabilen, Ollama'da mevcut ve instruct ayarlı.

Ağırlık tavanı kabaca 5-6 GiB. Ölçülmüş referans: `qwen2.5-coder:7b` Q4_K_M
kartta 5,16 GiB, 32K q8_0 KV bir slot için yaklaşık 0,9 GiB.

**Karar kuralı.** Ailenin en büyük sığan boyutunun ön koşulu geçmesi yetmiyor.
**En az iki boyut geçmeli**, yoksa ölçek ekseni yaşamıyor ve ikinci araştırma
sorusu ölüyor.

**Aile elemesi için kaba eşik: taban başarısı %25 üstü.** Kesin sayı pilottan
gelecek; bu eşik yalnız aday elemek için.

### İki ölçüt karıştırılmıyor

**Ana eksen şartı:** en az üç yoğun boyutun **var olması ve sığması**. Bu
aileye ait bir olgu, ölçümle ilgisi yok.

**Seçim ölçütü:** o boyutlardan en az **ikisinin ön koşulu geçmesi**. Bu ölçüm
sonucu.

Karıştırılırsa iki boyutlu bir aileye tarama harcanır ve kazansa bile ölçek
şekli cevaplanamaz.

Ollama kayıt sunucusundan ölçülen sığan boyut sayıları (ağırlık ≤ 6 GiB):

| Aile | Sığan yoğun boyut | Şart 2 | Not |
|---|---|---|---|
| `falcon3` | 1b, 3b, 7b, 10b | **✓ 4** | Yoğun, akıl yürütme modu yok |
| `qwen2.5-coder` | 0.5b, 1.5b, 3b, 7b | ✓ 4 | Şu anki aile, ön koşulu geçemedi |
| `qwen2.5` | 0.5b, 1.5b, 3b, 7b | ✓ 4 | Kod uzmanı değil |
| `qwen3` | 0.6b, 1.7b, 4b, 8b | ✓ 4 | Hibrit düşünme; kapatılabiliyor, şart 3 tartışmalı |
| `qwen3.5` | 0.8b, 2b, 4b | ✓ 3 | Kendi sayfası "sparse MoE" diyor, şart 2'nin yoğunluk kısmıyla çelişiyor |
| `deepseek-r1` | 1.5b, 7b, 8b | ✓ 3 | Akıl yürütme kapatılamıyor, **elendi** |
| `granite3.3`, `granite3.2`, `granite4`, `granite-code` | ikişer | ✗ 2 | Ayrıca aile kontrolü rolünde |
| `gemma3`, `gemma2`, `codegemma`, `starcoder2`, `yi-coder`, `llama3.2`, `hermes3`, `opencoder`, `cogito` | ikişer | ✗ 2 | — |

**Şartı tutan tek temiz aday `falcon3`.** Dört boyutu sığıyor, yoğun, akıl
yürütme modu yok, instruct ayarlı ve Granite dışı.

**İki boyutu sığan aileler otomatik elenmiyor** ama **en sona taranıyor**. Biri
kazanırsa ölçek şeklinin cevaplanamaz olduğu sınırlamalara yazılıyor: iki nokta
bir eğrinin yönünü vermez.

### Granite ayrı tutuluyor

`granite3.3`, `granite3.2`, `granite4` ve `granite-code` farklı hatlar ama aynı
kuruluş. Granite ana eksene alınırsa aile kontrolü **başka bir kuruluştan**
olmak zorunda, yoksa "farklı aile" kontrolü zayıflar.

Şu an karar gerekmiyor: dördü de şart 2'yi tutmuyor, yani ana eksene aday
değiller ve aile kontrolü rolü için serbest kalıyorlar. Aday listesinde Granite
dışı en az bir aile bulunuyor (`falcon3`).

### Tarama sırası: geçme olasılığına göre, saflığa göre değil

Maliyet asimetrisi: başarısız bir tarama bir koşuya mal oluyor, saflık ödünü
veren geçen bir tarama ise bir koşu **artı bir tasarım tavizi**. Temiz adayın
makul şansı varsa önce o gidiyor; açıkça zayıfsa sıra değişiyor.

Toplanan kanıt:

| Aday | Yayın | Yayımlanmış AppWorld sayısı | Not |
|---|---|---|---|
| `qwen3.5` | Şubat 2026 | yok | En yeni kuşak |
| `qwen3` | Nisan 2025 | **8B AWQ 4-bit %3,0**, FP16 %5,4 | `test_normal`, pass@1 |
| `falcon3` | **Aralık 2024** | yok | Qwen2.5-Coder ile aynı kuşak, kod uzmanı değil |

Kaynak: <https://arxiv.org/html/2604.11465v2>.

**Falcon 3 temiz aday ama açıkça zayıf.** 17 Aralık 2024'te yayımlandı, yani
ön koşulu geçemeyen Qwen2.5-Coder ile çağdaş, üstelik kod uzmanı da değil.
Aileyi yeniden açmamızın gerekçesi "2026 ailesi 2024 ailesinden iyi olabilir"di;
çağdaş bir aileyi ilk sıraya koymak muhtemelen bir koşuyu boşa harcar.

**Sıra:** `qwen3.5` → `qwen3` → `falcon3` → iki boyutlu aileler.

Qwen3'ün yayımlanmış sayısı da uyarı taşıyor: 8B'nin dört bit kuantalanmış hâli
`test_normal`'da %3,0 alıyor ve eleme eşiğimiz %25. Sıraya giriyor ama beklenti
düşük.

**2026 kuşağında sığan tek aile `qwen3.5`.** Ollama kütüphanesinde `gemma4`'ün
en küçüğü 6,9 GiB ile sığmıyor; `qwen3.6`, `qwen3.7`, `qwen3.8`, `llama5` ve
`phi5` yok.

### Koşullu iki aday

**`qwen3` — düşünmenin kapatılabilirliği koşuda değil, koşudan önce
doğrulanıyor.**

Kullanılacak **her boyutta ayrı ayrı** şu sınama koşuluyor: açık kipte düşünme
tetikleyen bir prompt seçiliyor, kapalı kipte **sıfır düşünme jetonu** çıktığı
gösteriliyor. Sonuç künyeye yazılıyor.

Bir boyut geçmezse aile eleniyor. Sınama koşudan önce yazılıyor, çünkü sonradan
yazılırsa aynı tuzağa düşeriz: bir şeyin çalıştığını görmek, doğru sebeple
çalıştığını göstermez (K-49).

**`qwen3.5` — eksen aktif parametre sayısıyla tanımlanıyor.**

Yoğunluk şartının sebebi ölçek ekseninin tek ve net bir sayıya dayanmasıydı.
MoE'de toplam ile aktif parametre ayrışıyor ve eksen belirsizleşiyor.

Kural: **eksen aktif parametre sayısı**, çünkü birim maliyeti o belirliyor ve
projenin maliyet hikâyesi de o. Toplam parametre yanına kaydediliyor. İkisi de
taramadan önce ilan ediliyor.

**Yoğun ve MoE aileleri tek eksende karıştırılmıyor.** Eksen ya bütünüyle yoğun
ya bütünüyle MoE.

### Üç sonucun kuralı, taramadan önce yazılı (K-62)

**Eşiği geçerse** aile seçilir.

**Kullanılabilir güç tabanı ile %25 arasına düşerse**, eşik düşürülüp
değerlendirme örneklemi büyütülerek telafi edilir. `test_normal`'da 123 görev
duruyor ve 123 görevde %10 başarı, 50 görevde %25 ile aynı ortak-çözülen
sayısını veriyor. Bedeli koşu süresi.

**Güç tabanının da altına düşerse** yerel yol kapanır ve kıyaslama değişikliği
ile model katmanı yükseltmesi arasında karar verilir.

**Elimizdeki en güçlü yerel sınıf veri noktası %5,4** (Qwen3-8B, FP16). Dört bit
hâli %3,0, yani kuantalama bedeli neredeyse yarısı. FP16'ya geçmek çözüm değil:
3B'nin üstünü sığdırmıyor ve eksende iki zayıf nokta bırakır.

Bunun anlamı açık: **`qwen3.5` geçmezse yerel hiçbir aile bu kıyaslamada
geçmez.**

### Eleme tasarımı

Her adayın sığan en büyük boyutu, bant taramasının en ayırt edici on iki
görevinde: referans uzunluk bandı 1-10'un altısı ve 11-20'nin altısı. Sınır
kontrolünde DeepSeek bu iki bantta 4/6 ve 6/6 aldı, qwen2.5-coder 7B ikisinde de
0/6.

Bir aday burada sıfır alıyorsa otuz görevde %25 eşiğini geçemez ve tam koşu
israf olur. Sıfırdan farklı alan adaylar otuz görevin tamamında koşuluyor.

**Bütçeler bağlayıcı olmayacak şekilde ayarlanıp raporlanıyor** (K-60). Her
adayda kodsuz adım ve ayrıştırılamayan adım oranı ayrı veriliyor.

**Sığan boyut sayısı ölçülerek doğrulanıyor, manifest boyutundan değil.**
`qwen3.5:9b` 6,6 GiB ve tavanın üstünde; kartta tam oturup oturmadığı yüklenip
ölçülüyor. Taşarsa bir küçük boyuta düşülüyor, **ve o durumda sığan boyut
sayısının üçün altına inip inmediği yeniden kontrol ediliyor** — inerse aile
şart 2'yi kaybediyor.

**Aile kontrolü ayrı seçiliyor**, ana eksen belirlendikten sonra: farklı bir
aile, ana eksenin en büyük noktası bandında, tek nokta, ön koşulu geçmiş.

## 2. Ayar bütçesi

**Kural.** Kurulum verisini gördükten sonra kaç parametre revizyonuna izin
verildiği önceden yazılıyor. Bütçe tükendikten sonra olumsuz sonuç parametreler
hakkında değil **tasarım hakkında** bir sonuçtur.

**Bugüne kadar tüketilen dört revizyon:**

| # | Revizyon | Ne değişti |
|---|---|---|
| 1 | Tavan çapası | Referans çözüm uzunluğundan doğrulayıcının beklediği çağrı sayısına, sonra `metadata.num_api_calls`'a (K-11, K-44) |
| 2 | Soğuk rejim | Isınmış rejim tekdüze olmadığı için epizot öncesi boşaltmaya geçildi (K-21) |
| 3 | Ön koşul eşiği | "Taban etkisinde mi" tanısından sansür/başarı temelli ölçüte (K-53, K-58) |
| 4 | Model ailesi | Qwen2.5-Coder ön koşulu geçemedi, aile yeniden seçiliyor (A-06, K-61) |

**Bütçenin sayısı yazılmadı ve bu bir boşluk.** Sayı bu belge dondurulurken
konmalı; konmazsa kural işlemez hâle gelir, çünkü "tükendi" hükmü verilemez.

## 3. Kurulumda dokunulan görevler

**Kural.** Kurulum sırasında dokunulan görevler **değerlendirme örnekleminden
çıkarılıyor**. Biriktirme havuzunda kalabilirler.

Ölçülmüş hâli (`results/touched-tasks.json`):

| Bölme | Dokunulan | Toplam | Kalan |
|---|---|---|---|
| train | 13 | 90 | biriktirme havuzu, kısıt yok |
| dev | 0 | 57 | biriktirme havuzu, kısıt yok |
| test_normal | 45 | 168 | **123 görev değerlendirmeye kalıyor** |
| test_challenge | 0 | 417 | **dokunulmadı**, zorluk bölmesi temiz |

`test_normal`'dan çıkarılan kırk beş görev kimliği:

```
024c982_1  024c982_3  042a9fc_1  09b0ee6_1  09b0ee6_2  09b0ee6_3
0de03ea_3  1150ed6_1  1150ed6_2  13547f5_2  166f4ff_1  21abae1_1
29a7b7e_1  29a7b7e_2  2d9f728_1  31dc501_2  32616b5_1  32616b5_3
3b8fb7a_1  3b8fb7a_2  3d9a636_3  59fae45_2  5a83b05_2  5a83b05_3
652485c_2  652485c_3  7847649_1  83a7951_2  8ce6779_1  8ce6779_2
9016950_3  986aa4e_2  9dabbc9_2  a30375d_1  afc4005_1  afc4005_3
b6d1104_3  b9c5c9a_3  c77c005_1  c77c005_3  d194965_2  dac78d9_1
f3f60f0_2  ff58e36_3  ffe6d5e_1
```

Çıkarma sebebi sızıntı değil, **görülmüşlük**. Bu görevlerde hangisinin zor
hangisinin kolay olduğunu gördük ve yayımlanmış gpt-4o koşusunun görev başına
sonuçlarını inceledik. Görülen sonuçtan türetilen bir kapsam kısıtı kiraz
toplama olurdu.

Aile taraması bu kırk beş görev üzerinde koşmaya devam ediyor; onlar zaten
değerlendirmeden çıkmış durumda.

**Ek — 25 Eylül 2026: liste kayıttan üretiliyor.** Yukarıdaki tablo ve kırk beş
kimlik 28 Ağustos'ta ölçülen hâl; silinmiyor. Liste elle yazılmıştı ve kayıttan
dört görev geride kalmıştı. Artık `scripts/setup/build_touched_tasks.py` onu
kayıttan üretiyor ve dört okuyucu yalnız `zihin.touched` üzerinden okuyor
(`K-166`). Bugünkü sayılar:

| Bölme | Dokunulan | Toplam | Kalan |
|---|---|---|---|
| train | **90** | 90 | biriktirme havuzu, kısıt yok |
| dev | 0 | 57 | biriktirme havuzu, kısıt yok |
| test_normal | **49** | 168 | **119 görev değerlendirmeye kalıyor** |
| test_challenge | 0 | 417 | **dokunulmadı** |

Eklenen dört `test_normal` görevi: `0a9d82a_1`, `0a9d82a_2`, `0a9d82a_3`,
`0de03ea_1`. `train`'in 90'a çıkması biriktirmeyi etkilemiyor; genişleme havuzundaki
payını 65'ten 0'a indiriyor (ön kayıt A.10'un eki).

## 4. Kurulumda taranacak parametreler ve karar kuralları

| Parametre | Karar kuralı | Durum |
|---|---|---|
| Adım tavanı çarpanı `k` | Üç değerde taranıyor; **tavana çarpma oranı** bütün koşullarda %10'un altında kalacak şekilde seçiliyor (K-43) | taranmadı |
| Durma kuralı eşiği | Farklı eşiklerde tavana çarpma ve kategori 4 oranı; ayrıca kural kapalıyken toparlanma ölçülüyor | geçici değer **15**, uç nokta kümesi ölçütüyle, iki taraflı kalibre edildi (bölüm 6) |
| Ön koşul eşiği | Taban koşulunda ilan edilen asgari başarı oranı. Aile elemesi için kaba eşik %25 | kaba eşik yazılı, kesin sayı pilottan |
| Model ailesi | Bölüm 1 | koşuluyor |
| Aile kontrolü noktası | Ana eksen seçildikten sonra, farklı aile, en büyük nokta bandında, tek nokta, ön koşulu geçmiş | seçilmedi |
| Beceri derleyicisi değer eşiği | Asıl filtre; naif derleyiciyle karşılaştırmada anlamlı fark üretecek en düşük değer | derleyici yok |
| Sabit ilan etme eşiği | Kaç farklı görevde aynı değer görülmeli. Maliyet asimetrisi gereği yanlış dondurmaya karşı muhafazakâr | derleyici yok |
| Boşluk kısıtının büyüklüğü | Örüntü madenciliğinde izin verilen boşluk | derleyici yok |
| Hata indeksinin asgari boyutu | Terk kriterinin dayanağı; bu sayının altında "etki yok" hükmü verilemez | indeks yok |
| Gürültü tabanı | Artık varyansın üst sınırı, model başına, ölçüldüğü rejim belirtilerek | ölçüldü: kural açık rejimde model başına ≤%9,5 (S-21) |

## 5. Tanı metriklerinin tanımı

Hepsi kurulum rejimine ait. **Hiçbiri birincil metriğe ve yanlışlama kapılarına
girmiyor.**

### Zorunlu tanı metriği

**Model çağrısı bölü başarılı API çağrısı.** Yorumu ön kayıtta: oran hareket
etmiyorsa kazanç paketlemeden geliyor, hareket ediyorsa israfın azalmasından da
geliyor.

### Bağlayıcılık göstergeleri (K-60)

| Parametre | Gösterge |
|---|---|
| Çıktı bütçesi | kodsuz adım oranı |
| Bağlam penceresi | kesilen gözlem oranı, `was_truncated` |
| Adım tavanı | tavana çarpma oranı |
| Durma kuralı | `no_progress` ile kapanan epizot oranı |

Gösterge sıfıra yakın değilse sonuç bir **alt sınır** ve öyle yazılıyor.

### Kategori 4 oranı

K-36'nın dördüncü kategorisi: kod çalıştı, hiç API çağrısı üretmedi. Koşul
başına raporlanıyor (K-54).

**İki rejim karıştırılmıyor.** Ana deneyde oran durma kuralı açıkken ölçülüyor.
Kural kapalı ölçüm yalnız eşik seçimine hizmet ediyor. Makalede hangi oranın
hangi rejimden geldiği yazılıyor.

### Dereceli skor

**Tanım (aile taramasından önce yazıldı).** AppWorld'ün doğrulayıcısı her
gereksinimi etiketliyor: `no_op_fail` hiçbir şey yapmayan ajanın düşürdüğü test,
`no_op_pass` hiçbir şey yapmasa da geçen test.

**Dereceli skor = geçilen `no_op_fail` testlerinin toplam `no_op_fail` testine
oranı.** `no_op_pass` testleri sayılmıyor, çünkü ajan hiçbir şey yapmadığında da
geçiyorlar ve ilerleme kanıtı değiller.

**Statüsü tanı metriği.** İkincil sonuç değil. Birincil metriğe ve yanlışlama
kapılarına asla girmiyor.

**Veriyi gördükten sonra doğdu** ve bu açıkça yazılıyor: kurulum aşamasında,
ikili başarı her yerde sıfırken ayrım gücü olan tek nicelik olarak türetildi.

**Bu kullanım için önceden ilan edildi:** aile taramasında adayları
karşılaştırmak, ve ikili başarı sıfır olduğunda taban ile aday arasında fark
olup olmadığını görmek.

### Tavana çarpma oranı ile sansür oranı

**İki ayrı nicelik ve karıştırılmıyor.**

Tavana çarpma oranı bir **ölçüm artefaktı**: %10'un altında kalmalı ve tavan
çarpanı buna göre seçiliyor.

Sansür oranı doğrulayıcı hükmüne dayanıyor ve bir **sonuç**. Yüzde on kuralı
buna uygulanmıyor; uygulansaydı tabana %90 başarı şartı konmuş olurdu.

Sansür sonlandırma sebebine göre değil hükme göre sayılıyor: tavana çarpsın,
durma kuralıyla kapansın ya da ajan tamamlandı bildirsin. Sonlandırma sebebi
ayrı bir tanı alanı.

## 6. Ölçümü sessizce kesen şeyler

Bu bölüm belge donduktan sonra eklendi ve büyümeye devam ediyor. Eklenme sebebi
kayda geçiyor: her maddenin arkasında ölçülmüş bir arıza var ve hepsi aynı
aileden — bir şeyin kimse fark etmeden eksilmesi. Kimi zaman eksilen bir epizot,
kimi zaman bir küme, kimi zaman da bir ölçütün kendisi.

### Bir epizodu sonlandırabilen her parametre ölçüm aletidir, tesisat değil

**Kural.** Etkilediği hiçbir ölçüm alıntılanmadan önce kalibre edilecek.

Gerekçe ölçülmüş. Durma kuralının eşiği tesisat muamelesi gördü ve geçici değeri
dörttü. Sınır kontrolünün yirmi başarılı epizodunun dokuzunda durgunluk dörde ya
da üstüne çıkıyordu, yani eski eşik başarıların yaklaşık yarısını kesebilirdi.
Bant taramasının otuz epizodunun on altısı `no_progress` ile kapandı — yüzde elli
üç — ve o on altının on beşi düzeltilmiş kuralla kesilmezdi. Ön koşul kapısı
kesilmiş bir taramaya dayanarak ateşlemişti.

Kalibrasyonun iki tarafı da gerekiyor: eşik hem gereksiz adımı kesmeli hem
başarabilecek epizodu kesmemeli. Tek tarafa bakmak ikinci bir hata üretti; eşik
on yazıldığında yanlış pozitif tarafı ölçülmemişti, on beşe çıkmasının sebebi o.

**Kapsama giren parametreler:** durma kuralı eşiği, adım tavanı ve çarpanı, çıktı
jetonu bütçesi, bağlam penceresi. K-60 bunların bağlayıcılığının gösterilmesini
zaten istiyor; buradaki ek şart kalibrasyonun ölçümden **önce** yapılması.

### Eksik bir epizot kümesi asla alıntılanmaz

**Kural.** Küme ya tamamlanır ya koşu atılır. Tek kural, iki uygulama.

**Gerekçe: uzunluk yanlılığı.** Kesinti uzun bir epizoda kısa olandan daha büyük
olasılıkla denk gelir. Hayatta kalanlar tutulursa eksik olanlar sistematik olarak
zor görevler olur ve başarı oranı yukarı yanlı çıkar. "Elimizde şu kadarı var,
onu kullanalım" bu yüzden geçerli değil: eksiklik rastgele değil.

**Kurulum ve kalibrasyon koşuları: sıfırdan tekrar, yeni önekle.** Yarıda kesilen
bir tarama bırakılıyor, öneki bir daha kullanılmıyor, o kümeye ekleme yapılmıyor.
Kod bunu zaten zorluyor: koşu kimliği künyenin birincil anahtarı ve
`scripts/setup/measure_band.py` öneki komut satırından alıyor.

**Ana koşu: epizot düzeyinde devam.** Sıfırdan tekrar burada uygulanabilir değil.
Kesintiler arası süre koşu süresinden kısaysa tamamlanma olasılığı sıfıra gider
ve kural ölçümü yasaklamış olur; ölçümü engelleyen temkinlilik temkinlilik değil.
Devam üç şart altında meşru: tamamlanmış epizot kümesi dosya sisteminden değil
veritabanından okunuyor, açılış kimliği künyeye giriyor, kesinti sonrası bütünlük
denetimi koşuluyor.

Garanti iki uygulamada da aynı. Ana koşu için gevşetilmiş bir kural yok, yalnız
tamamlamanın yolu farklı.

### Epizot niye atomik

Epizodun bütün satırları en sonda tek işlemde yazılıyor (`scripts/record_run.py`).
Yarıda kesilen bir epizot yarım satır bırakmıyor, hiç satır bırakmıyor. Bant2
denemesi bunun kanıtı: otuz epizot da düştü ve veritabanına tek satır girmedi.

Epizotlar birbirinden bağımsız. Tohum görev ile modelden türüyor, sıradaki
konumdan değil; model epizot öncesi boşaltılıyor ve boşaldığı doğrulanıyor; etkin
bağlam penceresi her epizotta yeniden doğrulanıyor; künye epizot başına yazılıyor
ve sunucu ayarlarını o anda okuyor. Yani kesintiden sonra koşullar değişmişse bu
veriye giriyor, sessizce kaybolmuyor.

### Kesinti sonrası bütünlük denetimi

Kesintiye açık kalmış bir veritabanına eklemeden önce dört şey ölçülüyor:

| Ne | Beklenen | Ölçülen (13 Ağustos 2026) |
|---|---|---|
| `PRAGMA integrity_check` | `ok` | `ok` |
| `PRAGMA synchronous` | 1, 2 ya da 3; **0 (OFF) kabul edilmiyor** | 2 (FULL) |
| `PRAGMA journal_mode` | `off` ve `memory` dışında | `delete` |
| Son epizodun satır kümesi | epizot + adım + eylem + gözlem + doğrulayıcı hükmü | ölçülmedi |

`synchronous` OFF ise commit edilmiş bir işlem bile sert kesintide
kaybedilebilir, o hâlde eksilme uzunluğa göre yanlı olur ve yukarıdaki kural
ihlal edilir. Son iki pragma künyeye yazılıyor ve şemadaki CHECK dayanıksız ayarı
reddediyor: dayanıksız bir depoya künye yazılamıyor.

İlk üçü tek komut:

```bash
uv run python -c "
from zihin.records import open_database, storage_durability
b = open_database('results/zihin.sqlite')
print(b.execute('PRAGMA integrity_check').fetchone()[0], storage_durability(b))"
```

Dördüncüsü, son epizodun satır kümesinin eksiksizliği:

```bash
uv run python -c "
from zihin.records import open_database
b = open_database('results/zihin.sqlite')
print(dict(b.execute('''
  SELECT e.episode_id, e.termination_reason,
         (SELECT COUNT(*) FROM steps WHERE episode_id = e.episode_id) steps,
         (SELECT COUNT(*) FROM verifier_results WHERE episode_id = e.episode_id) verdicts
  FROM episodes e ORDER BY e.episode_id DESC LIMIT 1''').fetchone()))"
```

`steps` sıfırsa ya da `verdicts` sıfırsa epizot yarım yazılmıştır ve o epizot kümeden
düşer — ama epizot tek işlemde yazıldığı için bu beklenmiyor. Beklenmeyen şeyi
ölçmenin sebebi K-49: bir şeyin çalıştığını görmek doğru sebeple çalıştığını
göstermez.

### Kural-kapalı koşu: tetikleyici ve üç sonucun yorumu

**Bu bölüm `bant3` taraması koşarken, sonucu görülmeden yazıldı (K-62).**

**Tetikleyici.** Tarama sıfır çıkarsa, **durma kuralıyla kesilen** epizotlar kural
kapalı olarak tekrar koşuluyor. Yalnız kesilenler; `agent_finished` ile bitenler
değil.

**Pay eşiği yok ve bilerek yok.** Sonuç sıfırken kesilen her epizot ilkesel olarak
"başarabilecek olan" adayı. Pay yüzde on da olsa yüzde seksen de olsa aynı soru
soruluyor. Eşik koymak cevabı payın büyüklüğüne bağlamak olurdu; mesele payın
büyüklüğü değil, sıfırın temizliği.

**Neden masa başında ayrılamıyor.** "Kural sonucu bozmadı" demenin gerekçesi
güçlü: eşik iki taraflı kalibre edildi, sınır kontrolünün geçen epizotlarında
durgunluk en fazla on ikiye çıkıyordu ve eşik on beş. "Bozdu" demenin gerekçesi de
güçlü: o kalibrasyon **başka bir modelin** başarılı epizotlarından geldi. Yerel
modelin başarılı epizodu hiç olmadığı için doğrudan kalibrasyon yapılamıyor.
Kural-kapalı koşu bu boşluğu kapatan tek ölçüm.

**Maliyet kabul edildi.** Epizotlar tavanlarına kadar gidiyor, muhtemelen birkaç
saat. Projenin bütün yönü bu sıfıra bağlı.

| Sonuç | Yorum |
|---|---|
| Kural kapalıyken de sıfır | Durma kuralı sebep değil. 0/30 temiz, ön koşul kapısı sağlam veriye dayanmış olur, aile taramasına geçilir. |
| Sıfırdan farklı | Eşik bu model sınıfı için yanlış. Elimizde artık bu modelin başarılı epizotları olur; eşik onlarla yeniden kalibre edilir, tarama tekrarlanır, aile kararı yeniden açılır. |
| Sıfır ama dereceli skor belirgin yükseliyor | Kural başarıyı değil ilerlemeyi kesiyor. Kapıyı değiştirmiyor; kayda geçiyor ve ana koşuda eşiğin gevşetilmesi tartışılıyor. |

### Sonuçtan bağımsız tanı: bu model sınıfının baskın arızası durma, bütçe değil

Sonlanma sebebinin sınıfı eski kuralla yeni kural arasında yer değiştirdi:

| Sonlanma | Eski kural (bant, 30 epizot) | Yeni kural (bant3) |
|---|---|---|
| `no_progress` | 16 | ölçülüyor |
| `step_ceiling` | 9 | ölçülüyor |
| `agent_finished` | 5 | ölçülüyor |

Eski kuralda dokuz epizot tavana çarpıyordu. Yeni kural tam da o "üretken görünüp
hiçbir yere varmayan" sınıfı yakalıyor: on beş ardışık adımda yeni uç nokta yok ve
durum değişmiyor.

**Bu, sonuç ne olursa olsun raporlanacak bir bulgu.** Model bütçesini tüketerek
değil, döngüye girerek kaybediyor. Adım tavanını büyütmek bu sınıfa bir şey
kazandırmaz.

### Koşan bir ölçümün içe aktardığı kaynak koşu sırasında düzenlenmiyor

**Kural.** Bir tarama koşarken `src/zihin/**` ve `scripts/record_run.py`
düzenlenmiyor. Tarama epizotları alt süreç olarak koşturuyor ve her alt süreç
kaynağı diskten yeniden okuyor; ortada yapılan bir düzenleme, epizot kümesinin
yarısını başka kodla koşturur.

**Künye bunu eskiden yakalayamıyordu.** `code_commit` HEAD'i yazıyor, çalışma
ağacını değil; commit edilmemiş bir değişiklik bütün epizotlarda aynı
`code_commit` altında görünüyordu.

**Kapatıldı.** Kirli çalışma ağacı artık ölçüm koşusunu engelliyor. Geçersiz
kılmak açık bir bayrak istiyor ve bayrak künyeye yazılıyor (`working_tree`).
Böylece `code_commit` gerçekten bir şey ifade ediyor: temiz koşuda HEAD kodun
tamamı, kirli koşuda künye bunu söylüyor. Kurulum keşfi engellenmiyor,
işaretleniyor.

Git okunamazsa değer `unknown` ve koşu yine engelleniyor: temiz olduğu
doğrulanamayan ağaç temiz sayılmıyor.

Bu kural 13 Ağustos 2026'da `bant3` taraması koşarken ihlal edildi ve ihlalin
atıl olduğu ölçüldü: `records.py`'ye eklenen sabit ve fonksiyon `record_run.py`
tarafından içe aktarılmıyor, dosyada silinen ya da değiştirilen satır yok (`git
diff --numstat` sıfır silme), taramada düşen epizot yok. Atıl olması kuralı
gereksiz kılmıyor; bir sonraki sefer atıl olmayabilir.

### Devam eden bir koşu, koşulun aynı olduğunu doğrulamadan devam etmiyor

**Kural.** Yarıda kesilen bir koşuya devam ederken, yazılmış epizotların koşulu
şimdi koşulacakla karşılaştırılıyor. Uyuşmazsa koşu reddediliyor ve küme yeni bir
önekle sıfırdan koşuluyor.

Atlama tek başına yetmiyor: eksiksiz yazılmış bir epizot atlanır, ama hangi
koşulda yazıldığı sorulmazsa küme iki farklı ölçümün karışımı olur. Künye bunu
kaydeder ve **engellemez** (S-31).

Koşul tanımlayıcı alanlar: model, sunum kipi, sıcaklık, taban tohum, çıktı
bütçesi, durma eşiği, bağlam penceresi, KV cache tipi, flash attention, AppWorld
commit'i, yönerge özeti, kütüphane kimliği, çalışma ağacı, **koşul**, **bölme** ve
**adım tavanı**.

Koşulun listede olması ana koşuda kritik: taban koşuluyla mekanizmalı koşunun
epizotlarının aynı kümede birleşmesi tam olarak engellemek istediğimiz şey.

`code_commit` reddedilmiyor ama iki commit arasındaki dosya farkı listeleniyor, ve
epizot içinde ne olduğunu belirleyen yollardan biri farkta görünürse uyarı redde
yükseliyor. Hangi epizodun koşacağını belirleyen kod listenin dışında.

### Ölçümü etkileyen hiçbir parametre ortamdan okunmuyor

**Kural.** Ortam yalnız gizli değerleri ve sunucudan geri okunan değerleri
taşıyor. Ölçümü etkileyen her parametre yapılandırmada ve **sessiz varsayılanı
yok**; belirtilmezse koşu düşüyor.

Kural yazılıydı ve `max_output_tokens`'a uygulanmamıştı. Sessiz varsayılanı 400'dü
ve bir sınır kontrolü koşusu yanlış bütçeyle başladı (S-30). Aynı model aynı otuz
görevde 400'de 6/30, 4000'de 20/30 veriyor.

**Önleyen düzeltme, tespit edenden değerli.** Devam denetimi bu karışımı yakalar;
yapılandırmaya taşımak baştan olmasını engeller. İkisi de yapıldı.

### Bir kısıtın yazıldığı yerde durması uygulandığı anlamına gelmiyor

**Kural.** Kısıtın **uygulandığı yer** ölçülecek, yazıldığı yer değil.

Gerekçe S-29. Künye sözleşmesinin makine tarafı `schema.sql`'e yazıldı, iki test
onu şema düzeyinde sınadı ve testler geçti — ama şema yalnız sıfırdan kurulan
dosyada uygulanıyor ve SQLite'ın `ALTER TABLE`'ı kısıt taşımıyor. Canlı
veritabanında sözleşmenin makine tarafı hiç yürürlüğe girmemişti. Testler taze
dosya kurduğu için bunu göremezdi; PR bu hâliyle onaylandı.

Somut hâli: bir kısıt eklendiğinde, kısıtın **koşuda kullanılan dosyada** var
olduğu okunacak. Şemayı okumak yetmiyor; `sqlite_master`'daki gerçek tanım
okunacak.

### Ölçüm serileri ayrı, her sayı serisiyle birlikte

İki seri var ve ikisi de canlı:

| Seri | Dosya | Ne var, ne yok |
|---|---|---|
| 1 | `results/zihin.sqlite` | Eski durma kuralı (eşik 4), künye sözleşmesinin makine tarafı yok. 62 künye, hepsi `local`, yalnız üç `qwen2.5-coder` boyutu. **Okunuyor, yazılmıyor.** |
| 2 | `results/zihin-2.sqlite` | Düzeltilmiş durma kuralı (eşik 15), tam künye sözleşmesi, açılış kimliği ve duvar saati. |
| 3 | `results/zihin-3.sqlite` | Kalkan kipi kısıtı da yürürlükte. Seri 2'ye eklenemedi çünkü `ALTER TABLE` kısıt taşımıyor (S-29); nöbetçi 32B ölçümünü tam bu yüzden reddetti ve seri açıldı. |

**Seri 1 arşiv değil, canlı referans.** Ayakta kalan iki teşhis ondan besleniyor.

**Seri 2 de arşiv değil.** Bant taramaları, sınır kontrolü ve kart koşusu orada; yeni ölçüm yazılmıyor, ama okunuyor ve alıntılanıyor.

**Kural.** Bir sayıyı alıntılayan her rapor hangi seriden geldiğini yazar. Aksi
hâlde ileride tek dosyayı sorgulayan biri onu bütün sanar.

### Var olması zorunlu bir alan `.get()` ile okunmaz

**Kural.** Zorunlu alan doğrudan indekslenecek ve yoksa hata fırlatacak; ya da
şema girişte bir kez doğrulanacak. `.get()` sessizce None döndürüyor.

Gerekçe S-32 ve daha genel olarak bu deponun bütün arıza geçmişi: arızaların
tamamı sessiz None'lardan çıktı. Durma kuralı, `api_calls.jsonl` satırlarında
bulunmayan `app` ve `api` anahtarlarını `.get()` ile okudu, her çağrı `None.None`
oldu ve uç nokta ölçütü hiç çalışmadı. Hata istisna fırlatsaydı ilk epizotta
görülürdü.

### Kurala giren veri ile kayda giren veri aynı yoldan gelecek

**Kural.** Bir ölçüt ile onun kaydı iki ayrı kaynaktan beslenmeyecek. Beslenmek
zorundaysa aralarındaki fark ölçülecek ve rapor edilecek.

Gerekçe yine S-32. Veritabanına yazılan uçlar yakalayıcıdan geliyordu ve
doğruydu; kuralın okuduğu uçlar günlükten geliyordu ve hiçbiri çözülmüyordu. İki
yol arasındaki bu fark hiçbir yerde görünmüyordu, çünkü karşılaştıran bir şey
yoktu. Aynı dosyada sayı ayrışması zaten ölçülüyordu — biçim ayrışması
ölçülmüyordu.

### Sağlık ölçütü: ölçüt kendi üzerinde dejenere olmuş mu

**Kural.** Ölçütün girdisinin dejenere olduğu, ölçümün kendisinden okunabilecek
bir sayıyla sınanacak ve o sınama ölçüm koşusunun içinde, otomatik olarak
koşacak.

Somut hâli: çok çağrılı bir epizotta durma kuralının gördüğü **farklı uç nokta
sayısı** bire düşüyorsa çözümleme çökmüş demektir. `record_run.py
--health-check` bunu koşu sonunda sınıyor ve bant taramasının ön kontrolü
bayrağı kendiliğinden veriyor. Sınır kontrolü aynı sayıyı ilk epizottan sonra
denetliyor, çünkü orada her epizot para harcıyor.

Bu ölçüt hatayı ilk gün yakalardı: bozuk kural her epizotta tam olarak bir uç
noktası görüyordu.

### Testin sahte verisi gerçek üreticinin biçiminden gelecek

**Kural.** Bir birim testinin kurduğu sahte kayıt, o kaydı gerçekte üreten şeyin
biçimine karşı çivilenecek.

Gerekçe S-32'nin en derin katmanı: durma kuralının on iki birim testi de geçiyordu
ve hepsi aynı uydurma biçimi kullanıyordu. Test, kodun varsaydığı biçimi
tekrarlıyordu, ürettiği biçimi değil. İkisi ayrıldığında ikisi birden yanıldı.

Somut hâli: `tests/data/` altında gerçek bir koşudan gelen bir günlük duruyor,
testler adımları o biçimle kuruyor ve anahtar kümesi ayrıca sınanıyor.

### Bir kapıya zincirlenen her komutun çıkış durumu kapıya bağlanır

**Kural.** Bir kapının önünde koşan her komutun çıkış durumu kapıyı gerçekten
durduracak biçimde bağlanacak, ve bağ **komut kasten düşürülerek** sınanacak.

> Bir kontrolün koşması, sonucunun bir şeyi engellediği anlamına gelmiyor.

Gerekçe: aynı spesifik şey iki kez oldu.

Birincisi doğrulama aletiydi. Alt süreçleri `check=True` olmadan çağırıyordu;
çöken bir kalibrasyon önceki çıktıyı yerinde bıraktı, alet **bayat dosyayı**
okuyup "aynı" dedi, ve bir commit doğrulanmış diye raporlandı, oysa değildi.

İkincisi test takımıydı. `pytest` komutu commit'in önünde koşuyordu ama çıkışı
`&&` ile bağlı değildi; takım düşerken commit geçti.

İkisinde de kontrol koştu, çıktısını gördüm, ve hiçbir şeyi engellemedi.

Somut hâli: zinciri kurduktan sonra komutu bir kez kasten düşür ve kapının
kapandığını gör. Bağın kendisi de bir arayüz, ve sınanmamış arayüz çalışmıyor
sayılır.

### Doğrulayıcıya karşı ölçülmüş olmak, dal testlerinin yerine geçmez

**Kural.** Bir modülün bir doğrulayıcıya karşı ölçülmüş olması onu sınanmış
saymıyor. İkisi ayrı ayrı gerekiyor.

Ayrım şu. **Ölçüm**, çıktının bir örneklemde doğrulayıcıyla ne kadar uyuştuğunu
söylüyor. **Test**, mantığın dallarında iddia ettiği şeyi yapıp yapmadığını
söylüyor. Birincisi bir sayı, ikincisi bir davranış iddiası, ve biri diğerini
kanıtlamıyor.

Gerekçe ölçülmüş. `allowed_apps.py` train + dev üzerinde 147 göreve karşı
ölçüldü, %75,5 tam eşleşme ve 0,857 Jaccard verdi, rapora girdi, kalkana monte
edildi — ve **tek satır testi yoktu**. Altyapı uygulamalarının koşulsuz izinli
olduğu kuralı kodda vardı ama hiçbir yerde çivili değildi; düşseydi kart
kullanan her görev yanlış engellenirdi ve %75,5 bunu görmezdi, çünkü o sayı
uygulama kümesini ölçüyor, kuralın yürürlükte olduğunu değil.

**Tehlikeli olan tam da uyum.** Yüzde 75,5 modülü doğrulanmış gibi gösterdi ve
test yazma ihtiyacını hissettirmedi. Yüksek bir sayı, kapsanmamış bir dalı
gizleyen en iyi örtüdür.

### Her yol haritası maddesi kapanış notuyla kapanır

**Kural.** Bir madde kapandığında `docs/reports/mekanizma-kapanis-notlari.md`
dosyasına kısa bir not düşer: ne kuruldu, ne ölçüldü, bitmiş sayılma
şartlarının yedisinden hangileri sağlandı.

**Gerekçe.** Yoksa pilot raporu yazılırken her sayı yeniden türetilir ve
ölçümler raporlara dağılır. Bu depoda yazma kümesi tek günde iki kez değişti;
aynı ölçüm iki farklı sayı verdi ve hangisinin hangi yapılandırmada alındığını
söyleyen tek şey kaydın kendisiydi.

Sağlanmayan şart varsa **sebebiyle** yazılır. Boş bırakmak, sağlanmış gibi
okunuyor.

### Her yol haritası maddesi kendi PR'ıyla kapanır

**Kural, dört parçalı.** Her yol haritası maddesi kendi PR'ıyla kapanıyor.
Maddenin kapanış notu PR açıklamasına giriyor. Madde bitmeden PR açılmıyor, ve PR
açılmadan sonraki maddeye geçilmiyor. Dal adı çalışılan maddeyi taşıyor
(`madde-3-derleyici` gibi), içeriğini anlatmayan bir ad taşımıyor.

**Gerekçe ölçüldü, ve bedeli sayıldı.** Kurulum fazında "her aşama bir PR" kuralı
vardı; mekanizma yol haritasına taşınmadı ve akış PR #19'dan sonra durdu. Yedi
maddenin tamamı tek dalda, 52 commit olarak birikti.

Bedel iki yerden çıktı. Birincisi: **CI o commit'lerin hiçbirini görmedi.** Dal
itilmediği için o günkü dört kontrol koşmadı, ve itildiğinde 45 test kırmızı çıktı — iki
ayrı ortam farkı yüzünden, ikisi de yerelde görünmez (S-49). İkincisi: geriye
dönük bölme, doğal olmayan sınırlar üretti — bir commit iki maddeye ait çıktı ve
bölünemedi, çünkü bölmek tarihi yeniden yazmak olurdu.

**Bölme zorlanmıyor.** Commit'ler doğal bir sınıra oturmuyorsa gruplanabildiği
kadar gruplanıyor ve nedeni PR açıklamasına yazılıyor. Yol haritası maddesi
olmayan iş de kendi PR'ında, "madde değil" diye etiketlenerek açılıyor.

**Beş CI işinin beşi de her PR'da yeşil.** Kırmızı bir kontrol, birleştirme kararını
değil düzeltme işini başlatıyor.

**PR raporu yeni ad listesi taşıyor** (K-102). Rapor, o PR'da eklenen modül
dosyası adlarını ve yeni public tanımlayıcıları ayrı bir bölümde sayıyor; yoksa
"yok" yazıyor. Sebebi ölçüldü: dil kuralı tanımlayıcıların İngilizce olmasını
istiyordu ve kural yeniden adlandırma turundan önce kondu, ama ileriye dönük
uygulanmadı — madde 8 `kayit_vekili.py`, `konteyner_girisi.py`,
`soket_koprusu.py` ve `SahteDunya` gibi adlar üretti. İnceleme diff üzerinden
değil rapor üzerinden yapılıyor, yani kuralın yaşayabileceği tek yer rapor.
ASCII denetimi bunu yakalamıyor: `kayit_vekili` zaten ASCII.

### Asgari indeks boyutu getirilebilir kalıp sayısıdır, indeks satırı değil

**Kural.** Mekanizma başına terk kriterinin dayandığı "indeks ilan edilen asgari
boyutta" şartı, getiricinin **ulaşabildiği** kalıpların sayısıyla ölçülür. İndeks
satır sayısı bu şart için geçerli bir sayı değil.

**Gerekçe ölçüldü.** İndeksteki en sık kalıp — `GET api_docs.api_descriptions`,
150 hata — hiçbir görev tarafından getirilemiyor: sembol uygulama ve altyapı
uygulamaları getiricide düşüyor (K-86, S-48). Yani 15 satırlık indeksin
getirilebilir boyutu 14, ve fark her zaman bu kadar küçük olmak zorunda değil.

Getirilemeyen satırlarla dolu bir indeks **yeterli görünür** ve mekanizmayı
haksız yere aklar: terk kriteri "indeks yeterince büyüktü, demek ki mekanizma
denendi" der, oysa modele hiç ulaşmayan bir kalıp denenmemiştir. Aynı kural
becerilere de uygulanıyor: kütüphane boyutu getirilebilir beceri sayısı.

### Rapor sayıyı kopyalamaz, veri setine atıf verir

**Kural.** Bir raporun dayandığı sayılar makine okunur tek bir veri dosyasında
durur. Rapor manşet sayıları düzyazıda söyler ama tabloları, ızgaraları ve
dağılımları kopyalamaz; dosyayı ve içindeki yolu gösterir. Veri dosyası her
girdisinin özetini (sha256) yazar.

**Gerekçe.** Kopyalanan sayı kaynağından bağımsız yaşlanır. Bu depoda yazma
kümesi tek günde iki kez değişti ve aynı ölçüm iki farklı sayı verdi; sekiz ayrı
çıktıdan elle taşınan bir tabloda hangi sayının hangi yapılandırmadan geldiği
görünmez.

**Veri seti girdilerinin tutarlılığını kendisi denetler.** Farklı ölçümler aynı
kütüphaneden mi geliyor — `library_id` ve `index_id` ayrışırsa kurulum durur. İki
kütüphaneden gelen sayılar tek sonuç gibi okunurdu ve fark hiçbir yerde
görünmezdi. Somut hâli `scripts/setup/build_pilot_dataset.py`.

### Bir ölçüm, ölçtüğü şeyin üretim uygulamasını çağırır

**Kural.** Ölçüm betiği ölçtüğü mantığı yeniden uygulamaz, üretimdeki
uygulamayı çağırır. Yeniden uygulama iki farklı doğru cevap üretir ve
hangisinin doğru olduğunu ayırt edecek bir şey yoktur.

Gerekçe ölçülmüş, ve kural aynı oturumda kendi ihlalini yakaladı. Kalkanın
yanlış pozitif oranını yeni bir yazma kümesiyle ölçmek için `writes_of`
yeniden yazıldı ve **sıfır** verdi; üretim yolunun aynı girdiyle verdiği cevap
altıydı. Fark URL ayrıştırmasındaydı. İki uygulama iki sayı üretti ve sayıya
bakarak hangisinin bozuk olduğu görülemezdi — yalnız bilinen bir referans
değerin tutmaması ele verdi. Referans değer olmasaydı ölçüm sessizce yanlış
olurdu.

Somut hâli: `importlib` ile üretim modülünü yükle ve fonksiyonunu çağır.
Değiştirmek istediğin şey girdi olsun, kod değil.

### Küçük olmak doğru olmak değil

**Kural.** Bir oran küçük çıktığında tek tek vakalara bakılacak. Küçüklük
doğruluk kanıtı sayılmıyor.

Gerekçe ölçülmüş. Gölge modunun ilk koşusu %0,09 engelleme oranı verdi —
9154 çağrıda 8. O sayıya bakıp geçmek mümkündü. Sekiz çağrının her birine
bakınca ikisinin `phone.show_contact_relationships` olduğu, onun da saf bir
okuma olduğu, ve yazma kümesine bir Python `set` metodu üzerinden girdiği
çıktı (S-37). Yüzde sıfır virgül dokuz hiçbir zaman kendini göstermez.

**Düzeltme, 15 Kasım 2026.** Sekiz engellemeden biri `tests/test_appworld_reset.py`'nin
kendi açtığı nottu: test çıktısını korpusa yazıyordu (S-83). Onsuz ilk koşu 9145 çağrıda
7 engelleme, %0,08. Kuralın gerekçesi değişmiyor: iki saf okuma yine oradaydı.

Aynı şey büyük oranlarda gerekmiyor, çünkü büyük oran zaten inceleniyor.
Tehlikeli olan küçük oran: sessiz kalıyor ve doğruymuş gibi duruyor.

### Bir fonksiyonun davranışı değişince çağıranın düzeltilmiş yolu koştuğu ayrıca doğrulanır

**Kural.** Düzeltme yalnız tanımda yapılmaz. Çağıranların düzeltilmiş yolu
gerçekten çalıştırdığı ölçülerek gösterilir.

Gerekçe ölçülmüş. Rota çözümleyicisine yöntem parametresi eklendi ve ayrım
doğrulandı, ama ölçüm betiği çözümleyiciyi yöntemsiz çağırmaya devam ediyordu.
Fonksiyon düzelmişti, çağıran düzelmemişti, ve düzeltme ölçümde hiç görünmedi.

**Statik imza denetimi bu sınıfı yakalamıyor.** O denetim eksik ya da fazla
anahtar kelimeyi görüyor; **varsayılanı olan bir parametreyi atlayan çağıranı
göremiyor**, çünkü öyle bir çağrı geçerli. Yeni bir parametreye varsayılan
vermek geriye dönük uyumluluk sağlıyor ve tam o yüzden sessiz kalıyor.

Somut hâli: düzeltmeden önce ve sonra aynı ölçüm koşulur ve sayının değiştiği
gösterilir. Değişmiyorsa ya düzeltme etkisiz ya çağıran eski yolda.

### Doğrulama bir görevin değil, bir ağaç durumunun özelliği

**Kural.** "Doğrulandı" demek her zaman bir commit'e bağlıdır. Temel çizgi
karşılaştırması hangi commit'e karşı alındığını kaydeder, karşılaştırma hangi
commit'te koştuğunu yazar, ve **ağaç kirliyse doğrulama ilan edilmez.** Ağaç
değişirse doğrulama yeniden koşulur.

Künyedeki `code_commit` disiplininin aynısı, ölçüm yerine doğrulamaya
uygulanmış hâli. Gerekçe ölçülmüş: bir commit "doğrulandı" diye kapatıldı,
ardından tek bir anahtar düzeltildi ve doğrulama tekrarlanmadı; o düzeltme
betiği düşüren bir hata taşıyordu.

**İkinci şart: aletin kendisi yanlış pozitif vermemeli.** Karşılaştırma betiği
alt süreçlerin çıkış kodunu denetlemiyordu. Kalibrasyon düştü, hiçbir dosya
yazmadı, karşılaştırma bir önceki koşudan kalan dosyaları okuyup "birebir aynı"
dedi. Bayat dosya üzerinde koşan bir karşılaştırma **her zaman** aynılık
raporlar, yani alet sessizce daima yeşil olur.

**Sonuç, geriye dönük.** Eski aletle yapılmış hiçbir doğrulama kanıt değil —
tanımlayıcı yeniden adlandırmasının doğrulaması dahil. Geçerli tek doğrulama
`09cbde6` commit'inde, temiz ağaçta ve damgalı temel çizgiyle alınmış olandır.

### Ayrıştırılan her dize bir arayüzdür

**Kural.** Eşleştirilen, karşılaştırılan ya da ayrıştırılan bir dize düzyazı
değil arayüzdür. Dil geçişinde önce tespit edilir; sonra ya olduğu gibi bırakılır
ya da eşleştiren kodla **aynı commit'te** değiştirilir.

Kapsam: `pytest.raises(match=)`, `in` ve `startswith` kontrolleri, düzenli
ifadeler, eşitlik karşılaştırmaları, ayrıştırma sınırlayıcıları. Çevrilirse
eşleştiren kod ya sessizce kırılır ya sessizce hep doğru döner.

Dil geçişinde 169 arayüz dizesi bulundu, 20'si Türkçeydi ve üç sınıfa ayrıldı:
istisna mesajına bağlı testler (mesajla aynı commit'te değişti), test verisi
(dosya içinde tutarlı değişti) ve **kaynak belgeye bağlı ayrıştırıcılar**
(dokunulmadı, bkz. S-33).

### Koruma, koruduğu şeyden daha az kırılgan olmalı

**Kural.** Bir kalıba dayanan üretimi koruyan denetim, o kalıptan daha dayanıklı
bir şeye dayanmalı.

Somut hâli S-33'te: karar CSV'si Türkçe düzyazı kalıplarıyla üretiliyor, ama
tamlık denetimi `\b[KA]-\d+\b` kimlik kalıbına bakıyor — hiçbir Türkçe sözcüğe
bağlı değil. Denetim, koruduğu ayrıştırıcı bozulduğunda ayakta kalıyor.

Bir alt sınır denetimi bu özelliği taşımıyordu ve ayrıca kısmi kaybı
yakalamıyordu: yetmiş kaydın kırkı kaybolsa eşik ya çok gevşek ya çok sıkı olur.
Tamlık denetimi kendi kendini de bakımlı, kayıt sayısı arttıkça eşik güncellemek
gerekmiyor.

### Uptime tek başına yetmiyor

`created_at` `/proc/uptime`'dan geliyor, açılış içinde hassas, ama yeniden
başlatmada sıfırlanıyor: kesintiden sonraki epizodun başlangıcı öncekinden küçük
çıkıyor ve sıralama sessizce bozuluyor. Bunun nadir olmadığı ölçüldü — WSL sanal
makinesi boşta kaldığında kapanıyor, yani uptime elektrik kesintisinden bağımsız
olarak da sıfırlanıyor.

Künyeye iki alan girdi. `boot_id` birleşme yerini görünür kılıyor: değeri farklı
olan iki künye ayrı açılışlarda koşmuş demektir. `wall_clock_utc` açılışlar arası
sıralamayı geri veriyor, çünkü boot_id rastgele bir UUID ve tek başına sıra
vermiyor; değeri SQLite'ın `CURRENT_TIMESTAMP`'inden geliyor, süreç içinde
hesaplanan bir zaman AppWorld'ün freezegun kullanımı yüzünden donmuş olabilir.
Uptime alanı açılış içi hassasiyet için duruyor.

### Bir testin işaretleri konusuna göre değil, bağımlılıklarına göre belirlenir

**Kural.** Bir test hangi konuda olduğuna bakılarak değil, neye ihtiyaç
duyduğuna bakılarak işaretlenir. "Sandbox hakkında" olmak `sandbox` işaretini
gerektirir; görev verisi okumak ayrıca `appworld` işaretini gerektirir.

**Gerekçe iki kez ölçüldü, ikisi de aynı yerde.** S-49'da kırk beş test yalnız
konusuna göre işaretsiz bırakılmıştı ve CI'da `appworld install` olmadığı için
kırıldı. Madde 8'de aynı şey tekrarlandı: iki sandbox testi `specs.json` okuyor
ve uygulama modüllerini istiyordu, ama "sandbox hakkında" oldukları için yalnız
`sandbox` işareti taşıyorlardı. Beşinci CI kontrolü kırmızı yandı.

İşaret bir etiket değil, bir sözleşme: "bu test şu olmadan koşamaz". Konu
etiketi o sözleşmeyi söylemiyor.

### Bir kereye mahsus kurulan bir kontrol, kurulmamış bir kontroldür

**Kural.** Bir arızayı yakalamak için kurulan kontrol depoya girer ve standart
ön kontrolün içinden çağrılır. Geçici olarak kurulup silinen kontrol, kurulmamış
sayılır.

**Gerekçe ölçülmüş.** S-49'da CI ortamını yerelde yeniden üreten bir simülasyon
elle kuruldu, iki arızayı da yakaladı, ve iş bitince silindi. Madde 8'de aynı
sınıftan bir arıza yine CI'da çıktı — simülasyon var olsaydı yerelde
görülecekti. Simülasyon artık `scripts/ci_simulasyonu.sh` ve
`scripts/local_checks.sh` onu çağırıyor.

**Kontrolün kendisi de ateşlediği görülerek kabul edildi.** İlk hâli geçici bir
worktree'yi `HEAD`'den kuruyordu, yani commit edilmemiş değişikliği hiç
görmüyordu: işareti kaldırıp koştuğumda yeşil yandı. Çalışma ağacından kurulan
hâliyle aynı deneme kırmızı yanıyor. Bir kontrolün yeşil yanması, doğru şeye
bakarak yandığı anlamına gelmiyor (K-49).

## 7. Bu belgenin bilerek sessiz kaldığı yerler

Hipotez, birincil hücre, estimand, analiz planı, kapılar, gürültü tabanının ön
kayda giren hâli ve güç kuralı burada değil. Hepsi deney ön kaydına ait ve
kurulum bittikten sonra, pilottan önce donacak.

## 8. Karar bekleyen tek alan

**Ayar bütçesinin sayısı.** Dört revizyon tüketildi; izin verilen toplam
yazılmadı. Bu belge o sayı konmadan tam anlamıyla donmuş sayılmıyor.

## 12. Üç kollu kart koşusu: sınırı ve yorumu, sonuç görülmeden

Bu bölüm koşudan **önce** yazıldı. Amacı, çıkan sayıya bakıp yorum seçme
imkânını ortadan kaldırmak.

### 12.1 Düzenek

Üç kol × beş görev × üç tekrar = 45 epizot, hepsi aynı commit'te.

| kol | slota giren |
|---|---|
| `cards` | getiricinin o görev için bulduğu kartlar |
| `baseline` | hiçbir şey; prompt referansla bayt bayına aynı (K-25) |
| `irrelevant` | kütüphaneden **uymayan** bir kart, yeni madencilik yok |

Tekrarlar `seed_index` 0, 1, 2 — mevcut tohum türetme mekanizması, yeni makine
yok. Ayrı koşu öneki. Özgün demo sonucu kayıttan silinmiyor; eski commit ölçümü
olarak etiketli kalıyor.

### 12.2 Alakasız kolun sınırı — ölçüldü, iddia edilmedi

Kütüphane `v0-gap2-sup3-142662f` dört beceri taşıyor ve **dördünün de etki
soneki bir `auth/token` POST'u**:

| beceri | uzunluk | destek | etki soneki |
|---|---|---|---|
| `134ca318…` | 2 | 8 | `POST venmo.auth/token` |
| `9bb946ad…` | 3 | 7 | `POST spotify.auth/token` |
| `65861cf8…` | 7 | 5 | `POST simple_note.auth/token` |
| `3ef8565f…` | 5 | 5 | `POST phone.auth/token` |

Gövdeler de aynı iskeleti taşıyor: belgeleri oku, süpervizör parolalarını oku,
jetonu al. Uygulamaya özgü olan tek şey hangi uygulamanın `auth/token` ucunun
çağrıldığı; **dizinin kendisi yapısal.**

Bunun sonucu şu: başka bir uygulamadan gelen kart da aynı dersi veriyor —
"jetonu al, taşı". Dolayısıyla **bu kütüphanede alakasız kontrol İÇERİK ile
ŞABLONU ayıramaz.** Ayırabildiği tek şey "kart biçimli metin" ile "kart biçimli
olmayan metin" arasındaki fark.

Bu bir kusur değil, bu kütüphanenin ölçülmüş bir özelliği. İçerik atfı için
birbirinden yapısal olarak farklı beceriler taşıyan bir kütüphane gerekiyor ve
bu korpus onu üretmedi.

### 12.3 Önceden ilan edilen yorum

**Kararlılık.** Üç tekrar beş görevin hepsinde uyuşursa sonuç kararlıdır ve
karşılaştırma anlamlıdır. Bazı görevlerde ayrışırsa gürültü tabanı sıfır değildir
ve karşılaştırma sayı olarak değil **oran** olarak yazılır. Çoğunda ayrışırsa
demonun "kartlı 2 çift, kartsız 0" iddiası desteklenmiyor demektir ve **geri
çekilir**.

**Kol karşılaştırması.**

| gözlem | yorum |
|---|---|
| alakasız kol kartlıya yakın | etki hacim ve biçimden; bu kütüphanede içerik atfı yapılamaz |
| alakasız kol kartsıza yakın | etki içerikten |
| alakasız kol arada | n=5'te yorumlanamaz, öyle raporlanır |
| **hiçbirine uymuyor** | **tablo yanlıştı; sonuç yorumsuz raporlanır ve tablonun neyi kaçırdığı yazılır** |

Son satır bu koşuda gerçekten tetikledi: alakasız kol üç öngörünün hiçbirine
uymadı, her ikisinin de **altında** çıktı. Ayrıntısı
`docs/reports/uc-kollu-kart-kosusu.md` §4'te.

**Etiket.** Sonuç **gösterimsel**; istatistiksel değil. Beş görev ve üç tekrar
ayırt edici güç vermiyor ve bu koşu bir kazanç iddiası taşımıyor.

**Beklenen sonuç, şimdiden yazılı.** Alakasız kolun da başarması bekleniyor,
çünkü 12.2'deki homojenlik onu bekletiyor. Öyle çıkarsa bulgu "kütüphane içerik
atfı için fazla homojen" olur — bu ölçülmüş bir sonuçtur, bir başarısızlık
değil.

### 12.4 Raporda ne olacak

Görev başına, kol başına, tekrar başına: sonuç, adım sayısı, sonlanma sebebi.
Sonra kararlılık analizi, sonra 12.3'teki tabloya göre kol karşılaştırması, sonra
özgün demo iddiasının ayakta kalıp kalmadığı.


## 13. Önceden ilan kuralı: her tablonun bir dördüncü dalı var

**Kural.** Sonuç görülmeden yazılan her yorum tablosu, açık bir "hiçbirine
uymuyorsa" dalı taşıyor. O dalın içeriği sabit: **tablo yanlıştı, sonuç yorumsuz
raporlanır, ve tablonun neyi kaçırdığı yazılır.**

**Gerekçe ölçüldü.** Üç kollu koşunun tablosu üç satır taşıyordu — alakasız kol
kartlıya yakın, kartsıza yakın, ya da arada. Çıkan desen dördüncüydü: alakasız
kol her ikisinin de altında. Üç satır yazmak, sonuç uzayının kapsandığını
varsaymak demek; ve kapsanmadığında ortaya çıkan boşluk sonucu satırlardan birine
zorlamaya davet ediyor. Zorlama olmadı ama davet gerçekti, ve davetin kendisi
tasarım hatası.

**Neden yorum yasağı, neden yeni bir satır değil.** Sonuç görüldükten sonra
tabloya dördüncü bir satır eklemek, ön kaydın işlevini ortadan kaldırır: o
noktada yorum veriye bakılarak seçilmiş olur. Dördüncü dal bu yüzden yorum
üretmiyor, yorumu durduruyor.

**Sınırı.** Bu dal, tablonun eksik olduğunu koşudan önce görmeyi sağlamıyor;
eksik çıktığında sonucun sessizce bir satıra sığdırılmasını engelliyor. Tabloyu
tam yazmak hâlâ yazanın işi.

## 14. 32B ölçümü: şartlar ve yorum, sonuç görülmeden

**Bu bölüm koşudan önce yazıldı** (K-62). Amacı, çıkan sayıya bakıp yorum seçme
imkânını ortadan kaldırmak.

### 14.1 Sorunun ne olduğu ve ne olmadığı

**Soru:** ön koşul kapısı model boyutuna mı bağlı?

Aile değişmiyor — `qwen2.5-coder`. Değişen tek şey "yerel, 8 GB'a sığan" kısıtı.
Tasarımda zaten kilitli bir karar var: eksenin en küçük noktası tabana çakılırsa
bir üst boyuta taşınır (S-14'ün azaltması). Şu an **üç nokta birden** çakılı, ve
bu koşu o kararın bir üst basamağını deniyor.

**Soru bu değil:** "eksen 32B'de bant açıyor mu". 32B yerel kısıtın dışında ve
eksene giremez; bu ölçüm ekseni genişletmiyor, ön koşul bulgusunun **sebebini**
daraltıyor.

### 14.2 Zorunlu şartlar

| Şart | Neden |
|---|---|
| Sağlayıcı **sabitlenecek** (`provider.only`, `allow_fallbacks: false`) | OpenRouter aynı etiketi birden çok sağlayıcıya yönlendiriyor ve **kuantalama sağlayıcının kararı**. Sabitlenmezse koşu tek bir koşul olmaz |
| Sağlayıcı adı künyeye yazılacak | Koşulun hangi tarafta koştuğu künyeden okunabilmeli |
| Bildirilen kuantalama ve azami bağlam künyeye **İLAN olarak** yazılacak | Barındırılan kipte doğrulama yapamıyoruz; `context_verified = 1` yasağı duruyor (şema düzeyinde zorlanıyor) |
| Çıktı bütçesi düzeltilmiş sınır kontrolüyle **aynı** (4000) ve künyede | 400 jetonla 6/30, 4000 jetonla 20/30 çıkmıştı (S-26). Yanlış bütçe **sahte bir sıfır** üretir |
| Tavana çarpan epizot oranı raporlanacak | Bütçenin bağlayıcı olmadığı gösterilmeden bir sıfır yorumlanamaz (K-60) |
| Görev kümesi, durma kuralı, eşik, tohum türetme, kalkan kipi: sınır kontrolüyle aynı | Tek değişen model etiketi ve sağlayıcı olsun |
| Ön kontrol koşacak | Yazma yolu otuz epizot başlamadan sınanacak (S-28) |

### 14.3 Sabitlemenin taşıma katmanında yapılması, ölçülmüş sebeple

**Sağlayıcı sabitlemesi iskelenin çağrı yolundan geçemiyor, ve bu ölçüldü.**
OpenRouter yönlendirmeyi istek gövdesindeki `provider` alanından okuyor. İskelenin
`LanguageModel`'ı generation kwargs'ı `litellm.completion` imzasına göre süzüyor;
`extra_body` o imzada **yok**, yani kurulumda reddediliyor. `non_cached_lm_call`
da imzasında olmayan her anahtarı `**kwargs` üzerinden **istisna fırlatarak**
reddediyor. İkisi de sessiz düşürme değil, iyi; ama sonuç aynı: alan tele
ulaşmıyor.

**Çözüm iskeleyi değiştirmek değil** (K-19). Alan, isteği ileten ince bir yerel
katmanda gövdeye ekleniyor — kayıt vekilinin ve `api_capture`'ın zaten oturduğu
yer, ve K-19'un kapsamı dışında kalan taşıma katmanı.

**Bu düzenlemenin kendisi doğrulanacak:** sabitleme yalnız gönderdiğimiz gövdeden
değil, **sağlayıcının yanıtından** okunacak. OpenRouter yanıtta hizmet veren
sağlayıcıyı bildiriyor; künyeye giren değer o. Böylece "sabitledik" bir ilan
değil bir gözlem oluyor.

### 14.4 Önceden ilan edilen yorum — asimetrik

| Gözlem | Yorum |
|---|---|
| **Sıfır** | Sağlayıcı hassasiyetinde bir 32B bu ortamda hiçbir şey çözemiyor. Tavan bizim kuantalamamızdan gelmiyor ve ön koşul bulgusu **belirgin biçimde güçleniyor**; "küçük model seçtiniz" itirazı kapanıyor |
| **Sıfırdan büyük** | Bant var. Ama **hangi hassasiyette olduğunu bilmiyoruz**: tek sağlayıcı olan Cloudflare kuantalamayı `unknown` diye bildiriyor (koşudan önce ölçüldü). Yerel Q4_K_M eşdeğerinin aynı davranacağı iddia edilemez — kuantalama sağlayıcının kararı, üstelik adlandırılmamış, ve o model zaten 8 GB'a sığmıyor. Bulgunun kurulabilir en geniş hâli: **"Cloudflare'in sunduğu hâliyle 32B'de bant var"** |
| **Hiçbirine uymuyor** | **Tablo yanlıştı; sonuç yorumsuz raporlanır ve tablonun neyi kaçırdığı yazılır** (K-104) |

**Asimetri kasıtlı.** Sıfır, mevcut bulguyu güçlendiriyor ve yeni bir iddia
kurmuyor. Sıfırdan büyük, yeni bir iddia kuruyor ve o iddianın kapsamı iki
karıştırıcıyla — kuantalama ve donanım — daraltılmış hâlde yazılıyor.

### 14.5 Maliyet

Üst sınır **3,00 dolar**, ve sayı tahminle değil ölçümle kondu.

İlk yazılan sınır 1,50 dolardı ve dayanağı "sınır kontrolü 0,62 dolar tuttu, bu
koşu benzer olmalı" varsayımıydı. **Varsayım ölçümle çürüdü.** `sinir3`'ün kırk
altı epizodundan okunan gerçek kullanım epizot başına ~100 893 girdi ve ~14 858
çıktı jetonu; Cloudflare'in fiyatıyla (0,66 $/M girdi, 1,00 $/M çıktı) otuz epizot
**~2,44 dolar** ediyor. 1,50 dolarlık sınır koşuyu ~%61'de durdururdu.

**Ve bu bir para meselesi değil, §6 meselesi.** Eksik bir epizot kümesi asla
alıntılanmıyor: kesinti uzun epizotlara daha çok denk geldiği için hayatta
kalanlar sistematik olarak kolay görevler olur. 1,50 dolarla koşmak, üretildiği
anda alıntılanamaz olan bir küme üretirdi.

Yeni sınır ölçülen 2,44'ün üstüne %20 pay ekliyor. Sınır yine bağlayıcı: koşucu
harcamayı epizot başına toplayıp aşarsa **durur**, ve ne kadarının koştuğu ile
gerçek maliyet raporlanır. Sınırın aşılması bir arıza değil bir sonuç.

**Tahminin kendi belirsizliği.** Sayı DeepSeek V4 Flash'ın jeton kullanımından
ölçekleniyor; 32B daha uzun ya da daha kısa yazabilir. Yön bilinmiyor, bu yüzden
pay iki tarafa da yetecek kadar konuldu ve gerçek maliyet ayrıca raporlanacak.

Sınırın aşılması bir arıza değil bir sonuç: koşunun tahmin edilenden pahalı olması
da ölçülmüş bir olgu ve öyle yazılır.

## 15. Colab'da 14B ölçümü: şartlar mutlak değerle, yorum sonuç görülmeden

**Bu bölüm koşudan önce yazıldı** (K-62). Şartlar **sayısıyla** yazıldı, başka bir
koşuya atıfla değil — S-58'in dersi bu.

### 15.1 Neden 14B, neden 32B değil

Ölçek ekseninin eksik noktası 14B. Tek tip kuantalamayı koruyor (`q4_K_M`),
ücretsiz T4'e sığıyor, ve "bizim kuantalamamızda bariyer boyut mu" sorusunu
doğrudan yanıtlıyor. 32B zaten OpenRouter'da ölçüldü ve orada **hassasiyet
bilinmiyordu** (`declared_quantisation: unknown`, S-58/S-59); kuantalama boyutla
karıştığı için o ölçüm boyut sorusunu ayıramıyor. Colab kuantalamayı sabit tutup
yalnız boyutu değiştiriyor.

### 15.2 Şartlar (`b14`), mutlak değerle

Aşağıdaki değerler `bant3` künyelerinden okundu — yerel 0/30'u üreten koşu — ve
buraya sayı olarak yazıldı. Koşu bunlarla koşacak, "aynı olsun" denmeyecek.

| Alan | Değer | Nereden |
|---|---|---|
| `model_tag` | `qwen2.5-coder:14b-instruct-q4_K_M` | eksenin eksik noktası |
| `serving_mode` | `local` | Ollama, Colab GPU'sunda |
| `max_output_tokens` | **400** | `bant3` künyesi |
| `no_progress_limit` | **15** | `bant3` künyesi |
| `shield_mode` | **`off`** | `bant3` künyesi |
| `temperature` | **0,2** | `bant3` künyesi |
| `base_seed` | **123** | `bant3` künyesi; tohum `seed_for(task_id, seed_index)` ile türüyor, model ve koşul dışarıda (K-20) |
| `num_ctx_requested` | **32768** | `bant3` künyesi |
| `kv_cache_type` | **`q8_0`** | `bant3` künyesi |
| `flash_attention` | **1** | `bant3` künyesi |
| Adım tavanı | `k = 2` çarpanı, taban 20, tavan 150 | bant taramasının formülü: `min(max(2 × çapa, 20), 150)` |
| Görev kümesi | aynı otuz görev | koşudan önce `bant3`'ün görev kümesiyle **birebir karşılaştırılacak**, `b32`'de yapıldığı gibi |

**400 jetonun kendi şartı var.** S-26 dört yüz jetonun yerelde bağlayıcı
olmadığını ölçmüştü — `qwen2.5-coder` akıl yürütme üretmiyor ve bant taramasının
958 adımında kodsuz adım sayısı sıfır. Ama bu **7B için** ölçüldü, 14B için
değil. Bu yüzden koşu **kodsuz adım oranını raporlayacak**; oran sıfıra yakın
değilse bütçe bağlayıcıdır ve sonuç bir alt sınırdır (K-60).

### 15.3 Koşudan önce ölçülecekler

`scripts/setup/measure_colab_environment.py`, üçü de makinenin özelliği:

**GPU ve VRAM.** Sürücünün bildirdiği model adı ve toplam bellek.

**Modelin tamamen VRAM'de olup olmadığı.** Yerelde üç boyut da tam yerleşik
ölçülmüştü (7B'de 29/29 katman). Kısmen boşaltılmış bir model başka bir hesabı
başka bir hızda koşturuyor, ve yerleşik bir model üzerinde kalibre edilmiş adım
tavanı o durumda diski ölçer. **Tam yerleşik değilse koşu başlamıyor** — betik
çıkış kodu 1 veriyor.

**Model yükleme süresi.** K-21'in soğuk rejimi yerelde ölçülen 2,72 / 3,01 / 3,55
saniyeye dayanıyor. Colab'ın diski o disk değil. Yükleme on kat pahalıysa rejimin
bedeli değişir ve bunun koşudan **önce** yazılması gerekiyor.

**Sunucunun istenen yapılandırmayı gerçekten koşturup koşturmadığı.** Dördüncü
ölçüm, ve ayrı bir soru. `server_settings` **istenen** değeri okuyor:
`OLLAMA_FLASH_ATTENTION`, `OLLAMA_KV_CACHE_TYPE`. Donanımın onu **kabul edip
etmediği** başka bir şey. Bir GPU q8_0 KV önbelleğini desteklemiyorsa istek
sessizce kabul edilir ve önbellek f16'da tutulur: iki katı bellek, ve §15.8'in
aritmetiği artık geçerli değil. İstenip uygulanmayan bir yapılandırma, ortamın
**aynı ölçümü daha yavaş** değil **başka bir ölçümü** koşturması demek, ve o
durumda Colab sonucu yerelle karşılaştırılamaz.

Bu yüzden sunucunun kendi günlüğünden okunuyor, ayara sorularak değil:

| Okunan | Kaynak satır |
|---|---|
| GPU'ya yüklenen katman sayısı | `offloaded 29/29 layers to GPU` |
| Flash attention'ın **etkin** hâli | `llama_context: flash_attn = enabled` |
| KV önbelleğinin **etkin** tipi | `K (q8_0): ..., V (q8_0): ...` |
| KV önbelleğinin boyutu | `llama_kv_cache: size = 952.00 MiB` |
| **İstenen** değerler | `--cache-type-k q8_0 --flash-attn on` |

Ayrıştırıcı, yerelde gerçek bir yükleme günlüğüne karşı yazıldı ve sınandı: 7B'de
**29/29 katman, flash attention etkin, KV q8_0, 952 MiB** — yani §15.8'in
"7B'de ölçülmüş 0,9 GiB" satırı doğrulandı. Colab'da aynı satırlar okunacak ve
istenen ile etkin ayrı ayrı raporlanacak.

### 15.4 Colab üçüncü ortam

WSL ve CI'dan sonra üçüncü. Bu depoda üç nöbetçi ortama bağlı çıktı ve temiz
klon koşusu bir dördüncüsünü buldu; K-117 yeni ortamda da geçerli. Önyükleme
betiği **bütün nöbetçileri bir kez koşturuyor** ve hangisinin bu ortamda
ayrıştığını raporluyor. Sweep durdurmuyor, raporluyor — amaç ortamı yargılamak
değil, ayrışanı görmek.

### 15.5 Önceden ilan edilen yorum

| Gözlem | Yorum |
|---|---|
| **Sıfırdan büyük** | Bant **bizim kuantalamamızda ve 14B'de** var, yani bariyer boyuttu. Ölçek ekseninin ikinci noktası geri geliyor |
| **Sıfır** | 7B ile 32B arasındaki fark boyuttan değil **hassasiyetten** geliyor olabilir. Sıradaki ölçüm barındırılan 7B olur, çünkü boyutu sabit tutup hassasiyeti değiştiren kontrol odur |
| **Hiçbirine uymuyor** | **Tablo yanlıştı; sonuç yorumsuz raporlanır ve tablonun neyi kaçırdığı yazılır** (K-104) |

**Sonuç keşifsel etiketlenecek.** Eksen noktası sıfırlar görüldükten **sonra**
seçildi; bu bir ön kayıt hücresi değil, ön koşul bulgusunun sebebini daraltan bir
tanı ölçümü. Ne kadar iyi çıkarsa çıksın onaylayıcı sayılmıyor.

### 15.6 Oturum bütçesi ve dalı

Colab'ın ücretsiz kademesinde oturum süresi ve GPU kotası sınırlı, ve kesinti
haber vermeden geliyor. Bu, §14.5'teki para tavanının zaman karşılığı.

**Bütçe: üç oturum.** Otuz epizot üç oturumda bitmezse koşu durur ve **eksik küme
yorumsuz raporlanır**; §6 zaten eksik bir epizot kümesinin alıntılanmasını
yasaklıyor, bu dal onu yorum tarafına da uzatıyor.

**Oturum sınırı koşuyu bloke etmiyor, çünkü devam mantığı tamamlananları
atlıyor** — ve bu iddia sınanmış: `tests/test_resumption.py` atlamanın yalnız
eleman çıkardığını, kalan epizodun nasıl koştuğunu değiştirmediğini çiviliyor
(ne sıra numarası ne tohum atlamadan etkileniyor). Yani bir oturum sonunda
yarıda kalan küme, bir sonraki oturumda kaldığı yerden tamamlanıyor ve
tamamlanmış epizotlar yeniden koşulmuyor.

**Her oturum sonunda sonuçlar depoya itiliyor** (§15.7). Oturum kaybolduğunda
veri kaybolmuyor; veritabanı Drive'a bağlı ve sonuçlar commit'li.

**Sayı ilan ediliyor, tahmin değil.** Kaç oturum harcandığı ve her oturumda kaç
epizodun koştuğu raporlanacak. Üç oturumun aşılması bir arıza değil bir sonuç:
ücretsiz kademede bu ölçümün koşulamadığı da ölçülmüş bir olgu.

### 15.7 Sonuçlar elle yapıştırılmıyor, depoya itiliyor

**Kural.** Colab koşusunun çıktıları sohbete yapıştırılmıyor; defter onları
depoya itiyor ve okuma git'ten yapılıyor.

**İki aday tartıldı ve biri seçildi.**

*Drive'a yazıp WSL'in `/mnt/c` üzerinden okuması.* Jeton istemiyor. Ama ikinci bir
kopya yaratıyor ve ayrışabiliyor; belirleyici sebep şu: **Drive'daki bir dosyanın
commit kimliği yok.** Bu deponun bütün disiplini her sayının onu üreten commit'le
birlikte gezmesi — künye `code_commit` taşıyor, raporlar seriyi adlandırıyor, ve
`check_merged_artefacts.py` yalnız depodakini doğrulayabiliyor. Drive'dan okunan
bir sayı hiçbir ağaç durumuna bağlanamaz, ki K-116 tam bunun üzerine yazıldı.

*Defterin depoya itmesi.* Bir jetona mal oluyor ve sonuca **commit kimliği**
kazandırıyor. Seçilen bu.

**Güvenlik şartları, betiğe yazılı.** `main`'e asla itmiyor ve asla zorla
itmiyor: sonuçlar `colab-sonuclari` dalına iniyor ve birleştirmeyi bir insan
yapıyor, yani otomatik bir itme tarihe ekleyebiliyor ama onu yeniden
yazamıyor. Yalnız `results/` altındaki dosyalar itiliyor — kaynak değişikliği bu
yoldan hiç gelmiyor, çünkü koşan kodun incelenen kod olması gerekiyor.

**Jeton.** Colab Secrets'ta duruyor ve defter `google.colab.userdata` ile
okuyor; `~/.zihin-env` bir WSL düzenlemesi ve orada geçerli değil. Jeton hiçbir
dosyaya yazılmıyor, ekrana basılmıyor ve commit'lenmiyor. **Komut satırına da
girmiyor:** git onu `GIT_ASKPASS` ile ortamdan okuyor, adresin içinde
taşınmıyor. Bu bir temkin değil ölçülmüş bir ders — ilk biçim jetonu klon
adresine koydu, klon düştü, ve Python'un `CalledProcessError`'ı `process.args`'ı
bastığı için sır bir hata izinin içinde çalışma zamanından çıktı ve iptal
edilmek zorunda kaldı (K-124). Kalan sınırı: jeton oturum boyunca süreç
ortamında ve `/tmp/zihin-askpass.sh` içinde duruyor, ve aynı kullanıcının bir
süreci ikisini de okuyabilir — Colab tek kullanıcılı bir sanal makine olduğu
için kabul edildi.

**İtme doğrulanıyor, varsayılmıyor.** Betik itmeden sonra uzaktaki dalın
SHA'sını yereldekiyle karşılaştırıyor ve tutmazsa çıkış 1 veriyor (K-116).

### 15.8 14B'nin T4'e sığması: kestirim ve onu bağlayan ölçüm

T4 ölçüldü: **15360 MiB toplam, 14913 MiB boş**, 12 GiB RAM, 66 GB boş disk.

Kestirim depodaki ölçülmüş sayılardan türetildi:

| | |
|---|---|
| 7B ağırlığı, **ölçülmüş** | 5,160 GiB |
| 14B ağırlığı, kestirim | ~9,98 GiB (parametre başına orandan) |
| 32K q8_0 KV, **7B'de ölçülmüş** | 0,9 GiB |
| 32K q8_0 KV, 14B kestirimi | ~1,54 GiB (katman 28 → 48) |
| **Toplam kestirim** | **~11,5 GiB (11800 MiB)** |
| Boş VRAM | 14,56 GiB (14913 MiB) |
| Pay | ~3,0 GiB |

**Bu bir kestirim, ölçüm değil, ve kararı o vermiyor.**
`measure_colab_environment.py` modelin gerçekten tamamen VRAM'de olup olmadığını
sunucuya sorup ölçüyor; tam yerleşik değilse çıkış kodu 1 ve koşu başlamıyor.
Kestirimin işlevi yalnız "denemeye değer mi" sorusunu yanıtlamak.

### 15.9 Colab imajının taşıdıkları ve taşımadıkları

Ortam olguları, ölçülerek. Bunlar bizim seçimlerimiz değil, üzerinde koştuğumuz
imajın özellikleri; ve her biri bir turun sebebi olduğu için kayda geçiyor.

| Olgu | Sonuç |
|---|---|
| GPU: Tesla T4, 15360 MiB toplam, 14913 MiB boş | 14B sığıyor (§15.8) |
| RAM 12 GiB, `/content` diski 113 GB (66 GB boş) | 9 GB model çekimi sığıyor |
| Drive bir FUSE bağı | Model önbelleği Drive'da **değil**; `/content` üzerinde |
| **`zstd` yok** | Ollama kurucusu bir zstd paketini açıyor ve düşüyor |
| `UV_SYSTEM_PYTHON=1` tanımlı | Hedefi söylenmemiş `uv pip install` sistem Python'una kuruyor (K-129) |
| Her hücre ayrı bir kabuk | Bir hücrede `export` edilen değişken sonrakine geçmiyor |
| `gh` yok | Birleşmiş PR eseri denetimi gerekçesiyle cevap vermeyi reddediyor |

`zstd`'nin yokluğu tek başına bir tur yedi, ve tur başına maliyet kullanıcının
döngüde olmasından geliyor. Bu yüzden §15.10'daki denetim yazıldı: tek tek
keşfetmek yerine hepsini önden sormak.

### 15.10 Ön koşullar önden ve topluca denetleniyor

**Kural.** Ollama kurulumu başlamadan önce, kalan her adımın ön koşulları
denetleniyor ve **eksiklerin hepsi birden** raporlanıyor.

**Gerekçe sayıyla.** Colab önyüklemesi beş turda beş ayrı eksik ön koşulda
düştü: jetonsuz klon, yukarı akış LFS bütçesi, boş veri önbelleği, yanlış Python
ortamı, `zstd`. Her tur bir sonrakini açığa çıkardı. N adımlı bir zincirde ön
koşulları önden sormak N turu bir tura indiriyor.

**Denetlenenler.** İkililer (`curl`, `tar`, `git`, `zstd`, `nvidia-smi`), proje
ortamının üç içe aktarması, GPU'nun VRAM'i, modelin **kayıt defterine sorulmuş**
gerçek boyutu (8,99 GB), üç yolda disk alanı, üç yolda yazılabilirlik, ve sunucu
portunun durumu.

**Hiçbir denetim diğerini durdurmuyor.** İlk eksiğin ikinci eksiği gizlemesi
sorunun kendisi, ayrıntısı değil.

**Kurulabilir olanlar arıza sayılmıyor.** `zstd` yoksa ve `apt-get` varsa,
denetim bunu "kurulacak" diye raporluyor; arıza, ikisinin birden olmaması.

---

## 16. Colab 32B — A100 üzerinde, kendi kuantalamamızla

### 16.1 Neden bu nokta

Eksende `qwen2.5-coder` ailesinin dört noktası ölçüldü: 1.5B, 3B, 7B yerelde
sıfır; 14B Colab'ın L4'ünde 3/30. Beşinci nokta 32B, ve **yeni bir kilit
açmıyor** — yerel donanım kilidi 14B ile zaten açılmıştı (K-133). Açtığı tek şey
ölçek: A100 80 GB'da 32B rahat sığıyor.

**OpenRouter'daki 32B bu nokta değil.** O ölçüm barındırılan bir sunucuda,
kuantalaması bilinmeyen ağırlıklarla ve eksik bir kümeyle (27/30) yapıldı
(S-58, S-59). Bu nokta bizim kuantalamamızla: `q4_K_M`, ölçülen dosya boyutu
**19,851 GB**.

### 16.2 Şartlar (`b32c`), mutlak değerle

| Alan | Değer | Nereden |
|---|---|---|
| `model_tag` | `qwen2.5-coder:32b-instruct-q4_K_M` | eksenin beşinci noktası |
| `serving_mode` | `local` | Ollama, Colab A100'ünde |
| `max_output_tokens` | **4000** | `config/recording.yaml` |
| `no_progress_limit` | **40** | `config/recording.yaml` |
| `shield_mode` | **`shadow`** | koşucunun mount varsayılanı |
| `temperature` | **0,2** | `config/models.yaml` |
| `base_seed` | **123** | `config/models.yaml` |
| `num_ctx_requested` | **32768** | `config/models.yaml` |
| `kv_cache_type` | **`q8_0`** | `config/models.yaml` |
| `flash_attention` | **1** | `config/models.yaml` |
| Adım tavanı | `min(max(2 × çapa, 20), 150)` | bant taramasının kendi formülü |
| Görev kümesi | aynı otuz görev | `bant3` ile birebir karşılaştırılacak |

### 16.3 Değerlerin gerekçesi, sonuca bakılarak seçilmediği için yazılıyor

**`max_output_tokens` 4000, ve 400 bir tasarım değil kazaydı.** §15.2 dört yüzü
`bant3` künyesinden okumuştu. Ölçüldü: `bant3` o değeri `config/recording.yaml`
içinde `max_output_tokens` anahtarı **hiç yokken** aldı (commit `fc9101a`).
Yani 400 seçilmiş bir bütçe değil, bir varsayılanın kalıntısı. 4000 sonradan ve
**bilerek** yapılandırmaya yazıldı. S-26 dört yüzün 7B'de bağlayıcı olmadığını
ölçmüştü, ama yetenekli bir modelde bağlayıcı olduğu görüldü; 32B için dört yüz
seçmek, sonucu bütçeye bağlamak olurdu.

**`no_progress_limit` 40.** Aynı kayıttan: `bant3` zamanında yapılandırma 15
taşıyordu, sonradan 40 oldu. 14B koşusunda 11 epizot bu kuralla durdu; kuralı
şimdi sıkmak koşuyu erken kesmek olur ve iki koşu karşılaştırılamaz hâle gelir.

**`shield_mode` `shadow`, çünkü `off` ULAŞILAMAZ.** `ShieldMode` yalnız
`shadow` ve `enforce` taşıyor; `off` üyesi **yok**. §15.2'deki `off` yalnız
kalkan mount edilmeden önceki künyelerden kopyalanmıştı. Gölge kip engellemiyor,
yalnız gözlüyor — yörünge etkilenmiyor.

**Bu üç değer 14B koşusunun kullandığı değerlerle aynı, ve bu tesadüf
saklanmıyor.** 14B koşusu bu deklarasyondan **önce** koştu ve §15.2'nin ilan
ettiği 400/15/off ile **koşmadı**; 4000/40/shadow ile koştu, çünkü ilan edilen
yer ile okunan yer ayrıydı (S-58 üçüncü örneği, K-136). Yani iki koşunun
şartlarının uyuşması bir tasarım değil, bir kazanın sonucu. Uyuşma
karşılaştırmayı mümkün kılıyor; ama "14B ile aynı şartlarda koştu" cümlesi
**sonradan** doğru oldu, önceden ilan edildiği için değil.

### 16.4 Mimari farkı okunacak, varsayılmayacak

Eksenin noktaları **üç farklı kartta** ölçülüyor: yerel RTX 4070 (Ada, 8.9),
Colab L4 (Ada, 8.9), Colab A100 (**Ampere, 8.0**). Ampere farklı bir nesil ve
flash attention ile `q8_0` KV desteği aynı olmayabilir.

Bu **ölçülecek, tahmin edilmeyecek**. `runtime_facts` sunucunun kendi
günlüğünden istenen ile etkin değeri okuyor ve `comparability` hükmü koşudan
önce basılıyor. `COMPARABLE` değilse koşu yine yapılır, sonuç **"yerelle
karşılaştırılamaz"** diye etiketlenir. Sınırlama S-61'de.

### 16.5 Önceden ilan edilen yorum

| Gözlenen | Yorum |
|---|---|
| **Sıfırdan büyük** | Bant bizim kuantalamamızda 32B'de de var. OpenRouter sondasının kuantalama karıştırıcısı düşer ve eksen dört ölçülebilir noktaya çıkar. |
| **Sıfır** | Daha ilginç olan bu, çünkü 14B 3/30 verdi. Büyüklük ile başarı arasında tekdüze bir ilişki yok demektir ve sebebi aranır — kuantalama, mimari, ya da görev kümesinin kendisi. |
| **Hiçbirine uymuyor** | Tablo yanlıştı. Sonuç yorumsuz raporlanır ve tablonun neyi kaçırdığı yazılır (K-104). |

**Sonuç keşifsel.** Beşinci nokta da sıfırlar görüldükten sonra seçildi.

### 16.6 Elimizdeki en yakın karşılaştırma

OpenRouter 32B koşusu da **4000 / 40 / shadow** ile koştu. Yani Colab 32B
`q4_K_M` ile OpenRouter 32B arasındaki fark büyük ölçüde **kuantalama** olur.
Sağlayıcı ve `serving_mode` de değişiyor, bu bir karıştırıcı; ama elimizdeki en
yakın karşılaştırma bu.

**Oran değil varlık karşılaştırması.** OpenRouter kümesi eksik (27/30, S-59) ve
§6 eksik bir kümeden oran alıntılanmasını yasaklıyor. Eksikliğin yönü asimetrik:
koşulmamış epizotlar bir geçişi gizleyebilir, üretemez.

### 16.7 Çapa uyarısı, aynı otuz görev olduğu için taşınıyor

Adım tavanı çapadan türüyor ve çapa (`num_api_calls`) **referans çözümün
yolunu** ölçüyor, görevin gerektirdiğini değil. 14B koşusunda ölçüldü:
`09b0ee6_1` çapa 102 taşıyor ve altı adımda geçildi; görev metni altı sanatçı
adı isteyen bir **cevap görevi** ve tek anlamlı testi bir dize eşitliği. Yani
`90+` bant etiketi o görev için zorluğu değil referans yolunun uzunluğunu
gösteriyor.

Aynı otuz görev koşulduğu için uyarı bu koşuya da geçerli: **bant başına
sonuçlar bant etiketiyle birlikte, ama etiketin ne ölçtüğü yazılarak**
raporlanacak. Sınırlama S-62'de.

---

## 17. Yerel eksen, dört bin jetonla yeniden

### 17.1 Neden yeniden koşuluyor, ve neden 4000

Eksenin üç yerel noktası — 1.5B, 3B, 7B — **400 jetonluk** bir çıktı bütçesiyle
koşulmuştu ve üçü de sıfır verdi. Colab noktaları 4000 ile koştu: 14B 3/30, 32B
11/30.

**400 bir tasarım değil kazaydı.** §16.3'te ölçülerek yazıldı: `bant3` o değeri
`config/recording.yaml` içinde o anahtar **hiç yokken** aldı (commit `fc9101a`).
Seçilmiş bir bütçe değil, bir varsayılanın kalıntısı. 4000 sonradan ve bilerek
yapılandırmaya yazıldı.

**Bütçenin bağlayıcı olduğu ölçüldü.** S-26 dört yüzün 7B'de bağlayıcı
olmadığını ölçmüştü, ama bu ölçüm **kodsuz adım oranı** üzerineydi ve bant
sıfırken bağlayıcılık görünmüyordu. Yetenekli modelde bağlayıcı olduğu görüldü.

**Eksenin bütün noktaları aynı bütçede olmalı.** Aksi hâlde eksen bir eksen
değil, iki farklı bütçede yapılmış iki ayrı ölçümün yan yana konmuş hâli olur.
Boyut ekseninin ölçtüğü şey boyut olmalı; çıktı bütçesi de değişiyorsa iki
değişken birden taşınır.

**Bu yeniden koşu ONAYLAYICI DEĞİL.** Bütçe, sonuçlar görüldükten sonra
değiştirildi. Sıfırdan büyük bir sonuç, "bütçe yüzündendi" diye okunabilir ama
bu bir keşif olur, önceden ilan edilmiş bir sınama değil. Kayıt bunu böyle
taşıyor.

**Önceden ilan edilen yorum.** Üç nokta da sıfır kalırsa: bütçe açıklama değil,
ve yerel sıfırların sebebi başka. En az biri sıfırdan büyük çıkarsa: 400
bağlayıcıydı ve eski üç sıfır **alt sınırdı**, ölçüm değil — o zaman S-14'ün
"taban etkisi" okuması yeniden değerlendirilir. Hiçbirine uymazsa K-104.

### 17.2 Şartlar (`b15l`), mutlak değerle

| Alan | Değer | Nereden |
|---|---|---|
| `model_tag` | `qwen2.5-coder:1.5b-instruct-q4_K_M` | eksenin noktası |
| `serving_mode` | `local` | Ollama, geliştirme makinesinde |
| `max_output_tokens` | **4000** | koşu komutunda, açıkça |
| `no_progress_limit` | **40** | koşu komutunda, açıkça |
| `shield_mode` | **`shadow`** | koşucunun mount varsayılanı |
| `temperature` | **0,2** | `config/models.yaml` |
| `base_seed` | **123** | `config/models.yaml` |
| `num_ctx_requested` | **32768** | `config/models.yaml` |
| `kv_cache_type` | **`q8_0`** | `config/models.yaml` |
| `flash_attention` | **1** | `config/models.yaml` |
| Adım tavanı | `min(max(2 × çapa, 20), 150)` | bant taramasının kendi formülü |
| Komut | `uv run python scripts/setup/measure_band.py b15l --stop-threshold 40 --max-output-tokens 4000` | koşuyu başlatan tek satır |

**Ek — 31 Ağustos 2026, koşudan önce.** Bu dört satır o gün girdi ve bir
beşincisi (`first_sweep`) aynı gün eklendi. Şart değişmedi;
şartın ilan edilmemiş olduğu ortaya çıktı. Defter kullanıcıya T4 seçtiriyordu ve
söyleyeceği başka bir yer yoktu: §18 çalışma zamanını hiç adlandırmıyordu, bu
yüzden defterin taşıdığı değer bir kopya değil **tek kaynaktı**, ve `b14`
çağından kalmıştı. Bir değerin kopyasını silmenin önkoşulu, okunacak bir aslının
olması.

### 17.3 Şartlar (`b3l`), mutlak değerle

| Alan | Değer | Nereden |
|---|---|---|
| `model_tag` | `qwen2.5-coder:3b-instruct-q4_K_M` | eksenin noktası |
| `serving_mode` | `local` | Ollama, geliştirme makinesinde |
| `max_output_tokens` | **4000** | koşu komutunda, açıkça |
| `no_progress_limit` | **40** | koşu komutunda, açıkça |
| `shield_mode` | **`shadow`** | koşucunun mount varsayılanı |
| `temperature` | **0,2** | `config/models.yaml` |
| `base_seed` | **123** | `config/models.yaml` |
| `num_ctx_requested` | **32768** | `config/models.yaml` |
| `kv_cache_type` | **`q8_0`** | `config/models.yaml` |
| `flash_attention` | **1** | `config/models.yaml` |
| Adım tavanı | `min(max(2 × çapa, 20), 150)` | bant taramasının kendi formülü |
| Komut | `uv run python scripts/setup/measure_band.py b3l --stop-threshold 40 --max-output-tokens 4000` | koşuyu başlatan tek satır |

### 17.4 Şartlar (`b7l`), mutlak değerle

| Alan | Değer | Nereden |
|---|---|---|
| `model_tag` | `qwen2.5-coder:7b-instruct-q4_K_M` | eksenin noktası |
| `serving_mode` | `local` | Ollama, geliştirme makinesinde |
| `max_output_tokens` | **4000** | koşu komutunda, açıkça |
| `no_progress_limit` | **40** | koşu komutunda, açıkça |
| `shield_mode` | **`shadow`** | koşucunun mount varsayılanı |
| `temperature` | **0,2** | `config/models.yaml` |
| `base_seed` | **123** | `config/models.yaml` |
| `num_ctx_requested` | **32768** | `config/models.yaml` |
| `kv_cache_type` | **`q8_0`** | `config/models.yaml` |
| `flash_attention` | **1** | `config/models.yaml` |
| Adım tavanı | `min(max(2 × çapa, 20), 150)` | bant taramasının kendi formülü |
| Komut | `uv run python scripts/setup/measure_band.py b7l --stop-threshold 40 --max-output-tokens 4000` | koşuyu başlatan tek satır |

### 17.5 Koşu düzeni

Üç model **sırayla** koşuyor, her biri otuz görev. Sunucu proje ayarlarıyla
başlatılıyor (`scripts/serve_models.ps1`), yani `num_ctx`, `kv_cache_type` ve
`flash_attention` sunucu sürecine geçiyor ve künyeye oradan yazılıyor (K-22).

**Model adı hiçbir yerde ikinci kez yazılmıyor.** Her koşu kendi önekini
taşıyor, önek kendi şartlar bölümünü adlandırıyor, ve model o bölümden çözülüyor
(K-138). Üç model üst üste koştuğu için bu tam olarak sınanacak yer.

**Devam mantığı.** Makine kapanırsa tamamlanmış epizotlar atlanıyor
(`tests/test_resumption.py`), yani koşu kaldığı yerden sürüyor.

**Her model için ayrı rapor**: bant dağılımı, sonlanma sebepleri, tavana çarpma
oranı, geçen epizotların adım sayısı, ve graded score.

## 18. Biriktirme koşusu: korpus değerlendirilecek modelin kendi epizotlarından

### 18.1 Neden şimdi, ve neyi kapatıyor

Tasarımın kalbi olan "biriktir, madencilik yap, değerlendir" döngüsü hiç
koşmadı. Bugünkü kütüphane sınır kontrolünün epizotlarından madenlendi, yani
**başka bir modelin** başarılarından; değerlendirilecek model kendi deneyimini
hiç biriktirmedi.

**Neyi kapatmıyor.** Bu koşu birincil soruyu cevaplamıyor. Bir korpus üretiyor,
ve o korpusun kütüphaneyi ne kadar büyüttüğünü ölçüyor.

**Ek — 3 Eylül 2026, blok 1'in madenciliği nöbetçiye takıldıktan sonra.**
Korpus tanımı bu ekle **model etiketi VE bölme** olarak yazılıyor: kütüphane ve
indeks, `model_ref`'i ilan edilen modele eşit **ve** `split`'i `train` olan
epizotlardan madenleniyor; iki üretici de bu kuralı zorunlu argüman olarak
alıyor ve koşucu geçiyor.

**Bu bir düzeltme, sapma değil.** Yukarıdaki cümle "korpus değerlendirilecek
modelin kendi epizotlarından" diyordu; madenci ise dosyadaki her geçen epizodu
okuyordu, önek, koşul ya da model süzgeci olmadan. Colab'daki dosya ölçüldü:
`b14` (14B, 31 epizot, 3 geçen), `b32c` (32B, `test_normal`, 31 epizot, 11
geçen) ve `bir1` (32B, `train`, 64 epizot, 17 geçen). Nöbetçiyi bağlayan on iki
çağrılık dizi `GET spotify.songs/{song_id}`'nin tekrarıydı ve desteğini iki
`b32c` epizotu ile bir `bir1` epizotundan alıyordu. İlan edilenle uyuşmayan bir
korpustan ilan edilene dönülüyor.

**İki gerekçe.** Birincisi ilanın kendisi: `b14` başka bir model, `b32`
kuantalaması bilinmeyen başka bir koşu (`S-58`). İkincisi **sızıntı**: `b32c`
aynı model ama `test_normal`'da koştu, ve değerlendirme de `test_normal`'da.
`b32c`'nin geçenlerinden madenlenen bir beceri değerlendirme görevinin çağrı
dizisini kodlar; sonra o kümede ölçüm yapmak test kümesinde eğitmek olur.

**Kural önek olarak değil, model artı bölme olarak yazıldı.** Bugün bu `bir1`'in
on yedi geçenine eşit; ikinci bir `train` koşusu geldiğinde o da girer, aynı
modelin `test_normal`'daki bir kardeşi ise dışarıda kalır. Bir önek ikisini de
söyleyemezdi.

**Süzülmüş korpusta ne çıktı.** On yedi epizot, on yedi görev, 490 çağrı, 35
elemanlı alfabe; boşluk 2 / destek 3'te **18 kapalı örüntü, 9'u etkili, 4
beceri**, ve nöbetçi bağlamıyor — tavan 12, 24 ve 48'de aynı 18 örüntü.
Kalibrasyon korpusu 105 örüntüden 4 beceri vermişti; burada 18'den 4. Kayıt
`K-159`'da.

### 18.2 Şartlar (`bir1`), mutlak değerle

| Alan | Değer | Nereden |
|---|---|---|
| `model_tag` | `qwen2.5-coder:32b-instruct-q4_K_M` | deneyin ilan edilmiş modeli |
| `serving_mode` | `local` | Ollama |
| `max_output_tokens` | **4000** | `config/recording.yaml` |
| `no_progress_limit` | **40** | `config/recording.yaml` |
| `shield_mode` | **`shadow`** | koşucunun mount varsayılanı |
| `temperature` | **0,2** | `config/models.yaml` |
| `base_seed` | **123** | `config/models.yaml` |
| `num_ctx_requested` | **32768** | `config/models.yaml` |
| `kv_cache_type` | **`q8_0`** | `config/models.yaml` |
| `flash_attention` | **1** | `config/models.yaml` |
| Adım tavanı | `min(max(2 × çapa, 20), 150)` | bant taramasının kendi formülü |
| Görev kümesi | `train` bölmesinin doksan görevi, tamamı | biriktirme havuzu |
| Tohum | tek, `seed_index` 0 | destek ayrık göreve göre sayılıyor |
| Koşul | **`baseline`** | kart yok: korpus sınanacak mekanizmayla kirlenmeyecek |
| `runtime` | **A100** | 32B'nin ölçülen dosyası 19,851 GB; T4'ün 15360 MiB'ine sığmıyor (§16.1) |
| `model_file_gb` | **19,851** | §16.1'de bu etiketin ölçülen dosya boyutu |
| `block_size` | **30** | `scripts/setup/run_accumulation.py` |
| `episode_ceiling` | **270** | §18.3, dal B |
| `first_sweep` | **90** | `train` bölmesinin görev sayısı; ilk süpürme hepsini koşuyor |
| `library_max_gap` | **2** | `results/accumulation.json`; kayıttaki kütüphane `v0-gap2-sup3-142662f` |
| `library_min_support` | **3** | aynı ölçüm, aynı kimlik |
| `index_min_support` | **1** | `results/accumulation.json` (`failure_index.min_support`); kayıttaki indeks `v0-sup1-4bb340a` |
| `library_max_length` | **256** | bütçe, eşik değil: 64 bağlıyor, 128/256/512 aynı 68 örüntü ve aynı 9 beceri (`K-161`) |
| `delivered_library_id` | `v0-gap2-sup3-0c3f4ac` | koşunun teslim ettiği kütüphane; 11 beceri, 45 destekleyen epizot |
| `delivered_index_id` | `v0-sup1-0c3f4ac` | aynı blokta madenlenen indeks; 29 kart |
| Komut | `uv run python scripts/setup/run_accumulation.py bir1` | koşuyu başlatan tek satır |

**Ek — 13 Eylül 2026, biriktirme kapanırken.** Son iki satır bir şart değil,
koşunun **çıktısı**: teslim edilen kütüphanenin ve indeksin kimlikleri. Buraya
yazılmalarının sebebi değişmemeleri gereği. Kütüphane deneyin girdisi olacak ve
`latest_library_and_index` onu satır sayısına göre seçiyor — yani ileride
madenlenecek başka bir kütüphane sessizce onun yerine geçebilirdi. Ön koşul
denetimi artık çözdüğü kimliği bu satırla karşılaştırıyor ve farklıysa
**reddediyor**. Kimlikler `0c3f4ac` commit'inde, boşluk 2 / destek 3 / sabit
eşiği 3 ile madenlendi (`K-164`).

**Ek — 3 Eylül 2026, blok 1'in madenciliği düştükten sonra.** Üç satır daha,
aynı gerekçeyle: değer değişmedi, ilan edilmemiş olduğu ortaya çıktı. Madencilik
eşiklerinin **kuralı** ön kayıtta (`K-50`: "şu ölçüme göre şöyle seçilecek"),
**sayıları** kurulum sonrasına aitti ve kurulum onları çoktan doldurmuştu —
ama hiçbir makine okunur yerde değillerdi. Koşucu `build_skill_library.py`'yi
argümansız çağırıyordu ve o betik `--max-gap` ile `--min-support` olmadan
başlamıyor; altmış epizot yazıldıktan sonra blok sınırında düştü. Sayılar
kayıttaki kütüphanenin ve indeksin kimliklerinde zaten yazılıydı, okunacak yerde
değil.

**Ek — 3 Eylül 2026, blok 3'ün madenciliği derinlik tavanına takıldıktan sonra.**
`library_max_length` satırı girdi. Bu bir **bütçe**, ilan edilmiş bir eşik değil:
madenci hâlâ bağlarsa kendini söylüyor. Değer "bağlamayan" olarak seçildi,
"tamamlatan" olarak değil: taze kayıtta (29 geçen, 1102 çağrı) 64 bağlıyor —
en uzun örüntü 70 — 128, 256 ve 512 bağlamıyor ve üçü aynı örüntü kümesini
(68) ve aynı kütüphaneyi (9 beceri) veriyor. 256 bağlamayan ilk değerin iki
katı, en uzun örüntünün üç buçuk katı ve kayıttaki en uzun epizodun (159 çağrı)
üstünde; bir örüntü kendisini destekleyen en kısa epizottan uzun olamaz.


**Bu koşu kütüphaneyi okumuyor, ve okumamalı.** Koşul `baseline`, yani hiçbir
kart prompt'a girmiyor. Kartlı koşsaydı üretilen korpus sınanacak mekanizmayla
kirlenirdi ve o korpustan madenlenen kütüphane **döngüsel** olurdu: mekanizmanın
ürettiği epizotlardan mekanizmayı beslemek. Ön koşul denetimi bu yüzden
`--prefix bir1` ile koşuluyor; ilan edilen koşulu okuyup kütüphaneyi bu koşu için
**istemiyor** (K-152).

**Tek tohum, ve gerekçesi ölçülmüş bir olgu.** Destek ayrık göreve göre
sayılıyor, yani zaten geçmiş bir göreve ikinci tohum kütüphaneye hiçbir şey
eklemiyor. Genişlik derinlikten önce.

### 18.3 Durma ölçütü: iki dal, hangisi önce ateşlerse

**Dal A — verim.** Her otuz epizotluk blok sonunda kütüphane **ve** indeks
gerçek üreticilerle yeniden madenleniyor. **İki ardışık blok sıfır yeni beceri
eklerse koşu duruyor.** Örüntü sayısına değil beceriye bakılıyor, çünkü yüz beş
örüntüden dört beceri çıkaran süzme zincirinin örüntü sayısını takip etmediği
ölçüldü. İki blok, tek bloğun tesadüfünü eliyor.

**Dal B — tavan.** İki yüz yetmiş epizot. A ateşlemezse koşu **yine duruyor** ve
rapor "kütüphane 270 epizotta doymamıştı" oluyor. Bu bir sonuç, başarısızlık
değil.

**Doksandan sonra ne koşuyor.** Birinci süpürme doksan görevin hepsi, tohum
sıfır. A ve B ateşlemediyse ikinci süpürme yalnız **düşen** görevleri bir sonraki
tohumla tekrar koşuyor; geçmiş bir göreve ikinci tohum desteğe katkı yapamaz,
düşen bir göreve yapabilir.

### 18.4 İndeks kütüphaneyle aynı blokta madenleniyor

`S-65` bir kez oldu: korpus büyüdü, indeks yeniden madenlenmedi, ve kayıttaki on
beş kart bugünün korpusunun verdiği yirmiden geride kaldı. Bu koşuda kütüphanenin
yeniden madenlendiği **her blokta** indeks de yeniden madenleniyor. İki üretici
`scripts/setup/build_skill_library.py` ve `scripts/setup/build_failure_index.py`,
ve blok defteri `results/accumulation-ledger.json` ikisinin sayılarını yan yana
tutuyor.

### 18.5 Önceden ilan edilen yorum, üç dal

Bugünkü oran: yüz beş örüntüden dört beceri. Korpus üçe katlandığında:

| Gözlem | Yorum |
|---|---|
| Oran **korunuyor** | Beceri sayısı korpusla doğrusal artıyor. |
| Oran **düşüyor** | Süzme zinciri darboğaz; zincire bakılır. |
| Oran **yükseliyor** | Korpus çeşitliliği artmış; bu da bir bulgu. |

**Hiçbirine uymuyorsa** tablo yanlıştı: sonuç yorumsuz raporlanıyor ve tablonun
neyi kaçırdığı yazılıyor (`K-104`).

### 18.6 Koşu düzeni

**Model adı ikinci kez yazılmıyor.** Önek kendi şartlar bölümünü adlandırıyor ve
model oradan çözülüyor (`K-138`).

**Devam mantığı.** Tamamlanmış epizotlar atlanıyor, yani oturum kesilirse koşu
kaldığı yerden sürüyor.

**Blok sınırında ne yazılıyor.** Her blok sonunda deftere bir satır giriyor:
kaçıncı blok, o ana kadarki epizot sayısı, ayrık geçen görev sayısı, kütüphane
kimliği ve beceri sayısı, indeks kimliği ve kart sayısı, ve o blokta eklenen yeni
beceri sayısı. Durma kararı bu deftere bakarak veriliyor, hafızaya değil.

## 19. Deney: önek ve sınır

Bu bölüm deneyin koşularını kaydın geri kalanından ayıran sınırı ilan ediyor.
Deneyin şartları, görev sırası ve dilimleri ayrı alt bölümlerde gelecek.

### 19.1 Önek

Deneyin her koşusu `dny` önekiyle koşuyor: koşu kimliğinin ilk parçası `dny`.
Kayıttaki başka hiçbir koşu bu öneki taşımıyor. Değer koddaki tek yerde,
`zihin.declared`'da, ve bu bölümle aynı olduğunu bir test çiviliyor.

### 19.2 Neden commit'e değil öneğe bağlı

Deney birden çok oturum sürecek ve kod o süre içinde değişebilir: ölçümü
tanımlayan bir yola dokunan bir düzeltme koşuyu durdurur ve devam daha sonraki
bir commit'te başlar (A.9'un 25 Eylül eki). Commit'e bağlı bir sınır o anda
kayardı. Önek değişmiyor.

### 19.3 Sınırın iki yüzü

**Dokunulan görev kuralı `dny`'yi saymıyor.** Kural "deney öncesi her koşu"
diyordu ve sınırı bilmiyordu; deneyin ilk epizodu bir değerlendirme görevine
dokunduğu anda liste reddedilirdi. Bundan sonra kural "`dny` dışındaki her koşu"
(ön kayıt A.10'un eki, `K-178`).

**`dny` epizotları iki şarta bağlı**, çünkü listenin dışında kaldıkları için
başka hiçbir şey onları görmüyor:

1. Görev değerlendirme örnekleminde: `test_normal`, dokunulan görevler çıkarılmış.
   Eğitim, dev ya da zorluk bölmesinden bir `dny` epizodu reddediliyor.
2. Koşu bir ön kontrol değil. Bu depodaki her koşucu sağlık kontrolünü kendi
   öneki altında, `-onkontrol` ekiyle yazdı: kayıtta yedi önek altında on üç
   böyle epizot var. `dny` altında aynı ad sınırın içinde bir sağlık kontrolü
   demek, ve reddediliyor.

### 19.4 Deney olmayan koşular: `dnyk`

Deneye ait ama hiçbir şey ölçmeyen koşular — ön kontrol, sağlık kontrolü, duman
koşusu — `dnyk` önekini alıyor. Dokunulan görev kuralı onları her koşu gibi
sayıyor: bir değerlendirme görevinde koşarlarsa görev örneklemden çıkıyor ve liste
bunu söylüyor. Kuru koşu (`--dry-run`) epizot yazmıyor ve öneke ihtiyaç duymuyor.

### 19.5 Deneyin komutu kirli bir ağaçta başlayamaz

`dny` önekli bir koşunun komutu `--allow-dirty-tree` taşıyamaz. Kirli ağaç kapısı,
ölçümü tanımlayan bir değişikliğin koşuyu durdurmasının yolu (A.9'un 25 Eylül
eki); bu bayrak koşuyu yine de başlatıyor ve künyeye yalnız "dirty" yazıyor.
`scripts/check_declared_conditions.py` komutu, hiçbir değeri karşılaştırmadan
önce bu yüzden reddediyor (`K-180`). Denetim argparse'ın eşleştirdiği gibi
eşleştiriyor: `--allow` de bayrağa ulaşıyor ve o da reddediliyor.

### 19.6 Şartlar (`dny`), mutlak değerle

Faz 1'in şartları, ilk `dny` epizodundan önce. §18.2'nin deneye uyan satırları, artı
deneyin kendi satırları. Biriktirmeye özgü satırlar (blok, tavan, ilk süpürme, madencilik
eşikleri) yok: deney madencilik yapmıyor, §18.2'nin teslim ettiği kütüphaneyi okuyor.
Her satırın anahtarı tek sözcük, çünkü denetim boşluklu bir anahtarı hiç okumuyor. Deney
için okunmayan ya da kaynağıyla karşılaştırılamayan tek bir satır bile denetimi
düşürüyor (`K-187`).

| Alan | Değer | Nereden |
|---|---|---|
| `model_tag` | `qwen2.5-coder:32b-instruct-q4_K_M` | birincil hücrenin modeli (ön kayıt A.2'nin 25 Eylül eki) |
| `serving_mode` | `local` | Ollama |
| `max_output_tokens` | **4000** | `config/recording.yaml` |
| `no_progress_limit` | **40** | `config/recording.yaml`; durma kuralı |
| `shield_mode` | **`shadow`** | koşucunun mount varsayılanı |
| `temperature` | **0,2** | `config/models.yaml` |
| `base_seed` | **123** | `config/models.yaml` |
| `seed_count` | **3** | `config/models.yaml`; her görev üç tohumla |
| `num_ctx_requested` | **32768** | `config/models.yaml` |
| `kv_cache_type` | **`q8_0`** | `config/models.yaml` |
| `flash_attention` | **1** | `config/models.yaml` |
| `step_ceiling` | `min(max(2 × çapa, 20), 150)` | bant taramasının formülü; `scripts/run_experiment.py` aynı üç sayıyı taşıyor |
| `min_expected_saving` | **1** | beş koşul yapılandırmasında aynı (`K-175`) |
| `library_id` | `v0-gap2-sup3-0c3f4ac` | §18.2'nin teslim ettiği kütüphane; analiz kümeleri onunla türetildi |
| `index_id` | `v0-sup1-0c3f4ac` | aynı blokta madenlenen indeks |
| `task_set` | **104** | değerlendirme örnekleminin eylem tabakası (`results/experiment-order.json`) |
| `covered_tasks` | **103** | kartlı kolun en az bir kartla ulaştığı görevler (`results/experiment-sets.json`) |
| `task_order_seed` | **123** | `base_seed`; her görevin anahtarı `sha256("123:" + task_id)`, sıra anahtarlar artan (`K-183`) |
| `task_order` | `dcbdbd43cdc495372cdd7a0149647888881110fd9d49ca4fda1010bcfdbd32b8` | sıranın özeti (`results/experiment-order.json`) |
| `conditions` | `baseline, skills_failures, irrelevant_retrieval` | faz 1; faz 2'nin iki koşulu (`skills`, `failures`) aynı koşucuyla, sonra |
| `runtime` | **A100** | 32B'nin ölçülen dosyası 19,851 GB; T4'ün 15360 MiB'ine sığmıyor (§16.1) |
| `model_file_gb` | **19,851** | §16.1'de bu etiketin ölçülen dosya boyutu |
| Komut | `uv run python scripts/run_experiment.py dny --tasks 10` | ilk dilim; `--tasks` dilimin boyutu, şart değil: her oturumda kullanıcı seçiyor |

**Kartsız görev (K1).** `8ce6779_3`'te kartlı kol hiç kart almıyor. Orada yalnız baseline
koşuyor, üç epizot; kart taşıyan koşulların hiçbiri bu görevde başlamıyor. Görev A.3'ün
kapsanan görevlerinin dışında, yani hiçbir onaylayıcı kontrastta değil.

**Hacmi eşleşmeyen iki görev.** `d194965_1` ve `d194965_3`'te alakasız kol beş beceri
kartı yerine üçle koşuyor. Epizotları `volume_matched = 0` taşıyor ve o kolu içeren her
onaylayıcı analiz bu iki görevi dışlıyor (ön kayıt A.4'ün Düzeltmesi, `K-181`).

### 19.7 Analiz kümeleri, koşucunun kendi slotlarından

Sayılar elle yazılmadı. Koşucunun slot fonksiyonu (`zihin.slots.compose`) her görev ve
kart taşıyan her koşul için çağrıldı, kümeler tek bir kuralla çıktı (`K-184`). Bir test bu
tabloyu `results/experiment-sets.json`'a karşı okuyor.

| Kontrast | Karşılaştırma | Görev |
|---|---|---|
| `Y-1` | `skills_failures` – `baseline` | **103** |
| `Y-6.2` | `skills_failures` – `irrelevant_retrieval` | **101** |
| `Y-4` | `failures` – `baseline` | **101** |
| `Y-5` | `skills` – `baseline` | **103** |
| `Y-6.2`, ikinci okuma | `skills` – `irrelevant_retrieval` | **101** |

Faz 1 **930** epizot: 103 kapsanan görevde 3 koşul × 3 tohum, `8ce6779_3`'te baseline × 3.
