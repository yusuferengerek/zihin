# SKILL_SPEC — becerinin veri yapısı

`docs/06-skill-language.tr.md` becerinin **nasıl madencilendiğini** anlatıyor. Bu
belge madenciliğin **ne ürettiğini** tanımlıyor: derleyicinin yazdığı, getiricinin
okuduğu, yürütücünün koştuğu ve düşürme kuralının saydığı kayıt.

İkisi ayrı belge çünkü ayrı şeyler değişiyor. Madencilik parametreleri kurulum
sonrasında kalibre ediliyor (K-50); buradaki alanlar `skills` tablosunun şeması
ve bir kez yazıldıktan sonra göç gerektiriyor.

**Tasarım kısıtı, her alan için geçerli.** Derleyici çevrimdışı, belirlenimci ve
model kullanmıyor (`03-architecture.tr.md`). Dolayısıyla buradaki hiçbir alan elle
yazılamaz ve hiçbiri bir modelden gelemez. Her alanın mekanik bir türetmesi var
ve türetme kayıttaki epizotlardan çıkıyor.

**Düzeltme, 18 Ekim 2026: ölçüleni tablo tanımlıyor.** Bu belge hiç dondurulmadı ve
tasarlanan kartı anlatıyor. Ölçülen beceri kaydının otoritatif tanımı `skills`
tablosu (`src/zihin/schema.sql`): ölçümü tanımlayan kodun parçası ve `4a04e50`'de
dondu (K-202). Bu belgenin dokuz alanı tasarlandı, o biçimiyle uygulanmadı:

- Altısının uygulaması yok: `precondition`, `invocations`, `blamed_failures`,
  `postcondition_misses`, `model_failures_gate_1`, `model_failures_gate_2`. Beceriler
  modele metin kartı olarak veriliyor ve çağrılmıyor; bu yüzden ön koşul
  kapılarının, son koşul ıskalarının, suç atfının ve çağrı sayaçlarının uygulaması
  yok.
- Üçü tabloda başka biçimde duruyor ve tablonun biçimi geçerli: `signature` yerine
  `free_parameters`; `calls` yerine `body` ve `body_length`; `effect_suffix` yazan
  çağrıların indekslerini değil, sonekin çağrılarını tutuyor.

Aşağıdaki 13 Ekim düzeltmesindeki "defterde karar yok" cümlesi bununla kapandı
(S-81).

---

## 1. Kimlik

| Alan | Tip | Türetme |
|---|---|---|
| `skill_id` | TEXT | Etki sonekinin özeti. Aynı etki soneki aynı beceri (`06-skill-language.tr.md`) |
| `library_id` | TEXT | Beceriyi üreten kütüphane derlemesinin kimliği; künyedeki `library_id` ile eşleşiyor |
| `signature` | TEXT | Serbest parametrelerin sıralı listesi; bağlı argümanlar ve sabitler burada değil |

Kimliğin etki sonekinden gelmesi bir karar: arama öneki değişse de aynı etkiyi
üreten diziler tek beceri sayılıyor.

## 2. Gövde

| Alan | Tip | Türetme |
|---|---|---|
| `calls` | JSON | Sıralı çağrı listesi. Her çağrı: `app`, `api`, `http_method`, argüman şablonu |
| `bound_arguments` | JSON | Çağrı indeksi → daha önceki bir çağrının çıktısındaki yapısal yol |
| `constants` | JSON | Gömülü değerler ve her birinin kaç farklı görevde görüldüğü |

`constants` yalnız değeri değil **kanıtını** da taşıyor. Yanlış dondurulmuş bir
sabit beceriyi sessizce bozuyor, ve sayı olmadan bir sabitin neden sabit
sayıldığı sonradan sorgulanamaz.

### Etki soneki boş olamaz: kütüphaneye girme şartı

Beceri arama öneki ve etki soneki olarak ikiye ayrılıyor
(`06-skill-language.tr.md`). **Kütüphaneye giren bir becerinin etki soneki boş
olamaz.** Bir çağrının etki üretip üretmediğine kalkanın yazma kümesi karar
veriyor; aynı artefakt hem kalkanın sınırını hem becerinin sınırını çiziyor.

