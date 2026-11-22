# AppWorld olguları

Aşama 2'nin çıktısı. Yedi soru ölçülerek cevaplandı, sekizinci madde kod
yazmadan incelendi. Tahmin yazmadım. Ölçemediğim yere ne ölçemediğimi ve neden
ölçemediğimi yazdım.

Ölçüm ortamı: AppWorld commit `a072b7a`, paket sürümü `0.2.0.dev0`, veri sürümü
`0.2.0`. Model gerektiren ölçümler `qwen2.5-coder:1.5b-instruct-q4_K_M` ile
alındı.

---

## 1. Bölmeler ve görev sayıları

Dört bölme var. Adları `data/datasets/` altındaki dosya adlarından, olduğu gibi:

| Bölme | Görev |
|---|---|
| `train` | 90 |
| `dev` | 57 |
| `test_normal` | 168 |
| `test_challenge` | 417 |
| **toplam** | **732** |

`data/tasks/` altında 733 dizin var. Fazlalık `_base_` adlı dizin ve hiçbir
bölmede geçmiyor, yani görev değil.

Sayılar `load_task_ids()` çıktısıyla da eşleşiyor. Bölme dosyalarını `wc -l` ile
saymak birer eksik veriyor, çünkü dosyalar sonda satır sonu taşımıyor.

## 2. Zorluk bölmesi ne içeriyor

**Cevap: ikisi birden, ama asıl fark görülmemiş uygulamada.** Zorluk bölmesi
hem eğitimde hiç geçmeyen uygulamalar içeriyor hem de görev başına daha çok
uygulamaya ve daha çok API'ye dokunuyor.

Açıklama metnine güvenmedim, saydım. Sayımın iki katı var, biri kesin biri
vekil.

**Kesin taraf.** Görev başına uygulama listesi `ground_truth/required_apps.json`
içinde ve yalnız 147 görevde var: train'in 90'ı ve dev'in 57'si. O 147 görevin
dokunduğu uygulamaların birleşimi beş tane:

| Uygulama | Kaç görevde |
|---|---|
| `spotify` | 78 |
| `phone` | 48 |
| `venmo` | 42 |
| `file_system` | 21 |
| `simple_note` | 15 |

Yani eğitim ve geliştirme bölmeleri, ortamdaki on bir kullanıcı uygulamasının
yalnız beşine dokunuyor. `amazon`, `gmail`, `splitwise`, `todoist` ve `api_docs`
o 147 görevin hiçbirinde geçmiyor.

**Vekil taraf.** Test bölmelerinde `required_apps.json` yok. Görev yönergesinden
uygulama adı çıkaran bir vekil yazdım ve onu referans listesi olan 147 görevde
sınadım. Sonuç: 147 görevin 111'inde küme birebir tuttu, yani yüzde 75,5. Küme
benzerliği (Jaccard) 0,878. Vekil `simple_note`'u altı görevde fazladan saydı,
`phone`'u otuz görevde ve `venmo`'yu üç görevde kaçırdı. Fazladan sayma
listesinde `amazon`, `splitwise` ve `todoist` hiç yok, yani vekil bu üçünü
gördüğünde yanılmıyor.

Vekile göre `test_challenge` görevlerinde `amazon` 171, `gmail` 312,
`splitwise` 9 ve `todoist` 3 kez geçiyor. Dördü de eğitimde bulunmayan
uygulamalar.

**Sayı tarafı, kesin.** `ground_truth/metadata.json` bütün 732 görevde var ve
görev başına uygulama ile API sayısını taşıyor:

| Bölme | uygulama ort. | uygulama medyan | maks | API ort. | API medyan | maks |
|---|---|---|---|---|---|---|
| `train` | 1,40 | 1 | 3 | 8,00 | 8 | 12 |
| `dev` | 1,37 | 1 | 2 | 7,63 | 8 | 10 |
| `test_normal` | 1,62 | 2 | 3 | 8,48 | 8,5 | 17 |
| `test_challenge` | 2,02 | 2 | 6 | 10,55 | 10 | 26 |

Zorluk dağılımı da aynı yöne işaret ediyor:

