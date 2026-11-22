# Deney tasarımı

## Neden dürüst ölçmek zor

Bu tasarımın büyük kısmı dört hata sınıfından kaçınmak için var. Bir iş yaparken
bunlar kontrol ediliyor.

**Tasarımın sonucu belirlediği yerler.** Bir karşılaştırmada hangi ekseni
sabitlediğine göre kazanan değişiyorsa, o karşılaştırma hiçbir şey ölçmez.

**Aynı anda birden çok değişkenin değiştiği yerler.** Bir paket test edilip tek
bir mekanizmaya atfediliyorsa sonuç yorumlanamaz.

**Totolojik metrikler.** Ölçülen fark tanımdan çıkıyorsa sonuç kendiliğinden
doğrudur ve bilgi taşımaz.

**Yamaların ürettiği yeni karıştırıcılar.** Bir düzeltme başka bir yerde yeni bir
karıştırıcı yaratabiliyor; baskı altında yapılan yamalar genelde bunu yapıyor.
Bu dördüncüsü sonradan eklendi.

## Koşullar

**Ek, 28 Ağustos 2026: altı koşulun biri yazılmadı.** `naive_compiler` koşulu
ölçütü koştuktan sonra deneye **yazılmadı** (K-145). Ölçüt koşudan önce ilan
edilmişti: naif madenci aynı korpusta derleyicinin dört becerisinin dördüne de
ulaştı, kaçırdığı 0 ve fazladan bulduğu 0. Aşağıdaki tablo özgün ilan olarak
duruyor; koşacak koşul sayısı **beş**.

Altı koşul. Her biri tek bir şeyi izole ediyor.

| Koşul | Beceri kartları | Hata kartları | Ne izole ediyor |
|---|---|---|---|
| Taban | yok | yok | referans noktası |
| Alakasız getirme | alakasız | alakasız | bağlam hacmi |
| Sadece beceriler | gerçek | alakasız | beceri içeriği |
| Sadece hatalar | alakasız | gerçek | hata içeriği |
| İkisi birden | gerçek | gerçek | ikisinin birlikte etkisi |
| Naif derleyici | naif madencilik | alakasız | madencilik kalitesi |

**Alakasız getirme** koşulundaki kartlar gerçek kart biçiminde ve uzunluğunda,
başka uygulamalardan alınmış alakasız kartlar. Kazancın bağlam hacminden gelip
gelmediğini ölçüyor.

**Naif derleyici** koşulu aynı atomikliği, aynı kart biçimini, aynı getiriciyi
ve aynı token bütçesini kullanıyor. Tek fark madencilik kalitesi. Naif taraf
sabit uzunlukta n-gram; kapalı örüntü yok, boşluk kısıtı yok, argüman kuralı
"değişen her şey serbest parametre". Sadece beceriler koşuluyla eşleşiyor.
Cevapladığı soru: bizim derleyicimiz naif bir derleyiciden iyi mi.

### İki kritik kontrast

Bozulursa analiz planının tamamı çöker.

1. **Taban ile alakasız getirme** arasındaki fark saf bağlam hacmi.
2. **Sadece beceriler ile alakasız getirme** arasındaki fark saf içerik.

### Kart sayısı ve dolgu

Kart sayısı **göreve göre** belirleniyor, koşula göre değil.

Her görev için önce getirme koşuluyor; bulunan uygun kart sayısı o görevin dolgu
payını belirliyor; kart taşıyan beş koşul aynı sayıda kart alıyor. Taban sıfır
kart alıyor.

Mekanizmalı koşullara da dolgu konuyor. Konmasaydı az kart alan koşulun bağlamı
kısalır ve ölçülen şey mekanizma değil bağlam uzunluğu olurdu.

## Model ekseni ve kontroller

### Ana eksen şartları

Dördü birlikte tutulmalı:

1. **Tek aile.** Boyut değişirken eğitim hattı, sözcük dağarcığı ve talimat
   biçimi sabit kalmalı. Aileler karışırsa eksende iki değişken birden değişir ve
   eğrinin yönü hiçbir şeye atfedilemez.