| Alan | Tip | Türetme |
|---|---|---|
| `effect_suffix` | JSON | Yazma kümesine göre yazan çağrıların indeksleri |
| `kind` | TEXT | `skill` (etki soneki dolu) veya `discovery_prefix` (boş) |

Etki soneki boş olan örüntüler **madencileniyor ama kütüphaneye girmiyor**. Ayrı
bir sınıf olarak — **keşif öneki** — ayrı raporlanıyor ve getiriciye
verilmiyor.

**Düzeltme, 13 Ekim 2026: `kind` alanı tabloda yok.** K-75 boş etki sonekli
örüntülerin kütüphaneye hiç girmediğini yazıyor ve `skills` tablosu buna uyuyor: boş
etki sonekini bir `CHECK` kısıtıyla reddediyor. Kütüphanedeki her kayıt bir beceri,
yani ayırt edecek bir alan gerekmiyor. Aşağıdaki dokuzuncu değişmez bu kısıtla
zorlanıyor. Tabloyla ayrışan öbür alanlar için defterde karar yok; onlar S-81'de
kayıtlı.

**Üç gerekçe, üçüncüsü asıl olan.**

**Birleştirme kuralı anlamını yitirir.** Aynı beceri olmanın ölçütü aynı etki
soneki. Boş sonekler birbirine eşit, dolayısıyla bütün salt okuma örüntüleri tek
beceriye çöker. Kural bir ayrım aracı olmaktan çıkar.

**Beceri kendini doğrulayamaz.** Son koşul durum farklarının kesişimi; salt
okuma hiçbir durum farkı üretmiyor, yani son koşul zorunlu olarak boş kalıyor ve
yürütme sonrası doğrulama dalı o beceride ölü. Doğrulanamayan bir beceri
düşürme kuralına da veri vermiyor.

**Alakasız getirme kontrolü evrensel boilerplate'i ayıramaz.** Kontrolün mantığı
"başka uygulamadan yanlış içerik ver, kazanç kaybolmalı". Uygulama-bağımsız bir
boilerplate'in alakasız sürümü **yok**: `api_docs` keşfi her görevde aynı ve her
görevde geçerli. Kontrol o kazancı içeriğe yazar ve atıf yanlış olur. Kütüphaneye
alınırsa ölçülen kazancın bir kısmı hiçbir kontrolle ayrılamaz hâle gelir — bu,
bir ölçüm kusuru değil, ölçülemezlik.

**Bulgu kaybolmuyor.** "İskelenin her görevde tekrarlanan bir keşif öneki var"
kendi başına raporlanabilir ve ilginç bir olgu; ölçülmüş hâli
`experiments/preregistration.md` içinde. Boilerplate önbelleklemesi bir kazanç
olarak iddia edilecekse **ayrı ve açıkça etiketli** olur, becerilere atfedilen
kazancın içinde değil.

**Boş etki soneki ile boş son koşul aynı şey değil.** Etki soneki dolu bir
beceri de boş son koşul üretebiliyor: yazmaları yalnız alan düzeyinde ise satır
sayımı onları görmüyor (aşağıdaki bilinen sınır). O beceri kütüphaneye giriyor,
yalnız doğrulama dalı çalışmıyor. Ölçüt **etki soneki**, son koşul değil.

## 3. Destek

| Alan | Tip | Türetme |
|---|---|---|
| `supporting_tasks` | JSON | Beceriyi destekleyen **farklı görev** kimlikleri |
| `supporting_episodes` | JSON | Epizot kimlikleri; postcondition'ın türetildiği küme |
| `support` | INTEGER | `len(supporting_tasks)`, epizot sayısı değil |

Destek görev üzerinden sayılıyor: tek bir görevin on epizodu bir örüntüyü
kütüphaneye sokmasın diye.

## 4. Ön koşul

| Alan | Tip | Türetme |
|---|---|---|
| `precondition` | JSON | Dizinin ilk çağrısının, dizi içinde üretilmeyen argümanları |

Ön koşul zaten suç atfının ikinci kapısında kullanılıyor
(`06-skill-language.tr.md`): imza doğru ama ön koşul sağlanmıyorsa hata modelin,
becerinin değil.

## 5. Son koşul

**Bu alan bugüne kadar tanımsızdı; şartnamenin eksik olan tek alanıydı.**

### Tanım

