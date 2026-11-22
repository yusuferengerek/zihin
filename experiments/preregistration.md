# Ön kayıt

Sonucu görmeden yazılan beklentiler ve yorum kuralları. Amaç, sonucu görüp
yorumu ona uydurmayı imkânsız kılmak.

Her kayıt tarih ve commit taşıyor. Sonuç geldikten sonra kayda dokunulmuyor;
sonuçla karşılaştırma ayrı bir bölümde yapılıyor.

Belge iki katmanlı. **Birinci bölüm deneyin kendi ön kaydı**: hipotez, hücre,
estimand, koşullar, kapılar, terk kriterleri. **İkinci bölüm kurulum fazının
madde kayıtları**: her mekanizma maddesi koşmadan önce ne beklendiği ve sonradan
ne çıktığı. İkincisi tarihsel kayıt, birincisi bağlayıcı sözleşme.

---

# Bölüm A — Deneyin ön kaydı

**Yazıldığı an:** kurulum fazının sekiz maddesi bitti, hiçbir mekanizma koşusu
yapılmadı. Ön koşul kapısı bir kez ateşledi ve model ailesi yeniden seçiliyor;
bu ön kayıt ailenin yeniden seçilmesinden **sonraki** koşuyu bağlıyor.

**Donmamış tek alan** §A.9'daki ayar bütçesinin sayısı. Bu belge o sayı
konmadan tam anlamıyla donmuş sayılmıyor ve sebebi §A.9'da yazılı.

## A.1 Hipotez ve iki araştırma sorusu

**Hipotez.** Derlenmiş beceriler ve açık bir başarısızlık indeksi, ayrılmış
görevlerde çözüm için gereken **model çağrısı** sayısını düşürür.

**Birinci soru — onaylayıcı.** Derlenmiş beceriler ve açık bir başarısızlık
indeksi, ayrılmış görevlerde çözüm için gereken model çağrısı sayısını düşürüyor
mu?

**İkinci soru — keşifsel.** İncelenen model boyutları içinde bu etki sistematik
olarak ortadan kalkıyor mu?

İkincisi keşifsel çünkü ölçek ekseni üç noktadan oluşuyor ve üç nokta bir
eğrinin şeklini onaylayıcı olarak belirlemeye yetmiyor. İkinci soru birinciye
bağlı: ölçek ekseninin en az iki noktası ön koşul kapısını geçmezse ikinci soru
ölçülemez hâle geliyor.

**Sormadığımız iki şey.** Başarı oranının artıp artmadığını sormuyoruz —
birincil metrik başarı değil, çözüme giden yolun uzunluğu. Mekanizmaların modeli
daha "akıllı" yapıp yapmadığını da sormuyoruz; model sabit, değişen bağlama
giren bilgi.

## A.2 Birincil hücrenin tanımı

**Tek hücre, ve tanımı ölçümden önce kapalı:**

| Boyut | Değer |
|---|---|
| Karşılaştırma | mekanizmalar açık (`skills_failures`) ile taban |
| Metrik | görev başına **model çağrısı** |
| Model | ana eksenin **en büyük yerel noktası** |
| Görev kümesi | **görülmemiş** alt küme (ezberleme kapısının bölmesi) |
| Yön | iki taraflı |

En büyük nokta seçiliyor çünkü hipotez için en zor durum: model büyüdükçe
biriken deneyimin katkısının azalması beklenen yön.

**Geri kalan her şey keşifsel:** diğer modeller, diğer bölme, diğer koşul
çiftleri, iki kontrol noktası, bütün ikincil metrikler. Keşifsel bir sonucun
onaylayıcı gibi sunulması bu belgenin engellemek için var olduğu şey.

### Ek — 25 Eylül 2026: birincil hücrenin modeli (KEŞİFSEL SEÇİM, onaylayıcı hüküm)

**Yukarıdaki tablo değişmedi.** "ana eksenin **en büyük yerel noktası**" satırı
silinmiyor. Bu ek, o satırın bugün adlandıramadığı modeli adlandırıyor ve
"yerel" şartının neden artık karşılanmadığını yazıyor.

**İlan.** Birincil hücrenin modeli `qwen2.5-coder:32b-instruct-q4_K_M`. Sunum
Ollama, kendi `q4_K_M` dosyamız, 32K bağlam, `q8_0` KV, A100 (kurulum protokolü
§16.2 ve §18.2).

**"Yerel" neydi.** Ana eksen şartı 2 (`05-experiment-design.tr.md`): her nokta
`q4_K_M`, 32K bağlam ve `q8_0` KV altında 8 GB'a sığacaktı, yani projenin kendi
makinesinde koşacaktı. Kısıt karar kaydında ayrı bir madde olarak hiç
yazılmamıştı (A-06, `K-133`). Ölçüme dokunan kısmı sunumun bizde olması:
kuantalama, bağlam ve KV bizim seçtiğimiz değerler, ve künye onları okuyor.

**Neden artık karşılanamıyor.**

1. Yerel üç nokta eksende sıfır verdi ve üçü de tavan sınırlı (A.6, A.11'in
   ekleri).
2. `S-14` pilottan önce **aşağı** daralmaya izin vermişti: en küçük nokta tabana
   yapışırsa eksen 3B ve 7B'ye iner. Yukarı yol aynı kayıtta **açıkça kapalıydı**,
   donanım yüzünden: "14B 8 GB'a sığmadığı için yukarı doğru telafi yok".
   Colab'ın GPU'su o engeli kaldırdı. Yani yukarı uzatma `S-14` tarafından
   önceden yetkilendirilmemişti; **sonradan alınmış bir karar**, ve yerel kilit
   20 Ağustos 2026'da kullanıcının açık onayıyla açıldı (`K-133`'ün 25 Eylül ekleri).
3. 32B eksenin tavanı bağlamayan tek noktası: `b32c`'de tavana çarpma %6,7; eylem
   tabakasında 7/25 = **0,280** (`results/stratum-rates.json`).
4. Kütüphane ve indeks 32B'nin kendi `train` epizotlarından madenlendi
   (`v0-gap2-sup3-0c3f4ac`, `v0-sup1-0c3f4ac`; `K-159`, `K-164`). Korpus kuralı
   kütüphaneyi modele bağlıyor: başka bir noktada birincil hücre başka bir modelin
   deneyimini sınardı.

**Korunan.** Aile ve kuantalama kilidi (beşi de `qwen2.5-coder`, beşi de
`q4_K_M`); sunumun bizde olması; "en büyük" gerekçesi — 32B eksenin en büyük
noktası, yani hipotez için en zor durum hâlâ bu hücre.

**Bırakılan.** 8 GB şartı ve kendi donanımımız.

**`01-problem-definition.tr.md` ile gerilim, ve kabul edilen bedel.** O belge
daha pahalı donanımı ve dışa bağımlılığı **kabul edilmeyen bedeller** sayıyor,
çünkü ölçülmek istenen kazanç modelin büyümesinden bağımsız bir kazanç. Birincil
hücreyi kiralık bir A100'e taşımak bu iki bedeli **bu hücrede kabul etmek**
demek: hesap kiralık, ve koşu Colab'a bağımlı. Hipotezin sorusu değişmiyor —
model sabit, değişen bağlama giren bilgi — ama o sorunun sorulduğu donanım
projenin kendi koşulu olmaktan çıktı, ve bu burada yazılı.

**Keşifsel etiket yalnız seçime bağlı; `Y-1` onaylayıcı kalıyor.** Nokta sıfırlar
görüldükten sonra seçildi, yani seçim veri güdümlü ve öyle etiketleniyor. Ama
seçimin gördüğü veri yalnız taban koşuluydu, ve bu ölçüldü: kayıtta 32B etiketli
her epizot `baseline` — `qwen2.5-coder:32b-instruct-q4_K_M` 238, OpenRouter'daki
32B 27 — ve kartlı tek bir 32B epizodu yok. Seçim ön koşul kapısının verisine
baktı, mekanizmanın etkisine bakmadı; mekanizmanın bu modeldeki sonucu henüz hiç
görülmedi. Bu yüzden `Y-1`'in hükmü onaylayıcı kalıyor. Keşifsel olan, **hangi
modelde** sorulduğu.

**Ne değişmiyor.** A.11'in 25 Ağustos eki: 32B'nin ölçek eksenindeki yeri — ikinci
soru için — keşifsel. Bu ek birinci sorunun hücresini adlandırıyor, ikincininkini
değil.

**Güç.** Bu ek `S-68`'i çözmüyor: 0,280 türetilen eşiğin altında.

**Ortam.** A100 Ampere 8.0; eksenin diğer noktaları Ada 8.9 kartlarda ölçüldü
(`S-61`).

## A.3 Estimand ve sansür — iki ayrı nicelik

**Estimand.** Bütün kapsanan görevlerde, görev bazında eşleştirilmiş model
çağrısı farkı. Çözülmeyen epizotlar adım tavanında **sansürlenmiş gözlem**
olarak giriyor, gerçekte kaç adım sürecekleri bilinmediği için.

**Kestirim.** Birincil kestirim **tavana kadar kısıtlanmış ortalama**, güven
aralığı görev kümesiyle **bootstrap**. **Wilcoxon** sansürsüz alt kümede
sağlamlık kontrolü. Duyarlılık analizi tavanın **1,5 ve 2 katıyla**
tekrarlanıyor.

**"İki koşulun da çözdüğü" analizi ikincil** ve adı koşullu verimlilik. Birincil
sayılırsa sansür seçilime dönüşür.

### Karıştırılmayacak iki nicelik

Bu ayrım ön kaydın en çok istismara açık yeri, o yüzden açıkça yazılıyor.

| | Tavana çarpma oranı | Sansür oranı |
|---|---|---|
| Ne | Adım tavanına dayanan epizot oranı | Doğrulayıcının geçirmediği epizot oranı |
| Türü | **Ölçüm artefaktı** | **Sonuç** |
| Kuralı | Yüzde onun altında kalmalı; tavan çarpanı buna göre seçiliyor | Yüzde on kuralı **uygulanmıyor** |

İkincisine yüzde on kuralı uygulansaydı tabana yüzde doksan başarı şartı konmuş
olurdu ve bu ölçülmüş hâlle bağdaşmıyor.

**Sansür sonlandırma sebebine göre değil doğrulayıcı hükmüne göre sayılıyor.**
Doğrulayıcının geçirmediği her epizot sansürlü: tavana çarpsın, durma kuralıyla
kapansın ya da ajan tamamlandı bildirsin (K-53). Sonlandırma sebebi ayrı bir tanı
alanı ve ayrı raporlanıyor.

## A.4 Altı koşul ve çıkarıcı kontrol

| Koşul | Beceri kartları | Hata kartları | Ne izole ediyor |
|---|---|---|---|
| `baseline` | yok | yok | referans noktası |
| `irrelevant_retrieval` | alakasız | alakasız | bağlam hacmi |
| `skills` | gerçek | alakasız | beceri içeriği |
| `failures` | alakasız | gerçek | hata içeriği |
| `skills_failures` | gerçek | gerçek | ikisinin birlikte etkisi |
| `naive_compiler` | naif madencilik | alakasız | madencilik kalitesi |