2. **En az üç yoğun boyut**, hepsi Q4_K_M ile 32K bağlam ve q8_0 KV altında
   8 GB'a sığmalı.
3. **Akıl yürütme modu olmayan ya da tamamen kapatılabilen.**
4. **Ollama'da mevcut ve instruct ayarlı.**

**Ölçülmüş referans:** `qwen2.5-coder:7b` Q4_K_M kartta 5,16 GiB; 32K q8_0 KV bir
slot için yaklaşık 0,9 GiB; 7B yüklüyken gerçek boş VRAM 1,74 GiB. Ağırlık
tavanı kabaca 5-6 GiB.

### İki kontrol, eksenin parçası değil

**Aile kontrolü.** Ana eksenden farklı bir aile, ana eksenin en büyük noktası
bandında, **tek nokta**. Sorusu: bu etki bu aileye mi özgü. Ana eksene alınamaz,
alınırsa rolü yok olur. Ön koşulu da geçmesi gerekiyor.

**Sınır kontrolü.** DeepSeek V4 Flash 0731, API üzerinden, düşünme kapalı.
Sorusu: kazanç küçük modelin eksiğini mi yamıyor.

İkisi de ayrı raporlanıyor.

### Elenenler

| Model | Sebep |
|---|---|
| Qwen2.5-Coder 14B ve üstü | 8 GB'a sığmıyor |
| Kimi K3 | akıl yürütme kapatılamıyor |
| GLM-5.2 | yalnız High ve Max modlarında |

Son ikisi sınır kontrolü adayıydı, ana eksen adayı değildi.

### Sabitler

Kuantalama tümünde Q4_K_M, KV cache q8_0, bağlam 32K, sıcaklık sabit ve sıfırdan
büyük, seed epizot başına.

**Sıcaklık sıfır reddedildi.** Sıfırda seed anlamsızlaşır ve tohumlar arası
yayılım ölür, oysa bütün istatistik planı o yayılıma dayanıyor. Ayrıca sıfırda
ajan başarısız bir çağrıyı sonsuza kadar tekrarlar.

**Seed yalnız görev kimliği ve tohum indisinden türüyor.** Model ve koşul
girmiyor. Girerse eşleştirilmiş tasarım bozulur: aynı görev ve aynı tohum indisi
her modelde ve her koşulda aynı seed'i vermeli.

**Model yükleme rejimi soğuk**, her epizottan önce boşaltma. Isınmış rejim tek
bir durum değil, soğuk rejim ölçülmüş biçimde tekdüze. Bedeli toplam koşunun
yaklaşık yüzde altısı.

## Metrikler

### Birincil

**Görev başına model çağrısı.**

**Totoloji itirazının cevabı.** Bu ortamda ajan durumlu Python yazıyor ve taban
da tek turda birden çok API çağırabiliyor. Beceri, paketleme imkânı vermiyor;
doğrulanmış paketi önceden veriyor. Kazanç, ajanın hangi çağrıların hangi
sırayla geleceğini keşfetmek için harcadığı turlardan geliyor.

**Ham API çağrısı sayısı birincil değil**, çünkü bir beceri çağrısını tek adım
saymak sonucu totolojik kılar.

### Zorunlu tanı metriği

**Model çağrısı bölü başarılı API çağrısı.**

Yorumu ön kayıtta yazılı: oran hareket etmiyorsa kazanç paketlemeden geliyor,
hareket ediyorsa israfın azalmasından da geliyor.

### İkincil

Başarı oranı, girdi tokenı, çıktı tokenı, kalkan ihlal sayısı, DSL kapsama
oranı, kapsama oranı, kesinti oranı, taşma oranı, kısmi yürütme oranı, geçersiz
beceri çağrısı, yanlış bağlamda çağrılma, çağrı tamamlama, kaçırılmış kullanım,
kategori 4 oranı.