> Son koşul, beceriyi destekleyen epizotlarda **gözlenen durum farklarının
> kesişimi**: her destekleyen epizotta değişen şey.

| Alan | Tip | Türetme |
|---|---|---|
| `postcondition` | JSON | `supporting_episodes` üzerindeki durum farklarının **şekil** kesişimi: `{"app.Model": "+" \| "-"}` |

Mekanik, elle yazılamaz, ve mevcut enstrümantasyonu kullanıyor. Durum farkı
zaten her adımda ölçülüyor ve `steps.state_change` sütununda duruyor
(`src/zihin/state_probe.py`). Biçimi `{"app.Model": işaretli fark}`; boş sözlük
"ölçüldü, değişim yok" demek, NULL "ölçülmedi" demek, ve ikisi ayrı.

### Neden bu tanım

Üç yerde iş görüyor ve üçü de bugün karşılığı olmayan bir boşluğu dolduruyor.

**Yürütme sonrası doğrulama.** Hiçbir API hata döndürmese bile son koşul
tutmuyorsa beceri başarısızdır. Bu tam olarak beşinci kategorinin — *sessiz boş
başarı* — yakaladığı arıza (`07-failure-taxonomy.tr.md`): ajan hatayı işlemi
etkisizleştirerek düzeltiyor ve dışarıdan temiz görünüyor. O kategori bugün
doğrulayıcıya kadar hiçbir yerde alarm üretmiyor, ve ölçülen epizotlarda en
yetenekli modelin baskın arıza biçimi oydu (K-36). Son koşul onu beceri
düzeyinde, doğrulayıcıyı beklemeden görünür kılıyor.

**Getirmede alaka.** Sembolik eşleşme kullanan getirici (`03-architecture.tr.md`)
görevin hedefiyle eşleşen son koşulu taşıyan beceriyi daha ilgili sayabiliyor.
Bu, gömme benzerliği getirmeden alakayı artırmanın bir yolu, yani reddedilen
yolu geri getirmiyor.

**Düşürme kuralı.** Son koşulunu sık tutmayan beceri düşüyor. Bu ölçüt suç
atfının üçüncü kapısını tamamlıyor: üçüncü kapı API hatası sayıyor, son koşul
ise hatasız başarısızlığı sayıyor.

### Bilinen sınır: güncelleme görünmüyor

Durum farkı tespiti **satır sayımına** dayanıyor. Ekleme ve silme görünüyor,
**güncelleme görünmüyor**: satır sayısını değiştirmeyen bir `PATCH` sondaya
görünmez (`state_probe.py`, S-35).

Dolayısıyla son koşul da aynı biçimde eksik olacak. Yalnız alan düzeyinde
değişiklik yapan bir beceri boş son koşul üretecek ve doğrulaması, alaka katkısı
ve düşürme ölçütü o beceride çalışmayacak.

**Bu, yazma kümesini sınırlayan kör noktanın aynısı.** İki mekanizma aynı
enstrümantasyona dayanıyor ve aynı yerde kör. K-41'in ampirik yarısı için
planlanan ikinci katman — epizot kapanışında AppWorld'ün kendi
`model_hashes.json` çıktısı — buradaki körlüğü de kapatır; ikisi tek çözümle
kapanıyor.

### Kesişim ne üzerinde alınıyor: **şekil**, büyüklük değil

Tanım "durum farklarının kesişimi" diyor. Durum farkı `{model: işaretli fark}`
biçiminde, yani kesişim üç şekilde alınabiliyor:

| Okuma | İddia | Örnek |
|---|---|---|
| Sıkı | (model, tam fark) | `{"simple_note.Note": 1}` |
| Gevşek | yalnız model adı | `{"simple_note.Note"}` |
| **Şekil** ✅ | (model, işaret) | `{"simple_note.Note": "+"}` |

**Şartname şekil okumasını alıyor, ve gerekçesi ölçüm değil, dilin kendi
tasarımı.**

Sıkı okuma beceri dilinin parametreleştirmesiyle çelişiyor. Serbest parametre,
becerinin farklı girdilere uygulanabilmesi için var
(`06-skill-language.tr.md`). N alıcıya mesaj gönderen bir beceride fark büyüklüğü
N ile değişir, dolayısıyla sıkı okuma o beceride **hiçbir** destekleyen epizotta
tutmaz ve kesişim boş çıkar. Bu bir ölçüm sorusu değil: serbest parametre
tanımı gereği değişiyorsa, ona bağlı büyüklük de tanımı gereği değişiyor.

