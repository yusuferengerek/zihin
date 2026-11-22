# Aşama 4 raporu — Ollama model sunum katmanı

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

## Kabul ölçütü ne diyordu

> Üç model de tek bir görevde koşuyor. Her biri için VRAM kullanımı ölçülüp
> raporlanıyor, özellikle 7B'nin 8 GB'a sığdığı ve ne kadar pay bıraktığı.
> num_ctx'in gerçekten 32768 olduğu doğrulanmış. Her koşunun künyesi tabloya
> yazılmış.

Paralel iş olarak adım tavanı kalibrasyonu da bu aşamada yapıldı.

## Neyi doğruladım

### Üç model de koştu ve üçü de tamamen VRAM'de

| Model | VRAM | Toplam | Tamamen GPU'da | Pencere | Adım | API çağrısı | Süre |
|---|---|---|---|---|---|---|---|
| `qwen2.5-coder:1.5b-instruct-q4_K_M` | 1,560 GiB | 1,560 GiB | evet | 32768 | 20 | 19 | 24,1 s |
| `qwen2.5-coder:3b-instruct-q4_K_M` | 2,602 GiB | 2,602 GiB | evet | 32768 | 20 | 4 | 51,2 s |
| `qwen2.5-coder:7b-instruct-q4_K_M` | 5,160 GiB | 5,160 GiB | evet | 32768 | 20 | 5 | 72,1 s |

Kart 8,0 GiB taşıyor. 7B yüklüyken 5,16 GiB dolu, yani 2,84 GiB pay kalıyor.
Ama sunucunun kendi ölçümü boştaki VRAM'i 6,9 GiB gösteriyor; masaüstünün
kullandığı kısım düşüldüğünde gerçek pay 1,74 GiB. Bu ikinci sayı planlama için
doğru olan.

Üçünde de `size_vram` değeri `size` değerine eşit, yani hiçbiri kısmen CPU'ya
taşmıyor. 32k bağlamın KV cache'i q8_0 ile bu rakamların içinde.

### Bağlam penceresi model başına doğrulandı

Üç modelde de sunucudan okunan etkin pencere 32768. Yapılandırmada yazması
yetmiyor; K-37'nin bütün gerekçesi bu. Ölçüm `tests/test_model_serving.py`
içinde model başına ayrı test olarak duruyor.

### Sunucu ayarları künyeye gerçekten yazıldı

| Ayar | Değer |
|---|---|
| `OLLAMA_CONTEXT_LENGTH` | 32768 |
| `OLLAMA_KV_CACHE_TYPE` | q8_0 |
| `OLLAMA_FLASH_ATTENTION` | true |
| `OLLAMA_KEEP_ALIVE` | 30m0s |
| `OLLAMA_HOST` | http://127.0.0.1:11434 |
| Ollama sürümü | 0.32.3 |

Kaynak sunucunun kendi yapılandırma dökümü, başlatıcı betiğin iddiası değil.
Ayrımı önemsiyorum: betik bir değeri geçirdiğini söyleyebilir ama sunucu onu
uygulamamış olabilir.

### Seed türetmesi deterministik ve etkili

Seed `run_id`, `task_id` ve `seed_index` üçlüsünden türetiliyor (K-20). Üç
model için çıkan değerler: 3907020950, 3001428063, 2725799904.

`tests/test_model_config.py` aynı üçlünün aynı seed'i verdiğini ve üç
bileşenden herhangi biri değiştiğinde seed'in değiştiğini sınıyor.
`tests/test_model_serving.py` ise sunucu tarafında aynı seed'in aynı çıktıyı,
farklı seed'in farklı çıktıyı verdiğini sınıyor. İkincisi olmadan birincisi
hiçbir şey kanıtlamaz: düşük sıcaklık da çıktıyı sabitleyebilirdi.

## Sayıların okunmaması gereken biçimi

Tablodaki API çağrısı sütununa bakıp "1.5B, 7B'den iyi" sonucu çıkarılamaz. Üç
model üç farklı seed'le koştu, çünkü seed `run_id` üzerinden türetiliyor ve
`run_id` model adını taşıyor. Üstelik tek görev ve tek tohum.

Söylenebilecek tek şey şu: üç model de yirmi adımlık tavana dayandı ve hiçbiri
görevi bitirmedi. S-14 ölçek ekseninin en küçük noktası için açılmıştı; bu
ölçüm taban etkisi endişesinin 3B ve 7B'yi de kapsayabileceğini gösteriyor.
Ama tek görev ve tek tohumla bunu söyleyemem, o yüzden S-14'ün kapsamını
genişletmiyorum, yalnız uyarıyı ekliyorum. Karar pilotun.

## Adım tavanı kalibrasyonu

K-11 iki çapayı birleştirmemi istemişti: train ve dev'deki referans uzunlukları
ile doğrulayıcının beklediği çağrı sayısı arasındaki ilişkiyi kalibre et, sonra
test bölmelerine uygula.

**Kalibrasyon tutmadı.** Doğrulayıcı tarafındaki aday nicelik
`ground_truth/test_data.json` içindeki `no_op_fail` sayısı. Etiketin anlamı şu:
hiçbir şey yapmayan bir ajan `no_op_pass` gereksinimini zaten geçer,
`no_op_fail` gereksinimini geçemez. Yani bu sayı doğrulayıcının aktif iş
beklediği gereksinim sayısı ve 732 görevin hepsinde var.

147 görev üzerinde ölçtüm:

- Referans çözüm uzunluğuyla korelasyon: **0,088**
- Yalnız yazma çağrılarıyla korelasyon: **0,122**
- Gereksinim başına çağrı oranı: medyan 10,75, p95 58,0, en yüksek 139,0

