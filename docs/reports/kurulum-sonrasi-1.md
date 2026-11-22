# Kurulum sonrası 1 — S-16 bağlandı, yükleme protokolü kilitlendi

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

Kurulum altı aşamayla kapandı. Bu iş zincirin ilk halkası: K-50'nin birinci
maddesi ve K-21'in iki şartı.

## Zincirin kapısı: eylem düzeyi yanıt verisi

`src/zihin/api_capture.py` AppWorld'ün `Requester` sınıfının `_get`, `_post`,
`_patch`, `_delete` ve `_put` metotlarını sarmalıyor. Yakalanan her çağrı istek
bilgisini, durum kodunu ve yanıt gövdesini taşıyor.

Kaydedici artık eylemleri buradan yazıyor. `actions.result_status` ve
`actions.error_class` sütunları S-05'ten beri boştu, şimdi doluyor.

### Kayıt sırası testle sabitlendi

Asıl kural burada bir davranış değil, bir sıra. `Requester._get` ve kardeşleri
dönmeden önce `raise_if_failure` çağırıyor ve başarısız yanıtta istisna
fırlatıyor. Kayıt istisnadan sonra alınırsa başarısız çağrılar hiç
kaydedilmiyor.

Bu tam olarak bir kez oldu ve ölçüm yeşil göründü: ilk sondada yedi çağrının
yedisi de 200 raporlandı, oysa ikisi başarısızdı.

`tests/test_api_capture.py` sırayı sabitliyor. Sahte bir `Requester` kullanıyor,
yani AppWorld kurulumu istemiyor ve CI'da koşuyor. Sekiz test var; biri
doğrudan "başarısız çağrı istisna yayılmadan önce kaydediliyor mu" sorusunu
soruyor, biri de sarmalayıcının istisnayı yutmadığını denetliyor.

### İki kaynak birlikte tutuluyor ve ilk işi bir arıza yakalamak oldu

Yakalayıcının saydığı çağrı ile `api_calls.jsonl` deltasının saydığı çağrı adım
başına karşılaştırılıyor. Tek kaynağa geçmedim, çünkü yakalayıcının bir çağrıyı
kaçırması ya da fazladan sayması sessiz kalırdı.

İlk determinizm koşusunda karşılaştırma tuttu: yakalayıcı adım başına 2, günlük
1 çağrı gördü. Toplamda 38'e 19.

Sebep, yakalayıcının çerçevenin kendi iç çağrısını da sayması. Her adımda
AppWorld `/supervisor/active_task` çağırıyor; o çağrı ajanın eylemi değil ve
`api_calls.jsonl`'e girmiyor. Yani her adıma hayalet bir eylem ekleniyordu.
Üstelik hayalet eylem 200 dönüyordu, ajanın gerçek çağrısı ise 401. Hata
indeksi bu veriyle beslenseydi her adımda başarılı bir çağrı görecekti.

Düzeltmeyi bayrağa değil davranışa bağladım. Yakalayıcı artık AppWorld'ün kendi
istek sayacına bakıyor: sayaç büyüdüyse çağrı ajanın eylemi sayılıyor. `track`
bayrağına güvenmek de bir varsayım olurdu. Düzeltmeden sonra iki kaynak birebir
tutuyor.

Üç test eklendi: iç çağrı yakalanmıyor, izlenmeyen başarısız çağrı da
yakalanmıyor, ve yakalanan sayı çerçevenin saydığına eşit.

Düzeltmeden sonra 1.5B ölçümü yeniden koşuldu: on epizotta da yakalanan 19,
günlükteki 19, hiç ayrışma yok. Determinizm hükmü değişmedi, çünkü yörünge
özetleri `environment_io.md` üzerinden hesaplanıyor ve kayıt katmanından
etkilenmiyor.

## K-21'in ikinci şartı: boşaltma ölçülüyor

`unload_model` artık boşaltma isteğinden sonra `/api/ps` üzerinden kontrol
ediyor. Model hâlâ yüklü görünüyorsa hata fırlatıyor ve epizot başlamıyor.

Protokol iddia değil ölçüm. Boşaltma sessizce başarısız olsaydı epizot ısınmış
rejimde başlar, rejimler karışır ve fark edilmezdi.

## K-21'in birinci şartı: iki modelde tuttu, birinde tutmadı

Model başına on soğuk epizot, aynı görev (`82e2fac_1`), aynı seed
(2773802488). Her epizottan önce model boşaltıldı ve boşaldığı doğrulandı.
Aynı koşuda ikinci bir tohumla tek epizot daha koşuldu.

| Model | Tekdüze | Farklı yörünge | Boşaltma | İkinci tohum farklı |
|---|---|---|---|---|
| 1.5B | evet | 1 | 10/10 doğrulandı | evet |
| 3B | evet | 1 | 10/10 doğrulandı | evet |
| 7B | **hayır** | **2** | 10/10 doğrulandı | evet |

7B'nin on koşusundan dokuzu `6fb9c5fc4d8d62b2`, biri `a224f9753ae5c0e7` verdi.
Ayrışan koşu 12 adım yerine 6 adımda bitti. API çağrısı sayısı onunda da 5,
yani ayrışan koşu aynı eylemleri üretip erken sonlandı.

Boşaltma her üç modelde de her epizotta doğrulandı, yani ayrışmanın sebebi
rejim karışması değil.

**Bu K-48'in tetiklendiği durum.** Kural sonuç görülmeden yazılmıştı: on
epizotluk sınama düşerse determinizm hedefinden vazgeçilip yükleme durumu
kaydedilen ortak değişkene indirilir. Sınama 7B'de düştü.