Şekil okuması iddia edilebilir olanı iddia ediyor: **hangi modeller değişti ve
hangi yönde — ekleme mi, silme mi.** Büyüklük, becerinin serbest parametresi
varsa serbest değişken; sabit bir iddia olarak yazılamaz.

Üç kullanımın üçü de şekil düzeyinde çalışıyor. Doğrulama için `Note` sayısının
artmış olması yeterli — sessiz boş başarıda hiç artmıyor. Alaka için hangi
modelin hangi yönde değiştiği ayırt edici. Düşürme için "artması gerekirken
artmadı" sayılabilir bir arıza.

### Ölçüm neyi söyleyecek: üç yorum, sonuç görülmeden ilan ediliyor

Büyüklüğün destekleyen epizotlarda sabit olup olmadığı madde 3'te ölçülecek.
Sonucun üç olası hâli ve her birinin ne anlama geldiği **şimdiden** yazılıyor,
sonra seçmek olmasın diye.

1. **Büyüklük bütün madencilenmiş becerilerin destekleyen epizotlarında
   sabitse** → sıkı okuma geri gelir. Şekil okuması gereksiz bir zayıflatma
   olurdu ve daha güçlü iddia bedelsiz elde edilebiliyor demektir.

2. **Değişiyor ve değişim bir serbest parametreyi izliyorsa** → şekil okuması
   doğrudur ve **sebep parametredir**. Beklenen hâl bu; yukarıdaki tasarım
   argümanı tam olarak bunu öngörüyor.

3. **Değişiyor ama hiçbir parametreyi izlemiyorsa** → durum farkı
   enstrümantasyonu gürültülüdür ve bu **ayrı bir sorundur**. Son koşulun
   okuma düzeyiyle ilgisi yok; çözümü de burada değil, sondanın kendisinde.

Üçüncü hâl gerçekleşirse son koşul mekanizmasının tamamı askıya alınır: gürültülü
bir ölçüme dayanan bir düşürme kuralı iyi becerileri düşürür.

### Ölçülmüş bağlam

Kayıtlı 3909 adımda:

