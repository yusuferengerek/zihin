# Mekanizma pilotu — rapor

**Bütün sayılar `results/pilot-dataset.json` içinde.** Bu rapor manşetleri
söylüyor, tabloları ve ızgaraları kopyalamıyor; her bölüm veri setindeki yolunu
gösteriyor. Sekiz ayrı ölçüm çıktısından elle taşınan bir sayı, kaynağından
bağımsız yaşlanır — bu depoda yazma kümesi tek günde iki kez değişti ve aynı
ölçüm iki farklı sayı verdi.

---

## Bu rapor neyin raporu, neyin değil

**Ön koşul kapısı 11 Ağustos 2026'da ateşledi, yerel eksende taban sıfır
çözüyor, ve birincil karşılaştırma bu yapılandırmada koşulamadı.**

Kanıt ve tarih (`pilot-dataset.json` → `precondition_gate`):

| | Ölçüm | Sonuç |
|---|---|---|
| Yerel eksen | `qwen2.5-coder:7b-instruct-q4_K_M`, test_normal, 30 görev | **0 geçti** |
| Yerel eksen, durma kuralı kapalı | aynı model, 26 görev | **0 geçti** |
| Sınır kontrolü | DeepSeek V4 Flash 0731, aynı 30 görev | 20 geçti |

Kapının ateşlemesi bir bulgu, arıza değil: kural `05-experiment-design.tr.md`
içinde önceden yazılmıştı ve tam olarak öngördüğü durumda ateşledi. Sınır
kontrolü sıfırların düzenekten değil modelden geldiğini gösterdi — hat
çalışıyor, o model çözmüyor.

