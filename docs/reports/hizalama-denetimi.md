# Hizalama denetimi — tasarım zemini ile deponun karşılaştırması

Bu rapor kodun ne yaptığını değil, neyin yazılı olmadığını anlatıyor.

Soru: bu araştırma hangi noktaya kadar yazılı zeminin dışında ilerletildi, ne
kadarı koda girdi, sonuç ne kadar dağıldı.

Karşılaştırma zemini, bütün tasarım kararlarını ve gerekçelerini içeren tam
bağlam belgesi. Depo tarafı `main` dalının 12 Ağustos 2026 hâli, on beş
birleştirilmiş PR.

## 1. Asıl bulgu: uyulacak yazılı zemin yoktu

Tasarım katmanının tamamı boş.

| Dosya | Satır | İçerik |
|---|---|---|
| `docs/01-problem-definition.tr.md` | 3 | başlık + "sonraki görevde yazılacak" |
| `docs/02-research-question.tr.md` | 3 | aynı |
| `docs/03-architecture.tr.md` | 3 | aynı |
| `docs/04-threat-model.tr.md` | 3 | aynı |
| `docs/05-experiment-design.tr.md` | 3 | aynı |
| `docs/06-skill-language.tr.md` | 3 | aynı |
| `docs/07-failure-taxonomy.tr.md` | 3 | aynı |
| `experiments/preregistration.md` | 3 | aynı |
| `experiments/decisions.csv` | 1 | yalnız başlık satırı |
| `experiments/experiment-matrix.csv` | 1 | yalnız başlık satırı |
| `docs/11-falsification.tr.md` | 27 | biçim tanımlı, "Kayıtlar: henüz yok" |
| `docs/10-external-review.tr.md` | 22 | biçim tanımlı, "Kayıtlar: henüz yok" |

Buna karşılık dolu olanlar: `docs/08-decisions.tr.md` 1324 satır ve 61 karar,
`docs/09-limitations.tr.md` 550 satır ve 24 sınır.

**Bunun anlamı.** On beş PR, altı kapanmış kurulum aşaması ve kırk beş
epizotluk ölçüm, problem tanımı, araştırma sorusu, mimari, deney tasarımı ve ön
kayıt yazılmadan birleştirildi. Tasarım kullanıcının kafasında ve konuşmada
duruyordu; depoda yalnız karar kaydı vardı.

Karar kaydı bunun yerini tutmuyor. Karar kaydı "neden şunu seçtik" tutar,
"tasarım nedir" tutmaz. K-31 iki kritik kontrastın hangileri olduğunu söylüyor
ama altı koşulun tanımı hiçbir yerde yazılı değil. K-53 sansürün nasıl
sayıldığını söylüyor ama birincil metriğin ne olduğu hiçbir yerde yazılı değil.

**Dolayısıyla "kurallara uymadan ilerledik" ifadesi eksik.** Uyulacak yazılı
kural büyük ölçüde yoktu. Ölçümler doğru yapıldı ama hangi tasarıma karşı
yorumlanacakları yazılı değildi, ve o boşluk aşağıdaki sapmaların hepsinin
ortak sebebi.

## 2. Zeminde olup depoda karşılığı olmayanlar

Tam bağlam belgesinin bölümleri, deponun karşılığıyla:

| Zemin | Depoda |
|---|---|
| §1 problem ve iki araştırma sorusu | **yok** |
| §2 üç hata sınıfı ve sonradan eklenen dördüncüsü | **yok** — tasarımın bütün gerekçesi |
| §3 yedi bileşen | dağınık: kayıt K-13..K-17, kalkan yüklemi K-41, sandbox K-01 gerekçesinde |
| §3 getiricinin sembolik olması ve gömme reddi | **yok** |
| §3 kayıt/projeksiyon ayrımı ve silme testi | kısmen K-15 |
| §4 altı koşulun tanımı | **yok**; yalnız yapılandırma dosyaları var |
| §4 naif derleyicinin tam tanımı | **yok** |
| §4 kart sayısının göreve göre belirlenmesi | kısmen K-29 |
| §5 ana eksen şartları | K-61 (bu turda yazıldı, henüz işlenmedi) |
| §5 aile kontrolünün bandı ve tek nokta olması | **yok** — K-61 bu ayrıntıyı taşımıyor |
| §6 birincil metrik ve totoloji itirazının cevabı | **yok** |
| §6 zorunlu tanı metriği ve yorumu | **yok** |
| §6 on beş ikincil metrik | **yok** |
| §6 "iki metrik birlikte hareket etmeli" kuralının düşmesi | **yok** |
| §7 kısıtlanmış ortalama, bootstrap, Wilcoxon | **yok** |
| §7 tavanın 1,5 ve 2 katıyla duyarlılık | **yok** |
| §7 toplanabilirlik varsayımı ve kurulumda sınanması | **yok** |
| §7 birincil karşılaştırmanın tek hücresi | **yok** |
| §7 ezberleme kapısı ve yarım eşiği | **yok** |
| §7 bölme kullanımı | K-42 |
| §8 üç yanlışlama kapısı | dosya var, kayıt yok |
| §8 mekanizma başına terk kriteri | **yok** |
| §8 ayar bütçesi | kısmen K-50 |
| §8 ölçek ekseninin dört şekli için yorum tablosu | **yok** |
| §9 beceri derleyicisinin tamamı | **yok** |
| §10 hata indeksinin tamamı | yalnız adım düzeyi, K-36 |
| §11 bağlam montajcısı | yalnız riski, K-26 ve S-07 |