| Bölme | zorluk 1 | zorluk 2 | zorluk 3 |
|---|---|---|---|
| `train` | 36 | 36 | 18 |
| `dev` | 30 | 24 | 3 |
| `test_normal` | 57 | 48 | 63 |
| `test_challenge` | 72 | 150 | 195 |

**Sınırı.** Test bölmeleri için uygulama adları vekil ölçümden geliyor ve vekil
her dört görevden birinde kümeyi tam tutturamıyor. Uygulama sayıları ve zorluk
dağılımı ise metadata'dan, kesin.

## 3. Referans çözümler

**Cevap: var, ama yalnız 147 görevde.** `appworld download data` varsayılan
kipte inmesine rağmen train ve dev görevleri `full` kipte geliyor.
`metadata.json` içindeki `mode` alanı bunu açıkça söylüyor: 147 görevde `full`,
kalan 585'inde `minimal`.

O 147 görevin `ground_truth/` dizininde şunlar var: `solution.py`,
`compiled_solution.py`, `api_calls.json`, `required_apps.json`,
`required_apis.json`, `generator.py`. Test bölmelerinde bu altı dosyanın hiçbiri
yok.

`api_calls.json` bir liste ve her elemanı `{"method", "url", "data"}` taşıyor.
Referans çözüm başına API çağrısı sayısı:

| Bölme | n | ortalama | medyan | p75 | p90 | p95 | maks |
|---|---|---|---|---|---|---|---|
| `train` | 90 | 51,81 | 38,5 | 70 | 105 | 144 | 244 |
| `dev` | 57 | 56,00 | 34,0 | 71 | 132 | 139 | 214 |
| `train+dev` | 147 | 53,44 | 37,0 | 71 | 125 | 144 | 244 |

`metadata.json` içindeki `num_api_calls` alanını `api_calls.json` uzunluğuyla
147 görevin hepsinde karşılaştırdım, hiçbirinde uyuşmazlık yok. Bu, dördüncü
sorunun metadata üzerinden cevaplanabileceğini gösteriyor.

Bu bulgu `docs/09-limitations.tr.md` içindeki S-02'yi kısmen çürütüyor. Referans
çözümler bakımcı anahtarı olmadan da elimizde, ama yalnız train ve dev için.

## 4. Görev başına API çağrısı dağılımı

Kaynak `metadata.json` ve 732 görevin hepsinde var. Kendi koşularımdan çıkarmama
gerek kalmadı.

| Bölme | n | ortalama | medyan | p75 | p90 | p95 | maks |
|---|---|---|---|---|---|---|---|
| `train` | 90 | 51,81 | 38,5 | 70 | 105 | 144 | 244 |
| `dev` | 57 | 56,00 | 34,0 | 71 | 132 | 139 | 214 |
| `test_normal` | 168 | 33,67 | 30,0 | 40 | 60 | 81 | 130 |
| `test_challenge` | 417 | 46,82 | 25,0 | 40 | 80 | 178 | 649 |
| hepsi | 732 | 45,13 | 27,0 | 45 | 88 | 139 | 649 |

Dikkat çeken şey `test_challenge` bölmesinin biçimi. Medyanı en düşük bölme o
(25), ama kuyruğu en uzun olan da o: p95 değeri 178 ve en yüksek görev 649 API
çağrısı istiyor. Yani zorluk bölmesi ortalama olarak değil, uç noktalarda ağır.
Adım tavanı ve bütçe planlaması bu kuyruğa göre yapılmalı, ortalamaya göre değil.

## 5. Veritabanı epizot başına sıfırlanıyor mu

**Cevap: evet, otomatik olarak, ve ucuz.**

Sıfırlamanın gerçekten olduğunu Aşama 1'de teste bağladım
(`tests/test_appworld_reset.py`). Yöntem şu: birinci koşu yeni bir not yaratıp
aynı koşuda okuyor, ikinci koşu aynı görevi yeniden açıp o kimliği istiyor ve
`409 The note with id 3084 does not exist` alıyor. Yaratma adımı olmadan sınama,
sıfırlama hiç çalışmasa bile geçerdi.

Ayrı bir sıfırlama çağrısı yok. `AppWorld` sınıfında `reset` ya da `restore`
içeren hiçbir metot bulunmuyor. Sıfırlama dünya açılışında kendiliğinden
yapılıyor.