**İki kritik kontrast, bozulursa analiz planı çöker:**

1. Taban ile alakasız getirme arasındaki fark **saf bağlam hacmi**.
2. Sadece beceriler ile alakasız getirme arasındaki fark **saf içerik**.

**Çıkarıcı kontrol.** Mekanizma etkisi, mekanizma koşulunun tabana göre
kazancından alakasız getirme koşulunun tabana göre kazancı çıkarılarak
hesaplanıyor, görev bazında eşleştirilmiş.

**Toplanabilirlik varsayımı ve ölçülmüş şüphe.** Hacim etkisi ile içerik
etkisinin toplanabilir olduğu varsayılıyor. Kurulum aşamasında ölçülen ayna
bulgusu bu varsayımın bu korpusta muhtemelen tutmayacağını söylüyor (K-84):
beceri kütüphanesinin dördü de giriş ve hata indeksinin en sık kalıpları da
giriş hatası, yani ikisi aynı arızayı hedefliyor. Birinin kapattığı arızayı
diğeri ikinci kez kapatamaz. **Bu beklenti ölçümden önce yazılıyor**, sonuç
toplanabilir çıkmazsa "sonradan fark ettik" denemesin diye.

**Kart sayısı göreve göre, koşula göre değil.** Her görev için önce getirme
koşuluyor; bulunan kart sayısı o görevin dolgu payını belirliyor; kart taşıyan
beş koşul aynı sayıda kart alıyor. Mekanizmalı koşullara da dolgu konuyor, yoksa
ölçülen şey mekanizma değil bağlam uzunluğu olur.

### Ek — 25 Eylül 2026: bir beceri kartı en az bir model çağrısı kazandırmalı (`min_expected_saving = 1`)

**İlan.** Getirici bir beceri kartını yalnız beklenen tasarrufu en az **bir model
çağrısı** ise slota koyuyor. Beklenen tasarruf `(observed_steps − 1) × support`:
gövdenin oluşumlarında kapladığı adım sayısının medyanı eksi bir, görev desteğiyle
çarpılmış. Değer altı koşul yapılandırmasında aynı (`retrieval.min_expected_saving`)
ve koşucu onu oradan okuyor; bugüne kadar koşucunun içinde yazılı `0`'dı ve hiçbir
yerde ilan edilmemişti (`K-50`).

**Gerekçesi metriğin tanımı.** Birincil metrik model çağrısı; bir adım bir model
çağrısı (`K-82`). Tek adımda yapılan bir diziyi önceden vermek o adımı ortadan
kaldırmıyor, çünkü modelin diziyi yürütmek için yine bir adıma ihtiyacı var. Sıfır
tasarruflu bir kart birincil metriği hareket ettiremez; slotta yalnız hacim olur.

**Neyi düşürdüğü** (`results/declared-filters.json`, getiricinin kendisiyle,
birincil örneklemin 104 görevinde):