**"İki metriğin birlikte hareket etmesi" kuralı düştü**, çünkü görev uzunluğuyla
etkileşiyor: uzun epizotlarda ikisi birlikte düşüyor, kısa epizotlarda kart
maliyeti baskın gelip token artıyor. İkisi de koşulsuz raporlanıyor ve görev
uzunluğuna göre ayrıştırılıyor.

### Tanı metriği olarak dereceli skor

`no_op_fail` etiketli testlerin geçilen oranı. **Tanı metriği; ikincil sonuç
değil.** Birincil metriğe ve yanlışlama kapılarına girmiyor.

Veriyi gördükten sonra doğdu ve bu açıkça yazılıyor: kurulum aşamasında, ikili
başarı her yerde sıfırken ayrım gücü olan tek nicelik olarak türetildi. Bir
taramada kullanılacaksa tanımı taramadan önce yazılıp o kullanım için önceden
ilan ediliyor.

## Analiz planı

Karşılaştırma **görev bazında eşleştirilmiş**.

### Estimand

Bütün kapsanan görevlerde. Çözülmeyen epizotlar adım tavanında **sansürlenmiş
gözlem** olarak giriyor, gerçekte kaç adım sürdüklerine bakılmaksızın.

Duyarlılık analizi tavanın **1,5 ve 2 katıyla** tekrarlanıyor.

"İki koşulun da çözdüğü" analizi ikincil ve adı **koşullu verimlilik**.

### Kestirim

Birincil kestirim **tavana kadar kısıtlanmış ortalama**, güven aralığı görev
kümesiyle **bootstrap**. **Wilcoxon** sansürsüz alt kümede sağlamlık kontrolü.

### İki nicelik karıştırılmıyor

**Tavana çarpma oranı** bir ölçüm artefaktı. Yüzde onun altında kalmalı ve tavan
çarpanı buna göre seçiliyor.

**Sansür oranı** doğrulayıcı hükmüne dayanıyor ve bir sonuç. Yüzde on kuralı
buna uygulanmıyor; uygulansaydı tabana yüzde doksan başarı şartı konmuş olurdu.

Sansür sonlandırma sebebine göre değil doğrulayıcı hükmüne göre sayılıyor.
Doğrulayıcının geçirmediği her epizot sansürlü: tavana çarpsın, durma kuralıyla
kapansın ya da ajan tamamlandı bildirsin. Sonlandırma sebebi ayrı bir tanı alanı.

### Mekanizma etkisi

Çıkarıcı kontrolle hesaplanıyor: mekanizma koşulunun tabana göre kazancından,
alakasız getirme koşulunun tabana göre kazancı çıkarılıyor, görev bazında
eşleştirilmiş.

Hacim etkisi ile içerik etkisinin **toplanabilir** olduğu varsayılıyor ve bu
varsayım kurulum aşamasında sınanıyor.

### Birincil karşılaştırma tek hücre

Mekanizmalar açık ile taban, model çağrısı metriğinde, ana eksenin en büyük
yerel noktasında, görülmemiş alt kümede, iki taraflı.

**Geri kalan her şey keşifsel:** diğer modeller, diğer bölme, diğer koşul
çiftleri, iki kontrol noktası, bütün ikincil metrikler.

**Ek, 25 Eylül 2026.** "Ana eksenin en büyük yerel noktası" ifadesi ön kayıt
A.2'nin 25 Eylül 2026 ekiyle güncellendi: birincil hücrenin modeli
`qwen2.5-coder:32b-instruct-q4_K_M`, ve "yerel" şartı artık karşılanmıyor. Seçim
keşifsel, `Y-1`'in hükmü onaylayıcı (`K-169`).

### Ezberleme kapısı

Dağılım içi test kümesi ikiye ayrılıyor: eylem dizisi biriktirmede görülmüş ve
görülmemiş görevler. Bölme ölçütü biriktirme kaydındaki **normalize eylem
dizisiyle birebir eşleşme**.

Kapı: görülmemiş görevlerdeki kazancın görülmüş görevlerdeki kazanca oranı,
**eşik yarım**.

### Zorluk bölmesi