**Sonucu.** Pilotun tanımı beş koşulun karşılaştırması (K-145'ten önce altı) ve birincil metrik görev
başına model çağrısı. Taban hiç çözmediği için adım farkı **tanımsız**:
karşılaştırılacak başarılı epizot yok. Bu raporda hiçbir yerde "mekanizma
kazandırdı" ya da "kazandırmadı" yazmıyor, çünkü o soru bu yapılandırmada
sorulmadı.

**Bu raporun konusu mekanizma pilotu:** mekanizmalar kuruldu mu, çalıştıkları
gösterildi mi, ve pilot koşusunun ihtiyaç duyacağı sayılar ölçüldü mü.

---

## Ne kuruldu ve çalıştığı nasıl gösterildi

**Mekanizmalar kuruldu ve çalıştıkları gösterildi. Dört giriş becerisi, ikisi
kimlik bilgisini kendi getiriyor. On beş kart, on biri yetki reddi. Kapsama
yanlışlama kapısının üstünde.**

### Beceri kütüphanesi

`pilot-dataset.json` → `skills`, kütüphane `v0-gap2-sup3-142662f`.

| Etki soneki | Destek | Gövde | Tasarruf | Parolayı kendi okuyor |
|---|---|---|---|---|
| `POST venmo.auth/token` | 8 görev | 2 çağrı | 8 | hayır |
| `POST spotify.auth/token` | 7 görev | 3 çağrı | 7 | **evet** |
| `POST simple_note.auth/token` | 5 görev | 7 çağrı | 30 | **evet** |
| `POST phone.auth/token` | 5 görev | 5 çağrı | 20 | hayır |

Dördü de giriş becerisi. İkisi `GET supervisor.account_passwords` çağrısını
gövdesinde taşıyor, yani parolayı kendi getiriyor ve çağıranından istemiyor;
diğer ikisi kimlik bilgilerini imzasında ilan ediyor (S-42'nin düzeltilmiş
hâli).

### Hata indeksi

`pilot-dataset.json` → `failure_patterns`, indeks `v0-sup1-4bb340a`.

| Etiket | Durum kodu | Kalıp |
|---|---|---|
| `authorization_denied` | 401 | **11** |
| `invalid_parameter` | 422 | 3 |
| `conflicting_state` | 409 | 1 |

On üç kalıbın karşıtsal eşi var, ikisinin yok ve o ikisi koşul taşımıyor (K-85).
On iki kalıpta ayıran koşul çağrının kendi uygulamasına ait.

### Getirici

Kapsama, filtresiz tavan (`pilot-dataset.json` → `coverage.per_split`):

| Bölme | Herhangi | Yalnız beceri | Yalnız hata | Madencilenmemiş görevlerde |
|---|---|---|---|---|
| train (90) | %96,7 | %90,0 | %96,7 | %96,7 |
| dev (57) | %94,7 | %89,5 | %94,7 | %94,7 |
| test_normal (168) | %100 | %94,6 | %100 | %100 (150 görev) |

Yanlışlama kapısı %25; dokuz ölçümün (üç bölme × üç okuma) dokuzu da üstünde.
Mekanizma başına ayrı verilmesinin sebebi pilotun kendi yapısı: "yalnız
beceriler" ile "yalnız hatalar" ayrı koşullar, ve bir görev biri için
kapsanmışken diğeri için kapsanmamış olabiliyor.

**Madencilenmemiş görevlerde kapsama düşmüyor.** test_normal'ın 168 görevinden
150'si kütüphanenin madencilendiği görevler arasında değil ve o 150'de kapsama
%100. Yani kapsama bir ezber değil.

### Kalkan

İki oran ayrı, ve birbirinin yerine geçmiyor (K-72,
`pilot-dataset.json` → `shield`):

| Oran | Değer | Nerede ölçülebiliyor |
|---|---|---|
| Yanlış pozitif | **6/147 = %4,1** | train + dev, yer gerçeği var |
| Engelleme, çağrı | **6/9154 = %0,07** | bütün korpus, 258 epizot |
| Engelleme, epizot | 6/258 = %2,33 | aynı |
| Fail-open dalı | 5213 çağrının 0'ı | aynı |

**Düzeltme, 15 Kasım 2026: engelleme satırları.** Bu korpusa bir testin iki çıktısı da
girmişti: `tests/test_appworld_reset.py`'nin iki AppWorld koşusu (2 epizot, 9 çağrı).
Engellenen altı çağrının biri o testin kendi açtığı nottu. Onlarsız çağrıda
5/9145 = %0,05, epizotta 5/256 = %1,95. Yeniden hesap S-83'te.
`results/shadow-mode.json` yeniden yazılmadı.

---

## Ne ölçüldü: iki eksik ölçüm

Bu iki sayı kilitli şartnamede duruyordu ve hiç sınanmamıştı.

### Kart jeton bütçeleri

Şartname beceri kartını yedi alan ve ≤180 jeton, hata kartını beş alan ve ≤120
jeton olarak yazıyor. Depoda **kart biçimi yoktu**: getirici kart nesnesi
döndürüyordu, basılmış hâli yoktu, dolayısıyla bütçe hiç ölçülmemişti. Biçim
kuruldu (`src/zihin/cards.py`, K-87) ve gerçek kartlara karşı, modelin kendi
tokenizer'ıyla ölçüldü (`pilot-dataset.json` → `card_tokens`):

| Kart | Sayı | Jeton | Bütçe | Aşan |
|---|---|---|---|---|
| Beceri | 4 | 78–122, medyan 88 | ≤180 | **0** |
| Hata | 14 | 36–48, medyan 42 | ≤120 | **0** |

Biçim bütçeye sığıyor; taşma olmadığı için biçim düzeltmesi gerekmedi. Ölçek
ekseninin üç modeli her kart için aynı sayıyı veriyor, yani "180 jeton" tek bir
sayıyı adlandırıyor.

**On beş kalıbın on dördü ölçüldü, çünkü on dördü getirilebiliyor.** Kalan biri
(`GET api_docs.api_descriptions`, 150 hata — indeksin en sık kalıbı) hiçbir görev
tarafından getirilemiyor: altyapı uygulamaları getiricide düşüyor. Ayrıntısı
S-48.

### Birleştirilmiş bağlam, k=5+5

`pilot-dataset.json` → `context_cost`. Ölçüm üretim yolunda: prompt dosyası
`scaffold.write_rendered_prompt` ile yazılıyor, referans ajanın kendisi okuyor ve
kendi `text_to_messages`'ı bölüyor; kısayolun ajanın çıktısıyla bayt bayına aynı
olduğu gerçek bir dünya açılarak doğrulandı.

| | Jeton, medyan | 32K pencerenin payı |
|---|---|---|
| Sabit blok | 3172–3185 | %9,7 |
| Kart bloğu, k=5+5 | 125 (train/dev) – 264 (test_normal) | %0,4–0,8 |
| İkisi birlikte | 3296–3447 | %10,1–10,5 |
| İkisi birlikte, en çok | 3645 | %11,1 |

**32K'ya sığıyor, ve sabit blok bütçenin onda birini yiyor.** Mimari belgesi
"beşte biri, kartlarla dörtte biri" diyordu; ölçüldüğünde yanlış çıktı ve
düzeltildi (S-46). Yanlışın kaynağı birim karışması: Aşama 2'nin 5958 sayısı adım
başına girdi jetonu, yani birikmiş geçmişi de içeriyor.

**Kartların bedeli bir turluk geçmiş.** Kayıttan ölçülen tur maliyeti medyan 182,
ortalama 419, p90 1066 jeton. Medyan turla pencereye kartsız 162, kartlı 161 tur
sığıyor.

**Ama bağlayıcı sınır pencere değil.** Referans iskele bağlamı karakterle kesiyor
ve 50000 karakter ölçülen içerikte **12799 jeton**, yani pencerenin %39'u
(S-47). Bağlam montajcısı bütçesini yazarken iki farklı birimle uğraşmak zorunda;
K-26'nın açık bıraktığı çakışma tam burada.

---

## Ne çıktı: yorum

### Ayna bulgusu, ve bağımsızlık varsayımına sonucu

**Kütüphane jetonu almayı öğretiyor, indeks jetonu taşımamayı yasaklıyor.**

| | Beceri kütüphanesi | Hata indeksi |
|---|---|---|
| Korpus | 22 geçen epizot, 20 görev | 5213 eylem, 767 hata |
| Madencilik | kapalı sıralı örüntü, destek görev üzerinden | karşıtsal koşul arama |
| Büyüklük | 4 becerinin **4'ü** giriş | 15 kartın **11'i** `authorization_denied` |

İki korpus, iki bağımsız madencilik, aynı mekanik darboğaz. Biri "önce jetonu
al" diyor, diğeri "jetonu taşımadan çağırma" diyor.

**Ölçümle gelen sınır (S-57).** Üç kollu koşuda giriş etkisine üç kolun
hepsinde ulaşıldı — on beş hücrenin üçü ile yedisi arasında — ama tamamlama
0/45. Jetonu almak bu örneklemde hiçbir görevi çözdürmedi. İki mekanizmanın aynı
darboğaza yakınsaması gerçek bir bulgu; o darboğazın görevin çözüldüğü yer
olmadığı da öyle. İkisi birlikte okunmalı.

**Sonucu ve şimdi ilan ediliyor: iki mekanizma bağımsız değil.** Deney tasarımı
`skills`, `failures` ve `skills_failures` koşullarını ayrı ayrı koşuyor ve
üçüncünün ilk ikisinin toplamına yakın çıkmasını beklemek doğal olurdu. **O
toplanabilirlik varsayımı bu korpusta muhtemelen tutmayacak** (K-84): ikisi de
aynı arızayı hedefliyorsa, birinin kapattığı arızayı diğeri ikinci kez
kapatamaz.

### Sıfır engelleme neyin kanıtı

**Model yörüngelerinde sıfır engelleme, kalkanın ucuz olduğunun kanıtı değil,
korpusun kalkanı sınamadığının kanıtı.** Altı engellemenin altısı da düzeneğin
kendi yazma sondalarından, tek görevde ve tek uçta. Sebebi korpusun kendisi: 58
görevin çoğu tek uygulamaya dokunuyor ve sınır geçen yazma fırsatı hiç doğmuyor.
Kalkanın gerçek maliyeti yanlış pozitif oranından okunuyor — %4,1 — ve o oran da
yalnız yer gerçeği olan iki bölmede ölçülebiliyor.

### Eylemsizliğin ödüllendirildiği görüldü, ve no-op düzeltmesinin sebebi bu

Uçtan uca demonun `0de03ea_1` görevinde doğrulayıcı beş test koşuyor. Ham skor
kartlı kolda 3, taban kolda 2 — yani fark küçük görünüyor. No-op tabanına göre
düzeltilince (`graded_detail`, K-53'ün dayandığı `no_op_fail` / `no_op_pass`
etiketleri) fark **2/3'e 0/3**: taban kolun iki geçişi de hiçbir şey yapmayan bir
ajanın geçeceği testler. Sayılar `results/demo-eklenti.json` içinde.

**Ters yöndeki bulgu daha keskin: kartlı kol eyleme geçtiği için bedava bir
geçişi kaybetti.** Beşinci test kuyruğa koleksiyon dışından şarkı girmemesini
istiyor. Boş kuyruk bunu bedava geçiyor; kuyruğa üç yanlış şarkı koyan kol
düşüyor. Yani bu görevde ham skor, hiçbir şey yapmamayı yanlış bir şey yapmaya
tercih ediyor.

Bu, no-op düzeltmesinin neden var olduğunun canlı örneği. Birincil metrik ham
geçiş sayısı olsaydı mekanizmaların eylemsizliği artırması ödüllendirilirdi;
K-53'ün sansür tanımı ve `graded_detail`'in anlamlı/önemsiz ayrımı tam bu
ödülü kesiyor. Tek görev, ve iddia bu kadar: metriğin bu yönde bir açığı
olduğunu ölçülmüş bir örnekle biliyoruz.

**Aynı demoda kartın zarar verdiği tek epizot da kaydedildi ve zararı kartın
içeriğinden gelmiyor.** `0a9d82a_3`'ün kartlı kolu yirmi adımın yirmisinde hiç
eylem üretmedi (K-36 kategori 4) ve ürettiği kod var olmayan API adlarını
çağırıyor, yani kartın gösterdiği diziye hiç gelmemiş. Tek epizot; sebebi
söylenemez, ama "kart yanlış çağrıya yönlendirdi" okuması bu veriyle
desteklenmiyor.

### Tasarruf kestirimleri bir alt sınır

**Tasarruf kestirimleri DeepSeek yörüngelerinden ölçüldü ve zayıf modeller için
bir alt sınır.** Geçen 22 epizodun 22'si `openrouter/deepseek/deepseek-v4-flash-0731`
ile koştu; yerel eksen hiç çözmediği için kütüphane başka bir yerden
madencilenemezdi. Zayıf bir model aynı çağrıları daha çok adımda yapar, yani
becerinin ona değeri bu sütunun söylediğinden yüksek olur — ve becerilerin yardım
etmesi beklenen modeller tam da o zayıf modeller.

**Değer eşiği hâlâ seçilmedi ve pilottan önce seçilmeyecek** (K-50). Duyarlılık
veri setinde: eşik 10'da beceri kapsaması %94,6'dan %50,6'ya, 30'da %35,7'ye
iniyor. Ayırt eden koşul sayısı üst sınırı 1'e çekilirse hata kapsaması
%100'den %38,1'e iniyor. Bir eşiği bu sayılara bakarak seçmek yirmi görevlik bir
korpusa uydurmak olurdu.

### Kapsama yüksek ama tek boyutlu

Yüksek kapsama tek başına getiricinin ayırt ettiğini göstermiyor: her göreve aynı
kartı veren bir getirici de %100 alırdı. Ayırt edicilik ayrıca ölçüldü
(`results/retriever-discrimination.json` → `distinct_card_sets`, `most_common_set_share`): test_normal'da kart kümeleri
birbirinden ayrışıyor ve en sık küme görevlerin küçük bir azınlığında kalıyor.
Getirici gerçekten ayırıyor.

**Ama ayırdığı şey hangi uygulamanın girişi olduğu, hangi tür beceri olduğu
değil.** Kütüphanedeki dört becerinin dördü de aynı işi farklı uygulamalarda
yapıyor, dolayısıyla getiricinin "doğru kartı seçmesi" bugün "doğru uygulamayı
seçmesi" demek. Getiricinin ayırt etme gücü ancak çeşitlenmiş bir kütüphaneyle
sınanabilir.

### Dört beceri bir korpus çeşitliliği bulgusu

Dört becerinin dördünün de giriş olması madenciliğin darlığından değil korpusun
yapısından geliyor, ve bu iddia madencilik ızgarasından çıkarılamıyor: ızgara her
eşikte **kaç** beceri çıktığını yazıyor, hangileri olduğunu yazmıyor. Doğrudan
ölçüldü (`pilot-dataset.json` → `corpus_diversity`).

Geçen 20 görev altı uygulamaya ve sekiz farklı uygulama kümesine dağılmış:
venmo 8, spotify 7, phone 5, simple_note 5, file_system 1, todoist 1.

Bir örüntünün kütüphaneye girmesi için en az üç farklı görevde geçmesi gerekiyor
(destek görev üzerinden sayılıyor). Üç ya da daha fazla görevde geçen **14 çağrı**
var ve dağılımı şu:

| Sınıf | Sayı | Örnek |
|---|---|---|
| Altyapı | 4 | `GET api_docs.api_doc`, `GET supervisor.account_passwords` — 20/20 görevde |
| Oturum | 4 | dört `auth/token` — kütüphanedeki dört beceri |
| Sıradan okuma | 5 | `GET phone.contacts` 5, `GET simple_note.notes` 5, `GET spotify.library/playlists` 4 |
| Sıradan **yazma** | **1** | `POST venmo.payment_requests`, 3 görev |

**Kütüphaneye giren becerinin etki soneki boş olamaz (K-75), yani aday olmak için
yazan bir çağrı gerekiyor.** Oturum çağrıları dışında bu eşiği geçen yazan çağrı
sayısı bir. Tekrarlayan tek şeyin kimlik doğrulama olduğu iddiası tam olarak bu
anlamda doğru: sıradan okumalar tekrarlıyor, ama etki üreten tekrar yalnız
girişte.

**Eşik gevşetilirse sayı büyüyor ve kimlikleri bilinmiyor.** Destek 2'ye
inildiğinde boşluk 2'de 11, boşluk 5'te 35 beceri çıkıyor (`mining_grid`). O
hücrelerde beceri kimlikleri kaydedilmedi, dolayısıyla "onlar da giriş mi" sorusu
bugün yanıtsız. Kayıtsızlık bir eksiklik ve pilot koşusundan önce kapanması
gerekmiyor: kurşun yapılandırma zaten destek 3.

---

## İki iddia, ve yalnız biri ayakta

**"Kartlar bağlama ulaşıyor" — ayakta.** Kart bloğunun prompt dosyasına bayt
bayına girdiği, iki kolun yalnız blok kadar farklı olduğu ve kartsız kolun
prompt'unun referansla özdeş kaldığı modele hiç bakmadan ölçüldü, üç görevde
3/3 (`results/card-demo.json` → `tasks[].entry`). Bu ölçüm mekanik ve gürültüden
etkilenmiyor.

**"Kartlar davranışı değiştiriyor" — desteklenmiyor.** Demonun tek epizotluk
kollarında kartlı kol iki çiftte başarılı etkiye ulaşmış, kartsız kol hiçbirinde
ulaşmamıştı. Üç kol × beş görev × üç tekrar koşulunca kartsız kol on beş
hücrenin altısında ulaşıyor ve on beş hücrenin on biri tekrarlar arasında
ayrışıyor. İddia geri çekildi (S-56, `docs/reports/uc-kollu-kart-kosusu.md`).

**Hasarın kapsamı.** Gürültü tabanı, iki kolu tek epizotla karşılaştıran her
ölçümü geçersiz kılıyor; bu düzenekte öyle olan tek ölçüm demoydu. Sıfırlar
etkilenmiyor: `bant2`, `bant3` ve `bant3-kapali` üç bağımsız koşu, üçü de sıfır,
ve gürültü bir sıfırı imal edemez. Ön koşul bulgusu (K-58) yerinde.

**Ek, 26 Ağustos 2026.** Bu üç koşunun tavana çarpma oranı sonradan ölçüldü ve
üçü eşit ağırlıkta değil: `bant3` %0,0, `bant3-kapali` **%96,2**, `bant2` ise
kayıtta yok. Bulgu ayakta — bir tavan sıfırı gizleyebilir ama üretemez — ama iki
sıfır **alt sınır** (S-63).

## Ne bozuldu

Pilot koşusu koşulmadığı için "epizot düştü" türü bir liste yok. Bozulan şeyler
ölçüm sırasında bulundu.

| | Ne | Sonuç |
|---|---|---|
| S-46 | Mimari belgesinin sabit blok payı ölçülmemişti, beşte bir yazıyordu | Ölçüldü, onda bir; belge düzeltildi |
| S-47 | Bağlam iki farklı birimde sınırlı ve hangisinin bağladığı bilinmiyordu | Karakter tavanı bağlıyor: 50000 karakter = 12799 jeton |
| S-48 | İndeksin en sık kalıbı hiçbir görev tarafından getirilemiyor | Kayda geçti; terk kriteri getirilebilir kalıp sayısına bakacak |
| K-76 | Kirli ağaç kapısı listeye daraltılırken listenin kendisi eksik çıktı | `retriever.py` ve `cards.py` listeye eklendi |
| — | `num_predict: 0` "üretme" demiyor: sunucu üç satırlık bir promptta kırk bin jeton üretti | Sayaç `num_predict: 1` ile çalışıyor |

Beşincisi küçük ama türü tanıdık: bir parametrenin adı davranışını söylemiyor ve
ölçüm sessizce başka bir şey ölçüyor olabilirdi — burada ölçmedi, çünkü ölçüm
takıldı ve fark edildi.

---

## Sınırlamalar

Aşağıdakiler bu pilotun sonuçlarını okurken bilinmesi gerekenler. Hepsinin tam
hâli `docs/09-limitations.tr.md` içinde.

**409 sınıfı v0 indeksinin kapsamı dışında (S-43).** Kayıtlı 34 `409` hatasının
hepsi tek uçta (`POST venmo.transactions`) ve gerçek sebebi nesne durumu. Koşul
dilinin bunu ifade edebilecek iki biçimi gözlenemiyor, çünkü yanıt gövdesi kayda
yazılmıyor (S-40). İndekste bu sınıftan bir kart var ama sebebi söylemiyor.

**Bağlı argüman tespiti ajanın yazdırdığı metinle sınırlı (S-40).** Bir argümanın
"daha önceki bir çağrının çıktısında geçtiği" ancak ajan o çıktıyı yazdırdıysa
görülebiliyor. Yazdırmadığı bir değere bağlılık serbest parametre olarak
görünüyor, yani imzalar olduğundan uzun olabilir.

**Son koşulların dördü de boş, ve iki ayrı sebebi var (S-41).** Birincisi bu dört
becerinin kendi doğası: giriş çağrısı jeton üretiyor, satır üretmiyor, ve durum
farkı satır sayımına dayanıyor (S-35). İkincisi atıf: bir adımda birden fazla
çağrı varsa o adımın durum farkı hangi çağrıdan geldiği ayrılamıyor, ve yalıtılmış
adım gerektiren kural oluşumların çoğunu ölçülemez kılıyor. İki sebep ayrı, ve
ikisi de "kesişim boş" değil "ölçülemedi" demek.

**Yazma kümesinde bilinen bir fazla dahil etme var: 64 uç (S-38).** GET dışı
yöntemle tanımlı ama gövdesinde yazma bulunmayan 64 uç kümede duruyor. İkisi
doğrulanmış okuyucu. Etkisi kayıtlı: her uç `body_write` alanını taşıyor, yani
fazla dahil etme raporun içinde değil ürünün içinde görünüyor.

**Kalkanın isabeti izinli uygulama çıkarımının isabetiyle sınırlı (S-03).** İzinli
küme görev metninden çıkarılıyor, yer gerçeğinden değil: tam eşleşme %75,5,
Jaccard 0,857. Kalkanın verdiği her karar bu çıkarımın üstünde duruyor ve
çıkarımın hatası kalkanın hatası olarak görünüyor.

**Kütüphane ve indeks tek modelin yörüngelerinden geldi.** Geçen 22 epizodun 22'si
aynı barındırılan modelle koştu ve hepsi test_normal'da. Başka bir modelin
yörüngelerinden başka beceriler çıkabilir; bu kütüphanenin çeşitliliği o modelin
davranışının çeşitliliği kadar.

**Kart biçimi bir modele hiç gösterilmedi.** Bütçeye sığdığı ölçüldü, okunabilir
olduğu ölçülmedi — ikisi ayrı sorular. Somut bir şüphe var: parametre adları
`3.password` biçiminde, yani "gövdenin üçüncü çağrısının `password` argümanı".
Ad kayıttan mekanik olarak geliyor ve bir modelin onu doğru bağlayabildiği
gösterilmedi. Bu, madde 7'nin — uçtan uca demo — ilk sorusu.

---

## Asıl koşuya taşınan kararlar

| Karar | Ne |
|---|---|
| K-87 | Kart biçimi: yedi alan, beş alan, okuma anında filtrelenen alan basılmıyor |
| K-88 | Bağlam maliyeti ölçüldü; bağlayıcı sınır karakter tavanı, pencere değil |
| K-89 | Pilotun sayıları tek veri dosyasında; rapor atıf veriyor, kopyalamıyor |
| K-76 | Kirli ağaç kapısı ölçümü belirleyen yollara daraltıldı, uygulandı |

**Açık kalan ve pilottan önce karar bekleyen:** değer eşiğinin sayısı, ayırt eden
koşul sayısı üst sınırı, karşıt başarısı olmayan kartların koşula alınıp
alınmayacağı (K-50 kapsamında üçü de duyarlılık ızgarasında duruyor), ve zorlama
kipindeki ikame yanıtın biçimi (K-71).

**Model ailesinin yeniden seçilmesi kapının ateşlemesinin sonucu** ve bu depoda
üretilecek bir şey değil: ya sıfırın üstünde skor alan bir yerel model, ya
pilotun yerel olma şartının kaldırılması.


---

## Ek — 26 Ağustos 2026: raporun son cümlesi kapandı

Bu rapor şu cümleyle bitiyordu: *"ya sıfırın üstünde skor alan bir yerel model,
ya pilotun yerel olma şartının kaldırılması."*

**İkincisi oldu.** Yerel olma şartı kaldırıldı (K-133, K-137) ve eksen iki nokta
uzatıldı. Yolun tamamı ayrı bir belgede: `docs/reports/eksen-uzatma.tr.md`.

### Eksenin bugünkü hâli

| Nokta | Sonuç | Tavana çarpma | Etiket |
|---|---|---|---|
| 1.5B | 0/30 | %33,3 | ALT SINIR |
| 3B | 0/30 | %33,3 | ALT SINIR |
| 7B | 0/30 | %30,0 | ALT SINIR |
| 14B | 3/30 | %20,0 | ALT SINIR |
| 32B | **11/30** | **%6,7** | **ÖLÇÜM** |

Beş sayı aynı ağırlıkta değil: K-60'ın eşiği %10 ve dördü aşıyor. Yerel üç
noktanın sıfırı 4000 jetonla yeniden ölçüldükten sonra da sıfır kaldı — bütçe
bağlayıcıydı ama bandı açan şey değildi.

### Bu pilotun sorusu için asıl sayı

Otuz görev değerlendirme dosyalarından iki tipe ayrıldı: **cevap tipi** (5) ve
**cevap+dünya tipi** (25).

| Model | Cevap (5) | Cevap+dünya (25) |
|---|---|---|
| 14B | 2/5 | 1/25 |
| 32B | 4/5 | **7/25** |

Bu pilotun mekanizmaları — beceri kütüphanesi API çağrı dizileri, hata indeksi
çağrı başarısızlıkları — yalnız **dünyayı değiştiren** görevlerde işe yarayabilir.
Yani mekanizmaların sınanabileceği bant 32B'de 7/25; 14B'de 1/25 idi.

### Bu ekin kurmadığı

Mekanizmaların model çağrısını düşürüp düşürmediği hâlâ ölçülmedi. Uzatma
koşuları **keşifsel**: eksen noktaları sıfırlar görüldükten sonra seçildi.
14B'nin koşulları koşudan sonra düzeltildi. Ve eksenin noktaları üç farklı
kartta ölçüldü (S-61).

### Bu turda açılan sınırlamalar

`S-58` koşul sapması (üçüncü örneğiyle), `S-59` eksik küme ve bağlayıcı tavan,
`S-61` üç farklı kart, `S-62` bant etiketinin ne ölçtüğü, `S-63` ön koşulun
dayandığı üç koşunun tavan denetimi. Tam hâlleri
`docs/09-limitations.tr.md` içinde.