## 3. Koda ve ölçüme giren sapmalar

### 3.1 Sabit adım tavanı, K-43 varken

K-43 tavanı görev başına `k × num_api_calls` diye bağlıyor. Sansür ölçümü
(PR #12) on beş epizodun on beşinde de sabit 20 kullandı; o beş görevin çapaları
10, 29, 71, 145 ve 195. S-22'ye yazıldı ama **sayılar o hâliyle rapor edildi.**

### 3.2 Zeminde olmayan bir metrik başlığa çıktı

`zihin.verification.graded_detail` — `no_op_fail` etiketli testlerin geçilen
oranı. §6'nın metrik listesinde yok. Kullanıcının "kısmi tamamlama dereceli mi"
sorusuna cevap olarak türetildi, sonra PR #13, #14 ve #15 raporlarında ana
raporlama niceliği oldu.

### 3.3 Birincil metrik ölçülmedi — sapma değil, kapının sonucu

§6: birincil metrik görev başına model çağrısı. PR #11'den #15'e kadar hiçbir
rapor onu vermiyor.

**Bu bir sapma değil.** Ön koşul kapısı ateşlediği için birincil metrik tanımsız:
hiçbir görev çözülmediğinde "çözüm için gereken model çağrısı" diye bir sayı
yok. Ölçülemedi, atlanmadı. Buraya sapma listesinde değil, kapının sonucu olarak
yazılıyor.

### 3.3a Ayar bütçesinin sayısı hiç belirlenmedi

§8 ayar bütçesini kural olarak koyuyor: kurulum verisini gördükten sonra kaç
parametre revizyonuna izin verildiği önceden yazılacak. **Sayı hiç yazılmadı**,
oysa alınan kararlar onu tüketiyor.

Bugüne kadar tüketilen dört revizyon: tavan çapası, soğuk rejim, ön koşul
eşiği, model ailesi.

### 3.3b Kurulum promptundaki Aşama 3 kabul ölçütü güncellenmedi

Ölçüt karar kaydında düzeltildi ama promptta eski hâliyle duruyor. İki kaynak
ayrıştı ve prompt okunarak iş yapılırsa yanlış ölçüt uygulanır.

### 3.3c İskele kesme mantığı ile montajcının çakışması planda yok

Referans iskelenin kendi bağlam kesme mantığı bizim montajcımızla çakışacak.
S-07 ve K-26 riski kaydediyor, ama hiçbir aşama planında bu çakışmanın ne zaman
ve nasıl çözüleceği yazılı değil.

### 3.4 Sınır kontrolü künye sözleşmesini atlıyor

§13 künye alanlarının zorunlu-dolu sözleşmesini kural olarak koyuyor.
`measure_boundary_control.py` künyeye hiç yazmıyor, kendi JSON'una yazıyor.
Gerekçesi yazılı ve o anda bildirildi, ama bu benim kararımdı ve §5 sınır
kontrolünü tasarımın parçası sayıyor.

### 3.5 Değerlendirme bölmesine bakıldı

`measure_gpt4o_subset.py` görevleri "güçlü bir modelin çözdüğü" ölçütüyle
seçiyor. Bu, `test_normal` üzerinde bir kapsam kısıtı ve §7 değerlendirmeyi
oradan çekiyor. Toplam kırk beş epizot `test_normal` görevlerinde koşuldu ve
gpt-4o'nun görev başına sonuçları incelendi. Eğitim yok, dolayısıyla sızıntı
yok; ama görülen sonuçtan türetilen herhangi bir kapsam kısıtı, mekanizmalar
koşmadan dondurulmazsa kiraz toplama olur.

### 3.6 Yapılandırma çoğalması

Betiklerde yirmi ortam değişkeni: `ZIHIN_COUNT`, `ZIHIN_API_BASE_URL`,
`ZIHIN_API_KEY_ENV`, `ZIHIN_API_MODEL`, `ZIHIN_PER_BAND`, `ZIHIN_MULTIPLIER`,
`ZIHIN_OUTPUT`, `ZIHIN_OUTPUT_COST`, `ZIHIN_EXPERIMENT`,
`ZIHIN_INPUT_COST`, `ZIHIN_TASKS`, `ZIHIN_MAX_STEPS`,
`ZIHIN_MAX_TOKENS`, `ZIHIN_MODEL`, `ZIHIN_REPEATS`, `ZIHIN_SPLIT`,
`ZIHIN_FLOOR_CEILING`, `ZIHIN_TASK_COUNT`, `ZIHIN_TASK_ID`, `ZIHIN_CEILING_LIMIT`.

Her biri yerinde gerekçeliydi. Toplamı, "fazladan yapılandırma ekleme"
kısıtının çiğnenmesi.

### 3.7 Zeminde adı olmayan betikler

On betik var. `measure_band.py`, `measure_gpt4o_subset.py` ve
`measure_boundary_control.py` zeminde adı geçmeyen keşifsel ölçümler.

### 3.8 Kod ile zemin arasında bir doğrudan çelişki

`config/models.yaml` doğrulaması `len(models) != 3` ise hata veriyor. §5 "en az
üç yoğun boyut" diyor. Dört boyut sığdıran bir aile yapılandırmayı geçemez.

### 3.9 Karar kaydının sırası bozuk

K-01'den K-61'e kadar kayıtlar var ama dosya sırası karışık: K-34 K-03'ten
sonra, K-43..K-46 K-11'den sonra, K-61 K-59 ve K-60'tan önce. Donan artefaktın
kendisi bu dosya.

## 4. Sonuç ne kadar dağıldı

| Rapor edilen sonuç | PR | Durum |
|---|---|---|
| Artık varyans üst sınırı, model başına %9,5 | #12 | **ayakta** |
| Sansür üç modelde de %100 | #12 | **yorumu bozuk** — sabit tavan, çapalar 10-195 |
| %10 ölçütünün sansüre uygulanması | #12 | **yanlış uygulama** — sansür sonuç, artefakt değil |
| Bant taraması 0/30 | #13 | **ayakta** — görev başına tavan, 7B'de kodsuz adım sıfır |
| "Kısa görevler daha kolay değil" | #13 | **geri alındı** — 7B taban artefaktı |
| Duvar auth'ta değil, 1445/1717 çağrı 200 | #14 | **ayakta** |
| Kategori 4 baskın değil, %16,9 | #14 | **ayakta** |
| gpt-4o alt kümesinde avantaj yok | #14 | **ayakta**, seçimi bölmeye bakarak yapıldı |
| Yönergenin 153. satırı çalışmıyor | #14 | **ayakta** |
| Sınır kontrolü 6/30 | #15 | **geçersiz** — çıktı bütçesi bağlayıcı |
| "Durma kuralı yetenekli modeli kesiyor" | #15 | **geri alındı** |
| Sınır kontrolü 20/30 | #15 | **alt sınır** — kodsuz adım %6,9 |
| Aile listesi, 6,5 GB ve "birden çok boyut" | (işlenmedi) | **geçersiz** — şart en az üç yoğun boyut |

Dört sonuç geri alındı ya da geçersiz oldu, biri yanlış ölçütle değerlendirildi,
biri alt sınıra indi. Hepsi son dört PR içinde.

**Dağılmanın ortak sebebi tek.** Ölçümler yapıldıkça yorumlanma çerçevesi de
aynı anda türetildi. Yazılı zemin olsaydı bunların dördü de ölçüm öncesinde
elenirdi: sabit tavan K-43'e takılırdı, dereceli skor §6'nın listesinde
olmadığı için başlığa çıkmazdı, %10 ölçütü §7'nin ayrımıyla doğru yere
uygulanırdı, bütçe §13'ün bağlayıcılık kuralıyla önceden denetlenirdi.

## 5. Hizalama planı

Sıra önemli: ölçüm yapılmadan önce zemin yazılı olmalı.

### Adım 0 — Tasarım katmanı yazılır (ölçüm yok, kod yok)

`01-problem-definition.tr.md`, `02-research-question.tr.md`, `03-architecture.tr.md`,
`04-threat-model.tr.md`, `05-experiment-design.tr.md`, `06-skill-language.tr.md` ve
`07-failure-taxonomy.tr.md` tam bağlam belgesinden dolduruluyor. K-61 hizalanıyor,
K-62 yazılıyor.

**Ön koşul kapısı bu adımda yazılıyor, Adım 1'de değil**, ve ateşlediği tarih
açıkça belirtiliyor. Aile taraması başlamadan önce yazılı olmazsa post-hoc
görünür.

Tek PR, yalnız belge. Kabul ölçütü: zeminin her bölümünün bir dosyada karşılığı
olması.

### Adım 1 — Ön kayıt ve yanlışlama kayıtları

`experiments/preregistration.md` §6, §7 ve §8'den yazılır: birincil metrik,
zorunlu tanı metriği, birincil hücre, estimand, sansür tanımı, kapılar, ölçek
ekseninin dört şekli için yorum tablosu.

**Ayar bütçesinin sayısı burada yazılıyor**, ve bugüne kadar tüketilen dört
revizyon listeleniyor: tavan çapası, soğuk rejim, ön koşul eşiği, model ailesi.

**Kurulumda dokunulan görev kimlikleri** de burada listeleniyor; değerlendirme
örnekleminden çıkarılıyorlar.

`docs/11-falsification.tr.md` üç yanlışlama kapısını kayıt olarak alır.

`experiments/experiment-matrix.csv` altı koşulu satır olarak alır.

### Adım 2 — Karar kaydı hizalanır

Sırası düzeltilir. Eksik kararlar yazılır: getiricinin sembolik olması, naif
derleyicinin tanımı, aile kontrolünün bandı, birincil metrik, tanı metriği,
duyarlılık analizi, toplanabilirlik varsayımı, ezberleme kapısı, terk kriteri.

Zeminle çelişen tek kod maddesi düzeltilir: `config/models.yaml` "en az üç".

### Adım 3 — Dağılan sonuçlar işaretlenir

PR #12, #13 ve #15 raporlarına durum satırı eklenir: hangi sayı ayakta, hangisi
geri alındı, hangisi alt sınır. Amaç geçmişi silmek değil, hiçbir bayat sayının
alıntılanamaması.

### Adım 4 — Sansür ölçümünün tekrarı ertelendi

Aile değişecekse o ölçüm zaten değersiz. Sabit yirmi tavanla alınan sayılar
geçersiz işaretlenip bekletiliyor; tekrar aile seçildikten sonra, o ailenin
kendi sayılarıyla yapılacak.

Bant taraması ve teşhisler ayakta, tekrar gerekmiyor.

### Adım 5 — Aile seçimi kaldığı yerden

Doğru şartlarla çıkarılmış aday listesi üzerinden, eleme iki bantta, bütçeler
bağlayıcı olmayacak şekilde.

## 6. Altı açık noktanın cevapları

Hepsi karara bağlandı.

1. **Barındırılan modelin künyesi.** Sözleşme atlanmıyor, genişletiliyor.
   `serving_mode` alanı ekleniyor; yerele özgü kavramlar hosted kipte koşullu
   boş bırakılabiliyor, local kipte zorunlu kalıyor. Fail-closed özelliği
   korunuyor.
2. **Dereceli skor tanı metriği**, ikincil sonuç değil. Birincil metriğe ve
   yanlışlama kapılarına asla girmiyor. Veriyi gördükten sonra doğduğu açıkça
   yazılıyor. Bir taramada kullanılacaksa tanımı taramadan önce yazılıp o
   kullanım için önceden ilan ediliyor.
3. **`config/models.yaml` "en az üç" olacak.** Config, tasarımdan daha katı bir
   kısıt kodlayamaz.
4. **Üç keşifsel betik kurulum aracı**, deney yolunda değil. `scripts/setup`
   altına alınıp belgeleniyor, deney matrisine girmiyor.
5. **Kurulum sırasında dokunulan görevler değerlendirme örnekleminden
   çıkarılıyor**, biriktirme havuzunda kalabilirler. Dokunulan görev kimlikleri
   listelenip ön kayda yazılıyor. `test_normal`'da 168 görev var, otuzunu
   kaybetmek pahalı değil.
6. **Ortam değişkeni kuralı:** ölçümü etkileyen her şey config'de ya da
   künyede, ortamda değil. Ortam yalnız gizli değerler ve sunucudan geri okunan
   değerler için kalıyor. Künyenin sessizce `None` okuması zaten bu yüzden
   olmuştu.

## 7. Denetimden çıkan genel kural

Dağılan dört sonucun ortak sebebi tek bir eksiklikti ve kural olarak yazıldı
(K-62):

**Yorumlanma kuralı koşudan önce yazılmamış bir ölçüm sonuç değildir, kurulum
tanısıdır, ve sonuç iddiasında kullanılamaz.**