Maliyeti, aynı görev beş kez açılıp kapatılarak ölçüldü:

| Aşama | ortalama | medyan | aralık |
|---|---|---|---|
| dünya açılışı | 0,578 s | 0,150 s | 0,140 – 2,310 s |
| tek `execute` | 0,004 s | 0,000 s | 0,000 – 0,010 s |
| dünya kapanışı | 0,008 s | 0,010 s | 0,000 – 0,010 s |

Ortalamayı yukarı çeken şey ilk açılış, 2,31 saniye. Sonraki dördü 0,15 saniye
civarında. Yani epizot başına sabit maliyet pratikte 0,16 saniye ve üç bin
epizotluk bir koşuda toplamı sekiz dakika bile etmiyor.

Ölçümde bir tuzak vardı, not ediyorum. İlk denemem anlamsız sayılar üretti,
çünkü AppWorld freezegun ile zamanı süreç geneli donduruyor ve `time.monotonic`
de donuyor. Modülü import etmeden önce saklanan referans da kurtarmadı. Ölçüm
`/proc/uptime` okunarak yapıldı.

## 6. Okuma ve yazma sınıflandırması

**Cevap: var, metadata'da, ve 473 API'nin hepsini kapsıyor.**

`data/api_docs/standard/` altındaki on bir dosya her API için bir kayıt taşıyor
ve kayıtta `method` alanı bulunuyor. Elle sınıflandırma yükü sıfır.

| Metot | Sayı | Oran |
|---|---|---|
| GET | 176 | %37,2 |
| POST | 166 | %35,1 |
| DELETE | 78 | %16,5 |
| PATCH | 53 | %11,2 |

GET okuma sayılırsa 176 okuma ve 297 yazma API'si var.

Uygulama başına API sayısı: `spotify` 92, `amazon` 75, `splitwise` 65,
`todoist` 56, `venmo` 54, `gmail` 48, `phone` 30, `file_system` 26,
`simple_note` 17, `supervisor` 6, `api_docs` 4.

Aynı sınıflandırma API adından da çıkarılabiliyor. `show_`, `search_`, `get_`,
`list_`, `view_` ve `download_` öneklerini okuma sayan bir kural 473 API'nin
470'inde doğru sonuç veriyor, yani yüzde 99,4. Üç istisna var:
`file_system.directory_exists` ve `file_system.file_exists` GET oldukları hâlde
okuma öneki taşımıyor, `spotify.download_song` ise `download_` ile başladığı
hâlde POST.

Kalkanın kural kaynağı için `method` alanı kullanılacak. Ad öneki yalnız akıl
kontrolü.

## 7. Ajan tek bir model turunda kaç API çağırıyor

**Cevap: bu modelde ölçülen sayı 0,0045 ve tasarım için kullanılamaz.**

On iki epizot koşuldu, hepsi `train` bölmesinden, hepsi ısınmış model üzerinde.

| | |
|---|---|
| epizot | 12 |
| toplam model turu | 223 |
| toplam API çağrısı | 1 |
| tur başına ortalama | 0,0045 |
| sıfır çağrılı epizot | 11 / 12 |
| adım tavanına dayanan epizot | 11 / 12 |
| adım başına girdi tokenı | 5958 |

Sayı düşük çünkü ölçtüğü şey ortam değil, model. `qwen2.5-coder:1.5b` bu görevde
çoğunlukla çalışmayan kod üretiyor ve yirmi adımlık tavana hiç API çağırmadan
dayanıyor. Ölçek ekseninin en küçük noktası taban etkisine yapışmış durumda.

Aynı sayı rejime de bağlı. Aynı görev soğuk modelle koşulduğunda 19 API çağrısı
üretiyor, ısınmış modelle koşulduğunda 1. Ayrıntısı aşağıda, S-11 bölümünde.

**ÖLÇÜLEMEDİ.** Tasarımın ihtiyaç duyduğu tur başına çağrı sayısı bu modelle
belirlenemez. Ölçüm Aşama 4'te 3B ve 7B modellerle tekrarlanacak. Referans
çözümlerdeki 53,44 çağrılık ortalama (üçüncü soru) üst sınır olarak duruyor,
çünkü referans çözüm tek seferde ve doğru yazılmış hâli temsil ediyor.