| Beceri | Destek | Gövde | Oluşum başına adım | Tasarruf |
|---|---|---|---|---|
| `POST spotify.auth/token` | **27** | `GET supervisor.account_passwords` → `POST spotify.auth/token` | 28 oluşumun **28'i tek adım** | 0 |
| `following_artists` ×3 | 5 | aynı çağrının üç tekrarı | medyan 1 (oluşumların %82'si) | 0 |
| `following_artists` ×5 | 4 | aynı çağrının beş tekrarı | medyan 1 (%63) | 0 |

**En yüksek destekli beceri neden düşüyor.** Kütüphanenin en çok desteklenen
becerisi, çünkü kimlik doğrulama spotify'a dokunan her görevde gerekli. Ama
ajan onu her seferinde, 28 oluşumun 28'inde, iki çağrıyı tek bir kod bloğunda
yazarak yaptı. Parolayı okumak ve jetonu almak zaten tek model çağrısı sürüyor;
kart o çağrıyı kaldıramaz. Destek becerinin ne kadar sık gerektiğini ölçüyor,
ne kadar kazandıracağını değil — ve bu becerinin kazandırabileceği şey sıfır.
İki tekrar becerisi aynı sebepten: ajan tekrarı bir döngü olarak tek adımda yazıyor.

**Görevlere etkisi.** Üç beceri de aynı 25 görevin slotuna giriyordu; o 25
görevin hepsi slottaki bir beceri kartını kaybediyor: beceri kartı 6 → 3 (17
görev), 7 → 4 (6 görev), 8 → 5 (2 görev). Beş slotlu bölümde bu 25 görevde slot
beşten üçe, dörde ya da beşe iniyor. Hiçbir görev son beceri kartını kaybetmiyor;
en az bir kart alan görev 104'te 103, önce de 103. Kart sayısı görev başına
getiriciden geliyor (A.4), yani bu 25 görevde kart taşıyan beş koşulun hepsi aynı
daha küçük sayıyı alıyor.

**Neyi düşürmüyor.** Kütüphaneyi: beceriler kayıtta duruyor ve eşik okuma
anında uygulanıyor (Bölüm B, Madde 3). Kütüphanenin boyutu `Y-5` için getirilebilir
beceri sayısıyla ölçülüyor (A.8); bu eşikle getirilebilir beceri 11'den 8'e iniyor.

### Ek — 25 Eylül 2026: alakasız kol aynı süzgeçten geçiyor ve hata kartları da alakasız

**İlan.** `irrelevant_retrieval` koşulunun kartları, kartlı koşulun kartlarıyla
**aynı süzgeçlerden** geçiyor — aynı kütüphane, aynı indeks, aynı değer eşiği
(yukarıdaki ek), aynı hata kartı süzgeçleri, aynı sıra — ve yalnız görevin
uygulamalarıyla ilişkide ters: alakasız kol görevin adlandırmadığı uygulamaların
**hem beceri hem hata kartlarını** alıyor. İki kol getiricide tek bir seçimden
geçiyor, alakayı ters çeviren tek bir bayrakla (`K-176`). Hiçbir görevin
getiremeyeceği kartlar — uygulamaları yalnız altyapı olanlar — alakasız kola da
girmiyor.

**Gerekçe.** Kontrol kolu kartlı koldan **yalnız alakada** farklı olmalı; yukarıdaki
iki kritik kontrastın ikincisi (içerik mi hacim mi) buna dayanıyor.

**Neyi düşürdüğü.** Bugüne kadar kurulu alakasız kol — §12'nin üç kollu koşusunda
kullanılan hâli — yalnız beceri taşıyordu, değer eşiği uygulamıyordu, ve hata kartı
hiç taşımıyordu; gerekçesi "başka bir uygulamanın hata kartı ile hiç hata kartı aynı
slot içeriği" idi. Bu ilan o tanımı ve gerekçesini düşürüyor. Ölçüldü
(`results/declared-filters.json`, getiricinin kendisiyle, 104 birincil görevde):

| | Eski alakasız kol | İlan edilen |
|---|---|---|
| Slotu kartlı koldan küçük olan görev | **86** | **2** |
| Slottaki hata kartı, toplam | 0 | 520 |
| Kartlı kol kadar beceri kartı veremediği görev | — | 2 (`d194965_1`, `d194965_3`) |

Eski kolun slotu 86 görevde kartlı koldan küçüktü, çünkü kartlı kolun hata kartlarının
karşılığı yoktu: "hacim kontrolü" hacmi eşlemiyordu.

**Açık kalan, ve bu ekin kurmadığı.** Yeni kol çoğu görevde kartlı koldan **fazla**
kart verebiliyor: 93 görevde slotu 5 beceri artı 5 hata kartıyla dolu, oysa kartlı
kol o görevlerin birçoğunda daha az alıyor. A.4 kart sayısının görev başına
getiriciden geldiğini ve kart taşıyan koşulların aynı sayıyı aldığını söylüyor; iki
kolu görev başına aynı sayıya indirmek koşucunun işi ve henüz kurulmadı. Kurulana
kadar hacim kontrastı eşlenmiş değil.

### Ek — 25 Eylül 2026: kart sayısı görev başına eşit; eşleşemeyen görevde kol koşmuyor

**İlan.** Kart taşıyan bir koşulun bir kart türünü alakasız havuzdan doldurduğu
her yerde, o türden **kartlı kolun o görevde slota koyduğu sayı kadar** kart alıyor
— ne fazla ne eksik; kartlı kol hiç almıyorsa hiç. Tür tür: beceri beceriyle, hata
hatayla. Kesim getiricide tek bir fonksiyon (`matched_to`, `K-179`).

**Ölçüldü** (`results/declared-filters.json`, getiricinin kendisiyle, birincil
örneklemin 104 görevinde):

| Kol | Kartlı kolla eşit | Eşleşemeyen |
|---|---|---|
| `irrelevant_retrieval` (iki tür de alakasız) | **102** | 2: `d194965_1`, `d194965_3` |
| `skills` (hata slotu alakasız havuzdan) | 104 | 0 |
| `failures` (beceri slotu alakasız havuzdan) | 102 | aynı 2 |

İki görevin sebebi aynı: kartlı kol beş beceri kartı alıyor, alakasız havuzda değer
eşiğini geçen üç beceri var. Bir görevde (`8ce6779_3`) kartlı kol hiç kart almıyor;
orada kontrol de sıfır, ve görev A.3'ün tahmin tanımındaki "kapsanan görevler"in
dışında.

**Eşleşemeyen görevde ne oluyor: o kol o görevde koşmuyor.** Eksik koşmuyor, çünkü
eksik bir kontrol kolu kontrol ettiği koldan daha az hacim taşır — bu ekin ve
yukarıdaki iki kritik kontrastın önlemek için var olduğu şey tam olarak bu.
Doldurulmuyor da, çünkü havuzda o türden başka kart yok. Bu yüzden:

- **Birincil hücre etkilenmiyor.** `skills_failures` ile `baseline` iki görevde de
  tanımlı; `Y-1` 104 görevin kapsananlarında okunuyor.
- **O kolu içeren her karşılaştırma, kolun tanımlı olduğu görevlerde** yapılıyor ve
  dışarıda kalan görevler adıyla raporlanıyor: çıkarıcı kontrol ve `Y-6`'nın ikinci
  dalı 102 görevde, `Y-4` 102 görevde, `Y-5` 104 görevde.
- Koşucu tanımsız bir kontrol kolunu başlatmıyor ve sebebini adıyla söylüyor.

**Düzeltme — 26 Eylül 2026: eşleşemeyen görevde kol eksik koşuyor ve işaretleniyor.**
Yukarıdaki ekin "o kol o görevde koşmuyor" hükmü düşüyor; ilk `dny` epizodundan önce,
hiçbir sonuç görülmeden (`K-181`).

- **Eksik koşuyor.** Alakasız havuz bir türde kartlı kolun sayısına yetmiyorsa kol
  havuzda ne varsa onunla koşuyor: `d194965_1` ve `d194965_3`'te alakasız kol beş beceri
  kartı yerine üçle, beş hata kartıyla. Epizotları `volume_matched = 0` taşıyor.
- **Tek kural.** `volume_matched = 0` bir kolu içeren her onaylayıcı analiz o görevleri
  dışlıyor. Kolu içermeyen analiz dışlamıyor.
- **Gerekçe, kullanıcının kararı.** Eksik bir kontrol kolu kontrol ettiği koldan az
  hacim taşır ve bu "içerik önemli" yönünde yanlılık yapar; o yüzden içerik kontrastı
  o görevlerde okunmuyor. Ama koşmamak, kolu içermeyen karşılaştırmaların da elinden
  görevi alıyordu, ve işaret koşudan önce ilan edildiği için dışlama sonuçtan bağımsız.
- **Kartsız görev değişmiyor.** Kartlı kolun hiç kart almadığı görevde (`8ce6779_3`) kart
  taşıyan hiçbir koşul başlamıyor; o görev A.3'ün kapsanan görevlerinin dışında.
- **Yukarıdaki görev sayıları bu düzeltmeyle geçersiz** — "`Y-4` 102, `Y-5` 104"
  kartsız görevi saymıyordu. Sayılar bu eke elle yazılmıyor: koşucunun kendi kart
  seçiminden türetiliyor ve kurulum protokolünün deney bölümünde duruyor.
- **Beş koşul tek seçimden geçiyor** (`zihin.slots`): alakasız havuzdan gelen her tür,
  kartlı kolun o görevde slota koyduğu sayıya kesiliyor. Koşucu ve analiz kümelerini
  sayan ölçüm aynı fonksiyonu çağırıyor.

### Ek — 26 Eylül 2026: deney iki fazda, fazın içinde görev dilimleri (KOŞUDAN ÖNCE)

**İlan, kullanıcının kararı.** Deney koşullara göre iki faza bölünüyor. Her fazın içinde
görevler dilim dilim ilerliyor. İlan ilk `dny` epizodundan önce (`K-188`).

- **Faz 1:** `baseline`, `skills_failures`, `irrelevant_retrieval`, eylem tabakasının 104
  görevinin hepsinde. `Y-1` (birincil) ve `Y-6`'nın ikinci dalı (içerik mi hacim mi) bu
  üçle cevaplanıyor. Kartlı kolun hiç kart almadığı `8ce6779_3`'te yalnız baseline koşuyor,
  yani faz 1 930 epizot.
- **Faz 2:** `skills` ve `failures`, aynı 104 görevde. `Y-4` ve `Y-5` bu fazla
  cevaplanıyor. Faz 1 bittikten sonra, bütçe varsa. Beş koşulun hepsi ilk `dny` epizodundan
  önce koşucuda kuruldu ve koşucu donduruldu (`K-181`, `K-182`). Faz 2 için ölçümü
  tanımlayan kod değişmeyecek; faz 1'in baseline'ı faz 2'nin kollarıyla bu yüzden
  karşılaştırılabilir kalıyor.

**Neden koşula göre iki faz, ama fazın içinde göreve göre dilim.** Her faz kendi
kontrastları için tam çift veriyor: faz 1 bittiğinde `Y-1` ve `Y-6`'nın ikinci dalı faz 2'yi
beklemiyor. Fazın içinde görev görev ilerlemek, her dilimin kendi başına eşleştirilmiş analiz
edilebilmesi için. Bir dilimin görevleri, o fazın her koşulunun her tohumunu taşıyor.

**Neden atlanan görev yok.** Hacmi eşleşemeyen koşullar `d194965_1` ve `d194965_3`'te eksik
koşuyor ve işaretleniyor (yukarıdaki Düzeltme, `K-181`). Hangi analizin o iki görevi
dışladığı koşudan önce ilan edildi. Kümeler kurulum protokolünün §19.7'sinde, koşucunun
kendi slotlarından (`K-184`).

**`Y-1`'in görev kümesi.** `Y-1` eylem tabakasının kapsanan görevlerinde okunur (103);
A.2'deki görülmüş/görülmemiş bölmesi yönsel raporlanır.

**Sıra ve dilim.** Görevler ilan edilmiş bir tohumdan gelen sırayla alınıyor, ilerlerken
seçilmiyor (`K-183`). Dilim, sıradaki N görev (`K-185`). Ölçümü tanımlayan bir yol iki dilim
arasında değişirse dilimler havuzlanmıyor ve değişiklik tarihli bir ek istiyor (`K-186`).

## A.5 Metrikler

**Birincil: görev başına model çağrısı.** Ham API çağrısı sayısı birincil değil,
çünkü bir beceri çağrısını tek adım saymak sonucu totolojik kılar.

**Totoloji itirazının cevabı, ölçümden önce.** Bu ortamda ajan durumlu Python
yazıyor ve taban da tek turda birden çok API çağırabiliyor. Beceri paketleme
imkânı vermiyor, doğrulanmış paketi önceden veriyor; kazanç ajanın hangi
çağrıların hangi sırayla geleceğini keşfetmek için harcadığı turlardan geliyor.

**Zorunlu tanı metriği: model çağrısı bölü başarılı API çağrısı.** Yorumu burada
yazılı: oran hareket etmiyorsa kazanç paketlemeden geliyor, hareket ediyorsa
israfın azalmasından da geliyor.

**Dereceli skor tanı metriği, ikincil sonuç değil.** Birincil metriğe ve
yanlışlama kapılarına girmiyor. Veriyi gördükten sonra doğduğu açıkça yazılıyor:
kurulum aşamasında ikili başarı her yerde sıfırken ayrım gücü olan tek nicelik
olarak türetildi.

**Eylemsizliğin ödüllendirilebildiği ölçüldü ve dereceli skorun sebebi bu.**
`0de03ea_1`'de ham skor 3'e 2, no-op tabanına göre düzeltilince 2/3'e 0/3; ve
kartlı kol eyleme geçtiği için bedava bir geçişi kaybetti. Birincil metrik ham
geçiş sayısı olsaydı mekanizmaların eylemsizliği artırması ödüllendirilirdi.

### Ek — 28 Ağustos 2026: görev tipi tabakalaması (KEŞİFSEL)

**Yukarıdaki A.5 değişmedi.** Bu bir ek, ve **keşifsel** etiketli: tip ayrımı
sonuçlar görüldükten sonra yapıldı. Onaylayıcı bir hipotez sınamasının parçası
değil ve öyle raporlanmayacak.

**Karar.** Cevap tipi görevler değerlendirme örnekleminden **çıkarılmıyor**.
Tabakalanıyor ve **ayrı** raporlanıyor:

| Tabaka | Görev | Rolü |
|---|---|---|
| Eylem tipi (`answer+world`) | 105 | **birincil ölçüm** |
| Cevap tipi (`answer`) | 18 | ayrı raporlanıyor, birincil sonuca girmiyor |

Sayılar `results/task-types.json` içinde; burada tekrarlanmıyor, atıf veriliyor.
Sınıflandırıcı `scripts/analyze_passes.py`'nin `task_shape` fonksiyonu, ikinci
bir kopya yazılmadı.

**Gerekçe: iki tabakada doğrulayıcı aynı güçte değil, ve fark ölçüldü.**

- Cevap tipi görevlerin **on sekizinin on sekizi** "hiçbir model değişmedi"
  iddiası taşıyor. Bu testi **hiçbir şey yapmayan bir ajan geçiyor**, tanım
  gereği.
- Cevap tipi görevlerin test medyanı **iki**. Yani bedava geçen o test hükmün
  yarısı; geriye tek bir dizge eşitliği kalıyor.
- Eylem tipi görevlerin test medyanı **yedi**, ve **hiçbirinde** o bedava test
  yok.

İkisini havuzlamak sıkı bir ölçümle gevşek bir ölçümü karıştırmak olurdu, ve
karışımın yönü belli: gevşek tabaka mekanizmaların ölçülmesini kolaylaştırır,
çünkü orada tesadüfi bir geçiş daha ucuz.

**Bu ayrım daha önce bir kez ısırdı.** `0de03ea_1`'de ham skor 3'e 2, no-op
tabanına göre düzeltilince 2/3'e 0/3, ve kartlı kol **eyleme geçtiği için**
bedava bir geçişi kaybetti (A.5). Tabakalama o gözlemin örneklem tarafındaki
karşılığı. Bant etiketinin zorluğu değil referans çözümün yolunu gösterdiği de
aynı sınıftan (`S-62`).

**Mekanizmaların sınanabileceği yer zaten eylem tabakası.** Beceri kütüphanesi
API çağrı dizileri tutuyor, hata indeksi çağrı başarısızlıkları; ikisi de yalnız
dünyayı değiştiren görevlerde işe yarayabilir. Birincil ölçümü oraya koymak
mekanizmayı kayırmak değil, mekanizmanın iddia ettiği yerde ölçmek.

**Bu ekin kabul ettiği bedel.** Birincil ölçümün örneklemi 123'ten **105**'e
iniyor. Güven aralığı genişliği örneklem boyutuna bağlı, yani daralma bir
maliyet ve okunan her aralıkta taşınacak.

**Bu ekin izin vermediği.** Cevap tabakasının sayıları birincil sonuç gibi
alıntılanamaz, ve iki tabaka sonradan "toplam şu çıktı" diye birleştirilemez.
Birleştirilirse birleştirmenin kendisi ayrıca yazılır.

**Yanlışlama kapıları hangi tabakada işliyor.** A.7'nin üç kapısı **eylem
tabakasında** değerlendiriliyor. Cevap tabakasında ayrıca hesaplanıyorsa
"keşifsel" damgasıyla ve kapı hükmü vermeden raporlanıyor.

### Ek — 25 Eylül 2026: tabakalar 104 ve 15

**Yukarıdaki tablo değişmedi.** Dokunulan görev listesi kayıttan üretilince
(A.10'un eki) değerlendirme örnekleminden dört görev daha çıktı ve tabakalar
yeniden sayıldı (`results/task-types.json`):

| Tabaka | 28 Ağustos | 25 Eylül | Çıkan |
|---|---|---|---|
| Eylem tipi (`answer+world`) | 105 | **104** | `0de03ea_1` |
| Cevap tipi (`answer`) | 18 | **15** | `0a9d82a_1`, `0a9d82a_2`, `0a9d82a_3` |

**Birincil ölçümün örneklemi 104.** Tabakalamanın gerekçesi aynı: cevap tipinin
on beşinin on beşi "hiçbir model değişmedi" iddiası taşıyor, eylem tipinin hiçbiri.

**`0de03ea_1` bu bölümün örnek görevi.** Çıkması yukarıdaki kuralları
değiştirmiyor: dereceli skorun tanı metriği olması ve ham geçiş sayısının birincil
olmaması, test dosyasının yapısına dayanıyor — eyleme geçen bir ajanın
düşürebileceği bir `no_op_pass` testi var — ve o yapı görevin örneklemde olup
olmamasından bağımsız.

### Ek — 25 Eylül 2026: bu bölümün örneği tek bir epizot

**Yukarıdaki kurallar değişmedi.** "Eylemsizliğin ödüllendirilebildiği ölçüldü"
cümlesinin dayandığı gözlem **tek bir epizot**: `demo` koşusunun `0de03ea_1`
üzerindeki kartlı epizodu. Aynı görevin sonraki dört kartlı epizodunun hiçbirinde
kol bir bedava testi kaybetmedi (`results/no-op-example.json`). Örnek tekrarlanmadı
ve `S-56`'nın sınıfında; sınırlaması `S-77`.

**Kural ayakta**, çünkü gözleme değil test dosyasının yapısına dayanıyor: eyleme
geçen bir ajanın düşürebileceği bir `no_op_pass` testi var. Yukarıdaki cümle
"ölçüldü" değil "bir kez gözlendi" diye okunmalı.

## A.6 Ön koşul kapısı — bir kez ateşledi

**Kural.** Taban koşulu ayrılmış kümede ilan edilen asgari başarı oranını
tutturamazsa **deney hipotezi test edememiştir ve mekanizma sonuçları
raporlanmaz.**

**Ateşleme: 11 Ağustos 2026.** Qwen2.5-Coder 1,5B, 3B ve 7B AppWorld'ün otuz
görevlik tabakalanmış örnekleminde hiçbir görevi çözmedi. Üç tabakalama denendi
ve hiçbiri ölçülebilir bant açmadı: referans uzunluk, güçlü modelin çözdüğü alt
küme, uygulama kümesi.

**Sıfırların düzenekten gelmediği gösterildi: 12 Ağustos 2026.** Aynı otuz
görevde DeepSeek V4 Flash 0731 bizim hattımızda 20/30, yayımlanmış gpt-4o koşusu
15/30. Bir yazı kısıtı buradan çıkıyor ve iki yerde ayrı tartışılmasın diye
burada sabitleniyor: **"düşünme kapalı, 20/30" cümlesi kurulamaz.** O koşuda
düşünme açıktı ve bu ilan edilen koşul değildi (S-34). Savunulabilir hâli:
*DeepSeek V4 Flash 0731 aynı otuz görevde bizim hattımızda 20/30 aldı; o koşuda
düşünme açıktı ve bu ilan edilen koşul değildi.*

**Kapının dayandığı ölçümün temizliği sonradan sınandı ve tuttu.** İlk tarama
eski durma kuralıyla koşulmuştu (S-27). Üç tekrar yapıldı: `bant2` 0/30, `bant3`
0/30, ve `bant3-kapalı` **durma kuralı tamamen kapalıyken** 26 epizotta 0. Kapı
temiz veriye dayanıyor.

**Ateşlemenin sonucu:** model ailesi yeniden seçiliyor. Bu ön kayıt yeniden
seçilen aileyle yapılacak koşuyu bağlıyor.

### Ek — 28 Ağustos 2026: geçiş oranı eşiği türetildi (KEŞİFSEL)

**Yukarıdaki ilanlar değişmedi.** Bu ek onlardan bir sayı **türetiyor**, hiçbirini
düzeltmiyor.

**Yöntem.** Sonuç üzerinde ayrım yapan her ilan örtük bir aralık genişliği şartı
taşıyor. Şartlar çıkarıldı, `results/interval-width.json`'daki ölçülmüş
genişliklerle çaprazlandı, ve eşik en büyük şartın okunur hâle geldiği oran
olarak alındı. Hesap `results/pass-threshold.json` içinde; karar K-146.

**Sonuç.** Eşik beklenen etkiye göre **0,75-0,85**; birincil tabakada ölçülen
oran **0,280**. Aradaki fark `S-68`. Ezberleme kapısı beklenen etki %10 ise
hiçbir oranda hüküm veremiyor: `S-67`.

**Keşifsel, çünkü türetme sonuçlar görüldükten sonra yapıldı** ve üç payı
(hacim, tek kol, eksen ayrışması) ilan etmeyi gerektirdi. Onaylayıcı bir güç
analizi değil; ilan edilmiş ayrımların bu tasarımda okunup okunamayacağının
ölçümü.

**Bu ek bir karar vermiyor.** Hangi ayrımların düşürüleceği, örneklemin
büyütülüp büyütülmeyeceği ya da modelin değiştirilip değiştirilmeyeceği açık.

**Düzeltme — 25 Eylül 2026: aralık genişliği taraması 123 görevle yapıldı, ve eşik ondan türetilmedi.**
Yukarıdaki "`results/interval-width.json`'daki ölçülmüş genişliklerle
çaprazlandı" cümlesi yanlıştı, ve ölçüldü. İki ayrı ölçüm var:

| Eser | Örneklem | Eşiğe girdi mi |
|---|---|---|
| `results/interval-width.json` | değerlendirme örnekleminin tamamı, **iki tabaka birlikte**: 123 görev (bugün 119) | **hayır** — `scripts/setup/derive_pass_threshold.py` onu okumuyor |
| `results/pass-threshold.json` | **eylem tabakası**: 105 görev (bugün 104) | evet — genişlikler türetici tarafından bu tabakada yeniden ölçülüyor |

Yani eşik, eylem tabakasında ölçülen genişliklerle çaprazlandı; aralık genişliği
taraması ise tabakalamadan (`K-144`) önce yazılmıştı ve cevap tabakasını da
içeren örneklemde kaldı. Eşiğin sayısı bu düzeltmeden etkilenmiyor: yukarıdaki
"0,75-0,85" eylem tabakasının ölçümü. Etkilenen, aralık genişliği tablosunun ne
hakkında olduğu: birincil tahminin genişliği değil, iki tabakanın havuzlanmış
örnekleminin genişliği. Sessizce düzeltilmedi; tablo olduğu gibi duruyor.

**Ek — 25 Eylül 2026.** Tarama eylem tabakasında yeniden koşuldu:
`results/interval-width-action.json`, 104 görev. Havuzlanmış tablo yerinde ve
süperseded işaretli (`K-174`).

## A.7 Yanlışlama kapıları

Üçü de ölçümden önce yazılı ve sonucu görüp değiştirilmiyor.

| # | Gözlem | Hüküm |
|---|---|---|
| 1 | Mekanizmalar ayrılmış görevlerde model çağrısı sayısını düşürmüyorsa | **hipotez desteklenmemiştir** |
| 2 | Kazanç görülmemiş görevlerde görülmüşün yarısının altına düşüyorsa | **ezberleme doğrulanmıştır** |
| 3 | Kapsama oranı %25'in altındaysa | "test edemedik" değil, **sembolik getiricinin bu ortamda ilgili deneyim bulamadığı bulgusudur** |

**Ezberleme kapısının bölmesi.** Dağılım içi test kümesi ikiye ayrılıyor: eylem
dizisi biriktirmede görülmüş ve görülmemiş görevler. Bölme ölçütü biriktirme
kaydındaki **normalize eylem dizisiyle birebir eşleşme**. Kapı: görülmemiş
görevlerdeki kazancın görülmüş görevlerdeki kazanca oranı, eşik **yarım**.

### Ek — 28 Ağustos 2026: onaylayıcı küme daraltıldı (KOŞUDAN ÖNCE)

**Yukarıdaki üç kapı olduğu gibi duruyor.** Hiçbiri silinmedi ve hiçbirinin
metni değişmedi. Değişen tek şey **hangilerinin hüküm verdiği**.

**Karar.** `Y-2` (ezberleme kapısı) ve `Y-6`'nın birinci dalı (hacim kontrolü)
**onaylayıcı kümeden çıkıyor**. İkisi de raporlanmaya devam ediyor, ama
**yönsel** olarak: görülmüş ve görülmemiş kazançlar ayrı ayrı yazılıyor, alakasız
kolun tabana göre farkı ayrı yazılıyor, ve hiçbiri "kapı ateşledi" ya da
"ateşlemedi" hükmü vermiyor.

**Kalan onaylayıcı ayrımlar üç tane:**

| # | Ayrım | Durum |
|---|---|---|
| `Y-1` | mekanizmalar model çağrısını düşürüyor mu — **birincil soru** | onaylayıcı |
| `Y-6`, ikinci dal | içerik mi hacim mi | onaylayıcı |
| `Y-4` / `Y-5` | tek mekanizma etki gösteriyor mu | onaylayıcı, **beklenen etki %20 ve üstündeyse** |

**Gerekçe, ve korunacak ayrım.** Bu iki kapı **sonuç hoşa gitmediği için**
çıkarılmıyor — sonuç henüz yok, deney koşmadı. Bu örneklem boyutunda **hüküm
üretemedikleri** için çıkarılıyor, ve bu ölçüldü: `S-67`. Ezberleme kapısı
örneklemin yarısını okuyor, o yarının aralığı birincil aralığın 1,42 katı, ve
"kazancın yarısı korundu" ile "hiç korunmadı"yı ayırmak zaten etkinin yarısından
dar bir aralık istiyor. Ölçülen geçiş oranında (0,280) o aralık hiçbir beklenen
etkide o kadar dar değil.

**Bir kapıyı sonucu görmeden daraltmak ile gördükten sonra daraltmak aynı şey
değil**, ve bu ek birincisi. Tarihi ve commit'i kayıtta; `scripts/check_dates.py`
ikisini karşılaştırıyor.

**Tırmanma tetiği, şimdi yazılıyor.** Deney 105 eylem görevinde koşulduğunda
`Y-1`'in bootstrap aralığı **sıfırı dışlayamazsa**, (b) yoluna geçilir: örneklem
büyütülür ve fiyatı K-149'da yazılı. Birincil sonuç okunuyorsa (b) gerekmez ve
istenmez. Bu tetik sonuç görülmeden konuyor, çünkü sonucu gördükten sonra konan
bir tetik tetik değildir.

**Tetiğin onayı: nasıl alındığı ve ne zaman.** Metin değişmedi; değişen tek şey
bu paragrafın var olması. Tetik ilk kez **28 Ağustos 2026**'da, yukarıdaki
hâliyle yazıldı, ve o anda onayı **varsayılmıştı**: yazan taraf onu dört işten
biri olarak listelendiği ve kapanış cümlesinin bütün ilanların girmesini
varsaydığı için onaylanmış saydı, ve bu varsayımı aynı gün açıkça bildirdi.
Onay **aynı gün, ayrı ve açık bir beyanla** verildi.

**Ara durum neden yazılıyor.** Bir tetiğin gücü ne zaman ve nasıl bağlandığında;
"varsayımla yazıldı, sonra açıkça onaylandı" ile "açık onayla yazıldı" aynı şey
değil, ve birincisini ikincisi gibi göstermek tam olarak bu belgenin engellemek
için var olduğu türden bir düzleştirme olurdu. İki an arasında tetiğin metni
değişmedi ve hiçbir sonuç görülmedi, yani ara durum tetiğin bağlayıcılığını
zayıflatmıyor — ama görünmez kalması onu doğrulanamaz kılardı.

**Ne değişmiyor.** Ön koşul kapısı (A.6), altı koşulun tanımı, estimand, sansür
kuralı ve ölçek ekseni yorum tablosu aynı. Daralan şey yalnız **hangi ayrımın
hüküm verdiği**.

**`S-66` bu ekin altında.** Bu daraltmanın dayandığı genişlikler iki tekrarlı
hücreden ölçülen bir gürültü katsayısıyla hesaplandı, yani her genişlik bir alt
sınır. Gerçek değişkenlik büyükse çıkarılan iki kapı **daha da** uzaklaşır,
yaklaşmaz.

### Ek — 25 Eylül 2026: tetiğin fiyatı bir aralık, ve tabaka 104

**Yukarıdaki tetik değişmedi, metni de.** Okunuşunu etkileyen iki şey değişti.

**Tabaka 104.** Tetik "105 eylem görevinde" diyor; dokunulan liste kayıttan
üretilince `0de03ea_1` eylem tabakasından çıktı (A.5'in 25 Eylül eki). Tetik
104 görevde koşulan deneye uygulanıyor.

**Fiyat bir aralık.** Tetiğin işaret ettiği fiyat — `K-149` — yedi tekrarın
medyanıydı. Tekrar başına (`K-168`): beklenen etki %20 ve üstüyse **400–557**
eylem görevi; %30'da yedi tekrarın ikisinde, %50'de birinde havuzun tamamı da
yetmiyor; %10'da hiçbirinde yetmiyor. Tetik ateşlerse (b) yoluna "500 görev"
diye değil bu aralıkla geçilir. A.10'un 25 Eylül ekindeki "500 bu havuzda hâlâ
var" cümlesi medyana bakıyor; aralığın üst ucu havuzun tamamı.

**Ne değişmiyor.** Kapının bu katmanda okunamadığı hükmü: yedi tekrarın hiçbiri,
hiçbir etkide, 104 görevde kapıya ulaşmıyor. Gerekçesi artık bir medyan değil,
dağılımın tamamı.

### Ek — 26 Eylül 2026: kısmi okuma yasağı (KOŞUDAN ÖNCE)

**Kural.** Deney 104 görevin hepsi bitmeden hiçbir onaylayıcı yorum yapılmıyor. Deney
dilim dilim koşuyor ve aylara yayılabilir; bir dilimin sonucuna bakılarak verilen her
karar — durmak, büyütmek, bir şeyi düzeltmek — sonucu görmüş bir karar olur. Bu ek ilk
`dny` epizodundan önce yazılıyor (`K-186`).

**Kısmi sonuç yalnız betimsel.** Bir dilim bittiğinde yalnız üç şey raporlanıyor:
- kaç görev bitti,
- kaç epizot yazıldı,
- tüm koşulların birlikte ortalama süresi.

Geçiş oranı, model çağrısı sayısı, koşula göre hiçbir şey ve hiçbir aralık raporlanmıyor.
Koşula göre süre de yok: bir epizodun süresi model çağrısı sayısını izliyor, yani koşula
göre süre birincil metriğin başka bir adı olurdu.

**`Y-1`'in aralığı tam kümede hesaplanıyor.** Tam küme, planlanan her epizodun yazılmış
olması: kapsanan her görevde 3 koşul × 3 tohum, kapsanmayan görevde baseline × 3. Dilim
etkisine de tam kümeden sonra bakılıyor.

**Makineyle zorlanıyor.** `scripts/analyze_experiment.py` tam küme bitmeden yalnız bu
üç satırı ve dilimlerin havuzlanıp havuzlanamadığını basıyor. `--confirmatory` tam
kümeden önce reddediliyor. Sürücünün kapanış özeti aynı üç satır.

### Ek — 26 Eylül 2026: `Y-6`'nın ikinci dalı faz 1'de `skills_failures` ile okunuyor (SONUÇ GÖRÜLMEDEN)

**Neyi adlandırıyor.** `Y-6`'nın ikinci dalı, alakasız kolun tabana göre "mekanizma koşulu
kadar" iyileşip iyileşmediğini soruyor. Hangi mekanizma koşulu olduğunu ise söylemiyor.
`K-31`'in iddia cümlesi içeriği "sadece beceriler ile alakasız getirme arasındaki fark"
olarak yazıyor, ve `skills` faz 2'de.

**İlan, kullanıcının kararı.** Faz 1'de mekanizma koşulu `skills_failures`. İkinci dal
`skills_failures` – `irrelevant_retrieval` karşılaştırmasıyla okunuyor, 101 görevde
(kurulum protokolü §19.7). İlan ilk `dny` epizodundan önce, hiçbir sonuç görülmeden
(`K-188`).

**Gerekçe.** Alakasız kol, kartlı kolun, yani `skills_failures`'ın slotuna tür tür
eşleniyor (`K-179`, `K-181`). Faz 1'deki karşılaştırma bu yüzden yalnız alakada farklı iki
kolu karşılaştırıyor.

**`K-31`'in kontrastı silinmiyor.** `skills` – `irrelevant_retrieval`, faz 2'nin ikinci
okuması olarak kalıyor (101 görev). Bu ek o okumanın hüküm verip vermediğini belirlemiyor;
o, faz 2 başlamadan ayrıca ilan edilecek.

## A.8 Mekanizma başına terk kriteri

**Kural.** Kapsama yeterliyken ve indeks ilan edilen asgari boyuttayken sadece
hatalar koşulu etki göstermiyorsa, **hata indeksi mekanizma olarak terk edilir,
yeniden ayarlanmaz.** Aynısı beceri derleyicisi için.

**"Asgari boyut" getirilebilir kalıp sayısıdır, indeks satırı değil.** Ölçüldü:
indeksin en sık kalıbı (`GET api_docs.api_descriptions`, 150 hata) hiçbir görev
tarafından getirilemiyor, çünkü altyapı uygulamaları getiricide düşüyor (K-86,
S-48). 15 satırlık indeksin getirilebilir boyutu 14. Getirilemeyen satırlarla
dolu bir indeks yeterli görünür ve mekanizmayı haksız yere aklar.

Aynı kural kütüphaneye de uygulanıyor: kütüphane boyutu getirilebilir beceri
sayısı.

## A.9 Ayar bütçesi ve değişiklik türü taksonomisi

**Kural.** Kurulum verisini gördükten sonra kaç parametre revizyonuna izin
verildiği önceden yazılıyor. **Bütçe tükendikten sonra olumsuz sonuç parametreler
hakkında değil tasarım hakkında bir sonuçtur.**

**Tüketilen dört revizyon:**

| # | Revizyon | Ne değişti |
|---|---|---|
| 1 | Tavan çapası | Referans çözüm uzunluğundan doğrulayıcının beklediği çağrı sayısına, sonra `metadata.num_api_calls`'a (K-11, K-44) |
| 2 | Soğuk rejim | Isınmış rejim tekdüze olmadığı için epizot öncesi boşaltmaya geçildi (K-21) |
| 3 | Ön koşul eşiği | "Taban etkisinde mi" tanısından sansür/başarı temelli ölçüte (K-53, K-58) |
| 4 | Model ailesi | Qwen2.5-Coder ön koşulu geçemedi, aile yeniden seçiliyor (A-06, K-61) |

**Değişiklik türü taksonomisi.** Her değişiklik üç türden birine giriyor ve
yalnız birincisi bütçeden düşüyor:

| Tür | Bütçeden düşer mi | Örnek |
|---|---|---|
| **Ayar** — ölçümü değiştiren bir parametrenin değeri veriye bakılarak değişiyor | **Evet** | Tavan çapası, ön koşul eşiği |
| **Düzeltme** — ölçülen bir arıza gideriliyor, hedef değer değil doğruluk | Hayır | Durma kuralının kimlik tanımı (S-25), çıktı bütçesinin ortamdan alınması (S-30) |
| **Tesisat** — ölçülen hiçbir niceliği değiştirmiyor | Hayır | Kayıt vekilinin kurulması, CI'a kurulum eklenmesi |

Ayrım keyfi olmasın diye ölçütü tek: **değişiklik ölçülen bir sayıyı hedef alarak
mı yapıldı, yoksa bir arızayı gidermek için mi.** Bir düzeltmenin ölçülen sayıyı
değiştirmesi onu ayar yapmıyor; ayarı ayar yapan şey niyetin sayıya bakması.

**Bütçenin sayısı hâlâ yazılmadı ve bu bir boşluk.** Sayı konmadan "tükendi"
hükmü verilemez, yani kural işlemez. Bu belge o sayı konmadan donmuş sayılmıyor.

### Ek — 25 Eylül 2026: ayar bütçesi sıfır

**İlan.** Bütçenin sayısı **0**. Deney ilan edilen yapılandırmayla koşuyor; ilandan
sonra hiçbir parametre veriye bakılarak değişmiyor, ve ölçümü tanımlayan bir şeyin
değişmesi koşuyu durduruyor.

**Bu ekle ön kaydın donmamış tek alanı doluyor.** Bölüm A'nın girişi bu belgenin o
sayı konmadan donmuş sayılmadığını yazıyordu; sayı konduğu için Bölüm A bu tarihten
itibaren donmuş.

**Tüketilen dört revizyonla ilişkisi.** Yukarıdaki dört revizyon bu sayı yokken ve
hiçbir mekanizma sonucu görülmeden yapıldı; sıfır onları geriye dönük aşılmış bir
bütçe yapmıyor. Sıfır bu ekten sonrasını sayıyor: bütçe ilan anında tükenmiş sayılıyor.
Yukarıdaki kural da böylece hemen işliyor: deneyin olumsuz bir sonucu **parametreler
hakkında değil tasarım hakkında** bir sonuç.

**Neyi düşürdüğü.** Deney verisini gördükten sonra ayar yapma imkânını, bütünüyle.
Veriye bakılarak değiştirilemeyecek olanlar, bugünkü değerleriyle: değer eşiği
(`min_expected_saving` 1), koşul sayısı sınırı (yok), doğrulanmamış hata kartları
(açık), slotlar (5 beceri, 5 hata), tavan kuralı (`min(max(2 × çapa, 20), 150)`),
durma eşiği (40), çıktı bütçesi (4000), sıcaklık (0,2), madencilik eşikleri (boşluk
2, destek 3), ve teslim edilen kütüphane ile indeks. Taksonominin **ayar** sınıfı
kapanıyor. **Düzeltme** ve **tesisat** sınıfları kapanmıyor, ama ölçümü tanımlayan
bir yola dokunan bir düzeltme koşuyu durduruyor ve devamı yeni bir ilan istiyor.

**Bugün neyin zorladığı.** Üç mekanizma kurulu ve bu ek onlara dayanıyor:

- **Kirli ağaç kapısı** (`K-76`): ölçümü tanımlayan yollarda — `config/`, getirici,
  kart biçimi, koşucu, derleyici, indeks, kayıt şeması ve diğerleri — commit'lenmemiş
  bir değişiklik varken koşu başlamıyor.
- **Devam denetimi** (`S-31`, `K-76`): bir koşunun yazılmış künyesindeki commit ile şimdiki
  commit arasında ölçümü tanımlayan bir yol değiştiyse devam reddediliyor; bir koşul
  alanı farklıysa da.
- **İlan edilen koşul denetimi** (`K-136`): koşudan önce ilan edilen değerler ile
  koşunun kullanacağı değerler karşılaştırılıyor.

**Açık kalan.** Kirli ağaç kapısının bir kaçış bayrağı var (`--allow-dirty-tree`;
künye "dirty" diye yazıyor ama koşu başlıyor). Deneyin ilan edilen komutu bu bayrağı
taşımamalı; bunun denetimi deneyin koşul tablosuyla birlikte kurulacak.

## A.10 Bölme kullanımı ve dokunulan görevler

**Biriktirme** train, dev ve kullanılmayan normal test görevlerinden.
**Değerlendirme** normal testten, örneklem biriktirmede temsil edilen
uygulamalarla sınırlı.

**Zorluk bölmesi bütün ve dokunulmamış kalıyor**, biriktirme oradan yapılmıyor.
Elimizdeki tek gerçekten görülmemiş uygulama verisi o.

**Kurulumda dokunulan görevler değerlendirme örnekleminden çıkarılıyor**,
biriktirme havuzunda kalabilirler. Sayıları ölçüldü ve kimlikleri
`results/touched-tasks.json` içinde:

| Bölme | Dokunulan görev |
|---|---|
| train | 13 |
| dev | 0 |
| test_normal | **45** |
| test_challenge | **0** |

Zorluk bölmesinin sıfır olması tesadüf değil, kuralın kendisi.

### Ek — 25 Eylül 2026: liste kayıttan üretiliyor; dört görev çıktı, train doksana çıktı

**Yukarıdaki tablo değişmedi.** 28 Ağustos'ta ölçülen buydu. Kural da değişmedi:
kurulumda dokunulan görev değerlendirme örnekleminden çıkıyor. Değişen, listenin
nereden geldiği. Liste elle yazılmıştı ve kayıttan geride kalmıştı; artık kayıttan
üretiliyor ve okunduğu her yerde kayda karşı denetleniyor (`K-166`).

| Bölme | 28 Ağustos | 25 Eylül | Fark |
|---|---|---|---|
| train | 13 | **90** | `bir1` bölmenin tamamını süpürdü |
| dev | 0 | 0 | — |
| test_normal | 45 | **49** | `0a9d82a_1`, `0a9d82a_2`, `0a9d82a_3`, `0de03ea_1` |
| test_challenge | 0 | **0** | — |

**Dört görev neden geride kalmıştı.** Uçtan uca demo, üç kollu kart koşusu ve
karşılaştırılabilirlik koşusu bu dördünü koştu; `0de03ea_1`'i on iki epizotla, üç
koşulda, kartlı kol dahil. Liste bu koşulardan sonra yazıldı ama onları saymadı.
Dördü de değerlendirme örneklemindeydi, `0de03ea_1` eylem tabakasında.

**Değerlendirme örneklemi.** `test_normal`'dan kalan 123 → **119**. Tabakalara
dağılımı `results/task-types.json`'da; A.5'in ekine ayrı bir tarihli ek düşülüyor.

**`train`'in doksana çıkmasının sonucu.** Kural `train` için bir kısıt koymuyor —
dokunulan görev biriktirme havuzunda kalabilir — yani biriktirmeye etkisi yok.
Etkisi örneklem büyütme yolunun havuzunda: `scripts/setup/measure_sample_size.py`
genişleme havuzundan dokunulan görevleri her bölmede çıkarıyor, ve `train`'in payı
**65 → 0**. Havuz 623 → **557** eylem görevi: `test_normal` 104, `test_challenge`
408, `dev` 45. `K-149`'un (b) yolunun istediği 500 bu havuzda hâlâ var;
`test_normal` ile `test_challenge` birlikte 512.

**Zorluk bölmesi.** Sıfır. Kayıtta o bölmeden tek bir epizot bile olursa yükleyici
artık reddediyor.

### Ek — 25 Eylül 2026: deney sınırı `dny`

**Yukarıdaki kural değişmedi, sınırı yazıldı.** "Kurulumda dokunulan görev" —
K-166'nın ifadesiyle "deney öncesi her koşu" — bundan sonra "**`dny` dışındaki her
koşu**" demek. Deneyin koşuları `dny` önekini taşıyor (kurulum protokolü §19) ve
dokunma sayılmıyor; kural sınırı bilmeseydi deneyin ilk epizodu değerlendirme
örneklemini boşaltırdı.

**Sınırın bedeli iki şart.** `dny` epizotları listenin dışında kaldığı için onları
yükleyici ayrıca denetliyor: görev değerlendirme örnekleminde olmalı, ve koşu bir
ön kontrol olmamalı. Deneye ait ama ölçüm olmayan koşular `dnyk` önekiyle koşuyor
ve dokunma sayılıyor (`K-178`).

## A.11 Ölçek ekseni yorum tablosu

Dört olası şekil için yorum ölçümden önce yazılıyor. **Sonradan yorum yasak.**

| Şekil | Ne demek |
|---|---|
| **Düz** | Etki model boyutundan bağımsız; biriken deneyim boyutla ikame edilmiyor. İkinci soruya cevap "hayır, ortadan kalkmıyor". |
| **Düşen** | Etki boyut büyüdükçe azalıyor; mekanizma modelin kendi yeteneğiyle ikame ediliyor. İkinci soruya cevap "evet, kalkıyor" ve birincil hücrenin en büyük noktada seçilmiş olması bu yüzden en zor durum. |
| **Yükselen** | Etki boyut büyüdükçe artıyor; büyük model derlenmiş deneyimi daha iyi kullanıyor. Beklenmiyor ve çıkarsa açıklama gerektirir, çünkü küçük modelin daha çok yardıma ihtiyacı olduğu varsayımıyla çelişir. |
| **Ters U** | Ortada tepe; en küçük nokta mekanizmayı kullanamayacak kadar zayıf, en büyük nokta ihtiyaç duymayacak kadar güçlü. Üç noktayla ayırt edilmesi zor ve bu ölçekte **onaylayıcı sayılmıyor**. |

Üç nokta bir eğrinin şeklini belirlemeye yetmiyor; tablo yorum disiplinini
sağlıyor, istatistiksel bir iddia kurmuyor.

### Ek — 20 Ağustos 2026: eksene dördüncü nokta

**Yukarıdaki ilan değişmedi.** Bu bir ek; özgün metin olduğu gibi duruyor ve
tablo aynı tablo.

**Ne eklendi.** Ölçek eksenine dördüncü nokta girdi:
`qwen2.5-coder:14b-instruct-q4_K_M`. Karar K-133'te, gerekçesiyle.

**Neden eklendi.** Bant taraması eksenin üç noktasının **birden** taban
etkisine yapıştığını ölçtü: 1.5B, 3B ve 7B, üçünde de ikili başarı sıfır.
S-14 bu durumu pilottan önce öngörmüş ve kuralı yazmıştı — en küçük nokta
tabana yapışırsa eksen yukarı kaydırılır — ama aynı kayıt telafinin neden
yapılamayacağını da yazıyordu: *"14B 8 GB'a sığmadığı için yukarı doğru telafi
yok."* Engel donanımdı, tasarım değil. Colab'ın GPU'su o engeli kaldırdı.

**Bu nokta KEŞİFSEL, ve bunun sebebi tek cümle.** Nokta **sıfırlar görüldükten
sonra** seçildi, yani veri güdümlü. Ne kadar iyi çıkarsa çıksın onaylayıcı
sayılmıyor. Yukarıdaki dört şekil tablosu dört noktayla da onaylayıcı olarak
ayrılamıyor; disiplini sağlıyor, iddiayı kurmuyor.

**Değişmeyen kilit: aile.** Dört nokta da `qwen2.5-coder`, dördü de `q4_K_M`.
Eksenin ölçtüğü şey boyut; aile ya da kuantalama değişseydi eksen iki değişkeni
birden taşırdı. Bu kilit açılmadı.

**Ortam farkı, ve ondan doğan şart.** 14B yerel makinede koşamıyor, yani bu
nokta başka bir GPU'da ölçülecek. Sunucunun istenen yapılandırmayı gerçekten
koşturup koşturmadığı koşudan önce ölçülüyor (kurulum protokolü §15.3). İstenen
ile etkin tutmazsa koşu yine yapılıyor ama sonuç **"yerelle karşılaştırılamaz"**
diye etiketleniyor.

**Düzeltme — 25 Eylül 2026: `S-14` yukarı uzatmaya izin vermemişti.** Yukarıdaki
"`S-14` bu durumu pilottan önce öngörmüş ve kuralı yazmıştı — en küçük nokta
tabana yapışırsa eksen yukarı kaydırılır" aktarımı aşırıydı ve silinmiyor.
`S-14`'ün kuralı **aşağı** daralmaydı (eksen 3B ve 7B'ye iner); yukarı yol aynı
kayıtta donanım yüzünden açıkça kapalıydı. Colab o engeli kaldırdı, ama uzatma
`S-14` tarafından önceden yetkilendirilmiş değil: sonradan, kullanıcının açık
onayıyla alınmış bir karar (`K-133`'ün 25 Eylül ekleri). Bu, noktanın keşifsel
etiketini değiştirmiyor, güçlendiriyor: seçim yalnız sıfırlardan sonra değil,
önceden yazılmış bir kural olmadan da yapıldı.

### Ek — 25 Ağustos 2026: eksene beşinci nokta

**Tarih düzeltmesi, 26 Ağustos 2026.** Bu ek ilk yazıldığında **21 Ağustos
2026** diye tarihlendi ve o tarih kayıtta yok. Eki depoya getiren commit
`e2e40dd`, tarihi 25 Ağustos 2026 14:06 UTC; ilan ettiği koşu `b32c`, künyesindeki
ilk epizot 25 Ağustos 2026 18:55 UTC. Yani ilan koşudan **dört saat kırk dokuz
dakika** önce yapıldı, dört gün önce değil. "Koşudan önce ilan edildi" iddiası
ayakta duruyor ama payı bu kadar, ve yanlış tarih onu olduğundan geniş
gösteriyordu. Sessizce düzeltilmedi: bir ön kaydın değeri tarihlerinin `git log`
ile doğrulanabilir olmasında, ve doğrulanabilirlik yanlışın da yazılmasını
gerektiriyor.

**Yukarıdaki ilan ve bir önceki ek değişmedi.** Bu ikinci bir ek.

**Ne eklendi.** `qwen2.5-coder:32b-instruct-q4_K_M`, eksenin beşinci noktası.
Karar K-137'de, şartları kurulum protokolü §16'da, koşudan önce.

**Neden eklendi.** 14B Colab'ın L4'ünde 3/30 verdi, yani bant sıfırdan çıktı.
Bir üst nokta, bandın büyüklükle nasıl davrandığını gösterebilecek tek şey. Yeni
bir kilit açılmıyor: yerel donanım kilidi 14B ile zaten açılmıştı.

**Bu nokta da KEŞİFSEL.** Sıfırlar görüldükten sonra seçildi. Beş nokta da bir
eğrinin şeklini onaylayıcı olarak belirlemeye yetmiyor; yukarıdaki dört şekil
tablosu disiplini sağlıyor, iddiayı kurmuyor.

**Değişmeyen kilit: aile.** Beş nokta da `qwen2.5-coder`, beşi de `q4_K_M`.

**Önceden ilan edilen yorum protokol §16.5'te**, üç dalıyla: sıfırdan büyük,
sıfır, ve hiçbirine uymayan. Sıfır çıkması **daha ilginç** sayılıyor ve bu
şimdiden yazılı, sonuç görüldükten sonra değil.

**Ortam farkı.** Bu nokta A100'de (Ampere 8.0) ölçülecek; eksenin diğer noktaları
Ada 8.9 kartlarda ölçüldü. İstenen yapılandırmanın gerçekten koştuğu koşudan
önce okunuyor; tutmazsa sonuç "yerelle karşılaştırılamaz" diye etiketlenir.

## A.12 Dış inceleme

Dış inceleme kaydı `docs/10-external-review.tr.md` içinde. **Dosya henüz
konmadı**; içerik proje sahibinde ve bu bölüm dosya geldiğinde ona atıf verecek
biçimde bırakıldı.

---

# Bölüm B — Kurulum fazının madde kayıtları

Aşağıdakiler mekanizma yol haritasının maddeleri koşmadan önce yazıldı; her
birinin altında sonradan gelen sonuç ayrı başlıkta duruyor.

## Madde 3 — Derleyici v0 ve `skills` tablosu

**Yazıldığı an:** derleyici henüz yazılmadı, hiçbir beceri üretilmedi.

### Korpusun ölçülmüş sınırları

Beceriler yalnız başarılı epizotlardan madencileniyor
(`docs/06-skill-language.tr.md`). Seri 2'de:

| | |
|---|---|
| Toplam epizot | 105 |
| **Geçen epizot** | **22** |
| **Geçen epizotların farklı görev sayısı** | **20** |
| İki kez geçen görev | `024c982_1`, `024c982_3` |

Destek farklı görev üzerinden sayıldığı için **görev desteğinin tavanı 20**.
Örüntülerin çoğunun tek görevde kalması bekleniyor; bu korpusun küçüklüğünün
doğrudan sonucu, bir arıza değil.

### Beklenti 1: giriş ailesi uygulama başına parçalanacak

Kimlik doğrulama dizisi — supervisor'dan parola, `auth/token`, jetonla çağrı —
22 geçen epizodun **22'sinde** var (16'sında bir, 5'inde iki, 1'inde üç
`auth/token` çağrısı).

Ama tek bir yüksek destekli aile olarak çıkmayacak, çünkü
`POST spotify.auth/token` ile `POST venmo.auth/token` **farklı çağrılar**, aynı
çağrının farklı argümanı değil. Uygulama adı çağrı kimliğinin parçası, argüman
değil. Ölçülmüş parçalanma:

| Uygulama | Destek (farklı görev) |
|---|---|
| venmo | 7 |
| spotify | 6 |
| phone | 5 |
| simple_note | 5 |
| file_system | 1 |
| todoist | 1 |
| **herhangi bir auth (birleşim)** | **20** |

Yani "her görevde var" doğru, ama derleyicinin göreceği en yüksek giriş desteği
**7**, 20 değil.

### Beklenti 2: en yüksek destekli örüntü giriş değil, belge okuma olacak

Destek-20 taşıyan üç tekil çağrı var ve üçü de keşif:
`GET api_docs.api_descriptions`, `GET supervisor.account_passwords`,
`GET api_docs.api_doc`. Uzunluk alt sınırı iki olduğu için tekil çağrılar
beceri olmuyor, ama bitişik çiftlerde de aynı desen sürüyor:

| Destek | Çift |
|---|---|
| 12 | `api_descriptions -> account_passwords` |
| 10 | `api_descriptions -> api_doc` |
| 10 | `api_doc -> account_passwords` |
| 6 | `account_passwords -> spotify.auth/token` |

Bu sayılar **bitişik** çiftlerden; madencilik boşluk kısıtıyla çalışıyor,
dolayısıyla gerçek destekler bu sayıların **alt sınırı**.

**İlan edilen risk.** Derleyicinin bulacağı en yüksek destekli örüntü, iskelenin
kendi keşif davranışı olabilir — görev yetkinliği değil.

**Karar verildi, sonuç görülmeden: salt okuma örüntüleri kütüphaneye girmiyor
(K-75).** Etki soneki boş olan örüntüler madencileniyor ama ayrı bir sınıf
olarak — *keşif öneki* — ayrı raporlanıyor, birincil kütüphaneye girmiyor,
getiriciye verilmiyor. Gerekçesi `SKILL_SPEC.md` içinde; asıl olan üçüncüsü:
alakasız getirme kontrolü evrensel boilerplate'i **ayıramıyor**, çünkü
uygulama-bağımsız bir boilerplate'in alakasız sürümü yok. Kütüphaneye alınırsa
ölçülen kazancın bir kısmı hiçbir kontrolle ayrılamaz.

Bulgu kaybolmuyor: keşif öneki kendi başına raporlanacak. Boilerplate
önbelleklemesi bir kazanç olarak iddia edilecekse ayrı ve açıkça etiketli olur.

**Bu, aşağıdaki üç yorumun sayımını değiştiriyor.** "Eşikleri geçen beceri
sayısı" yalnız `kind == "skill"` kayıtlarını sayıyor. Keşif önekleri o sayının
dışında ve ayrı bir satırda raporlanıyor.

### Beklenti 3: en değerli beceri mekanik kimlik doğrulama olacak

Bu korpusta derlenmeye değer en anlamlı beceri, zayıf modellerin tam olarak
beceremediği mekanik kimlik doğrulama dizisi. Anlatı olarak da tutarlı: dizi her
görevde gerekli, tamamen mekanik, ve hata payı yüksek.

Parçalanma bunu zayıflatmıyor, biçimini değiştiriyor: bir "giriş" becerisi değil,
uygulama başına giriş becerileri.

### Üç sonucun yorumu

Sonuç görülmeden yazılıyor.

1. **Üç ya da daha çok beceri eşikleri geçerse** → ilerle ve raporla.

2. **Yalnız giriş ailesi geçerse** → bu, korpus çeşitliliği hakkında bir
   bulgudur, mekanizma hakkında değil. Beceri sayısı neyse odur ve öyle
   raporlanır.

3. **Hiçbiri geçmezse** → eşikler 20 görevlik bir korpus için yüksek demektir.
   Dürüst hamle **eşik duyarlılığını raporlamak**: eşik değiştikçe beceri
   sayısının nasıl değiştiğini göstermek. Sayı tutturmak için eşiği düşürmek
   değil.

### İki sınır, şimdiden yazılı

**"Üç ile beş gerçek beceri" bir hedef, taahhüt değil.** Eşiği o sayıya ulaşmak
için düşürmek, vekili doğrulayıcısına uydurmanın aynısı olurdu — K-70'te
yapılmayan şey tam olarak buydu ve %75,5'i anlamlı kılan da odur.

**Korpusu büyütmek bir karar, otomatik sonraki adım değil.** Önce 20 görevle
koşulacak, sonuç getirilecek, sonra bakılacak.

---

## Madde 3 — sonuç

*Aşağıdaki bölüm derleyici koştuktan sonra yazıldı. Yukarıdaki hiçbir satıra
dokunulmadı.*

**Gerçekleşen: ikinci yorum.** Öncü yapılandırmada (boşluk 2, destek 3, koşudan
önce seçilmişti) birleşme sonrası **4 beceri** çıktı ve **dördü de giriş
ailesinden**:

| Destek | Etki soneki | Kaç örüntüden birleşti |
|---|---|---|
| 8 | `POST venmo.auth/token` | 19 |
| 7 | `POST spotify.auth/token` | 7 |
| 5 | `POST simple_note.auth/token` | 4 |
| 5 | `POST phone.auth/token` | 8 |

Bu, korpus çeşitliliği hakkında bir bulgu, mekanizma hakkında değil. Beceri
sayısı neyse odur ve eşik düşürülmedi.

**Beklenti 1 doğrulandı.** Giriş ailesi gerçekten uygulama başına parçalandı ve
en yüksek destek 8 çıktı, 20 değil.

**Beklenti 2 doğrulandı ve karara bağlandı.** En yüksek destekli örüntü gerçekten
iskelenin keşif davranışıydı; K-75 onu keşif öneki sınıfına ayırdı, K-80 ise
iskelenin tamamlama çağrısını beceri gövdesinden çıkardı.

**Beklenti 3 biçim değiştirerek doğrulandı.** En değerli beceri sınıfı mekanik
kimlik doğrulama oldu, ama bir "giriş becerisi" olarak değil, uygulama başına
dört ayrı beceri olarak.

**Eşik duyarlılığı (birleşme sonrası beceri sayısı).**

| Boşluk \ Destek | 2 | 3 | 4 | 5 | 6 | 8 | 10 |
|---|---|---|---|---|---|---|---|
| 0 | 8* | 4 | 4 | 3 | 2 | 0 | 0 |
| 2 | 11* | **4** | 4 | 4 | 2 | 1 | 0 |
| 5 | 35* | 7 | 4 | 4 | 2 | 1 | 0 |

`*` aramanın sınıra dayandığı ve sonucun eksik olduğu hücreler.

Sayı destek 3–5 aralığında ve boşluk 0–5 aralığında **4'te sabit**. Bu
istikrar, sayının bir eşik seçiminin artefaktı olmadığını gösteriyor.

**Tek istisna: boşluk 5 / destek 3'te üç ortam eylemi becerisi hayatta kalıyor**,
üçü de `venmo.payment_requests` içeriyor ve destekleri 3. Daha geniş bir boşluk
`payment_requests` çağrısını daha uzaktaki bir çağrıyla eşleştirmeye izin
verdiği için asgari uzunluk şartı sağlanıyor. Üçünün etki sonekleri farklı
(`payment_requests` tek başına, `phone.auth + payment_requests`,
`venmo.auth + payment_requests`), dolayısıyla birleşmiyorlar; tasarımın kendi
notu bunu öngörüyor: aynı hedefe farklı etkiyle varan diziler v1'de ayrı kalıyor.

**Son koşullar.** Dördü de ölçülebilir, dördü de boş. Sebebi ölçüldü ve olgu:
`auth/token` 213 tek çağrılı adımda sıfır durum farkı üretiyor. Giriş jeton
üretiyor, satır üretmiyor (S-41).

### Dördün kaçı kimlik doğrulamanın zor kısmını çözüyor: **ikisi**

Bir giriş becerisi, kimlik okumasını gövdesinde taşıyorsa parolayı kendisi
getiriyor. Taşımıyorsa çağıranın parolayı zaten bilmesi gerekiyor ve beceri
yalnız bir model çağrısı kazandırıyor.

| Beceri | Destek | Kimlik okuması gövdede | `password` |
|---|---|---|---|
| `venmo.auth/token` | 8 | **hayır** | serbest parametre |
| `spotify.auth/token` | 7 | evet | bağlı |
| `simple_note.auth/token` | 5 | evet | bağlı |
| `phone.auth/token` | 5 | **hayır** | serbest parametre |

**En yüksek destekli beceri en zayıfı.** Pilot iddiası bu ayrımla kurulacak:
"dört giriş becerisi" değil, "ikisi kimlik bilgisini kendi getiren dört giriş
becerisi".

### Değer eşiği uygulanmamıştı, duyarlılığı ölçüldü

Şartnameye göre asıl filtre beklenen tasarruf: `(uzunluk − 1) × görev desteği ×
başarı oranı`. Değeri hiç seçilmedi (K-50) ve derleyici bugüne kadar yalnız
destek ve asgari uzunluk üzerinden filtreliyordu. **Yani yukarıdaki dört sayısı
değer filtresi öncesi.**

Başarı oranı v0'da yapı gereği 1: beceriler yalnız geçen epizotlardan
madencileniyor. Çarpan, becerilerin çağrılma sicili biriktikten sonra anlam
kazanacak.

**Formülün payı ölçüldü ve bir uçta abartıyor.** Model çağrısı adım demek, API
çağrısı değil; iskele bir adımda birkaç çağrı yapabiliyor.

| Beceri | Çağrı | Adım (medyan) | `(L−1)×d` | `(adım−1)×d` |
|---|---|---|---|---|
| venmo | 2 | 2 | 8 | 8 |
| **spotify** | **3** | **2** | **14** | **7** |
| simple_note | 7 | 7 | 30 | 30 |
| phone | 5 | 5 | 20 | 20 |

Dörtte üçünde aynı; spotify becerisinde formül tasarrufu iki katına çıkarıyor,
çünkü o üç çağrı iki adımda yapılmış.

**Duyarlılık ızgarası, boşluk 2. Satır değer eşiği, sütun destek eşiği.**

Şartnamenin formülüyle:

| eşik | d≥3 | d≥4 | d≥5 | d≥6 |
|---|---|---|---|---|
| 0–8 | **4** | 4 | 4 | 2 |
| 10–14 | 3 | 3 | 3 | 1 |
| 16–20 | 2 | 2 | 2 | 0 |
| 25–30 | 1 | 1 | 1 | 0 |
| 40 | 0 | 0 | 0 | 0 |

Adım tabanlı tasarrufla:

| eşik | d≥3 | d≥4 | d≥5 | d≥6 |
|---|---|---|---|---|
| 0–4 | **4** | 4 | 4 | 2 |
| 8 | 3 | 3 | 3 | 1 |
| 10–20 | 2 | 2 | 2 | 0 |
| 25–30 | 1 | 1 | 1 | 0 |

**Dört sayısı yalnız eşik ≤ 8 (formül) ya da ≤ 4 (adım tabanlı) için geçerli.**
Destek eşiğinin aksine değer eşiği sayıyı hızla düşürüyor, yani bu parametre
sonucun asıl belirleyicisi.

**İlk düşen, kimlik okumasını taşımayan `venmo` becerisi.** İki bağımsız ölçüt —
kendi kimlik bilgisini getirme ve beklenen tasarruf — en yüksek destekli
beceride aynı yöne bakıyor.

**Eşik seçilmedi.** Sonuca bakarak seçmemek için, ve tabloya yazılırken
filtrelenmiyor: beklenen tasarruf bir sütun olarak saklanıyor ve eşik okuma
anında uygulanıyor. Böylece seçilmemiş bir sayı kayda gömülmüyor.

---

## Madde 6 — Kart jeton bütçesi

**Yazıldığı an:** kart biçimi yazılmadan önce. Bütçeler ve geçme kuralı ölçümden
önce verildi ve olduğu gibi alındı.

**Bütçe.** Beceri kartı yedi alan ve ≤180 jeton, hata kartı beş alan ve ≤120
jeton.

**Geçme kuralı, sonucu görmeden.** Taşan kart varsa **biçim yanlış demektir**,
bütçe değil, ve düzeltmesi bu maddenin içinde. Kural bir yorum serbestliği
bırakmıyor: bütçeyi yükseltmek bir seçenek olarak yazılmadı.

**Ölçümün nasıl yapılacağı da önceden.** Modelin kendi tokenizer'ıyla ve gerçek
kartlara karşı. Bayt sayısından türetilmiş bir kestirim geçerli sayılmıyor,
çünkü sınanan şey bir jeton bütçesi.

## Madde 6 — sonuç

**Ölçüldü** (`results/card-tokens.json`; veri setinde `card_tokens`):

| Kart | Sayı | Jeton | Bütçe | Aşan |
|---|---|---|---|---|
| Beceri | 4 | 78–122, medyan 88 | ≤180 | **0** |
| Hata | 14 | 36–48, medyan 42 | ≤120 | **0** |

Alan sayısı beceride 7, hatada 5; hepsinde. Biçim düzeltmesi gerekmedi.

**Bütçenin bolluğu da bir bulgu.** En büyük beceri kartı bütçesinin %68'ini
kullanıyor ve o kart yedi çağrılık gövdesiyle kütüphanenin en uzunu. Bütçe bu
kütüphane için bağlayıcı değil; bağlayıcı hâle gelmesi ya çok daha uzun gövdeler
ya da alan başına düzyazı gerektirirdi. İkincisi kasten yok — renderer öğüt
yazmıyor (K-87).

**Ölçekle ilgili tek soru kapandı.** Ölçek ekseninin üç modeli her kart için aynı
jeton sayısını veriyor, yani "180 jeton" tek bir sayıyı adlandırıyor ve bütçe
modele göre yeniden yazılmak zorunda değil.

---

## Madde 7 — Uçtan uca demo: ayrıştırma ile kullanma ayrı ölçülüyor

**Yazıldığı an:** demo koşulmadan önce, hiçbir kartlı epizot yokken.

**İki ölçüm, ve ayrı olmalarının sebebi.** Model kartı ayrıştırabilir ve yine de
yok sayabilir. Kartın bağlama girdiğini göstermek, kullanıldığını göstermiyor;
tek bir "demo çalıştı" cümlesi ikisini birbirine karıştırırdı.

| Ölçüm | Nasıl | Modele bakıyor mu |
|---|---|---|
| **Giriş** | Blok prompt dosyasının içinde bayt bayına; iki prompt yalnız blok kadar farklı; künye özetleri farklı | Hayır, mekanik |
| **Kullanım** | Karttaki dizi çağrı dizisinde geçiyor mu, ve kartsız koşuda ne oluyor | Evet |

**Eşleştirilmiş taban zorunlu, ve gerekçesi ölçümün geçerliliği.** Eşleşen bir
dizi tek başına hiçbir şey söylemiyor: kütüphanedeki dört becerinin dördü de
giriş, ve model giriş çağrılarını kartsız da yapardı. Bu yüzden her görev iki kez
koşuyor — kartlı ve kartsız, aynı seed, aynı model, aynı soğuk rejim — ve
karşılaştırma epizot çiftleri üzerinden.

**Eşleşme kısıtı kartın üretildiği kısıtın aynısı:** boşluk 2 (K-81). Daha gevşek
bir arama kartla ilgisi olmayan bir diziyi de eşleşme sayardı.

**Dört sonucun yorumu, sonuç görülmeden:**

1. **Blok girmediyse** mekanizma bozuk ve kullanım sorusu anlamsız. Betik bu
   durumda sıfırdan farklı çıkıyor; ölçüm değil, arıza.
2. **Girdi ve yörüngeler birebir aynıysa** kart yok sayıldı. Bu bir başarısızlık
   değil, bir **sonuç**: kartın içeriği bu modelde davranışı değiştirmiyor, ve
   pilotun mekanizma koşullarının bu modelde taban koşulundan ayrışmayacağını
   önceden söyler.
3. **Girdi, yörünge değişti ve gövde eşleşti** ise kart kullanıldı. Kazanç iddiası
   yine yok — demo üç görev ve başarı ölçmüyor — ama mekanizmanın davranışa
   ulaştığı gösterilmiş olur.
4. **Girdi, yörünge değişti ama gövde eşleşmedi** ise kart davranışı başka bir
   yoldan değiştirdi. Bu en dikkatli okunması gereken hâl: bağlama fazladan metin
   koymak da yörüngeyi değiştirir, ve o fark mekanizmanın değil hacmin sonucu
   olabilir. Ayrımı yalnız `irrelevant_retrieval` koşulu verebilir (K-29, S-19) ve
   o koşul demoda koşmuyor.

**Demo bir pilot değil ve olmayacak.** Ön koşul kapısı ateşledi, taban sıfır
çözüyor, birincil metrik tanımsız. Üç görev seçiliyor ve seçim ölçütleri koşudan
önce yazılı: kütüphanenin madencilendiği görevlerden olmayacak, en az bir beceri
kartı alacak, tek uygulama adlandıracak. Sıra görev kimliğine göre.

### Seçim ölçütüne dördüncü madde eklendi: farklı senaryo

**Kusur, koşu sırasında bulundu ve kaydı burada.** Yukarıdaki üç ölçüt kimliğe
göre sıralandığında ilk üç eşleşme `0a9d82a_1`, `0a9d82a_2`, `0a9d82a_3` çıktı —
aynı senaryonun üç varyantı, aynı uygulama (`simple_note`), aynı kart. "Üç görev"
diye yazılan şey tek bir kartın üç kez sınanmasıydı, ve başka kartların davranışı
hakkında hiçbir şey söylemezdi.

**Düzeltme:** her görev farklı senaryodan. AppWorld kimliği `senaryo_varyant`
biçiminde, yani ayrım mekanik ve seçim hâlâ deterministik.

**Koşmuş epizotlar silinmedi.** İlk iki varyantın dört epizodu kayıtta duruyor ve
raporda **senaryo içi tekrar** olarak ayrı etiketli: aynı kart, aynı uygulama,
farklı varyant. Bu bir bonus gözlem, düzeltilmiş demonun parçası değil.

**Bu bir sonucu görüp ölçütü değiştirmek değil.** Ölçüt sonuç sayısına bakılarak
değişmedi; değişme sebebi seçimin niyetini karşılamaması, ve niyet ("üç görev")
ölçütten önce yazılıydı. Ayrım önemli, o yüzden ikisi de burada duruyor.

### Beşinci yorum eklendi: soru sorulamayan hâl

**Dört yorum bir hâli öngörmüyordu ve o hâl gerçekleşti.** `0a9d82a_1`'de iki kol
da **hiç çağrı üretmedi**: yirmi adımın yirmisi yürütme hatası. İkinci yorum
("yörüngeler birebir aynıysa kart yok sayıldı") bu duruma uyar görünüyor, çünkü
iki boş dizi eşit. Ama uymuyor.

**İki boş dizinin eşitliği bir kimlik iddiası değil.** Model hiç eylem
üretmediyse kartın davranışı değiştirip değiştirmediği sorulamıyor; "değiştirmedi"
demek, ölçülmemiş bir şey hakkında olumlu bir iddia olur. Ayrım K-79'un
ayrımının aynısı: *ölçüldü, değişim yok* ile *ölçülemedi* ayrı şeyler ve
karıştırılmaları bir kez düzeltildi.

**Beşinci yorum:** iki kol da eylem üretmediyse kullanım sorusu o görevde
**sorulamaz**, ve görev "yok sayıldı" sayılmaz. Veri dosyasında `answerable`
alanı bunu taşıyor; özet ikisini ayrı sayıyor.

Yerel 7B'nin hiç çağrı üretmemesi beklenmedik de değil: kayıtlı 59 7B epizodunun
14'ünde (%24) sıfır çağrı var. Yorumun eksikliği, olgunun sürprizi değil.

**Beceri yürütücüsü yok, yani atomiklik sınanmıyor.** Kart çağrı dizisini
yazıyor, model o diziyi kendisi yapıyor. `06-skill-language.tr.md`'nin atomik
yürütmesi, kırılan becerinin yapılandırılmış dönüşü ve üç kapılı suç atfı bu
demoda yok; sınanan şey kartın **içeriğinin** davranışa ulaşıp ulaşmadığı.