Bir belirsizlik var ve karar vermiyorum: K-48 kuralın model başına mı yoksa
tümü için mi uygulanacağını söylemiyor. İki model tekdüze, biri değil. Kuralı
tümü için uygulamak, tekdüzeliği ölçülmüş iki modelde de determinizmden
vazgeçmek demek; model başına uygulamak ise ölçek ekseninin üç noktasının
farklı analiz varsayımları taşıması demek. İkisi de bedelli.

Ayrışma oranını yükseltmek için tekrar koşmadım. Şart "hepsi birebir aynı
çıkmalı" diyordu ve çıkmadı; tekrarlayıp daha iyi bir sonuç aramak, ölçümü
sonuca göre seçmek olurdu.

**Yan bulgu.** 3B on epizodun onunda da sıfır API çağrısı yaptı ve yirmi adım
tavanına dayandı. S-14 ölçek ekseninin en küçük noktası için açılmıştı; 3B de
aynı yerde. 7B beş çağrı yapıp on iki adımda bitirdi, yani üç nokta içinde
yalnız o taban etkisinin dışında.

## Karşılaştığım sürprizler

### Sunucu betiği ayaktaki sunucuyu düşmüş sanıyordu

Determinizm koşusu ilk denemede bağlantı zaman aşımıyla düştü. Sebep sunucunun
kapalı olmasıydı, ama onu yeniden başlatmaya çalışınca betik "sunucu ayağa
kalkmadı" dedi ve çıktı.

Oysa sunucu ayaktaydı. Betik başlattıktan sonra sekiz saniye bekleyip tek bir
sağlık yoklaması yapıyordu; bu makinede GPU keşfi 23 saniye sürüyor. Log'da
başlangıç 11:03:07, `inference compute` satırı 11:03:30.

Düzeltme sabit bekleme yerine yoklama koymak oldu, ve ikinci bir yoklama daha
eklendi: `inference compute` satırı log'a düşene kadar bekleniyor. Sebebi
ölçümle ilgili; GPU hazır olmadan alınan bir yükleme süresi ölçümü yanıltıcı
olurdu.

Bu, K-49'un altıncı örneği. Betik daha önce "başarılı" raporlamıştı ve o rapor
doğruydu ama yanlış sebeple: o seferki GPU keşfi sekiz saniyeden kısa sürmüştü.

### Prompt yolu eşzamanlılıkta çakışacaktı

Prompt dosyası epizot başına yeniden üretiliyor, çünkü slot içeriği epizoda
göre değişecek. Yol sabitti. Küçük modellerde eşzamanlı epizot koşacak ve iki
epizot birbirinin dosyasını ezecekti.

Ezilme sessiz olurdu: ikisi de geçerli bir prompt okuyup koşmaya devam ederdi
ve fark yalnız sonuçlarda görünürdü. `episode_prompt_path` yolu koşu kimliği,
görev kimliği ve tohum indisinden türetiyor.

## Karara bağlananlar

- **K-21.** Soğuk rejim, iki şartıyla.
- **K-47.** Gereken determinizmin türü: aynı görev, seed, koşul ve model
  dörtlüsünün tekrarında aynı sonuç; tohumlar arası fark kalıyor.
- **K-48.** Tekdüzelik tutmazsa determinizm hedefinden vazgeçilip yükleme
  durumu kaydedilen ortak değişkene indiriliyor. Kural sonuç görülmeden
  yazıldı.
- **K-49.** Bir şeyin çalıştığı görüldüğünde doğru sebeple mi çalıştığı ayrıca
  sorulacak. Altı örneğiyle birlikte kayıtta.
- **K-50.** Kurulum sonrası bağımlılık zinciri ve ön kaydın donma kuralı: kural
  donuyor, sayılar donmuyor.

## K-42 için ölçülmüş taban

Zincirin ikinci maddesi K-42'nin karara bağlanması. Karar sizin ama sayılar
çıkarıldı.

"Değerlendirme örneklemi yalnız biriktirmede temsil edilen uygulamalardan
çekilir" kuralı uygulandığında zorluk bölmesinden ayakta kalan görev:

| Havuz | Uygulama | test_normal | test_challenge |
|---|---|---|---|
| Yalnız train + dev | 5 | 141/168 | 37/417 |
| + test_normal'ın tamamı | 8 | 165/168 | 193/417 |
| Bütün kullanıcı uygulamaları | 9 | 165/168 | 405/417 |

Havuz genişletilmezse zorluk bölmesinin yüzde dokuzu kalıyor.

**Yapısal sorun.** Zorluk bölmesini en çok açan uygulama `amazon`, tek başına
185 görev getiriyor. Ama `amazon` train'de, dev'de ve test_normal'da hiç
geçmiyor. Havuza girmesinin tek yolu zorluk görevleri üzerinde biriktirme
yapmak, o da görülmemiş görev özelliğini bozar.

Biriktirmeyle erişilebilen tavan sekiz uygulama ve 193/417. `amazon`'a dokunan
212 zorluk görevi, kural korunursa değerlendirme örnekleminin dışında kalıyor.
Diğer üçünün katkısı: `gmail` +150, `todoist` +3, `splitwise` +0.

Sayılar vekil ölçümden geliyor, tam isabet yüzde 75,5. Yön güvenilir çünkü
vekil `amazon`, `splitwise` ve `todoist` için hiç fazladan sayma yapmadı.

## Sırada

K-42'nin karara bağlanması, sonra önyükleme biriktirmesi. Ayrıca K-48'in model
başına mı yoksa üç nokta için birden mi uygulanacağı.

## Yerel-yalnız kontroller

Son koşu: `2026-08-11T12:26:24+03:00`, commit `1b72bf7`. On dört test geçti,
99 test elendi.
