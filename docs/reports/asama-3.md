# Aşama 3 raporu — SQLite kayıt şeması

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor. Şemanın neden
öyle olduğu `DATA_MODEL.md` içinde.

## Kabul ölçütü ne diyordu

> Aşama 1'deki tek görev koşusu bu şemaya yazılıyor. Bir epizod, birden çok
> adım, adım başına birden çok eylem, eylem başına bir gözlem. Bir sorguyla
> epizodun tamamını sırayla okuyabiliyorsun. Testler bunu doğruluyor.

Üstüne bu aşamaya `shield_violations` tablosu, epizot başına model yükleme
durumu ve sıra numarası eklendi.

## Neyi doğruladım

### Gerçek bir koşu şemaya yazıldı

`scripts/record_run.py` görev `82e2fac_1` üzerinde koşuldu. Sonuç: 1 epizot,
20 adım, 19 eylem, 20 gözlem, 1 doğrulayıcı satırı.

Sayı Aşama 2'nin soğuk rejim ölçümüyle birebir aynı: orada da aynı görev 19 API
çağrısı üretmişti. Bu, kaydın koşuyu doğru yakaladığının bağımsız kontrolü.

Toplamda beş görev kaydedildi: 5 künye, 5 epizot, 86 adım, 56 eylem, 86 gözlem.

### Adım başına birden çok eylem gerçek koşuda da çıktı

İlk kaydettiğim görevde her adım tek çağrı yaptı, yani ölçütün bu maddesi
gösterilemedi. Şemanın taşıyabildiğini sentetik test zaten kanıtlıyordu ama
gerçek koşuda görmek istedim. Dört görev daha kaydettim; `6104387_1` toplam 33
eylem üretti ve bir adımında iki çağrı yaptı.

### Yalnız ekleme tetikleyiciyle zorlanıyor

Yedi tablonun her biri için ayrı ayrı sınandı: `UPDATE` ve `DELETE` denemesi
`IntegrityError` fırlatıyor. Sözleşme değil, makine kuralı.

Yabancı anahtarlar da zorlanıyor. Olmayan bir koşuya epizot yazmak reddediliyor.
Bunun bir tuzağı vardı: SQLite'ta yabancı anahtarlar varsayılan olarak kapalı ve
şemadaki `PRAGMA` satırı dosyaya yazılmıyor. Her bağlantıda açıkça açılıyor,
yoksa kısıt sessizce uygulanmıyordu.

### Epizodun tamamı tek sorguyla okunuyor

`episode_timeline` görünümü. Sol dış birleşim kullanıldı, böylece eylem
üretmeyen adımlar da satır veriyor. Bunun ayrı bir testi var: K-36'nın dördüncü
ve beşinci kategorileri hiç eylem üretmiyor ve o adımlar çizelgeden düşerse
sıfır eylemli epizot, ajanın çağırmamayı seçtiği epizotla aynı görünür.

### Testler

43 test CI'da koşuyor, sentetik veriyle. 6 test `appworld` işaretli ve gerçek
koşuyu okuyor. Tam takım 49 test.

## Karşılaştığım sürprizler

### Eylemler koşu bittikten sonra adımlara bağlanamıyor

`logs/api_calls.jsonl` düz bir liste ve hangi çağrının hangi adıma ait olduğunu
söylemiyor. Koşu bittikten sonra bakıldığında eylemleri adımlara dağıtmanın
güvenilir bir yolu yok.

K-14 bunu zaten öngörmüş: kayıt her `execute()` çağrısından sonra yürütücü
süreçte alınacak. Uyguladığım hâli şu: dosyanın o adımda uzadığı kadarı o adımın
eylemleridir.

İskeleye dokunmadım. `SimplifiedReActCodeAgent` olduğu gibi kuruluyor, yalnız
ortamın `execute` metodu dışarıdan sarmalanıyor. Prompt, ayrıştırıcı ve döngü
aynı kalıyor.

### K-37'nin kapısı ilk denemede koşuyu durdurdu

Doğrulama şartını yazdım, koştum, koşu durdu: etkin bağlam penceresi `None`
geldi. Kapı çalışıyordu ama sebebi benim yöntemimdi. `/api/ps` yalnız o an
yüklü modeli bildiriyor; model soğukken pencere okunamıyor.

Doğrulamanın modeli yüklemesi gerekiyor. Bunun bir yan etkisi var ve
saklamıyorum: doğrulama modeli ısıtıyor, yani epizot ısınmış rejimde başlıyor.
Aşama 2'de ölçüldüğü gibi o rejimde aynı görev 19 yerine 1 çağrı üretiyor.

Çözüm olarak doğrulamadan sonra modeli tekrar boşaltıyorum ve epizot soğuk
rejimde başlıyor. Aşama 2'de ölçülen tek tekrarlanabilir protokol bu. Karar
geçici; K-21'in nihai hâlini Aşama 4 belirleyecek.

### `api_calls.jsonl` beklenenden dar

S-05 yanıt gövdesinin olmayabileceğini söylüyordu. Ölçtüm: dosya yalnız
`method`, `url` ve `data` taşıyor. Yanıt gövdesi de yok, durum kodu da yok.