| | |
|---|---|
| Durum değişimi gösteren adım | **28** (%0,7) |
| Değişen farklı model | 18 |
| Aynı modelde birden fazla büyüklük görülen model | **9** (18'in yarısı) |
| Değişimin geçtiği uygulamalar | venmo 17, todoist 12, splitwise 6, phone 4, spotify 4, gmail 3, file_system 1 |

İki uyarı, ikisi de sayının kendisinden önemli. Bu sayı **adım düzeyinde** ve
farklı işlemleri karıştırıyor; asıl soru aynı becerinin destekleyen
epizotlarındaki sabitlik ve o ancak beceriler üretildikten sonra sorulabiliyor.
Ve %0,7'lik değişim oranı bu korpusun ağırlıklı olarak salt okuma olmasından
geliyor — kalkanın sıfır engelleme oranıyla **aynı sebep**, aynı korpus özelliği.

`supervisor` durum farklarında hiç görünmüyor, yani `state_probe` ile
`allowed_apps` içindeki altyapı listelerinin farklı olması son koşulu
kirletmiyor.

## 6. Beklenen tasarruf

| Alan | Tip | Türetme |
|---|---|---|
| `observed_steps` | INTEGER | Gövdenin oluşumlarda kapladığı adım sayısı, medyan |
| `expected_saving` | INTEGER | `(observed_steps − 1) × support` |
| `expected_saving_calls` | INTEGER | `(body_length − 1) × support`, tanı amaçlı |

**Birim model çağrısı, API çağrısı değil.** Bu projenin birincil metriği model
çağrısı, bir adım bir model çağrısı, ve beceri tek adımda çağrılıyor. Dolayısıyla
tasarruf **gözlenen adım sayısı** eksi bir çarpı destek.

`06-skill-language.tr.md` bunu "uzunluk eksi bir" diye yazıyordu ve ajan çağrıları
zaten paketlemişse fazla sayıyor. Ölçüldü: `spotify.auth/token` becerisi üç
çağrıyı iki adımda yapıyor, yani çağrı tabanlı formül tasarrufu 7'den 14'e
çıkarıyor. Dört beceriden üçünde iki sayı aynı, birinde iki katı fark var.

Çağrı tabanlı sayı tanı olarak yanında duruyor: iki sayının farkı, şartnamenin
yanlış birimi saydığını gösteren şeyin kendisi.

### Kestirim bir alt sınır, ve okunuşu bunu gerektiriyor

Gözlenen adım sayısı sınır kontrolünün yörüngelerinden geliyor. **Zayıf bir
yerel model aynı çağrıları daha çok adımda yapar**, yani becerinin ona değeri bu
sütunun söylediğinden yüksek olur.

Becerilerin yardım etmesi beklenen modeller tam da o zayıf modeller. Dolayısıyla
buradaki her sayı, hedef kitlesi için bir **alt sınır**. Pilot raporunda bu
cümleyle okunacak.

### Eşik uygulanmıyor, saklanıyor

Değer eşiğinin sayısı seçilmedi (K-50) ve **pilottan önce seçilmeyecek**: korpus
yirmi görev, kestirim korpusa özgü, ve bir eşik seçmek küçük örnekleme uydurmak
olur. Sütun saklanıyor, eşik okuma anında uygulanıyor, duyarlılık ızgarası
`experiments/preregistration.md` içinde. Getirici dört becerinin dördünü de
alıyor ve duyarlılık notu yanında duruyor.

## 7. Sicil

| Alan | Tip | Türetme |
|---|---|---|
| `invocations` | INTEGER | Kaç kez çağrıldı |
| `blamed_failures` | INTEGER | Suç atfının **üçüncü** kapısından geçen hatalar |
| `postcondition_misses` | INTEGER | API hatası yokken son koşulun tutmadığı çağrılar |
| `model_failures_gate_1` | INTEGER | Çağrı beceriye hiç ulaşmadı |
| `model_failures_gate_2` | INTEGER | İmza doğru, ön koşul sağlanmıyor |

İlk iki kapının sayaçları ayrı tutuluyor ve düşürme kuralını beslemiyor. Kapılar
olmasaydı model hataları beceriye yazılır ve iyi beceriler kütüphaneden düşerdi.

`postcondition_misses` düşürme kuralına giren **ikinci** sayı.

---

## Değişmezler

Derleyicinin çıktısının sağlaması gerekenler. Doğrulama kapısı madde 3'te
yazılacak ve bunları sınayacak.

1. `support == len(supporting_tasks)` ve `supporting_tasks` tekil.
2. `len(calls) >= 2` — uzunluk alt sınırı iki.
3. `signature` ile `bound_arguments` ayrık: bağlı bir argüman imzada olamaz.
4. `constants` içindeki her değerin görev sayısı, sabit ilan etme eşiğinden
   küçük olamaz.
5. `constants` içinde dinamik tip kara listesinden bir değer olamaz.
6. `postcondition`, `supporting_episodes` üzerinden yeniden hesaplandığında aynı
   çıkıyor — türetilmiş projeksiyon olma şartı (`03-architecture.tr.md`).
7. Boş `postcondition` geçerli bir değer ve NULL'dan farklı: birincisi "kesişim
   boş", ikincisi "hesaplanmadı".
8. `postcondition` değerleri yalnız `"+"` ve `"-"`; sayı yazılamıyor. Şekil
   okuması bir karar, kodun kaza eseri ürettiği bir biçim değil, ve büyüklük
   sızarsa iddia sessizce sıkı okumaya döner.
9. `kind == "skill"` olan her kayıtta `effect_suffix` boş değil, ve
   `kind == "discovery_prefix"` olan her kayıtta boş. Boş etki sonekli bir kayıt
   kütüphaneye ya da getiriciye ulaşamıyor.

## Yazılmamış olanlar

Değer eşiği, sabit ilan etme eşiği ve boşluk kısıtının sayıları burada yok;
karar kuralları ön kayda, sayıları kurulum sonrasına ait (K-50).

Son koşulun okuma düzeyi **karara bağlandı** — şekil — ve gerekçesi tasarımdan
geliyor, ölçümden değil. Madde 3'te ölçülecek olan şey kararın kendisi değil,
üç yorumdan hangisinin gerçekleştiği; üçü de yukarıda önceden yazıldı.