Bir de not: adım başına 5958 girdi tokenı, bağlam bütçesi için doğrudan
kullanılabilir bir sayı. Yönerge dosyası tek başına 11350 bayt ve gözlemler
biriktikçe bu sayı büyüyor.

## 8. Motor ajan sürecinden ayrı çalışabiliyor mu

**Cevap: evet, ve destekleniyor. Ama süreç başına tek dünya kısıtı var.**

Bunu kod yazmadan, CLI'yı ve paket kaynağını inceleyerek çıkardım.

AppWorld dört sunucu komutu sunuyor: `appworld serve environment`,
`serve apis`, `serve mcp` ve `serve multiple`. Hepsinde `--docker` bayrağı var,
yani motor konteyner içinde de koşabiliyor. `--num-servers` seçeneği birden çok
sunucuyu birlikte başlatıyor ve `--port -1` verildiğinde portları kendisi
atıyor.

İstemci tarafında `AppWorld` kurucusu `remote_environment_url`, `remote_apis_url`
ve `remote_docker` parametrelerini kabul ediyor. Yani ajanın kodu bir süreçte,
motor başka bir süreçte, hatta başka bir konteynerde koşabilir.

Kısıt şurada: `appworld/serve/environment.py` modül düzeyinde tek bir `world`
nesnesi tutuyor. `maybe_raise_exception` fonksiyonu, istenen `task_id` etkin
dünyanınkinden farklıysa HTTP 400 döndürüyor:

```
The active task world is {world.task_id}. But you have requested to operate on {task_id}
```

Sebebi iki katlı. Freezegun zamanı süreç geneli donduruyor, ayrıca veritabanı
bağlantılarının sızmaması isteniyor.

**Sonucu.** N paralel epizot, N motor süreci demek. Bu bir engel değil, çünkü
`--num-servers` bunu zaten destekliyor. Ama bellek ve çekirdek bütçesi kalemi
olarak pilot planında durması gerekiyor ve duruyor.

---

# S-11 kapandı: oynaklığın kaynağı rastgelelik değilmiş

Aşama 1'de aynı görev, aynı seed ve aynı sıcaklıkla koşulan üç epizot 19, 1 ve
19 API çağrısı vermişti. Bu, üç tohumlu varyans planının dayandığı seed
kontrolünün hiç olmadığı anlamına gelebilirdi. Ölçtüm, öyle değilmiş.

## Seed geçiyor

Önce taşıma katmanına baktım. litellm'in `ollama_chat` sağlayıcısına aynı istemi
aynı seed'le iki kez gönderdim, çıktılar farklı çıktı. Sonra aynı sınamayı
Ollama'nın kendi `/api/chat` ucuna yaptım, çıktılar birebir aynı çıktı ve farklı
seed farklı çıktı verdi.

Bu ilk bakışta litellm'i suçlu gösteriyordu. Ama deseni görmek için litellm
üzerinden dört çağrı yaptım ve dördü de birbirinin aynısı çıktı, üstelik yerli
uçtan gelen metinle birebir eşleştiler. Ayrışan tek şey bütün dizinin ilk
çağrısıydı.

## Ayrışan şey yükleme durumu

Modeli açıkça boşaltıp arka arkaya üç çağrı yapan bir sınama yazdım ve iki tur
koştum. İki turda da aynı sonuç:

| Çağrı | Özet |
|---|---|
| 1, soğuk | `0b9d5bfca170070e` |
| 2, ısınmış | `fc4f39f3c60221c4` |
| 3, ısınmış | `fc4f39f3c60221c4` |

Soğuk çağrının çıktısı da kendi içinde kararlı. İki turda da aynı özeti verdi.
Yani rastgelelik yok, iki ayrı belirlenimci rejim var.

## Epizot düzeyinde de aynı

Aynı görevi dört kez koşturdum: soğuk, ısınmış, soğuk, ısınmış. Yörüngenin
tamamının özetini aldım.