Çarpımsal bir çapa bu dağılımla 261 ile 986 arasında tavanlar üretiyor. Kullanılamaz.

**Ama kalibrasyona gerek yokmuş.** K-11 çapayı referans uzunluktan almaktan
vazgeçmişti ve gerekçesi test bölmelerinde referansın olmamasıydı. Çözüm dosyası
gerçekten yok. Ama `ground_truth/metadata.json` içindeki `num_api_calls` alanı
732 görevin hepsinde dolu, hiçbirinde boş değil, ve referans çözümü olan 147
görevde `api_calls.json` uzunluğuyla birebir tutuyor.

Yani çapa doğrudan `metadata.num_api_calls` olabilir. Bölme başına p95: train
144, dev 139, test_normal 81, test_challenge 178.

Bunu Aşama 2'de zaten kullanmıştım, dördüncü sorunun dağılımını oradan
çıkarmıştım. Aradaki bağlantıyı o zaman kurmamışım.

## Yanıt verisi enstrümantasyonu: birinci tercih çalışıyor

S-16 için önerdiğiniz sıranın ilkini denedim ve tuttu.

`Requester._get`, `_post`, `_patch` ve `_delete` metotları ham yanıt nesnesini
döndürüyor; o nesnede hem durum kodu hem gövde var. İstek bilgisi de aynı
çağrının argümanlarında. Tek bir sarmalama ikisini birden yakalıyor ve bu taşıma
katmanı, ajanın prompt'una, ayrıştırıcısına ve döngüsüne dokunmuyor.

Sondada yakalananlar:

```
GET  /supervisor/profile            200  {"first_name": "Joyce", ...}
GET  /supervisor/account_passwords  200  [{"account_name": "amazon", ...}]
POST /spotify/auth/token            200  {"access_token": "eyJhbGci..."}
POST /spotify/auth/token            401  {"message": "Invalid credentials"}
```

Bir tuzağı vardı ve ilk denememde tam olarak ilgilendiğim vakayı kaçırdım.
`_get` ve `_post` içinde `raise_if_failure` çağrılıyor ve başarısız yanıtta
istisna fırlatıyor. Sarmalayıcı kaydı istisnadan sonra almaya çalışırsa
başarısız çağrılar hiç kaydedilmiyor. İlk sondam yedi çağrının yedisini de 200
olarak gösterdi, oysa iki tanesi başarısızdı. Sarmalayıcı istisnayı yakalayıp
kaydettikten sonra yeniden fırlatacak şekilde düzeltildi.

Şu an yalnız yapılabilirliği gösterdim; kaydediciye bağlanması ayrı bir iş ve
biriktirme başlamadan yapılacak. `actions.result_status` ve `error_class`
sütunları zaten şemada duruyor.

## Karşılaştığım sürprizler

### Künyeye sunucu ayarları boş yazılmış

İlk koşuda künyedeki KV cache tipi, flash attention ve `keep_alive` alanları
`None` çıktı. Sebebi şu: ayarlar Windows'taki Ollama sürecinin ortamında, ölçüm
betiği ise WSL içinde koşuyor. `os.environ` oradan bunları göremiyor.

Bu K-37'nin ikinci şartının sessizce boşa çıkması demekti. Düzeltme sunucunun
kendi yapılandırma dökümünü okumak oldu.

### Model indirmesini kendi betiğim kesti

7B indirmesi yüzde yüze geldiğinde `serve_models.ps1` betiğini çalıştırdım.
Betik çalışan ollama süreçlerini durduruyor ve pull istemcisi sunucuya bağlı
olduğu için indirme manifest yazılmadan kesildi. Model listede görünmedi.
Blob'lar önbellekte kaldığı için yeniden çekmek hızlı oldu.

### Ölçüm betiği epizot yazıp adım yazmıyordu

İlk sürüm modelleri ölçüyor, künye ve epizot satırını yazıyor ama adım, eylem
ve gözlem yazmıyordu. Sonuç, `total_model_calls` alanında 20 yazan ama hiç adım
satırı olmayan bir kayıttı. Aşama 3'ün testleri bunu yakaladı ve düştü.

Düzeltme kaydedici ajanı betikten pakete taşımak oldu
(`src/zihin/recording_agent.py`). Artık iki betik de aynı kaydediciyi
kullanıyor ve her epizot dört düzeyiyle yazılıyor.

## Kalanlar

Aşama 4'ün iki kararı bilerek açık bırakıldı ve ikisi de aşağıdaki her şeyi
kilitliyor: yükleme protokolü (K-21) ve ona bağlı doğrulama zamanlaması (K-37).
Şu anki geçici çözüm her epizottan önce boşaltmak. Kalıcı hâli S-13 ile birlikte
verilecek.

## Yerel-yalnız kontroller

Son koşu: `2026-08-11T00:38:07+03:00`, commit `ec1e68d`. On dört test geçti,
56 test elendi.

## Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Sunucu betiği, ölçüm betiği, kaydedici ajan modülü |
| Testi yazıldı | Evet, 70 test. 56'sı CI'da, 14'ü yerel |
| Loglandı | CHANGELOG girdisi yazıldı |
| Belgesi yazıldı | REPRODUCE, 08-decisions, 09-limitations, PROJECT_STATUS |
| Hata durumu düşünüldü | Bağlam penceresi tutmayan model atlanıyor, sunucu ayarları sunucunun kendi beyanından okunuyor |
| PR üzerinden gözden geçirildi | PR açıldı |
| Temiz kurulumda baştan çalıştırıldı | CI dört kontrolü geçiyor |