Yani `actions.result_status` ve `actions.error_class` bu kaynaktan
doldurulamıyor. Sütunlar duruyor ama `NULL`. Adımın başarılı olup olmadığı
yalnız gözlem metninden okunabiliyor, tek tek çağrı düzeyinde değil.

### Yalnız ekleme kuralı yazma sırasını belirledi

Epizodun bitiş zamanı ve toplamları ancak epizot bitince biliniyor, `UPDATE` de
yasak. Bu yüzden epizot bellekte biriktirilip sonunda tek işlemde yazılıyor.
Koşu ortasında çökme olursa AppWorld'ün kendi kayıtları diskte duruyor, yani
veri kaybolmuyor, yalnız veritabanına girmemiş oluyor.

## Kalkanın yüklemi için ölçüm

Kalkanın okuma/yazma ayrımının güvenilirliğini sordunuz. Önce bir düzeltme:
Aşama 2'deki yüzde 75,5'lik vekil o yüklem değildi, görev başına uygulama
listesi çıkarma vekiliydi. Kalkanın yüklemi `method` alanına dayanıyor ve o
alan doğrudan veri, 473 API'nin yüzde yüzünü kapsıyor.

Ama işaret ettiğiniz asıl risk gerçekti ve ölçtüm: durum değiştiren GET uçları
var mı? Her API işleyicisi `ast` ile ayrıştırılıp gövdesinde yazma çağrısı
arandı. On beş GET ucu yazma çağrısı içeriyor ve dağılım rastgele değil:

| Grup | Uç | Ne yapıyor |
|---|---|---|
| `download_*` | 9 | `file_system` uygulamasına dosya yazıyor, ayrı erişim jetonu alıyor |
| Tembel ilklendirme | 4 | İlk okumada varsayılan satırı yaratıyor |
| Türetilmiş alan güncellemesi | 2 | Önbellek alanını güncelliyor |

İkisini elle doğruladım. `spotify.show_volume` gerçekten `MusicPlayer.create()`
çağırıp satır yazıyor. `amazon.download_order_receipt` gerçekten `create_file()`
ile dosya oluşturuyor.

Tarama akıl kontrolünden geçti: GET dışı 302 ucun 211'inde yazma çağrısı
bulundu. Ama kalan 91'i işi yardımcı fonksiyona devrediyor, yani aynı devretme
GET tarafında da olabilir. **On beş bir alt sınır.** S-15 olarak açtım; liste
Aşama 4 öncesinde çalışma zamanı ölçümüyle genişletilecek.

## Şartnameden bir sapma

Kabul ölçütü "eylem başına bir gözlem" diyor. Şema gözlemi adıma bağlıyor,
eyleme değil. Sapma değil, K-13'ün uygulanması: şartname bu noktada
düzeltilmişti. Sebebi ölçülmüş bir olgu, `execute()` adım başına tek çıktı
dizesi döndürüyor ve eylem düzeyinde tam çıktı diye bir kavram ortamda yok.

## Karara bağlananlar

- **K-38.** Epizotlar koşullara serpiştirilerek atanıyor, bloklu değil.
- **K-39.** Model yükleme durumu ve sıra numarası epizot başına kaydediliyor.
- **K-40.** Çözülmeyen epizot, gerçekte kaç adım sürerse sürsün tavanda
  sansürleniyor.
- **K-41.** Kalkanın yüklemi `method` alanından, on beş uçluk açık istisna
  listesiyle.
- **K-42.** Biriktirme havuzu normal test görevleriyle genişletiliyor,
  değerlendirme örneklemi yalnız biriktirmede temsil edilen uygulamalardan
  çekiliyor. İkisi de ön kayda giriyor.
- **K-11.** İkinci çapa eklendi. Referans uzunluk ile doğrulayıcının beklediği
  çağrı sayısı arasındaki ilişki kalibre edilip test bölmelerine uygulanacak.
  Kalibrasyon henüz yapılmadı, Aşama 4 öncesinde çıkarılacak.
- **S-05** doğrulandı ve daraltıldı. **S-15** açıldı.

## Yerel-yalnız kontroller

Son koşu: `2026-08-10T23:35:47+03:00`, commit `49e348a`. Altı test geçti, 43
test elendi.

## Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet, şema, kayıt katmanı ve yürütücü |
| Testi yazıldı | Evet, 49 test. 43'ü CI'da, 6'sı gerçek koşuyu okuyor |
| Loglandı | CHANGELOG girdisi yazıldı |
| Belgesi yazıldı | `DATA_MODEL.md`, 08-decisions, 09-limitations, PROJECT_STATUS, REPRODUCE |
| Hata durumu düşünüldü | Yabancı anahtar, yalnız ekleme, enum kısıtları ve bağlam penceresi kapısı ayrı ayrı sınandı |
| PR üzerinden gözden geçirildi | PR açıldı |
| Temiz kurulumda baştan çalıştırıldı | CI AppWorld dahil kuruyor, dört kontrol yeşil |