Ayrı bir ölçüm: uygulamalar arası aktarım. Beceriler için sıfıra yakın sonuç
önceden yazılı; hata indeksi için sıfırdan farklı çıkabilir, çünkü hata
kalıpları soyut olabilir.

### Bölme kullanımı

Biriktirme train, dev ve kullanılmayan normal test görevlerinden. Değerlendirme
normal testten, örneklem biriktirmede temsil edilen uygulamalarla sınırlı.

**Zorluk bölmesi bütün ve dokunulmamış kalıyor**, biriktirme oradan yapılmıyor.
Elimizdeki tek gerçekten görülmemiş uygulama verisi o.

**Kurulum sırasında dokunulan görevler değerlendirme örnekleminden çıkarılıyor**,
biriktirme havuzunda kalabilirler. Dokunulan görev kimlikleri listelenip ön kayda
yazılıyor.

### Normalizasyon ikincil

Ölçülen adım sayısından görev başına indirilemez taban çıkarılıyor, kalan israf,
iki koşulun israfı karşılaştırılıyor. Taban `metadata.num_api_calls` alanından.

Birincil metrik **ham eşleştirilmiş fark** kalıyor, çünkü normalizasyon bir
modelleme kararı ve itiraza açık.

## Kapılar

### Ön koşul kapısı

Taban koşulu ayrılmış kümede ilan edilen asgari başarı oranını tutturamazsa
**deney hipotezi test edememiştir ve mekanizma sonuçları raporlanmaz.**

Kapı bağlayıcı olmayan bütçe altında ölçülüyor; kapı koşusunda kodsuz adım oranı
raporlanıyor.

**Bu kapı bir kez ateşledi: 11 Ağustos 2026.** Qwen2.5-Coder 1,5B, 3B ve 7B
AppWorld'ün otuz görevlik tabakalanmış örnekleminde hiçbir görevi çözmedi. Üç
tabakalama denendi ve hiçbiri ölçülebilir bant açmadı: referans uzunluk, güçlü
modelin çözdüğü alt küme, uygulama kümesi.

12 Ağustos 2026'da sınır kontrolü sıfırların düzenekten değil modelden geldiğini
gösterdi: aynı otuz görevde DeepSeek V4 Flash 0731 bizim hattımızda 20/30,
yayımlanmış gpt-4o koşusu 15/30.

Ateşlemenin sonucu: model ailesi yeniden seçiliyor.

### Yanlışlama kapıları

1. Mekanizmalar ayrılmış görevlerde model çağrısı sayısını düşürmüyorsa
   **hipotez desteklenmemiştir.**
2. Kazanç görülmemiş görevlerde görülmüş görevlerdeki kazancın yarısının altına
   düşüyorsa **ezberleme doğrulanmıştır.**
3. Kapsama oranı yüzde yirmi beşin altındaysa bu "test edemedik" değil,
   **sembolik getiricinin bu ortamda ilgili deneyim bulamadığı bulgusudur.**

### Mekanizma başına terk kriteri

Kapsama yeterliyken ve indeks ilan edilen asgari boyuttayken sadece hatalar
koşulu etki göstermiyorsa, **hata indeksi mekanizma olarak terk edilir, yeniden
ayarlanmaz.** Aynısı beceri derleyicisi için.

### Ayar bütçesi

Kurulum verisini gördükten sonra kaç parametre revizyonuna izin verildiği
önceden yazılıyor. **Bütçe tükendikten sonra olumsuz sonuç parametreler hakkında
değil tasarım hakkında bir sonuçtur.**

Sayı ve bugüne kadar tüketilen revizyonların listesi ön kayıtta
(`experiments/preregistration.md`).

### Ölçek ekseni yorum tablosu

Dört olası şekil için yorum ön kayda giriyor: düz, düşen, yükselen, ters U.
**Sonradan yorum yasak.**

Önceden ilan edilen her yorum tablosu bir dördüncü dal da taşıyor: gözlenen desen
satırların hiçbirine uymuyorsa tablo yanlıştı, sonuç yorumsuz raporlanır, ve
tablonun neyi kaçırdığı yazılır (K-104).