| Koşu | Rejim | API çağrısı | Yörünge özeti |
|---|---|---|---|
| 1 | soğuk | 19 | `656aaf05ce034ff4` |
| 2 | ısınmış | 1 | `5eb6d02cf297b218` |
| 3 | soğuk | 19 | `656aaf05ce034ff4` |
| 4 | ısınmış | 1 | `5eb6d02cf297b218` |

İki soğuk koşu birebir aynı yörüngeyi üretti. İki ısınmış koşu da öyle. İkisi
birbirinden farklı.

## Hüküm ve kalan belirsizlik

Seed kontrolü var. Epizotlar belirlenimci. Aşama 1'deki 19, 1, 19 dizisi
rastgelelik değil, modelin bellekte yüklü olup olmamasıydı.

Bir belirsizlik kalıyor ve saklamıyorum. "Isınmış" tek bir durum değil. Yukarıda
ısınmış koşu 1 çağrı verdi, ama on iki epizotluk ölçüm batch'inde aynı görev yine
ısınmış modelle koşuldu ve 0 çağrı verdi. Aradaki fark, o batch'te modelin daha
önce hangi istekleri gördüğü. Yani sunucu tarafında yükleme durumundan başka bir
durum daha var ve onu istemciden görmüyoruz.

**Tasarıma sonucu.** Epizotların tekrarlanabilir olması için modelin sunucudaki
durumunu kontrol etmemiz gerekiyor. Ölçtüğüm tek güvenilir protokol şu: her
epizottan önce modeli boşalt, böylece her epizot aynı soğuk durumdan başlasın.
Bu protokolle iki koşu birebir aynı yörüngeyi verdi. Maliyeti epizot başına bir
model yüklemesi.

Bu, K-21'in `keep_alive` gerekçesiyle çelişiyor. O karar yeniden yükleme
maliyetinden kaçınmak için süreyi uzun tutuyordu. Şimdi elimizde ölçülmüş bir
takas var ve kararı Aşama 4 verecek.

---

# "1" epizodu: sessiz boş başarı

On iki epizotluk ölçümde tek bir epizot 1 API çağrısı verdi ve üç adımda,
4,2 saniyede bitti. Diğerlerinin hepsi yirmi adımlık tavana dayandı. Bu farkın
gerçek oynaklık mı yoksa yakalanmamış bir arıza biçimi mi olduğunu sordunuz.
İkincisi.

Görev `692c77d_1` idi; yönerge metni AppWorld lisansı gereği çıkarıldı, özgün
metnin özeti `sha256:a950a91993090db7f485be0426584f1860ec42f296285eec93e92d53eb7bc1cf` (`S-79`).

**Adım 1.** Model `for playlist in playlists:` yazdı. `playlists` tanımlı değil.
Yürütme `NameError` ile düştü ve tek bir eylem üretmedi.

**Adım 2.** Model hatayı gördü ve düzeltti. Düzeltme şuydu: `playlists = []`.
Boş liste. Yürütme bu sefer başarılı oldu, çünkü döngü hiç dönmedi. Yine tek bir
eylem üretilmedi, ama ortam `Execution successful.` dedi.

**Adım 3.** Model işin bittiğine hükmetti ve `apis.supervisor.complete_task()`
çağırdı. Kaydedilen tek API çağrısı bu.

Epizot temiz görünüyor. Üç adım, hata yok, görev tamamlandı bildirimi var. Oysa
hiçbir şey yapılmadı.

Adım 1 sizin tanımladığınız dördüncü kategoriye giriyor: kod üretildi,
ayrıştırıldı, ama hiç eylem üretmeden yürütme hatası verdi. Adım 2 o kategoriye
girmiyor, çünkü yürütme hata vermedi. Ayrı bir etiket öneriyorum ve karar
kaydına K-36 olarak yazdım: **yürütme başarılı ama hiç eylem üretilmedi.**

İki etiketi ayırmak gerekiyor, çünkü ikisi farklı şeyleri gösteriyor. Yürütme
hatası modelin kod yazamadığını söyler. Boş başarı ise modelin görevi
sessizce etkisizleştirdiğini söyler ve doğrulayıcıya kadar hiçbir yerde alarm
üretmez. Pilot verisinde ikincisi birincisinden tehlikeli, çünkü sağlıklı epizot
gibi görünür.
