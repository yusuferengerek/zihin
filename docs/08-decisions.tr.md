# Kararlar

Alınan her karar burada, gerekçesiyle duruyor. Bir karar değiştiyse eskisi
silinmiyor. Üstü çiziliyor ve neden değiştiği yazılıyor.

Her kaydın biçimi aynı: bağlam, karar, gerekçe.

---

## Ortam ve depo

### K-01 — Platform WSL2, Ubuntu 24.04

**Bağlam.** AppWorld hem Windows'ta hem Linux'ta koşabiliyor. Windows desteği
depo `main` dalında var ve AppWorld'ün kendi CI'ında `windows-latest` üzerinde
doğrulanıyor.

**Karar.** WSL2 üzerinde temiz bir Ubuntu 24.04 dağıtımı, adı `zihin`. Depo
WSL'in kendi dosya sisteminde duruyor, `/mnt/*` üzerinde değil.

**Gerekçe.** Dört sebep var.

1. Sandbox kararı kök yetkisiz podman, yani Linux. Windows'ta kurulsaydı Aşama
   5'te zorunlu bir göç çıkardı.
2. Windows'ta `timeout_call` desteklenmiyor ve `default_timeout_seconds` zorla
   `None` oluyor. Bu bir konfor kaybı değil, dört sonlandırma yolundan birinin
   ölmesi.
3. AppWorld'ün kendi Windows CI'ı doğrulamayı ilk dört göreve kısıtlıyor ve
   yanında `super slow on windows / figure out why` notu taşıyor. Üç bin
   epizotluk bir koşu için ciddi bir uyarıdır.
4. Ubuntu 24.04, GitHub Actions'ın `ubuntu-latest` koşucusuyla aynı sürüm.
   Geliştirme ortamı ile CI birebir eşleşiyor.

Deponun `/mnt/d` yerine ext4 üzerinde durmasının sebebi ayrı. 9p dosya sistemi
çok sayıda küçük dosyada ve SQLite'ta feci yavaş. Yedek Windows tarafında
durabilir.

### K-02 — WSL bellek sınırı 8 GB

**Bağlam.** `.wslconfig` iptal edilen bir denemeden kalma hâliyle WSL'i 4 GB'a
kapatıyordu. Dosya host geneli, docker-desktop dahil her dağıtıma uygulanıyor.

**Karar.** `memory=8GB`, `processors=8`, `swap=4GB`. Eski dosyanın yedeği
`~/.wslconfig.iptal-edilen-proje.bak` içinde.

**Gerekçe.** Makinede 15.6 GB var. Ollama Windows tarafında kalıyor ve modeli
GPU'ya yüklüyor. Host tarafına yaklaşık 7.6 GB kalması yeterli.

### K-03 — Ağ kipi şimdilik varsayılan (NAT)

**Karar.** ~~WSL ağ kipi değiştirilmedi. WSL içinden Windows host'taki Ollama'ya
erişim Aşama 4'te ölçülüp karara bağlanacak.~~ Aşama 1 modeli beklenenden erken
istedi, karar K-34'e taşındı.

**Gerekçe.** `networkingMode=mirrored` köprüyü tek satırda çözerdi ama dışarı
yönlü DNS'i bozduğu bilinen durumlar var. Kurulum boyunca gereken paket
indirmelerine gereksiz bir değişken eklememek için ertelendi.

### K-34 — Ağ kipi mirrored

**Bağlam.** Aşama 1'in kabul ölçütü tek görevi uçtan uca koşturmayı istiyor,
yani modele Aşama 4'ten önce ihtiyaç var. NAT altında WSL'den Windows'taki
Ollama'ya gelen bağlantıyı Hyper-V güvenlik duvarı kesiyor. Üç adres denendi ve
üçü de erişilemedi: `127.0.0.1`, ağ geçidi adresi ve `resolv.conf` nameserver'ı.
Sebebi `DefaultInboundAction` değerinin `Block` olması.

**Karar.** `~/.wslconfig` içinde `networkingMode=mirrored`.

**Gerekçe.** Üç yol vardı, mirrored diğer ikisini gereksiz kıldı. Yalnız 11434
portunu açan Hyper-V kuralı yönetici yetkisi istiyor ve sunucunun `0.0.0.0`'a
bağlanmasını gerektiriyor. O durumda Ollama LAN arayüzünde de dinler ve kimlik
doğrulaması olmadığı için onu koruyan tek şey güvenlik duvarı kalırdı. Ollama'yı
WSL içine kurmak köprüyü tümden kaldırırdı ama Windows'taki mevcut model
deposundan ayrı ikinci bir depo doğururdu. Mirrored kipte sunucu `127.0.0.1`'e
bağlı kalıyor ve WSL yine erişiyor.

K-03'ün DNS kaygısı ölçüldü ve çıkmadı. Geçişten sonra `pypi.org`, `github.com`
ve `registry.ollama.ai` çözüldü, HTTPS istekleri döndü, `uv lock --check` geçti.

### K-04 — Özel GitHub deposu, gerçek PR

**Karar.** Özel depo, adı `zihin`. Her aşama bir dal ve bir gerçek PR.

**Gerekçe.** İki ölçüt de ancak gerçek bir koşucuda doğrulanabilir: CI'nın
dördünün yeşil olması ve temiz makinede klonlanıp kurulabilmesi. Yerelde taklit
edilen CI doğrulama sayılmaz.

### K-05 — Python 3.11

**Karar.** `requires-python = "==3.11.*"`, `.python-version` içinde `3.11`.

**Gerekçe.** AppWorld `>=3.11` istiyor. Desteklenen en düşük sürümü seçmek en az
sürpriz üreten seçimdir. Üst sürümlerde çıkacak uyumsuzluklar bize değil yukarı
akışa görünür.

### K-06 — Bağımlılık yönetimi `uv`, kilit `uv.lock`

**Karar.** `uv` 0.11.28. Kilit dosyası `uv.lock` depoya giriyor.

**Gerekçe.** Makinede zaten kurulu, tek ikili dosya, Python sürümünü de kendisi
yönetiyor. AppWorld'ün kendisi de build arka ucu olarak `uv_build` kullanıyor.

### K-07 — Aşama 0 bağımlılıkları AppWorld'ü içermiyor

**Karar.** Aşama 0 yalnız üç bağımlılığı kilitliyor. Çalışma zamanında `pyyaml`,
geliştirmede `pytest` ve `ruff`. AppWorld Aşama 1'in PR'ında girecek.

**Gerekçe.** Kural şu: bir aşamanın kabul ölçütü geçmeden sonrakine başlanmaz.
Aşama 0'ın ölçütü temiz makinede bağımlılıkların kurulabilmesi. O ölçütü henüz
gerekmeyen ağır bir bağımlılıkla sınamak yanıltıcı olurdu.

**Sonucu.** Aşama 0 asıl ağır bağımlılığı hiç sınamamış oluyor. Bu boşluk
K-32'de kapatılıyor. Temiz makine doğrulaması Aşama 1'de AppWorld dahil
tekrarlanacak.

### K-08 — Lint aracı `ruff`

**Karar.** `ruff check` ve `ruff format`. Tip denetleyici yok.

**Gerekçe.** Lint ve biçimlendirmeyi tek araçta topluyor. Şartname dört kontrol
tanımlıyor, beşinci bir kontrol eklemek istenmeyeni yapmak olurdu.

### K-09 — Satır sonları her yerde LF

**Karar.** `.gitattributes` içinde `* text=auto eol=lf`.

**Gerekçe.** Aşama 5'in kabul ölçütü bayt bayına aynı prompt istiyor. Prompt
dosyalarının özet değeri satır sonuna duyarlı ve platform arası kayma bu ölçütü
sessizce bozar.

---

## AppWorld

### K-10 — AppWorld GitHub `main`, tek bir commit'e sabit

**Bağlam.** PyPI'daki son sürüm `0.1.3.post1`, depo `main` ise `0.2.0.dev0`.
İkisi ciddi biçimde ayrışmış.

**Karar.** `main` dalından, tek bir commit hash'ine sabitlenerek kurulacak. O
hash künyeye, yani `run_manifests` tablosuna yazılacak.

**Gerekçe.** Aşama 5 referans ajan iskelesini değiştirmeden almayı istiyor. O
iskele ve prompt dosyası yalnız `main` dalında. `main` hareketli bir dal olduğu
için sürüm damgası olarak commit hash'i kullanmak zorunlu.

**Aşama 1 düzeltmesi: iskele ayrı bir dağıtımda.** İskele `appworld` paketinin
içinde değil. `appworld run` komutu `appworld_agents` modülünü istiyor, o modül
PyPI'da yok ve deposu diye tahmin edilen adres 404 veriyor. Depodaki
`experiments/code/simplified/` dosyaları da kendi kendine yetmiyor, hepsi
`appworld_agents.*` import ediyor. Kaynağı aynı depo:
`experiments/pyproject.toml`, `appworld-agents` adıyla ikinci bir dağıtım
tanımlıyor ve `appworld_agents = "."` satırıyla `experiments/` dizinini paket
köküne bağlıyor.

Sonuç olarak iki dağıtım da aynı commit'e sabitlendi, ikincisi
`subdirectory = "experiments"` ile geliyor. Aynı commit şart, yoksa iskele ile
motor birbirinden ayrışır. Yönerge dosyası kurulu paketin içinde geliyor ve
11350 bayt. K-23'ün kopyalama kararı `site-packages` içindeki bu dosyadan
yapılacak.

### K-11 — Adım tavanının çapası doğrulayıcının beklediği durum değiştiren çağrı sayısı

**Bağlam.** Adım tavanını referans çözüm uzunluğuna bağlamak düşünülmüştü. Ancak
`appworld download data` varsayılan olarak `minimal` modda iniyor. `partial` ve
`full` modlar bakımcıya özel anahtar istiyor, referans çözümler ise yalnız `full`
modda geliyor.

**Karar.** ~~Adım tavanı referans çözüm uzunluğuna bağlanacak.~~ Çapa,
doğrulayıcının beklediği durum değiştiren çağrı sayısıdır.

**Gerekçe.** Yeni çapa kıyaslamanın kendi test tanımından geliyor ve ajan
davranışından bağımsız. Yayımlanmış gpt-4o koşuları ikincil akıl kontrolü olarak
kullanılacak, çapa olarak değil.

**Aşama 2 sonrası genişletme: iki çapa birleştiriliyor.** Referans çözümlerin
elimizde olduğu ölçüldü, ama yalnız train ve dev'de. Test bölmelerinde referans
yok, doğrulayıcının beklediği çağrı sayısı ise her yerde var.

Yeni hâli şu. Train ve dev üzerinde referans çözüm uzunluğu ile doğrulayıcının
beklediği durum değiştiren çağrı sayısı arasındaki ilişki kalibre edilecek.
Kalibre edilen ilişki test bölmelerine uygulanacak. Böylece çapa hem ölçülmüş
bir referansa dayanıyor hem ajan davranışından bağımsız kalıyor, ve test
bölmesinde referans olmaması sorun olmaktan çıkıyor.

**Aşama 4 ölçümü: kalibrasyon gereksizmiş.** İki şey ölçüldü.

Birincisi, önerilen kalibrasyon tutmuyor. Doğrulayıcı tarafındaki aday nicelik
`ground_truth/test_data.json` içindeki `no_op_fail` sayısıydı; hiçbir şey
yapmayan ajanın düşürdüğü gereksinim sayısı, yani doğrulayıcının aktif iş
beklediği yer. 147 görevde referans çözüm uzunluğuyla korelasyonu 0,088. Yalnız
yazma çağrılarıyla korelasyonu 0,122. Gereksinim başına çağrı oranı 1 ile 139
arasında geziniyor, dolayısıyla çarpımsal bir çapa 261 ile 986 arasında saçma
tavanlar üretiyor.

İkincisi ve asıl olan: kalibrasyona gerek yok. K-11 çapayı referans uzunluktan
almaktan vazgeçmişti ve gerekçesi test bölmelerinde referansın olmamasıydı.
Çözüm dosyası gerçekten yok, ama `ground_truth/metadata.json` içindeki
`num_api_calls` alanı 732 görevin hepsinde dolu, hiçbirinde boş değil. O alan
referans çözümün çağrı sayısını taşıyor ve `api_calls.json` uzunluğuyla 147
görevde birebir tutuyor.

**Sonuç.** Çapa doğrudan `metadata.num_api_calls` olacak, kalibrasyon adımı
düşüyor. Bölme başına p95 değerleri: train 144, dev 139, test_normal 81,
test_challenge 178. `no_op_fail` sayısı ikincil akıl kontrolü olarak kalıyor,
çünkü doğrulayıcıdan geliyor ve ajan davranışından bağımsız.

### K-43 — Adım tavanı görev başına, tek bir küresel sayı değil

**Karar.** Tavan görev başına hesaplanıyor. Çapası `metadata.num_api_calls`,
çarpanı `k` üç değerde taranacak ve **tavana çarpma oranı** bütün koşullarda
yüzde onun altında kalacak şekilde seçilecek.

**Düzeltme.** Bu madde ilk hâlinde "sansür oranı yüzde onun altında kalacak"
diyordu. Yanlıştı ve K-53'ün ayırdığı iki niceliği birleştiriyordu. Yüzde on
kuralı yalnız tavana çarpma oranına, yani ölçüm artefaktına uygulanıyor.
Doğrulayıcı temelli sansür oranı bir sonuç ve o kurala bağlı değil.

**Gerekçe.** Differansiyel sansür. Zor görevle kolay görev aynı tavanı
paylaşırsa tavana çarpma oranı görev zorluğuyla karışır ve koşul
karşılaştırması bozulur. Görev başına tavan bunu kaynağında kesiyor.

**Uyarı: birimler farklı.** Tavan model çağrısı biriminde, çapa API çağrısı
biriminde. Aradaki dönüşüm pilotta ölçülecek, varsayılmayacak. Aşama 3'te bir
epizotta yirmi adıma on dokuz eylem düştü ama tek görevden oran çıkarılmaz.

### K-44 — Normalizasyon tabanı `metadata.num_api_calls`

**Bağlam.** Görev başına indirilemez asgari için üç zayıf kaynak vardı ve üçü de
sorunluydu. Referans çözümler test bölmesinde yok. Gözlenen asgari ölçüme bağlı
ve kazanan laneti taşıyor. Doğrulayıcı sayısı okuma çağrılarını saymıyor.

**Karar.** Taban `ground_truth/metadata.json` içindeki `num_api_calls` alanı.

**Gerekçe.** Alan 732 görevin hepsinde dolu, hiçbirinde boş değil, ve referans
çözümü olan 147 görevde `api_calls.json` uzunluğuyla birebir tutuyor. Görev
başına indirilemez asgari için ölçülmüş tek kaynak bu. Taban artık tahmin değil.

### K-45 — Eşzamanlılık ölçülmüş hâliyle: 7B'de tek epizot

**Bağlam.** K-12 paralel epizot için port başına ayrı sunucu süreci gerektiğini
söylüyordu. Aşama 4 buna ikinci bir kısıt ekledi.

**Ölçüm.** 7B yüklüyken kartta 5,16 GiB dolu ve gerçek pay 1,74 GiB. 32K
bağlamın q8_0 KV cache'i bir slot için kabaca 0,9 GiB.

**Karar.** 7B'de pratikte tek epizot koşuyor. Küçük modellerde pay daha geniş
ama orada da AppWorld'ün tek dünya tek süreç kısıtı bağlıyor. İki kısıt üst
üste biniyor ve koşu süresi tahmini bu ikisine göre yeniden yapılacak.

### K-46 — Künye alanlarının zorunlu-dolu sözleşmesi

**Bağlam.** Aşama 4'te künyeye KV cache tipi, flash attention ve `keep_alive`
`None` yazıldı. Sebebi şu: ayarlar Windows'taki sunucu sürecinin ortamında,
okuma WSL içinden yapılıyordu. Koşu yeşil görünüyordu.

**Karar.** Künyede boş kalamayacak alanların listesi kodda duruyor. Biri boşsa
künye yazılmıyor ve koşu düşüyor. `context_verified` 1 değilse de düşüyor.
Sunucu ortamındaki `OLLAMA_` ile başlayan bir ayar okunamamışsa yine düşüyor.

**Gerekçe.** Bu alanlar koşu sırasında toplanmazsa sonradan toplanamıyor.
Sessiz boşluk, koşu bittikten sonra fark edildiğinde koşuyu değersiz kılıyor.
WSL ile Windows arasından okunan her değer bu riski taşıyor.

### K-12 — Eşzamanlılık, dünya başına ayrı sunucu süreci

**Bağlam.** AppWorld motoru ayrı süreçte koşabiliyor. Ancak bir sunucu süreci
aynı anda tek bir dünya tutuyor, ikinci bir dünya istendiğinde HTTP 400 dönüyor.
Sebebi freezegun'ın zamanı süreç geneli taklit etmesi.

**Karar.** Paralel epizot için port başına ayrı sunucu süreci gerekecek. Bu kısıt
pilot planına yazıldı.

**Düzeltme, 14 Ağustos 2026: kısıt paralelliği engellemiyor.** Ölçüldü ki
AppWorld dünyayı `fastapi.testclient.TestClient` ile **süreç içinde**
koşturuyor; port açmıyor, HTTP soketi kullanmıyor. Epizot başına ayrı süreç
zaten koştuğumuz için "bir sunucu süreci tek dünya tutuyor" kısıtı otomatik
olarak sağlanıyor ve paralel epizodun önünde engel değil.

Kalan gerçek engel başka ve daha dar: paralellik **yerel** koşularda ölçümü
değiştiriyor, çünkü tek GPU paylaşılıyor ve soğuk başlangıç rejimi (K-21, K-37)
paralellikle ölüyor. Barındırılan koşularda bu engel yok. Paralellik bu ayrımla
kabul edildi ve barındırılan koşularla sınırlandı; uygulaması ertelendi.

---

## Kayıt şeması

### K-13 — Gözlem adım düzeyinde, eylem düzeyinde değil

**Bağlam.** Şartname gözlemi eyleme bağlıyordu. Ancak AppWorld'ün `execute()`
metodu adım başına tek bir çıktı dizesi döndürüyor, tek tek API çağrıları için
ayrı çıktı vermiyor.

**Karar.** ~~Gözlem eyleme bağlı.~~ Hiyerarşi epizot, adım ve eylem. Gözlem
adıma bağlı.

**Gerekçe.** Bağlama giren metin adım düzeyinde bir şey. Eylem düzeyinde tam
çıktı diye bir kavram AppWorld'de yok.

### K-14 — `actions` tablosu `api_calls.jsonl` dosyasından, host tarafında

**Karar.** Eylem satırları AppWorld'ün `logs/api_calls.jsonl` dosyasından
dolacak. Ayrıştırma her `execute()` çağrısından sonra yürütücü süreçte yapılacak.

**Gerekçe.** Mimari kural korunuyor. Kayda yazma işi host tarafında yapılıyor,
ajanın çalıştırdığı kodun içinden değil.

Bu dosyanın yanıt gövdesi taşıyıp taşımadığı henüz doğrulanmadı. Taşımıyorsa
eylemler yalnız istek ve durum taşır, bu da sınırlamalara yazılır.

### K-15 — Ham parametreler tam hâliyle saklanıyor

**Karar.** `actions` tablosunda ham parametreler özet değeriyle değil tam
hâliyle duruyor. Normalize hâl ayrı sütunda.

**Gerekçe.** Normalizasyon kuralı değişecek ve projeksiyonun kayıttan yeniden
hesaplanabilmesi gerekiyor. Yalnız özet tutulduğunda bu imkânsız hâle gelir.

### K-16 — Yalnız ekleme tetikleyiciyle zorlanıyor

**Karar.** Kayıt tablolarında `UPDATE` ve `DELETE`, `RAISE(ABORT)` eden SQLite
tetikleyicileriyle engellenecek.

**Gerekçe.** Bu bir sözleşme değil, mimari kural. Makine tarafından korunması
gerekiyor.

### K-17 — Gözlem boyut sınırı ve disk kotası

**Karar.** Bağlama giren kesilmiş metin için üst sınır 8192 bayt. Diskteki tam
çıktı için koşu başına kota var ve kota dolduğunda koşu duruyor.

**Gerekçe.** Sessizce kayıt düşürmek, sonradan fark edilmeyen bir veri kaybı
üretir. Durmak kaybetmekten iyidir.

### K-41 — Kalkanın okuma/yazma yüklemi `method` alanından, on beş istisnayla

**Bağlam.** Okuma ve yazma ayrımı API dokümanlarındaki `method` alanında
duruyor ve 473 API'nin yüzde yüzünü kapsıyor. Elle sınıflandırma yükü yok.
Ama yüklem bir varsayım taşıyor: hiçbir GET ucunun durumu değiştirmediği
varsayımı.

**Ölçüm.** Varsayım açılmış uygulama kaynağından sınandı. Her API işleyicisi
`ast` ile ayrıştırılıp gövdesinde yazma çağrısı arandı. On beş GET ucu yazma
çağrısı içeriyor ve dağılım rastgele değil, üç sistematik grup:

1. **`download_*`, dokuz uç.** `amazon`, `gmail`, `splitwise`, `spotify`,
   `todoist` ve `venmo` uygulamalarında. Hepsi `file_system` uygulamasına dosya
   yazıyor ve bunun için ayrı bir erişim jetonu alıyor. Görev açısından gerçek
   ve görünür bir yazma.
2. **Tembel ilklendirme, dört uç.** `spotify.show_current_song`,
   `show_song_queue`, `show_volume` ve `splitwise.show_group_balance`. İlk
   okumada varsayılan satırı yaratıyorlar.
3. **Türetilmiş alan güncellemesi, iki uç.**
   `phone.show_contact_relationships` ve `todoist.show_projects`.

**Karar.** Yüklem `method` alanını kullanacak, üstüne bu on beş uçluk açık bir
istisna listesi konacak. `download_*` grubu ayrıca önek kuralı olarak
yazılacak, çünkü kalkanın kaçırmaması gereken asıl grup o.

**Sınırı.** Tarama yalnız işleyici gövdesindeki doğrudan yazma çağrılarını
görüyor. GET dışı 302 ucun 211'inde yazma çağrısı bulundu, kalan 91'i işi
yardımcı fonksiyona devrediyor. Aynı devretme GET tarafında da olabilir, yani
on beş bir alt sınır.

**Karar güncellendi: yazma kümesi elle değil ölçülerek türetiliyor.** Statik
liste tek başına yetmiyor, çünkü kaçırdığı sınıf sistematik. Bulunan on beşin
dokuzu `download_*` ve o dokuzu ayrı bir erişim jetonuyla `file_system`
uygulamasına yazıyor, yani bir GET uygulama sınırını geçiyor. Kalkanın birinci
aşama yüklemi tam olarak uygulama sınırını geçen yazmaları yakalamak için var;
bu grup kalkanın kör noktası değil, var oluş sebebinin ortasındaki delik.

Yeni hâli şu. Yazma kümesi gözlenen durum farklarından türetiliyor: her
eylemden sonra veritabanı ya değişiyor ya değişmiyor ve bunu zaten
kaydediyoruz. Ampirik küme delegasyonu kendiliğinden kapsıyor, çünkü davranışa
bakıyor koda değil. Küme biriktirme fazı boyunca birikiyor ve değerlendirme
başlamadan donduruluyor. Dondurma şart, çünkü kalkan altı koşulda birebir aynı
olmak zorunda.

**Yazma kümesi ikisinin birleşimi; biri diğerinin yerine geçmiyor.** Statik
tarama ampirik kümenin önsel hâli değil, ayrı bir bileşeni. Sebep ikisinin kör
noktalarının farklı yerde olması.

Ampirik ölçüm satır sayısına bakıyor: adım öncesi ve sonrası, model başına
`count()`. Ekleme ve silme görünüyor, güncelleme görünmüyor — bir alan değişip
satır sayısı aynı kalırsa ölçüm hiçbir şey göstermiyor. Yukarıdaki üçüncü grup
tam olarak bu sınıf: `phone.show_contact_relationships` ve
`todoist.show_projects` türetilmiş bir alanı güncelliyor, yeni satır açmıyor.
Yazma kümesi yalnız ampirik ölçümden türetilseydi bu iki uç kümeye hiç girmezdi.

Statik taramanın kör noktası ters yönde: yalnız işleyici gövdesindeki doğrudan
çağrıları görüyor, yardımcı fonksiyona devredilenleri görmüyor. GET dışı 302
ucun 91'i işi devrediyor ve aynı devretme GET tarafında da olabilir. Ampirik
ölçüm davranışa baktığı için devretmeyi kendiliğinden kapsıyor.

İkisi de alt sınır ve alt sınırı farklı yerden veriyor. Bu yüzden kalkanın
yazma kümesi `statik ∪ ampirik` olarak donduruluyor. Gerekçe buraya yazılıyor
ki ileride "ampirik ölçüm var, statik tarama gereksiz" diye okunmasın: ampirik
ölçüm statik taramanın yakaladığı sınıfı yapısal olarak göremiyor, ölçüm daha
uzun sürdüğünde de göremeyecek.

Epizot kapanışındaki `model_hashes.json` üçüncü bir kat ama kümeyi tek başına
kuramıyor: güncellemeyi görüyor, hangi çağrının yaptığını söylemiyor. Rolü
kümeyi genişletmek değil, adım sayımlarıyla açıklanamayan değişiklik kaldığında
alarm vermek.

**Bir düzeltme.** Aşama 2 raporundaki yüzde 75,5'lik vekil, kalkanın
okuma/yazma yüklemi değil, görev başına uygulama listesi çıkarma vekiliydi.
Kalkanın yüklemi `method` alanına dayanıyor ve o alan doğrudan veri, vekil
değil. Ad önekinden çıkarım ise 473 API'nin 470'inde doğru, yani yüzde 99,4;
üç istisnası `file_system.directory_exists`, `file_system.file_exists` ve
`spotify.download_song`.

### K-18 — Tanımlayıcılar İngilizce, yorumlar Türkçe

**Karar.** Tablo ve sütun adları İngilizce, örneğin `episodes`, `run_id` ve
`verifier_results`. Şema dosyasındaki yorumlar Türkçe.

### K-36 — Adım düzeyi taksonomisi beş kategori taşıyor

**Bağlam.** Taksonomi üç kategoriyle başlamıştı: kod üretilmedi, ayrıştırılamadı,
bağlam taştı. Aşama 2 ölçümü bu üçüne girmeyen iki durum çıkardı ve ikisi de
sıfır eylemle sonuçlanıyor.

**Karar.** Beş kategori:

1. Kod üretilmedi.
2. Üretildi ama ayrıştırılamadı.
3. Bağlam taştı.
4. Üretildi, ayrıştırıldı, ama hiç eylem üretmeden yürütme hatası verdi.
5. Üretildi, ayrıştırıldı, yürütme başarılı oldu, ama yine de hiç eylem
   üretilmedi.

**Gerekçe.** Dördüncüsü ölçüldü: model `for playlist in playlists:` yazdı,
`playlists` tanımlı değildi, yürütme `NameError` ile düştü ve hiçbir çağrı
sunucuya ulaşmadı. Sıfır çağrılı epizot ile ajanın çağırmamayı seçtiği epizot
aynı şey değil, ayrı etiketlenmeleri gerekiyor.

Beşincisi aynı epizodun bir sonraki adımında çıktı. Model hatayı `playlists = []`
yazarak düzeltti. Döngü hiç dönmedi, ortam `Execution successful.` dedi ve model
görevi tamamlanmış saydı. Yürütme hatası modelin kod yazamadığını gösterir; boş
başarı ise modelin görevi sessizce etkisizleştirdiğini gösterir ve doğrulayıcıya
kadar hiçbir yerde alarm üretmez. Pilot verisinde ikincisi daha tehlikeli, çünkü
sağlıklı epizot gibi görünüyor.

Ölçümün tamamı `docs/appworld-facts.tr.md` içinde.

### K-38 — Epizotlar koşullara serpiştirilerek atanıyor

**Bağlam.** Kilitli plan epizotları koşullara bloklu koşuyor gibi duruyordu:
önce taban, sonra mekanizmalar. Aşama 2 ölçümü bunu tehlikeli kılıyor. Sunucu
durumundaki kayma epizot yörüngesini değiştirebiliyor ve bloklu koşuda o kayma
doğrudan koşul farkına dönüşür.

**Karar.** Epizotlar koşullara serpiştirilmiş atanacak, bloklu değil.

**Gerekçe.** Bloklu koşuda sunucu durumu ile koşul birbirine karışır ve ayırt
edilemez. Serpiştirme bu karışmayı kırıyor: kayma varsa bütün koşullara aynı
oranda dağılıyor.

### K-39 — Model yükleme durumu ve sıra numarası epizot başına kaydediliyor

**Karar.** `episodes` tablosu iki alan daha taşıyor: `model_load_state` ve
`sequence_in_run`.

**Gerekçe.** Yükleme durumu ölçülmüş bir gizli değişken; aynı görev soğuk
modelde 19, ısınmış modelde 1 API çağrısı üretti. Kaydedilmezse epizotlar arası
fark koşul farkı sanılır. Sıra numarası da koşu içindeki kaymayı sonradan ortak
değişken olarak sınamayı sağlıyor.

### K-40 — Çözülmeyen epizot tavanda sansürleniyor

**Bağlam.** Bu kural estimand kararının içindeydi ama "tavanda sansür" ifadesi
yalnız tavana çarpan epizotlar için anlaşılabilirdi.

**Karar.** Çözülmeyen epizot, gerçekte kaç adım sürerse sürsün tavan değeriyle
analize giriyor. Kendi adım sayısıyla girmiyor.

**Gerekçe.** K-36'nın beşinci kategorisi doğrudan bir metrik tehlikesi
üretiyor. Boş başarı epizodu üç model çağrısıyla bitiyor ve ham sayıda verimli
görünüyor. Mekanizmalar bu davranışı artırırsa birincil metrik onları
ödüllendirir. Sansür bu ödülü kesiyor.

---

## Model sunumu

### K-19 — `num_ctx` geçirme yolu ve iskeleye dokunmama kısıtının kapsamı

**Bağlam.** `num_ctx` Ollama'ya ulaşmazsa varsayılan bağlam penceresi çok küçük
kalır ve tasarım sessizce çöker. Dört yol var.

**Karar.** Sırayla:

1. **Önce denenecek.** litellm `ollama_chat/<etiket>` üzerinden
   `generation_kwargs` ile. İskeleye hiç dokunulmuyor.
2. **Geçmezse buna düşülecek.** Ollama'nın yerel `/api/chat` uç noktasına karşı
   kendi ince taşıma katmanımız.
3. **Tamamen elendi.** OpenAI uyumlu `/v1` ve `extra_body`. Sessizce yutma,
   tolere edemeyeceğimiz tek arıza biçimi.
4. **Tamamen elendi.** Modelfile'a `PARAMETER num_ctx` gömmek. Model kimliğini
   değiştiriyor ve parametreyi künyeden gizliyor.

**Kapsam açıklaması.** Referans iskeleyi değiştirmeme kısıtı ajan mantığını
kapsıyor, yani prompt'u, ayrıştırmayı ve döngüyü. Taşıma katmanını değiştirmek
iskeleyi değiştirmek sayılmıyor. Şart şu: aynı mesajlar gitsin ve aynı metin
dönsün.

**Sınanmamış izin, 14 Ağustos 2026.** Düşünmeyi kapatma işi sırasında bu
kapsam açıklaması ikinci kez uygulandı ve `LanguageModel` ile
`non_cached_lm_call` taşıma katmanı sayıldı: prompt kurmuyorlar, ajan çıktısı
ayrıştırmıyorlar, döngü yönetmiyorlar. Gerekçe sağlam görünüyor **ama karar
uygulanmadı**, çünkü değişiklik gerekmedi — iskelenin kendi kurduğu
`generation_kwargs` sözlüğüne değer koymak yetti ve iskelede tek satır
değişmedi.

Bu yüzden izin **sınanmamış** olarak kayda geçiyor. İleride gerçek bir iskele
değişikliği gündeme gelirse buradaki akıl yürütme emsal sayılmayacak, sıfırdan
tartışılacak. İzinler böyle genişler.

**Aşama 1 ölçümü, birinci yol `num_ctx` taşıyamıyor.** İskelenin `LanguageModel`
sınıfı hangi anahtarların geçebileceğini `litellm.completion` imzasından çıkarıp
beyaz liste uyguluyor ve listede olmayan her anahtar için `ValueError`
fırlatıyor. Listede 41 ad var. `num_ctx` yok, `api_base` de yok, onun yerine
`base_url` var. Yani litellm yolu bağlantıyı kuruyor ama bağlam penceresini
geçiremiyor. Birinci yol tamamen ölmedi, model çağrısı hâlâ oradan gidiyor. Ama
`num_ctx` için yetmiyor. Devamı A-05'te.

### K-20 — Sıcaklık 0.2, seed deterministik türetiliyor

**Karar.** Sıcaklık sabit ama sıfırdan büyük. Başlangıç değeri 0.2, kesin değer
kurulum aşamasında taranacak. Seed epizot başına ve deterministik, ~~`run_id`,
`task_id` ve `seed_index` üçlüsünden~~ **`task_id` ve `seed_index` ikilisinden**
türetiliyor.

**Aşama 4'te bulunan hata.** Üçlü kuralda `run_id` vardı ve `run_id` model adını
taşıyordu, yani her model farklı seed'le koşuyordu. Eşleştirilmiş tasarımda seed
bir bloklama faktörü: aynı görev ve aynı tohum indisi her modelde ve her koşulda
aynı seed'i vermeli. Aksi hâlde model farkı ile seed farkı iç içe geçer ve
ayrılamaz. Model de koşul da seed'e girmiyor.

İmza `tests/test_model_config.py` içinde ayrı bir testle sabitlendi; üçüncü bir
argüman geri gelirse test düşüyor.

**Gerekçe.** Sıfır sıcaklıkta seed anlamsızlaşır ve tohumlar arası yayılım ölür.
Oysa bütün istatistik planı o yayılıma dayanıyor. Ayrıca sıfır sıcaklıkta ajan
başarısız bir çağrıyı sonsuza kadar tekrarlar, çünkü dağılım değişmiyor.

**Aşama 2 ölçümü: seed geçiyor, oynaklığın kaynağı başkaymış.** Aşama 1'deki 19,
1, 19 dizisi rastgelelik değildi. litellm seed'i doğru geçiriyor; aynı seed'le
arka arkaya dört çağrı birebir aynı metni veriyor ve metin Ollama'nın kendi
ucundan gelenle eşleşiyor.

Ayrışan şey modelin bellekte yüklü olup olmaması. Soğuk yüklemeden sonraki ilk
çıkarım ısınmış hâldekinden farklı, ama kendi içinde kararlı. Epizot düzeyinde
de böyle: aynı görev soğuk modelle 19 API çağrısı ve tek bir yörünge özeti
veriyor, ısınmış modelle 1 çağrı ve başka bir özet. İki soğuk koşu birebir aynı,
iki ısınmış koşu birebir aynı.

Bunun sonucu K-21'i ilgilendiriyor ve ölçümü `docs/appworld-facts.tr.md` içinde.

### K-21 — `keep_alive` 30 dakika, model değiştirirken açık boşaltma

**Gerekçe.** 8 GB VRAM'e üç model aynı anda sığmıyor. Kabaca 1.1, 2.0 ve 4.7 GB,
üstüne 32k bağlam. Modeli süresiz tutmak, model değiştirmeyi elle boşaltmaya
mahkûm ediyor.

**Aşama 2 ölçümü kararı yeniden açıyor.** Epizotun yörüngesi modelin yüklü olup
olmamasına göre değişiyor ve fark küçük değil: aynı görev soğuk modelde 19,
ısınmış modelde 1 API çağrısı üretti. Ölçtüğüm tek güvenilir tekrarlanabilirlik
protokolü her epizottan önce modeli boşaltmak, yani `keep_alive` süresini
uzatmanın tam tersi.

**Aşama 5 maliyet ölçümü.** Model başına yükleme süresi, üçer ölçümün medyanı:

| Model | Medyan yükleme | VRAM |
|---|---|---|
| 1.5B | 2,72 s | 1,560 GiB |
| 3B | 3,01 s | 2,602 GiB |
| 7B | 3,55 s | 5,160 GiB |

Üç bin epizot üç modele eşit bölünürse soğuk protokolün toplam yükleme maliyeti
yaklaşık 9280 saniye, yani 2,6 saat. Epizot süreleri 24 ile 72 saniye arasında
ölçüldüğü için toplam koşu süresi 40 saatin üzerinde; yükleme payı kabaca yüzde
altı.

**Karar: soğuk rejim.** Her epizottan önce model boşaltılıyor.

**Gerekçe.** S-13 ısınmış rejimin tek bir durum olmadığını gösterdi. Elimizde
tekdüzeliği ölçülmüş tek seçenek soğuk rejim. Bedeli kırk saatlik bir koşuda
2,6 saat, yani yüzde altı; karşılığı ölçülmüş tekdüzelik.

**Birinci şart: tekdüzelik geniş örneklemde doğrulanacak.** Aşama 5'teki
doğrulama n=2 ve tek görevdeydi. Biriktirme başlamadan önce model başına on
soğuk epizot koşuluyor ve hepsinin birebir aynı yörüngeyi vermesi gerekiyor.

**İkinci şart: boşaltma ölçülecek, iddia edilmeyecek.** `model_load_state`
alanı kalıyor ve epizot başına modelin gerçekten boşaldığı sunucuya sorularak
doğrulanıyor. `unload_model` boşaltma isteğinden sonra `/api/ps` üzerinden
kontrol ediyor ve model hâlâ yüklüyse hata fırlatıyor. Boşaltma sessizce
başarısız olursa rejimler karışır ve fark edilmez.

### K-47 — Gereken determinizmin türü

**Karar.** Aynı görev, seed, koşul ve model dörtlüsünün tekrarında aynı sonuç.
Tohumlar arası fark **kalmalı**.

**Gerekçe.** Varyans kestirimimizin kaynağı tohumlar arası yayılım. Determinizm
o yayılımı öldürecek kadar ileri giderse istatistik planı çöker. Bu yüzden
tekdüzelik sınaması aynı anda iki şeye bakıyor: aynı dörtlü aynı sonucu
veriyor mu, ve ikinci bir tohum farklı sonuç veriyor mu. İkincisi olmadan
birincisi hiçbir şey kanıtlamaz.

### K-48 — Tekdüzelik tutmazsa ne yapılacağı, şimdiden yazılıyor

**Karar.** ~~On epizotluk sınama düşerse determinizm hedefinden vazgeçiliyor ve
model yükleme durumu yalnız kaydedilen bir ortak değişkene indiriliyor.~~
Sınama 7B'de düştü ve karar K-51'e taşındı.

**Gerekçe.** Bu kural sonuç görülmeden yazıldı. Sonradan yazılsaydı, çıkan
sonuca göre uydurulmuş olurdu.

### K-51 — Determinizm varsayılmıyor, artık varyans ölçülüyor

**Bağlam.** K-48 iki seçenek sunuyordu: determinizmi varsaymak ya da ondan
tümden vazgeçmek. On epizotluk ölçüm 1.5B ve 3B'de tekdüzelik verdi, 7B'de
vermedi. İkili seçim burada yanlış çerçeve.

**Karar.** Determinizm bir analiz varsayımı olarak alınmıyor. Analizin tek
gerçek bağımlılığı gerileme tespitindeki gürültü kuralı: bir görev,
eşleştirilmiş farkı kendi tohumlar arası yayılımını aşıyorsa gerilemiş
sayılıyor.

Aynı görev, seed, koşul ve model dörtlüsü birkaç kez tekrarlanıp **artık
varyans model başına ölçülüyor** ve gürültü tabanına ekleniyor. Yöntem üç
modelde aynı, büyüklük modele göre değişiyor ve ölçülmüş oluyor.

**Gerekçe.** Determinizm yoksa tohum yayılımı toplam gürültüyü olduğundan küçük
gösterir ve gereğinden fazla gerileme işaretlenir. Artık varyansı ölçüp tabana
eklemek bu sapmayı kaynağında kapatıyor. 1.5B ve 3B'de sıfır çıkarsa katkısı
kendiliğinden sıfır olur, 7B'de ne çıkarsa hesaba girer. Ne determinizmden
vazgeçilmiş oluyor ne de olmayan bir tekdüzelik varsayılıyor.

**Sonucu.** Pilota tekrar koşuları ekleniyor. `REPRODUCE.md` de dürüst
konuşuyor: 1.5B ve 3B birebir, 7B ölçülmüş varyans içinde tekrarlanabilir.

### K-49 — Bir şeyin çalıştığını gördüğünde, doğru sebeple mi çalıştığını ayrıca sor

**Bağlam.** Aynı arıza sınıfı kurulum boyunca beş kez tekrarlandı ve beşi de
"yeşil görünen ölçüm" biçimindeydi.

1. Mutasyon betiği kirli zeminde koştu; ikinci ve üçüncü mutasyon hiç
   sınanmadı ama çıktı düzgün göründü.
2. API yakalayıcısının ilk hâli kaydı `raise` sonrasında alıyordu; yedi
   çağrının yedisi de 200 raporlandı, oysa ikisi başarısızdı.
3. Künye WSL sınırından sessizce `None` okudu; koşu yeşil bitti.
4. Ölçüm betiği epizot yazıp adım yazmadı; `total_model_calls` 20 diyordu ama
   adım satırı yoktu.
5. Slot Jinja değişkeni olsaydı parametre geçirilmeden de çalışırdı, ama
   tanımsız değişkenin sessizce boş render edilmesi sayesinde.

**Karar.** Bir şeyin çalıştığı görüldüğünde, doğru sebeple mi çalıştığı ayrıca
sorulacak. Pratikte üç alışkanlık: sınamayı bir kez de bozarak koş, yeşil
sonucun hangi varsayıma dayandığını yaz, ve sessizce çalışan hiçbir şeye
dayanma.

### K-22 — Ollama sunucusu betikten ve oturumdan bağımsız başlatılıyor

**Karar.** Tepsi uygulaması kapatılacak, `ollama serve` kendi betiğimizden
başlatılacak. Betik sunucuyu çağıran oturumdan bağımsız bir süreç olarak
açacak.

**Gerekçe.** `OLLAMA_KV_CACHE_TYPE` ve `OLLAMA_FLASH_ATTENTION` sunucu sürecine
geçmeli, istemciye değil. Betikten başlatmak ayarların künyede
kanıtlanabilmesini sağlıyor.

Oturum bağımsızlığı şartı Aşama 1'de ölçülerek eklendi. Sunucuyu oturuma bağlı
bir arka plan süreci olarak başlattığımda iki kez düştü. Uzun bir koşunun
ortasında sunucunun kaybolması sessiz veri kaybı demek: epizotlar düşer, kayıt
yarım kalır ve bunu ancak sonradan fark edersin.

### K-37 — `num_ctx` sunucu tarafında, ama koşu başına doğrulanarak

**Bağlam.** A-05 açık soru olarak duruyordu. K-19'un birinci yolu `num_ctx`
taşıyamıyor, çünkü iskele beyaz listesini `litellm.completion` imzasından
çıkarıyor ve `num_ctx` o listede yok.

**Karar.** Bağlam penceresi sunucu tarafındaki `OLLAMA_CONTEXT_LENGTH` ortam
değişkeniyle veriliyor. İskelenin beyaz listesi değiştirilmiyor, çünkü o
iskeleye dokunmak olur.

**İki şartı var ve ikisi de zorunlu.**

1. Her koşudan önce sunucuya sorulup etkin bağlam penceresinin gerçekten 32768
   olduğu doğrulanacak. Tutmuyorsa koşu yüksek sesle düşecek.
2. Sunucu ortamı künyeye yazılacak.

**Gerekçe.** Bu ayar depo dışında yaşıyor. Sunucu bir kez ortam değişkeni
olmadan yeniden başlarsa her şey sessizce 4096'ya döner ve ölçüm bozulur ama
hiçbir yerde hata görünmez. Sessiz dönüş tolere edemeyeceğimiz tek arıza biçimi,
koşu başına doğrulama bu yüzden şart.

Modelfile'a gömmekten farkı da burada. Değer sunucunun kendi yapılandırma
dökümünde açıkça duruyor ve model kimliğine dokunmuyor.

**Doğrulama protokolü yükleme protokolünden türüyor, bağımsız karar değil.**
Aşama 3'te ölçüldü: `/api/ps` yalnız o an yüklü modeli bildiriyor, yani
pencereyi okumak modeli yüklemeyi gerektiriyor ve doğrulamanın kendisi modeli
ısıtıyor. İki karar bu yüzden birbirine bağlı.

- Isınmış rejim seçilirse yükleme dönemi başına tek doğrulama yeter ve dönem
  kimliği epizoda yazılır.
- Soğuk rejim seçilirse doğrula, boşalt, başlat zaten bedava.

Şu anki geçici çözüm ikincisi. Kalıcı hâli S-13 ile birlikte, K-21'in nihai
kararıyla aynı anda belirlenecek.

---

## İskele ve slot

### K-23 — Prompt dosyası depoya kopyalanıyor

**Karar.** `react_code_agent/instructions.txt` depoya kopyalanacak, slot kopyaya
eklenecek, `prompt_file_path` kopyayı gösterecek. `site-packages` içindeki
dosyaya dokunulmayacak.

**Gerekçe.** Temiz kurulumda tekrarlanabilirlik.

### K-24 — Slot konumu yönergelerden sonra, görev talimatından önce

**Karar.** Slot statik konumda duruyor ve tur başına değişmiyor. Konum config'den
okunabiliyor ama şimdilik tek değerde sabit.

**Gerekçe.** Statik konum prefix cache'i bozmuyor.

### K-25 — Boş slot bayt bayına aynı prompt üretiyor

**Karar.** Slot boşken hiçbir şey basmayacak, fazladan satır sonu bile
bırakmayacak.

**Gerekçe.** Aksi hâlde tokenleştirme değişir ve aynı yörünge ölçütü tesadüfen
bozulur.

### K-26 — İskelenin kendi kesme mantığına şimdilik dokunulmuyor

**Bağlam.** Referans iskelenin `trimmed_messages` özelliği eski gözlemleri
`[NOT SHOWN FOR BREVITY]` ile değiştiriyor. Yani iskelenin kendi bağlam kesme
mantığı var.

**Karar.** Şimdilik dokunulmuyor, bağlam kesme kapsam dışı.

**Risk kaydı.** Bizim bağlam montajcımız geldiğinde iki kesme mantığı çakışacak.
Şimdi çözülmüyor, çakışma riski olarak kaydediliyor.

---

## Koşul yapılandırması

Bu bölümde koşullar Türkçe adlarıyla anılıyor. Karşılıkları şöyle: taban
(`baseline`), sadece beceriler (`skills`), sadece hatalar (`failures`), ikisi
birden (`skills_failures`), alakasız getirme (`irrelevant_retrieval`), naif
derleyici (`naive_compiler`).

### K-28 — `retrieval.mode` getirme yöntemini taşıyor, içerik alakasını değil

**Bağlam.** Alan başlangıçta `none` ve `standard` değerleriyle yazılmıştı ve
`skills.source` ile `failures.source` alanlarıyla aynı ekseni, yani içerik
alakasını taşıyormuş gibi duruyordu. Aynı eksenin iki yerde durması çelişme
imkânı yaratıyordu. `retrieval.mode = none` ile `skills.source = standard` bir
arada yazılabiliyordu ve bunun ne anlama geldiği tanımsızdı.

**Karar.** İki değer: `none` ve `symbolic`. İçerik alakası yalnız `skills.source`
ve `failures.source` alanlarında. `none` yalnız tabanda, kalan beş koşulda
`symbolic`.

**Gerekçe.** Alan artık tek bir soruyu cevaplıyor: getirme hangi yöntemle
yapılıyor. İleride hibrit getirme denenirse bu alan üçüncü değeri alır ve içerik
ekseni buna hiç karışmaz.

### K-29 — `fill.enabled` taban dışında bütün koşullarda açık

**Karar.** Taban kapalı, kalan beşi açık.

**Gerekçe.** Kart taşıyan beş koşul görev başına aynı kart sayısını alıyor ve
eksik slotlar dolguyla tamamlanıyor. Somut örneği şu: sadece beceriler koşulunun
hata slotları dolguyla doluyor. Dolmasaydı ikisi birden koşuluyla kart sayısı
eşitlenmez, iki koşul arasındaki fark içerikten çıkıp hacme kayardı. Taban sıfır
kart aldığı için dolgunun orada işi yok.

### K-30 — `failures.source` üç değer taşıyor

**Karar.** `none`, `standard` ve `irrelevant`. `naive` yok.

**Gerekçe.** Naif hata indeksi diye bir şey yok. Naif derleyici yalnız beceri
üretiyor ve naif derleyici koşulu yalnız sadece beceriler koşuluyla eşleşiyor.
Kullanılmayan enum değeri eklenmiyor, çünkü duran değeri birileri kullanmaya
kalkar.

### K-31 — İki kritik kontrast

**Karar.** Aşağıdaki iki kontrast analiz planının taşıyıcısı. Bozulmaları serbest
bırakılmıyor, testle korunuyorlar.

1. Taban ile alakasız getirme arasındaki fark **saf bağlam hacmi**. İkisi de
   alakalı içerik taşımıyor. Biri gerçek kart taşımaya başlarsa fark hacim
   olmaktan çıkar.
2. Sadece beceriler ile alakasız getirme arasındaki fark **saf içerik**. İkisi
   yalnız `skills.source` alanında ayrılıyor. İkinci bir alan da ayrışırsa
   kontrast sessizce anlamını yitirir.

**Gerekçe.** Bu ikisi bozulursa analiz planının tamamı çöker. Belgede iddia
olarak durmaları yetmiyor. `test_pure_volume_contrast_carries_no_relevant_content`
ve `test_pure_content_contrast_differs_in_one_field_only` bunları makine
tarafından denetliyor.

Bir not: saf içerik kontrastı daha önce ikisi birden ile alakasız getirme çifti
olarak yazılmıştı. Yanlıştı, çünkü o çift iki alanda birden ayrışıyor ve tek
eksenli değil.

---

## Aşama ölçütleri ve raporlama

### K-27 — Aşama raporları iki yerde

**Karar.** Asıl yer PR açıklaması. Aynı metin `docs/reports/asama-N.md` altına da
düşüyor.

**Gerekçe.** PR açıklaması gözden geçirmenin olduğu yer, depo kopyası ise
kalıcılık için.

### K-32 — Temiz makine doğrulaması Aşama 1'de AppWorld dahil tekrarlanıyor

**Bağlam.** K-07 gereği AppWorld Aşama 0'ın kilidine girmedi. Doğru karardı ama
bir sonucu oldu: Aşama 0'ın temiz makinede kurulabilme ölçütü, projenin asıl ağır
bağımlılığını hiç sınamadı.

**Karar.** Aşama 1'in kabul ölçütüne ekleniyor. Temiz makinede kurulum AppWorld
dahil yeniden doğrulanacak, Git LFS önkoşulu REPRODUCE.md'ye yazılacak.

### K-33 — Durum ve gözden geçirme dosyaları

**Karar.** Altı dosya iskelete taslak olarak giriyor: `PROJECT_STATUS.md`,
`REPRODUCE.md`, `PILOT_REPORT.md`, `docs/10-external-review.tr.md`,
`docs/11-falsification.tr.md` ve `experiments/decisions.csv`.

İlk üçü danışmanın asgari listesinde vardı ve bizde yoktu. Son üçü o asgarinin
üstüne eklendi.

`PROJECT_STATUS.md` bileşen, durum, kanıt ve eksik sütunlarını taşıyor. Her aşama
sonunda güncelleniyor, ilk satırı Aşama 0'dan doldu.

**İçerik taşıyan üç şey kendi aşamasına bağlı, şimdi yazılmıyor.**
`shield_violations` tablosu Aşama 3'te şemaya girecek, `DATA_MODEL.md` Aşama 3'ün
çıktısı olacak, REPRODUCE.md'nin içi Aşama 1'de dolacak.

### K-42 — Biriktirme havuzu ve değerlendirme örneklemi ön kayda giriyor

**Bağlam.** Aşama 2 ölçtü: train ve dev'in 147 görevi, ortamdaki on bir
kullanıcı uygulamasının yalnız beşine dokunuyor. `spotify`, `phone`, `venmo`,
`file_system` ve `simple_note`. Geriye kalan dördü, yani `amazon`, `gmail`,
`splitwise` ve `todoist`, eğitim tarafında hiç geçmiyor.

**Karar, nihai hâli.** Dört madde ön kayda giriyor.

1. **Zorluk bölmesi bütün ve dokunulmamış kalıyor.** Biriktirme oradan
   yapılmayacak.
2. Biriktirme train, dev ve kullanılmayan normal test görevlerinden.
3. Değerlendirme normal testten, örneklem biriktirmede temsil edilen
   uygulamalarla sınırlı.
4. Uygulamalar arası aktarım ölçümü erişilebilir 37 görevle koşacak ve küçük
   n'iyle birlikte raporlanacak.

**Gerekçe.** Zorluk bölmesi elimizdeki tek gerçekten görülmemiş uygulama
verisi. Onu ikincil bir ölçümün örneklemini büyütmek için harcamak, tek temiz
uygulamalar arası testi yok etmek demek. Üstelik o ölçümde beceriler için
sıfıra yakın sonuç zaten önceden yazılı, yani büyük n'in getirisi düşük.
Dürüstçe raporlanmış 37, artık ayrılmış olmayan 193'ten iyi.

**Gerekçe.** Havuz beş uygulamayla sınırlı kalır ve değerlendirme daha geniş
bir kümede yapılırsa kapsama oranı çöker; beceriler yapısal olarak ateşleyemez.
Bu, mekanizmanın işe yaramadığı sonucunu değil, mekanizmanın hiç denenmediği
sonucunu üretir ve ikisi karıştırılamaz.

Aynı ölçüm ezberleme kapısı kararını da destekliyor. Zorluk bölmesindeki fark
gerçekten görülmemiş uygulama, yani dağılım içi görülmüş ile görülmemiş görev
ayrımı yapay değil.

**Ölçülmüş taban.** Kuralın maliyeti sayıldı. "Değerlendirme örneklemi yalnız
biriktirmede temsil edilen uygulamalardan çekilir" kuralı uygulandığında zorluk
bölmesinden kaç görev ayakta kalıyor:

| Havuz | Uygulama | test_normal | test_challenge |
|---|---|---|---|
| Yalnız train + dev | 5 | 141/168 | **37/417** |
| + test_normal'ın tamamı | 8 | 165/168 | **193/417** |
| Bütün kullanıcı uygulamaları | 9 | 165/168 | 405/417 |

Havuz genişletilmezse zorluk bölmesinin yüzde dokuzu kalıyor. Genişletme
zorunluluk, doğrulanmış hâliyle.

**Yapısal sorun: `amazon` yalnız zorluk bölmesinden erişilebiliyor.** Zorluk
bölmesini en çok açan uygulama o, tek başına 185 görev getiriyor. Ama `amazon`
train'de, dev'de ve test_normal'da hiç geçmiyor. Havuza girmesinin tek yolu
zorluk görevleri üzerinde biriktirme yapmak, o da görülmemiş görev özelliğini
bozar.

Sonuç olarak biriktirmeyle erişilebilen tavan sekiz uygulama ve 193/417.
`amazon`'a dokunan 212 zorluk görevi, kural korunursa değerlendirme örnekleminin
dışında kalıyor.

Diğer üçünün katkısı: `gmail` +150 görev ve test_normal'da üç görevde geçtiği
için havuza girebiliyor. `todoist` +3, `splitwise` +0.

**Sınırı.** Test bölmelerindeki uygulama adları vekil ölçümden geliyor, tam
isabet yüzde 75,5. Yön güvenilir, çünkü vekil `amazon`, `splitwise` ve
`todoist` için hiç fazladan sayma yapmadı. Kesin sayılar bu belirsizliği
taşıyor.

### K-35 — Yerel-yalnız kontroller listelenip her birleşmeden önce koşuluyor

**Bağlam.** `appworld` işaretli testler indirilmiş 198 MB veri istiyor ve CI'da
koşmuyor. Aralarında epizot başına veritabanı sıfırlaması var. Bu projenin en
önemli değişmezlerinden biri ve makine koruması altında değil.

**Karar.** Veriyi CI'a indirmiyoruz, maliyeti karşılamıyor. Bunun yerine
yerel-yalnız kontrollerin listesi REPRODUCE.md içinde duruyor,
`scripts/local_checks.sh` onları tek komutla koşturuyor ve her aşama raporu bu
çıktının en son ne zaman, hangi commit'te ve hangi sonuçla alındığını yazıyor.

**Gerekçe.** Liste tutulmazsa altı hafta sonra o testin en son ne zaman geçtiğini
kimse bilmez. Koşulduğu tarihin rapora yazılması, koşuldu iddiasını
denetlenebilir kılan şeydir.

---

## Kurulum sonrası sıra

### K-50 — Bağımlılık zinciri ve ön kaydın donma kuralı

**Karar.** Kurulum sonrası iş şu sırayla yürüyor. Sıra keyfî değil, her adım
öncekinin çıktısına bağlı.

1. **S-16 bağlanması.** Zincirin kapısı. Yanıt verisi olmadan yapılan hiçbir
   biriktirme hata indeksi madenciliğine yaramaz ve geriye dönük eklenemez.
2. **K-42'nin iki maddesinin karara bağlanması.** Havuz tanımı neyin
   biriktirileceğini belirliyor.
3. **Önyükleme biriktirmesi.** Yalnız taban koşuluyla koşulan küçük bir
   biriktirme, ilk kütüphaneyi çıkarmaya yetecek kadar.
4. Derleyici, getirici, hata indeksi ve kalkan.
5. Kurulum aşaması taramaları.
6. Pilot.
7. Tam biriktirme ve ana koşu.

**Önyükleme neden gerekli.** Planda açıkça yazmıyordu ve bir döngü vardı. Pilot
taban ile mekanizmaların birlikte koşmasını gerektiriyor, çünkü güç hesabı
farkın varyansını istiyor. Ama mekanizmalar madencilik için korpus istiyor.
Döngüyü kıran şey yalnız tabanla koşulan küçük bir biriktirme.

**Ön kayıt ne zaman donuyor: kural donuyor, sayılar donmuyor.**

Ön kayda giren, yani sonuç görülmeden kilitlenen: hipotez, birincil hücre,
estimand, bölme kuralı, dışlama kuralları, analiz planı, eşikler ve terk
kriterleri.

Değeri kurulum aşamasının doldurduğu, ama **karar kuralı** ön kayda yazılan:
adım tavanı çarpanı, sıcaklık, madencilik eşikleri ve D14 katılığı. Bunlar için
ön kayıt "şu değer" demiyor, "şu ölçüme göre şöyle seçilecek" diyor. Ayar
bütçesi de orada ilan ediliyor.

### K-52 — Önyükleme biriktirmesi deneyin parçası değil

**Karar.** Zincirin üçüncü adımındaki biriktirme bir ölçüm değil, bir yapım
işi. Amacı derleyiciyi, getiriciyi ve hata indeksini yazıp hatalarını
temizlemek. Oradan çıkan kütüphane hiçbir değerlendirmeye girmiyor: ne beceri
kartı, ne hata indeksi girdisi, ne de eşik ayarı için sayı olarak.

**Somut kural.** Önyükleme koşularının `run_id` öneki `bootstrap-`. Derleyici
çalıştığı doğrulandıktan sonra o kütüphane atılıyor ve gerçek biriktirme
K-42'nin havuzuyla sıfırdan koşuluyor. Ön kayda giren sayıların hiçbiri
`bootstrap-` önekli koşulardan gelemez.

**Sebep.** Aynı epizotlar hem aracı ayarlamak hem de aracın çıktısını ölçmek
için kullanılırsa ölçüm kendi ayar kümesinde yapılmış olur. Kütüphanenin
kalitesi de o epizotlara aşırı uyar. Ayrımı şimdi yazmanın maliyeti bir önek,
sonra fark etmenin maliyeti biriktirmenin tekrarı.

### K-53 — İki ayrı nicelik: tavana çarpma oranı ve sansür oranı

**Düzeltme.** Bu madde iki niceliği tek isim altında birleştirmişti ve
birleştirme yanlıştı. Ayrılıyorlar.

**Tavana çarpma oranı bir ölçüm artefaktı.** Epizodun adım tavanına dayanıp
kesilmesi, görevin çözülemediğini değil, bizim koyduğumuz sınırın bağladığını
gösteriyor. Bu oran %10'un altında kalmalı ve tavan çarpanı `k` buna göre
seçiliyor (K-43). Ölçüt burada, çünkü ölçtüğü şey düzeneğin kendisi.

**Sansür oranı bir sonuç.** Doğrulayıcının geçirmediği her epizot sansürlüdür.
Bu bir artefakt değil, modelin o görev kümesindeki performansı. **%10 kuralı
buna uygulanmaz.** Uygulansaydı taban koşuluna %90 başarı şartı koymuş olurduk,
ki hiçbir modelin karşılamadığı ve karşılaması da beklenmeyen bir şart.

**Eksende kalma ölçütü hangisine bakıyor.** Model eksende kalıp kalmayacağına
sansür oranıyla karar veriliyor, ama eşik %10 değil. Eşik, eşleştirilmiş
tasarımın bir şey söyleyebilmesi için gereken taban başarısından geliyor ve
değeri pilottan çıkacak; kaba aday eleme eşiği taban başarısının %25'in
üstünde olması.

**Sansürü doğrulayıcının hükmü tanımlıyor, sonlanma sebebi değil.**
Doğrulayıcının geçirmediği her epizot sansürlüdür.

Tanım iki kez sonlanma sebepleri sayılarak yazılmıştı: başta yalnız
`step_ceiling`, sonra `no_progress` de eklenerek. İkisi de eksik. Sebep listesi
ajanın görevi
bitirdiğini bildirip doğrulayıcıdan kaldığı hâli kaçırıyor, ve o hâl K-36'nın
beşinci kategorisinin kendisi: 7B'nin en çok ürettiği arıza biçimi. Sebeple
tanımlanan bir sansür, en yetenekli modelimizin baskın arızasını sansürsüz
sayardı.

İkinci sakınca bakımda. Sebeple tanımlanan sansür her yeni sonlanma yolunda
güncellenmek zorunda kalır ve güncelleme unutulduğunda sansür oranı sessizce
küçülür. Hükümle tanımlandığında yeni bir sonlanma yolu tanımı hiç
ilgilendirmiyor.

`termination_reason` ayrı bir tanı alanı olarak duruyor: sansürlü epizotların
hangi yoldan sansürlendiği raporlanıyor, ama ölçüt o dağılıma bakmıyor.

`verifier_results.passed` üç hâl taşıyor ve üçüncüsü tanıma girmiyor. `NULL`
"geçmedi" demek değil, "hüküm okunamadı" demek. Analize giren hiçbir epizotta
`NULL` bulunmamalı; bulunursa bu bir ölçüm arızasıdır ve sansür sayısının içine
yutulmamalı.

**Sebep.** Tanı ile ölçüt aynı şey değil. Hiçbir görevi çözmeyen bir model
tanısı ne olursa olsun %100 sansür üretir ve sansürlü veriden kazanç
kestirilemez. 3B'nin baskın hatası ayrı bir bulgu, ama eksende kalmasına o
bulgu değil bu oran karar veriyor.

**Aşağıdaki ölçüm bağlayıcı bir tavanla yapıldı.** Beş görevin çapaları 10 ile
195 arasındayken tavan hepsinde sabit 20'ydi (S-22). Yani o tabloda tavana
çarpma ile sansür iç içe geçmiş durumda ve tablo yalnız "ölçüt karşılanmıyor"
sonucunu taşıyor, oranın kendisini değil.

**Ölçüm.** Beş görev, model başına görev başına bir soğuk epizot, taban koşulu,
durma kuralı açık:

| Model | Epizot | Doğrulayıcıdan geçen | Sansür | %95 alt sınır |
|---|---|---|---|---|
| 1.5B | 5 | 0 | %100 | %54,9 |
| 3B | 5 | 0 | %100 | %54,9 |
| 7B | 5 | 0 | %100 | %54,9 |

Üç modelde de ölçüt karşılanmıyor ve fark küçük değil: alt sınır %54,9, ölçüt
%10'un altını istiyor. Beklenen sonuç 1.5B ve 3B içindi; **7B'nin de aynı yere
düşmesi beklenmiyordu.** Bunun anlamı, bu beş görevde ölçek ekseninin hiçbir
noktasında birincil metrik tanımlı değil, yalnız tanı metrikleri çalışıyor.

Ölçümün kapsamı S-22'de yazılı: beş görev rastgele örneklem değil ve model
başına bir epizot var. Eksenin tümüyle düşüp düşmediğine pilotun kendi
örnekleminde bakılacak; buradan çıkan, "7B sorun değil" varsayımının artık
dayanaksız olduğu.

**Bağlantı.** Ölçüt S-14'ün azaltmasını sayısallaştırıyor: eksen daralması
artık pilotun yorumuna değil tek bir orana bağlı. K-40 ile ikisi aynı tanımın
iki yarısı: burası hangi epizodun sansürlü olduğunu söylüyor, K-40 o epizodun
analize hangi değerle girdiğini.

### K-54 — Kategori 4 oranı koşul başına raporlanıyor

**Karar.** K-36'nın dördüncü kategorisi — kod çalıştı ama hiç API çağrısı
üretmedi — her koşul için ayrı bir tanı metriği olarak raporlanıyor.

**Sebep.** Bu kategori mekanizmanın çalışıp çalışmadığını başarı oranından önce
gösteriyor. Beceri kartı ya da hata indeksi işe yarıyorsa etkisini önce burada
göstermeli: ajan doğru API'yi çağırmaya başlamalı. Başarı oranı değişmeden
kategori 4 oranı düşerse mekanizma çalışıyor ama yetmiyor demektir; ikisi de
sabit kalırsa mekanizma hiç tutmamış demektir. Tek sayıya bakınca bu iki durum
ayırt edilemiyor.

**İki rejim, iki ayrı kullanım.** Kategori 4 oranı iki yerde ölçülüyor ve
sayıları birbirinin yerine geçmiyor.

Ana deneyde oran durma kuralı **açıkken** ölçülüyor, çünkü deney o rejimde
koşuyor. Kural erken adımları kestiği için oran eşiğe koşullu; ama koşullama
bütün koşullarda aynı olduğundan koşullar arası karşılaştırma geçerli kalıyor.
Mekanizmanın etkisi zaten farkta aranıyor, düzeyde değil.

Kural **kapalıyken** ölçüm yalnız kurulum aşamasının eşik seçimine hizmet
ediyor: kesilen epizotlar sonraki adımlarda toparlanıyor mu, yani eşik gerçek
bir tıkanmayı mı kesiyor yoksa yavaş bir başlangıcı mı. Oradan çıkan oran ana
deneyin sayısı değil, eşiğin gerekçesi.

Makalede her oranın hangi rejimden geldiği yazılıyor ve iki rejimin sayıları
aynı tabloda yan yana konmuyor.

### K-55 — Güç hesabı çıkarılan nicelik üzerinden

**Karar.** Güç hesabı ham başarı farkı üzerinden değil, mekanizmanın doğrudan
etkilediği nicelik üzerinden yapılıyor: kategori 4 oranındaki düşüş ve doğru
API'ye ulaşan adım oranı.

**Sebep.** Ham kazanç, mekanizmanın etkisini modelin görevi bitirme
yeteneğinden geçirerek ölçüyor. Taban etkisine yapışmış bir modelde o geçiş
sinyali yutuyor: doğru çağrıyı bulsa bile görevi bitiremediği için kazanç
sıfır görünüyor. Çıkarılan nicelik aradaki katmanı atlıyor, dolayısıyla aynı
örneklem büyüklüğünde daha yüksek güç veriyor.

### K-56 — İlgisiz getirme koşulu isteğe bağlı değil, taşıyıcı

**Karar.** `irrelevant_retrieval` koşulu ana tasarımda zorunlu. Pilot bütçesi
daralırsa kesilecek koşullar listesinde değil.

**Sebep.** S-19 şu riski işaret ediyordu: mekanizmanın etkisi kartın içeriğinden
değil, bağlama fazladan bir metin eklenmesinden gelebilir. Küçük modellerde 3B
bulgusundan sonra bu risk soyut olmaktan çıktı — yönergedeki tek iyi biçimli
örnek baskın hatayı kapatabiliyorsa, kartın kendisi de aynı işi biçim olarak
yapıyor olabilir. İçerik ile varlığı ayıran tek koşul bu, çünkü
`skills ↔ irrelevant_retrieval` karşıtlığı kart uzunluğunu ve konumunu sabit
tutup yalnız içeriği bozuyor. Koşul düşerse ana iddia yorumlanamaz hâle gelir.

### K-57 — Önyükleme biriktirmesi durduruldu, önce bant taraması

**Karar.** Zincirin üçüncü adımı, yani derleyiciyi kurup önyükleme korpusu
biriktirme işi, durduruldu. Yerine ölçülebilir bant taraması koşuyor.

**Sebep analiz değil, mekanizmanın kendisi.** Beceriler yalnız başarılı
epizotlardan madenciliyor. Sansür ölçümünde üç modelin üçü de hiçbir görevi
geçmedi, yani madencilenecek korpus yok. Derleyiciyi kurup ona boş bir korpus
vermek, derleyicinin çalıştığını da göstermez: boş girdide her derleyici boş
çıktı verir.

**Taramanın soracağı dört sayı.** Referans uzunluk bandına göre başarı oranı;
en kısa bantta kaç görev olduğu; kısmi tamamlamanın dereceli olup olmadığı; ve
geçen epizotlarda harcanan model çağrısı. Sonuncusu bant varsa K-43'ün
çarpanını da veriyor.

**Bant çıkmazsa üç yol var, ikisi yaşayabilir.**

1. **Değerlendirme örneklemini kısa görevlerden çekmek.** `num_api_calls` 732
   görevin hepsinde dolu, yani tabakalama bedava. Ön kayda yazılabilir kural:
   örneklem referans uzunluğu şu eşiğin altındaki görevlerden çekilmiştir,
   çünkü bu model sınıfı uzun görevleri tamamlayamıyor. En pratik yol.
2. **Sonucu ikili başarıdan kısmi ilerlemeye çevirmek.** Hipotez "çözüm için
   gereken çağrı" yerine "çağrı başına ilerleme" olur. Ön kaydın yeniden
   yazılmasını gerektiriyor.
3. **Birincil hücreyi yerel olmayan bir modele taşımak.** Son çare; yerel ve
   küçük çerçevesini bozuyor.

**Kısmi ilerleme ölçülebilir.** AppWorld'ün resmî ölçütü ikili:
`task_goal_completion` görev başına `success` boole'unun yüzdesi,
`scenario_goal_completion` ise senaryo içindeki minimum. Ama `TestTracker` her
gereksinimi etiketliyor. `no_op_fail` etiketli test, hiçbir şey yapmayan ajanın
düşürdüğü test; `no_op_pass` etiketli test hiçbir şey yapmasa da geçen test.
Dereceli skor `no_op_fail` testlerinin geçilen oranı olarak kuruluyor ve
önemsiz geçişleri dışarıda bırakıyor.

Sansür ölçümündeki on beş epizotta bu skor sıfır: 48 testin 41'i `no_op_fail`,
7'si `no_op_pass`, ve geçen yedi testin yedisi de `no_op_pass`. Yani ikili
başarı sıfırken kısmi ilerleme de sıfırdı.

### K-58 — Ön koşul kapısı: taban çözemiyorsa hipotez test edilmemiştir

**Karar.** Mekanizma koşullarından önce taban koşulu ayrılmış bir görev
kümesinde koşuluyor. Taban ilan edilmiş asgari başarı oranını tutturamazsa
deney hipotezi test etmemiştir ve mekanizma sonuçları raporlanmaz.

**Kapının üç parçası.**

1. **Ayrılmış küme.** Kapı için ayrılan görevler değerlendirme örnekleminin
   dışında. Ayrı olmak zorunda: aynı görevlerden hem kapı hem sonuç çıkarılırsa
   kapı değerlendirme örneklemini tüketir ve seçim sonuca sızar.
2. **İlan edilmiş asgari oran.** Sayı, güç hesabının varsaydığı taban oranı.
   Gözlenen taban onun altındaysa çalışma kurgu gereği güçsüzdür; kapı bunu
   veri görülmeden değil, sayı ilan edildikten sonra ölçüyor. Değer ön kayıt
   dondurulurken yazılıyor, kural şimdi donuyor.
3. **Geçilmezse ne yayımlanır.** Kapının kendisi, tanı metrikleri ve düzeneğin
   çalıştığının kanıtı. Mekanizma karşılaştırması yayımlanmaz — ne olumlu ne
   olumsuz, çünkü ölçülemeyen bir farkın işareti de yorumlanamaz.

**Sebep.** Bütün analiz planı "çözülmüş görev var" ön koşulunun üzerinde
duruyor: estimand, sansür kuralı, totoloji tartışması, çıkarıcı kontrol, güç
hesabı. Ön koşul on üç gün boyunca sınanmadı ve bant taraması otuz görevde sıfır
geçiş buldu.

**Neden şimdi yazılıyor.** Kapı sonuçtan sonra eklenirse post-hoc gerekçe gibi
görünür ve haklı olarak öyle okunur. Kural, sonucu bilmediğimiz bir koşu için
şimdi donuyor.

**Kapı ölçülürken bütçe bağlayıcı olmamalı.** Sınır kontrolünde ölçüldü: aynı
model, aynı görevler, yalnız çıktı bütçesi değişince geçen görev 6/30'dan
20/30'a çıktı (S-26). Bağlayıcı bir bütçe altında ölçülen kapı, hipotezi değil
yapılandırmayı sınar. Kapı koşusunda kodsuz adım oranı raporlanıyor; sıfıra
yakın değilse kapı geçersiz sayılıyor.

**Bağlantı.** K-53 aynı fikrin model düzeyindeki hâli: sansür oranı yüksekse o
model eksende kalmıyor. K-58 deney düzeyinde: taban çözemiyorsa deney
raporlanmıyor.

### K-69 — Kalkan okumayı kapsamıyor, ve gerekçesi ölçüldü

**Karar.** Kalkanın birinci aşama yüklemi yalnız **yazmayı** süzüyor. Okuma her
uygulamada koşulsuz serbest.

**Bu, dış incelemenin R3 itirazının reddini iptal etmek değil, o kararın kendi
şartının işlemesi.** R3 geri alınırken şart konmuştu: yanlış pozitif artacağı
için gölge modu ölçümünden geçecek. Ölçüm gölge modundan önce geldi ve hayır
dedi.

**Ölçüm.** Kalkanın izinli uygulama kümesi görev metninden çıkarılıyor (K-70) ve
çıkarım 147 görevde %75,5 isabetli. Hata profili tek bir uygulamada yığılmış:
`phone` 30 görevde kaçırılıyor.

O otuz görevin **hepsi** `phone`'u yalnız okumayı gerektiriyor. Yönergeler
"roommates", "siblings", "coworkers" diyor; ilişki `phone` kişi kayıtlarında
duruyor ve okunması gerekiyor. Referans çözümlerde o otuz görevin **sıfırında**
`phone`'a yazma var.

Okuma kapsansaydı beş görevden biri kalkan yüzünden kırılırdı. Yüzde 75
isabetli bir çıkarımla okuma kapısı kurulamaz.

**Yanlış pozitif maliyeti de aynı ölçümden çıktı.** Uygulama kümesi hata oranı
%24,5 ama kalkanın yanlış pozitifi %4,1: kaçırılan 39 uygulama örneğinin yalnız
6'sında referans çözüm o uygulamaya gerçekten yazıyor. İkisi ayrı sayılar ve
karıştırılırsa kalkanın maliyeti altı kat abartılır.

**Kararı ne değiştirir.** Uygulama kümesi çıkarımı belirgin biçimde iyileşirse
okuma kapsanabilir. O zamana kadar sınırlamalarda madde olarak duruyor (S-03).

**Kayıttaki boşluk da kayda geçiyor.** R3 ve dış incelemenin iki turu depoda
hiçbir yerde yok; `docs/10-external-review.tr.md` şablon hâlinde. Kararların çoğu
konuşmada geçti ve nereden geldikleri yazılı değil. Bu belge o boşluğun ilk
kapanan parçası.

### K-149 — Ne gerekirdi: (b) yolunun fiyatı bir sonuç olarak yazılıyor

**Karar.** Ezberleme kapısını menzile sokmanın fiyatı bir **ölçüm sonucu**
olarak kaydediliyor. Bu kayıt "yapamadık" demiyor; "ne gerektiğini ölçtük"
diyor. Eser `results/sample-size.json`.

**Gereken.** Geçiş oranı ölçülen 0,280'de sabit tutulup yalnız örneklem
büyütüldüğünde, kapının okuduğu yarının aralığı etkinin yarısının altına **500
eylem görevinde** iniyor — ve bu yalnız beklenen etki %20 ve üstündeyse. %10 ise
havuzun tamamında (623 eylem görevi) bile inmiyor.

**Beş yüz görevin bileşimi.** Bugünkü 105'in üstüne `test_challenge`'ın eylem
tipi 408 görevinden **395**'i. O bölmenin neredeyse tamamı.

**Hesap tarafı.** 500 görev × 5 koşul × 3 tohum = 7500 epizot. Ölçülen epizot
başına 0,02994 oturum saatiyle **yaklaşık 225 oturum-saati**, bugünkü tasarımın
dört katı.

**Ve asıl nitelik: bu hassasiyeti artırmak değil, ölçülen şeyi değiştirmek
olurdu.** Eklenen görevler `test_challenge`'tan geliyor ve o bölmenin çapa
dağılımı farklı — ortalama 47,6 karşı 32,8, en büyüğü 649 karşı 126, ve çapası
75 ve üstü olan görevlerin payı %12,5 karşı **%2,9**. Tavan çapadan türediği için
tavan dağılımı da kayıyor. Yani büyüyen örneklem aynı sorunun daha kesin cevabını
değil, **başka bir görev popülasyonu hakkında** bir cevap verirdi. Sayılar
`results/sample-size.json` içinde.

**Kaba kestirim ile ölçüm neden ayrıştı.** Elle yapılan kestirim ~282 göreve
işaret ediyordu; ölçüm 500 dedi. Genişlik kök-n ile gitmiyor, çünkü eklenen
görevlerin tavanları büyük ve sansürlü gözlemler daha uzağa düşüyor. Kestirimin
yanlış olması bir kusur değil; ölçümün neden gerektiğinin örneği.

**`S-66` bu sayının altında.** Gürültü katsayısı iki tekrarlı hücreden ölçüldü,
yani 500 bir **alt sınır**: gerçek değişkenlik büyükse yükselir, düşmez.

**Ek — 25 Eylül 2026: 500 bir medyan.** Yukarıdaki sayı yedi tekrarın medyanından
çıkan tek bir çekilişti; tohumu bir kaydırmak onu 623, ulaşılamaz ve 400'e taşıdı.
Tekrar başına dağılım `K-168`'de: beklenen etki %20 ve üstüyse 400–557 eylem
görevi, %30'da yedi tekrarın ikisinde ve %50'de birinde havuzun tamamı da
yetmiyor. Tabaka artık 104, havuz 557; epizot tarafı 6000–8355, yaklaşık 180–250
oturum-saati. Nitelik paragrafı ve `S-66` olduğu gibi geçerli.

### K-206 — Geçmişi yeniden yazma yasağının kapsamı

**Karar, kullanıcının.** "Bu depoda geçmiş yeniden yazılmaz" kuralı şunları kapsıyor:
`main`, `main`'e birleşmiş her şey, her etiket, ve herhangi bir kayıt veritabanındaki bir
`code_commit` anahtarının gösterdiği her commit. Bunların hiçbirini taşımayan, birleşmemiş
bir özellik dalı sahibin açık onayıyla yeniden kurulabilir.

**İlk uygulaması.** `public-build` dalının iki commit'i (`3dd6ece`, `8c5957f`) asistan
adlarını düz metin olarak taşıyordu. Zorla push'tan önce doğrulandı: ikisi de `main`'den ve
hiçbir etiketten erişilmiyor, ve üç yerel veritabanının commit taşıyan sütunlarının
(`code_commit`, `appworld_commit`, `compiler_commit`, `opened_commit`) hiçbirinde
geçmiyor. Dal `main`'den temiz commit'lerle yeniden kuruluyor ve zorla push ediliyor; #77
aynı PR olarak kalıyor.

### K-205 — Açık depo "mind" bu arşivden bir betikle kuruluyor

**Karar, kullanıcının.** Bu depo (zihin) özel kalıyor ve kaydın sistemi olmaya devam
ediyor. Açık depo "mind", arşivin ağacından `scripts/build_public_tree.py` ile kurulan,
geçmiş taşımayan yeni bir depo. Python paketi `zihin` adını koruyor. İlk yapının arşiv
commit'i 4a78cc2b2762f095c70a8ec555107a84c36a9197. Bu arşivin geçmişi yeniden yazılmıyor
(`K-206`).

**Kural.**
- Dışlananlar: staj raporunun iki dili (`K-197`), `.sqlite` dosyaları, yapının kendi
  girdileri (`scripts/public_templates/`), `.cache` dizinleri ve commit'in kendi
  `.gitignore`'una takılan izlenen dosyalar.
- Pakete girenler: AppWorld rota dizgesi, AppWorld'ün kendi API listesindeki bir
  (uygulama, API) çifti (`app.api` ya da `apis.app.api` biçiminde) ya da görev metni
  taşıyan her veri dosyası. Kod ve belgeler pakete girmiyor. `results/demo-eklenti.json`
  modelin ürettiği çağrıları taşıdığı için pakette. `results/sandbox-olcum.json`'ın tek
  isabeti bir API değil, bir Python öznitelik yolu; dosya düz metin kalıyor.
- Paket `derived/appworld-derived.bundle`, `K-194`'ün yoluyla ve git'e sabitli
  0.2.0.dev0'ın sabitleriyle paketleniyor. `derived/MANIFEST.json` yalnız özgün yolu ve
  sha256'yı taşıyor. `scripts/unpack_derived.py` dosyaları `appworld unpack` ile özgün
  yollarına açıyor.
- Kod sayılan ve bir rotayı anabilen türler `.py`, `.md`, `.sql`, `.sh`, `.ps1` ve
  `.ipynb`. AppWorld'ün açık kaynak ajan paketinden gelen iki istem dosyası düz metin.
- Görev metni: her bölmedeki her talimatın her 40 karakterlik normalleştirilmiş penceresi;
  40 karakterden kısa talimatlar bütün olarak.
- Doğrulama: özel ad listesi, görev metni, paket dışında rota taşıyan bir veri dosyası,
  asistan adı ve gitleaks. İkili dosyalar da taranıyor: zip ve wheel arşivleri içerik
  içerik, öbürleri bayt olarak. Vendored üçüncü taraf içerikteki bir isabet yalnız yol,
  içerik ve sha256 ile anahtarlanmış bir izin listesinden geçiyor, ve PROVENANCE onu
  lisansıyla basıyor. Tek bir isabet yapıyı düşürüyor.
- Açık ağaç yamaları kesin dayanakla uygulanıyor, dayanak yoksa yapı düşüyor, ve
  PROVENANCE her yamayı dosyası, çıkan satırları ve gerekçesiyle listeliyor.
- `--check` bütün kapıları geçici bir dizinde koşuyor ve ağaç bırakmıyor. CI'ın Testler
  işinde koşuyor; iş sayısı beşte kalıyor.
- Aynı commit'ten iki yapı, paket dosyası dışında baytı baytına aynı; bir test bunu
  sınıyor. PROVENANCE paketin hash'ini değil manifestin hash'ini taşıyor, çünkü paketin
  baytları her yapıda değişiyor.
- Eşitleme: aynı betik daha yeni bir arşiv commit'ine karşı koşuluyor ve fark açık depoya
  tek commit olarak uygulanıyor: "Sync with archive <hash>".

**İlk kuru deneme düştü, ve düşmesi doğruydu.** `692c77d_1` görevinin talimatından bir
alıntı `docs/reports/asama-2.md`'de ve onun PR gövdesinde kalmıştı (`S-82`). Alıntı D5
biçimine çevrildi.

**Ek — 14 Kasım 2026: Adım 3 tek commit.** Açık depo, doğrulanmış ağacın tamamını taşıyan
tek bir commit'le başlıyor: ileti "Initial public release", son satırı "Archive: <hash>".
Temiz klondaki doğrulamaların hepsi geçerli.

**Ek — 14 Kasım 2026: AppWorld wheel'leri, şifreli metin ve CI'da gitleaks.** Üçü de
kullanıcının kararı.
- `vendor/appworld/` altındaki iki wheel açık ağaca girmiyor; arşiv onları değiştirmeden
  tutuyor. Açık depo görev metni taşıyan AppWorld ikili dosyalarını yeniden dağıtmıyor:
  ajan paketinin istemleri, aynı senaryonun üç `test_normal` görevinin talimatlarında
  ortak olan 47 karakterlik bir parçayı taşıyor. Yedek yansı istek üzerine arşivden
  veriliyor. Açık ağaçta
  `vendor/appworld/README.md` ve iki REPRODUCE dosyası kesin dayanaklı yamalarla yukarı
  akış kaynağını, sabitlenen commit'i, iki wheel'in adını ve sha256'sını ve yansının
  arşivde durduğunu söylüyor. Üçüncü taraf izin listesi boş.
- Wheel'leri açan tek yer `scripts/bootstrap_repo.sh`'in geri düşüş dalı: `uv sync` düşer
  ve günlük LFS'ten söz ederse giriliyor. Hiçbir CI adımı ve hiçbir test onları açmıyor.
- Tasarım gereği şifreli olan dosyaların (`*.bundle`, türetilmiş paket dahil) içeriği ad,
  talimat ve asistan adı için taranmıyor; yolları taranıyor. Güvencesi: pakete giren her
  düz metin girdi paketlemeden önce ad ve asistan adı için taranıyor ve bir isabet yapıyı
  paketlemeden önce düşürüyor. Gerekçe: `apps.bundle`'daki üç harfli kısaltma isabeti
  şifreli metin üzerindeki kelime taramasının rastgele isabet ürettiğini gösterdi.
  Türetilmiş paketin baytları her yapıda değiştiği için aynı kaza yapıyı ara sıra
  düşürürdü.
- CI'ın Testler işi gitleaks 8.30.1'i resmî GitHub sürümünden indiriyor ve sürümün
  yayımladığı sha256 tutmadan çalıştırmıyor. İş sayısı beşte kalıyor.
- Bu ek, `K-198`'in wheel maddesini yalnız açık ağaç için daraltıyor. Arşivde `K-198` geçerli.
- Adım 3'ün test ölçütü: temiz klonda geçen test sayısı, arşivde geçen sayıdan dört
  gruptaki atlamalar çıkarılınca kalan sayıya eşit olmalı, ve düşen test olmamalı.
  Gruplar: özel şablonlar, kayıt veritabanları, tek commit'lik geçmiş, izlenmeyen
  AppWorld koşu çıktıları. Her atlama test adı ve gerekçesiyle listeleniyor.

**Ek — 15 Kasım 2026: açık deponun adı `zihin`, arşivinki `zihin-archive`.** Kullanıcının
kararı. "mind" adında bir depo olmayacak. Açık depo `yusuferengerek/zihin`. Bu özel arşivi
kullanıcı Adım 5'te, açık depo kurulmadan önce `zihin-archive` olarak yeniden adlandıracak.
Yukarıdaki metin "mind" adını yazıldığı gibi koruyor. Şablonlar, üretilen dosyalar, yapı
betiği, PROVENANCE ve site yapılandırması artık `zihin` adını kullanıyor.
- Adım 5'in sırası: önce arşiv yeniden adlandırılıyor, sonra yerel `origin` adresi
  güncelleniyor ve doğrulanıyor, en son açık depo kuruluyor. Sebebi: eski adres, açık depo
  kurulduğu anda ona çözülecek.
- Açık ağaçta arşivin GitHub adresini ya da ona bir PR atfını taşıyan yerler, yeniden
  adlandırmadan sonra açık depoyu gösterecek. Değiştirilmediler. Hangileri oldukları
  kullanıcıya raporlandı.

**Ek — 16 Kasım 2026: arşivin Colab varsayılanları `zihin-archive` adını taşıyor.**
Kullanıcının kararı. Bu commit'ten itibaren arşivin Colab varsayılanları
`yusuferengerek/zihin-archive`: defterdeki ve `scripts/colab_publish_results.sh`'deki
`ZIHIN_REPO_SLUG` varsayılanı, `experiments/colab/README.md`'deki Colab bağlantısı ve "Depo:"
satırı. Kullanıcı arşivi yeniden adlandırana kadar Colab'daki klon düşüyor. Bu isteniyor:
düşen bir klon hiçbir şey sızdırmıyor.
- Açık yapı bu dört yeri dört tam dayanaklı yamayla `yusuferengerek/zihin`'e geri
  çeviriyor. PROVENANCE onları öteki yamalarla birlikte listeliyor.
- `docs/reports/mekanizma-kapanis-notlari.md`'deki sekiz PR bağlantısı artık arşivin
  `zihin-archive` adresini gösteriyor ve açık ağaçta da öyle kalıyor: o PR'lar yalnız
  arşivde var.
- 15 Kasım ekinin son maddesinin kapsadığı dört dosya bunlar. O madde bu commit'ten
  itibaren geçerli değil.

**Ek — 17 Kasım 2026: Adım 4, kayıt veritabanları değiştirilmeden paketleniyor.** İki
karar da kullanıcının. Girdiler `K-194`'ün dört veritabanı: `results/zihin.sqlite`,
`results/zihin-2.sqlite`, `results/zihin-3.sqlite` ve b1ceb78 blob'undan çıkarılan
`zihin-3-colab.sqlite`. Hiçbiri düzenlenmiyor, süzülmüyor ya da yeniden kurulmuyor.
- D1. gitleaks bulguları eklerde kalıyor. Bulgular AppWorld'ün yerel sunucusunun sahte
  kullanıcılarına verdiği oturum belirteçleri, `relationship=` dizgeleri ve modelin yazdığı
  yer tutucular. Hiçbiri gerçek bir hizmete erişim vermiyor.
- D2. Sahibin yerel kullanıcı adını taşıyan yollar eklerde kalıyor. Onları çıkarmak kaydı
  yeniden yazmak olurdu.
- Paketin anahtarı AppWorld paketinin içinde yayımlanıyor. `appworld` kuran herkes ekleri
  açabilir. Paketleme AppWorld'ün şartını yerine getiriyor ve içeriği kirlenmeye karşı
  koruyor, okunmaya karşı korumuyor. Eklerdeki her şey okunabilir sayılıyor.

gitleaks 8.30.1 varsayılan kurallarla, her veritabanının sütun başına metin dökümü üzerinde
koştu. Ham `.sqlite` dosyasını ikili diye atlıyor. Bulguların sınıfları:

| Sınıf | Kural | Tablo ve sütun | zihin | zihin-2 | zihin-3 | zihin-3-colab |
|---|---|---|---|---|---|---|
| Tam JWT | jwt | `observations.truncated_text` | 174 | 351 | 460 | 72 |
| Tam JWT | jwt | `steps.generated_code` | 0 | 1 | 0 | 0 |
| Tam JWT | generic-api-key | `observations.truncated_text` | 0 | 0 | 2 | 0 |
| `relationship=` | generic-api-key | `observations.truncated_text` | 6 | 1 | 1 | 0 |
| `relationship=` | generic-api-key | `steps.generated_code` | 6 | 9 | 17 | 2 |
| Toplam | | | 186 | 362 | 480 | 74 |

- Tam JWT: HS256, iddiaları yalnız `exp` ve `sub`, imzası 43 karakter. `sub` her zaman
  `<uygulama>+<hesap>` biçiminde. Hesap ya AppWorld verisindeki bir e-posta adresi ya da
  `phone` uygulamasının bir telefon numarası. İmzalar AppWorld'ün anahtarıyla doğrulanmadı.
- `relationship=`: generic-api-key kuralının sır diye yakaladığı 13 karakterlik bir argüman
  adı. Değer değil.
- Kararın dayandığı rapor 1, 28, 120 ve 32 bulguyu kesik JWT sayıyordu. Bu yanlıştı. Hepsi
  tam JWT, ve hepsinin ardından bir satır sonu geliyor. Döküm satır sonunu `\n` olarak
  yazıyor, gitleaks onu sırrın parçası sandı, ilk sınıflama da gitleaks'in sırrını okudu.
  İkinci ölçüm her bulgunun belirtecini hücrenin kendisinden okudu.
- Gerçekten kesik altı JWT parçası `zihin-2`'nin `observations.truncated_text` sütununda
  duruyor. gitleaks onları yakalamadı.
- Modelin yazdığı yer tutucular yalnız `zihin-3`'ün `steps.generated_code` sütununda. 73
  `Authorization` başlığının 39'u `Bearer YOUR_ACCESS_TOKEN`, 34'ü
  `f"Bearer {access_token}"`. Bir de "your_stripe_api_key" adlı bir tanıtıcı var.
- `OPENROUTER_API_KEY` yalnız `run_manifests.model_server_env` içinde, değişkenin adı olarak
  geçiyor: `zihin-2`'de 48, `zihin-3`'te 27 satırda. OpenRouter anahtar biçimi (`sk-or-`)
  hiçbir hücrede ve hiçbir ham baytta yok.

`supervisor.account_passwords` yanıtları AppWorld'ün sahte hesaplarının parolalarını
taşıyor ve D1 altında eklerde kalıyor. Gözlemlerde basılan her (hesap, parola) çifti, o
epizodun kendi görevinin AppWorld verisindeki bir hesap. Hesaba benzeyen 16 çift daha var,
ama onlar hesap değil: değerleri "string" sözcüğü olan yanıt şeması, AppWorld'ün API
belgesinden. Onları `api_docs.api_doc` çağıran adımlar basıyor.

| Veritabanı | Çağrı | Epizot | Basılan çift |
|---|---|---|---|
| zihin | 461 | 27 | 207 |
| zihin-2 | 640 | 110 | 982 |
| zihin-3 | 725 | 302 | 457 |
| zihin-3-colab | 133 | 55 | 110 |

Sahibin yerel kullanıcı adını taşıyan yollar (D2):

| Tablo ve sütun | Önek | zihin | zihin-2 | zihin-3 | zihin-3-colab |
|---|---|---|---|---|---|
| `observations.full_output_path` | `/home/<sahip>/` | 1338 | 5005 | 4089 | 0 |
| `observations.truncated_text` | `/home/<sahip>/` | 1 | 0 | 0 | 0 |
| `verifier_results.detail_path` | `/home/<sahip>/` | 60 | 164 | 120 | 0 |
| `run_manifests.model_server_env` | `Users/<sahip>/` | 62 | 116 | 93 | 0 |

Öteki `/home/...` yolları AppWorld'ün sahte dosya sistemindeki kullanıcılara ait.

Model AppWorld'ün verisinde olmayan on gmail adresi uydurdu. Veritabanı başına sayılınca on
iki ediyorlar (1 + 1 + 10), çünkü listedeki son adres `zihin`, `zihin-2` ve `zihin-3`'te
geçiyor. Geçtikleri her epizotta adresi ilk taşıyan modelin kodu: kod, adresi taşıyan ilk
gözlemden ya da ilk eylemden daha geç bir adımda değil. Hiçbir bölmenin hiçbir görev
talimatı onları taşımıyor. Adresler burada ilk iki karakterleri, üç yıldız ve alan adıyla
yazılıyor. Tam liste yalnız yerel tarama raporunda.
- `ad***@gmail.com`: `zihin-3`
- `ed***@gmail.com`: `zihin-3`
- `ja***@gmail.com`: `zihin-3`
- `jo***@gmail.com`: `zihin-3`
- `ka***@gmail.com`: `zihin-3`
- `ma***@gmail.com`: `zihin-3`
- `ma***@gmail.com`: `zihin-3`
- `me***@gmail.com`: `zihin-3`
- `ro***@gmail.com`: `zihin-3`
- `ro***@gmail.com`: `zihin`, `zihin-2`, `zihin-3`

**Ek — 22 Kasım 2026: 17 Kasım ekinin iki parçası bu tarihte yazıldı.** Yukarıdaki 17
Kasım ekinde iki parça o güne ait değil: uydurulan adreslerin maskelenmesi ve tablosuyla
birlikte `supervisor.account_passwords` paragrafı. İkisi de 22 Kasım 2026'da `211aeef` ile
yazıldı. Ekin geri kalanı 17 Kasım 2026'da `fcb4ce0` ile yazıldı. Tam adresler o commit'te,
arşivin geçmişinde kalıyor. Kullanıcının kararı: dal yeniden kurulmuyor.

### K-204 — CI, konteyner ve yapılandırma dosyalarındaki Türkçe çevrilmiyor

**Karar, kullanıcının.** `.github/workflows/ci.yml`, `Containerfile` ve `config/*.yaml`'daki
Türkçe ne bu depoda ne açık depoda çevriliyor: CI iş adları, konteyner dosyası ve
yapılandırma yorumları. Bu dosyalar `4a04e50`'de dondu ve deney bitene kadar değişmiyor.
Açık deponun README'si bir "Language" başlığı altında bunu ve deneyden sonraki
eşitlemede çevrileceklerini söylüyor.

**Bir ayrıntı.** `Containerfile` ve `config/` ölçümü tanımlayan yollar listesinde; bir
değişiklik sürücünün durma kuralını tetikliyor. `.github/workflows/ci.yml` o listede değil.
Karar onu da dondurulmuş sayıyor, ama sürücü onu izlemiyor.

**Ek — 14 Kasım 2026: `ci.yml` iki kez değişti.** İkisi de kullanıcının açık kararı ve
ikisi de Testler işine bir adım ekledi: açık depo yapısının kapıları (`5b03e47`) ve sabit
sürümlü, sha256'sı doğrulanan gitleaks kurulumu (`9a3f066`). İş sayısı beşte kaldı.
Dosyadaki Türkçe çevrilmedi.

### K-203 — Birleşen her dal birleşmeden sonra siliniyor

**Karar, kullanıcının.** `main`'e birleşen her dal, ayrı bir karar beklemeden birleşmeden
sonra siliniyor. Silmeden önce dalın ucu depo dışındaki geri yükleme kaydına yazılıyor.
Bu kural, `K-191`, `K-192` ve `K-201`'deki tek tek silme kararlarının yerini gelecekteki
dallar için alıyor.

### K-202 — `SKILL_SPEC` düzeltiliyor, kod değil; ölçüleni `skills` tablosu tanımlıyor

**Karar, kullanıcının.** `S-81`'in dokuz alanı için şartname düzeltiliyor, koda
dokunulmuyor; sıfır kod değişikliği.

**Gerekçe.** `skills` tablosu ölçümü tanımlayan kodun parçası (`src/zihin/schema.sql`)
ve o kod `4a04e50`'de dondu. `SKILL_SPEC.tr.md` hiç dondurulmadı ve tasarlanan kartı
anlatıyor. Ölçülenin otoritatif tanımı tablo.

**Dokuz alan tasarlandı, o biçimiyle uygulanmadı.**
- Altısının uygulaması yok: *precondition*, *invocations*, *blamed_failures*,
  *postcondition_misses*, *model_failures_gate_1*, *model_failures_gate_2*. Beceriler
  modele metin kartı olarak veriliyor ve çağrılmıyor; bu yüzden ön koşul kapılarının,
  son koşul ıskalarının, suç atfının ve çağrı sayaçlarının uygulaması yok.
- Üçü tabloda başka biçimde duruyor ve tablonun biçimi geçerli: *signature* yerine
  `free_parameters`; *calls* yerine `body` ve `body_length`; *effect_suffix* yazan
  çağrıların indekslerini değil, sonekin çağrılarını tutuyor.

Şartnamenin iki dili tarihli bir düzeltmeyle bunu yazıyor; `S-81` bu kayda dayanarak
kapandı.

### K-201 — `tasarim-katmani` bir arşiv etiketinde tutuluyor; üç dal silindi

**Karar, kullanıcının.** `K-192`'nin ayrı karar beklediği iki dal ve `public-readiness`
için:
- `ceviri-hazirligi` silindi. Tek commit'i (`7feb45c`) `main`'e #48 ile eşdeğer bir
  yama olarak girmişti (`98d64aa`); kaybolan içerik yok.
- `public-readiness` silindi; #71 birleşmişti.
- `tasarim-katmani` için önce `288593d` üzerinde açıklamalı `archive/tasarim-katmani`
  etiketi kuruldu ve push edildi, sonra dal silindi. Yedi commit (`190b0bc`'den
  `288593d`'ye) etiketten erişiliyor: GitHub'ın `main` ile etiket arasındaki
  karşılaştırması dal silinmeden önce de sonra da aynı yedi commit'i verdi.

**Neden arşiv.** Dalın önerileri #16 birleştikten sonra dala eklenmişti ve `main`'e
hiç girmedi: parametre başına ayar bütçesi; önce beş, sonra altı türlü değişiklik
taksonomisi; `K-13`, `K-41`, `K-42`, `K-43` ve `K-53`'teki yerinde değişikliklerin bu
türlere göre sınıflandırılması; eksende kalma ölçütünün kaldırılıp ön koşul kapısına
katılması. Bu öneriler ön kaydın A.9 bölümü ve `K-177` ile aşıldı ve kayıt için
tutuluyor. #16'nın başı `6f16e4f`'yi gösterdiği için etiketsiz bir silme bu commit'leri
GitHub'da hiçbir referanstan erişilemez bırakırdı.

### K-200 — Üç giriş belgesi çevriliyor; kalan Türkçe belgeler README'lerde listeleniyor

**Karar, kullanıcının (D12).** `REPRODUCE.md`, `DATA_MODEL.md` ve `SKILL_SPEC.md`
İngilizceye çevriliyor. Çeviri deponun iki dilli adlandırma kuralıyla ve bu
temizlikten ayrı bir PR'da yapılacak. Bunların dışındaki yalnız Türkçe belgeler iki
README'de "Yalnız Türkçe belgeler" bölümünde adlarıyla listelendi.

**Bir sayı düzeltildi.** Denetim raporu `docs/reports/` altında 27 yalnız Türkçe belge
saymıştı. Doğrusu 26: o klasördeki 27 Türkçe dosyadan biri, `eksen-uzatma.tr.md`, İngilizce
eşini taşıyor.

**Ek — 13 Ekim 2026: adlar README kuralıyla.** Üç belgenin Türkçe kaynağı
`REPRODUCE.tr.md`, `DATA_MODEL.tr.md` ve `SKILL_SPEC.tr.md` adını aldı; İngilizce çeviri
eski adlarda duruyor. Kökte iki dilli tek emsal README (`K-105`): İngilizce yarı
uzantısız adı, Türkçe yarı `.tr.md` adını taşıyor. `docs/` altındaki şema seçilseydi
(`.tr.md` kaynak, `.en.md` çeviri) eski adlar ortadan kalkardı. Onlara bağlanan dört
dosya ölçümü tanımlayan yollarda: `config/models.yaml`, `src/zihin/model_server.py`,
`src/zihin/compiler.py` ve `src/zihin/schema.sql`. Bağlantıyı düzeltmek sürücüyü
durdururdu, düzeltmemek ölü bağlantı bırakırdı. Bu adlarla hiçbir bağlantı kopmuyor.
Seçim PR'da; kullanıcı PR'ı inceleyerek onaylıyor.

**Çeviri kaynağı eskimiş yerleriyle taşıyor.** Ölçülen yerler düzeltilmedi; düzeltmeleri
ayrı bir karar:
- `DATA_MODEL.tr.md` dokuz tablo sayıyor; şemada bugün on iki tablo var, `run_ledger`,
  `experiment_slices` ve `experiment_episodes` sonradan girdi. Künye sabitini eski
  adıyla anıyor, kodda adı `REQUIRED_MANIFEST_FIELDS`. "Tek gerçek kaynağı" bölümü iki
  projeksiyon tablosunun "burada olmadığını" söylüyor, belgenin kendi tablo listesi
  ikisini de sayıyor.
- `SKILL_SPEC.tr.md` bir şartname ve `skills` tablosu ondan ayrışıyor: tabloda
  `free_parameters` ve `body` var; `kind`, `precondition` ve sicil sayaçları yok.
- `REPRODUCE.tr.md` `appworld` işaretli testlerin CI'da koştuğunu bir bölümde söylüyor,
  sonraki bölümde koşmadığını. Model sunucusu bölümü 1.5B, 3B ve 7B'yi ve Aşama 4
  öncesini anlatıyor.

### K-199 — README'lerin durum bölümü ve proje durumu bugüne çekildi

**Karar, kullanıcının (D11).** İki README'nin durum bölümü bugünü anlatıyor:
- Birincil hücre `qwen2.5-coder:32b-instruct-q4_K_M`'ye ve Colab A100'e taşındı; aynı otuz
  görevde 11/30.
- Deneyin tanımı donduruldu (kurulum protokolü 19.6) ve sürücü hazır.
- Tamamlanmış deney hücresi yok. Bu depodaki kayıt hiç deney epizodu taşımıyor; 26 Eylül
  2026'dan sonra Colab'da bir dilim koşup koşmadığı depodan bilinmiyor.

**Düzeltilen yanlışlar ve eskimişlikler.**
- `results/`'in izlenmediği söyleniyordu; belgelerin atıf verdiği JSON dosyaları izleniyor.
- CI'ın iş sayısı ve adları.
- İngilizce README'deki "all five", "all six" oldu.
- Dolgu cümlesi `K-181` ile uyumlu hâle geldi.
- İki kontrast paragrafı `K-188`'e göre yeniden yazıldı.
- `naive_compiler`'ın deneye yazılmadığı eklendi (`K-145`).
- `PROJECT_STATUS.md`'nin "sandbox yok" satırı düzeltildi. Aynı belgede sonraki kararlarla
  çelişen satırlar da düzeltildi: model ekseni, kart sayısı, ayar bütçesi, durma eşiği,
  birincil metrik, CI ve sıradaki adım.

Taslak PR'da; kullanıcı PR'ı inceleyerek onaylıyor. Vendored AppWorld wheel'leri ağaç
tablosunda "yedek yansı" olarak anılıyor; birincil kurulum yolu değiller.

### K-198 — Yönteme ait model adları ve vendored AppWorld wheel'leri kalıyor

**Karar, kullanıcının (D10).** Şunlar olduğu gibi kalıyor:
- Dış incelemede danışılan modellerin adları (`docs/10-external-review.tr.md`, satır 32,
  35, 70, 75).
- Yayımlanmış referans koşusu olan `gpt-4o`'nun bütün anmaları.
- `vendor/appworld/` altındaki iki wheel. İçlerindeki uygulama ve test bundle'ları
  şifreli.

### K-197 — Staj raporu bu depoda kalıyor, açık kopyadan çıkarılıyor

**Karar, kullanıcının (D9).** `docs/13-internship-report.tr.md` ve
`docs/13-internship-report.en.md` bu depoda kalıyor. Açık kopyaya ise kurum izni
kullanıcı tarafından teyit edilene kadar girmiyor: dosyalar kurumu, çalışma yerini,
üniversiteyi ve danışmanı adıyla anıyor. Başka belgelerdeki adsız danışman anmaları
kalıyor.

**Ek — 18 Ekim 2026: süzülmüş kopya iptal.** Süzülmüş açık kopya planı 13 Ekim
2026'da iptal edildi; açık depo ağaçtan, kendi tasarımıyla yeni bir depo olarak
kurulacak (`K-189`'un eki). Bu kaydın "açık kopyadan çıkarılıyor" yarısının dayandığı
kopya artık kurulmuyor. Belgenin yeni açık depoya girip girmeyeceği o deponun
tasarımına ait; kurum izni şartı değişmedi. Belge bu depoda kalıyor.

### K-196 — Commit yazar kimlikleri olduğu gibi kabul edildi

**Karar, kullanıcının (D8).** Geçmişteki yazar kimlikleri kabul edildi: dört kişisel kimlik
ve Colab koşucusunun kimliği. Değiştirmek geçmişi yeniden yazmayı gerektirir, ve bu
depoda geçmiş yeniden yazılmıyor (`K-189`).

### K-195 — Kişisel ve makineye özgü yollar olduğu gibi kalıyor

**Karar, kullanıcının (D7).** Denetimin bulduğu yolların hiçbiri düzenlenmiyor:
- `config/models.yaml` satır 55 dahil. Bu ölçümü tanımlayan bir yol; düzenlense sürücü
  dururdu.
- `results/b32c-taramasi.json` satır 2 ve 32.
- `experiments/colab/README.md` satır 103–104.
- `docs/reports/kurulum-sonrasi-4.md` satır 14.
- Bu belgenin bir satırı.

### K-194 — Kayıt veritabanları yalnız şifreli bir sürüm eki olarak, AppWorld'ün yöntemiyle

**Karar, kullanıcının (D6).** Dört kayıt veritabanı yalnız şifreli bir sürüm eki olarak
yayımlanıyor:
- `zihin.sqlite`
- `zihin-2.sqlite`
- `zihin-3.sqlite`
- `facd233`'teki b1ceb78 blob'undan geri alınan `results/zihin-3-colab.sqlite`

**Bağlayan şart, AppWorld'ün `data/LICENSE` dosyasından harfi harfine:**

> The contents of this folder are part of the protected portion of AppWorld, released as
> an encrypted .bundle file under the Apache 2.0 license with the additional requirement
> that any public redistribution of it (or of its derivatives) must also be done in an
> encrypted format.

**AppWorld'ün belgelediği yöntem.** AppWorld'ün leaderboard deposunun yönergesi şöyle:
"appworld pack" deney çıktısını sıkıştırıp şifreleyerek bir "leaderboard.bundle"
dosyasına koyuyor, "appworld unpack" açıyor. Anahtar AppWorld paketinin kendi içinde
duruyor. Bu depoya, PR'lara ve raporlara hiçbir anahtar ya da anahtar malzemesi
yazılmıyor.

**Ölçülen bir sapma, ve onayı bekleniyor.** "appworld pack" yalnız bir beyaz listedeki deney
çıktısı dosyalarını paketliyor: `metadata.json`, günlükler, `dbs` altındaki `.jsonl`
dosyaları. `.sqlite` dosyaları listenin dışında; komut veritabanlarını paketlemiyor.
Önerilen yol şu:
- Ekler, komutun çağırdığı aynı paketleme fonksiyonuyla (AppWorld'ün crypto modülündeki
  bundle paketleyicisi) ve aynı anahtar sabitleriyle üretilir. Anahtar kopyalanmaz, kendi
  modülünden okunur.
- Dosyalar belgelenmiş "appworld unpack" komutunun açabileceği yerleşimle konur.

Bu, komutun kendisi değil, aynı şifreleme ve aynı anahtar düzeni. Kullanıcı onaylayana
kadar hiçbir ek üretilmiyor.

**Ek — 13 Ekim 2026: onaylandı, iki şartla.** Kullanıcı önerilen yolu onayladı.
- **Sürüm ve fonksiyon.** Paket `appworld` 0.2.0.dev0; `pyproject.toml`'un sabitlediği git
  commit'i a072b7a86e7c1d5b1d7175659d750ebb9b79f10a. Paketleme fonksiyonu
  "appworld.common.crypto.pack_bundle": "appworld pack" komutunun çalıştırdığı
  "appworld.leaderboard.pack_experiment" onu paketin kendi parola ve tuz sabitleriyle
  çağırıyor. Açma tarafı aynı modülün "unpack_bundle" fonksiyonu.
- **Gösterim şartı.** Herhangi bir ek yayımlanmadan önce, yalnız yayımlanmış appworld
  paketinin kurulu olduğu temiz bir sanal ortamda, belgelenmiş "appworld unpack"
  komutunun eki açtığı ve veritabanlarının sha256'larının tuttuğu gösterilecek.
- **Zaman.** Ekler şimdi üretilmiyor; açık depo adımına ait.

**Ölçülen bir açık soru.** PyPI'daki son yayımlanmış sürüm 0.1.3.post1; bu depo
0.2.0.dev0'ı git commit'inden kuruyor. Gösterim şartındaki "yayımlanmış paket"in
hangisi olduğu, ve 0.1.3.post1'in aynı komutu ve aynı sabitleri taşıyıp taşımadığı
ölçülmedi.

**Ek — 18 Ekim 2026: "yayımlanmış paket" ve uyumluluk.** Kullanıcı karar verdi:
gösterim şartındaki "yayımlanmış paket", `REPRODUCE`'un okura kurdurduğu sürüm, yani
git'e sabitlenmiş 0.2.0.dev0; gösterim onunla yapılacak. Ayrıca ölçüldü:
- PyPI'daki 0.1.3.post1 temiz bir sanal ortama kuruldu. 0.2.0.dev0'ın "pack_bundle"
  fonksiyonuyla zararsız bir metin dosyasından üretilen bir test paketini belgelenmiş
  "appworld unpack" komutuyla açtı; dosyanın sha256'sı tuttu.
- İki sürümün anahtar sabitleri eşit; değerleri hiçbir yere yazılmadan karşılaştırıldı.
- Ters kanıt: dosyanın metni paketin içinde düz geçmiyor, ve yanlış bir parola paketi
  açmadı, tek dosya yazılmadı.
- Paketleyici 0.1.3.post1'de "appworld.common.utils", 0.2.0.dev0'da
  "appworld.common.crypto" altında; modül yolu farklı, biçim aynı.

Gerçek ekler üretilmedi; veritabanlarına dokunulmadı.

### K-193 — AppWorld türevleri kimlik ve sha256 ile değiştirildi; rota testinin örneği bir train görevinden

**Karar, kullanıcının (D5), adıyla.**
- **(a)** `results/demo-eklenti.json` satır 71'deki test yönergesi yerine görev kimliği ve
  sha256 kondu (`S-78`).
- **(b)** `tests/data/api_calls-32616b5_1.jsonl` yerine bir `train` görevinin günlüğü geldi
  (`tests/data/api_calls-229360a_2.jsonl`). Testte yalnız dosya yolu satırı değişti
  (`S-80`).
- **(c)** İki belgedeki üç `train` yönergesi yerine görev kimliği ve sha256 kondu (`S-79`).

**(b)'de bildirilen bir uyumsuzluk.** Yeni örnek AppWorld'ün yayımladığı gpt-4o koşusundan,
çünkü testi değiştirmeden geçen tek `train` günlükleri o koşuya ait. Dosya yine de bir
AppWorld deney çıktısı ve türevi. (c)'nin gerekçesi, lisansın `train` ile `test`'i
ayırmadığı, ona da uygulanıyor. Test bölmesinin kirlenmesi kalktı; lisans sorusu kalmadı
denemez (`S-80`).

**Ek — 13 Ekim 2026: (b) artık sentetik.** Rota testinin örnek günlüğü
`tests/data/api_calls-synthetic.jsonl`: `scripts/build_api_calls_fixture.py`'nin yazdığı,
on rota üzerinde 22 çağrı; her çağrının `data` alanı boş, görev metni, model çıktısı ve
yörünge yok (#73). On rota AppWorld'ün açık API Explorer sayfasında gösteriliyor;
kullanıcı adların açık olduğuna hükmetti ve `S-80` kapandı. Rota adlarının açık depoda
nasıl duracağı açık deponun tasarımına bırakıldı.

### K-192 — Birleşmiş 56 uzak dal siliniyor; iki dal ayrı karar bekliyor

**Karar, kullanıcının (D4).** `main`'e birleşmiş 56 uzak dal, bu temizliğin PR'ı
birleştikten sonra siliniyor. `ceviri-hazirligi` ve `tasarim-katmani` silinmiyor:
`main`'e göre farkları raporlanıyor, ve onlar için ayrı bir karar bekleniyor. Dal silmek
geçmişi yeniden yazmak değil. PR'ların başlarını GitHub `refs/pull` altında ayrıca
tutuyor.

**Düzeltme, 13 Ekim 2026: 56 değil 54.** Denetim raporu birleşmiş dal sayısını 56
yazmıştı. Denetimin kendi dökümünde `main` dışında 57 uzak dal vardı ve üçü
birleşmemişti; birleşmiş dal 54'tü. Silmeden önce her dal yeni `main`'e karşı yeniden
ölçüldü: aynı 54 ad, ve sonradan birleşen `public-readiness`. Silinenler o 54 dal ve
`colab-sonuclari` (`K-191`), toplam 55, tek bir atomik push'la. `public-readiness` bu
kararın kapsamında olmadığı için silinmedi. Silinen her dalın adı ve ucu depo dışında
bir geri yükleme kaydında duruyor.

### K-191 — `colab-sonuclari` dalı siliniyor

**Karar, kullanıcının (D3).** Uzak `colab-sonuclari` dalı, bu temizliğin PR'ı birleştikten
sonra siliniyor. Dal `main`'e birleşmemiş tek bir commit taşıyor (`e9af016`), ve o commit
kaydın Drive yolunu gösteren bir sembolik bağ içeriyor.

### K-190 — PR #1 için GitHub'a başvurulmuyor

**Karar, kullanıcının (D2).** Kapalı PR #1'in başı (`refs/pull/1/head`) bu depoda kalıyor.
O başta yalnız bu referanstan erişilen üç commit var, ve iletileri bir ortak-yazar atıf
satırı taşıyor. Bu referanslar süzülmüş açık kopyaya taşınmıyor; sorun yapı gereği
kapanıyor. Üç commit hiçbir kaydın `code_commit` anahtarı değil.

**Ek — 18 Ekim 2026: süzülmüş kopya iptal.** Süzülmüş açık kopya planı 13 Ekim
2026'da iptal edildi; açık depo ağaçtan, kendi tasarımıyla yeni bir depo olarak
kurulacak (`K-189`'un eki). Yeni depo ağaçtan kurulduğu için bu deponun geçmişini ve
PR referanslarını taşımıyor; sonuç değişmiyor: `refs/pull/1/head` ve üç commit açık
depoya girmiyor.

### K-189 — Bu depo özel kalıyor ve kaydın sistemi; açık depo main'in süzülmüş bir kopyasından

**Karar, kullanıcının (D1).** Bu depo özel kalıyor ve kaydın sistemi olmaya devam ediyor.
Commit kimlikleri hiç yeniden yazılmıyor, çünkü kayıtların `code_commit` anahtarları
onlara bağlı. Açık depo, `main`'in bu depo dışındaki bir klonda süzülmüş bir kopyasından
kuruluyor. Kopya, özgün commit'ten süzülmüş commit'e bir eşleme taşıyor.

**Neden.** Herkese açılma denetimi, `main`'in geçmişinde 62 `test_normal` epizodu taşıyan
bir kayıt veritabanı buldu (`facd233`, `results/zihin-3-colab.sqlite`). Onu bu depodan
kaldırmak geçmişi yeniden yazmayı gerektirir.

**Uygulanmayan bir madde.** Temizlik PR'ının altıncı maddesi PR dökümüydü: 70 PR'ın
numarası, başlığı, dalı, birleşme tarihi ve gövdesi, harfi harfine. Açık kopyada GitHub'ın
PR üst verisi olmayacağı için istenmişti. İstenen adla (`docs/pull-request-log.md`) belge
adlandırma denetimini düşürüyor. Kural gereği denetime dokunulmadı ve madde uygulanmadı.
Konum kararı kullanıcıda.

**Ek — 13 Ekim 2026: PR dökümü kökte; süzülmüş kopya iptal.** Uygulanmayan altıncı
madde kullanıcının kararıyla kökte `PULL_REQUESTS.md` olarak uygulandı: bütün PR'lar,
numara, başlık, dal, birleşme tarihi ve gövde harfi harfine; iki README'de yalnız
Türkçe belgeler arasında listeli. Döküm yeni PR'lar birleştikçe yeniden üretiliyor.
Aynı gün kullanıcı bu temizliğin ikinci kısmını, süzülmüş açık kopyayı, iptal etti:
açık depo ağaçtan, kendi tasarımıyla yeni bir depo olarak kurulacak. Bu depo özel
kalıyor ve kaydın sistemi olmaya devam ediyor; yukarıdaki commit eşlemesi kurulmuyor.

### K-188 — Deney iki fazda; `Y-6.2` faz 1'de `skills_failures` ile; `Y-1` kapsanan görevlerde

**Karar, kullanıcının.** Ön kayda üç ilan girdi, hepsi 26 Eylül tarihli ve ilk `dny`
epizodundan önce.

1. **Faz tasarımı** (A.4'e ek). Faz 1: `baseline`, `skills_failures`,
   `irrelevant_retrieval`, 104 görevin hepsinde, 930 epizot. `Y-1` ve `Y-6`'nın ikinci dalı
   bu üçle cevaplanıyor. Faz 2: `skills` ve `failures`, faz 1'den sonra, bütçe varsa;
   `Y-4` ve `Y-5` o fazda. Fazın içinde dilimler göreve göre: her dilim kendi başına
   eşleştirilmiş analiz edilebilsin diye. Atlanan görev yok: hacmi eşleşemeyen kol eksik
   koşuyor ve işaretleniyor (`K-181`).
2. **K2** (A.7'ye ek, ve yanlışlama belgesinin `Y-6` bölümüne ek). `Y-6`'nın ikinci dalı
   "mekanizma koşulu" diyor ama hangisini söylemiyordu. Faz 1'de o koşul `skills_failures`,
   ve karşılaştırma 101 görevde okunuyor. `K-31`'in `skills` – alakasız kontrastı faz 2'nin
   ikinci okuması olarak kalıyor, silinmiyor.
3. **K3** (faz ekinde tek cümle). `Y-1` eylem tabakasının kapsanan görevlerinde okunuyor
   (103). Görülmüş/görülmemiş bölmesi yönsel raporlanıyor.

**K3 neyi çözüyor.** A.2'nin tablosu birincil hücreyi "görülmemiş alt küme" üzerinde
tanımlıyordu. A.7'nin 28 Ağustos eki ve `S-67` ise `Y-1`'i eylem tabakasının tamamında
okuyordu. İki metin çelişiyordu. Görülmüş/görülmemiş bölmesi teslim edilen kütüphane için
hiç ölçülmedi; eldeki ölçüm eski kütüphaneye (`142662f`) ait.

**Açık kalan.** `Y-6`'nın ikinci okumasının (faz 2) hüküm verip vermediği bu kararda
belirlenmedi. Faz 2 başlamadan ayrıca ilan edilecek.

### K-187 — Deneyin şartlar bölümü: her satır okunuyor, her satır kaynağıyla karşılaştırılıyor

**Karar.** Kurulum protokolüne iki bölüm girdi, iki dilde.
- §19.6 Şartlar (`dny`). §18.2'nin deneye uyan satırları, artı deneyin kendi satırları:
  `seed_count` 3, `min_expected_saving` 1, kütüphane ve indeks kimlikleri (`0c3f4ac`),
  görev kümesi 104 (kapsanan 103), görev sırasının tohumu ve özeti, faz 1'in üç koşulu,
  komut. Kartsız görev (K1) ve hacmi eşleşmeyen iki görev de bu bölümde yazılı.
- §19.7 Analiz kümeleri: `K-184`'ün ölçtüğü sayılar. Bir test tabloyu iki dilde
  `results/experiment-sets.json`'a karşı okuyor.

**Denetim, kullanıcının kararı: "??" geçmiyor.** `check_declared_conditions.py`, deneyin
tablosunda şu iki durumdan birini görürse düşüyor:
- Kaynağıyla karşılaştıramadığı bir satır. Önceki bölümlerde böyle bir satır yalnız
  listeleniyordu.
- Ayrıştırıcının hiç okumadığı bir satır. Anahtarı boşluklu bir satır okunmuyor ve "??"
  olarak bile görünmüyordu; §18.2'nin "Adım tavanı" ve "Görev kümesi" satırları hâlâ
  böyle. Deneyin tablosunda her anahtar tek sözcük.

Yeni satırların kaynakları:
- `step_ceiling`: sürücünün üç sabiti.
- `min_expected_saving`: beş koşul yapılandırması; tek değer olmalı.
- `library_id`, `index_id`, `covered_tasks`: analiz kümelerinin dosyası.
- `task_set`, `task_order_seed`, `task_order`: sıra dosyası. Dosya kendisine karşı da
  sınanıyor.
- `conditions`: sürücünün koştuğu `PHASE_ONE`, ve her ad koşucunun kurabildiği bir koşul
  olmalı.
- `runtime`: defterin ve README'nin çalışma zamanı seçme satırları.
- `model_file_gb`: tek kaynak. Önyükleme bu satırı okuyor, denetim bunu doğruluyor.

Deneyin 22 değer satırının hepsi karşılaştırılıyor, "??" yok. `bir1` ve `b7l` hâlâ geçiyor.
Önceki bölümlerin karşılaştırılamayan satırları eskisi gibi yalnız listeleniyor; bu karar
onlara dokunmuyor.

**Ön koşul denetimi deneyin kütüphane okuduğunu biliyor.** `check_prerequisites.py`
koşulu tek bir `koşul` satırından okuyordu. Deney üç koşulu bir liste olarak bildiriyor;
listeden biri bile kart taşıyorsa kütüphane isteniyor. Koşucusu `--condition` alan bir
komut için "koşucunun sabit koşulu" artık okunmuyor, çünkü böyle bir sabit yok.

**Defter deneyi koşuyor.** Dördüncü hücre şu: `require_colab_environment.py &&
run_experiment.py dny --tasks 10`. Hücrenin metni, ilk hücre ve README §19.6'ya atıf
veriyor. `--tasks` her oturumda kullanıcının seçtiği dilim boyutu, şart değil.

**Defter denetiminin arıza testleri taşındı.** `tests/test_colab_notebook.py`'deki dört arıza `bir1`'in hücre metnine bağlıydı ve kapı onları yakaladı: artık yeni hücre metnine enjekte ediliyorlar. Biri anlamca değişti. "Önceki koşunun epizot sayısı" arızası, bildirilen tavanın metinden düşmesini sınıyordu. Deneyin bildirilmiş bir epizot tavanı yok, o yüzden arıza artık "bildirilmemiş bir epizot sayısı yazılması"; denetim onu da reddediyor.

**Ateşlediği gösterildi.** Yeni testler eski kodda düştü. Beş mutasyonda testler düştü:
- karşılaştırılamayan satır yalnız listelenince,
- okunmayan satır sorulmayınca,
- sıra satırı kendisiyle karşılaştırılınca,
- ön koşul denetimi listeyi yok sayınca,
- protokol `Y-6.2` için 102 yazınca.

### K-186 — Kısmi okuma yasağı ve dilimlerin karşılaştırılabilirliği makineyle

**Karar.** Tam küme bitmeden hiçbir onaylayıcı yorum yapılmıyor. Kısmi sonuç yalnız
betimsel: biten görev, yazılan epizot, tüm koşulların birlikte ortalama süresi. İlan ön
kayıt A.7'nin 26 Eylül ekinde.

**Karşılaştırılabilirlik kuralı, kullanıcının kararı.** Ölçümü tanımlayan yollardan biri
iki dilim arasında değiştiyse dilimler havuzlanamıyor ve değişiklik tarihli bir ek
istiyor. Liste dışındaki değişiklik serbest.

`scripts/analyze_experiment.py` her deney epizodunun künyesindeki commit'i deneyin ilk
epizodunun commit'iyle karşılaştırıyor. Karşılaştırma ölçümü tanımlayan yollar listesi
(`MEASUREMENT_DEFINING_PATHS`) üzerinden yapılıyor. İlk epizottan aynı biçimde farklı
olan epizotlar bir karşılaştırılabilirlik grubu oluşturuyor. Kırılma sayılan durumlar:
- Bir dilim iki gruba yayılıyorsa (dilim içi).
- Ardışık iki dilim farklı gruplardaysa (dilimler arası).
- Git'in okuyamadığı bir commit.

Kırılma varsa betik sıfır olmayan kodla çıkıyor; havuzlama hiçbir yerde sessizce olmuyor.
Karşılaştırma bir öncekiyle değil hep ilkiyle yapılıyor, sürücünün durma kuralında olduğu
gibi.

**Açık olan.** `--confirmatory` tam kümeden önce reddediliyor. Tam kümeden sonra da henüz
bir şey hesaplamıyor: onaylayıcı analiz bu betikte yok, ve betik bunu söylüyor.

**Ateşlediği gösterildi.** `tests/test_analyze_experiment.py` eski kodda düştü. Dört
mutasyonda testler düştü:
- onaylayıcı kapı açılınca,
- dilim içi kırılma sayılmayınca,
- karşılaştırma bir önceki commit'le yapılınca,
- rapora bir geçiş oranı satırı eklenince.

### K-185 — Deneyin sürücüsü: dilim, durma kuralı, `dnyk` ön kontrolü, havuzlanmış özet

**Karar.** `scripts/run_experiment.py dny --tasks N` faz 1'i koşuyor.
- Açık bir dilim yoksa yeni dilim, bildirilen sıranın dilime girmemiş ilk N görevi. Yeni
  dilimin görev listesi koşudan önce kayda yazılıyor.
- Her görevde 3 tohum × 3 koşul koşuyor (`baseline`, `skills_failures`,
  `irrelevant_retrieval`), tohum sırasıyla. Kartlı kolun ulaşamadığı görevde yalnız
  baseline koşuyor (K1).
- Bir önceki oturum dilimi yarım bıraktıysa, N ne derse desin önce o dilim tamamlanıyor.
- Her epizodun kendi koşu kimliği var: `dny-<koşul>-s<tohum>-<görev>`, dolayısıyla kendi
  künyesi.
- Oturum, sürücünün bir çağrısı. Kimliği başlangıç zamanı (UTC) artı boot id'nin başı.

**Durma kuralı, kullanıcının kararı.** Deneyin ilk epizodundan beri ölçümü tanımlayan bir
yol değiştiyse sürücü hiçbir şey koşmadan duruyor. Uyarıp devam etmiyor. Karşılaştırma
ilk epizodun commit'iyle yapılıyor, bir öncekiyle değil: yoksa her biri tek başına göze
batmayan iki değişiklik toplamda başka bir ölçüme varırdı. Git okunamazsa bu da değişiklik
sayılıyor ve sürücü yine duruyor; yapılmamış bir karşılaştırma uyum demek değil.
`--accept-path-change` devam ettiriyor. Koşucu, bu bayrakla geçen her epizoda
`experiment_episodes.path_change_accepted = 1` yazıyor. Bayrak oturum başına veriliyor,
kalıcı değil.

**Koşmadan önce başka neler duruyor.**
- Kayıt künye kısıtlarını taşımıyorsa.
- Deney tabloları şemanınki değilse.
- Koşucunun açtığı kütüphane, analiz kümelerinin türetildiği kütüphane değilse.
- Dilimin görevlerinde bugün kurulan slotlar kümelerin türetildiği slotlar değilse.
- Deney sınırı aşılmışsa.
- Ön kontrol düşerse.

Ön kontrol `dnyk-onkontrol<n>` kimliğiyle, kurulumun zaten dokunduğu `024c982_1`'de
koşuyor. Tavanı 3; `n` kayıttan sayılıyor.

**Ölçülen bir etkileşim, ve çözümü.** Dokunulan liste her ön kontrol ailesini kaynak
olarak tutuyor; kayıtta `bir1-onkontrol2` … `7` ayrı ayrı yazılı. Her oturumun `dnyk`
ön kontrolü listeye yeni bir aile ekler. Üyelik değişmez ama listenin kayıtla tam
karşılaştırması ikinci oturumda "liste kaydın gerisinde" diye dururdu. Sürücü bu yüzden
şunu yapıyor:
- Üyeliği işlenmiş listeden okuyor (`load_touched(series=())`).
- Kayıttan gereken tek şeyi, deney sınırını, doğrudan denetliyor (`experiment_problems`).
- Tam karşılaştırmayı listenin yeniden üretildiği yere bırakıyor: kayıt geri getirildiğinde
  yerelde `build_touched_tasks.py` ile.

Bunun bedeli, her oturumdan sonra listenin kaynağının bir satır büyümesi ve yerelde
yeniden üretilip commit edilmesi.

**Başarısız epizot.** Sürücü ilk başarısız epizotta duruyor. Aynı komut yeniden
çalıştırılınca kaldığı yerden sürüyor: tamamlanan epizotları kayıttan atlıyor, yazılı
olanların koşulunu `resume_check` ile karşılaştırıyor. Benim seçimim. Devam etseydi, her
epizotta tekrarlanan bir ret oturumu boşa harcardı.

**Özet.** Yalnız biten görev sayısı, yazılan epizot sayısı ve tüm koşulların birlikte
ortalama süresi. Koşula göre süre yok: bir epizodun süresi model çağrısı sayısını izliyor,
yani koşula göre süre birincil metriğin başka bir adı olurdu. `--dry-run` planı yazıyor,
kayda hiçbir şey yazmıyor.

**Ateşlediği gösterildi.** `tests/test_run_experiment.py` eski kodda toplanamadı. Beş
mutasyonda testler düştü:
- değişiklik yalnız yazdırılıp devam edilince,
- ilk yerine son epizodun commit'i alınınca,
- açık dilim önce tamamlanmayınca,
- kartsız görevde üç koşul koşunca,
- özete koşula göre bir alan eklenince.

### K-184 — Analiz kümeleri koşucunun kendi slotlarından türetiliyor

**Karar.** Her onaylayıcı kontrastın okunduğu görev kümesi elle yazılmıyor.
`scripts/setup/measure_experiment_sets.py`, koşucunun her slotu kurduğu fonksiyonu
(`zihin.slots.compose`) koşucunun açtığı kütüphaneyle (`open_library`) çağırıyor. Bunu
sıradaki her görev ve kart taşıyan her koşul için yapıyor. Kümeler bu slotlardan tek bir
kuralla çıkıyor (`zihin.experiment.analysis_sets`). Kural şu: görev, kartlı kol ona en az
bir kartla ulaşıyorsa (A.3'ün kapsanan görevi) ve kontrastın iki kolundan hiçbiri kartlı
kolun hacminin altında koşmuyorsa (`K-181`) kümededir. Çıktı `results/experiment-sets.json`.

**Ölçüldü** (kütüphane `v0-gap2-sup3-0c3f4ac`, indeks `v0-sup1-0c3f4ac`, 104 görev):

| Kontrast | Karşılaştırma | Görev |
|---|---|---|
| `Y-1` | `skills_failures` – `baseline` | **103** |
| `Y-6.2` | `skills_failures` – `irrelevant_retrieval` | **101** |
| `Y-4` | `failures` – `baseline` | **101** |
| `Y-5` | `skills` – `baseline` | **103** |
| `Y-6.2`, ikinci okuma | `skills` – `irrelevant_retrieval` | 101 |

- Kapsanmayan tek görev `8ce6779_3`.
- Hacmi eşleşmeyen iki görev `d194965_1` ve `d194965_3`. Bu iki görevde hem `failures`
  hem `irrelevant_retrieval` beş yerine üç beceri kartıyla koşuyor.
- `skills` her görevde eşleşiyor.
- Faz 1 **930** epizot: 103 görevde 3 koşul × 3 tohum, `8ce6779_3`'te yalnız baseline × 3.

**Raporumdaki hata.** Tasarım raporunda `Y-5` için 104 yazmıştım. `skills_failures`'ın
kartı olmayan görevde `skills`'in de kartı yok ve K1 kart taşıyan her koşula uygulanıyor.
Kullanıcı bunu yakaladı. Ölçüm 103 veriyor.

**Sıradaki yerleri.** `8ce6779_3` 25., `d194965_3` 65., `d194965_1` 95. sırada.

**Ateşlediği gösterildi.** `tests/test_experiment_sets.py` eski kodda toplanamadı. Üç
mutasyonda testler düştü:
- kısa kol dışlanmayınca,
- kapsanmayan görev dışlanmayınca,
- her göreve üç koşul sayılınca.

Kayıt olan makinede ek bir test slotları bugün yeniden kuruyor ve dosyayla karşılaştırıyor.
CI'da kayıt yok, orada atlanıyor.

### K-183 — Görev sırası ilan edilmiş bir tohumdan, dosyada, yeniden üretilerek sınanıyor

**Karar.** Deneyin 104 görevlik sırası `sha256("123:" + görev)` değerine göre artan
sıralama. 123, `config/models.yaml`'daki `base_seed`; bu değer bu karardan çok önce ilan
edilmişti, yani sıranın kendine ait bir serbestliği yok. Denenip atılabilecek ikinci bir
tohum yok. Dilimler sıranın başından alınıyor. Deney ilerlerken görev seçilmiyor.

**Gerekçe, kullanıcının kabul ettiği varsayılan.** Önceki dilim görüldükten sonra
seçilen görev, sonuca göre seçilmiş bir görevdir. Karıştırma değil özet kullanıldı,
çünkü karıştırma arkasındaki rastgele sayı üretecinin uygulaması kadar
tekrarlanabilir. Bildirilen bir dizgenin özeti ise her yerde aynı.

**Nerede.** `results/experiment-order.json` şunları taşıyor: tohum, yöntem, 104 görevlik
sıra ve sıranın özeti (`dcbdbd43cdc4…`). Örneklem eşik türetmesinin kendi tanımından
alınıyor (`derive_pass_threshold.action_stratum`), yeniden yazılmıyor.
`scripts/setup/build_experiment_order.py --check` sırayı örneklemden ve tohumdan yeniden
üretip karşılaştırıyor. `zihin.experiment.load_order` dosyayı kendisine karşı sınıyor:
özet sıranınki olmalı, sıra da bildirilen anahtarın kendi görevlerine verdiği sıra olmalı.

**Ateşlediği gösterildi.** `tests/test_experiment_order.py` eski kodda toplanamadı. Üç
mutasyonda testler düştü:
- anahtar tohumu yok sayınca,
- üretici alfabetik sıralayınca,
- özet denetimi kaldırılınca.

### K-182 — Deney epizodu nereye ait olduğunu kendi işleminde yazıyor; koşucu donuyor

**Karar.** Kayda iki tablo girdi.
- `experiment_slices`: bir dilim açılırken görev listesi, koşudan önce. Dilim, sıradaki
  N görev. Satırda görevin sıradaki yeri, dilimi açan oturum ve dilimin açıldığı commit
  var. Bir görev tek dilimde olabilir.
- `experiment_episodes`: epizot kimliğine bağlı bir satır, epizotla aynı işlemde. Satır
  dilimi, oturumu, `volume_matched`'i (baseline'da NULL) ve yol değişikliğini kabul
  bayrağını taşıyor.

CHECK'ler tanımsız değeri reddediyor. Yazıcı, dilimin tutmadığı bir görevin satırını
reddediyor.

**Kullanıcının kararı: künyenin yanında, künyede değil.** Var olan dosyaya sütun
`ALTER TABLE` ile giriyor ve CHECK taşımıyor (`S-29`). Tablo ise şemanın kendi CREATE'iyle
kuruluyor ve CHECK'leri de geliyor.

**Koşucu `dny` koşusunu kendisi reddediyor.** `zihin.declared.experiment_run_problems`
ayrıştırılmış seçeneklere bakıyor ve koşucu kaydı açmadan önce onu soruyor. Beş ret
sebebi var:
- `--allow-dirty-tree`, kısaltmaları dahil.
- `--condition` ile adlandırılmamış bir koşul.
- `test_normal` dışında bir bölme.
- Dilim yok.
- Oturum yok.

Denetim (`K-180`) bildirilen komutu okuyordu. Koşucuyu doğrudan çağıran bir yol o
denetimle hiç karşılaşmıyordu; bu ret o yolu kapatıyor. Deney dışındaki bir koşuya dilim,
oturum ya da kabul bayrağı verilirse o da reddediliyor.

**Açık kalan: tetikleyici yok.** Eksik tabloyu mevcut dosyaya ekleyen göç şemayı `;`
üzerinden bölüyor. Tetikleyicinin gövdesi de `;` taşıyor. Bu yüzden buraya yazılan bir
tetikleyici taze dosyada olurdu, deneyin yazdığı seride olmazdı. Salt ekleme bu iki
tabloda yazıcılara dayanıyor, `run_ledger`'da olduğu gibi.

**Koşucu donuyor.** `scripts/record_run.py`, beş koşulu da kuran bu hâliyle ölçümü
tanımlayan bir yol olarak donuyor, faz 2 için de değişmeyecek. İlk `dny` epizodundan
sonra sürücünün durma kuralı bunu zorluyor.

**Ateşlediği gösterildi.** `tests/test_experiment_record.py` eski kodda toplanamadı. Dört
mutasyonda testler düştü:
- ret kirli bayrağa bakmayınca,
- dilim üyeliği sorulmayınca,
- `volume_matched`'in CHECK'i silinince,
- koşucu reddi kendi seçeneği yerine sabit bir değerle çağırınca.

Son mutasyonu ilk yazdığım test yakalamadı: aradığı metin dosyada iki çağrıda geçiyordu.
Test artık çağrının kendi argümanlarını okuyor.

### K-181 — Eşleşemeyen görevde kol eksik koşar ve işaretlenir; beş koşul tek seçimden

**Karar.** Alakasız havuz bir kart türünde kartlı kolun (`skills_failures`) sayısına
yetmediğinde kol havuzda olanla koşuyor ve epizotları `volume_matched = 0` taşıyor.
`volume_matched = 0` bir kolu içeren her onaylayıcı analiz o görevleri dışlıyor. Ön
kayıt A.4'ün üçüncü 25 Eylül ekine 26 Eylül tarihli Düzeltme.

**Gerekçe, kullanıcının kararı.** `K-179`'un "koşmuyor" hükmü benim seçimimdi. Eksik
kontrol "içerik önemli" yönünde yanlılık yapar, o yüzden içerik kontrastı o görevlerde
okunmamalı; ama koşmamak, kolu içermeyen analizlerden de görevi alıyordu. İşaret
koşudan önce ilan edildiği için dışlama sonuca bakmıyor.

**Beş koşul tek seçimden.** `src/zihin/slots.py` (`compose`), deneyin beş koşulunun
slotunu kuruyor: `baseline`, `skills_failures`, `skills`, `failures`,
`irrelevant_retrieval`. Görevin kendi kartından gelen tür `retrieve`'dan,
alakasız türler `retrieve_irrelevant`'tan geliyor ve kartlı kolun sayısına
kesiliyor. Koşucu `--condition` ile beşinden birini adıyla koşuyor. Faz 2'nin iki
koşulu (`skills`, `failures`) bu commit'ten önce koşucuda yoktu. Modül ölçümü
tanımlayan yollar listesinde.

**Kartsız görev.** Kartlı kolun slotu diğerlerinin referansı olduğu için, onun boş
olduğu görevde her slot boşa kesiliyor ve koşucu kart taşıyan bir koşulu orada
başlatmıyor (`Slot.runnable`).

**Eski adlar.** `--cards` ve `--irrelevant-cards` duruyor. İkincisinin epizotları
`skills_failures_irrelevant` adını taşımıştı (§12), ve o bayrakla yapılan bir koşu o
adı almaya devam ediyor. Deney koşullarını `--condition` ile adlandırıyor.

**Ateşlediği gösterildi.** `tests/test_slots.py` eski kodda toplanamadı. Üç mutasyon:
`skills` koşulunda beceri havuzu alakasıza çevrilince, kesim kartlı kolun sayısı
yerine slot boyutuna yapılınca, ve kartsız görevde kol koşulabilir sayılınca testler
düştü.

### K-180 — Deneyin komutu `--allow-dirty-tree` taşıyamaz

**Karar.** `scripts/check_declared_conditions.py`, `dny` önekli bir koşunun
komutunda `--allow-dirty-tree` görürse — ya da argparse'ın ona çözdüğü herhangi
bir kısaltmasını — hiçbir değeri karşılaştırmadan reddediyor. Kural
`zihin.declared`'da (`experiment_command_problems`). İlan kurulum protokolü §19.5'te.

**Gerekçe, kullanıcının kararı.** A.9'un sıfır bütçesi "değişiklik koşuyu durdurur"
diyor ve bunu zorlayan kapılardan biri kirli ağaç kapısı; bu bayrak kapıyı atlıyor.

**Ölçülen bir delik, kapatıldı.** argparse uzun seçeneklerin belirsiz olmayan her
kısaltmasını kabul ediyor: `record_run.py`'de `--allow`, `--allow-dirty` ve `--al`
aynı bayrağa çözülüyor. Yalnız tam yazıma bakan bir denetim bu üçünü geçirirdi.

**Nereden geçiyor.** `scripts/run_declared.sh` komutu çalıştırmadan önce bu betiği
koşturuyor; Colab'da önyüklemenin ön koşul adımı onu çağırıyor. İki yol da buradan
geçiyor. Bugün `dny` bir şartlar bölümü ilan etmediği için betik `dny`'yi zaten
"ilan edilmemiş" diye reddediyor; bayrak denetimi şartlar tablosu geldiğinde
çalışacak yerde duruyor, ve test bir `dny` bölümünü sahteleyerek o yolu koşturuyor.

**Ateşlediği gösterildi.** Yedi yeni test (`tests/test_declared_conditions.py`) eski
kodda düştü. Eşleştirme tam yazıma indirilince üç kısaltma testi, betiğin çağrısı
kaldırılınca uçtan uca test düştü. İlan edilmiş gerçek koşular (`bir1`, `b7l`)
denetimden hâlâ geçiyor.

**Açık kalan.** Koşucunun kendisi (`record_run.py`) bayrağı `dny` için reddetmiyor;
denetimi atlayıp koşucuyu doğrudan çağıran bir yol bayrağı taşıyabilir.

### K-179 — Kart sayısı iki kolda eşit; eşleşemeyen görevde kontrol kolu koşmuyor

**Karar.** `matched_to` alakasız havuzu, kartlı kolun o görevde slota koyduğu
sayıya tür tür kesiyor: ne fazla ne eksik, sıfırsa sıfır. Havuz yetmiyorsa kol o
görevde tanımsız ve koşmuyor; `scripts/record_run.py` kontrol kolunu bu kesimle
kuruyor ve tanımsızsa başlatmıyor. İlan ön kayıt A.4'ün üçüncü 25 Eylül ekinde.

**Gerekçe, kullanıcının kararı.** A.4 görev başına eşit kart sayısı istiyor; yeni
kontrol kolu çoğu görevde kartlı koldan fazla kart verebiliyordu, iki görevde az.

**Ölçüldü** (`results/declared-filters.json`). `irrelevant_retrieval` 104 görevin
102'sinde eşit; `d194965_1` ve `d194965_3`'te havuz 5 beceri yerine 3 veriyor.
`failures` koşulu beceri slotunu aynı havuzdan doldurduğu için aynı iki görevde
tanımsız; `skills` koşulu her görevde tanımlı.

**Eşleşemeyen görev: benim seçimim, gerekçesiyle.** Kullanıcı "atlanır mı, eksik
mi koşar" diye sordu ve ilanı bana bıraktı. **Atlanıyor**: eksik bir kontrol kolu
kontrol ettiği koldan az hacim taşır, ve doldurulacak başka kart yok. Birincil hücre
etkilenmiyor; o kolu içeren karşılaştırmalar kolun tanımlı olduğu görevlerde
yapılıyor ve dışarıdakiler adıyla raporlanıyor.

**Ateşlediği gösterildi.** Yeni testler (`tests/test_retriever.py`) eski kodda
toplanamadı. Kesim kaldırılınca dört test, eksiklik bildirimi kaldırılınca bir test
düştü.

### K-178 — Deney sınırı `dny` öneki; ölçüm olmayan deney koşuları `dnyk`

**Karar.** Deneyin koşuları `dny` önekiyle koşuyor. Dokunulan görev üreticisi `dny`
epizotlarını saymıyor: onlar dokunma değil, deney. Deneye ait ama hiçbir şey
ölçmeyen koşular — ön kontrol, sağlık kontrolü, duman koşusu — `dnyk` önekini
alıyor ve dokunma sayılıyor. İlan kurulum protokolü §19'da ve ön kayıt A.10'un
25 Eylül ekinde. Değerler `zihin.declared`'da tek yerde.

**Gerekçe, kullanıcının kararı.** Kural sınır bilmiyordu; deneyin ilk epizodu bir
değerlendirme görevine dokunduğu anda liste reddedilirdi. Sınır commit'e değil
öneğe bağlı, çünkü kod deney boyunca değişebilir ve önek değişmez.

**Soru: `dny` önekiyle koşan ama deney olmayan bir şey olabilir mi? Ölçüldü:
evet.** Bu depodaki her tarama koşucusu sağlık kontrolünü kendi öneki altında,
`<önek>-onkontrol[N]` diye yazdı. Kayıtta yedi önek altında on üç böyle epizot var
(`b14`, `b15l`, `b32c`, `b3l`, `b7l`, `bant3`, `bir1`). Aynı kalıpla yazılmış bir
deney koşucusu sağlık kontrolünü sınırın içine koyardı. Kuru koşu epizot yazmıyor.
Bu yüzden:

1. Ölçüm olmayan deney koşuları `dnyk` alıyor.
2. Yükleyici, ailesi `onkontrol` taşıyan bir `dny` koşusunu reddediyor.
3. Yükleyici, değerlendirme örnekleminin dışındaki bir görevin `dny` epizodunu da
   reddediyor — eğitim, dev, zorluk bölmesi ya da dokunulmuş bir görev. Liste `dny`'yi
   saymadığı için başka hiçbir şey bunu görmezdi.

**Ateşlediği gösterildi.** Yeni testler (`tests/test_touched_tasks.py`) eski kodda
düştü. `dny` dışlaması kaldırılınca "deney listeyi değiştirmez" testi düştü;
yükleyicinin sınır denetimi kaldırılınca ön kontrol ve örneklem dışı testleri düştü.

**Sınırı.** İkinci şartın ölçütü bir ad: bugün koşucuların yazdığı tek işaret
`onkontrol`. Deneyin koşu kimliği dilbilgisi dilimlemeyle ilan edilecek; o zaman
kural bir izin listesine sıkılaştırılabilir.

### K-177 — Ayar bütçesi sıfır; ön kaydın Bölüm A'sı donmuş

**Karar.** A.9'un boş bıraktığı sayı 0. Deney ilan edilen yapılandırmayla koşuyor;
ölçümü tanımlayan bir şeyin değişmesi koşuyu durduruyor. İlan ön kayıt A.9'un 25
Eylül ekinde.

**Gerekçe, kullanıcının kararı.** Bütçe sayısı yokken "tükendi" hükmü verilemiyordu
ve A.9'un kuralı işlemiyordu; Bölüm A bu yüzden donmuş sayılmıyordu.

**Neyi düşürdüğü.** Deney verisine bakılarak parametre değiştirme imkânını. Dört
tüketilmiş revizyon bu sayıdan önce ve mekanizma sonucu görülmeden yapıldı; sıfır
ilandan sonrasını sayıyor, yani bütçe ilan anında tükendi ve olumsuz bir sonuç
tasarım hakkında bir sonuç.

**Zorlayan, kodda doğrulandı.** Kirli ağaç kapısı (`K-76`), devam denetiminin
ölçümü tanımlayan yol değişince reddetmesi (`S-31`, `K-76`), ve ilan edilen koşul denetimi
(`K-136`). **Açık:** kirli ağaç kapısının `--allow-dirty-tree` kaçışı; deneyin
komutunun onu taşımadığını denetlemek deneyin koşul tablosuyla kurulacak.

### K-176 — Alakasız kol yalnız alakada farklı: aynı süzgeçler, hata kartları dahil

**Karar.** `retrieve` ve `retrieve_irrelevant` tek bir seçimden (`_select`) geçiyor
ve aynı argümanları alıyor; fark tek bir bayrak: görevin uygulamalarıyla ilişki
ters çevriliyor. Alakasız kol artık değer eşiğini uyguluyor ve başka uygulamaların
hata kartlarını taşıyor. `scripts/record_run.py`'nin kontrol kolu kartlı kolun
süzgeçleriyle çağırıyor. İlan ön kayıt A.4'ün 25 Eylül ekinde.

**Gerekçe, kullanıcının kararı.** Kontrol kolu yalnız alakada farklı olmalı. Eski
kol hem türde hem hacimde farklıydı: hata kartı yoktu, değer eşiği yoktu.

**Düşen tanım.** §12'nin üç kollu koşusu alakasız kolu "yalnız beceri" diye
tanımlamıştı ve bu tanım koşucuya ve bir teste de yazılmıştı
("the irrelevant pool carries no failure card"). Test kaldırıldı; yerine
"başka uygulamaların hata kartlarını taşır" testi girdi. Üç kollu koşunun kayıttaki
epizotları eski kolla koştu ve öyle kalıyor.

**Ölçüldü** (`results/declared-filters.json`): eski kolun slotu 104 görevin 86'sında
kartlı koldan küçüktü, ilan edilen kolunki 2'sinde. Kontrol slotuna toplam 520 hata
kartı giriyor.

**Ateşlediği gösterildi.** Yeni testler eski getiricide düştü (on hata). Kontrol kolu
değer eşiğini atlayınca bir test, hata kartlarını yeniden bırakınca dört test düştü.

**Açık kalan.** Görev başına kart sayısını iki kolda eşitlemek (A.4, `K-29`) koşucuda
kurulu değil; yeni kol çoğu görevde kartlı koldan fazla kart verebiliyor. Deneyin koşu
yolunu kuran işin parçası.

### K-175 — `min_expected_saving = 1`: bir beceri kartı en az bir model çağrısı kazandırmalı

**Karar.** Değer 1, altı koşul yapılandırmasında aynı (`retrieval.min_expected_saving`),
ve koşucu onu oradan okuyor. İlan ön kayıt A.4'ün 25 Eylül ekinde.

**Gerekçe, kullanıcının kararı.** Metriğin tanımından: birincil metrik model
çağrısı, ve bir beceri en az bir çağrı kazandırmalı. Sıfır tasarruflu bir kart
yalnız hacim ekler.

**Neyi düşürdüğü, ölçülmüş** (`results/declared-filters.json`,
`scripts/setup/measure_declared_filters.py`). Üç beceri: `POST spotify.auth/token`
(destek 27, kütüphanenin en yüksek destekli becerisi; 28 oluşumun 28'i tek adım)
ve iki `following_artists` tekrarı (destek 5 ve 4; medyan tek adım). Üçü de aynı
25 birincil görevin slotundaydı; o görevler bir beceri kartı kaybediyor, hiçbiri
sonuncusunu değil. Getirilebilir beceri 11 → 8.

**Neden ilan edilmemiş bir sıfırdı.** Getirici eşiği varsayılansız zorunlu argüman
olarak alıyordu (`K-50`, `K-85`), ama tek çağıran — `scripts/record_run.py` — onu
`0` diye yazıyordu. Varsayılan getiriciden koşucuya taşınmıştı.

**Ateşlediği gösterildi.** İki yeni test (`tests/test_config_schema.py`) eski kodda
düştü. Koşucu `0`'a geri döndürülünce biri düştü. Bir koşul yapılandırması başka bir
eşik taşıyınca ikisi düştü: eşiğin aynı olması testi ve `K-31`'in saf içerik
kontrastı — iki koşul arasında ayrışan bir eşik kontrastı ikinci bir alanla yükler.

**Sınırı.** `observed_steps` bir medyan; tekrar becerilerinde oluşumların bir kısmı
iki adım sürüyor (%18 ve %37). Kural medyanı okuyor ve bu burada yazılı.

### K-174 — Aralık genişliği taraması eylem tabakasında; havuzlanmış tablo süperseded

**Karar.** `scripts/setup/measure_interval_width.py` artık birincil örneklemde,
eylem tabakasında koşuyor: 104 görev. Tabakayı kendisi tanımlamıyor,
`derive_pass_threshold.py`'nin `action_stratum`'ından alıyor. Yeni tablo
`results/interval-width-action.json`. Eski tablo — iki tabaka birlikte, 119 görev —
`results/interval-width.json`'da duruyor, silinmedi, ve kendi içinde süperseded
işaretli.

**Gerekçe.** Tarama tabakalamadan (`K-144`) önce yazılmıştı ve birincil tahminin
okunmadığı bir örneklemi anlatıyordu (ön kayıt A.6'nın 25 Eylül düzeltmesi).

**Ne değişti** (aynı kayıt, aynı liste, aynı tohum; 92 geçen epizot):

| Izgara | Hücre | Medyan genişlik, havuz → eylem | Hücre başına değişim |
|---|---|---|---|
| A — aynı görevler, daha az çağrı | 20 | 0,72 → 0,74 | −%24 … +%41, medyan +%8 |
| B — düşenler çözüme dönüyor | 20 | 4,70 → 6,14 | −%1 … +%61, medyan **+%26** |

**Okuma.** A'nın +%8'i örneklemin 119'dan 104'e inmesinin kök-n beklentisi
(+%7) kadar ve hücre aralığı, geçen tur ölçülen tohum gürültüsüyle (−%25 … +%45)
aynı büyüklükte. B'ninki değil: yirmi hücrenin on dokuzu daha geniş. Sebep
yapısal: cevap tabakasının görevleri küçük çapalı, yani küçük tavanlı; onlar
çıkınca bir sansür dönüşünün boyu büyüyor. Havuzlanmış tablo B'yi medyanda
yaklaşık dörtte bir dar gösteriyordu.

**Ayakta kalan.** `S-66`'nın "B, A'dan çok daha geniş" cümlesi eylem tabakasında
da tutuyor: medyanda 8,2 kat. Türetilen eşik bu taramadan gelmiyor (A.6'nın
düzeltmesi), yani eşik değişmedi.

**Ateşlediği gösterildi.** Üç yeni test (`tests/test_interval_stratum.py`) eski
betik ve eski eserle düştü: betik kendi örneklemini tanımlıyordu, birincil
örneklemin boyu üç eserde aynı değildi, eski tablo süperseded demiyordu.

### K-173 — Colab önyüklemesi Drive'daki seriyi doğruluyor; bulamazsa ya da tutmazsa duruyor

**Karar.** `scripts/colab_bootstrap.sh`'nin E adımı, Drive'daki seriyi bağlamadan
**önce** `scripts/verify_series_merge.py --check --database <Drive yolu>` koşturuyor.
Birleşmenin bıraktığı her önek en az o kadar epizotla — bugün 389 — ve
`run_ledger` tablosu yoksa önyükleme duruyor. Drive'da dosya yoksa da duruyor:
"yeni seri kur" dalı kaldırıldı.

**Gerekçe.** Kullanıcı yerel birleşik dosyayı Drive'a kopyalayacak; kopyanın
doğru dosya olduğunu insanın gözü değil önyükleme söylemeli. Seri iki kez böyle
bölündü: bir kez Drive'daki yarım dosyaya yazılarak, bir kez yerel dosyanın
üzerine başka bir dosya konarak (`S-74`). İkisinde de soran bir şey yoktu.

**"Yeni seri kur" dalı neden gitti.** Drive'da dosya bulamayan bir oturum boş bir
seri açıp ona yazıyordu. Seri 3 var; onu bulamayan bir oturumun yapacağı doğru iş
durmak, üçüncü bir parça açmak değil.

**Ateşlediği gösterildi.** İki yeni test (`tests/test_series_check.py`) eski
önyüklemede düştü. Önyüklemenin E adımı kendi metniyle üç Drive durumunda
koşturuldu: birleşik kayıt doğrulandı ve bağlandı; 269 epizotluk Colab dosyası
dokuz problemle durdu ve bağlanmadı; dosya yokken durdu ve kopyalama talimatını
adıyla verdi. Kopyalama adımları `experiments/colab/README.md`'de.

**Sınırı.** Bu doğrulama oturumun başında. Oturum ortasında Drive'daki dosyanın
değiştirilmesini sormuyor.

### K-172 — Seri 3'ün birleşme doğrulaması sürekli bir denetim oldu

**Karar.** `scripts/verify_series_merge.py --check` birleşmenin bıraktığını her
koşuda soruyor ve `scripts/local_checks.sh`'ye bağlı. Hiçbir şey yazmıyor.
`--database` alıyor, yani bir Colab oturumu onu Drive'daki kopyaya yöneltebilir.

**Gerekçe.** Birleşmenin kendi doğrulaması bir kez koştu (`S-74`), ve bir kez koşan
bir denetim koşmamış sayılır. Bölünme tam da hiçbir şeyin sormadığı bir anda,
dosyanın yolunda başka bir dosyayla değiştirilmesiyle oldu.

**Ne soruyor.**

1. `results/series-3-merge.json`'un kaydettiği her önek hâlâ orada, en az o kadar
   epizotla. Kayıt yalnız ekleme alıyor; küçülen ya da kaybolan bir önek, yoldaki
   dosyanın seri olmadığı demek. Büyüyen seri geçiyor.
2. Seriyi `database` alanında adlandıran her tarama eserinin öneki orada.
3. `run_ledger` şemanın tablosu (`K-171`).

**Ateşlediği gösterildi.** Altı yeni test (`tests/test_series_check.py`) eski
betikte düştü, yenisinde geçiyor. Gerçek dosyalarda: bugünkü kayıt geçti (389
epizot); birleşmeden önceki Colab kaydı dokuz problemle reddedildi (dört eksik
önek, dört tarama eserinin iddiası, ledger); göçten önceki birleşik kayıt yalnız
ledger yüzünden reddedildi.

### K-171 — `run_ledger` gerçek kayda hiç girmemişti; göç uygulandı, ön koşul denetimi soruyor

**Karar.** Seri 3 `zihin.records.open_database` üzerinden bir kez açıldı ve
şemanın kendi `CREATE TABLE`'ı `run_ledger`'ı kısıtlarıyla birlikte kurdu.
`scripts/setup/check_prerequisites.py` artık her koşuda tabloyu soruyor: yok ya
da şemanınkinden farklıysa eksik diyor. Şemayı okuyan kod tek yerde
(`_schema_statements`, `schema_statement`, `table_matches_schema`).

**Soru: birleşik dosya göç öncesi parçalardan mı kuruldu, yoksa göç hiç koşmadı
mı? Ölçüldü: ikisi de, ve ikincisi birincisinin sebebi.**

| Olgu | Değer |
|---|---|
| `run_ledger` şemaya girdi | `579d4f1`, 10 Eylül 2026 19:01 (+03:00) |
| Son `bir1` künyesi | 10 Eylül 2026 15:00 UTC — şemadan **bir saat önce** |
| Tabloyu taşıyan tek kopya | `~/gocme-denemesi.sqlite`: 156 epizot, 3 Eylül anlık görüntüsü; `K-162`'nin "gerçek dosyanın bir kopyasında denendi"si |
| Colab kaydının indirilen kopyaları (10 ve 13 Eylül) | tablo **yok** |
| Birleşik dosya | tablo **yok**: `scripts/merge_series.py` dosyayı `open_database` ile açmıyor |

Tablo, dosya yazma kipinde ilk açıldığında kuruluyordu. Bu kodla gerçek kayda
hiçbir yazma yapılmadı: koşu bitmişti. Göç yalnız eski bir kopyada gösterildi.

**Göç nasıl uygulandı.** Önce bir kopyada: yalnız `run_ledger` ve dizini eklendi,
hiçbir tablonun DDL'i ya da içeriği değişmedi. Bu ayrıca soruldu, çünkü aynı yol
şeması değişmiş izdüşümleri (`skills`, `failure_patterns`) boşaltıyor ve teslim
edilen kütüphane orada. İki kütüphane ve iki indeks yerinde kaldı. Sonra gerçek
kayıtta, aynı sonuçla. Göç öncesi dosya `~/yedek/zihin-3-merged-389-before-ledger.sqlite`.

**Ateşlediği gösterildi.** Beş yeni test (`tests/test_run_ledger_check.py`) eski
kodda toplanamadı bile; yenisinde geçiyor. Denetim dosyayı onararak açacak
biçimde bozulunca iki test düştü: bakarken tabloyu kuran bir denetim, eksikliği
göremez. Gerçek dosyalarda: birleşmeden önceki Colab kaydı ve göçten önceki
birleşik kayıt için **eksik**, göçten sonra **tamam**.

**Drive.** Drive'a kopyalanacak dosya bu, göç edilmiş hâli.

### K-170 — Kapsam dışı iki iş kuyruğa alındı; dil denetiminin kapsamı bir sınırlama

**Karar.** Bu turda bulunan ve dokunulmayan iki iş kuyruğa yazılıyor. Dil
denetiminin yalnız Python taraması `S-76` olarak kaydediliyor.

**Kuyruk.** İkisi de bu turda bilerek açık bırakıldı:

1. **Kod tarafında kalan Türkçe.** `K-77`'nin kuralı yorumların ve çalışma zamanı
   metinlerinin İngilizce olmasını istiyor; `scripts/check_language.py`'nin
   kapsamı dışında 20 izlenen dosya Türkçe düzyazı taşıyor (`S-76`). İş iki parçalı:
   denetimin kapsamını genişletmek, ve kapsama giren dosyaları çevirmek.
2. **`config/models.yaml`'daki tarih.** Yorum 32B için "21 Ağustos 2026'da
   eklendi" diyor. Ön kayıt A.11'in beşinci nokta eki o tarihi 26 Ağustos'ta
   düzeltti: ek 25 Ağustos'ta (`e2e40dd`) yazıldı. Yorum düzeltilmedi.

**Gerekçe.** Kullanıcının kararı: ikisi de bu turun kapsamı dışında. Sessizce
düzeltilmedi, sessizce de bırakılmadı; ikisi de burada ve `S-76`'da adıyla
duruyor.

### K-169 — Birincil hücrenin modeli 32B; keşifsel etiket yalnız seçime bağlı

**Karar.** Birincil hücre `qwen2.5-coder:32b-instruct-q4_K_M` üzerinde. İlan ön
kayıt A.2'nin 25 Eylül ekinde; özgün satır ("en büyük yerel nokta") duruyor.
Seçim keşifsel etiketli; `Y-1`'in hükmü onaylayıcı kalıyor.

**Gerekçe.** Birincil hücre fiilen 32B'ye taşınmıştı — biriktirme 32B'de koştu,
kütüphane onun epizotlarından — ama depoda bunu ilan eden bir ek yoktu. Yerel üç
nokta sıfır verdi; 32B eksenin tavanı bağlamayan tek noktası.

**Etiketin kapsamı, kullanıcının kararıyla: (i).** Keşifsel olan **seçim**. İki
okuma vardı: etiket yalnız seçime bağlı, ya da `Y-1`'in hükmüne de. İkincisi
deneyde onaylayıcı hiçbir şey bırakmazdı. Birincisinin dayanağı ölçüldü:
kayıtta 32B etiketli 265 epizodun 265'i `baseline`; seçim mekanizmanın etkisini
hiç görmedi.

**Zincirde düzeltilen bir halka.** `S-14` yukarı uzatmayı önceden
yetkilendirmemişti; aşağı daralmaya izin vermiş, yukarı yolu donanım yüzünden
kapalı yazmıştı. Uzatma sonradan alınmış bir karar; `K-133` ve A.11'in 20 Ağustos
eki bunu "eksen yukarı kaydırılır" diye aktarıyordu; ikisine ve aynı ifadeyi
taşıyan eksen uzatma raporuna tarihli ek düşüldü.

**Kabul edilen bedel.** `01-problem-definition.tr.md`'nin kabul edilmeyen bedel
saydığı iki şey — pahalı donanım, dışa bağımlılık — bu hücrede kabul edildi. Ek
bunu adıyla yazıyor.

### K-168 — (b) yolunun fiyatı bir nokta değil, bir aralık

**Karar.** `K-149`'un 500'ü bir dağılımın medyanı olarak yeniden yazılıyor.
`measure_sample_size.py` artık yedi tekrarın her birinin cevabını, tohumuyla,
eserde tutuyor (`results/sample-size.json`, `tasks_needed_by_replicate`).
Alıntılar noktayı değil aralığı veriyor: ön kayıt A.7'nin tetiği, alternatifler
defterinin (b) satırı, `K-149`, `K-147` ve `S-68` tarihli eklerle.

**Gerekçe, ölçülmüş.** 28 Ağustos'un listesi ve kaydıyla, yalnız bootstrap
tohumunu bir kaydırmak manşeti %20/%30/%50 için 500/500/500'den
623/ulaşılamaz/400'e taşıdı. Manşet yedi tekrarın medyanından çıkan tek bir
çekiliş; onu tek sayı olarak alıntılamak çekilişi ölçüm gibi sunmaktı.

**Dağılım.** Birleşik kayıt, 104 görevlik tabaka, havuz 557, sınır etkinin yarısı.
Her tekrarın cevabı: o tekrarda kapının okuduğu yarının aralığının, o boydan
itibaren her boyda etkinin yarısının altında kaldığı en küçük boy.

| Beklenen etki | Yedi tekrar, tohum `20260819`–`20260825` sırasıyla | Aralık | Ulaşılamaz |
|---|---|---|---|
| %10 | —, —, —, —, —, —, — | — | 7/7 |
| %20 | 500, 557, 500, 500, 557, 500, 400 | 400–557 | 0/7 |
| %30 | 500, —, 500, —, 500, 500, 557 | 500–557 | 2/7: `20260820`, `20260822` |
| %50 | 400, 400, 500, —, 500, 500, 500 | 400–500 | 1/7: `20260822` |

Medyanın cevabı her etkide yine 500 (%10'da ulaşılamaz).

**Ayakta kalan sonuç, ve yeni gerekçesi.** Ezberleme kapısı bu katmanda — 104
eylem görevinde — okunamaz. Bu artık bir medyanın hükmü değil: yirmi sekiz
tekrar-etki hücresinin **hiçbirinde** kapı 104 görevde okunur olmuyor, ve
dağılımın alt ucu 400.

**Fiyat aralık olarak.** Beklenen etki %20 ve üstüyse 400–557 eylem görevi; üst
uç havuzun tamamı: `test_normal` 104, `test_challenge` 408, `dev` 45. Görev başına
15 epizotla (5 koşul × 3 tohum) 6000–8355 epizot; `K-149`'un epizot başına 0,02994
oturum-saatiyle yaklaşık 180–250 oturum-saati. Ve %30'da yedi tekrarın ikisinde,
%50'de birinde havuzun tamamı da yetmiyor.

**Ateşlediği gösterildi.** `first_size_under`'ın testi (`tests/test_sample_size.py`)
kural "bir kez altına indiği ilk boy"a gevşetilince düştü. Eserin her tekrarı
taşıdığını ve aralığın tekrarlardan hesaplandığını ikinci bir test denetliyor.

**Sınırı.** Yedi tekrar dağılımın kendisini de kaba ölçüyor. `S-66` hâlâ altında:
gürültü katsayısı iki hücreden geldiği için her genişlik bir alt sınır, yani aralık
da iyimser tarafta.

### K-167 — Aşağı akış birleşik kayıtla yeniden üretildi; örneklem ölçümü sayı kopyalamıyor

**Karar.** Dokunulan listeyi okuyan dört betiğin ve ardılının beş çıktısı
birleşik seri 3 ve yeni listeyle yeniden üretildi. `measure_sample_size.py`'deki
üç kopya sayı artık türetiliyor: geçiş oranı `results/pass-threshold.json`'dan,
mevcut örneklem havuzun `test_normal` payından, en büyük boy havuzun kendisinden.
`derive_pass_threshold.py`'nin varsayılanı 9 oldu (`S-75`).

**Gerekçe.** Üç sayı başka ölçümlerin kopyasıydı: `PASS_RATE = 0.280`,
`current_sample: 105` ve 623'te biten boy ızgarası. Liste dört görev büyüyünce
havuz 622'ye düştü ve betik koşmayı reddetti. Reddetmesi iyiydi; ama sayılar öbür
yöne kaysaydı bayat girdilerle sessizce koşacaktı.

**Sonuç.**

| Eser | 28 Ağustos | 25 Eylül |
|---|---|---|
| `results/task-types.json` | 123 görev: eylem 105, cevap 18 | 119 görev: eylem **104**, cevap **15** |
| `results/interval-width.json` | 123 görev, 42 geçen epizot | **119** görev, **92** geçen epizot; medyan maliyet 12 → 12 |
| `results/pass-threshold.json` | birincil 105; eşik —/0,85/0,75/0,75 | birincil **104**; eşik **aynı** |
| `results/stratum-rates.json` | eşik [0,75, 0,85] | **değişmedi** |
| `results/sample-size.json` | havuz 623; gereken —/500/500/500 | havuz **557**; gereken **aynı** |

**Geçen epizotların bileşimi değişti.** 42'nin hepsi `test_normal`'daydı:
DeepSeek 22, 14B 3, OpenRouter'daki 32B 6, 32B 11. 92'nin 50'si ilan edilen
32B'nin `train` epizotları (`bir1`). Maliyet yeniden örneklemesi bundan sonra
çoğunlukla değerlendirilecek modelin kendi çözümlerinden geliyor; medyan aynı
kaldı.

**Ateşlediği gösterildi.** Dört yeni test (`tests/test_sample_size.py`) eski
betiğe karşı dördü de düştü, yenisinde geçiyor. Eski betik yeni listeyle koşmayı
reddetmişti; yenisi havuzu okuyup koştu.

**Sınırı.** (b) yolunun 500'ü hâlâ yedi tekrarın **medyanından** çıkan tek bir
sayı ve 400 ile 500 arasındaki pay dar: 400'de oranlar 0,566/0,541/0,513, 500'de
0,483/0,474/0,467. Tekrar başına dağılımı ayrı bir kararda.

### K-166 — Dokunulan görev listesi kayıttan üretiliyor ve okunduğu yerde denetleniyor

**Karar.** `results/touched-tasks.json` artık elle yazılmıyor:
`scripts/setup/build_touched_tasks.py` onu kayıttan üretiyor. Dört ölçüm betiği
listeyi yalnız `zihin.touched.load_touched` üzerinden okuyabiliyor. Nöbetçi üç
katmanlı:

| Katman | Nerede | Ne soruyor |
|---|---|---|
| Kullanım anı | `load_touched`, dört okuyucunun her çağrısında | Kayıt tamsa: türet, farklıysa reddet. Kaydın bir kısmı varsa: o kısmın dokunduğu her görev listede mi. Her durumda: `test_challenge`'da tek epizot bile varsa reddet |
| Yerel | `scripts/local_checks.sh` | `build_touched_tasks.py --check`; kayıt eksikse karşılaştırmayı reddediyor, zayıf bir "tuttu" vermiyor |
| CI | `tests/test_touched_tasks.py` | Dosyanın yapısı ve kökeninin listelerle tutarlılığı; her görevin AppWorld'deki bölmesinde durması; türetme ve reddin sentetik, gerçek şemalı kayıtlarda sınanması |

**Gerekçe.** Liste bir kez elle yazılmıştı ve kayıttan dört görev geride kaldı;
dördü de değerlendirme örneklemindeydi. CI kayda erişemiyor (`*.sqlite` git'te
yok), yani "CI düşsün" isteğinin CI'da karşılanabilen kısmı yapı ve türetme
mantığı; kayıtla karşılaştırma kaydın durduğu yerde, kullanım anında ve yerel
denetimde.

**Kural.** Kayıttaki her epizot sayılıyor: ön kontrol, demo, tarama, üç kollu,
karşılaştırılabilirlik — deney öncesi her koşu. Görevin bölmesi AppWorld'ün
listesinden, epizodun `split` sütunundan değil: `024c982_1`'in sekiz satırı
`train` yazıyor ve görev `test_normal`'da. Bu satırlar üretilen dosyada
`recorded_split_disagrees` altında adıyla duruyor.

**Sonuç.** `test_normal` 45 → 49 (`0a9d82a_1`, `0a9d82a_2`, `0a9d82a_3`,
`0de03ea_1`), `train` 13 → 90, `dev` 0, `test_challenge` 0. Her görevin hangi
seride, hangi koşuda, hangi koşulla ve modelle kaç epizot aldığı dosyada.

**Ateşlediği gösterildi.**

- Okuyucular ve liste taşınmadan önce: `--check` elle yazılmış listeyi reddetti,
  beş test düştü (yapı, ve dört okuyucunun dördü yükleyiciyi çağırmıyor).
- Üretilmiş listeden `0de03ea_1` silindiğinde `--check` ve `measure_task_types.py`
  aynı gerekçeyle reddetti.
- Yükleyicinin karşılaştırması etkisizleştirildiğinde üç test düştü.
- `test_challenge` reddi etkisizleştirildiğinde ilk hâliyle **hiçbir test
  düşmedi**. Sebep ölçüldü: o ret üç yerden erişiliyor — listede o bölmeden görev
  varsa yapı denetimi, tam kayıtta karşılaştırma, kısmi kayıtta içerme — yani ret
  kalkınca da reddediliyor, yalnız gerekçe değişiyor. Test gerekçeye bağlandı ve
  aynı mutasyonda düştü.

**Sınırı.** Kısmi kayıtta denetim yalnız "liste o kısmın gerisinde değil" diyebilir;
listenin fazlasını göremez. Kayıt dışındaki sonda dizinleri (`experiments/outputs`
altında `0de03ea_1`'in beş sondası) sayılmıyor; bugün kümeye görev eklemiyorlar.

### K-165 — Seri 3'ün yerel yarısı kayda geri kondu; bölünme bir sınırlama olarak yazıldı

**Karar.** `b3l`, `b7l`, `b15l` ve `b32`'nin 120 epizodu `results/zihin-3.sqlite`'a
birleştirildi; seri 3 artık tek dosyada 389 epizot. Bölünmenin kendisi `S-74`
olarak yazıldı. Birleşmenin kaydı `results/series-3-merge.json`.

**Gerekçe.** `K-139`'un kuralı çiğnenmişti ve çiğnendiği ölçüldü: 13 Eylül'den
beri depodaki kayıt dört tarama eserinin kendi `database` alanında adlandırdığı
önekleri taşımıyordu. Kullanıcının kararı: birleştir, aynı sınamayla.

**Nasıl yapıldı.** Kaynak `~/yedek/zihin-3-yerel.sqlite`. Önce onun 120 koşusu,
26 Ağustos'ta birleştirilmiş `~/gelen/zihin-3-birlesik.sqlite` içindeki
kopyalarıyla içerikçe karşılaştırıldı: 120'si de aynı. Üzerine yazılan dosya
birleşmeden önce `~/yedek/zihin-3-colab-269-before-merge.sqlite` olarak saklandı.
Sonra `scripts/merge_series.py` yeni bir dosyaya yazdı, sınadı, ve o dosya kaydın
yerine kondu.

**Ateşlediği gösterildi.** `scripts/merge_series.py` yerel yarıyı zaten taşıyan bir
dosyaya birleştirmeyi 120 çakışmayla reddetti ve hiçbir şey yazmadı.
`scripts/verify_series_merge.py` birleşmemiş dosyaya karşı altı problemle
reddetti; birleşik dosyaya karşı temiz geçti.

**Bu kararın yapmadığı.** Drive'daki kopyaya dokunmuyor — o dosya buradan
görünmüyor. Ve bölünmeyi sürekli soran bir denetim kurmuyor; ikisi de `S-74`'ün
açık kalan yarısı.

### K-164 — Biriktirme üçüncü bir dalla kapandı: duran şey aletin kendisi

**Karar.** Biriktirme koşusu kapanıyor. Eşik değişmiyor, temsil değişmiyor, elde
ne varsa o raporlanıyor. Teslim edilen kütüphane ve indeks kimlikleri §18.2'ye
girdi ve ön koşul denetimi çözdüğü kimliği onlarla karşılaştırıyor;
`LIBRARY_SERIES` kütüphanenin madenlendiği seriye taşındı. İki iş deney sonrasına
kuyruğa alındı.

**Gerekçe.** İlan edilen iki dalın ikisi de ateşlemedi ve koşu yine de durdu;
durduran şey ölçüt değil, ölçüm aracıydı. `K-104` bu durumu adlandırıyor.

---

**Kapanışın dalı: ne A, ne B.**

| Dal | Ne oldu |
|---|---|
| **A — verim** | **Hiç değerlendirilemedi.** Defter her oturumda kayboluyordu, her blok bütün becerileri yeni sayıyordu, "iki ardışık sessiz blok" bir kez bile sorulamadı (`K-162`, `S-73`) |
| **B — tavan** | **Ateşlemedi.** 199 epizot, ilan edilen tavan 270 |
| **Üçüncü** | **Alet durdu.** İlan edilen eşiklerle madencilik artık bitmiyor (`K-163`) |

Bu koşu, defter arızası yüzünden, **yalnız B ile durabilir** durumdaydı — ve B'ye
71 epizot kala alet durdu. `K-104`'ün dalı: yorum tablosu bu deseni öngörmedi,
sonuç yorumsuz raporlanıyor.

---

**Biriktirme neden durdu, ölçümüyle.**

Süzülmüş korpus 50 geçen epizot, 2018 çağrı. İlan edilen eşiklerle (boşluk 2,
destek 3, tavan 256), ilk n geçen epizotta:

| n | Çağrı | Örüntü | Etkili | Beceri | Süre |
|---|---|---|---|---|---|
| 5 | 44 | 3 | 2 | 2 | 0,0 sn |
| 15 | 426 | 17 | 9 | 4 | 0,0 sn |
| 25 | 1029 | 60 | 19 | 7 | 0,7 sn |
| 30 | 1108 | 69 | 25 | 9 | 0,6 sn |
| 35 | 1246 | 75 | 31 | **11** | 0,5 sn |
| 40 | 1442 | 105 | 43 | 11 | 0,8 sn |
| 43 | 1701 | 112 | 46 | 11 | 0,7 sn |
| 46 | 1875 | 131 | 55 | 11 | 1,1 sn |
| **47** | — | — | — | — | **240 sn'de bitmedi** |
| 50 | — | — | — | — | **25 dakikada bitmedi** |

**Uçurum 46 ile 47 arasında ve keskin:** 1,1 saniyeden dört dakikadan uzuna.
Sebebi korpustaki **219 uzunluğunda tek-çağrı koşusu** — `2a163ab_1`, 244
çağrılık epizotta `GET spotify.songs/{song_id}`'nin arka arkaya tekrarı
(`K-161`'in öğe-başına-çağrı döngüsünün büyümüş hâli). 47'nci epizot o dizinin
üçüncü destekleyicisini getiriyor; destek 3'e ulaşan 219'luk bir tekrarın kapalı
alt-örüntüleri kombinatoryal olarak patlıyor.

**Tavanı düşürmek çözmüyor, çünkü sorun derinlik değil dallanma:**

| Tavan | Örüntü | Bağladı | Süre |
|---|---|---|---|
| 12 | 2707 | evet | 11,6 sn |
| 16 | 12664 | evet | 338,9 sn |

Bağlayan bir arama eksiktir ve üretici eksik aramadan kütüphane çıkarmıyor
(`K-158`). Destek 3'te hiçbir tavan hem bitiyor hem tamam.

**`min_support` ölçüldü, uygulanmadı.** Tavan 256'da, aynı korpusta:

| `min_support` | Örüntü | En uzun | Bağladı | Süre |
|---|---|---|---|---|
| **3 (ilan edilen)** | — | — | — | **bitmedi** |
| 4 | 115 | 69 | hayır | 0,9 sn |
| 5 | 85 | 60 | hayır | 0,2 sn |
| 6 | 62 | 50 | hayır | 0,1 sn |
| 8 | 33 | 33 | hayır | 0,0 sn |
| 10 | 24 | 23 | hayır | 0,0 sn |

Bu tablo kararın **girdisi**, kararın kendisi değil. Eşik değişikliği ön kaydın
işlevini bitirdiği için ancak tarihli ek ve keşifsel etiketle olabilir.

---

**Doygunluk sorusu cevaplanmadı, ve cevaplanamaz.**

A dalının isteyeceği gözlem hiç kaydedilmedi; yukarıdaki eğri kayıttan
**yeniden kurulmuş** bir vekil, ve elli geçen epizodun kırk altısından ötesine
uzatılamıyor.

**Ne görülüyor:** beceri sayısı son üç ölçülebilir noktada **11'de sabit**,
örüntü ve etkili örüntü sayısı ise yükselmeye devam ediyor (75 → 105 → 112 →
131; 31 → 43 → 46 → 55).

**Ne söylenemez:** bunun doygunluk olduğu. Üç sebeple. Birincisi bu kesme
noktaları otuz epizotluk **blok sınırları değil**, geçen epizot sayıları — ilan
edilen gözlem bu değil. İkincisi son dört geçen epizot hiç madenlenemiyor, yani
eğrinin ucu ölçülmemiş. Üçüncüsü son eklenen epizotlar tohum 2'den geliyor ve
tohum sıfırdakilerle aynı karakterde olmayabilir.

**Rapora giren cümle: "doymadı" değil, "söyleyemedik".**

---

**Teslim edilen, ve sabitlendiği yer.**

| | |
|---|---|
| Süpürme epizodu | 199 |
| Ayrık geçen görev | **50** |
| Kütüphane | `v0-gap2-sup3-0c3f4ac`, **11 beceri**, **45 destekleyen epizot** |
| İndeks | `v0-sup1-0c3f4ac`, **29 kart** |
| Madenlendiği commit | `0c3f4ac` |
| Eşikler | boşluk 2, destek 3, sabit eşiği 3 |

Kimlikler §18.2'ye girdi. Sebebi: `latest_library_and_index` kütüphaneyi **satır
sayısına göre** seçiyor, yani sonradan madenlenecek bir kütüphane bunun yerine
sessizce geçebilirdi — ve bu kütüphane deneyin girdisi. Ön koşul denetimi artık
her koşuda çözdüğü çifti ilan edilenle karşılaştırıyor ve farklıysa reddediyor.
Eser: `results/accumulation-closure.json`.

**`LIBRARY_SERIES` taşındı.** `K-143`'ün açık bıraktığı not her blok sınırında
çıkıyordu: üreticiler `ACTIVE_SERIES`'e yazıyor, işaretçi seri 2'yi gösteriyordu.
Artık `ACTIVE_SERIES` ile aynı. Ve işaretçiyi taşımak ikinci bir şeyi ortaya
çıkardı: iki kurulum ölçümü `--database` için `LIBRARY_SERIES`'e düşüyordu ama
istedikleri **kalibrasyon serisi**. Bir sabit iki iş yapıyordu; taşıma onları
sessizce yeniden yönlendirirdi. `CALIBRATION_SERIES` kendi adıyla ayrıldı.

---

**Kuyruk, deney sonrası.** İkisi de ayrı çalışma:

1. **`min_support` yükseltmesi** — yukarıdaki tablo ölçüldü, uygulanmadı.
2. **Tekrarlı çağrıların katlanması** — "tekrar bir beceri mi, döngü mü" bir
   **temsil** kararı, `K-161`'in sorduğu sorunun aynısı. Bugünkü on bir becerinin
   biri bu döngünün kendisi; katlama hem kütüphaneyi hem aramanın maliyetini
   değiştirir, yani ölçümün öznesini değiştirir ve koşu ortasında yapılamaz.

### K-163 — Duran koşu sayıldı; ilan edilen destek eşiği bu korpusta kapanmıyor (K-104)

**Karar.** Duran koşunun kaydı ölçüldü ve devam noktası doğrulandı. Sağlık
kontrolü artık kendi bölmesini kaydediyor. **Eşiklere dokunulmadı:** ölçüm ilan
edilen `min_support` 3'ün bu korpusta yararlı sürede kapanmadığını gösteriyor ve
bu `K-104`'ün dalı — sonuç yorumsuz raporlanıyor, eşik değişikliği kullanıcının,
tarihli ek ve keşifsel etiketle.

**Gerekçe.** `K-158`'in karar ağacı: bir nöbetçi bütçe ise yükseltilir; yükseltilince
yine bağlıyorsa ya da yararlı sürede bitmiyorsa, artık bütçe sorusu değildir.

---

**Kayıt ne taşıyor (10 Eylül 19:33 kopyası).**

| | |
|---|---|
| Toplam epizot | 269 (`b14` 31, `b32c` 31, `bir1` 207) |
| `bir1` süpürme epizodu (koşucunun kuralıyla) | **199** |
| Ayrık geçen görev | **50** |
| Tohum 0 / 1 / 2 | 91 / 61 / 48 epizot, 29 / 13 / 8 geçen |
| Sağlık kontrolü satırı | 7, hiçbiri geçmedi |
| Tavana kalan | 71 epizot |
| Kapanmış olması gereken blok sınırı | 6 |

**Süpürme 0 tamam:** doksan görevin doksanı yazılmış. Tohum 1 ve 2 de tükenmiş —
her ikisinde de koşulacak görev kalmamış. Koşucunun dördüncü tohumu istemesinin
sebebi buydu.

**Kullanıcının bildirdiği 188 / 46 bu kopyada 199 / 50.** Fark koşunun
bildirimden sonra da ilerlemiş olmasıyla açıklanıyor; sayılar bu kopyadan.

---

**Kütüphane doğru korpustan madenlendi mi: evet, kaydın kendi sütunlarından.**

| Kütüphane | Beceri | Destekleyen epizot | Nereden |
|---|---|---|---|
| `v0-gap2-sup3-fc83a92` | 4 | 15 | hepsi `bir1` / `train` |
| `v0-gap2-sup3-0c3f4ac` | 11 | 45 | hepsi `bir1` / `train` |

`b14` yok, `b32c` yok, `test_normal` yok. Süzgeç (`K-159`) blok boyunca
yürürlükteydi. İndeks de aynı: `v0-sup1-0c3f4ac`, 29 kart.

**Ve iki kütüphane sağ kaldı, yedi değil.** Kimlik commit taşıyor, yani bir
oturumdaki bütün madencilikler aynı kimliği alıp birbirini siliyor ama commit
değişince yeni kimlik doğuyor. `S-73`'ün "tek kütüphane" cümlesi bu kopyada iki;
blok başına geçmiş yine yok, ama iki anlık görüntü var.

---

**Ölçülen asıl şey: madencilik artık bitmiyor.**

Süzülmüş korpus 50 geçen epizot, 2018 çağrı. İlan edilen eşiklerle (boşluk 2,
destek 3) ve ilan edilen tavanla (256):

| Korpus (ilk n geçen epizot) | Çağrı | Örüntü | Süre |
|---|---|---|---|
| 30 | 1108 | 69 | 0,9 sn |
| 40 | 1442 | 105 | 1,1 sn |
| 44 | 1748 | 112 | 1,3 sn |
| 46 | 1875 | 131 | 1,9 sn |
| **47** | — | — | **240 sn'de bitmedi** |
| 48 | — | — | 240 sn'de bitmedi |
| 50 | — | — | **25 dakikada bitmedi** |

Uçurum 46 ile 47 arasında ve keskin: 1,9 saniyeden dört dakikadan uzuna.

**Sebebi de ölçüldü.** Korpustaki en uzun tek-çağrı koşusu **219** — 43'üncü
sıradaki `2a163ab_1`, 244 çağrılık epizotta `GET spotify.songs/{song_id}`'nin
arka arkaya 219 tekrarı (`K-161`'in öğe-başına-çağrı döngüsü, büyümüş hâli).
47'nci epizot o dizinin üçüncü destekleyicisini getiriyor; destek 3'e ulaşan bir
219'luk tekrarın kapalı alt-örüntüleri kombinatoryal olarak patlıyor.

**Tavanı düşürmek de çözmüyor**, çünkü sorun derinlik değil dallanma:

| Tavan | Örüntü | Bağladı | Süre |
|---|---|---|---|
| 12 | 2707 | evet | 11,6 sn |
| 16 | 12664 | evet | 338,9 sn |

Bağlayan bir arama eksik bir aramadır ve üretici ondan kütüphane çıkarmıyor
(`K-158`). Yani destek 3'te **hiçbir tavan** hem bitiyor hem tamam.

**Destek eşiği ne yapıyor** — tavan 256'da, aynı korpusta:

| `min_support` | Örüntü | En uzun | Bağladı | Süre |
|---|---|---|---|---|
| **3 (ilan edilen)** | — | — | — | **bitmedi** |
| 4 | 115 | 69 | hayır | 0,9 sn |
| 5 | 85 | 60 | hayır | 0,2 sn |
| 6 | 62 | 50 | hayır | 0,1 sn |
| 8 | 33 | 33 | hayır | 0,0 sn |
| 10 | 24 | 23 | hayır | 0,0 sn |

Bu tablo **uygulanmadı**. `K-104`: yorum tablosu bu deseni öngörmedi, sonuç
yorumsuz raporlanıyor, ve eşiği değiştirmek ön kaydın işlevini bitirdiği için
ancak kullanıcının tarihli eki ve keşifsel etiketiyle olabilir. Ölçüm kararın
girdisi, kararın kendisi değil.

---

**Bir düzeltme: sağlık kontrolü yanlış bölme yazıyordu.** `run_episode` ön
kontrole de koşunun bölmesini veriyordu, yani `024c982_1` — bir `test_normal`
görevi — sekiz satırda `split='train'` diye kaydedilmiş. Süzgeç o sütunu okuyor,
yani geçen bir sağlık kontrolü korpusa **train epizodu olarak** girerdi. Sekizi
de düştü, hiçbiri derleyiciye ulaşmadı; ama kayıt olmayan bir şeyi söylüyordu.
`PREFLIGHT_SPLIT` ilan edildi ve bir test onu `load_task_ids`'e karşı çiviliyor.
Eski satırlar duruyor: kayıt ekle-only.

### K-162 — Koşunun durumu iki depoya bölünmüştü; A dalı bir kez bile değerlendirilmedi

**Karar.** Defter kayda taşındı: `run_ledger` tablosu, blok sınırı başına bir
satır, epizotlarla **aynı dosyada** ve aynı dayanıklılıkta.
`results/accumulation-ledger.json` duruyor ama artık **türetilmiş bir
projeksiyon**. A dalı defterin kendisine sorulan bir soru
(`branch_a_fired(defter)`), madencilik adımının kuyruğunda hesaplanan bir sayı
değil. Ve tohum sayısı tek kaynaktan geliyor: türetmenin kendi sınırı.

**Gerekçe.** Colab her oturumda checkout'u yeniden klonluyor; kayıt Drive'a
sembolik bağlı, defter değildi. Koşunun durumu bir dayanıklı ve bir geçici depoya
bölünmüştü, ve durma ölçütünün okuduğu yarı geçici olandı.

---

**Ölçüldü.** `scripts/colab_bootstrap.sh` E adımı **yalnız** seriyi bağlıyor:

```
ln -sfn "$DRIVE_ROOT/results/$SERIES_NAME" "$WORKDIR/results/$SERIES_NAME"
```

`results/` altındaki başka hiçbir şey Drive'a gitmiyor, ve defter hücresi her
oturumda `git reset --hard origin/main` yapıyor — checkout "atılabilir" olarak
tasarlanmış (`K-125`'in yanındaki not). Yani `results/accumulation-ledger.json`
her oturumda yok. Kullanıcının teşhisi birebir doğru.

**Sonucu, kullanıcının bildirdiği sayılarla.** Yedi madencilik olayı, her
seferinde "0 block closed in the ledger", ve her blokta `skills 11 (+11)` — yani
**hepsi yeni sayıldı**. `new_skills` hiçbir zaman sıfır olamadı, dolayısıyla
"iki ardışık sessiz blok" **bir kez bile değerlendirilemedi**. Durma ölçütünün
yarısı hiç çalışmadı. B dalı çalıştı, çünkü o sayıyı kayıttan alıyor (`K-160`).

**İkinci arıza birincinin sonucu.** A ateşlemediği için süpürmeler ilerlemeye
devam etti ve dördüncü tohum istendi; `seed_for` reddetti:
`seed_index must be between 0 and 2, got 3`. Şema doğru durdurdu.

---

**Tohum sayısı: üç kaynak, üç farklı şey söylüyor. Karar verilmedi.**

| Kaynak | Ne diyor |
|---|---|
| §18.3 | "ikinci süpürme yalnız düşen görevleri **bir sonraki tohumla** tekrar koşuyor" — **sayı yok** |
| §18.2 tohum satırı | "tek, `seed_index` 0" |
| `config/models.yaml` | `seed_count = 3`, yani `seed_for` 0–2'yi türetiyor |
| Koşucu (önceki hâli) | `range(4)`, `seed_index >= 3` |

§18.3 kaç tohum olduğunu **söylemiyor**; §18.2 bu koşu için bir tohum ilan
ediyor; mekanizma üçe izin veriyor. Koşucu bu üçü arasında seçim yapmıyor:
**türetilemeyecek bir tohumu istemeyi bıraktı**. `SEED_COUNT` artık
`models.yaml`'dan geliyor, kimlik kümesi `range(SEED_COUNT)`, ve tükendiğinde
koşu adı konmuş bir sebeple duruyor: *"the seed derivation allows 3 seed(s)
(0 to 2) and all of them are spent"*. Hangi sayının ilan edilmiş olduğu
kullanıcının kararı ve tarihli bir ek ister.

---

**Neden hiçbir test yakalamadı: `K-117`.**

Üç başlangıçlık test defteri `tmp_path / "ledger.json"`'a koyuyordu ve o yol
testin tamamı boyunca yaşıyor — yani test **yeniden başlatmayı atlatan bir
defter** modelliyordu. Gerçek olan atlatmıyordu. Test ortamı gerçek ortamdan tam
da sınanan özellikte farklıydı, ve bu farkın bedelini koşu ödedi.

`tests/test_ledger_durability.py` bu yüzden her vakada **checkout'u siliyor**:
`results/` altındaki her şey gidiyor, kayıt kalıyor — yeni bir oturumun yaptığı
şey. Sekiz test artı üç tohum testi. Üç dosya (`run_accumulation.py`,
`schema.sql`, `records.py`) tek tek `HEAD`'e geri konunca üçünde de düşüyorlar;
üçü birden geri konunca modül zaten içe aktarılamıyor.

**Ve bir dayanıklılık ayrıntısı.** `(prefix, block)` tekil: bir yeniden başlatma
kapattığı bloğu tekrar kapatmaya kalkarsa çakışma veriyor, sessizce ikinci satır
yazmıyor — bir kez koşmuş bloğun iki gözlem sayılması `blocks_covered`'ın
(`K-156`) tersi olurdu. Tablo şemanın kendi `CREATE TABLE`'ından geliyor, yani
Drive'daki mevcut dosyaya **CHECK'leriyle birlikte** göç ediyor; gerçek dosyanın
bir kopyasında denendi: 156 epizot yerinde, beş CHECK ve UNIQUE geldi.

---

**Ne kaybedildi, ne kaybedilmedi.** Kaybedilen tek şey **A dalının gözlemi**:
blok sınırlarında kütüphanenin yeni beceri ekleyip eklemediği hiç
karşılaştırılmadı, ve o gözlemler geriye dönük kurulamaz — hangi blokta hangi
kütüphanenin çıktığı yazılmadı. Kaybedilmeyen: epizotlar, geçenler ve son
kütüphane kayıtta ve süzgeç (`K-159`) blok boyunca yürürlükteydi, yani madencilik
her seferinde doğru korpustan koştu. Katlanmış blok sınırları **hangi anda**
madenlendiğini bozar, **neyden** madenlendiğini bozmaz.

**Ek — 25 Eylül 2026: tablo koda girdi, kayda girmedi.** Yukarıdaki "Defter kayda
taşındı" cümlesi kod için doğru, kaydın kendisi için değildi. Şema değişikliği
son `bir1` epizodundan bir saat sonra geldi ve gerçek kayıt o kodla hiç yazma
kipinde açılmadı; göç yalnız eski bir kopyada gösterildi. Tablo gerçek kayda 25
Eylül'de girdi (`K-171`).

### K-161 — Elli yedi uzun örüntü bir öğe-başına-çağrı döngüsü; derinlik tavanı 256'lık bir bütçe

**Karar.** §18.2 `library_max_length` = **256** ilan ediyor ve koşucu onu
geçiyor. Değer "bağlamayan" olarak seçildi, "tamamlatan" olarak değil; nöbetçi
yerinde kalıyor ve bağlarsa yine söylüyor. Korpus-şekli bulgusu rapora giriyor.

**Gerekçe.** Taze kayıtta (15:42; 29 geçen, 1102 çağrı, alfabe 43) tavan 12'de
105 örüntü ve **57 uzayabilen örüntü**; 64'te de bağlıyor; 128, 256 ve 512
bağlamıyor ve üçü **aynı 68 örüntü, aynı 9 beceri**. Üçü de bir saniyenin
altında.

---

**Ne oldu — elli yedi uzun örüntü ne?** Tavan kalkınca 68 kapalı örüntünün
20'si on iki ve üstü, en uzunu **70**. Beşi tek sembolün tekrarı, on ikisi iki
ya da üç sembol, üçü beş-altı sembol. En sık beş:

| Uzunluk | Destek | Şekli |
|---|---|---|
| 16 | 8 görev | `GET spotify.songs/{song_id}` ×16 |
| 17 | 7 | aynı ×16, önünde `GET api_docs.api_doc` |
| 17 | 7 | aynı ×17 |
| 33 | 6 | aynı ×33 |
| 18 | 6 | aynı ×17, önünde `api_doc` |

**Giriş değil, sayfalama da değil: öğe başına bir çağrı döngüsü.** Ajan bir
çalma listesindeki şarkıları tek tek `GET spotify.songs/{song_id}` ile çekiyor;
yirmi uzun örüntünün yirmisinde bu sembol var, onunda `api_docs.api_doc`,
sekizinde `spotify.library/playlists`. Epizot başına en uzun tek-çağrı koşusu
70, 69, 69, 50, 33. Bu, madenlenen "beceri"nin ne olduğu hakkında bir cümle:
tavan 256'da çıkan dokuz beceriden biri **bu döngünün kendisi** —
`GET spotify.songs/{song_id}`'nin tekrarı — ve destek ölçütü onu bir örüntü
olarak görüyor. Yorum yapılmıyor; §18.5 koşu bitince okunur. Ama rapora, bağlama
çözülmüş olsa da: yirmi dokuz epizotta destek ≥ 3 ile on iki artı çağrılık elli
yedi dizi, ağır ve tek-sembollü bir tekrardır.

---

**Bütçe neden 256.** Bir örüntü kendisini destekleyen en kısa epizottan uzun
olamaz ve destek üç istiyor; kayıttaki en uzun epizot 159 çağrı, en uzun
tek-çağrı koşusu 70. 64 bağlıyor çünkü 70 var. 128 bağlamıyor ama en uzun
örüntünün iki katından az — korpusa göre ayar olurdu. 256 bağlamayan ilk değerin
iki katı, en uzun örüntünün üç buçuk katı ve en uzun epizodun üstünde. Sonuç
sınırdan bağımsız: 128/256/512 birebir aynı küme ve aynı kütüphane.

**Gerçek üreticiyle, koşucunun geçtiği argümanlarla, taze kopyada `--dry-run`:**
nöbetçi bağlamıyor, kütüphane çıkıyor. Blok 3 aynı yerde durmayacak.

**Neyi değiştirmiyor.** Eşikler (boşluk 2, destek 3) ve nöbetçi. Tavan bir
bütçe, ve K-158'in karar ağacı duruyor: 256 bağlarsa bu artık bütçe sorusu
değildir, `K-104`.

### K-160 — Süpürme 0 doksanın seksen dokuzu: iki sayım hatası, ve tavanın tesisatı

**Karar.** Koşunun epizot sayısı **süpürülen bölmenin görevleri** üzerinden
sayılıyor; bloklar defter satırı olarak değil **kapsanan blok** olarak sayılıyor;
ve `--max-length` yalnız §18.2 `library_max_length` ilan ettiğinde geçiliyor,
nöbetçi yerinde kalıyor.

**Gerekçe.** Çıktı `[29/30]`'da kesildi ve `[30/30]` yoktu. Kesilmedi:
sınır bir epizot erken ateşledi, çünkü sayım bir fazlaydı.

---

**Doksan mı seksen dokuz mu: seksen dokuz, artı bayat bir satır.** İndirilen
kayıtta (13:05) `bir1` altında 64 satır var: 60 süpürme epizotu, 3 `onkontrol`
ön kontrolü, ve **bir tane daha** — `bir1-024c982_1-024c982_1-32b`, `K-155`'ten
önceki ilk ön kontrol, koşunun kendi kimliğiyle yazılmış, tavanı 3, görevi
`test_normal`'dan. Sayım `run_id LIKE 'bir1-%' AND NOT LIKE 'bir1-onkontrol%'`
idi, yani o satırı **süpürme epizotu** saydı: 61.

Üçüncü başlangıçta `spent = 61`, `since_block = 1`; yirmi dokuz epizot sonra
`since_block = 30` ve sınır ateşledi. Sayılan 90, gerçek 89. Otuzuncu görev iş
listesinde duruyor; bir sonraki başlangıçta ilk koşulacak şey o.

**Düzeltme.** `library_state()` yalnız `task_id` süpürülen bölmede olan
epizotları sayıyor (`swept_tasks()`, `load_task_ids(SPLIT)`'ten bir kez). Kayıt
ekle-only; satır duruyor, sayım süpürme epizotunun ne olduğunu öğrendi.

---

**İkinci hata: bloklar satır olarak sayılıyordu.** Yakalama madenciliği tek
satır yazıp `blocks_covered: 2` diyor (`K-156`). Ama `len(ledger["blocks"])`
dört yerde blok sayısı olarak kullanılıyordu. Sonucu: yakalamadan sonraki blok
**2** diye numaralandı (3 olmalıydı), ve bir sonraki yeniden başlatma
`90 // 30 − 1 = 2` sınır borçlu sanacaktı (1 olmalı) — yani bir kez daha
yakalama madenciliği yapıp `blocks_covered: 2` yazacak, üç blok için dört
kapsayacaktı. A dalı bu sayıyı okuyor.

**Düzeltme.** `blocks_closed(defter) = Σ blocks_covered`; `boundaries_due`,
`catch_up` ve döngünün numaralaması onu kullanıyor.

---

**Tavanın tesisatı.** `max_length` bütçe, ilan edilmiş eşik değil. Koşucu §18.2
`library_max_length` ilan ediyorsa `--max-length` geçiyor, etmiyorsa derleyicinin
varsayılanı kalıyor; nöbetçi her iki durumda bağlarsa kendini söylüyor. Değer
bu kayda **girmedi**: "bağlamayan değer" ölçümle seçilecek — 64 ve 128'de aynı
kütüphane, ikisi de bağlamadan — ve ölçüm taze kaydı istiyor.

**Elli yedi uzun örüntü: buradan gösterilemedi.** İndirilen kopya 13:05'ten;
süpürme 0'ın kalanı, blok 1-2'nin madenciliği ve blok 3'ün bağlaması ondan
sonra. Kopyada 17 geçen var, 29 değil; nöbetçi onda bağlamıyor. En sık beş
örüntü ve 64/128 ölçümü taze kopyayla yapılacak; §18.2 satırı o zaman girer.

**Testler.** Bölme dışı görevin koşu kimliğiyle yazılmış satırı sayılmıyor;
`blocks_closed` iki blok kapsayan tek satırda 2, `boundaries_due(…, 90)` 1;
döngü iki çağrı yerinde de kapsamadan numaralıyor; tavan yalnız ilan edilince
geçiliyor. Koşucu `HEAD`'e geri konunca beşi de düşüyor. Sentetik korpuslu
testler artık kendi görev kümelerini ilan ediyor.

### K-159 — Korpus kuralı: model etiketi VE bölme; nöbetçiyi bağlayan dizi sızıntıydı

**Karar.** İki üretici de korpusu **model etiketi ve bölme** ile okuyor:
`passing_sequences(connection, *, model_tag, split)` ve
`observed_episodes(connection, *, model_tag, split)`, ikisi de zorunlu, ikisi
de `--model-tag`/`--split` olarak komut satırında zorunlu, ve koşucu kendi
`MODEL` ve `SPLIT`'ini geçiyor. Kural önek değil: ikinci bir `train` koşusu
girer, aynı modelin `test_normal`'daki kardeşi dışarıda kalır. §18.1'e tarihli
ek olarak yazıldı ve **düzeltme** olarak: ilan edilenle uyuşmayan bir korpustan
ilan edilene dönüş.

**Gerekçe.** İlan "modelin kendi epizotları" diyordu; madenci dosyadaki her
geçen epizodu okuyordu. Ve `b32c` aynı model olsa da `test_normal`'da koştu —
değerlendirme bölmesinde — yani onun geçenlerinden madenlenen beceri
değerlendirme görevinin çağrı dizisini kodlar. Sızıntı.

---

**Kayıt indirildi ve ölçüldü; epizot harcanmadı.** `mind/downloads/zihin-3.sqlite`,
3 Eylül 13:05.

| Önek | Epizot | Geçen | Bölme | Model |
|---|---|---|---|---|
| `b14` | 31 | 3 | `test_normal` | 14B |
| `b32c` | 31 | 11 | `test_normal` | 32B |
| `bir1` | 64 | **17** | `train` | 32B |

**Colab'ın madencisinin gördüğü küme:** 31 geçen epizot, 29 görev, 894 çağrı,
alfabe 47. Nöbetçinin cümlesi:

```
guard max_length bound: 2 frequent pattern(s) of length 12 still had frequent
extensions and the limit is 12.
```

**Bağlayan dizi ne?** Tahmin "giriş iskeleti"ydi; değildi. Tavan 48'e çıkarılınca
**yine bağlıyor** — 48 uzunluğunda bir örüntü hâlâ uzuyor — ve o örüntü
`GET spotify.songs/{song_id}`'nin arka arkaya tekrarı: bir şarkı döngüsü.
Destek 3 görev: `09b0ee6_1` ve `09b0ee6_3` (`b32c`, `test_normal`) ve bir `bir1`
görevi. Yani nöbetçiyi bağlayan üç epizottan **ikisi değerlendirme
bölmesinden**. Sızıntı bir varsayım değil, ölçülen örüntünün kendisi.

**Süzülmüş korpus:** 17 geçen epizot, 17 görev, 490 çağrı, alfabe 35, en uzun
epizot 159 çağrı, epizot başına 9,9 adım. Boşluk 2 / destek 3'te **18 kapalı
örüntü → 9 etkili → 4 beceri**, nöbetçi bağlamıyor. Tavan 12, 24 ve 48'de
**aynı 18 örüntü**, en uzunu 11: arama tamamlanmış ve sonuç sınırdan bağımsız.
Üçüncü adım gerekmedi. On iki çağrılık diziler başka koşulardan geliyormuş.

| | Kalibrasyon (DeepSeek, `test_normal`) | `bir1`, süzülmüş |
|---|---|---|
| Geçen epizot / görev | 22 / 20 | 17 / 17 |
| Çağrı | 854 | 490 |
| Kapalı örüntü | 105 | 18 |
| Beceri | 4 | 4 |
| Örüntü : beceri | 26 : 1 | 4,5 : 1 |

Dört becerinin etki sonekleri: `POST spotify.auth/token`,
`POST file_system.auth/token`, `POST spotify.following_artists/{artist_id}`, ve
ilk ile üçüncünün birleşimi. Yorum yok; §18.5'in dalları koşu bitince okunur.

---

**Kalibrasyon korpusunun kuralı da yazıldı.** Eşikler `zihin-2`'deki `sinir3`
üzerinde seçilmişti: DeepSeek V4 Flash, `test_normal`, `baseline`, 20 geçen
(+2 `sinir2`). Kurulum ölçümleri (`mine_skills`, `compare_naive_miner`,
`measure_accumulation`) artık bu kuralı açıkça geçiyor
(`CALIBRATION_MODEL_TAG`, `CALIBRATION_SPLIT`); "dosyadaki her şey" okuması
yalnız hata altyapısı ölçümleri için, **kendi adıyla** (`every_observed_episode`)
duruyor ve üreticiler onu çağıramıyor — test bunu AST'den okuyor.

**Testler.** `tests/test_corpus_rule.py`: dosyaya `b14`, `b32c`, `bir1` konuyor,
süzgeç yalnız `bir1`'i döndürüyor; `bir1`'in `test_normal`'daki kardeşi
eklenince dışarıda kalıyor; ikinci bir `train` koşusu giriyor; hata indeksi
aynı kuralı geçenlere ve düşenlere uyguluyor; kural boş bırakılamıyor; koşucu
iki üreticiye `MODEL` ve `SPLIT`'i geçiyor. Üç dosya tek tek `HEAD`'e geri
konunca üçünde de testler düşüyor. Zorunlu argüman süpürmesi (`K-156`) yeni
bayrakları kendiliğinden istedi.

### K-158 — Madencinin nöbetçisi kendini adlandırıyor; okuduğu korpus ilan edilen değil

**Karar.** `mine_patterns` bir nöbetçi bağladığında sonuç **hangisinin**
bağladığını, gördüğü değeri, sınırını ve aramanın neresinde olduğunu taşıyor;
`build_skill_library.py`'nin reddi bu cümleyi ve madenlenen korpusun şeklini
(epizot, görev, çağrı, alfabe, en uzun epizot, **öneklere göre dağılım**)
yazıyor. İki nöbetçi komut satırından yükseltilebiliyor (`--max-length`,
`--max-patterns`); varsayılan yok, sayı derleyicide tek yerde. Eşikler
değiştirilmedi.

**Gerekçe.** "The search hit a guard and the result is incomplete" cümlesi bir
turu Colab'a geri gönderdi ve düğüm bütçesi ile derinlik tavanı arasında, ya da
kıl payı ile patlama arasında seçim yapacak hiçbir bilgi taşımıyordu (`K-125`).

---

**Ne bağladı: buradan ölçülemiyor, ve sebebi yazılı.** Altmış epizot Drive'da;
`colab-sonuclari`'ndaki son itme 25 Ağustos'un `b14`'ü. Depo içinden bir denetim
deponun dışındaki kopyaya ulaşamıyor (`S-69`). Değeri getirecek şey artık aracın
kendi cümlesi: Colab'da tek satır, epizot harcamadan —

```
uv run python scripts/setup/build_skill_library.py --max-gap 2 --min-support 3
```

**Ulaşılabilen ölçüldü, ve bir şey çıktı.** `passing_sequences` dosyadaki
**her** geçen epizodu okuyor: önek, koşul, model süzgeci yok. Colab'daki
`zihin-3.sqlite` `bir1`'in altmışından önce altı önekten 182 epizot taşıyor.
Yani nöbetçinin bağladığı korpus "altmış epizot" değil, altmış artı dosyadaki
geri kalanı. Buradaki kopya o geri kalanı taşıyor:

| | Kalibrasyon (`zihin-2`) | Colab dosyası, `bir1` hariç (`zihin-3`) |
|---|---|---|
| Geçen epizot | 22 | 20 |
| Ayrık görev | 20 | 13 |
| Eylem | 854 | 540 |
| Epizot başına adım (ort.) | 17,4 | 9,2 |
| En uzun epizot (çağrı) | 255 | 95 |
| Alfabe | 46 | 32 |
| Önekler | `sinir2` 2, `sinir3` 20 | `b14` 3, `b32` 6, `b32c` 11 |
| Boşluk 2 / destek 3, varsayılan nöbetçiler | 100 örüntü, bağlamadı | 11 örüntü, bağlamadı |
| Nöbetçiler yükseltilince (24 / 2 000 000) | — | aynı 11, `+0 / −0` |

Kalibrasyon korpusu içinde 255 çağrılık bir epizotla bile bağlamamıştı;
ulaşılabilen altyapı da bağlamıyor ve sınırdan bağımsız. **Bağlamayı getiren şey
`bir1`'in kendi altmışı** — 32B'nin `train` üzerinde geçen epizotları — artı bu
yirmi. Şekli Colab'daki cümle söyleyecek.

**Ve dosyanın geri kalanı ilan edilen korpus değil.** §18.1 korpusu
"değerlendirilecek modelin kendi epizotları" diye ilan ediyor. Madenci `b14`'ün
(14B) ve `b32`'nin (OpenRouter, kuantalaması bilinmeyen, `S-58`) geçen
epizotlarını da okuyor. `b32c` aynı model etiketi; `b14` ve `b32` değil. Bu
`S-72`'de, kapanışı bir süzgeç ve süzgecin ölçütü — önek mi, model etiketi mi —
kullanıcının kararı, çünkü ilan "model" diyor, "koşu" demiyor.

---

**Karar ağacı, cümle geldikten sonra.** İki nöbetçi var ve ikisi de bütçe,
kural değil:

- **`max_patterns` bağladıysa** — düğüm bütçesi. `--max-patterns` on katına
  yükseltilir; arama **bağlamadan bitiyorsa** tamamlanmıştır, ve sonucun sınırdan
  bağımsız olduğu iki farklı sınırla aynı örüntü kümesinin çıkmasıyla gösterilir
  (buradaki ölçümde `+0 / −0`). **Yükseltilince yine bağlıyorsa** ya da yararlı
  sürede bitmiyorsa, bu artık bütçe sorusu değil: ilan edilen eşikler bu korpusta
  kapanmıyor demektir. `K-104`: yorum tablosu bunu öngörmedi, sonuç yorumsuz
  raporlanır, eşik ancak tarihli ek ve keşifsel etiketle değişir.
- **`max_length` bağladıysa** — derinlik tavanı. Aynı işlem: `--max-length`
  yükseltilir, bitiyorsa tamam. Ama bağlaması kendi başına bir bilgi: üç ayrı
  görev en az on iki çağrılık bir diziyi boşluk ≤ 2 ile paylaşıyor. Bu korpusun
  şekli hakkında bir cümle ve rapora girer.

Rapor iki dalı da söylüyor; kullanıcının okuduğu şey nöbetçinin adı, gördüğü
sayı ve sınır.

---

**Tasarım sorusu: madencilik düşünce koşu tümüyle duruyor.** Bu bir öneri,
**uygulanmadı**.

*Öneri.* Blok sınırında `build()` düşerse koşucu durmasın: defterin satırına
`mining: deferred` ve nöbetçinin cümlesi yazılsın, epizotlar devam etsin, bir
sonraki sınırda yeniden denensin. B dalı (tavan) kayıttan sayıldığı için
çalışmaya devam eder; A dalı (verim) o blok için değerlendirilemez ve defter bunu
açıkça söyler.

*Artı.* Oturum saati boşa gitmez — her Colab oturumu bir bütçe, ve madencilik
saniyeler sürerken epizotlar saatler sürüyor. Korpus büyümeye devam eder, ve
büyümüş korpus nöbetçiyi *daha* olası bağlar, yani ertelemenin kendisi bilgi
üretir. Üç turdur her arıza koşuyu sıfırdan başlatıyor; erteleme koşunun
ilerlemesini arızadan ayırır.

*Eksi.* A dalı "iki ardışık sessiz blok" sayar; ertelenmiş bir blok ne sessiz ne
verimli, **gözlemsiz**. İki gözlemsiz blok üst üste gelirse A dalı hiç
değerlendirilemez ve koşu yalnız B ile durur — bu, ilan edilen durma ölçütünün
yarısını devre dışı bırakmak demek ve §18.3'e tarihli bir ek ister. İkincisi:
madencilik düşüyorsa sebep ilan edilen eşiklerin bu korpusta kapanmaması olabilir
(`K-104` dalı), ve o durumda daha çok epizot sorunu büyütür, çözmez —
270'e kadar koşup sonunda madenlenemeyen bir korpusla kalmak mümkün. Üçüncüsü:
`S-65`'in sınıfı — korpus büyüdü, indeks madenlenmedi — tam olarak ertelemenin
ürettiği durum; ertelenmiş blokların sayısı defterde sınırlanmalı.

*Karar vermek için gereken şey* nöbetçinin cümlesi. Bütçe bağladıysa erteleme
gereksiz — bir yükseltme yeter. Eşikler kapanmıyorsa erteleme yanlış cevap. Yani
öneri, cümle gelene kadar bekliyor.

---

**Testler.** `tests/test_mining_guards.py` iki nöbetçiyi de sentetik bir
korpusta bağlatıyor ve raporun adı, görülen değeri, sınırı ve yükseltilecek
bayrağı taşımasını istiyor; yükseltilince aramanın bittiğini; ve
`build_skill_library.py`'nin reddinin cümleyi ve korpus satırını taşıdığını.
`compiler.py` `HEAD`'e geri konunca altı testin beşi düşüyor; altıncısı
üreticinin bayrakları geçirdiğini çiviliyor.

### K-157 — Koşucunun her yazması listelendi; ön kontrol bir sağlık kontrolü

**Karar.** Koşucunun yaptığı her yazma çıkarıldı ve her biri için "yeniden
başlatınca ne oluyor" ölçüldü. Çakışan tek yazma — epizot satırı —
devam-farkında yapıldı, ve **ön kontrol bir sağlık kontrolü olarak karara
bağlandı**: her başlangıçta koşuyor ve her başlangıçta kayıttan numaralanan yeni
bir kimlik alıyor.

**Gerekçe.** Üç yeniden başlatma üç ayrı devam arızası verdi ve üçü de ancak
koşarak bulundu; hiçbir test koşucuyu iki kez başlatmamıştı.

---

**Yazma listesi, ölçülerek.** Her satır gerçek bir kayda iki kez uygulandı ve
ikinci denemenin davranışı yazıldı.

| Yazma | Kimliği | Yeniden başlatınca | Koşucu tekrar deniyor mu |
|---|---|---|---|
| `run_manifests` | `run_id` (PK) | karşılaştırılıp devam ediliyor | evet, ön kontrolde |
| `episodes` | UNIQUE (run_id, task_id, condition, seed) | **çakışıyordu** | evet, ön kontrolde |
| `steps` | UNIQUE (episode_id, step_index) | tek başına çakışır | **hayır** — `episode_id` her seferinde yeni |
| `actions` | UNIQUE (step_id, action_index) | tek başına çakışır | **hayır** — `step_id` her seferinde yeni |
| `observations` | `step_id` UNIQUE | tek başına çakışır | **hayır** |
| `shield_violations` | UNIQUE (step_id, violation_index) | tek başına çakışır | **hayır** |
| `verifier_results` | `episode_id` UNIQUE | tek başına çakışır | **hayır** |
| `skills` | UNIQUE (library_id, effect_suffix) | `replace_library` sildiği için devam ediliyor | evet, her blokta |
| `failure_patterns` | UNIQUE (index_id, app, api, …) | `replace_index` sildiği için devam ediliyor | evet, her blokta |
| `results/accumulation-ledger.json` | dosyanın tamamı | yüklenip yeniden yazılıyor, ekleniyor | evet |
| AppWorld çıktı ağacı | `experiments/outputs/{deney}/tasks/{görev}` | `rmtree` + `makedirs`, üzerine yazılıyor | evet |
| `results/sandbox-tepe.json` | dosyanın tamamı | üzerine yazılıyor | hayır — `--sandbox` bu koşuda kapalı |

**Çocuk satırların hepsi tek başına çakışır ama koşucu hiçbirini tekrar
denemiyor**, çünkü `episode_id` ve `step_id` her yazmada yeni bir
autoincrement. Epizot satırı çakıştığında işlem geri alınıyor ve altındakiler
hiç denenmiyor. Yani listede **gerçekten** çakışan tek yazma epizottu.

**Ve tamamlanmamış bir epizot mümkün değil.** Künye, epizot, adımlar ve hüküm tek
bir `with connection:` bloğunda yazılıyor; SQLite hepsini ya yazıyor ya hiçbirini.
`written()` bu yüzden yarım yazılmış bir epizot görüp tekrar denemiyor.

---

**Epizot yazımı da künyenin öğrendiğini öğrendi.** `insert_episode` artık aynı
kimliği bulduğunda `EPISODE_CONDITION_FIELDS`'i karşılaştırıyor: aynıysa
`AlreadyRecorded` **fırlatıyor**, farklıysa farkı adlandırıp reddediyor.

**Neden bayrak değil istisna.** Çağıran, yazmanın olmadığını **bilmek zorunda**:
adımlar ve hüküm `episode_id`'ye bağlı ve o epizodun satırları zaten orada. Bir
bayrak göz ardı edilebilir, bir istisna edilemez. `record_run.py` onu yakalayıp
sıfırla çıkıyor — zaten kayıtlı bir epizot bir arıza değil.

---

**Ön kontrol: ölçüm mü, sağlık kontrolü mü? Sağlık kontrolü.**

Kanıtı üç tane ve üçü de kodda: tavanı **üç** — görevi çözemez ve çözmesi
beklenmiyor; görevi `test_normal`'dan, koşu `train` süpürüyor, yani örneklemin
dışında; ve koşunun epizot sayımlarından çıkarılıyor (`K-156`).

**Sorulan iki seçenekten ikincisi seçildi: her başlangıçta yeni kimlik.**
Birincisi — yazma yolunu sınayıp kayıtta iz bırakmamak — reddedildi, çünkü
epizotlar ekle-only ve yalnız türetilmiş projeksiyonlar silinebilir
(`03-architecture.tr.md`). Kendi kanıtını silen bir sağlık kontrolü, kanıtladığı
tek şeyi kayıtsız bırakırdı. Üç kez koştuğunu söyleyen bir kayıt doğruyu
söylüyor: üç başlangıç oldu.

**Numara kayıttan geliyor, saatten değil.** Aynı Colab makinesindeki iki
başlangıç aynı `boot_id`'yi paylaşıyor ve duvar saati kaydın söz dağarcığında
yok; "kaçı zaten orada" ise kaydın cevapladığı bir soru.

---

**Ve üç başlangıçlık test.** `tests/test_restart.py` koşucuyu üç kez üst üste
başlatıyor: birincisi yirmi epizot yazıp ölüyor, ikincisi devam edip blok
sınırında düşüyor, üçüncüsü tamamlıyor. Üçünde de hiçbir yazma çakışmıyor,
epizot sayısı ayrık kimlik sayısına eşit, ve ön kontrol üç ayrı satır bırakıyor.

**Neyin yerine ne konduğu yazılı.** Model sunucusu taklit ediliyor; **yazmalar
taklit edilmiyor** — `record_run.py`'nin yaptığı yazmaların aynısı, gerçek
`zihin.records` yardımcılarıyla, tek işlemde. Blok sınırındaki üreticiler gerçek
betikler, alt süreç olarak. Tek enjekte edilen arıza `build`'in kendi
`SystemExit`'i, yani ikinci başlangıcın gerçek çöküşü.

**Bir yan sonuç, ve doğrusu.** Taklit korpus hiçbir API çağrısı yazmadığı için
madenci hiçbir blokta beceri bulmuyor ve **A dalı iki sessiz bloktan sonra
ateşliyor**. Koşu altmışta duruyor — ilan edildiği yerde. Bu testin bir artefaktı
değil, durma kuralının çalıştığının kanıtı.

Üç mutasyonun üçü de yakalanıyor: epizot yazımını düz eklemeye döndürmek, ön
kontrolün kimliğini sabitlemek, ve `record_run.py`'nin ele almasını kaldırmak.

### K-156 — Blok sınırı: eşikler ilan edilmemişti, sınır oturumdan sayılıyordu

**Karar.** Madencilik eşikleri koşunun ilan edilmiş şartlarından okunuyor, blok
sınırları **kayıttan** sayılıyor, ve blok sınırı yolunun kendisi gerçek
üreticilerle sınanıyor.

**Gerekçe.** `--dry-run` epizot harcamadığı için blok sınırına hiç ulaşmıyor;
madencilik çağrısı ilk kez Colab'da, altmış epizot yazıldıktan sonra koştu.

---

**Ne oldu.** Koşucu `build_skill_library.py`'yi argümansız çağırıyordu:

```
build("build_skill_library.py")
build("build_failure_index.py")
```

Birincisi `--max-gap` ve `--min-support` olmadan, ikincisi `--min-support`
olmadan başlamıyor (`required=True`). argparse çıkış kodu 2 verdi, `build()`
`sys.exit` etti, koşu durdu. Altmış epizot yazılıydı ve güvendeydi.

**Sayılar zaten vardı, okunacak yerde değildi.** `K-50` madencilik eşikleri için
"kural ön kayda, sayılar kurulum sonrasına" diyor, ve kurulum onları çoktan
doldurmuştu: kayıttaki kütüphane `v0-gap2-sup3-142662f`, indeks `v0-sup1-4bb340a`,
ve `results/accumulation.json` üçünü de taşıyor. Yani sayılar **kimliklerin
içinde** yazılıydı. §18.2'ye üç satır girdi — `library_max_gap`,
`library_min_support`, `index_min_support` — ve koşucu onları `declared_field`
ile okuyor. Kendi içine yazmak ikinci kopya olurdu; test bir sabiti reddediyor.

**Veritabanı da geçiliyor artık.** Her iki üretici `--database` için kendi
başına `ACTIVE_SERIES`'e düşüyordu, yani ebeveyn ve çocuk hangi dosyayı
açacaklarına **ayrı ayrı** karar veriyordu. Bugün aynı cevabı veren iki karar
yine iki karardır (`K-138`).

---

**İkinci arıza, ölçülerek bulundu: devam blok sınırında da kurulmamıştı.**

Yeniden başlatınca `spent` defterden geliyordu:

```python
spent = ledger["blocks"][-1]["episodes_run_total"] if ledger["blocks"] else 0
```

Defter ancak bir blok kapanınca ilerliyor. Blok 1 kapanamadığı için defter boştu,
yani `spent = 0` ve `since_block = 0`. Sonucu iki katlı:

| | Olması gereken | Olan |
|---|---|---|
| Blok 1'in madenciliği | hemen, 60 epizot yazılıyken | 30 epizot daha koştuktan sonra, 90'da |
| Tavana kalan | 270 − 60 = 210 | 270, yani altmış epizot fazla |

Yani madencilik **atlanmıyordu, erteleniyordu**, ve A dalının ilk gözlemi otuz
epizotluk değil doksan epizotluk bir korpustan gelecekti. Tavan da altmış epizot
kayıyordu.

**Düzeltme sayıyı kayda taşıdı.** `spent` artık `library_state()`'ten geliyor —
veritabanındaki koşu epizotları — ve kaç sınırın madenlenmeden geçtiği
`boundaries_due(defter, spent)` ile soruluyor: `spent // BLOCK` eksi defterdeki
satır sayısı. Altmış epizot ve boş defterle cevap **iki**.

**İki sınır bir gözlem sayılıyor.** İki kez üst üste madenlemek aynı korpustan
aynı kütüphaneyi çıkarır ve ikincisi "sıfır yeni beceri" olurdu — A dalı için
kimsenin koşmadığı bir bloğun gözlemi. Yakalama madenciliği tek satır yazıyor ve
`blocks_covered` kaç sınırı temsil ettiğini söylüyor. Muhafazakâr yön: durmayı
zorlaştırıyor, kolaylaştırmıyor.

**Altmışın kendisi bu arızanın izi.** Sınır otuzda; koşu otuzda düşmüş, yeniden
başlatılmış, defter boş olduğu için sıfırdan saymaya başlamış ve otuz epizot daha
koşup **yine blok 1'de** düşmüş. Kullanıcının bildirdiği sayı bunun dışında bir
şeyle açıklanmıyor. Colab'ın defteri elde olmadığı için bu bir çıkarım, ölçüm
değil.

---

**Ve genel soru: koşucunun çağırdığı başka betik var mı?**

Üç tane, ve artık bunu hatırlamak gerekmiyor — `tests/test_block_boundary.py`
koşucunun AST'sinden her çağrı yerini çıkarıyor, her betiğin **kendi
ayrıştırıcısını** kurup zorunlu argümanlarını soruyor, ve geçilenlerle
karşılaştırıyor:

| Betik | İstediği | Geçilen |
|---|---|---|
| `scripts/record_run.py` | — | `--allow-dirty-tree`, `--health-check` |
| `build_skill_library.py` | `--max-gap`, `--min-support` | ikisi de, artı `--database` |
| `build_failure_index.py` | `--min-support` | evet, artı `--database` |

Listede olmayan bir çağrı yeri belirirse taban düşüyor: bulunan küme ile
bilinen küme birebir karşılaştırılıyor.

**Ve blok sınırı artık gerçek betiklerle koşuyor.** Test geçici bir kayda otuz
epizot yazıyor, `close_block`'u çağırıyor, ve iki üretici **alt süreç olarak**
koşuyor — taklit değil. Taklit edilmiş bir betik argümanlarını reddetmezdi, yani
tam da bu arızayı kaçırırdı. Ölçülen çıktı: `v0-gap2-sup3-c7a652f` ve
`v0-sup1-c7a652f`, ikisi de çıkış 0.

Dört mutasyonun dördü de yakalanıyor: eşikleri geri çekmek, sabit yazmak, sayıyı
deftere geri döndürmek, ve yakalamayı sınır başına bir satır yazacak hâle
getirmek.

### K-155 — Devam epizot düzeyinde kurulmuştu, künye düzeyinde değil

**Karar.** Künye yazımı devam-farkında: aynı `run_id` ile ikinci kez çağrıldığında
yazılı künyenin koşullarını **epizot tarafının kullandığı karşılaştırmayla**
(`resume_check`) karşılaştırıyor. Aynıysa yazmıyor ve devam ediyor; farklıysa
neyin farklı olduğunu satır satır söyleyip duruyor.

**Gerekçe.** İki şeyin uyuşması gerekiyordu ve yalnız biri devam-farkında
yapılmıştı; unutulanı, Colab'ın oturumu geri aldığı ilk anda koşuyu tamamen
durdurdu.

**Bağlam.** Biriktirme koşusu Colab timeout'undan sonra yeniden başlatıldı ve
ön kontrol düştü:

```
sqlite3.IntegrityError: UNIQUE constraint failed: run_manifests.run_id
```

**Hangi yolun ateşlediği ölçüldü, ve tahminim yanlıştı.** İlk açıklamam
"oturum künye ile epizot arasında geri alındı" idi. O yol gerçek ve düzeltmenin
kapsamında, ama **gözlenen** yol daha basit: `main()` her başlangıçta
`preflight()` çağırıyor, hiçbir koşula bağlı değil, ve o ön kontrol epizodu
**koşunun kendi kimliğiyle** yazıyordu. Yani epizot ilk denemede eksiksiz
tamamlanmış olsa bile ikinci başlangıç aynı `run_id` ile künye yazmaya çalışıyor.
Kullanıcının gördüğü satır zaten bunu söylüyordu: düşen şey ön kontroldü.

**Ve sebebi yine aynı sınıf.** `measure_band.py` ön kontrole kendi önekini
veriyor — `episode_command(task, ceiling, prefix=f"{PREFIX}-onkontrol", ...)` —
ve bu yüzden `b32c` kaydında ön kontrol ayrı bir `run_id` altında, ceiling 3'te
duruyor. `run_accumulation.py` o dosyadan yazıldı ve **o argümanı taşımadı**:
`run_episode`'un prefix parametresi bile yoktu. Yetenek bir yerde, çağıran başka
yerde.

**İki sonucu vardı, ikisi de ölçüldü.** Birincisi çakışma. İkincisi sessiz:
`LIKE '{PREFIX}-%'` ön kontrolü de sayıyordu, yani koşunun toplam epizot sayısı
her başlangıçta bir artıyordu ve **B dalı o toplamı okuyor**.

**Üçüncü bir sonuç yok, ve bunu da ölçtüm.** Ön kontrol görevi `024c982_1`
`test_normal` bölmesinde; biriktirme `train` süpürüyor ve o görev doksanın içinde
**değil**. Yani süpürmeden sessizce düşen bir görev yok. Aynı kod `train`'den bir
görevi ön kontrol seçseydi olurdu: `written()` o id'yi tamamlanmış görür ve görev
ceiling 3'lük epizoduyla kümede kalırdı.

**Her iki yol da yeniden üretildi.** `HEAD`'in koduyla künye+epizotsuz durum ve
künye+tam epizot durumu ayrı ayrı kuruldu; ikisinde de aynı `IntegrityError`
çıktı, düzeltilmiş kodda ikisi de geçiyor.

**Karşılaştırma ikinci kez yazılmadı.** Hangi alanların koşulu tanımladığını ve
bir `code_commit` farkının ne zaman uyarıdan redde yükseldiğini bilen tek yer
`resume_check`; bu bilginin ikinci bir kopyası bu deponun tekrar tekrar kaydettiği
kusurun ta kendisi. Künye yazımı yalnız **hangi id'yi soracağına** ve **cevapla ne
yapacağına** karar veriyor.

**Ön kontrol artık kendi kimliğini taşıyor.** `run_episode` bir `prefix`
parametresi aldı ve ön kontrol `f"{PREFIX}-onkontrol"` ile koşuyor —
`measure_band.py`'nin yaptığının aynısı, kopyalanarak değil aynı biçimde. Koşunun
sayıları da onu dışarıda bırakıyor: sağlık kontrolü bir epizot harcıyor ama
koşunun epizodu değil.

**Ve `require_episode=False` bir ayrıntı değil, düzeltmenin kendisi.**
`resume_check` künyeyi epizotla `JOIN`'liyordu. Arızanın çıktığı durumda epizot
**yok**, yani iç birleştirme hiçbir satır döndürmez, her alan hiçbir şeyle uyuşur
ve denetim "uyuyor" der. Boş bir karşılaştırma bir mutabakat değil. `LEFT JOIN`
seçeneği eklendi ve `DevamDenetimi` artık **kaç id karşılaştırdığını** taşıyor,
böylece "karşılaştırdım ve uydu" ile "karşılaştıracak bir şey bulamadım" birbirinden
ayrılıyor.

---

**Sorulan soru ölçüldü: "otuz epizot zaten yazılmış" sayısı `bir1`'e mi ait?**

Evet. Devam nöbetçisi önekler arası **saymıyor**, ve bunu yapısı gereği yapmıyor:
`run_accumulation` her görev ve her tohum için **tam kimliği** üretiyor
(`f"{PREFIX}{suffix}-{task}-{task}-{SHORT}"`) ve `completed_runs` o listeyi
`LIKE` ile değil `IN` ile soruyor. Bir veritabanına 31 `b32c` ve 5 `bir1` epizodu
yazılıp 360 `bir1` kimliği soruldu: dönen küme **5**, içinde `b32c` **yok**.

**Ama sınıf canlı, ve başka bir yerde.** Defterin sayıları — `episodes_this_run`
ve `distinct_tasks_passed`, yani durma kararının okuduğu sayılar — `LIKE PREFIX%`
ile alınıyordu, ayraçsız. Gerçek kayıtta ölçüldü:

| Örüntü | Satır | Yakaladığı önekler |
|---|---|---|
| `b32%` | 58 | `b32`, `b32c` |
| `b32-%` | 27 | `b32` |
| `b32c-%` | 31 | `b32c` |
| `bir1-%` | 0 | — |

`bir1`'in bugün böyle bir kardeşi yok, ama `b32`/`b32c` çifti aynı dosyada duruyor.
Örüntülere ayraç girdi ve `tests/test_resumption.py` koşucunun ürettiği her örneği
okuyup ayraçsız olanı reddediyor — SQL'in yanlış olabildiğini *göstermek* hiçbir
şeyi çivilemiyor.

---

**Testin kapsamadığı yer, arızanın çıktığı yerdi.** `tests/test_resumption.py`
epizot tarafını ayrıntısıyla sınıyordu: hangi epizotlar atlanıyor, atlamanın
kalanı değiştirip değiştirmediği, ve yazılı koşulun uyuşması. Künye tarafı için
**tek test yoktu**, ve kırılan yarı oydu. Yedi test grubu eklendi; künyesiz değil,
**epizotsuz künye** durumunu kuruyorlar, çünkü timeout'un bıraktığı durum o.
`HEAD`'in koduna karşı altısı düşüyor.

### K-154 — Defterin hücre hücre denetimi: on iki arıza, tek sınıf, ve nöbetçisi

**Karar.** Colab defteri, deponun geri kalanı gibi, ilan edilen kaynağa karşı
denetleniyor: `scripts/check_colab_notebook.py` her hücrenin adlandırdığı yolu,
attığı atfı, yazdığı değişkeni, söylediği sayıyı ve çalışma dizinini koşunun
ilan edilmiş şartlarına vuruyor, ve on iki arızanın on ikisini de yakaladığı
`tests/test_colab_notebook.py` ile kanıtlanıyor.

**Gerekçe.** Nöbetçisi olmayan eser, arızası ancak koşarak bulunan eserdir; bu
defterde her biri bir Colab oturumuna mal olan beş tur bunu ölçtü.

**Bağlam.** Son beş turda beş arıza çıktı ve beşi de aynı şekildeydi: bir yetenek
ya da değer bir yerde güncellendi, kopyasını taşıyan ya da onu çağıran
güncellenmedi. Beşi de ancak **koşarak** bulundu, yani her biri bir Colab oturumu
ve bütçeden bir pay. Sebep yapısaldı: her betiğin nöbetçisi vardı, defterin tek
testi `tests/test_colab_ref.py` idi ve o bir dal adıyla koşu komutunu çiviliyordu.
Koşudan önce on iki hücrenin tamamı tarandı.

---

**Ne çıktı: on iki arıza, hepsi aynı sınıftan.**

| # | Arıza | Nerede |
|---|---|---|
| 1 | Okuyucuya T4 seçtiriliyor; ilan edilen modelin ölçülen dosyası 19,851 GB | hücre 0 |
| 2 | Önyükleme "about 8.99 GB" diyor — 14B'nin boyutu | `colab_bootstrap.sh` |
| 3 | Şartlar §15.2'den atıf alıyor; `bir1`'inkiler §18.2 | hücre 8 |
| 4 | Devam mantığı §15.6'dan atıf alıyor; `bir1`'inki §18.6 | hücre 8 |
| 5 | İtme kuralı §15.7'den; §18'in kendi bölümü yok | hücre 10 |
| 6 | Düzyazı "Otuz epizot" diyor; ilk süpürme doksan, tavan 270 | hücre 0 |
| 7 | Nöbetçinin ret iletisi "Thirty episodes" diyor | `require_colab_environment.py` |
| 8 | README aynı iki kopyayı taşıyor | `colab/README.md` |
| 9 | `ZIHIN_SCAN` yazılıyor, o hücrenin koşturduğu hiçbir şey okumuyor | hücre 9 |
| 10 | `ZIHIN_PREFIX` okunuyor, hiçbir hücre yazmıyor | `colab_bootstrap.sh` |
| 11 | `ZIHIN_WORKDIR` geçersiz kılması hücre 4'te geçerli, dördünde değil | hücre 5, 7, 9, 11 |
| 12 | Nöbetçi nöbet tutmuyor: iki `!` satırı, ret ediyor, koşu yine başlıyor | hücre 9 |

**Bir bulgu ölçümle geri alındı.** "Hiçbir şey GPU'yu ilan edilen modelle
karşılaştırmıyor" yazmıştım. `check_prerequisites.py:gpu()` tam bunu yapıyor:
boyutu Ollama kayıt defterinden **çekimden önce** soruyor, 1,25 çarpanıyla VRAM'e
vuruyor, ve önyükleme onu E2'de — ollama'dan ve modelden önce — çağırıyor. Ben
önyüklemenin B adımında (Drive) durduğunu görüp A adımının yorumundan
genelledim. Karşılaştırma var ve doğru yerde.

---

**On ikincisi ölçülerek bulundu, ve okuyarak bulunamazdı.**

Hücre 9 iki `!` satırıydı: önce `require_colab_environment.py`, sonra
`run_accumulation.py`. Hücre 8'in düzyazısı "bu hücre başlamıyor" diyordu.
IPython 9.16'ya karşı ölçüldü:

| Biçim | Nöbetçi | Koşucu | Hücre |
|---|---|---|---|
| iki `!` satırı | ret etti, çıkış 1 | **koştu** | `success: True` |
| tek satır, `&&` | ret etti, çıkış 1 | koşmadı | `success: True` |

Başarısız bir `!` satırı sonrakini durdurmuyor ve hücre yine başarı bildiriyor.
Düzyazı bir korumayı tarif ediyordu, kod onu kurmuyordu. Düzeltme tek satır ve
`&&`; `declared.run_command` artık `&&` ile ayrılmış parçaları ayrı okuyor, yani
ilan edilen komut hâlâ tek bir parça olarak bulunuyor.

---

**Kökü olmayan bir kopya silinemez.**

1 numaralı arızanın kaynağı yoktu: §18 çalışma zamanını **hiç** adlandırmıyordu.
Yani defterin taşıdığı "T4" bir kopya değil **tek kaynaktı**, ve `b14` çağından
kalmıştı. Önce §18.2'ye dört satır girdi — `runtime`, `model_file_gb`,
`block_size`, `episode_ceiling` — sonra bir beşincisi, `first_sweep`. Şart
değişmedi; şartın ilan edilmemiş olduğu ortaya çıktı, ve tarihiyle yazıldı.

---

**Nöbetçi: `scripts/check_colab_notebook.py`.**

Yedi kural, ve her biri bulunan bir arızanın sınıfı:

1. Defterin adlandırdığı her yol izlenen bir dosya.
2. Attığı her bölüm atfı **koştuğu koşunun** bölümü — ya da gerekçesiyle
   listelenmiş, koşudan bağımsız bir kural. Varlık denetimi burada yetmiyor:
   §15.2 *var*, ve yanlış.
3. Bir hücrenin yazdığı her değişkeni, defterin koşturduğu bir şey okuyor.
4. Düzyazının söylediği her sayı tablonun ilan ettiği sayı; okuyucuya çalışma
   zamanı seçtiren satır ilan edileni adlandırıyor.
5. Kadans toplam değil: "every thirty episodes" bir oran, "Thirty episodes must
   not start" bir iddia. Sayı ikisini ayırmıyor, önündeki kelime ayırıyor.
6. Hiçbir betik varsayılansız bir `ZIHIN_*` düğmesini, onu yazan bir hücre
   olmadan okumuyor.
7. Koşu komutu nöbetçinin satırında.

**Ve tabanları var.** Hücre sayısı, yol sayısı, atıf sayısı: biri düşerse denetim
temiz rapor vermiyor, **çekiliyor**. Bu dosyanın var olma sebebi tam da bakmayı
bırakıp cevap vermeye devam eden bir nöbetçi.

**Sayılar tablodan, veriden değil.** İlk süpürmenin doksanı önce AppWorld'e
sorularak bulunuyordu ve AppWorld'ün verisi CI'da yok: aynı commit burada kabul
edip orada reddederdi. `first_sweep` ilan edildi (K-117).

---

**On iki düzeltmenin on ikisi de ateşliyor.**

`tests/test_colab_notebook.py` her arızayı tek tek geri koyuyor, denetimi
koşuyor, reddin **o arıza hakkında** olmasını istiyor, ve dosyayı geri alıyor. On
iki vakanın on ikisi de yakalanıyor. On üçüncü test tabanı sınıyor: hücreler
kesildiğinde denetim geçmiyor, çekiliyor.

Kuralları yazarken iki kez fazla geniş kaldılar ve ikisi de ölçümle daraldı: ilk
biçim bir sayının **eskiden ne olduğunu** kaydeden yorumu işaretledi, ve bir SQL
dizgesindeki `episodes` kelimesini. Bir düzeltmenin açıklamasında ateşleyen kural,
açıklamayı dosyadan kovan kuraldır.

---

**Sınıfın kendisi hakkında.** On ikisinin hepsi `main`'in ucundaki dosyaların
özelliğiydi: bayat bir atıf, okuyucusu olmayan bir değişken, ölçülmüş bir sayıyla
çelişen bir sabit, aynı dosyanın sunduğu geçersiz kılmayı yok sayan bir yol.
Hiçbiri `S-69` değil. `S-69` yalnız **teslimatı** kapsıyor: koşan kopyanın bu
dosya olup olmadığını depo içinden hiçbir denetim göremez. Bu ayrım önemli,
çünkü "zaten S-69" demek on iki düzeltilebilir arızayı düzeltilemez saymak olurdu.

### K-153 — Yetenek eklendi, çağıran öğretilmedi; ve "önek yok" artık bir cevap değil

**Karar.** Bir yeteneğin eklenmesi kullanıldığı anlamına gelmiyor, ve bunu
söyleyen şey bir test olmalı. Defterin koşu komutu artık ilan edilen bir öneği
adlandırıyor, komut arama kuralı tek bir koşucunun adına bağlı değil, ve önek
çözülemediğinde ön koşul denetimi **bilinmiyor** diyor.

**Arıza.** K-152 ön koşul denetimine `--prefix` ekledi ve gereksinimleri koşu
tipine bağladı. Defter o öneği hiç geçmedi, yani yetenek kullanılmadı ve denetim
eski geniş iletisiyle koşmaya devam etti. **Yetenek bir yerde, çağıran başka
yerde.** Aynı desenin bu turdaki beşinci örneği.

**İkinci arıza birincisini gizliyordu.** `run_command()` defterde
`measure_band.py` arıyordu. Defter başka bir koşucuya geçtiği gün arama sessizce
boş dönüyordu, yani "defterden türet" yolu da çalışmayacaktı. Kural değişti: bir
koşu komutu, **protokolün şartlar bölümü ilan ettiği bir öneği adlandıran**
kabuk satırıdır. Bu kural bayatlayamaz, çünkü önekler protokolden geliyor.

**Ve defterin koşu hücresi zaten bayattı.** `measure_band.py b32c` koşuyordu —
yani uçtan uca koşulsaydı biriktirme değil, önceki 32B bant taraması yeniden
koşacaktı. Hücre `run_accumulation.py bir1`'e çevrildi.

**"Önek verilmedi" artık geniş koşmuyor.** Eski davranış her gereksinimi
soruyordu; bu, olmayan bir gereksinimi sorup koşuyu durdurmak demekti. Yeni
davranış üç kaynağı sırayla deniyor — komut satırı, defterin koşu komutu,
koşucunun kendisi — ve hiçbiri cevap vermezse **bilinmiyor** diyor. K-131'in
deseni: belirlenemedi bir hayır değil, ve varsayılan bir cevap değil.

**Geri düşüş öneğe bağlı.** Defterin komutu yalnız **o öneği adlandırıyorsa** o
koşunun komutu sayılıyor. Başka bir koşunun komutunu okumak, tam olarak bu
çözümleyicinin engellemek için var olduğu şey olurdu.

**Çağıran teste bağlandı.** `tests/test_colab_ref.py` artık defterin koşu
komutunun ilan edilen bir öneği adlandırdığını ve komutun şartlar bölümüyle
aynı olduğunu çiviliyor. Ateşlediği kanıtlandı: defteri ilan edilmemiş bir öneğe
çevirdiğimde test düştü.

### K-152 — Temiz kurulumun çıkardığı üç arıza: özne, taban, ve eksik bir satır

**Karar.** Üç arıza da düzeltildi ve üçünün de sebebi düzeltmeden **önce**
ölçüldü: ön koşul denetimi gereksinimi koşu tipine bağlıyor, `check_language`'in
tabanı boyuttan özneye taşındı, ve `GIT_ASKPASS` süreç ortamına yazılıyor.

**Bağlam.** `main`'den temiz bir kurulum üç şey çıkardı. Üçü de ölçüldü, sonra
düzeltildi.

---

**1. Ön koşul denetimi olmayan bir gereksinimi soruyordu — özne yine yanlıştı.**

Denetim beceri kütüphanesini **koşulsuz** istiyordu. Biriktirme koşusu onu
okumuyor: `scripts/setup/run_accumulation.py` hiçbir kart bayrağı geçmiyor ve
`scripts/record_run.py` kütüphaneyi yalnız `--cards` ya da `--irrelevant-cards`
verildiğinde çözüyor. Ölçüldü, varsayılmadı.

**Ve okumamalı da.** Biriktirme korpus üretiyor. Kartlı koşsaydı üretilen korpus
sınanacak mekanizmayla kirlenirdi ve o korpustan madenlenen kütüphane
**döngüsel** olurdu: mekanizmanın ürettiği epizotlardan mekanizmayı beslemek.
Kullanıcının gördüğü döngüsellik gerçekti.

**Düzeltme gereksinimi koşu tipine bağladı, ve bağı ilan edilebilir yaptı.**
Protokol §18.2'ye `Koşul | baseline` satırı girdi; `check_declared_conditions.py`
o satırı koşucunun kaynağından çözüyor — komutun adlandırdığı koşucu kart bayrağı
geçmiyorsa koşul `record_run.py`'nin `CONDITION` varsayılanı. Ön koşul denetimi
`--prefix` alıyor ve ilan edilen koşul `baseline` ise kütüphaneyi **istemiyor**.

**Bu sınıfın dördüncü örneği.** K-138 doğru koşup yanlış model hakkında cevap
verdi; K-142 doğru soruyu yanlış kümede sordu; `S-69` doğru dosyayı doğrulayıp
başka dosya koştu; bu dördüncüsü doğru gereksinimi yanlış koşu tipine sordu.

---

**2. `check_language`'in tabanı yanlış şeyi sayıyordu.**

Aynı commit, iki cevap: yerelde sıfır, taze klonda altmış yedi. Ölçüldü:

| Korpus kaynağı | Dizge |
|---|---|
| dosya ve dizin adları | 194 |
| izlenen `results/*.json` | 1832 |
| izlenmeyen `results/*.json` (23 dosya) | 854 |
| **kayıt (`*.sqlite`)** | **12308** |

Taze klonun korpusu **2026**, tabanı 1000 — yani taban **aşılıyordu** ve denetim
eksik bir korpusla cevap veriyordu. Kaydın taşıdığı 12308 dizge yokken, yalnız o
dizgelerde bulunan altmış yedi veri anahtarı düzyazı sanıldı.

**Tabanın kendisi bir kez ateşliyordu ve artık ateşlemiyordu.** K-142 atıf alan
on iki eseri izlemeye aldı; taze klonun korpusu 254'ten 2026'ya çıktı ve tabanı
aştı. Bir boşluğu kapatmak için yapılan değişiklik başka bir nöbetçiyi
sessizce **silahsızlandırdı**.

**Düzeltme tabanı boyuttan özneye taşıdı.** Taban artık **kaydın katkısına**
bakıyor: kayıt 5000 dizgenin altında katkı yapıyorsa denetim **düşüyor**. Taze
klon artık cevap vermiyor, çekiliyor — K-117'nin istediği bu.

**Ve CI hiç sormuyordu.** `check_language.py` iş akışlarının hiçbirinde yok;
yalnız `local_checks.sh` içinde. Yani "CI yeşil, taze klon kırmızı" iki cevap
değil, **bir cevap ve bir sessizlik**. Kaydın gerektiği için bu doğru yer, ama
"CI yeşil" cümlesi bu denetim hakkında hiçbir şey söylemiyor.

**Bir yan sonuç.** İlan edilen koşul tablolarının alan adları da korpusa girdi:
`koşul` gibi bir alan, Türkçe bir belge ile kodu arasındaki arayüz, ve onu
çevirmek aramayı bozar — dosya adlarıyla aynı gerekçe.

---

**3. Jeton vardı, git onu kullanamıyordu.**

`working copy` denetimi `git fetch` yapamadığı için "bilinmiyor" dönüyordu.
Sebep ölçüldü: defter `os.environ`'a yalnız `GITHUB_TOKEN` yazıyor.
`GIT_ASKPASS` ve `GIT_TERMINAL_PROMPT` yalnız o hücrenin git çağrılarına verilen
yerel bir sözlükte duruyor, ve klonda bir `credential.helper` de kurulmuyor
(K-124 jetonu URL'den çıkarmıştı). Yani sonraki her süreç jetonu **ortamında
taşıyor ama git'in onu alacağı bir yol yok**.

**Düzeltme iki satır.** `GIT_ASKPASS` ve `GIT_TERMINAL_PROMPT` artık `os.environ`
içinde, yani her sonraki hücre ve her alt süreç devralıyor. Jeton hâlâ URL'de
değil, `argv`'de değil, git config'inde değil.

**Neden önemliydi.** Bayatlığın en olası olduğu ortam Colab, ve denetim tam
orada susuyordu.

### K-151 — Klonlanacak dal tek yerde, ve bayat bir kopya kendini söylüyor

**Karar.** Colab defterinin çektiği dal `main`. Adı **tek yerde** yaşıyor —
defterdeki `ZIHIN_REF` varsayılanı — ve README'nin aynı adı söylediğini bir test
çiviliyor. Ayrıca ön koşul denetimi çalışma kopyasının `origin/main`'in kaç
commit gerisinde olduğunu soruyor.

**Arıza kendini yanlış adlandırdı, ve düzeltilen asıl şey bu.** Defter birleşmiş
bir özellik dalını çekmeye devam etti. Temiz bir Colab kurulumunda o daldan sonra
eklenen dosyalar yoktu ve Python bir `FileNotFoundError` bastı. O hata "bu dosya
hiç yazılmadı" diye okunur; ilk okuma "ajan eksik yapmış" oldu. Oysa dosya
yazılmıştı, kopya bayattı. **Bayat bir kopyanın bayat olduğunu söylemesi
gerekiyor.**

**Dal adı neden tek kaynak olmak zorundaydı.** Ad üç yerde duruyordu: defterin
`ZIHIN_REF` varsayılanı, README'nin doğrudan bağlantısı, ve README'nin adım
listesi. Her birleşmeden sonra üçünün de elle güncellenmesi gerekiyordu, ve bir
kez unutulunca hiçbir şey itiraz etmedi. `tests/test_colab_ref.py` üçünün aynı
adı söylediğini ve o adın `main` olduğunu çiviliyor; ateşlediği kanıtlandı.

**`main`, çünkü birleşmiş iş orada.** Bir özellik dalı bir andır; `main` işin
biriktiği yer. Defterin bir özellik dalını çekmesi, o dal birleştiği anda
sessizce yanlış hâle geliyor.

**`S-64` bunu zaten adlandırmıştı.** O kayıt "dal ile `origin/main` arasında kaç
commit var, tek bir komut, ve şu an hiçbir denetim onu sormuyor" diyordu. Şimdi
soruyor: denetim `origin`'i tazeliyor, farkı sayıyor, ve geride ise **düşüyor** —
"şu kadar commit geride, o commit'lerde eklenen dosyalar burada yok ve hiç
yazılmamış gibi görünecek" diyerek. Tazeleme başarısızsa cevap *bilinmiyor*, ki
*güncel* ile aynı şey değil (K-131).

**Sınırı.** Denetim çalışma kopyasının geriliğini ölçüyor; `S-64`'ün öbür yarısı
— hiç birleşmemiş iş — hâlâ hiçbir denetimin öznesi değil.

### K-150 — Biriktirme koşusu koşudan önce ilan edildi, ve durma kararı deftere bakıyor

**Karar.** Biriktirme koşusunun şartları, durma ölçütü ve yorumu
`experiments/setup-protocol.tr.md` §18'de, koşu başlamadan yazıldı. Koşucu
`scripts/setup/run_accumulation.py`, defteri `results/accumulation-ledger.json`.

**Şartlar tek kaynaktan doğrulandı.** Önek `bir1` kendi bölümünü adlandırıyor,
model oradan çözülüyor (K-138), ve `scripts/check_declared_conditions.py` ilan
edilen on alanın onunu koşunun okuyacağı yerle karşılaştırdı: hepsi tuttu. Bu
denetim koşudan **önce** koştu, çünkü S-58 üç kez koşudan sonra koştu.

**Durma ölçütü iki dallı ve karar hafızadan değil defterden veriliyor.** Dal A
iki ardışık bloğun sıfır yeni beceri eklemesi; dal B iki yüz yetmiş epizot
tavanı. Her blok sonunda deftere bir satır giriyor ve durma kararı o satırlara
bakılarak veriliyor. Hafızadan verilen bir durma kararı, koşuyu sonuca göre
durdurmayı mümkün kılar.

**Beceriye bakılıyor, örüntüye değil.** Yüz beş örüntüden dört beceri çıkaran
süzme zincirinin örüntü sayısını takip etmediği ölçüldü (K-145), yani örüntü
eğrisini izlemek yanlış niceliği izlemek olurdu.

**İndeks kütüphaneyle aynı blokta madenleniyor.** `S-65` bir kez oldu ve sebebi
tam olarak birini madenleyip diğerini madenlememekti. Koşucu iki üreticiyi
yan yana çağırıyor ve biri düşerse koşu duruyor.

**K-143'ün açık bıraktığı boşluk kapandı.** O kayıt "kütüphane yeniden
madenlenirse yeni seriye düşer ve `LIBRARY_SERIES` satırının onunla birlikte
taşınması gerekir; bunu hatırlatan bir denetim yok" diyordu. Bu koşu her otuz
epizotta madenliyor, yani boşluk ilk blokta ısırırdı. Ön koşul denetimine bir
satır eklendi: aktif seri kütüphane serisinden daha çok beceri taşıyorsa denetim
**düşüyor** ve taşınacak satırı adıyla söylüyor. Ateşlediği kanıtlandı. Koşucu
da blok sınırında aynı şeyi yazıyor.

**Tek tohum, ve gerekçesi ölçülmüş.** Destek ayrık göreve göre sayılıyor; geçmiş
bir göreve ikinci tohum kütüphaneye hiçbir şey eklemiyor. İkinci ve üçüncü
süpürmeler yalnız düşen görevleri koşuyor.

**Yorum önceden yazıldı, üç dal ve bir dördüncü.** Bugünkü oran yüz beş örüntüden
dört beceri; korunursa doğrusal artış, düşerse süzme zinciri darboğaz,
yükselirse korpus çeşitliliği artmış. Hiçbirine uymuyorsa `K-104`.

**Bu koşu birincil soruyu cevaplamıyor.** Bir korpus üretiyor ve o korpusun
kütüphaneyi ne kadar büyüttüğünü ölçüyor. Deneyin kendisi ayrı.

### K-148 — Onaylayıcı küme daraltıldı: iki kapı yönsel oldu, koşudan önce

**Karar.** Güç sorununun üç kapanış yolundan **(c)** seçildi: hangi ayrımların
onaylayıcı sayılacağı daraltılıyor. `Y-2` (ezberleme) ve `Y-6`'nın birinci dalı
(hacim kontrolü) onaylayıcı kümeden çıkıyor. İlan `experiments/preregistration.md`
A.7'nin altında, tarihli, **koşudan önce**.

**Kalan onaylayıcı ayrımlar üç tane:** `Y-1` (birincil soru), `Y-6`'nın ikinci
dalı (içerik mi hacim mi), ve `Y-4`/`Y-5` (beklenen etki %20 ve üstündeyse).

**Korunacak ayrım, ve bu kaydın asıl işi.** İki kapı **sonuç hoşa gitmediği için
çıkarılmıyor** — sonuç yok, deney koşmadı. Bu örneklem boyutunda **hüküm
üretemedikleri** için çıkarılıyor, ve bunu ölçen kayıt `S-67`. Fark önemli çünkü
ikisi dışarıdan aynı görünür: her ikisinde de bir kapı kayıttan düşer. Ayıran
şey **zamanlama ve gerekçenin kaynağı**, ve ikisi de burada kayıtlı.

**Kapılar silinmiyor.** Özgün ilanları `docs/11-falsification.tr.md` içinde
olduğu gibi duruyor; altlarına tarihli ek düşüldü. Silmek, daraltmanın neyi
daralttığını doğrulanamaz kılardı — `config/naive_compiler.yaml`'ın kalmasıyla
aynı sebep.

**Yönsel kalıyorlar, susmuyorlar.** Kazanç görülmüş ve görülmemiş görevlerde ayrı
ayrı raporlanacak; alakasız kolun tabana göre farkı ayrı raporlanacak. Yazılmayan
tek şey **hüküm**: "kapı ateşledi" ya da "ateşlemedi" cümlesi kurulmayacak.

**Neden (c), ve bu kayıt seçimi savunmuyor.** (a) ölçümle kapalı: bu projenin
ölçtüğü en yüksek nokta DeepSeek eylem tabakasında 0,600 veriyor, eşik 0,75
(K-147). (b) 500 görev ve ~225 oturum-saati istiyor, ve ölçülen popülasyonu
değiştiriyor (K-149). (c) bedava. Seçim kullanıcınındı; bu kayıt onu ve
gerekçesini tutuyor.

**Tırmanma tetiği ilan edildi.** Deney 105 eylem görevinde koşulduğunda `Y-1`'in
bootstrap aralığı sıfırı **dışlayamazsa**, (b) yoluna geçilir. Birincil sonuç
okunuyorsa (b) gerekmez. Tetik sonuç görülmeden konuyor, çünkü sonucu gördükten
sonra konan bir tetik tetik değildir.

**Alternatifler defteri kapanmıyor.** Üç yolun durumu `docs/14-alternatives-ledger.tr.md`
içinde tutuluyor ve çerçeve içindeki yollar tükenirse oraya dönülüyor.

**`S-66` bu kararın altında.** Daraltmanın dayandığı genişlikler iki hücreden
ölçülen bir gürültü katsayısıyla hesaplandı: her genişlik alt sınır, yani
çıkarılan iki kapı gerçekte **daha da** uzakta olabilir, daha yakında olamaz.

### K-147 — İki kapanış yolu fiyatlandırıldı; yorum önceden yazılmıştı ve ateşledi

**Karar.** Güç sorununun üç kapanış yolundan ikisi ölçüldü, üçüncüsü bedava.
Yol **seçilmedi**; bu kayıt fiyatları ve önceden yazılmış yorumun hükmünü
taşıyor. Eserler `results/stratum-rates.json` ve `results/sample-size.json`.

**Yorum ölçümden önce yazılmıştı.** DeepSeek'in eylem tabakasındaki oranı 0,75
ve üstündeyse (a) ilkece var ve soru "hangi kullanılabilir model ulaşır"a döner;
altındaysa (a) ölçtüğümüz her model için kapalı ve seçim (b) ile (c) arasına
iner.

**(a) yolunun tavanı: 15/25 = 0,600.** Eşiğin (0,75) altında, yani **ikinci dal
ateşledi**.

| Koşu | Toplam | Eylem tabakası | Cevap |
|---|---|---|---|
| DeepSeek V4 Flash, birleşim | 20/30 | **15/25 = 0,600** | 5/5 |
| — durma kuralı açıkken | 13/30 | 8/25 = 0,320 | 5/5 |
| — kuralın kestiklerinde kural kapalıyken | 7/30 | 7/25 = 0,280 | 0/5 |
| gpt-4o, yayımlanmış | 15/30 | **10/25 = 0,400** | 5/5 |
| `qwen2.5-coder:32b` | 11/30 | 7/25 = 0,280 | 4/5 |
| `qwen2.5-coder:14b` | 3/30 | 1/25 = 0,040 | 2/5 |

**DeepSeek bu projenin ölçtüğü en yüksek nokta**, ve eylem tabakasında eşiğin
altında. Yani (a) yolu ölçülen hiçbir model için açık değil. Bu bir model
bulgusu değil, tasarım bulgusu.

**Manşet oran neden yanıltıyor, sayıyla.** Yeterince güçlü her koşu cevap
tabakasının **beşte beşini** çözüyor — DeepSeek, gpt-4o, ve 32B dördünü. Cevap
tabakası doyuyor, çünkü orada hiçbir şey yapmayan bir ajanın bedava geçtiği bir
test var (K-144). Manşet oran bu doygunluğu eylem tabakasının üstüne sıvıyor ve
sistematik olarak yukarı sapıyor: DeepSeek'te 0,667 karşı 0,600, 32B'de 0,367
karşı 0,280.

**Bir yan gözlem, kaydedilmeye değer.** Kural kapalıyken gelen yedi geçişin
**yedisi de** eylem tipi, hiçbiri cevap tipi değil. Durma kuralı kestiği yerde
seçici davranmıyordu: kestiği şey tam olarak dünyayı değiştiren görevlerdi.

**(b) yolunun fiyatı: 500 eylem görevi.** Geçiş oranı ölçülen 0,280'de sabit
tutulup yalnız örneklem boyutu büyütüldüğünde, ezberleme kapısının okuduğu
yarının aralığı etkinin yarısının altına **beş yüz görevde** iniyor (beklenen
etki %20 ve üstü için). Beklenen etki %10 ise havuzun tamamında bile inmiyor.

**Beş yüz görev nereden gelir.** Bugünkü 105'in üstüne `test_challenge`'ın
eylem tipi 408 görevinden 395'i, yani o bölmenin neredeyse tamamı. Ayrılmış küme
tanımı değişir. Havuzun tümü 623 eylem görevi (`test_normal` 105,
`test_challenge` 408, `dev` 45, `train` 65) ve `train` biriktirme havuzu olduğu
için oradan almak ayrı bir karar.

**(b)'nin hesap tarafı da fiyatlı.** 500 görev × 5 koşul × 3 tohum = 7500
epizot; ölçülen epizot başına 0,02994 oturum saatiyle **~225 oturum-saati**,
bugünkü tasarımın dört katı.

**Kaba kestirim ile ölçüm ayrıştı ve ölçüm kazandı.** Elle yapılan kestirim ~282
göreve işaret ediyordu; ölçüm 500 diyor. Fark genişliğin yalnız kök-n ile
gitmemesinden: büyüyen örneklem `test_challenge`'tan geliyor ve o bölmenin
çapaları büyük, yani tavanları da büyük, yani sansürlü gözlemler daha uzak.

**(c) bedava ve bu kayıt onu ölçmedi.** Hangi ayrımların onaylayıcı sayılacağını
daraltmak para değil karar istiyor.

**S-66 iki fiyatın da altında.** Gürültü katsayısı iki hücreden ölçüldü, yani
gerekli örneklem boyutu **alt sınır**: gerçek değişkenlik büyükse 500 yükselir,
düşmez.

**Ek — 25 Eylül 2026.** Yukarıdaki 500 bir medyan; tekrar başına aralık 400–557
ve bazı tekrarlarda ulaşılamaz (`K-168`).

### K-146 — Geçiş oranı eşiği seçilmedi, ön kayıttan türetildi

**Karar.** Eşik ne benim ne kullanıcının seçtiği bir sayı. Ön kayıttaki her
ayrım örtük bir genişlik şartı taşıyor; şartlar çıkarıldı, ölçülmüş aralık
genişlikleriyle çaprazlandı, ve eşik **en büyük şartın** okunur hâle geldiği
oran oldu. Türetici `scripts/setup/derive_pass_threshold.py`, eseri
`results/pass-threshold.json`.

**Her şart tek bir ölçülen niceliğe indirgeniyor.** Birincil aralığın genişliği
`w`, birincil etki `d`. Türetilmiş bir nicelik hakkındaki bir ilan — bir alt
küme, iki farkın farkı, tek bir kol — o niceliğin genişliğini ister, ve o
genişliğin `w`'ye oranı **örneklemin yapısal bir olgusu**, etki büyüklüğünün
değil. İki oran ölçüldü: alt küme birincil genişliğin **1,42** katı, çıkarıcı
kontrol **0,82** katı. Geriye kalan her şart `w/|d|` üzerinde bir sınır.

**Bağlayıcı olan tek şart ezberleme kapısı.** Y-2 iki parametre kümesinde de
eşiği belirliyor, çünkü şartı ilan edilen paylardan bağımsız: kapı örneklemin
**yarısını** okuyor ve o yarının aralığı 1,42 kat geniş, yani birincil genişlik
etkinin **0,35**'inin altında kalmalı. Öbür beş şart 0,50 ile 2,00 arasında ve
hepsi daha erken sağlanıyor.

**Üç sonuç önceden yazılmıştı ve üçü de çıktı.**

1. **Bazı ayrımlar bir oranda okunur hâle geliyor.** Y-1 0,10-0,15'te, Y-6.2
   0,10-0,20'de, Y-4/Y-5 0,10-0,37'de, A.11 0,10-0,65'te, Y-6.1 0,15-0,55'te.
2. **İki ayrım hiçbir oranda okunmuyor, ve ikisi de beklenen etki %10 iken.**
   Y-2 her iki parametre kümesinde de taranan en yüksek orana (0,85) kadar
   okunmuyor; Y-6.1 muhafazakâr kümede aynı durumda. Bunlar kusur değil,
   tasarımın taşıyamadığı iddialar: `S-67`.
3. **Türetilen eşik ölçülen oranın üstünde.** Eşik beklenen etkiye göre 0,75 ile
   0,85 arasında; birincil tabakada ölçülen oran **0,280**. 32B nitelemiyor ve
   deney bu hâliyle güçsüz: `S-68`.

**Ölçülen oran 0,367 değil 0,280, ve fark tabakalamadan geliyor.** 32B'nin
11/30'u iki tabakayı karıştırıyor: cevap tipinde 4/5, eylem tipinde **7/25**.
K-144'ten sonra birincil örneklem eylem tabakası, yani karşılaştırılacak sayı
0,280. Cevap tabakasının yüksek oranı tam da hiçbir şey yapmayan bir ajanın
bedava test topladığı yerden geliyor.

**Üç pay ilan edildi, ölçülmedi, ve adları yazılı.** Ön kayıt hacim etkisinin
mekanizma etkisine oranını, tek kolun birleşik koldaki payını, ve iki eksen
noktasının bir şekli şekil yapacak kadar ayrışma miktarını söylemiyor; kayıtta
da yok. İkisi muhafazakâr ikisi cömert iki küme üzerinden tarandı ve **ikisi de
aynı eşiği** verdi, çünkü bağlayıcı şart bu paylardan bağımsız.

**Türetilmeyen ilanlar da sayıldı.** Kapsama eşiği (%25) ve tavana çarpma kuralı
(%10) farklı nicelikler — binom oranlar, bu tablonun içinde değiller. Tanı
metriğinin "oran hareket ediyor mu" ayrımının eşiği **hiç ilan edilmemiş**, ayar
bütçesinin sayısı da öyle (ön kayıt bunu kendisi yazıyor). Ters U şekli ilanın
kendisinde onaylayıcı sayılmıyor, yani şart doğurmuyor. Ve **negatif aktarım
eşiği diye bir ilan depoda yok**: kartların zarar verdiği durumu Y-1'in "ters
yöndeyse" yan cümlesi dışında hiçbir yer karşılamıyor.

**S-66 her satırda.** Genişliklerin arkasındaki gürültü katsayısı iki hücreden
ölçüldü, yani her genişlik bir alt sınır ve türetilen her eşik **iyimser**
tarafta. Gerçek eşik bundan yüksek olabilir, düşük olamaz.

### K-145 — Naif madenci ölçütü koştu: koşul yazılmıyor, ve sebebi yazılıyor

**Karar.** `naive_compiler` koşulu yazılmıyor. Naif madenci aynı korpusta
derleyicinin dört becerisinin dördünü de buluyor, yani koşulun izole edeceği
fark bu korpusta yok.

**Ölçüt koşudan önce ilan edilmişti.** İki kütüphane belirgin farklıysa
`naive_compiler` koşulu altı koşulun içine giriyor ve maliyeti kabul ediliyor;
aynı becerileri üretiyorsa koşul yazılmıyor ve bulgu "bu korpusta derleyicinin
karmaşıklığı hiçbir şey kazandırmadı" oluyor.

**Naif madenci naif yazıldı.** Sabit uzunlukta **bitişik** n-gram, aynı alfabe,
destek yine ayrık göreve göre. Beş şey yok: kapalı örüntü süzgeci, boşluk
toleransı, argüman sınıflandırması (her argüman serbest), etki soneki şartı, ve
etki sonekine göre birleştirme. Beşi de gerçek derleyicinin bir kararı.

**Hüküm: aynı dört beceri.** Derleyicinin dört etki soneki de düz bir n-gram
tarafından **bulunuyor**; yalnız naif madencinin bulduğu bir etki **yok**. Ölçüt
gereği `naive_compiler` koşulu **yazılmıyor**, ve altı koşul beşe inmiyor —
koşul zaten yazılmamış oluyor.

**Ölçütün kapsamadığı ve karara bırakılan.** İki kütüphane aynı etkileri taşıyor
ama aynı **boyutta** değil: derleyici dört kart, naif madenci altmış dokuz kart
üretiyor. Ölçüt "aynı beceriler mi" diye soruyordu ve cevabı evet; "aynı kart
kümesi mi" diye sorsaydı cevabı hayır olurdu. Derleyicinin bu korpustaki katkısı
**keşif değil sıkıştırma**, ve bu cümle bulgunun kendisi.

**Bulgunun ikinci yarısı kütüphanenin içeriğinde.** Dört becerinin dördü de
`POST <uygulama>.auth/token`, yani giriş çağrısı. K-84 aynı sonucu getirici
tarafından söylüyordu; madenci tarafından da aynı çıkıyor. Bir n-gram madencisinin
bunu bulmakta zorlanmaması sürpriz değil.

**Sınırı.** Yirmi ayrık geçen görevlik bir korpusta ölçüldü ve beş kararı
**birlikte** kaldırıyor, yani hangisinin işe yaradığını söylemiyor. Korpus
büyüdüğünde tekrar koşulması gereken bir ölçüm; eser
`results/naive-miner.json`, karşılaştırıcı `scripts/setup/compare_naive_miner.py`.

### K-144 — Cevap tipi görevler çıkarılmıyor, tabakalanıyor

**Karar.** Değerlendirme örnekleminde cevap tipi görevler duruyor ama birincil
ölçüme girmiyor. Birincil ölçüm **eylem tipi** görevlerde; cevap tipi görevler
**ayrı** raporlanıyor. Ön kayda 28 Ağustos 2026 tarihli ve **keşifsel** etiketli
bir ek olarak yazıldı.

**Gerekçe ölçüldü, varsayılmadı.** İki tabakada doğrulayıcı aynı güçte değil:

- Cevap tipi görevlerin **hepsinde** "hiçbir model değişmedi" iddiası var, ve o
  testi hiçbir şey yapmayan bir ajan tanım gereği geçiyor.
- Cevap tipi görevlerin test medyanı **iki**, yani bedava geçen test hükmün
  yarısı; geriye tek bir dizge eşitliği kalıyor.
- Eylem tipi görevlerin test medyanı **yedi**, ve hiçbirinde o bedava test yok.

Sayılar `results/task-types.json` içinde; sınıflandırıcı `scripts/analyze_passes.py`
içindeki `task_shape`, ikinci bir kopya yazılmadı.

**Neden çıkarmak değil tabakalamak.** Çıkarmak örneklemi daraltır ve dışarıda
kalanı görünmez yapar. Tabakalamak ikisini de raporlar ve gevşek ölçümün gevşek
olduğunu **yazılı** tutar. Havuzlamak ise sıkı bir ölçümle gevşek bir ölçümü
karıştırmak olurdu, ve karışımın yönü belli: gevşek tabaka tesadüfi geçişi
ucuzlatır, yani mekanizmayı kayırır.

**Keşifsel, ve bu saklanmıyor.** Tip ayrımı sonuçlar görüldükten sonra yapıldı.
Onaylayıcı bir sınamanın parçası değil ve yanlışlama kapıları yalnız eylem
tabakasında hüküm veriyor.

**Kabul edilen bedel.** Birincil örneklem 123'ten 105'e iniyor; güven aralığı
örneklem boyutuna bağlı olduğu için bu daralma okunan her aralıkta taşınıyor.

### K-143 — Kütüphanenin yeri açık bir sabit; koşunun yazdığı yer değil

**Karar.** Beceri kütüphanesi ve hata indeksi `zihin.records.LIBRARY_SERIES`'ten
okunuyor, `ACTIVE_SERIES`'ten değil. Kart isteyen her çağrı `open_library()`'den
geçiyor; epizotlar yazıldıkları yere yazılmaya devam ediyor. İkisi ayrı soru.

**Gerekçe: iki soru bir işaretçiye bağlanmıştı.** `ACTIVE_SERIES` "koşu nereye
yazıyor" sorusunun cevabı ve bir seri **şema** sebebiyle açılıyor — `ALTER
TABLE`'ın ekleyemediği bir `CHECK` kısıtı yüzünden (S-29). Kütüphanenin bununla
ilgisi yok: bir kez madenlenir ve madenlendiği serinin içinde durur. Seri 3
açılınca iki cevap ayrıştı ve yedi çağrı yanlış dosyaya sordu.

**Arıza sessiz değil ama geç.** `latest_library_and_index` boş kütüphanede
`RecordError` atıyor, yani koşu düşüyor — ama **epizot başladıktan sonra**,
madencilik adımında. Ön koşul denetimine bir satır eklendi
(`scripts/setup/check_prerequisites.py`), böylece cevap koşudan önce geliyor.

**Neden sabit, neden arama değil.** "Satırı olan hangi dosyaysa o" demek, cevabı
diskte ne bulunduğuna bağlar. Sabit olunca kütüphane taşındığında **satır
taşınıyor**, ve o taşınma birinin okuyabileceği bir commit oluyor.

**Reddin kendisi yol gösteriyor.** Boş bir seride kütüphane sorulduğunda mesaj
üç şeyi birden söylüyor: hangi dosyaya bakıldığı, kütüphanenin hangi seride
olduğu, ve koşuların hangi seriye yazıldığı.

**Aynı desen tarandı ve yedi yerde vardı.** `scripts/record_run.py`,
`scripts/setup/measure_retrieval.py`, `scripts/setup/build_pilot_dataset.py`,
`scripts/setup/measure_card_demo.py`, `scripts/setup/measure_context_cost.py`,
`scripts/setup/measure_card_tokens.py` ve
`scripts/setup/measure_retriever_discrimination.py`. Yedisi de düzeltildi, ve
desenin kendisi bir teste çivilendi: bir betik `ACTIVE_SERIES` açıp aynı
bağlantıya kütüphaneyi soruyorsa test düşüyor (kanıtlandı).

**İkinci eksen aynı hastalıktan.** `build_pilot_dataset.py` **epizot** tarafını
da `ACTIVE_SERIES`'ten okuyordu ve çıktısına o sabiti yazıyordu; pilot seri
2'den kurulmuştu. Artık `--database` açık bir argüman ve özet **saydığı dosyayı**
adıyla yazıyor.

**Sınırı.** `build_skill_library.py` ve `build_failure_index.py` hâlâ
`ACTIVE_SERIES`'e madenliyor. Kütüphane yeniden madenlenirse yeni seriye düşer
ve `LIBRARY_SERIES` satırının onunla birlikte taşınması gerekir; bunu hatırlatan
bir denetim yok, yalnız bu kayıt var.

### K-142 — Atıf alan eser izleniyor; atıf ancak çözülebiliyorsa atıftır

**Karar.** Sunum iskeletinin ve pilot raporunun atıf verdiği her `results/*.json`
eseri git'te izleniyor. `results/` genelinde eleme sürüyor; kural dar: **atıf
alan izleniyor, almayan koşuya özel kalıyor.** `scripts/check_citations.py`
ikisini birden soruyor — dosya var mı, ve `git ls-files` onu taşıyor mu.

**Gerekçe.** Bir belge bir dosyayı kanıt diye gösteriyorsa, o dosyayı yalnız
üreten makinede bulmak kanıt değil. Depoyu klonlayan bir hakem otuz atıfın on
sekizini çözemiyordu.

**Bulan şey CI oldu, yerel koşu değil.** Atıf denetimi bir tur önce kurulmuştu
ve yerelde "otuz atıfın otuzu çözülüyor" diyordu. Aynı denetim test olarak
CI'da koştu ve taze klonda on sekizini çözemedi, çünkü `results/*` eleniyor.
Yerel disk ile depo ağacı iki ayrı küme, ve denetim birincisine bakıyordu.

**Sınıf tanıdık, biçimi yeni.** K-49 "yeşil bir kontrol koştuğunun kanıtı
değil" diyordu. Buradaki hâli daha ince: kontrol koştu, doğru soruyu sordu, ve
**yanlış kümede** sordu. Yeni soru kümeyi adlandırıyor.

**Bedeli ölçüldü.** İzlenmeye alınan dokuz eser toplam 243 KB.

**Sınırı.** Kural yalnız atıf alanları kapsıyor. Bir belgede adı geçmeyen ama
bir betiğin okuduğu eser hâlâ elenebilir.

### K-141 — PR #49 dört yığılı PR'a bölünüyor, tarih yeniden yazılmadan

**Karar.** On dokuz Ağustos'tan yirmi altı Ağustos'a kadar biriken otuz beş
commit tek bir PR olarak birleşmiyor. Dört PR'a bölünüyor, ve bölme **dal
işaretçisiyle** yapılıyor: mevcut doğrusal tarih üzerinde sınır commit'lerine dal
açılıyor, birincisi `main`'e birleşince ikincisi açılıyor, ve böyle devam
ediyor. Her PR'ın farkı tam olarak kendi commit'leri oluyor.

**Neden bölünüyor.** Protokol §6 her yol haritası maddesinin kendi PR'ıyla
kapanmasını istiyor ve gerekçesi burada birebir geçerli: otuz beş commit'lik bir
PR incelenemez, ve tek bir kapanış notu dört ayrı konuyu anlatmak zorunda
kalırdı. Konular gerçekten ayrı: protokol çevirisi ile 32B ölçümü, Colab koşum
ortamının kurulması, koşul zincirinin ölçülmesi, ve eksenin uzatılıp
raporlanması.

**Neden cherry-pick değil.** Tarih yeniden yazılmıyor; bu karar kesin. Cherry-pick
commit'leri bölmek ya da kopyalamak demek olurdu. Dal işaretçisi hiçbir commit'e
dokunmuyor.

**Sınırlar ve boyutlar.**

| PR | Aralık | Commit | Konu |
|---|---|---|---|
| A | `8591b66`..`30ffb88` | 12 | protokol çevirisi, çit içi ölçümü, analiz betiği, yolların yapılandırmaya taşınması, kapanış raporu, 32B ölçümü |
| B | `4cb17b4`..`5952c94` | 14 | Colab koşum ortamı: önyükleme, klonun sırrı, LFS yansısı, Ollama, ön koşullar, yerleşiklik, kalkanın girdisi |
| C | `f01132e`..`ed5ce8b` | 3 | koşul zinciri ölçüldü, 32B ilan edildi, model adı tek kaynağa indi |
| D | `438e1b6`..`41f79ec` | 6 | yerel eksen 4000'de, geçiş incelemesi, 32B kaydı, serinin birleşmesi, eksen uzatma raporu, atıf ve tarih denetimleri |

**Bölmenin bedeli ölçülecek, varsayılmayacak.** Her sınır commit'inin kendi
başına yeşil olması gerekiyor. Yeşil olmayan bir commit sınır değildir; CI
söyleyecek, ve söylerse o iki PR tek PR olarak birleşiyor. Bu, bölmenin
sınanmadan iddia edilmemesi demek.

**Beşinci bir şey var ve o birleşmiyor.** `origin/colab-sonuclari` dalı 14B
noktasının iki eserini taşıyor (`results/b14-taramasi.json`,
`results/colab-ortam.json`) ve hiçbir dalın atası değil. Aynı dalda bir
`results/zihin-3.sqlite` de var ve o **birleştirilmiş serinin aşılmış yarısı**;
dalı birleştirmek onu geri getirirdi. Bu yüzden dal birleşmiyor, iki JSON eseri
ayrı bir commit'le taşınıyor, ve dal köken kaydı olarak duruyor.

**`check_merged_artefacts.py` bunu yakalayamazdı.** Öznesi birleşmiş PR'lar;
birleşmemiş iş onun için yok. Ayrıntısı `S-64`'te.

### K-140 — Kendi tarihini yazan her ek, onu yazan commit'le karşılaştırılıyor

**Karar.** Bir belgeye kendi tarihini yazan her satır — "Ek — 25 Ağustos 2026",
"Kapandı, 18 Ağustos 2026" — o metni depoya getiren commit'in tarihiyle
karşılaştırılıyor. Denetim `scripts/check_dates.py`, `local_checks.sh` içinde.

**Gerekçe: bir ön kaydın değeri tarihlerinin doğrulanabilir olmasında.**
"Koşudan önce ilan edildi" bir zaman iddiası, ve onu ancak kayıt çözer. Belgeye
yazılan tarih iddia, commit tarihi kanıt. Bir hakem `git log`'a bakarsa ikisini
karşılaştırır.

**Bulan olay.** `experiments/preregistration.md` §A.11'in ikinci eki kendini **21
Ağustos 2026** diye tarihledi. Eki yazan commit `e2e40dd`, tarihi 25 Ağustos
14:06 UTC; ilan ettiği koşu `b32c`, künyesindeki ilk epizot 18:55 UTC. Yani ilan
koşudan **dört saat kırk dokuz dakika** önce yapıldı, dört gün önce değil. İddia
yıkılmadı, payı daraldı — ve yanlış tarih onu olduğundan geniş gösteriyordu.

**İki tür tarih ayrılıyor.** *Olay tarihi* ("kapı 11 Ağustos'ta ateşledi")
sonradan yazılır ve olaya aittir; denetlenmiyor. *Ek tarihi* ("Ek — 25 Ağustos
2026") yazma anını iddia eder; denetleniyor. Tarama on dokuz ek tarihi buldu ve
ikisi tutmadı: yukarıdaki, ve `S-58`'in üçüncü örneği (20 Ağustos yazıyordu, o
gün §15'in koşullarının ilan edildiği gündü; bulgu `f01132e` ile 25 Ağustos'ta
yazıldı).

**Arama yol kısıtsız yapılıyor.** Yeniden adlandırma, yola kısıtlı bir aramada
metni dizin şemasının değiştiği güne tarihler. İlk tarama tam da bunu yaptı ve
yirmi iki sahte uyuşmazlık üretti; gerçek sayı ikiydi.

**Çeviri ayrı ölçülüyor.** `.en.md` kaynağından sonra yazılır ve kaynağın
tarihlerini taşır, yani kendi commit'i bir şey kanıtlamaz. Orada ölçülen şey
çevirinin bir tarihi **değiştirmemiş** olması: iki yarının kendini tarihleyen
satırları çoklu küme olarak karşılaştırılıyor. Serbest düzyazı karşılaştırmaya
girmiyor, çünkü Türkçe "20 Ağustos'ta" yazarken İngilizce "on 2026-08-20" yazıyor
ve fark gösterimde, kayıtta değil.

**Kaçış deliği dar.** Düzeltilmiş bir tarih kendi commit'iyle asla tutmaz, çünkü
düzeltmek bugün yeni bir commit yaratır. Bu yüzden uyuşmazlık, paragrafta
**yazılan tarihe eşit tarihli bir commit'i adıyla anan** bir düzeltme notu varsa
da kabul ediliyor. Commit'i adıyla anmak işin tamamı; notun kendisi hiçbir şeyi
susturmuyor.

**Sınırı.** Denetim tarihin doğru olduğunu değil, **kayıtla tutarlı** olduğunu
gösteriyor. Yanlış tarihle yazılıp aynı gün commit'lenmiş bir ek bu denetimden
geçer.

### K-139 — Başka bir makineden gelen kayıt önce doğrulanıyor, sonra seriye katılıyor

**Karar.** Bir ölçüm serisi iki makinede koşabilir, ama **iki dosyada
kalamaz**. Dışarıdan gelen yarı önce doğrulanıyor, sonra katılıyor, ve katılma
satır satır sınanıyor.

**Gerekçe: elle taşınan bir kayıt zinciri kırıyor.** Bu deponun bütün disiplini
her sayının onu üreten commit'le birlikte gezmesi. Colab oturumu kapanınca
tarama çıktısı kayboldu ve veritabanı Drive'dan **elle** indirildi. Elle taşınan
bir dosyayı doğrulamadan okumak, kaydı hikâyeye çevirir.

**Doğrulama neye karşı yapılıyor.** İlan edilen şartlara (§16.2'nin sekiz alanı)
ve **taşımadan önce başka bir yerde gözlenmiş** iki alana: ön kontrol künyesinin
`boot_id`'si ve `wall_clock_utc`'si. Birincisi dosyanın doğru koşuyu taşıdığını,
ikincisi o koşunun bizim gördüğümüz koşu olduğunu gösteriyor. Sekiz alanın
sekizi ve iki gözlemin ikisi tuttu; `code_commit` de koşudan önce itilen
commit'ti.

**Bölünmüş seri bir analiz hatası kaynağı.** "Seri 3'ü oku" diyen bir analiz,
iki dosyaya bölünmüş bir seride yarısını görür ve kimsenin yeniden üretemeyeceği
bir sayı raporlar. Bu yüzden birleştirme ertelenmedi.

**Birleştirme iddia değil, sınanan bir işlem.** `merge_series.py` çakışan koşu
kimliği varsa **duruyor**, anlamadığı tabloda satır varsa **duruyor**, tamsayı
anahtarları kaydırıp yabancı anahtarları aynı miktarda kaydırıyor, ve sonra
sayıları, `PRAGMA foreign_key_check`'i ve koşu başına epizot sayılarını
karşılaştırıyor. Yeni bir dosyaya yazıyor; iki yarı el değmeden duruyor.

**Sınırı.** Doğrulama dosyanın **bizim koşumuz** olduğunu gösteriyor, içeriğinin
doğru olduğunu değil. Bir epizodun kendi içinde yanlış yazılmış olması bu
denetimden geçer; onu yakalayan şey şema kısıtları ve künye sözleşmesi.

### K-138 — Doğru koşan ama yanlış özne üzerinde koşan bir denetim, düşen denetimden kötüdür

**Karar.** Bir denetim **öznesini kendi buluyor**, kendisine söylenmesini
beklemiyor. Koşunun hangi model, hangi önek, hangi seri üzerinde çalıştığı tek
bir yerde ilan ediliyor — koşunun kendi önekinin adlandırdığı şartlar tablosu —
ve her okuyucu oradan çözüyor. Hiçbir betikte model adı varsayılanı yok.

**Gerekçe ölçüldü, ve bu sınıfın en keskin hâli.** Colab'da önyükleme 14B
çekti, ölçüm 32B istedi. Sebep: model adı **altı yerde** yazılıydı — defterde
iki `%env` satırı ve dört betikte birer varsayılan. Defterin `%env` satırları
önyükleme hücresinden **sonra** geliyordu, yani `colab_bootstrap.sh` kendi 14B
varsayılanına düştü ve 14B çekti. Ön koşul denetimi de kendi 14B varsayılanını
kullandı ve **"yirmi dokuz sorunun hepsi cevaplandı, eksik yok"** dedi.

**Cevap doğruydu. Özne yanlıştı.** Denetim 14B hakkında haklıydı ve 32B hakkında
alakasızdı. Düşen bir denetim durdurur; **başarı bildiren bir denetim
yürütür**. Bu yüzden bu kayıt K-49'un ("yeşil bir denetim koştuğunun kanıtı
değil") ve K-132'nin ("uydurma girdiyle sınamak üreteni sınamıyor") üçüncü
kardeşi: doğru cevap, doğru mekanizma, **yanlış özne**.

**VRAM düzeltmesi bunun kanıtı.** Bir tur önce VRAM ihtiyacını modelin ölçülen
boyutundan hesaplamaya geçmiştik ve mekanizma çalıştı — 14B için 10714 MiB
hesapladı. Düzeltme doğruydu, **girdisi yanlıştı**. Bir hesabın doğruluğu
girdisinin doğruluğunu göstermiyor.

**Uygulaması: tek kaynak, ve türetme.** `src/zihin/declared.py` koşunun
komutundan öneki, önekten şartlar bölümünü, bölümden değerleri çözüyor.
`measure_band.py` zaten öneği taşıyor, oradan modeli buluyor. Önyükleme aynı
soruyu soruyor. Üç kurulum betiğindeki 14B varsayılanı silindi; `ZIHIN_MODEL`
verilmişse ilanla **karşılaştırılıyor** ve tutmazsa duruluyor. `record_run.py`'ın
`models[0]` geri düşüşü de kaldırıldı — o varsayılan eksenin **en küçük**
modelini sessizce koştururdu.

**Aynı tur içinde süpürüldü, kuyruğa bırakılmadı.** Aynı desenden dört tane daha
bulundu: koşu öneki defterde iki kez (koşu komutunda ve yayımlama komutunda),
seri adı `zihin-3.sqlite` dört yerde, sunucu günlüğü yolu bir fonksiyon
varsayılanında ikinci kez, ve sunucu adresi üç hücrede. Dördü de tek kaynağa
indirildi. Kalan iki tekrar bilerek bırakıldı ve sebebi yazıldı: `/content/zihin`
defterin `!` satırlarında (Colab'ın sabit yolu) ve `11434` betiklerin kullanım
örneklerinde (belge metni, çalışan değer değil).

**Sınırı.** Kural bir değerin **kaç yerde yazıldığını** azaltıyor; hangi değerin
doğru olduğunu söylemiyor. Tek kaynak yanlışsa herkes aynı yanlışı alır — ve
onu yakalayan şey bu kayıt değil, ilanın kendisinin gözden geçirilmesi.

### K-137 — Eksene beşinci nokta: 32B, ve bu kez açılan bir kilit yok

**Karar.** `qwen2.5-coder:32b-instruct-q4_K_M` ölçek eksenine beşinci nokta
olarak giriyor. `config/models.yaml` onu taşıyor, ön kayıt A.11'e ikinci bir
tarihli ek düşüldü, ve sonuç **keşifsel** etiketli. Şartları protokol §16.2'de,
koşudan önce ve mutlak değerle.

**14B'den farkı: yeni bir kilit açmıyor.** K-133 "model yerel donanımda koşuyor"
kısıtını kaldırmıştı; o kilit zaten açık. Bu nokta yalnız ölçeği uzatıyor. Aile
kilidi yine duruyor — beşi de `qwen2.5-coder`, beşi de `q4_K_M`, ve bu artık
prozada değil testte (`test_the_axis_varies_size_and_nothing_else`).

**OpenRouter'daki 32B bu nokta değil, ve karıştırılmaması gerekiyor.** O ölçüm
barındırılan bir sunucuda, **kuantalaması bilinmeyen** ağırlıklarla ve eksik bir
kümeyle yapıldı (S-58, S-59). Bu nokta bizim kuantalamamızla, ölçülen dosya
boyutu 19,851 GB. İkisi arasındaki fark büyük ölçüde kuantalama olur ve
karşılaştırma **oran değil varlık** düzeyinde yapılabilir (§16.6).

**Şartlar sonuca bakılarak seçilmedi, ve gerekçesi yazıldı.** §16.3 üç değerin
neden o değer olduğunu ayrı ayrı anlatıyor: 400 bir tasarım değil bir
varsayılanın kalıntısıydı, 4000 sonradan bilerek seçildi; 40 sıkılırsa iki koşu
karşılaştırılamaz; `off` **ulaşılamaz** çünkü `ShieldMode`'da o üye yok.

**Bir tesadüf saklanmıyor.** Bu üç değer 14B koşusunun kullandığı değerlerin
aynısı — ama 14B koşusu bu deklarasyondan **önce** koştu ve §15.2'nin ilan
ettiği değerlerle koşmadı (S-58 üçüncü örneği). Yani iki koşunun uyuşması bir
kazanın sonucu; karşılaştırmayı mümkün kılıyor ama önceden ilan edilmiş bir
tasarım değil. Uyuşmanın **sonradan** doğru olduğu yazılı.

**Mimari farkı ölçülecek.** A100 Ampere 8.0; yerel kart ve L4 Ada 8.9. Flash
attention ve `q8_0` KV desteğinin aynı olup olmadığı `runtime_facts` ile
okunuyor ve `comparability` hükmü koşudan önce basılıyor. Tutmazsa koşu yapılır
ve sonuç etiketlenir. Sınırlama S-61.

**Sınırı.** Beşinci nokta ekseni uzatıyor, eğrinin şeklini onaylayıcı olarak
belirlemeye yetecek hâle getirmiyor; A.11'in dört şekli beş noktayla da
ayrılamıyor.

### K-136 — İlan edilen koşul, koşunun okuduğu yerden verilir; ve bir denetim ikisini karşılaştırır

**Karar.** Ön kayıtta ya da protokolde ilan edilen her koşul, koşunun onu
**okuduğu yerden** veriliyor. İlan bir metin değil bir değer olduğu için, ikisi
bir denetimle karşılaştırılıyor: `check_declared_conditions.py` protokolün
tablosunu okuyor, koşunun komutunu ve yapılandırmasını çözüyor, ve sayı olarak
karşılaştırıyor.

**Gerekçe: aynı kayma üçüncü kez.** S-58 iki kez "koşul göreli yazıldı" diye
kapandı ve mutlak yazmaya geçildi. Mutlak yazmak yetmedi. Üçüncü kez protokolde
`400` ve `15` yazıyordu, koşu `4000` ve `40` ile koştu, ve arada hiçbir bağ
yoktu — protokol bir belgeydi, koşu bir yapılandırma okuyordu.

**İki ayrı kopma, ve ikisi de sessizdi.** `max_output_tokens` için protokoldeki
değer `bant3` künyesinden kopyalanmıştı; o künye yapılandırmada o anahtar **hiç
yokken** üretilmişti, yani kopyalanan sayı hiçbir yapılandırmaya karşılık
gelmiyordu. `no_progress_limit` için defter doğru değeri **geçiyordu**, ama
`measure_band.py` bayrağı tanımıyor ve `sys.argv`'yi iki dize için tarayıp
gerisini düşürüyordu. Kabul edilmiş görünen bir bayrak, reddedilen bir bayraktan
daha kötü.

**Uygulaması, üç parça.** `measure_band.py` argümanlarını `argparse` ile
ayrıştırıyor ve **tanımadığı argümanı reddediyor**. Tanıdığı koşulları
epizoda iletiyor. `record_run.py` `--max-output-tokens` alıyor, çünkü ilan
edilen bir koşul ilan edildiği yerden verilebilmeli. Ve denetim ön koşul
denetiminin içinden koşuyor, yani koşudan önce.

**K-135'in kardeşi.** Orada aynı **değerin** iki çözümü vardı ve yerelde ikisi
aynı çıkıyordu. Burada aynı **koşulun** iki kaydı var — biri belgede, biri
yapılandırmada — ve ikisi baştan farklıydı; kimse karşılaştırmadığı için
görünmedi.

**Sınırı, ve şu an açık duran bir madde.** Denetim değeri **sayı olarak**
karşılaştırıyor; ilan edilen ama koşucuda karşılığı olmayan bir alanı
düzeltemiyor, yalnız raporluyor. `shield_mode` tam bu durumda: protokol `off`
diyor, `ShieldMode`'un `off` üyesi yok, ve hangisinin değişeceği bir ölçüm
kararı.

### K-135 — Aynı şeyi iki yerde çözmek, iki cevap demek; ve yerelde ikisi kazara aynı çıkıyor

**Karar.** Bir değerin **tek** bir çözümü oluyor, ve onu bütün okuyucular
çağırıyor. Makineye ait bir yol için öncelik ortam değişkeninde, yapılandırma
geri düşüş: günlüğün yeri sunucunun koştuğu makinenin özelliği, projenin değil.

**Gerekçe ölçüldü, ve arıza tam çatlaktan geçti.** Sunucu günlüğünün yolu iki
yerde ayrı çözülüyordu. `measure_colab_environment.py` `ZIHIN_SERVER_LOG`
okuyordu, kendi varsayılanıyla. `record_run.py` ise `server_log()` üzerinden
`config/models.yaml`'a gidiyordu, ve oradaki değer geliştirme makinesinin
Windows yolu. **Yerelde ikisi de doğru cevabı veriyordu**, çünkü o dosya burada
var. Colab'da ayrıştılar: ortam ölçümü çalışma zamanının günlüğünü okuyup
`COMPARABLE` dedi, koşu ise var olmayan bir Windows yoluna bakıp ilk epizotta
düştü. Aynı dosya, iki cevap, ve biri "hazırız" diyordu.

**Yerel anlaşma bir kanıt değil.** İki çözümün aynı makinede aynı sonucu vermesi
onların aynı olduğunu göstermiyor; yalnız o makinede ayrışmadıklarını gösteriyor.
K-117 bir denetimin cevabının ortama bağlı olmamasını istiyor; bu kayıt aynı
şeyi **bir değerin** cevabı için söylüyor.

**Arıza üç katman uzakta konuşuyordu.** Görünen ileti
`OLLAMA_FLASH_ATTENTION could not be read from the server dump` idi: eksik olan
ayarı söylüyor, aranan **dosyayı** söylemiyordu. Aynı cümle "günlükte böyle bir
satır yok" ile "günlük hiç orada değil" durumlarını birden kapsıyordu — iki
farklı sorun, iki farklı çözüm. İleti artık yolu ve işletim sisteminin hata metnini adlandırıyor
(K-125).

**Kapı bir katman öne alındı.** Koşudan hemen önce, künyenin ihtiyaç duyacağı
beş ayar **koşucunun çözeceği yoldan** okunuyor. Burada okunuyorsa orada da
okunuyor, çünkü artık tek çözüm var. Ön koşul denetimi ise sunucudan önce
koştuğu için yalnız **hangi yolun kullanılacağını** bildiriyor: ortamdan mı,
yapılandırma geri düşüşünden mi.

**K-121'in inceltilmesi.** O kayıt makineye özgü yolların koda değil
yapılandırmaya gireceğini söylüyordu. Eksik olan şuydu: yapılandırma **bir**
makinenin cevabı. Başka bir makine kendi cevabını verebilmeli, yoksa
yapılandırma gömülü yolun daha kibar hâli olur.

**Sınırı.** Kural yolları kapsıyor. Aynı desen bir sayı ya da bir eşik için de
mümkün — iki yerde ayrı hesaplanan, yerelde aynı çıkan bir değer. Onu yakalayan
şey bu kayıt değil, tek bir çözümü çağırmak.

### K-134 — Dizin rol ilan eder; bir girdi çıktı dizininde durmuyor, ve üçüncü kez aynı sınıf

**Karar.** Koşunun **okuduğu** her dosya depoda duruyor ve rolünü ilan eden bir
dizinde: `inputs/`. Bir koşunun **ürettiği** dosya `results/` altında kalıyor.
Bir dosya iki role birden sahipse — bir ölçümün çıktısı, sonrakinin girdisi —
konumu üreticiyi anlatıyor ama izlenmesi tüketiciye göre ayarlanıyor.

**Gerekçe ölçüldü, ve eksiklik değil konum.** `write-set-static.json`
`results/` altındaydı. Rolü tam tersi: kalkanın neyi engelleyip neyi
geçireceğini o belirliyor, yani **ölçümü tanımlayan** bir eser. `results/*`
`.gitignore` tarafından eleniyor, yani dosya depoya hiç girmemişti. Yerel
makinede görünmüyordu çünkü dosya oradaydı; taze bir klonda koşu
`FileNotFoundError` ile düştü. Dizin adı yanlış bir şey ilan ediyordu ve yanlış
ilan ancak dosyanın olmadığı yerde görünüyor.

**Yeniden üretmek çözüm değil, sessiz bir fark kaynağı.** Kurulu `appworld`
paketi biraz farklıysa yazma kümesi farklı çıkar, kalkan başka davranır, ve
hiçbir şey uyarı vermez. `vendor/appworld/` ile aynı mantık uygulandı: dosya
depoda durur, her ortam **aynı baytları** alır, ve doğruluğu bir özet
karşılaştırmasıyla sınanır. `derive_write_set.py --check` kurulu paketten
yeniden türetip bayt bayına karşılaştırıyor; tutmazsa duruyor ve neyin
farklılaştığını yazıyor. Otomatik yeniden yazma yok: hangisinin doğru olduğuna
insan karar veriyor.

**Sayılar buna bağlı.** 296 yazar uç ve sınır geçen 19, raporlarda alıntılanan
sayılar, bu dosyadan geliyor. Her ortamda aynı olmaları dosyanın her ortamda
aynı olmasına bağlı, ve "aynı" bir iddia olduğu için ölçülüyor.

**İkinci örnek, süpürmede çıktı.** Bant taraması (`ZIHIN_SCAN`) da taze klonda
yoktu. Ama onun **konumu doğru**: gerçekten bir ölçümün çıktısı. Yanlış olan
elenmesiydi — sonraki ölçüm onu girdi olarak okuyor. Bu yüzden taşınmadı,
`.gitignore` içinde istisna edildi. İki dosya, iki farklı kusur, iki farklı
düzeltme; ikisini aynı kefeye koymak birini yanlış yere taşırdı.

**Üçüncü kez aynı sınıf, ve asıl karar bu.** Taze bir ortam, yerel ortamın
biriktirdiği ama deponun taşımadığı bir türetilmiş eseri açığa çıkardı: önce
`appworld` LFS nesneleri, sonra veri önbelleği, şimdi yazma kümesi. Üçü de aynı
şekil. Dördüncüsünü beklemek yerine **liste** yazıldı: `check_prerequisites.py`
artık koşunun okuduğu her dosyayı adıyla, kim okuduğuyla ve nereden geldiğiyle
soruyor — kalkanın, derleyicinin, getiricinin, koşucunun ve iskelenin girdileri.
Bir onarım daha değil, sınıfın kalanını tek turda çıkaran bir denetim (K-130).

**Sınırı.** Liste bugün bilinen okuyucuları kapsıyor. Yarın eklenen bir okuyucu
kendi girdisini listeye yazmazsa aynı sınıf dördüncü kez çıkar; onu yakalayan
şey bu kayıt değil, taze bir ortamda koşmak.

### K-133 — Ölçek ekseni 14B ile bir nokta yukarı taşınıyor; açılan kilit yerel donanım, aile değil

**Karar.** `qwen2.5-coder:14b-instruct-q4_K_M` ölçek eksenine dördüncü nokta
olarak giriyor. `config/models.yaml` onu taşıyor, ön kayıt A.11'e tarihli bir ek
düşüldü, ve sonuç **keşifsel** etiketli. A-06 bununla cevaplanıyor.

**Tasarımdaki dayanağı, ve dayanak yeni değil.** S-14 kuralı pilottan **önce**
ilan etmişti: eksenin en küçük noktası taban etkisine yapışırsa eksen yukarı
kaydırılır. Aynı kayıt neden yapılamadığını da yazmıştı — *"14B 8 GB'a
sığmadığı için yukarı doğru telafi yok."* Yani engel tasarım değil donanımdı, ve
kural o engel kalkarsa ne yapılacağını zaten söylüyordu. Bant taraması sonra
üç noktanın **birden** çakılı olduğunu ölçtü: 1.5B, 3B ve 7B, hepsi sıfır.
Eksenin en küçük noktası değil, eksenin tamamı tabanda.

**Açılan kilit tek: "model yerel donanımda koşuyor".** Bu kısıt karar kaydında
ayrı bir madde olarak hiç yazılmamıştı ve A-06 onu tam bu yüzden yeniden açtı.
Colab'ın GPU'su onu kaldırıyor.

**Açılmayan kilit: aile.** Dört nokta da `qwen2.5-coder`, dördü de `q4_K_M`.
Eksenin ölçtüğü şey **boyut**; aile ya da kuantalama değişirse eksen boyut
ekseni olmaktan çıkar ve iki değişkeni birden taşır. Aile kilidi kullanıcının
kararıyla duruyor ve bu kayıt ona dokunmuyor.

**Keşifsel, ve sebebi tek cümle.** Nokta **sıfırlar görüldükten sonra**
seçildi. Veri güdümlü bir eksen uzatması onaylayıcı olamaz, ne kadar iyi
çıkarsa çıksın. Ön kayıttaki özgün ilan olduğu gibi duruyor; ek onun altında ve
tarihli.

**Sınırı.** Dördüncü nokta ekseni bir nokta uzatıyor, eğrinin şeklini
belirlemeye yetecek hâle getirmiyor. A.11'in dört şekli üç noktayla da dörtle de
onaylayıcı olarak ayrılamıyor; tablo yorum disiplini için duruyor, istatistiksel
iddia için değil. Ayrıca 14B yerelde koşamadığı için **ortam** da değişiyor: o
farkın ölçümü §15.3'ün dördüncü maddesi, ve tutmazsa sonuç "yerelle
karşılaştırılamaz" diye etiketlenecek.

**Ek — 25 Eylül 2026: kilidin açılmasının onayı, nasıl alındığı ve ne zaman.**
Yukarıdaki metin değişmedi; değişen tek şey bu paragrafın var olması. Yerel
donanım kilidi **20 Ağustos 2026'da kullanıcının açık onayıyla** açıldı. Onay
konuşmada verildi ve o gün kayda girmedi; bugün, tarihiyle kayda geçiyor. Günü,
bu kararın yazıldığı günden alınıyor (commit `0c01f51`); konuşmanın kendisi
depoda yok.

**Ara durum neden yazılıyor.** Bir kilidin açılmasının gücü, onayın ne zaman ve
nasıl verildiğinde. "Onayla açıldı ve o gün yazıldı" ile "onayla açıldı, beş hafta
sonra yazıldı" aynı şey değil, ve ikincisini birincisi gibi göstermek ön kaydın
engellemek için var olduğu türden bir düzleştirme olurdu. Arada kararın metni
değişmedi; görünmez kalması onu doğrulanamaz kılardı. İlke, ön kayıt A.7'nin
"tetiğin onayı" paragrafıyla aynı.

**Ek — 25 Eylül 2026: `S-14` bu uzatmayı önceden yetkilendirmemişti.** Yukarıdaki
"`S-14` kuralı pilottan önce ilan etmişti: eksenin en küçük noktası taban etkisine
yapışırsa eksen yukarı kaydırılır" cümlesi aşırıydı ve silinmiyor. `S-14`'ün
pilottan önceki kuralı **aşağı** daralmaydı: "1,5B taban koşulunda çözüm
üretmiyorsa eksen 3B ve 7B'ye iner". Yukarı yol aynı kayıtta **açıkça kapalıydı**,
donanım yüzünden. Colab'ın GPU'su o engeli kaldırdı; ama engelin kalkması yukarı
uzatmayı kendiliğinden yetkilendirmiyor. Uzatma **sonradan alınmış bir karar**,
kullanıcının açık onayıyla (yukarıdaki ek). "Engel tasarım değil donanımdı"
cümlesi doğru; "kural o engel kalkarsa ne yapılacağını zaten söylüyordu" cümlesi
değil — kural bunu söylemiyordu.

### K-132 — Bir nöbetçiyi uydurma girdiyle sınamak, o girdiyi üreteni sınamıyor

**Karar.** Bir denetimin sınanması, denetimin okuduğu veriyi **üreten kodu da**
kapsıyor. Elle yazılmış bir girdi dosyasıyla yapılan sınama, yalnız "denetim bu
girdiye doğru tepki veriyor" der; "girdi doğru" demez.

**Gerekçe ölçüldü, ve arıza tam bu boşluktan geçti.**
`require_colab_environment.py` dört durumda yerelde sınanmıştı ve dördünde de
doğru davrandı — ama dört durum da **elle yazılmış JSON**'du. Denetimin gerçekte
okuduğu alanı üreten `residency()` hiç koşturulmadı, ve o fonksiyonun içinde
`vram_footprint`'in döndürmediği iki anahtar okunuyordu. Sonuç: alan **her
makinede, her model için, her koşulda** False. Nöbetçi kusursuz çalıştı; okuduğu
sayı hiçbir zaman ölçülmemişti.

**K-49'un tamamlayıcısı.** K-49 "yeşil bir denetim koştuğunun kanıtı değil"
diyor ve nöbetçinin ateşlendiğini görmeyi istiyor. Bu kayıt bir adım öteye
gidiyor: **ateşlenen nöbetçi, doğru sayıya bakarak mı ateşlendi.** Uydurma girdi
birinciyi kanıtlıyor, ikinciyi kanıtlamıyor.

**Uygulaması.** Üretici en az bir kez gerçek bir kaynağa karşı koşturuluyor ve
çıktısı gözle karşılaştırılıyor. Burada bu, yerel Ollama sunucusunu proje
ayarlarıyla ayağa kaldırıp `/api/ps`'in ham cevabını fonksiyonun döndürdüğüyle
yan yana basmak oldu: ham cevap `size == size_vram`, fonksiyon `fully_resident:
False`. Kusur bir bakışta görüldü.

**Sınırı.** Bir kez gerçek kaynağa karşı koşmak, kaynağın **bütün** biçimlerini
kapsamıyor. Ollama'nın alan adlarını değiştirdiği bir sürüm aynı sessiz sıfırı
yeniden üretir; onu yakalayan şey bu kural değil, `state` alanının
"belirlenemedi" diyebilmesi (K-131).

### K-131 — "Belirlenemedi" bir "hayır" değil

**Karar.** Bir ölçümün cevabı alınamadığında sonuç **yok** olarak raporlanıyor,
**olumsuz** olarak değil. Bir nöbetçi ikisinde de durabilir, ama **aynı cümleyi
kurmuyor**: biri "cevap eksik", öteki "cevap hayır".

**Gerekçe ölçüldü.** Colab ortam ölçümü `fully in VRAM: False`, `resident: None`
yazdı ve koruma bunu "yerleşik değil" diye okudu. `None` "belirlenemedi"
demekti. İki ayrı sebep aynı çıktıyı üretiyordu: model hiç yüklenmemişti (taze
bir çalışma zamanında `/api/ps` boş), ve `residency()` var olmayan iki anahtarı
okuyordu. İkisi de düzeltildi, ama asıl kusur **okuma**ydı: yokluk, olumsuzluğa
çevrildi.

**Bu depoda daha önce yazılmış bir hatanın aynısı.** `setting_flag` tam bunun
için var: okunamayan bir ayarı `0` diye künyeye yazmak, "flash attention
kapalıydı" demektir ve **makul** bir değer olduğu için hiçbir CHECK itiraz
edemez. Aynı kalıp bir kez daha, başka bir dosyada.

**Uygulaması.** `residency()` artık üç durum döndürüyor: `resident`, `partial`,
`undetermined`. Koruma üçünü de reddediyor ama `undetermined` için ayrı bir
cümle kuruyor ve ne yapılacağını söylüyor. Üç durum da gerçek bir ölçüme karşı
sınandı.

**Sınırı.** Kural yalnız **ayrımı** kuruyor. "Belirlenemedi" cevabının neden
alınamadığı hâlâ ayrı bir soru, ve onu yanıtlayan şey bu kural değil,
`require_server()`'ın dört sorusu.

### K-130 — Ön koşullar önden ve topluca soruluyor; arıza olmadan eksik kendini adlandırıyor

**Karar.** Bir zincirin herhangi bir adımı başlamadan önce, **kalan bütün
adımların** ön koşulları denetleniyor ve **eksiklerin hepsi birden**
raporlanıyor. Hiçbir denetim diğerini durdurmuyor.

**Gerekçe bir sayı.** Colab önyüklemesi beş turda beş ayrı eksik ön koşulda
düştü: jetonsuz klon, yukarı akış LFS bütçesi, boş veri önbelleği, yanlış Python
ortamı, `zstd`. Her tur bir sonrakini açığa çıkardı, ve her turun bedeli
kullanıcının döngüde beklemesi. Beşi de önden sorulabilir sorulardı. N adımlı
bir zincirde ön koşulları önden sormak **N turu bir tura indiriyor**.

**K-125'in önleyici hâli.** K-125 arızanın kendini adlandırmasını istiyordu:
çıkış kodu değil, aracın kendi cümlesi. Bu kayıt bir adım öncesini istiyor —
**arıza olmadan eksiğin kendini adlandırması**. İkisi aynı şeyin iki zamanı:
biri olan bitene isim veriyor, öteki olacak olana.

**Sıra ölçütü: ucuz ve kesin olan önce.** Denetim hiçbir şey kurmuyor ve hiçbir
şey başlatmıyor; yalnız soruyor. Bu yüzden en pahalı adımdan (dokuz gigabaytlık
model çekme) önce, en ucuz sorular (bir ikili PATH'te mi) sorulabiliyor.

**Kurulabilir olan arıza değil.** `zstd` yoksa ama `apt-get` varsa, denetim bunu
"kurulacak" diye raporluyor. Arıza, ikisinin birden olmaması. Yoksa denetim,
kendi betiğinin çözebileceği bir şeyi kullanıcıya havale ederdi.

**Ölçüm tahminin yerini alıyor.** Disk denetimi modelin boyutunu kestirmiyor,
Ollama kayıt defterine soruyor: `qwen2.5-coder:14b-instruct-q4_K_M` **8,99 GB**.
Bir ön koşul denetimi kendi eşiğini uydurursa, denetim değil bir tahmin olur.

**Sınırı, ve dürüst olan kısım.** Denetim yalnız **sorulabilen** soruları
soruyor. Sunucunun hücreler arası yaşayıp yaşamadığı, modelin çekilmesinin Drive
üzerinden ne kadar süreceği, ve koşunun oturum bütçesine sığıp sığmadığı bu
denetimin göremediği şeyler — çünkü hepsi ancak denendiğinde ortaya çıkıyor.
Onlar için kural değişmiyor: K-125, arıza kendini adlandırsın.

### K-129 — Bir paketin var olması, doğru ortamda var olması değil

**Karar.** Bir kurulumun hedef ortamı **adıyla veriliyor**, keşfe bırakılmıyor.
Ve kurulumdan sonra sorulan soru "paket kuruldu mu" değil, "**koşacak yorumlayıcı
onu içe aktarabiliyor mu**".

**Gerekçe ölçüldü, ve iki aday ölçümle ayrıldı.** Colab'da yansı tekerlekleri
kuruldu ve kullanılamadı: `uv pip install` `Using Python 3.12.13 environment at:
/usr` dedi, yani `appworld` sistem yorumlayıcısına gitti, geri kalan 110 paket
ise `.venv`'de kaldı. Sonuç, `/usr/local/bin/appworld` altında `munch`
bulunamaması. İki aday vardı — komutta venv hedeflemesinin olmaması, ya da aynı
turda eklenen `UV_NO_SYNC=1`'in ortam keşfini değiştirmesi — ve ikisi de yerelde
ayrıldı:

| Ölçüm | Seçilen ortam |
|---|---|
| Sade `uv pip install` (venv var) | `.venv` — doğru |
| `UV_NO_SYNC=1` ile | `.venv` — **değiştirmiyor** |
| `UV_SYSTEM_PYTHON=1` ile | `Using Python 3.12.3 environment at: /usr` |
| `UV_SYSTEM_PYTHON=1` + `--python .venv/bin/python` | `.venv` — doğru |
| `UV_SYSTEM_PYTHON=1` altında `uv run` | `.venv` — **etkilenmiyor** |

Yani `UV_NO_SYNC` suçsuz, `uv run` suçsuz, ve kusur tek bir satırda: hedefi
söylemeyen `uv pip install`. `UV_SYSTEM_PYTHON=1` bir Colab çalışma zamanının
normal hâli — çıplak bir `!uv pip install`'in defterde çalışmasını sağlayan şey
o. Yani ortam yanlış bir şey yapmıyor; biz hedefi söylemediğimiz için onun
varsayılanına düştük.

**K-127'nin kardeşi.** Orada soru kabın varlığı ile içeriğinin varlığı arasında
ayrılıyordu; burada **varlık ile erişilebilirlik** arasında. "Kuruldu" ve
"ihtiyaç duyulan yere kuruldu" iki ayrı soru, ve denetimimiz birincisini
sormuştu. Aynı aile: en ucuz test, en sık karşılaşılan arızayı göremeyen test.

**Uygulaması.** Kurulum `--python "$HERE/.venv/bin/python"` ile hedefleniyor.
Hemen ardından o yorumlayıcı doğrudan çağrılıp içe aktarma sınanıyor — `uv run`
ile değil, çünkü o noktada `UV_NO_SYNC` henüz konmamış durumda ve `uv run`
reddeden yukarı akış kaynağına geri döner. Ve önyükleme kendi yorumlayıcısını
günlüğe basıyor: hangi ortamda olduğunu sonradan yeniden kurmak gerekmiyor.

**Sınırı.** Bu kural yalnız **bizim çağırdığımız** kurulumları kapsıyor. Bir
aracın kendi içinde başlattığı bir kurulum, hedefini yine kendi keşfiyle seçer;
onu yakalayan şey bu kural değil, kurulumdan sonraki içe aktarma sınaması.

### K-128 — Koşmayan bir adım, geçen bir adım gibi görünmüyor; ve kuran adımlar denetleyenlerden önce koşuyor

**Karar.** İki parça, ikisi de aynı arızadan çıktı. **Bir betik öldüğünde hangi
adımda öldüğünü söylüyor.** Ve **ortamı kuran adımlar, ortamı denetleyen
adımlardan önce koşuyor**; denetim rapor veriyor, kurulumu engellemiyor.

**Gerekçe ölçüldü.** Colab önyüklemesi D adımında düştü. `set -e` betiği
sonlandırdı ve E, F, G — Drive veritabanı bağı, **Ollama kurulumu**, model
çekme — hiç koşmadı. Hiçbiri bir şey yazmadı, çünkü koşmayan kod konuşmuyor.
Çıktı durdu, ve **duran bir çıktı bitmiş bir çıktı gibi görünüyor**. Kullanıcı
tarafında sonuç şuydu: dört ayrı elle teşhis (ollama yok, model listesi boş,
süreç sayısı sıfır, port kapalı) ve hepsi tek bir gerçeği gösteriyordu — adım
hiç çağrılmamıştı.

**Sessizliğin bir kardeşi var: yanlış sıralama.** Portable önyükleme hem kuruyor
(LFS, bağımlılık, AppWorld, veri) hem denetliyor (ruff, build, testler, nöbetçi
taraması). Denetim kısmı çıkış kodunu belirlediği için, **yeni bir ortamda
anlaşmazlık çıkaran bir denetim modeli hiç kurdurmuyordu**. Oysa yeni bir ortam
tam olarak bir nöbetçinin anlaşmazlık çıkarması beklenen yerdir (K-117). Yani
yapı, kendi tasarımıyla çelişiyordu.

**Uygulaması.** `step()` adı bir değişkende tutuyor ve bir `ERR` tuzağı ölürken
onu basıyor: "şu adımda durdu, bundan sonraki hiçbir adım koşmadı". Çağıran
betik, çağırdığı betiğin çıkış kodunu kendi kapısı saymıyor; onun yerine
**kendi şartlarını adıyla sınıyor** (`appworld` içe aktarılıyor mu, `data/tasks`
var mı). Böylece bir denetim anlaşmazlığı raporlanıyor ama makineyi modelsiz
bırakmıyor.

**Sınırı.** Tuzak yalnız sıfırdan farklı bir çıkışı yakalıyor. Sessizce yanlış
iş yapıp sıfır dönen bir adım hâlâ görünmez; onu yakalayan şey bu kural değil,
sonraki adımın kendi şartını sınaması.

### K-127 — Bir kabın varlığı, içeriğinin varlığı değil

**Karar.** Bir dizinin, önbelleğin ya da deponun kullanılabilirliği **içindeki
beklenen şeyle** sınanıyor, kendi varlığıyla değil.

**Gerekçe ölçüldü, ve bir Colab turuna mal oldu.** Önyüklemenin veri adımı
`[ -d "$DATA_CACHE" ]` diye soruyordu: önbellek dizini var mı. Colab
önyüklemesi ise daha önceki bir adımda `mkdir -p "$DRIVE_ROOT/data"` yapıyor.
Yani soru **her zaman evet** cevabını alıyordu, dizin bomboş olsa bile. Sonuç
zinciri: boş dizin bağlandı, indirme atlandı, `[ -d "$HERE/data/tasks" ]`
düştü, ve arkasındaki her şey — Ollama dahil — hiç koşmadı (K-128).

**Neden yerel sınamada çıkmadı, ve bu K-122'nin kendi yazdığı sınır.** Adım
yerelde koşturuldu ve geçti, çünkü buradaki önbellek **doluydu**. K-122 kuralı
koyarken sınırını da yazmıştı: "yalnız fark edilen kolaylıkları söküyor". Dolu
bir önbellek fark edilmemiş bir kolaylıktı. Kural kendi kör noktasını önceden
tarif etmişti ve tam oradan vuruldu.

**Genel biçimi.** Kap ile içerik ayrı sorular: dizin var mı / aradığım dosya
içinde mi, tablo var mı / satır var mı, anahtar tanımlı mı / değeri boş değil
mi. Varlık testi ucuz olduğu için seçiliyor, ve boş bir kap onu her zaman
geçiyor — yani en ucuz test, en sık karşılaşılan arızayı göremeyen test.

**Sınırı.** İçerik testi de bir vekil. `data/tasks` dizininin var olması
verinin **doğru** veri olduğunu göstermiyor; yalnız boş olmadığını gösteriyor.
Bir sonraki katman künye (`appworld_commit`) ve özet karşılaştırması, ve o
katman K-126'da.

### K-126 — Yukarı akış erişilemez olduğunda depodaki yansıdan kuruluyor, ve yansı sessiz değil

**Karar.** Sabitlenen AppWorld commit'i yukarı akıştan kurulamadığında, aynı
commit'ten üretilmiş iki tekerlek `vendor/appworld/` altından kuruluyor. Yukarı
akış **her zaman önce** deneniyor; yansıya yalnız bilinen arıza imzasında
düşülüyor ve düşüldüğünde künye bunu taşıyor.

**Önce ölçüldü: PyPI kapalı çıktı.** İki ölçüm kararı tek başına verdi.
`appworld-agents` PyPI'da **yok** (HTTP 404) ve referans iskele (K-19) o
dağıtımın içinde — depoya `v0.1.3`'ten *sonra* girmiş. PyPI'daki en yüksek
sürüm `0.1.3.post1`, etiketin tarihi 2024-10-14, bizim sabitimizle arasında
**196 commit** var. Yükleme tarihinin 2026-02-17 görünmesi eski bir etiketin
yeniden yayımlanmasından; sürümü tarihe değil etikete bakarak ölçmek gerekiyordu.
Yani PyPI'ya geçmek 196 commit geri gitmek ve iskeleyi kaybetmek demekti.

**Yansının biçimi: iki tekerlek, Drive değil depo.** Kullanıcı Drive önerdi ve
gerekçesi sağlamdı: nesneler yerel makinede duruyor. Ölçüm başka bir yol açtı —
tekerlekler **toplam 1,18 MB**. Bu boyutta yansı depoya sığıyor, ve depoya
girince üç şey kazanıyor: commit kimliği (K-116'nın üzerine yazıldığı şey),
kullanıcı tarafında **sıfır elle adım**, ve klonlayan herkesin aynı baytları
alması. Drive'daki bir dosyanın commit kimliği yok ve elle kopyalanması
gerekiyordu.

**Aynılık iddia edilmiyor, ölçülüyor.** Bir bundle'ın sha256'sı onun Git LFS
nesne kimliğidir. `record_appworld_source.py` kurulu bundle'ları özetleyip
sabitlenen commit'in nesne kimlikleriyle karşılaştırıyor ve tutmazsa önyükleme
duruyor. Bu, yukarı akıştan kurulduğunda da koşuyor: aynı denetim iki yönde de
çalışıyor.

**Sessiz geri düşüş yasak.** Yansı kullanıldığında künyenin `os_environment`
alanı `appworld: mirror a072b7a86 (2026-08-20)` taşıyor. Sebep basit: ölçümün
hangi eserden çıktığı, ölçümün kendisi kadar kayıt konusu. Şema değişmedi, yeni
seri açılmadı — alan zaten serbest metin ve `resume_check` onu karşılaştırmıyor.

**Yalnız bilinen imza geri düşüyor.** `uv sync` başka bir sebeple düşerse yansı
devreye girmiyor, çünkü bir yansı o arızayı yutsaydı kimsenin sormadığı bir
soruyu cevaplamış olurdu (K-123).

**Mekanizmanın bir yan şartı ölçülerek bulundu.** `uv run` her çağrıdan önce
ortamı yeniden eşitliyor. Yani yansı kurulduktan sonraki ilk `uv run` yukarı akış
kaynağına dönüyor ve yeniden düşüyor — geri düşüş kuruluyor ve bir satır sonra
geri alınıyor. Bu ancak önyükleme temiz bir klonda gerçekten koşturulunca
görüldü; betiği okuyarak görünmüyordu. Çözüm `UV_NO_SYNC=1`, ve iki yolda da
konuyor: ikinci adımdan sonra ortam bilerek kurulmuş durumda, ve bir önyüklemenin
ortasında sessiz bir yeniden çözümleme yukarı akış yolunda da istenmiyor. Defter
onu çekirdek ortamına koyuyor, çünkü sonraki hücreler ayrı kabuklar.

**Sınırı.** Yansı tekrarlanabilirliği kurtarmıyor, güvenin adresini
değiştiriyor: yansıyı kullanan artık yukarı akışa değil bize güveniyor. Nesne
kimliklerinin doğru kimlikler olduğu, yukarı akış geri gelene kadar bizim
kaydımıza dayanıyor. Bu yüzden yansı geri düşüş; yukarı akış açıldığında
önyükleme kendiliğinden ona dönüyor ve geri alınacak bir şey yok
(`scripts/check_upstream_lfs.py` sorar).

### K-125 — Aynı çıkış kodunu veren birden çok sebep varsa, gösterilecek şey kod değil aracın kendi cümlesi

**Karar.** Bir dış araç çağrıldığında hata metni yakalanıp gösteriliyor. `check=True`
gibi yalnız çıkış kodunu yükselten biçimler, kodun tek bir sebebe karşılık geldiği
yerlerde kalıyor.

**Gerekçe ölçüldü.** Colab defterinin klon adımı `subprocess.run(..., check=True)`
ile koşuyordu. Düştü ve geriye yalnız `çıkış 128` kaldı. `git clone`'un dört ayrı
arızası aynı 128'i veriyor, ve dördü de yerelde boş bir ortamda üretildi: hedef
dizin boş değil, jeton geçersiz, dal yok, kimlik yok. Dördü **farklı** cümleler
yazıyor, ve kod hiçbirini ayırmıyor. Sebebi taşıyan tek şey yakalanmayan
`stderr`'dı, yani düzeltmenin yeri bir tur boyunca bilinemedi.

**Bir kural değil, bir hesap.** Yakalanan çıktı ekrana basılacaksa sır sızdırma
riski doğuyor; o yüzden gösterim öncesi maskeleme K-124'e bağlanıyor. İkisi
birlikte uygulanıyor: hata metni gösteriliyor **ve** içindeki sır siliniyor.

**Sınırı.** Kural aracın konuşmasını gerektiriyor. Hiçbir şey yazmadan düşen bir
araçta kod tek bilgi olarak kalıyor; o durumda gösterilen "araç hiçbir şey
yazmadı" cümlesi, boş bir satır değil.

### K-124 — Sır komut satırına girmiyor, çünkü hata izi komut satırını basıyor

**Karar.** Bir sır hiçbir zaman `argv`'ye ya da bir adresin içine konmuyor. Kimlik
bilgisi süreç ortamından okunuyor; git için bu `GIT_ASKPASS`, başka araçlar için
eşdeğeri.

**Gerekçe ölçüldü, ve bedeli bir jeton oldu.** Defterin klon adımı jetonu
`https://x-access-token:JETON@github.com/...` biçiminde adresin içinde
taşıyordu. Klon düştü, ve Python'un `CalledProcessError`'ı ileti metnine
`process.args`'ı koyuyor. Böylece jeton, tam metin hâlinde, bir hata izinin
içinde çalışma zamanından çıktı ve iptal edilmek zorunda kaldı.

**Sızdıran şey git değildi.** git kendi iletilerinde adresi maskeliyor: aynı
başarısız klon `fatal: Authentication failed for 'https://github.com/...'` yazıyor
ve jeton görünmüyor. Maskelemeyen taraf Python'du. Yani "araç sırrı gizler"
varsayımı, sırrı **araca veren** katman için geçerli değil.

**Ölçüldü.** `GIT_ASKPASS` ile geçersiz bir jeton, boş bir ortamda hem klonda hem
itmede denendi: git kimliği yardımcıdan aldı (hata `could not read Username`
değil `Invalid username or token`) ve sahte jeton hiçbir çıktıda geçmedi.

**Sınırı.** Jeton hâlâ süreç ortamında ve 0700 izinli geçici bir dosyada duruyor;
aynı kullanıcının bir süreci ikisini de okuyabilir. Kural sırrın **kayıt altına
alınan** yüzeylerden çıkmasını engelliyor — hata izleri, günlükler, yapıştırılan
çıktılar — makineyi paylaşan bir süreçten değil.

### K-123 — Bildirilen belirti ile ona iliştirilen sebep ayrı şeyler; damga yalnız belirtinin

**Karar.** Bir belirti başka birinden geldiğinde belgeye giren şey belirtidir.
Yanına konan sebep bir çıkarımdır ve öyle etiketleniyor. "Ölçüldü" damgası
yalnız bu deponun kendi ürettiği bir gözlemin üstüne basılıyor.

**Gerekçe, yanlış tarafından ölçüldü.** Colab'ın ilk denemesinde defter
GitHub'dan açılmadı ve 404 geldi; bu gözlemdi. Yanına bir sebep koydum —
"Colab'ın doğrudan bağlantısı özel depolarda çalışmıyor" — ve ikisini birlikte
README'ye **"Ölçüldü, ilk denemede çıktı"** diye yazdım. Belirti doğruydu, sebep
yanlıştı: 404'ün sebebi Colab'ın GitHub yetkilendirmesinin henüz tamamlanmamış
olmasıydı, ve tamamlanınca **aynı doğrudan bağlantı** açıldı.

**Yanlışı taşıyan şey damgaydı, cümle değil.** Sebep bir tahmin olarak yazılsaydı
tahmin gibi okunur ve ilk fırsatta sınanırdı. "Ölçüldü" yazılınca sınanacak bir
şey kalmadı: talimat çalışmayan bir yolu tek yol diye gösterdi ve çalışan yolu
yasakladı. Depo bu ayrımı sayılar için zaten yapıyor — §15.8 kestirimin yanına
"bu bir kestirim, ölçüm değil" yazıyor. Eksik olan, aynı ayrımın **düzyazıdaki
sebep cümlelerine** uygulanmasıydı.

**Uygulaması.** Erişilmeyen bir ortam hakkındaki her cümle üç etiketten birini
taşıyor: *gözlendi* (kim, ne zaman), *belgelenmiş davranış* (kaynağı olan),
*çıkarım* (sınanmamış). "Ölçüldü" yalnız birincisi için, ve yalnız ölçümü bu
depo yaptıysa. K-122 bir adımın hedef ortama gitmeden sınanmasını istiyor; bu
kayıt hiç sınanamayan kısmın nasıl yazılacağını söylüyor.

**Sınırı.** Kural etiketi düzeltiyor, çıkarımı doğrulamıyor. Doğru etiketlenmiş
bir çıkarım da yanlış olabilir; farkı yanlış olduğunda **ucuz** olması — sınanacak
bir aday gibi durur, kapanmış bir soru gibi değil.

### K-122 — Başka bir ortama gidecek bir adım, yerelde ortamın kolaylıkları söküldükten sonra sınanıyor

**Karar.** Bir adım başka bir ortamda koşacaksa ve o ortama özgü değilse, yerelde
sınanıyor — ama **yerel ortamın kolaylıkları kapatılarak**. Kimlik yardımcısı,
kurulu araç, tanımlı ortam değişkeni: hedef ortamda olmayan her şey sınama
sırasında da olmamalı.

**Gerekçe ölçüldü, ve kural olmadan sınama yanlış cevap veriyordu.** Colab
defterinin klonlama adımı özel depoyu jetonsuz klonluyordu ve orada düştü:
`fatal: could not read Username for 'https://github.com'`. Adım Colab'a özgü
değildi, yani yerelde sınanabilirdi. Sınandı ve **geçti** — çünkü bu makinede
`credential.https://github.com.helper` olarak `gh auth git-credential` tanımlı ve
git jetonu sessizce oradan aldı. Aynı klon `env -i HOME=/tmp/bosev` ile temiz bir
ortamda koşturulunca kullanıcının gördüğü hatanın **aynısını** verdi.

**Yani yanlış negatifi üreten şey sınamanın kendisiydi.** K-117 bir denetimin
cevabının ortama bağlı olmamasını istiyor; bu kayıt aynı şeyi bir katman
yukarıda, **sınamanın ortamına** uyguluyor. Yeşil bir yerel sınama, hedef ortamda
olmayan bir kolaylık sayesinde yeşilse hiçbir şey söylemiyor.

**Uygulaması.** Kimlik gerektiren bir adım `env -i` ile boş bir ortamda ve boş
bir `HOME` ile koşturuluyor. Jetonlu biçim de aynı temiz ortamda doğrulanıyor,
çünkü düzeltmenin çalıştığını göstermek de aynı kanıt standardını istiyor.

**Sınırı.** Kural yalnız **fark edilen** kolaylıkları söküyor. Hedef ortamda
olmayan ama yerelde farkına varılmamış bir şey yine yanlış negatif üretebilir; o
durumu yakalayan şey bu kural değil, hedef ortamda bir kez koşmak.

### K-121 — Kullanıcıya özgü yollar yapılandırmada, gerekçe gizlilik değil tekrarlanabilirlik

**Karar.** Kullanıcı adı ya da makineye özgü bir dizin taşıyan hiçbir yol koda
gömülü durmuyor. Depo kökü `__file__`'dan türetiliyor; makineye özgü olanlar
yapılandırmaya giriyor ve oradan okunuyor.

**Gerekçe.** `REPRODUCE.md` bir teslim maddesi ve talimat niteliğinde. İçinde ya
da dayandığı kodda `/home/yusuf/zihin` gibi bir yol varsa, o talimat **yazıldığı
makine dışında hiç kimse için doğru değil** — komut çalışır görünür ve başka bir
şeye bakar. Gizlilik bunun yan etkisi, sebebi değil; sebep talimatın başkası için
de doğru olması.

**Uygulaması.** `scripts/check_merged_artefacts.py` kökü artık türetiyor, ki
depodaki bütün diğer betiklerin zaten yaptığı şey buydu — o tek istisnaydı.
Sunucu günlüğünün yolu `config/models.yaml` içine `server_log` olarak girdi ve
`src/zihin/model_server.py` ile `scripts/measure_models.py` oradan okuyor. Değer
künyeye giren sunucu ayarlarının kaynağı (K-37), yani ölçüme giren bir değer;
yapılandırmada olması zaten kuraldı ve bu parametreye uygulanmamıştı.

**Sınırı.** Kural koda ve talimata uygulanıyor, **tarihsel raporlara değil**.
`docs/reports/kurulum-sonrasi-4.md` o gün o makinede ne yapıldığını anlatıyor ve
oradaki yol bir talimat değil bir kayıt; değiştirilirse kayıt yanlış olur.

### K-120 — Geçmiş yeniden yazılmıyor: ölçüm kişisel içerik olmadığını gösterdi

**Karar.** Depo geçmişi CV ya da kişisel içerik gerekçesiyle **yeniden
yazılmayacak**. Soru kapalı ve bu kayıt onu kapalı tutmak için var.

**Gerekçe ölçüldü.** Talimat kişisel içeriğin silinmesiydi. Ölçüm üç şey gösterdi:
bütün geçmişteki dosya adları tarandı ve **hiçbir commit'te CV dosyası yok**;
on üç kişisel terim bütün commit'lerin içeriğinde arandı ve tek eşleşme
("başvuruyor") "ajan tanımsız değişkene başvuruyor" cümlesindeki fiil çıktı;
altmış PR gövdesi ve issue listesi tarandı, sıfır eşleşme. Geçmişte duran şey
kişisel veri değil, **CV'nin bir yapılacak-iş satırı olarak adı** — dört commit
ve bir commit mesajı. Çalışma ağacındaki atıflar `aad6649` ile çıkarıldı.

**Neden yine de yapılmadı.** İki ayrı sebep, ikisi de ölçülmüş.

*Bedel.* `36d4393`'ün elli altı torunu var; yeniden yazma hepsinin SHA'sını
değiştirir. Depo kendi SHA'larına atıf veriyor — kapanış notları commit aralıkları
taşıyor, karar kayıtları `637c825` ve `09cbde6` gibi commit'leri adıyla anıyor.
İzlenebilirlik bu deponun bütün disiplini, ve yeniden yazma onu kırar.

*Etkisizlik.* Zorla itme GitHub'dan silmiyor. Erişilemez hâle gelen commit'ler
doğrudan SHA adresiyle açılmaya devam ediyor. "İz kalmasın" ancak GitHub'a purge
talebiyle ya da deponun silinip yeniden kurulmasıyla sağlanır, ve ikisi de bu
kararın konusu değil.

**Sınırı.** Karar **kişisel içerik bulunmadığı ölçümüne** dayanıyor. Depoya
gerçek kişisel veri girerse bu kayıt onu kapsamıyor; o durumda soru yeniden
açılır ve cevabı muhtemelen deponun yeniden kurulması olur.

### K-119 — Yarım kalan iş oturum sonunda dala commit'leniyor

**Karar.** Bir oturum sonunda tamamlanmamış iş `/tmp` altında ya da çalışma
dizininde bırakılmıyor; dala commit'leniyor. Depoya girmesi bir denetimi
yanıltacaksa, denetimin tanımadığı bir adla girer — çeviriler için `.en.partial.md`
soneki — ve o dosyanın durumu hiçbir ilan tablosunu değiştirmez.

**Gerekçe ölçüldü.** Bir önceki turda itilmemiş bir commit kayboldu ve PR onsuz
birleşti (K-116). Ertesi tur üç yüz yirmi beş satırlık yarım bir çeviri `/tmp`
altında bırakıldı: aynı sınıf maruziyet, üstelik bu sefer git bile araya
girmiyor.

**Neden yarım işi olduğu gibi commit'lemiyoruz.** Yarım bir çeviriyi
`setup-protocol.en.md` diye koymak eş denetimini kandırmak olur: `PENDING`
listesinde `.en.md` gören denetim "çeviri bitti, listeyi güncelle" der ve bitmemiş
bir işi bitmiş sayar. Sonek bu yüzden var — dayanıklılık ile dürüstlük arasında
seçim yapmayı gerektirmiyor.

**Neden üçüncü bir kategori açılmadı.** K-104'ün ölçütü uygulandı: bekleyen bir
adım — çevirinin bitmesi — uymamayı çözüyor, yani uymama geçici ve taksonomi
eksik değil (K-115'in dördüncü sınıfının aksine).

**Sınırı.** Kural işin **kaybolmamasını** sağlıyor, ilerlemesini değil. Bir dalda
duran yarım çeviri, bitirilmesi hatırlanmazsa yine bekler; onu tutan şey kuyruk
(`docs/reports/denetim-bosluk-raporu.md`), bu kural değil.

### K-118 — Kümeye bakmak üyeye bakmanın yerine geçmiyor

**Karar.** Bir korumanın kapsamı, korunanların **kümesi** üzerinden değil her
**üyesi** üzerinden ölçülüyor. "Koşucularda devam koruması var" biçiminde bir
cümle, koşucuların hepsinde olduğu anlamına gelmiyor ve öyle okunmuyor.

**Gerekçe ölçüldü.** Üç ölçüm koşucusundan `measure_band` devam korumasını
taşımıyordu, `measure_rule_off` ön kontrolü taşımıyordu, ve
`measure_boundary_control` ikisini de taşıyordu. Eksikler **birbirini
tamamlamıyordu**: kümeye bakınca her iki koruma da "koşucularda var" görünüyordu,
çünkü her koruma en az bir koşucuda vardı. Üyeye bakınca ikisi de delikti.

**Neden bu genel bir tuzak.** Bir kümede her özelliğin en az bir örneği varsa
küme özet olarak doğru görünüyor; yanlış olan şey özetin kendisi değil, özetin
üyeye dair bir şey söylediği varsayımı. Aynı yapı her "N şeyin hepsinde X var"
cümlesinde geçerli, ve doğrulaması N kez bakmayı gerektiriyor.

**Uygulaması.** `scripts/count_guards.py` üyeleri sayıyor, kümeyi değil; her satır
bir üye ve eksik nöbetçileri adıyla listeleniyor (K-115).

**Sınırı.** Üye başına bakmak, üye listesinin kendisinin tam olmasına bağlı.
Listeyi yapısal çıkarmak bu yüzden kuralın parçası; elle tutulan bir üye listesi
aynı tuzağı bir katman yukarı taşır.

### K-117 — Bir denetimin cevabı ortama bağlıysa denetim değil

**Karar.** Bir denetim aynı girdiye her ortamda aynı cevabı veriyor. Yerelde geçip
CI'da düşen — ya da tersi — bir denetim düzeltilmeden kullanılmıyor, çünkü hangi
cevabın doğru olduğu belirsiz.

**Gerekçe ölçüldü, aynı turda üç kez.**

1. Tanımlayıcı çözümlemesi `.venv` içindeki kurulu paketi de tarıyordu. Lint işi
   paketi kuruyor ama `appworld install` koşmuyor, yani uygulama modüllerindeki
   adlar yerelde çözülüyor CI'da çözülmüyordu. Çözüm kümesi kendi ağacımızla
   sınırlandı ve AppWorld tarafındaki on üç ad tek tek ilan edildi.
2. Karar CSV'si karşılaştırması satır sonuna bağlıydı: üreteç CRLF yazıyor, git
   commit edilen dosyayı LF'e normalleştiriyor. Yerel çalışma kopyası CRLF olduğu
   için eşitlik tutuyordu, CI checkout'unda tutmuyordu. Üreteç LF'e çekildi.
3. Daha önce aynı sınıf `sys.path` üzerinden ısırmıştı (S-49): `python -m pytest`
   çalışma dizinini ekliyor, `pytest` betiği eklemiyor.

**Neden bu bir denetim tanımı meselesi.** Ortama bağlı bir denetim iki cevap
üretiyor ve ikisi de kanıt sayılamıyor: yeşil olan "burada geçti" diyor, kırmızı
olan "orada düştü" diyor, ve hangisinin denetlenen şeye dair olduğu belli değil.
Belirsiz cevap veren bir ölçüm, ölçüm değil.

**Sınırı.** Kural farkın **görüldüğü** durumları kapsıyor. İki ortamda da aynı
yanlış cevabı veren bir denetim bu kuraldan geçer; onu yakalayan şey negatif test
(K-49) ve ölçekte sınama (K-113).

### K-116 — CI'ın yeşil olduğu değil, hangi commit'te yeşil olduğu doğrulanıyor

**Karar.** Bir değişikliğin CI'dan geçtiğini söylemeden önce, CI'ın koştuğu
commit'in **o değişikliği içerdiği** doğrulanıyor. Rengi okumak yetmiyor; koşunun
`headSha`'sı yerel commit ile karşılaştırılıyor.

**Gerekçe ölçüldü, ve maliyeti bir tur oldu.** Denetim süpürmesinin commit'i
(`7feb45c`) itilmedi. Hemen ardından CI sorgulandı, beş iş de yeşil göründü, ve
"birleşmeye hazır" diye raporlandı. Yeşil olan koşu **bir önceki commit'e** aitti.
PR birleşti, ve süpürmenin bütün içeriği — `--check` bayrağı, CI adımı, boşluk
raporu, K-113 ve K-114 — `main`'e hiç girmedi. Kayıp, yapısal sayım
`build_decisions_csv.py`'yi hâlâ nöbetçisiz gösterdiği için bulundu.

**Sınıfı tanıdık.** Yeşil bir kontrol, koştuğunun kanıtı değil (K-49); burada aynı
cümlenin bir katman yukarısı geçerli: yeşil bir CI, **senin değişikliğinde**
koştuğunun kanıtı değil. İki hâlde de doğrulama, doğrulamak istediğin şeye
bağlanmamıştı.

**Sınırı.** Kural itilmiş bir commit'i doğruluyor; itmenin kendisinin sessizce
başarısız olabilmesi ayrı bir şey ve onu yakalayan şey bu karşılaştırmanın
kendisi.

### K-115 — Koruma gerektiren türler sayılıyor, ilan edilen korumalar değil

**Karar.** Nöbetçi kapsamı **yapısal olarak** ölçülüyor: koruma gerektiren türler
adlandırılıyor, her türün her üyesi sayılıyor, ve her üyede nöbetçi var mı diye
bakılıyor (`scripts/count_guards.py`, CI'da). Üç tür: **üretilen görünümler**,
sonra **ölçüm koşucuları**, sonra **ayrıştırılan arayüzler**.

**Neden düzyazı taraması yetmiyor.** İlan edilen denetimleri tarayan süpürme
(K-114) yalnız *söylenen* ile *kurulan* arasındaki farkı görebiliyor. Hiç ilan
edilmemiş ama gerekli olan bir korumayı göremiyor — ve tam olarak o sınıf
kayboluyor. Bu yüzden o sayım bir **alt sınır**, bu sayım bir **üst sınır**.

**Gerekçe ölçüldü, ilk koşuda.** Düzyazı taraması üç ölçüm koşucusu tanıyordu.
Yapısal sayım **yedi** buldu: `measure_card_arms`, `measure_card_demo`,
`measure_context_cost` ve `measure_gpt4o_subset` hiçbir belgede denetimleriyle
anılmamıştı, dolayısıyla ilan taramasında görünmüyorlardı. Dördü de nöbetçisiz.

**Yaş sırası, önem sırası değil.** Korumalar dersler biriktikçe eklendi, yani en
önce kurulan şey en az korumaya sahip: koruma ondan **sonra** icat edildi.
`experiments/decisions.csv` üretilen görünümlerin en eskisiydi ve tek nöbetçisi
olmayanı çıktı; tesadüf değil, şeklin kendisi. Sonraki süpürmeler yaş sırasına
göre yapılıyor.

**Bilinen çıplaklar ilan ediliyor.** `ACCEPTED` listesi bugünkü yedi çıplak bölgeyi
gerekçesiyle taşıyor. Listede olmayan çıplak bir bölge kontrolü düşürüyor, ve
listede olup artık korunan bir bölge de düşürüyor — bayat bir muafiyet, muafiyet
sayılmıyor. Liste olmasaydı kontrol ilk koşusunda kırmızı yanar ve kapatılırdı;
kapalı bir kontrol hiç olmayandan kötü.

**Sınırı.** Sayım nöbetçinin **varlığını** ölçüyor, doğruluğunu değil. Hiçbir şeyi
karşılaştırmayan bir `--check` buradan geçer — bunun bir kez olduğu kayıtlı
(K-106) — ve onu yalnız negatif bir test yakalıyor.

### K-114 — Bir denetimden söz ederken soru "şartnamede var mı" değil "bağlı mı"

**Karar.** Bir denetimin varlığı, onu ilan eden cümleyle değil, çağrıldığı yerle
kanıtlanıyor. Belgede bir denetimden geniş zamanda söz eden her cümlenin arkasında
CI'da, `local_checks.sh` içinde ya da bir koşucunun ön kontrolünde bir çağrı
olmak zorunda; yoksa cümle geçmiş zamana çekiliyor ya da denetim yazılıyor.

**Alt desen: tasarım ifadesini uygulama iddiası sanmak.** İki dilli dalganın
tasarımı "CI üç denetim: eş var mı, ikisi aynı commit'te mi değişti, kaynak
commit güncel mi" diyordu. Cümle bir **tasarım ifadesiydi** — ne yapılacağını
söylüyordu — ve sonradan bir **uygulama iddiası** gibi okundu. Ölçüldü: yalnız
birincisi kuruldu, ve kalan ikisinin dayandığı alan dokuz çevirinin sıfırında
var. Aynı desen bu depoda **yedi kez** tekrarlandı ve hizalama denetiminin
merkezî bulgusunun aynısı.

**Gerekçe ölçüldü: bir süpürme yapıldı.** Protokol ve tasarım belgelerinde ilan
edilen her denetim, CI ve `local_checks.sh` içinde gerçekten bağlı olanlara karşı
tarandı (`docs/reports/denetim-bosluk-raporu.md`). On iki ilan bağlı çıktı,
**beşi bağlı değil.** En ağırı: `experiments/decisions.csv` üretilen görünümlerin
en eskisiydi ve **hiçbir bayatlık nöbetçisi yoktu** — ne CI'da ne yerel
betikte — oysa tam bu arıza iki kez gerçekleşmişti (S-33'te 68 satır kaybı,
K-103'te otuz sessizce yanlış gerekçe). `--check` eklendi ve CI'a bağlandı.

**Sınırı.** Süpürmenin ilan tarafı düzyazı okunarak çıkarıldı; bir denetimden söz
etmenin sabit bir biçimi yok. Yani beş sayısı bir **alt sınır**, ve bu kural
gelecekteki ilanları da ancak biri okuyup soruyu sorarsa yakalıyor.

### K-113 — Bir denetim ölçekte de sınanıyor, ve sessiz arıza biçimi adlandırılıyor

**Karar.** Yeni bir denetim yalnız küçük bir örnekle değil, koruyacağı **gerçek
boyuttaki** girdiyle sınanıyor. Ayrıca denetimin sessiz arıza biçimi — yanlış
pozitif mi, yanlış negatif mi — yazılıyor, çünkü ikisi farklı şeyler gizliyor.

**Gerekçe ölçüldü.** Çeviri çapası denetimi sekiz belgede kuruldu, dördü gerçek
dört uyuşmazlık buldu, ve doğru çalışıyor göründü. İki bin satırlık bir belgeye
uygulanınca **iki kusuru çıktı**, ikisi de küçük girdide görünmüyordu:

1. Satır sonuna bölünmüş bir ters tırnak çifti (`` `appworld\ninstall` ``) regexe
   uymuyordu, ve uymadığı yerde **yanlış ters tırnakları eşleyip** düzyazıyı kod
   sanıyordu.
2. Üçlü ters tırnaklı bloklar da ters tırnakla sınırlı olduğu için kapanış çiti
   sonraki satır içi ters tırnakla eşleşiyordu.

**Sessiz arıza biçimi burada yanlış negatifti.** İkisi de hiçbir şey söylemeden
kaçırıyordu; denetim yeşil kalıyordu ve yeşil "kontrol edildi" diye okunuyordu.
Yanlış pozitif gürültülüdür ve kendini bildirir; yanlış negatif tam da korumaya
çalıştığın şeyi geçirir.

**Neden ölçek bir eksen.** İki kusur da girdi uzunluğuyla ortaya çıktı: uzun
belgede satır kaydırma daha sık, ve çitli blok daha olası. Küçük örnek denetimin
mantığını sınıyor, boyut denetimin **varsayımlarını** sınıyor.

**Sınırı.** Kural ölçeği bir eksen olarak ekliyor, bütün eksenleri değil. Bir
denetim, hiç görmediği bir içerik biçimiyle karşılaşınca yine kaçırabilir; ölçek
yalnız en ucuz sınanan eksen.

### K-112 — Denetlenecek alan yoksa denetim atlamıyor, düşüyor

**Karar.** Bir denetimin dayandığı alan — dosya, alan adı, bölüm — bulunmadığında
denetim sessizce geçmiyor; **düşüyor**. "Bakacak bir şey yoktu" bir başarı değil,
denetimin kendi ön koşulunun karşılanmadığının bildirimi.

**Gerekçe ölçüldü.** Belge eş denetimi üç kategoriyle kuruldu ve üçüne de girmeyen
bir belgenin kontrolü düşürmesi bilerek yazılmıştı. Aynı ilke aynı dosyanın başka
bir yerinde uygulanmamıştı: çapa denetimi, ikili beyan edilmiş bir belgenin
dosyalarından biri yoksa `continue` ediyordu. O dalda denetim hiçbir şey söylemeden
yeşil kalıyor.

**İkinci ve daha ağır örnek.** İki dilli dalganın tasarımı üç CI denetimi ilan
etmişti: eş var mı, ikisi aynı commit'te mi değişti, kaynak commit güncel mi.
Ölçüldü: **yalnız birincisi kuruldu.** İkincisi ve üçüncüsü hiç yazılmadı, ve
dayandıkları alan — her `.en.md` başlığındaki kaynak commit'i — sekiz çevirinin
sıfırında var. Yani ilan edilen denetim yokluğuyla değil, sessizliğiyle geçiyordu.

**Ayrım.** Kurulmamış bir denetim ile boşlukta geçen bir denetim aynı şey değil.
Birincisi eksik iş, ikincisi yanlış sinyal. Bu karar ikincisini yasaklıyor;
birincisini yakalayan şey ilan ile kodun karşılaştırılması, ve o karşılaştırma
bu turda elle yapıldı.

**Sınırı.** Kural yalnız **yazılmış** denetimlere uygulanıyor. Hiç yazılmamış bir
denetim hiçbir dalda düşmüyor, çünkü ortada dal yok.

### K-111 — Çeviri çapaları sayıyla karşılaştırılıyor, kümeyle değil

**Karar.** Bir kaynak belge ile çevirisi arasında değişmemesi gereken dizeler —
ters tırnak içindeki her şey, kayıt kimlikleri (`S-36`, `K-107`), çıplak dosya
yolları — **çokluk kümesi** olarak karşılaştırılıyor. Dil eki taşıyan çapraz
atıflar `.md`'ye katlanıyor, çünkü değişmesi gereken tek çapa o.

**Genel ilke.** Nicelik "kaç kez geçiyor" olduğunda küme karşılaştırması kaybı
**sessizce kabul eder**. `S-05`'i dört kez anan bir belgenin çevirisinde iki kez
geçmesi iki atıf kaybı; küme iki tarafta da `S-05` görür ve eşit der. Aynı şey
her yerde geçerli: bir projeksiyon "hangi değerler var" diye soruyorsa, "kaç
tane" sorusunun cevabını kaybediyor demektir.

**Gerekçe ölçüldü.** Mekanik çeviri bu depoda üç kez gömülü bir adı düşürdü.
Sonuncusu `scripts/check_language.py` içinde "It writes the map into , so the
strings it emits are that document's text" satırını bir dalga boyunca ayakta
tuttu ve gözle bulundu. Denetim kurulur kurulmaz sekiz belgede 208 çapa saydı ve
dördü uyuşmadı; ikisi ters tırnağını kaybetmiş tanımlayıcıydı (`pop`, `connect`).

**Bulunan asıl şey yön ihlaliydi.** `05-experiment-design`'ın İngilizcesi,
Türkçe kaynağında **hiç olmayan** bir paragraf taşıyordu. Eş denetimi varlığı ve
birlikte değişmeyi denetliyordu, **yönü** denetlemiyordu; kaynak-türev ilişkisi
ihlal edilmiş ve hiçbir şey ses çıkarmamıştı.

**Sınırı.** Çapa denetimi yönü yalnız **eklenen içerik çapa taşıyorsa** yakalıyor.
O paragraf `(K-104)` yazdığı için görüldü; çapasız düzyazı — hiçbir kimlik, yol
ya da ters tırnak içermeyen bir cümle — iki tarafta da sayısız kalır ve sızar.
Yönü tam denetlemek için gereken şey başka: her çevirinin kaynağının hangi
sürümünden yapıldığını taşıması, ve o sürümün güncelliğinin ölçülmesi (K-112'de
ölçülen eksik).

### K-110 — Kapanış artığı ya kayda dönüşüyor ya da kayda gerek olmadığı yazılıyor

**Karar.** Bir sınırlama kapatılırken yazılan **neyin kapanmadığı** paragrafında
adı geçen her artık iki yoldan birine giriyor: ya kendi açık kaydına dönüşüyor,
ya da o paragrafta artığın kayda değmediği **açıkça** yazılıyor ve sebebi
veriliyor. Üçüncü seçenek — artığı adlandırıp orada bırakmak — kapalı.

**Gerekçe ölçüldü.** `S-36` kapatılırken artık adıyla yazılmıştı: *kayıtta hiç
görülmemiş bir yol/yöntem çifti sınanmadı.* Sunum iskeletiyle sınırlama
haritasının çapraz kontrolü, `3.4` numaralı iddianın ("vekilin ürettiği kimlik
kayıtlı kimlikle aynı") **sıfır sınırlaması** olduğunu gösterdi. Yani artık
görünür kılınmış, sonra hiçbir açık kayda geçmemişti. Kapanış notu kapalı bir
kaydın gövdesinde duruyor ve kapalı kayıtlar haritada eksen taşımıyor; orada
kalan bir artık aranan yerde yok.

**Neden yarısı tamamından kötü.** Aşırı kapatmama disiplini artığı bilerek
görünür kılıyor. Görünür kılıp taşımamak, hiç yazmamaktan daha yanıltıcı: belge
artığın bilindiğini gösteriyor, ve bilinen bir artığın takip edildiği varsayılıyor.
İkinci adım atılmazsa disiplin kendi kanıtını üretip yok ediyor.

**Uygulaması ve sırası.** Kural bugünden itibaren yazılan her kapanış için
geçerli. On altı mevcut kapanışın geriye dönük taraması **çeviriden sonraya**
bırakıldı; çünkü tarama yeni kayıtlar üretebilir ve `docs/09-limitations` şu anda
çeviri kuyruğunda. Aynı kuyrukta bekleyen iki iş daha var: çapraz kontrolün yedi
aday sınırlaması, ve ters yöndeki beş kayıt.

**Sınırı.** Kural artığın **adlandırılmış** olmasına dayanıyor. Kapanış notu
artığı hiç yazmazsa bu kural ateşlemiyor; o durumu yakalayan şey kuralın kendisi
değil, kapanış ölçütünün üç parçalı yazımı.

### K-109 — Her açık sınırlama kapanma sınıfını taşıyor, ve ölçüt işin kimin elinde olduğu

**Karar.** `docs/09-limitations` içindeki her **açık** kayıt, eksen işaretinin
altında bir kapanma sınıfı taşıyor. Dört sınıf: **Dış olgu** (yukarı akış,
donanım ya da K-19 ile dondurulmuş iskele), **Ölçüldü** (soru soruldu, cevap
geldi, cevabın kendisi kısıt), **Sonraki tur** (planlanmış bir ölçüm ya da yapım
kapatabilir), **Kalıcı kayıt** (kendi tarihimizde olmuş, hiçbir iş geri almaz).
Harita sınıfı bir sütun olarak basıyor ve sınıfsız açık kayıt kontrolü düşürüyor.

**İşlemsel test.** Tek soru: *bu kaydı kapatacak iş kimin elinde?* Sınıf, kaydın
konusuna değil kapanma yoluna bakıyor. Bu ayrım gerekli, çünkü bir kayıt hem
ölçüm sonucu hem de kapanabilir olabiliyor; sınıfı belirleyen ikincisi.

**Gerekçe.** Kapanma turunda otuz üç madde üç ölçütle süpürüldü ve sonuç PR
gövdesinde üç sınıf hâlinde raporlandı. Rapor kapanınca o değerlendirme
kaybolacaktı: belge tarafında otuz dokuz madde düz liste olarak duruyor ve düz
liste "otuz dokuz çözülmemiş sorun" diye okunuyor. Sınıflarıyla okununca doğru
cümle çıkıyor: kaç madde bulgunun kendisi, kaç madde sonraki tura bağlı. Üçüncü
sınıfın sayısı **belgenin ne kadarının geçici olduğunu** veriyor; bugün otuz
dokuzun on yedisi.

**K-104 bir kez daha ateşledi.** Süpürme üç sınıf ilan etmişti ve on beş kayıt
üzerinden örneklenmişti. Ölçüt otuz dokuzun tamamına uygulandığında iki kayıt
(`S-23`, `S-24`) üçüne de uymadı: kendi geçmişimizde olmuş, geri alınamaz
olaylar. Dördüncü sınıf o yüzden var — önceden değil, ölçüt tam geçişte
uygulandığı için.

**Örnekleme ile tam geçişin farkı, ikinci kanıt.** Aynı desen çapraz kontrolde
de çıktı: sunum iddialarının sınırlamalarla birleştirilmesi beklenmeyen bir grup
üretti — kendisi zaten sınırlama olan iddialar (bölüm 6). İki turda da yeni sınıf
**tam geçişte** göründü, örneklemede değil. Örnekleme beklenen sınıfları
doğruluyor; beklenmeyeni yalnız tam geçiş veriyor. Bir sınıflandırmanın örnekle
kurulup tamamına uygulanmadan raporlanması bu yüzden eksik sayılıyor.

**Sınırı.** Sınıf bir yargı, ölçüm değil. "Sonraki tur" bir kaydın kapanacağını
değil kapanma yolunun bizde olduğunu söylüyor; o turun koşulmaması sınıfı
yanlışlamıyor, yalnız geçici kısmı geçici bırakıyor.

### K-108 — Türetilmiş bir görünümün şekli, girdilerinin üzerinde bir kontroldür

**Karar.** Bir projeksiyon üretilirken, aynı veriye **ikinci bir yönden** bakan
bir görünüm de üretiliyor. İkinci görünümün şekli birincinin girdileri üzerinde
bir denetim sayılıyor.

**Gerekçe ölçüldü.** Sınırlama haritası önce sınırlama anahtarlıydı: her kaydın
hangi iddiayı kısıtladığı. İddia anahtarlı ters görünüm üretilince bir
tutarsızlık göründü: `S-16`'nın işareti `07-failure-taxonomy ve üç kapılı suç
atfı` diye yazılmıştı ve zaten var olan bir iddia için **ikinci bir anahtar**
üretiyordu. Birinci yönde bu görünmüyordu — orada her satır kendi başına
doğruydu. İkinci yönde iki satır aynı yere düşmesi gerekirken düşmedi.

**Neden bu genel bir ilke.** Bir görünüm veriyi gruplandırıyorsa, gruplamanın
kendisi girdilerin tutarlı adlandırıldığını varsayıyor. Varsayım tutmazsa
görünümün **şekli** bozuluyor: beklenenden çok anahtar, tek elemanlı gruplar,
ya da aynı şeyin iki adı. Bu bozulma girdiye bakarak değil çıktıya bakarak
görünüyor.

**Uygulaması.** `scripts/build_limitations_index.py` iki tabloyu birden basıyor.
Bundan sonra bir projeksiyon eklenirken ikinci yön de soruluyor; yoksa gerekçesi
yazılıyor.

**Sınırı.** İkinci yön yalnız **gruplama tutarsızlığını** gösteriyor. Bir
girdinin yanlış ama tutarlı adlandırılması iki yönde de doğru görünür.

### K-107 — Her sınırlama bir iddia eksenine yerleşiyor, ve ölçüt iddianın adı

**Karar.** `docs/09-limitations` içindeki her açık kayıt iki sınıftan birine
giriyor. **İddiayı sınırlıyor:** pilot raporunda, sunumda ya da karar kaydında
söylenen bir şeyi kısıtlıyor. **Kapsam:** yapılmamış ya da ulaşılmamış bir alanı
kaydediyor, o alanda bir iddia olmadığı için hiçbir şeyi kısıtlamıyor.

**İşlemsel test.** Bir maddeyi "iddiayı sınırlıyor" saymak için **sınırladığı
iddia adıyla yazılıyor**. Ad verilemiyorsa madde kapsamdır. Sınıflandırmayı
iddiaya bağlamak tahmine bağlamaktan iyi, ve yan ürünü sunumun ihtiyaç duyduğu
şey: iddia → sınırlama haritası.

**K-104 burada da geçerli.** İkisine de uymayan bir madde **sınıflandırılmadan**,
sebebiyle raporlanıyor. Zorlanmıyor.

**İkinci doğruluk kaynağı üretilmiyor.** Eksen, kaydın başlığının altındaki ilk
alıntı satırından okunuyor — `> **İddiayı sınırlıyor.** <iddia>`,
`> **Kapsam.** <ne kaydettiği>`, `> **Sınıflandırılmadı.** <sebep>`. Harita bu
satırı okuyor; elle tutulan bir kopya yok ve `--check` ayrışmayı yakalıyor.

**Kapanmış kaydın ekseni sorulmuyor.** Kapanmış bir sınırlama hiçbir şeyi
kısıtlamıyor, o yüzden sütunda eksik değil tire duruyor.

**Ölçülen ilk dağılım.** 46 açık maddenin 34'ü bir iddiayı sınırlıyor, 6'sı
kapsam, 6'sı sınıflandırılmadı. Sınıflandırılmayanların hepsi aynı sınıftan:
düzeltilmiş bir arıza kaydının bugünkü rolü — sınırladığı bir iddia mı, yoksa
kapanmış bir olay mı — bu turda karara bağlanmadı.

### K-106 — Hiçbir şeyi değiştirmeyen bir düzenleme arızadır; biçimlendirici dize eşleşmelerini bayatlatır

**Karar.** Dize eşleşmeli düzenlemeler iki kurala bağlı.

1. **Bir düzenleme başarı bildirip hiçbir şeyi değiştirmediyse arızadır.** Eşleşme
   tutmadıysa betik durmalı, sessizce geçmemeli.
2. **Bir biçimlendirici koştuktan sonra, ondan önce yazılmış dize eşleşmeleri
   bayattır.** Yeniden ölçülmeden kullanılamaz.

**Gerekçe ölçüldü.** `readme_problems` fonksiyonu yazıldı, `check_docs_parity.py`
içine kondu, ve `main` içinden çağrılması için bir `replace` yazıldı. Arada
`ruff format` koştu ve hedef satırı yeniden biçimlendirdi; `replace` artık
eşleşmiyordu, `assert` yoktu, ve betik "tamam" yazıp çıktı. Denetim yeşil
koşuyordu ve README'yi hiç denetlemiyordu.

**Bu K-49'un bir alt deseni.** K-49 "yeşil yanmak doğru sebeple yanmanın kanıtı
değil" diyor. Buradaki alt desen daha dar ve daha sinsi: yeşil yanan şey hiç
koşmamış olabiliyor, ve koşmadığını gösteren tek şey negatif test.

**Uygulaması.** Depodaki düzenleme betikleri `if old not in t: raise` deseni
taşıyor; bu madde o deseni istisnasız hâle getiriyor. Bir denetim eklendiğinde
ateşlerken görülmeden birleştirilmiyor — üç durumun ikisi kırmızı, biri yeşil
olacak biçimde ölçülüyor.

**Sınırı.** Kural düzenlemenin doğru yeri değiştirdiğini garanti etmiyor, yalnız
bir yeri değiştirdiğini garanti ediyor. Yanlış ama var olan bir eşleşmeyi
yakalamıyor.

### K-105 — Belgelerde tek adlandırma şeması, ve README'nin ayrı ele alınışı

**Karar.** `docs/` altındaki her belge `NN-ingilizce-kebab.tr.md` (Türkçe kaynak)
ve `NN-ingilizce-kebab.en.md` (İngilizce çeviri) biçiminde. Kök İngilizce ve
kebab-case, numara öneki korunuyor, dil son sonek. Şema
`scripts/check_docs_parity.py` ile denetleniyor ve denetim CI'ın Lint işinde
koşuyor.

**Gerekçe.** Dosya adı da bir tanımlayıcı ve bu depoda tanımlayıcılar İngilizce
(K-102). `sandbox-kapsami.en.md` — Türkçe bir kökün altında İngilizce bir çeviri —
tam olarak üç oturum boyunca koddan temizlenen karışık hâlin kendisiydi.
Danışmanın açacağı dizinde o istisnanın kalmaması için `12-sandbox-kapsami`
yeniden adlandırıldı; atıf taraması tek dosyalıktı ve ucuzdu.

**Neden yarım göç edilmedi.** İki adlandırma kuralı aynı anda yürürlükte olsaydı
eş denetimi temiz açılamaz ve okuyan iki kural öğrenmek zorunda kalırdı. Bu
yüzden adlandırma göçü tek turda bütün dizine uygulandı; çeviri ise ayrı bir
eksen ve dalgalar hâlinde ilerliyor.

**Üç kategori, ve her biri bir konum.** Denetim `BILINGUAL` (çevirisi var ve
denetleniyor), `PENDING` (çeviri borcu var, dalgası yazılı) ve `TURKISH_ONLY`
(çevirisi olmayacak, sebebi yazılı) ayrımını taşıyor. Üçüne de girmeyen bir belge
denetimi düşürüyor: "unuttuk" ile "karar verdik" birbirine benzemesin diye.

**README ayrı ele alınıyor, ve şemanın tersine.** `README.md` depo kökünde ve
adını platform koyuyor; GitHub yalnız o adı işliyor. Karar: **`README.md`
İngilizce ön kapı, `README.tr.md` Türkçe kaynak**, ikisinin başında karşılıklı dil
bağlantısı.

**Gerekçe.** README depo sayfasında ilk görünen şey ve dışarıdan gelen okur onu
görüyor. Danışmanın İngilizce isteği ile yayın ihtimali birlikte düşünülünce ön
kapının İngilizce olması yerinde.

**Kanonik ad kaynağın adı** ilkesi bu tek dosyada bozuluyor ve bozulması
kasıtlı. O ilkenin amacı dar: **ayrıştırılan ya da atıf verilen** bir belgede
hangi yarının yetkili olduğu belli olsun. README ne ayrıştırılıyor ne atıf
alıyor, yani ilkenin koruduğu şey burada risk altında değil.

**Bedeli.** Depoda tek bir istisna var ve okuyanın onu öğrenmesi gerekiyor. Bedel
`scripts/check_docs_parity.py` içindeki `readme_problems` ile karşılanıyor: kural
kodda yazılı, iki yarının varlığı ve karşılıklı bağlantısı denetleniyor, yani
istisna sessiz kalmıyor.

### K-104 — Her önceden ilan tablosunun bir "hiçbirine uymuyor" dalı var

**Karar.** Sonuç görülmeden yazılan her yorum tablosu açık bir dördüncü dal
taşıyor: gözlenen desen satırların hiçbirine uymuyorsa tablo yanlıştı, sonuç
yorumsuz raporlanır, ve tablonun neyi kaçırdığı yazılır. Kural
`experiments/setup-protocol.tr.md` §13'te.

**Gerekçe.** Üç kollu kart koşusunun yorum tablosu üç satır taşıyordu: alakasız
kol kartlıya yakın, kartsıza yakın, ya da arada. Ölçülen desen dördüncüydü —
alakasız kol her ikisinin de altında (3/15, karşısında 7/15 ve 6/15). Üç satır
yazmak sonuç uzayının kapsandığını varsaymak demek, ve kapsanmadığında sonucu
satırlardan birine zorlamaya davet ediyor.

**Neden sonradan satır eklenmiyor.** Sonuç görüldükten sonra tabloya bir satır
eklemek ön kaydın işlevini bitirir: yorum o noktada veriye bakılarak seçilmiş
olur. Dördüncü dal bu yüzden bir yorum üretmiyor, yorumu durduruyor.

**Uymama iki türlü, ve yalnız biri kategori gerektiriyor.** Dal ateşlediğinde
sorulan soru şu: **bekleyen bir adım bu uymamayı çözüyor mu.**

*Geçici uymama.* Sınırlama belgesinde altı kayıt iddia eksenine
sınıflandırılamamıştı. Uymamanın sebebi taksonomi değil kayıtların bayatlığıydı,
ve bekleyen adım — kapanma turu — onu çözecekti. Üçüncü bir eksen kategorisi
**eklenmedi**, ve tur koşulduğunda altısı da kapandı; kategori eklenseydi bugün
boş dururdu.

*Yapısal uymama.* Kapanma sınıfında iki kayıt (`S-23`, `S-24`) üç sınıfın hiçbirine
uymadı, ve hiçbir bekleyen adım onlara dokunmuyor: kendi geçmişimizde olmuş,
geri alınamaz olaylar. Burada taksonomi gerçekten eksikti ve dördüncü sınıf
açıldı (K-109).

Yani K-104 "asla kategori ekleme" demiyor. Uymamayı sonuca zorlamayı yasaklıyor,
ve kategori eklemeyi tek bir koşula bağlıyor: bekleyen hiçbir adım uymamayı
çözmüyorsa taksonomi eksiktir.

**Sınırı.** Dal, tablonun eksikliğini önceden görmeyi sağlamıyor; yalnız eksiklik
ortaya çıktığında sonucun sessizce bir satıra sığdırılmasını engelliyor.

### K-103 — Karar girdilerinin başlık kümesi şemaya karşı doğrulanıyor

**Karar.** `experiments/decisions.csv` üretilmeden önce iki denetim koşuyor.
Birincisi eskiden beri var: her kimlik CSV'ye ulaşmış mı (varlık). İkincisi yeni:
her karar girdisinin başlık kümesi beklenen şemaya uyuyor mu (yapı). Şema iki
kural taşıyor — her `K-` girdisi ilk sözcüğü `Karar` olan bir başlık taşıyacak,
ve yapısal bir kökün üstüne düşen (diakritikler kalkınca aynı harfleri veren) ama
o kök gibi yazılmamış hiçbir başlık olmayacak. Ayrıca gerekçe başlığı tek bir
dizge olarak değil **aile** olarak ayrıştırılıyor: `Gerekçe` ve `Sebep` ile
başlayan her başlık bir gerekçe açıyor.

**Gerekçe.** K-102 yazılırken başlık `**Gerekçe ölçüldü.**` kondu; ayrıştırıcı
`**Gerekçe.**` dizgesinde bölüyordu, bölme tutmadı, ve CSV gerekçe özeti olarak
"Karar." taşıdı. Testler yeşildi, betik hata vermedi. Varlık denetimi kimliği
gördü, içeriğine bakmadı. Tek bir başlığı özel olarak denetlemek aynı sınıfın
ikinci örneğini kaçırırdı, o yüzden denetim başlık kümesinin tamamına konuldu.

**Ölçüm.** Aile ayrıştırması kurulunca on yedi kaydın gerekçe özeti düzeldi;
hepsi "Karar." yazıyordu. Sonra geri düşüş kuralı düzeltilince (ilk başlığı atla)
on üç kayıt daha düzeldi. Yani sessiz yanlış satır sınıfı K-102'ye özgü değildi,
kayıtta otuz örneği vardı ve hiçbir şey itiraz etmemişti.

**Sınırı.** Şema yapısal sözcük dağarcığını kısıtlıyor, düzyazıyı değil. Hiç
görülmemiş bir sözcükle başlayan anlamlı bir başlık yakalanmıyor; belgede böyle
başlıklar var ve olmaları gerekiyor. Yakalanan şey kökün yanlış yazılması ve
karar başlığının hiç olmaması. Kural üçe kaydedilmiş istisna taşıyor (K-53,
K-84, K-85): sessizce eklenebilen bir istisna istisna değil, delik olurdu.

### K-102 — PR raporu yeni modül adlarını ve public tanımlayıcıları listeliyor

**Karar.** Her PR raporu, o PR'da **eklenen** modül dosyası adlarını ve yeni
public tanımlayıcıları (sınıf, fonksiyon, sabit) ayrı bir bölümde listeliyor.
Liste boşsa "yok" yazılıyor; bölüm atlanmıyor.

**Gerekçe.** Dil kuralı tanımlayıcıların İngilizce olmasını istiyor ve
kural yeniden adlandırma turundan önce kondu. Ama ileriye dönük uygulanmadı: madde
8 (sandbox) `kayit_vekili.py`, `konteyner_girisi.py`, `soket_koprusu.py`
modüllerini ve `SahteHata`, `SahteDunya`, `gorulen`, `beklenen` tanımlayıcılarını
üretti. Kural vardı, yeni kod eski varsayılana döndü ve arada hiçbir şey itiraz
etmedi.

**Neden rapor, neden diff değil.** İnceleme diff üzerinden değil rapor üzerinden
yapılıyor. Raporda görünmeyen bir şey uygulanamaz; kuralın yaşayabileceği tek yer
orası.

**ASCII denetimi işe yaramaz ve denenmedi.** `kayit_vekili` zaten ASCII. Bir
tanımlayıcının hangi dilde olduğu makineyle ucuza belirlenemiyor, o yüzden
denetim otomatik değil: rapor listeyi getiriyor, kuralı okuyan uyguluyor.

**Sınırı.** Bu bir koruma değil bir görünürlük kuralı. Yanlış adı engellemiyor,
gözden kaçmasını engelliyor. Otomatik bir denetim yazılırsa bu madde onun yerine
geçer.

### K-101 — Aile taraması iptal; ölçüm silinmiyor

**Karar.** Model ailesinin değiştirilmesi işi kapatıldı. Qwen3.5, Qwen3 ve
Falcon3 adaylarının taranması yapılmayacak; eksen Qwen2.5-Coder olarak kalıyor.

**Gerekçe.** Aile kilidi sınır kontrolünden sonra yeniden açılmıştı: düzenek
doğrulandı, sıfırlar modelden geliyordu, ve daha yeni bir aile aynı boyutta daha
yetenekli olabilirdi. Kullanıcı aileyi değiştirmeme kararı verdi; bu bir kapsam
kararı, ölçüme dayanan bir bulgu değil.

**Yapılmış ölçüm siliniyor değil, taşınıyor.** `docs/reports/model-ailesi-taramasi.md`
(76 satır) yalnız `origin/model-ailesi` dalında duruyordu ve main'de yoktu. main'e
alınıyor, başına iptal notu düşülerek. Ölçüm bir karar iptal edildi diye
geçersizleşmiyor; iptal edilen karara ait olduğunu söylemek yeterli.

**Kayıt yeri.** Bu madde ajan görev listesinde bir izleyici olarak duruyordu.
Görev listesi oturumla sıfırlanıyor; bir kapsam kararının orada durması, kararın
kaybolması demek.

### K-100 — CI `appworld install` ve veriyi kuruyor; bedeli ölçüldü

**Karar.** CI iki test işinde de `appworld install` ve `appworld download data`
koşuyor, veri dizini önbelleğe alınıyor, ve `appworld` işareti artık elenmiyor.

**Gerekçe.** S-49'da kırk beş testin CI'da hiç koşmadığı ortaya çıkmıştı ve
çözüm testleri işaretleyip elemekti — yani gereksinimi görünür kıldı ama
kapsamayı kapatmadı. Yedi kapanış notunun "temiz kurulumda baştan çalıştırıldı"
satırı bu yüzden eksik kalıyordu.

**Bedeli ölçüldü ve bilerek ödendi** (`results/ci-kapsam.json`):

| | Önce | Sonra |
|---|---|---|
| Testler: geçen | 356 | **435** |
| Testler: atlanan | 47 | **7** |
| Testler: elenen | 58 | 19 |
| Sandbox: geçen | 9 | **11** |
| Testler işi | 53 s | 53 s |
| Sandbox işi | 66 s | 92 s |
| Duvar saati (en uzun iş) | 66 s | **92 s** |

Kurulum adımı 9,6 s. Testler işinin süresi değişmedi çünkü pytest adımı 33,0
s'den 17,3 s'ye indi; bu beklenmedik ve tek koşudan, koşucu değişkenliği
olabilir. Toplam bedel 26 saniye.

**Kurulumun başarılı olması yetmiyor, koştuğu doğrulanıyor.** İşaretler ya da
kancalar hâlâ dışlıyorsa kurulum boşa gider ve bunu hiçbir şey söylemez. Ayrı
bir adım üç şeyi denetliyor: "uygulama modülleri yok" gerekçesiyle atlanan test
kaldı mı, `appworld` işaretli testler toplanıyor mu, ve rota tablosu kuruluyor
mu. Ölçülen: sıfır atlama, 12 uygulama.

**Kalan yedi atlama yapısal.** Üçü de `results/` ya da `experiments/outputs/`
altındaki üretilmiş artefaktlara bağlı; ikisi de gitignore'da, çünkü kod ile
sonuç aynı commit'i paylaşmıyor. Bu atlamalar tasarımın sonucu.

**Simülasyon da değişti.** `ci_simulasyonu.sh` artık uygulama modüllerinin
yokluğunu taklit etmiyor: olmayan bir makineyi taklit etmek yanlış kırmızı
üretirdi. Kalan iki fark taklit ediliyor — temiz checkout ve `pytest` betiğinin
sys.path'i.

### K-99 — Test işaretleri bağımlılığa göre, ve CI simülasyonu standart ön kontrolün parçası

**Karar.** İki kural, ikisi de `experiments/setup-protocol.tr.md` §6'da:

1. Bir testin işaretleri konusuna göre değil **bağımlılıklarına** göre
   belirlenir.
2. Bir arızayı yakalamak için kurulan kontrol depoya girer ve standart ön
   kontrolden çağrılır; geçici kurulup silinen kontrol kurulmamış sayılır.

**Gerekçe: aynı yerde iki kez tökezledik.** S-49'da kırk beş test CI'da kırıldı
çünkü gereksinimleri işaretlerinde yazmıyordu; o turda CI ortamını yerelde
yeniden üreten bir simülasyon elle kuruldu, işe yaradı ve **silindi**. Madde
8'de iki sandbox testi aynı sınıftan bir sebeple kırmızı yandı: görev verisi
okuyorlardı ama "sandbox hakkında" oldukları için yalnız `sandbox` işareti
taşıyorlardı. Simülasyon depoda olsaydı push'tan önce görülecekti.

**Simülasyon üç farkı taklit ediyor**, üçü de ölçülmüş arızalardan geliyor:
`data/` yok, uygulama modülleri yok (`appworld install` koşmamış),
ve `pytest` betiği çağrılıyor (`python -m pytest` değil, sys.path farkı).

**Kontrolün kendisi ateşlediği görülerek kabul edildi.** İlk hâli çalışma
dizinini `HEAD`'den kuruyordu ve commit edilmemiş değişikliği görmüyordu: işareti
kaldırıp koştuğumda yeşil yandı. Çalışma ağacından kurulan hâliyle aynı deneme
kırmızı yanıyor. Kontrolün doğru şeye baktığı, bakmadığı hâl gösterilerek
sınandı.

### K-98 — Bir koşu, başlattığı şeyle konuştuğunu doğrulamadan sayılmaz

**Karar.** Koşu başında, başlatılan sürecin kimliği teyit ediliyor. Sandbox'ta
ölçüt `SO_PEERCRED`: ortam soketinin karşı tarafındaki pid ile
`podman inspect .State.Pid` eşleşmezse koşu düşüyor.

**Gerekçe — üç kez aynı sınıftan arıza.** Artakalan bir durum üç kez yanlış yeşil
üretti: mutasyon betiği kirli zeminde koştu, doğrulama aleti bayat dosya okudu,
ve madde 8'de konteyner hiç başlamadığı hâlde epizot artakalan bir ortam
sunucusuna koşup temiz göründü. Üçünün ortak yanı, aracın "cevap aldım" ile
"doğru şeyden cevap aldım" arasındaki farkı sormaması.

**Ölçüt neden `SO_PEERCRED`.** Unix soketin TCP'de olmayan bilgisi ve ölçüldü:
karşı tarafın pid'i konteynerin pid'iyle birebir eşleşiyor. Nonce da olurdu ama
okunması için fazladan bir `execute` çağrısı gerekirdi ve o çağrı şeffaflık
testinin karşılaştırdığı metni kirletirdi.

**Kaydın tarafında da bir hâli var.** Vekil uygulama çağrısı gördüğü hâlde tek
adım kaydedilmemişse kaydedici takılmamış demektir; koşu epizot satırını yazmadan
düşüyor. Bu da ölçülmüş bir arızadan geliyor (S-53).

### K-97 — Sandbox güvenlik testleri beşinci CI kontrolü, mevcut test işinin içine girmiyorlar

**Karar.** Altı güvenlik testi kendi CI işinde koşuyor. "Dört CI kontrolü her
PR'da yeşil" cümlesi betimleyici bir kayıttı, korunacak bir kısıt değil.

**Gerekçe.** İki sebep. Podman testleri imaj çekiyor ve konteyner ayağa
kaldırıyor, yani mevcut test işini uzatır. Daha önemlisi: bir düşüşün nereden
geldiği belirsizleşir. Ayrı iş, kırmızı yandığında hangi katmanın kırıldığını
adıyla söylüyor.

**Koşabildiği ölçüldü.** GitHub `ubuntu-24.04` koşucusunda podman 5.8.4 kurulu,
kök yetkisiz, cgroup v2, crun. Salt okunur kök, kök yetkisiz eşleme, pids
sınırı, bellek sınırı, tmpfs sınırı ve epizotlar arası kirlenme korumalarının
altısı da **ateşlerken** görüldü. Yani S-49'un "temiz kurulumda yeniden
çalıştırıldı" boşluğu bu eksende büyümüyor.

**Ölçümün kendisi bir K-49 örneği.** Birinci turda üç adım yeşil yandı ve
hiçbir şey kanıtlamıyordu: bellek testi `/dev/shm`in kendi 64 MiB varsayılanına
çarpmıştı, tmpfs adımının çıkış kodu `dd`den değil `tail`den geliyordu, loopback
adımında host'ta hiçbir şey dinlemiyordu. Üçü düzeltildi ve bellek testine
sınırsız bir kontrol kolu eklendi.

### K-96 — Şeffaflık testi üç kollu, referansı tekrar kararlılığı ölçülmüş bir epizot

**Karar.** Üç kol: süreç içi, sunulan kip vekilsiz, sunulan kip vekilli.
Referans epizot `6104387_1`.

**Gerekçe — neden üç kol.** İki değişiklik aynı anda iniyor: taşıma katmanı
süreç içi ASGI'den gerçek HTTP'ye geçiyor, ve araya vekil giriyor. Tek testte
birleştirilirse çıkan fark atfedilemez hâle gelir. "Doğrudan" bu yüzden
"sunulan kip, vekil yok" demek.

**Gerekçe — neden bu epizot.** Demonun aynı yörünge üreten iki epizodu 0 ve 2
çağrı taşıyor; sıfır çağrı vekili hiç sınamaz, iki çağrı neredeyse hiç. Ayrıca
demonun `identical_trajectory` alanı kartlı kol ile taban kolun aynı çıktığını
söylüyor, **tekrar kararlılığını söylemiyor** — ikisi ayrı şey ve şeffaflık testi
ikincisine dayanıyor. `6104387_1` altı tekrarda tek yörünge veriyor ve 20 çağrı
taşıyor, hepsi 200.

**Araç zaten var.** Yörünge özeti `scripts/check_determinism.py` içindeki
tanımın aynısı: `sha256(logs/environment_io.md)`. Ajanın gördüğü metnin tamamı o
dosyada.

### K-95 — Konteynerin tek kanalı salt okunur bağlanan bir unix soket; yönetim rotaları vekilde yapısal olarak kesiliyor

**Karar.** Ağ kipi `--network=none`. Konteyner vekile, host'ta duran bir unix
sokete bağlanarak ulaşıyor; soket dizini **salt okunur** bağlanıyor ve
konteynerin içinde soketi yerel bir TCP portuna bağlayan bir köprü koşuyor.
Ayrıca vekil, API sunucusunun yirmi bir yönetim rotasını sabit bir beyaz listeyle
kesiyor.

**Gerekçe — ağ.** Şart şu: konteyner tam olarak tek host portuna ulaşsın. Dört
kip ölçüldü ve üçü şartı karşılamıyor:

| Kip | Dış ağ | Host portu | Soket köprüsü |
|---|---|---|---|
| `--network=none` | erişilemez | erişilemez | **çalışıyor** |
| varsayılan (netavark) | **erişilebilir** | erişilemez | çalışıyor |
| `slirp4netns:allow_host_loopback` | **erişilebilir** | 10.0.2.2 üzerinden açık | çalışıyor |
| `pasta` | **erişilebilir** | erişilemez | çalışıyor |

Dış ağa erişim üç kipte de gerçek: 1.1.1.1'e yapılan istek 403 dönüyor, yani
istek internete çıkıyor. Yalnız `none` `Network unreachable` veriyor. Ek olarak
`slirp4netns` GitHub koşucusunda kurulu değil, yani o kip her iki yerde
kullanılamaz.

**Soketin salt okunur bağlanabildiği ölçüldü.** Unix sokete `connect` yazma izni
istiyor ve salt okunur bağlamanın onu kesmesi bekleniyordu. Kesmiyor: `ro`
bağlamada da bağlantı kuruldu ve köprü üzerinden host 200 döndü. Yani "tek
kanal" şartı ile "yazılabilir bağlama yok" kuralı çakışmıyor. Varsayım değil,
`scripts/setup/measure_container_network.py` çıktısı.

**Köprü neden gerekiyor.** Referansın `Requester`ı `requests` ile konuşuyor ve
`requests` yalnız TCP biliyor. `--network=none` altında `lo` arayüzü ayakta
kalıyor, yani konteyner içinde bir TCP dinleyicisi çalışıyor. Köprü stdlib ile
yazılıyor: imajda Python zaten var, yeni bağımlılık eklenmiyor.

**Gerekçe — beyaz liste.** `appworld serve apis` on iki uygulamayı `/{app}`
altına bağlıyor, ama kökte kendi yönetim rotaları da var: `POST /dbs/save`
gönderilen yola veritabanı yazıyor ve **yazan süreç host tarafındaki API
sunucusu**. `POST /seed`, `POST /date_time` ve `POST /activate/task/{id}` de
doğrudan ölçümü bozuyor. Konteynerin içindeki kod bu rotalara `apis.*` ile aynı
kanaldan ulaşabilir; salt okunur kök ve ağ yalıtımı durdurmaz, çünkü yazan süreç
konteynerin içinde değil.

**Beyaz liste kalkanın yüklemi değil, ondan ayrı bir katman.** Kalkan görev
kapsamlı izin veriyor: hangi uygulamaya yazılabilir. Beyaz liste hangi rotaların
**var olduğunu** belirliyor. Referans ajan `apis.*` üzerinden yönetim rotalarına
ulaşamıyor, yani onları kesmek meşru bir yörüngeyi değiştiremez — ama bu bir
iddia ve testi var (§8'in yedinci testi).

**Sunucuların bağlanma adresi bizim elimizde değil.** `uvicorn.run(host="0.0.0.0")`
`appworld/serve/apis.py:31` ve `environment.py:301` içinde gömülü, bayrağı yok.
S-47'nin sorusu burada da geçerli ve cevabı tersi: bu değer referansın.

### K-94 — Günlükler epizot sonunda `podman cp` ile alınıyor, yazılabilir bağlama yok

**Karar.** `environment_io.md` ve `api_calls.jsonl` konteynerin içinde yazılıyor
ve epizot bittikten sonra `podman cp` ile alınıyor. Konteyner dosya sistemi koşu
boyunca salt okunur kalıyor.

**Gerekçe.** AppWorld'ün kendi docker tasarımı `experiments/outputs` dizinini
yazılabilir bağlıyor. O dizin doğrulayıcının okuduğu veritabanlarını da taşıyor,
yani yazılabilir bağlama birinci tehdidin tam yüzeyi: ajanın kodu kendi
değerlendirmesini yazabilir hâle gelir. Kopyalama epizot bittikten sonra
olduğu için o pencere hiç açılmıyor.

**Verdict taşınmıyor.** Ölçüldü: `verdict()` host tarafında `evaluate_dataset` ile
koşuyor ve okuduğu çıktı veritabanlarını host tarafındaki API sunucusu yazıyor
(`POST /dbs/save`). Konteynere taşınan şey yalnız iki günlük dosyası.

### K-93 — Sunulan kipte durum sondası HTTP üzerinden yapılıyor, iki ölçütlü kural korunuyor

**Bağlam.** Sunulan kipte `world.models` `None` oluyor, `state_probe.snapshot`
`{}` dönüyor ve `diff({}, {})` de `{}` dönüyor — `None` değil. Bu depoda `{}`
"ölçüldü, değişmedi" demek, yani sonda açık kalırsa kayıt her adımda ölçüm
yaptığını iddia eder ve hiçbir ölçüm olmaz.

**Karar.** Sonda kapatılmıyor, taşınıyor. `POST /dbs/save` çağrısı
`format="changes"` ve `save_model_hashes=True` ile adım sınırında yapılıyor;
`model_hashes.json` hangi modellerin değiştiğini söylüyor. Durma kuralı iki
ölçütlü kalıyor.

**Dört şey ölçüldü, hepsi kararın şartı:**

1. **Aynı ayrım gücü.** Dosya `{"spotify": {"MusicPlayer": 1}}` biçiminde, yani
   bugünkü sondayla aynı `app.Model` düzeyinde.
2. **Daha duyarlı.** Bugünkü sonda satır sayısı okuyor ve satır sayısını
   değiştirmeyen bir `PATCH`i göremiyor — kendi belgesinin yazdığı sınır.
   `set_volume` tam öyle bir çağrı ve HTTP sondası onu gördü.
3. **Ucuz.** Çağrı başına 2,0–2,5 ms, adım süresi ~2,2 s. Binde bir.
4. **Epizodun kendi kaydını bozmuyor.** Risk şuydu: değişiklik kaydını tüketirse
   kapanışta yazılan `model_hashes.json` eksik kalır ve doğrulayıcının
   `models.changed_model_names()` testi yanlış düşer. Sondalı ve sondasız iki
   koşunun geçen ve düşen test kümeleri birebir aynı çıktı.

**Semantik farkı yeni bir kolona giriyor.** Bugünkü `steps.state_change` işaretli
satır sayısı farkı taşıyor (`+1`, `-1`); özet tabanlı sonda "hangi model
değişti" taşıyor. Aynı kolona iki anlam koymak bu deponun kaçınmaya çalıştığı
sessiz yalanın kendisi, o yüzden ikinci bir kolon açılıyor ve süreç içi kipte
`state_change`, sunulan kipte yeni kolon doluyor; diğeri `NULL` kalıyor.

**Sonda kapatılsaydı ne kaybedilirdi, ölçüldü.** 4102 adımda durum ölçütü durma
kuralının kararını **bir kez bile** değiştirmemiş: yalnız durum sayesinde
duraklama sayılmayan adım sayısı sıfır. Yani kapatma seçeneği de savunulabilirdi
ve bu sayı iki seçeneğin eşdeğerliğinin dayanağı. Taşıma seçildi çünkü bedeli
binde bir ve kazandığı şey `PATCH` duyarlılığı.

### K-92 — Vekil parametre tipini AppWorld'ün kendi rota imzasından türetiyor

**Bağlam.** Vekil çağrıyı telde görüyor ve telde tür yok:
`requests.get(url, params={"page_index": 0})` sorgu dizesine `page_index=0`
yazıyor ve `0` orada metin. Durma kuralının gördüğü kimlik o sözlüğün JSON'u.

**Karar.** Tür rotanın kendi imzasından türetiliyor. Çeviriyi yapan şey bizim
yazdığımız bir tablo değil, sunucunun kendi kullandığı `ModelField.validate`.

**Gerekçe.** K-63'ün tekniğinin aynısı, yalnız yol parametresi yerine sorgu
parametresine uygulanmış hâli: orada `path_regex` yolu çözüyor, burada rotanın
alanları değeri çeviriyor. Diğer iki seçenek reddedildi: metin olarak kaydetmek
madenlenmiş her şeyle karşılaştırılabilirliği kırıyor, argüman sözlüğünü
konteyner içinde yakalamak ise kaydın bir parçasını güvenilmez bölgeye koyuyor —
küçük hâli bile aynı tehdit.

**Doğrulandı, ve doğrulamanın kontrol kolu var.** `scripts/setup/verify_wire_identity.py`
kayıttaki 5261 eylemin hepsini telden geçirip geri kuruyor:

| Kol | Kayıtlı kimlikle eşleşen |
|---|---|
| İmzadan tür türetilerek | **5261 / 5261** |
| İmzaya bakmadan (kontrol) | 4171 / 5261 |

İmzasız kolda 1090 eylem eşleşmiyor ve bu sayı bağımsız olarak ölçülen "metin
olmayan değer taşıyan GET eylemi" sayısıyla aynı. Kontrol kolu olmadan tam
eşleşme hiçbir şey kanıtlamazdı: ölçümün yeşil yanması, imzanın bir işe
yaradığının kanıtı değil (K-49).

**Doğrulama bir ayrıntı buldu.** `page_limit` alanı `int` ama üstünde `le=20`
kısıtı var; ajanın 50 yazdığı iki çağrıda doğrulama düşüyor ve değer geri
gelmiyordu. Aradığımız şey geçerlilik değil tür, o yüzden kısıt düştüğünde
doğrudan bildirilen türe çevriliyor. Kısıt sunucunun işi ve sunucu onu kendisi
uyguluyor; o iki çağrı zaten 401 ile reddedilmişti.

### K-91 — Demoda ayrıştırma ile kullanma ayrı ölçülüyor, ve kullanım ölçümü eşleştirilmiş taban gerektiriyor

**Karar.** Uçtan uca demo iki ayrı ölçüm yapıyor ve ikisi ayrı raporlanıyor:
kart bağlama **girdi mi**, ve modelin ürettiği çağrı karttaki diziyle **eşleşiyor
mu**.

**Gerekçe.** Model kartı ayrıştırabilir ve yine de yok sayabilir. "Demo çalıştı"
cümlesi ikisini karıştırır ve karıştığı yerde mekanizmanın davranışa ulaştığı
sanılır. Giriş ölçümü mekanik ve modele hiç bakmıyor; kullanım ölçümü modele
bakıyor.

**Kullanım ölçümü eşleştirilmiş taban olmadan geçersiz.** Kütüphanedeki dört
becerinin dördü de giriş, ve model giriş çağrılarını kartsız da yapıyor.
Eşleşmeyi tek başına "kart kullanıldı" diye okumak, kartın hiç etkisi olmadığı
hâlde olumlu sonuç üretirdi. Bu yüzden her görev kartlı ve kartsız iki kez
koşuyor: aynı seed, aynı model, aynı soğuk rejim.

**Eşleşme, kartın üretildiği boşluk kısıtıyla aranıyor** (boşluk 2, K-81). Daha
gevşek bir arama kartla ilgisi olmayan bir diziyi de eşleşme sayardı; daha sıkı
bir arama kartın kendi tanımından daha katı olurdu.

**Yörüngelerin birebir aynı çıkması bir sonuç, arıza değil.** O hâlde kart girdi
ve hiçbir şey değiştirmedi demektir, ve bu pilotun mekanizma koşullarının bu
modelde taban koşulundan ayrışmayacağını önceden söyler. Dört sonucun yorumu
`experiments/preregistration.md` içinde, koşudan önce yazıldı.

**Kart bulunamayan görevde kartlı koşu başlamıyor.** Boş slotla koşan bir epizot
kayıtta `library_id` taşırdı ve kartlı görünürdü; kartsız koştuğu yalnız prompt
dosyasından anlaşılırdı. Yürütücü bu durumda çıkıyor.

### K-90 — Karakter tavanı bizim parametremiz: künyeye giriyor, montajcının bütçesi karakterle yazılıyor

**Bağlam.** S-47 bağlayıcı bağlam sınırının jeton penceresi değil iskelenin
karakter tavanı olduğunu gösterdi. Sonraki soru şu: bu tavan yapılandırılabilir
mi, yoksa gömülü ajan mantığı mı? Cevap ölçümün değil kaynağın okunmasıyla geldi.

**Ölçülen olgu.** Tavan ajanın **kurucu parametresi**
(`SimplifiedReActCodeAgent(max_prompt_length=...)`) ve varsayılanı `None`, yani
"kesme yok". Kesme **mantığı** iskelenin içinde (`truncate_input`) ve ona
dokunulmuyor; tavanın **değeri** çağıranın.

Referansın bu ajan için verdiği değer: `null`. Depoda yayımlanan 108
`simplified_react_code_agent` yapılandırmasının **108'i** tavanı `null`
bırakıyor. 50000 değeri legacy `plan_execute` ailesinin 18 config'inden geliyor,
yani başka bir ajanın ayarı.

**Bizim 50000 değeri 10 Ağustos'ta yürütücüye girdi ve bir karar kaydı yoktu.**
Bağladığı da ölçüldü: kayıtlı 105 epizodun **31'i** tavanı geçti, en erken 9.
adımda, medyan 19. adımda. Yani korpusun üçte birinde geçmişin başı atıldı ve bu
hiçbir yerde yazılı değildi.

**Karar üç parçalı.**

**1. Tavan taşıma katmanı sayılıyor, `num_ctx` gibi.** Yapılandırılabilir olduğu
için değeri bizim; `config/recording.yaml` içinde `max_prompt_characters` olarak
duruyor ve ajana geçen sayı ile künyeye giren sayı tek kaynaktan okunuyor. Değer
şimdilik **değişmedi**: 50000 kalıyor, çünkü sayının ne olacağı ölçüm kararı ve
bu commit yalnız kaydı kuruyor.

**2. Künyeye giriyor ve devam denetiminin reddet listesinde.** `max_output_tokens`
ile aynı sınıf: koşu ortasında değişirse epizotların yarısı başka bir bağlam
uzunluğuyla koşar ve fark yalnız künyeden okunabilir. NULL "kaydedilmedi" demek
ve eski satırlar için doğru olan da bu — künye yalnız ekleme kabul ediyor, yani
geçmişe sayı yazılamaz. `-1` "tavan yok" demek.

**3. Bağlam montajcısı bütçesini karakterle yazacak.** Bağlayıcı birim o. Jetonla
yazan bir montajcı hiç ulaşamayacağı bir sınırı hedefler: pencerenin %39'unda
duran bir tavan varken 32K'ya göre planlamak, bütçenin %61'ini var sanmak olur.

**Bilinen bir yan etki.** `scripts/measure_models.py` künye sözleşmesini zaten
sağlamıyordu (`max_output_tokens` hiç geçmiyor) ve iptal edilen aile taramasının
aracı. Yeni zorunlu alan onu da kapsıyor; betik koşulursa `RecordError` ile
düşüyor, sessizce eksik künye yazmıyor.

### K-89 — Pilotun sayıları tek veri dosyasında, rapor ona atıf veriyor

**Karar.** Mekanizma pilotunun bütün ölçümleri `results/pilot-dataset.json`
içinde, makine okunur. Rapor sayıyı kopyalamıyor, dosyaya atıf veriyor; manşet
sayıları düzyazıda geçiyor ama tablolar ve ızgaralar veri setinde duruyor.

**Gerekçe.** Sayılar sekiz ayrı ölçüm çıktısında, sekiz ayrı günde üretildi. Bu
depoda tam bu arıza bir kez oldu: yazma kümesi tek günde iki kez değişti ve aynı
ölçüm iki farklı sayı verdi. Kopyalayan bir rapor denetlenemez; atıf veren bir
rapor denetlenebilir.

**Veri seti kaynaklarıyla birlikte kurulmuyorsa kurulmuyor.** `build_pilot_dataset.py`
eksik girdiyle çıkıyor, her girdinin sha256'sını yazıyor, ve üç ölçümün
bildirdiği `library_id`/`index_id` ayrışırsa duruyor. İkinci kontrol asıl olan:
farklı kütüphanelerden gelen sayılar tek sonuç gibi okunurdu.

### K-88 — Bağlam maliyeti ölçüldü; bağlayıcı sınır jeton penceresi değil, iskelenin karakter tavanı

**Karar.** Bağlam montajcısının girdisi olan üç sayı ölçüldü ve
`03-architecture.tr.md`'deki ölçülmemiş iddia düzeltildi.

**Ölçüm** (`results/context-cost.json`, üretim yolu bir dünya açılarak
doğrulandı):

| | Değer | Pencerenin payı |
|---|---|---|
| Sabit blok, medyan | **3172–3185 jeton** | %9,7 |
| Kart bloğu, k=5+5 medyan | 125 (train/dev) – 264 (test_normal) | %0,4–0,8 |
| Kartlarla toplam, medyan | 3296–3447 | %10,1–10,5 |
| Kartlarla toplam, en çok | 3645 | %11,1 |

**Mimari belgesi "beşte biri, kartlarla dörtte biri" diyordu ve yanlıştı.**
Doğrusu onda biri, kartlarla yine onda biri. Yanlışın kaynağı bir birim
karışması: Aşama 2'nin 5958 sayısı **adım başına girdi jetonu**, yani birikmiş
geçmişi de içeriyor; sabit blok o sayının yarısından küçük. Belge düzeltildi
(S-46).

**Bağlayıcı sınır pencere değil.** Referans iskele bağlamı **karakterle**
kesiyor: `max_prompt_length` 50000 ve kesme iskelenin içinde (S-07, K-26).
Ölçüldü: gerçek kayıt içeriğinde 50000 karakter **12799 jeton**, yani 32K
pencerenin %39'u. Pencere hiçbir zaman dolmuyor; dolan şey karakter tavanı.

**Kartların geçmişe maliyeti bir tur.** Kayıttan ölçülen tur maliyeti medyan 182,
ortalama 419, p90 1066 jeton. Medyan turla pencereye kartsız 162, kartlı 161 tur
sığıyor. Yani kart bloğu bir turluk geçmişe eş; darboğaz kartlar değil,
gözlemlerin boyutu.

### K-87 — Kart biçimi kilitlendi: yedi alan, beş alan, ve okuma anında filtrelenen alan karta basılmıyor

**Bağlam.** Kart jeton bütçeleri — beceri kartı ≤180, hata kartı ≤120 — ve alan
sayıları şartnamede sayı olarak duruyordu ama **hiçbir kart biçimi depoda
yazılmamıştı**: getirici kart nesnesi döndürüyor, basılmış hâli yoktu.
Dolayısıyla bütçe hiç sınanmamıştı.

**Karar.** `src/zihin/cards.py` basılmış hâli üretiyor. Alan başına bir satır.

Beceri kartının yedi alanı `SkillCard`'ın yedi alanı: kimlik, uygulamalar, etki
soneki, gövde, serbest parametreler, destek, beklenen tasarruf.

Hata kartının beş alanı kalıbın kimliği ile koşulu: çağrı (yöntem + uç), hata
etiketi, koşul, argüman şekli, görülme sayısı.

**İndeksin sakladığı tanı alanları karta basılmıyor.** `discriminating_count` ve
`own_app_condition` getiricinin filtre girdisi (K-85), modelin bunlarla
yapabileceği bir şey yok. İndeks her şeyi kökeniyle saklıyor, okuyan filtreliyor,
basılan yalnız eylem için gerekeni taşıyor.

**Aynı ölçüt beceri kartında da işliyor.** `bound_arguments`, `constants` ve
`postcondition` kayıtta duruyor ama karta girmiyor: bağlı argüman gövdenin kendi
içinde çözülüyor, sabit gövdeye gömülü koşuyor, son koşul düşürme kuralının ve
yürütme sonrası doğrulamanın girdisi. Çağıranın bilmesi gereken tek şey ne
sağlayacağı, ve onu `parameters` satırı söylüyor.

**Bilinen bir okunabilirlik sınırı.** Parametre adları `3.password` biçiminde,
yani "gövdenin üçüncü çağrısının `password` argümanı". Bu ad kayıttan mekanik
olarak geliyor ve bir modele hiç gösterilmedi; anlaşılır olup olmadığı madde
7'nin sorusu, ve düzeltmesi biçimin kendisinde olur, kartın içeriğinde değil.

**Renderer hiçbir şey uydurmuyor.** Öğüt yok, çerçeve metni yok, boş alan için
tahmin yok. Eklenen her cümle derleyicinin türetmediği bir içerik olurdu ve
ölçülen kazancın bir kısmı ona giderdi (`03-architecture.tr.md`: derleyici çevrimdışı
ve model kullanmıyor).

**Ölçülmemiş bir ölçüm ölçüldü** (`results/card-tokens.json`, modelin kendi
tokenizer'ıyla):

| Kart | Sayı | Jeton | Bütçe | Aşan |
|---|---|---|---|---|
| Beceri | 4 | 78–122, medyan 88 | ≤180 | **0** |
| Hata | 14 | 36–48, medyan 42 | ≤120 | **0** |

Biçim bütçeye sığıyor, yani düzeltme gerekmedi. Ölçeğin üç modeli her kart için
**aynı** sayıyı veriyor; "180 jeton" tek bir sayıyı adlandırıyor.

**k=5+5 bloğu en çok 523 jeton**, bütçelerin doyduğu hâlin tavanı 1500. Blok
maliyeti kartların toplamı; birleştirmenin kendi maliyeti yok.

**İki alan kararı ölçümle değil, kayıtla gerekçelendi.** `expected_saving` NULL
ise kart "unknown" yazıyor, sıfır yazmıyor — atfedilemeyen bir tasarruf
değersizlik değil (K-79). Karşıt başarısı olmayan kalıp koşul taşımıyor (K-85) ama
kart bunu **söylüyor**: koşulunu sessizce düşüren bir kart koşulsuz bir yasak
olurdu ve `07-failure-taxonomy.tr.md` onu açıkça reddediyor.

### K-86 — Getirici uygulamayı sembol alıyor, ve altyapıyı kalkandan farklı ele alıyor

**Karar.** Sembolik eşleşmenin sembolü **uygulama**. Görev metni uygulamaları
adlandırıyor, her kart bir uygulamaya ait, eşleşme bu ikisi arasında. Çıkarım
kalkanın kullandığının aynısı (`allowed_apps.py`).

**Eşleşme becerinin etki sonekine bakıyor, gövdesine değil.** Madencilenmiş her
beceri gövdesi bir `api_docs` okumasıyla başlıyor; gövdeye bakan bir eşleşme her
beceriyi her göreve verirdi ve kapsama %100 çıkıp hiçbir şey ifade etmezdi.

**Altyapı uygulamaları getiricide düşürülüyor, kalkanda düşürülmüyor.** Fark
kasıtlı ve iki gerekçesi var: kalkan `supervisor` ile `api_docs`'a erişimi
kesemez, yoksa hiçbir görev başlamaz; getirici onlara eşleşseydi her göreve aynı
`api_docs` kartını verirdi, ki o kart tam da tesadüfi koşula dayanan kart (S-45).
Tek çıkarım, iki kullanım, ve fark yazılı.

**Ölçülen kapsama, filtresiz tavan:**

| Bölme | Herhangi | Yalnız beceri | Yalnız hata |
|---|---|---|---|
| train (90) | %96,7 | %90,0 | %96,7 |
| dev (57) | %94,7 | %89,5 | %94,7 |
| test_normal (168) | **%100** | %94,6 | %100 |

Yanlışlama kapısı %25 ve üçü de üstünde
(`05-experiment-design.tr.md`). Mekanizma başına ayrı ölçülüyor, çünkü pilotun
"yalnız beceriler" ve "yalnız hatalar" koşulları ayrı.

**Yüksek kapsama tek başına getiricinin ayırt ettiğini göstermiyor.** Her göreve
aynı kartı veren bir getirici de %100 alırdı. Ayırt edicilik ayrıca ölçüldü
(`results/retriever-discrimination.json` → `distinct_card_sets`, `most_common_set_share`) ve
test_normal'da kart kümeleri ayrışıyor. Yani getirici gerçekten ayırıyor — ama
**ayırdığı şey hangi uygulamanın girişi**, hangi tür beceri değil. K-84'ün aynı
sonucu.

### K-85 — İndeks her şeyi kökeniyle saklıyor, getirici okuma anında filtreliyor

**Üç karar, S-45'in cevabı.**

**1. Karşıt başarısı sıfır olan kalıp koşul taşımıyor.** Yalnız "bilinen başarı
yok" işaretiyle indekse giriyor. Bu bir filtre değil, karşıtsal indirgemenin
kendi mantığının tutarlı uygulanması: ayırt edecek bir şey yokken ayırt etme
iddiası boş. `splitwise.auth/logout` kartındaki 59 koşul böyle düşüyor ve kural
için ölçüm gerekmiyor. Şemada dört ayrı CHECK bunu zorluyor.

**2. Tesadüfi ayırt etme için ad hoc kural konmuyor.** "Aynı uygulama" kısıtı
eklenmiyor, iki sebeple: dil kapalı kalmalı, ve o kısıt **meşru** uygulamalar
arası koşulları da reddederdi — jeton `supervisor`'dan geliyor.

Asıl mesele çoklu karşılaştırma: 92 aday yüklem, küçük hata grupları, bazı
koşullar şansa ayırıyor. Panzehir bir kısıt değil, kartın üstündeki sayaç
(`discriminating_count`, `own_app_condition`). 92'de 59 ayırıyorsa neredeyse
kesin tesadüf; 92'de 1 ayırıyorsa daha olası ama grup boyutuna bağlı, ve o sayı
da kartta.

**3. İndeks her şeyi saklıyor, getirici okuma anında filtreliyor.** Filtrenin
eşiği bir kurulum parametresi, duyarlılıkla raporlanacak, şimdi seçilmiyor.
Seçilmemiş parametreyi kayda gömmeme kuralının aynısı ve değer eşiğinde
uygulanan desenin aynısı (K-82).

### K-84 — İki mekanizma aynı darboğazı hedefliyor, toplanabilirlik muhtemelen tutmayacak

**Sonuç görülmeden ilan ediliyor.**

**Ayna bulgusu.** Beceri kütüphanesi ile hata indeksi iki ayrı korpustan
(geçen epizotlar ve başarısız eylemler), iki ayrı madencilikle üretildi ve ikisi
de **aynı mekanik darboğazı** buldu:

| | Kütüphane | İndeks |
|---|---|---|
| Ne öğretiyor | Jetonu almayı | Jetonu taşımamayı yasaklıyor |
| Büyüklük | 4 becerinin **4'ü** giriş | 15 kartın **11'i** `authorization_denied` |

**Sonucu: iki mekanizma bağımsız değil.** "Yalnız beceriler" ile "yalnız
hatalar" koşulları aynı şeye yardım ediyor. Dolayısıyla **"ikisi birden"
toplanabilir olmayabilir**: kazanç iki kez sayılamaz.

Kurulum aşamasında sınamayı planladığımız toplanabilirlik varsayımı tam olarak
buydu, ve **bu korpusta muhtemelen tutmayacak**. Şimdi yazılıyor ki sonuç
görüldükten sonra yorumlanmasın.

Bu bir arıza değil, korpusun özelliği: yirmi görev farklı uygulamalara dağılmış,
tekrarlayan tek mekanik iş kimlik doğrulama. Aynı sebep hem beceri sayısını
dörtte, hem kart dağılımını kimlik doğrulamada topluyor.

### K-83 — Koşul dili kapalı kalıyor; argüman şekli kalıbın parçası, koşulun değil

**Karar.** Dile dördüncü bir biçim eklenmiyor. Argümanın varlığı ya da yokluğu
**kalıbın** parçası; koşul yalnız üçüncü biçimi kullanıyor (dizide daha önce
belirli bir çağrının başarıyla yapılmış olması).

**Üç gerekçe.**

Dil bilerek kapalı ve sayılabilir. Genişletme çubuğu "birinci okuma ifade
edemiyor" olmalı, ve ölçüm bunun tersini gösteriyor: **498 401'in 498'i** ifade
edilebiliyor.

Beceri tarafı da argümanı çağrının parçası sayıyor, yani tutarlı.

İki desen ayrı koşullarla **ayrı kartlar** üretiyor, ki istenen de bu: biri
"önce giriş yap" diyor, diğeri "girdin ama jetonu taşımıyorsun".

**Şart: argüman bileşeni normalize şekil, değer değil.** Her argümanın varlığı
ve yokluğu, içeriği değil. Değere göre anahtarlansaydı kalıp uzayı patlar ve
destek çökerdi — beceri tarafında somut yola göre anahtarlamanın yapacağının
aynısı. Bugün risk görünmüyor, çünkü "jeton verilmiş ama reddedilmiş" sıfır kez
geçiyor, ama kural baştan konuyor.

**Sonuç: `access_token` şekilden düşürülmüyor.** Derleyici onu beceri
argümanlarından atıyor (her çağrıda var ve her imzayı kirletir), indeks ise
tutuyor, çünkü **yokluğu** 401'lerin üçte birini ayıran şeyin ta kendisi. Aynı
alan, iki mekanizmada iki farklı rol.

### K-82 — Beklenen tasarruf model çağrısıyla ölçülüyor, API çağrısıyla değil

**Karar.** `beklenen tasarruf = (gözlenen adım sayısı − 1) × görev desteği`.
`06-skill-language.tr.md`'nin "uzunluk eksi bir" ifadesi düzeltildi.

**Gerekçe.** Bu projenin birincil metriği model çağrısı, bir adım bir model
çağrısı, ve beceri tek adımda çağrılıyor. Çağrı uzunluğunu saymak, ajan
çağrıları zaten paketlemişse fazla sayıyor.

**Ölçüldü.** `spotify.auth/token` becerisi üç çağrıyı **iki adımda** yapıyor;
çağrı tabanlı formül tasarrufu 7'den 14'e çıkarıyor. Dört beceriden üçünde iki
sayı aynı, birinde iki kat fark var. Hata payı formülün kendisinde ve yalnız
ikisini birden ölçünce görünüyor.

Çağrı tabanlı sayı tanı sütunu olarak duruyor: iki sayının farkı, şartnamenin
yanlış birimi saydığını gösteren şeyin kendisi.

**Kestirim bir alt sınır.** Gözlenen adım sayısı sınır kontrolünün
yörüngelerinden geliyor. Zayıf bir yerel model aynı çağrıları daha çok adımda
yapar, yani becerinin ona değeri bu sayıdan yüksek. Becerilerin yardım etmesi
beklenen modeller tam da o zayıf modeller, dolayısıyla her sayı hedef kitlesi
için alt sınır. Pilot raporunda bu cümleyle okunacak.

**Değer eşiği pilottan önce seçilmiyor.** Korpus yirmi görev ve kestirim
korpusa özgü; eşik seçmek küçük örnekleme uydurmak olurdu. Izgara raporlanıyor,
getirici dört becerinin dördünü de alıyor, duyarlılık notu yanında duruyor.

### K-81 — Boşluk parametresi verime göre değil, yürütülebilirliğe göre seçiliyor

**Karar.** Boşluk üst sınırının ölçütü kaç beceri çıktığı **değil**, düşen ara
çağrıların becerinin etkisine ilgisiz olduğunun gösterilebilmesi.

**Gerekçe.** Boşluk madencilik ile yürütme için farklı anlam taşıyor.
Madencilikte gürültüye rağmen örüntü bulmayı sağlıyor. Yürütmede beceri gövdesi
**atomik** koşuyor (`06-skill-language.tr.md`), yani boşluğun atladığı çağrılar hiç
çalışmıyor. Gözlenen oluşumda beş ara çağrı varsa, derlenmiş beceri onları
atlıyor ve gözlenen etkiyi üretmeyebilir.

Verim ölçüt olsaydı parametreyi sonuca göre seçmiş olurduk — eşik için
yapılmayan şeyin aynısı.

**Ölçüldü. Üç kategori çıktı, ikisi zararsız.**

| Atlanan çağrı | Sonuç |
|---|---|
| Okuma | Zararsız. Ürettiği bir değer gerekiyorsa artık serbest parametre (S-42) |
| Başka uygulamanın etkisi | Zararsız. `phone` girişini atlamak `venmo` jetonunu bozmuyor |
| **Aynı uygulamanın etkisi** | **Bozucu.** Beceri kendi ihtiyaç duyduğu şeyi atlıyor |

Üçüncü kategori, kullanıcının "içlerinde yazma varsa beceri bozulur" dediği
durum; ikinci kategori ölçüm sırasında çıktı ve ayrı tutuluyor çünkü bağımsız.

**Sonuç.**

| Yapılandırma | Bozucu atlama |
|---|---|
| Boşluk 2, destek 3 | **Sıfır.** Dört giriş becerisi yalnız okuma ve başka uygulama etkisi atlıyor |
| Boşluk 5, destek 3 | Üç ortam eylemi becerisinin üçünde de var. `payment_requests` becerisi 161 oluşumda `venmo.auth/token`, 114'ünde başka bir `payment_requests` atlıyor. Bir giriş becerisi de bir kez kendi girişini atlıyor |

**Yani boşluk 5'te hayatta kalan üç ortam eylemi becerisi artefakt.** Madencilikte
geçerli, yürütmede jetonsuz koşar. Üst sınır boşluk **2**.

### K-80 — `complete_task` beceri gövdesinden de çıkarıldı, yalnız etki sonekinden değil

**Karar.** İskele kontrol kanalı çağrıları örüntünün **içinde** hiç yer almıyor.
Dizide duruyorlar — boşluk mesafesi gerçekten olan çağrılar üzerinden ölçülsün
diye — ama bir becerinin gövdesine giremiyorlar.

**Gerekçe.** Gövdesinde `complete_task` olan bir beceri çağrıldığında epizodu
sonlandırır. O beceriyi kullanan ajan, kullanmakla görevi bitirmiş olur; erken
çağırırsa yanlış tamamlama yapar. **Beceri iş taşır, kontrol akışı taşımaz**, ve
ayrım K-78'in etki soneki için kullandığı ayrımın aynısı.

**Sonucu karar anında ilan edildi, sonradan yorumlanmadı.** Korpustaki tek
gerçek ortam eylemi örüntüsü `POST venmo.payment_requests` + `complete_task`
idi; kontrol çağrısı çıkınca tek çağrıya düşüyor ve asgari uzunluk iki olduğu
için düşüyor. Yani boşluk 2 / destek 3'te ortam eylemi becerisi **sıfır** kalıyor
ve kütüphane yalnız giriş becerilerinden oluşuyor.

**Bu bir arıza değil, korpus çeşitliliği bulgusu.** Yirmi görev farklı
uygulamalara dağılmış, ortam eylemleri tekrarlamıyor; tekrarlayan tek şey her
görevin başındaki kimlik doğrulama. Sayı tutturmak için eşik düşürülmedi.

### K-79 — Son koşul yalnız tek çağrılı adımlardan okunuyor

**Karar.** Bir örüntü oluşumunun durum farkı, yalnız **tam olarak bir çağrı
yapmış** adımlardan okunuyor. Oluşumun etki sonekindeki çağrılardan herhangi
biri çok çağrılı bir adımdaysa, o oluşum **ölçülemez** sayılıyor ve kesişime
hiç girmiyor.

**Gerekçe: atıf yalıtım gerektiriyor.** On bir çağrı yapmış bir adımda farkın
hangi çağrıdan geldiği bilinemez. Bütün çağrılara atfetmek fazla atıf,
oransal dağıtmak veri uydurmak. Kayıtlı korpusta 16 fark taşıyan adımın 8'i tek
çağrılı.

**İkinci parça bir düzeltmeden geldi ve önemli.** İlk uygulama oluşumu, adımlardan
**herhangi biri** yalıtılmışsa ölçülmüş sayıyordu. Ölçülen sonuç: bir
destekleyen epizotta etki çağrısı üç çağrılık bir adımdaydı ama iskelenin
tamamlama çağrısı tek başınaydı, oluşum "ölçüldü" sayıldı, boş şekil katkı verdi
ve dört başka oluşumun üzerinde anlaştığı kesişimi sildi. Bu, "atfedilemedi"yi
"ölçüldü, bir şey olmadı" diye okumaktı — **sıfır fark tek başına kanıt değil**.

**Sonucu kabul ediliyor.** v0'da becerilerin büyük kısmı boş son koşulla
çıkıyor. Şartname buna zaten izin veriyor ve S-41'de sınırlama olarak yazılı.

### K-78 — Kalkan ile derleyici "etki" sorusunu ayrı ayrı yanıtlıyor

**Karar.** İki ölçüt ayrıldı.

| | Kalkan | Derleyici |
|---|---|---|
| Sorduğu | Bu izinli mi | Bu bir şey başardı mı |
| `login` / `logout` | Yazma **değil** (K-74) | **Etki** |
| `complete_task` | Yazma | **Etki değil** |

**Giriş, tarafların ayrıldığı yer.** K-74'ün oturum muafiyeti K-69'dan türedi:
okuma koşulsuz serbest, giriş okumanın ön koşulu, dolayısıyla giriş de serbest
olmalı. Bu bir **izin ifadesi**, başarım ifadesi değil. Derleyici için giriş
somut bir şey başarıyor: sonraki çağrıların ihtiyaç duyduğu jetonu üretiyor.

Kalkan tarafındaki muafiyet aynen duruyor. Aynı kayıt iki soruya iki cevap
veriyor, ve bu doğru, çünkü iki soru.

**Ölçülen sonuç tam da tasarımın öngördüğü şey.** Giriş ailesi gerçek beceri
oluyor ve yerel modellerin gözlenen arıza biçimini hedefliyor. Salt okuma keşif
örüntüleri dirilmiyor, çünkü auth içermiyorlar.

**`complete_task` K-75'in kaçağıydı.** `POST supervisor.message` dünya durumunu
değiştirmiyor, sonlandırma sinyali gönderiyor. Doğru ayrım **iskele kontrol
kanalı ile ortam eylemi** arasında, altyapı uygulaması üzerinden değil: `admin`
gerçek eylemler de taşıyor, ve `admin`'e yazan her ucun kendi uygulamasına da
yazdığı ölçüldü, dolayısıyla altyapı uygulamaları hakkında ayrı bir kurala gerek
yok. Kategorinin bugün tek üyesi `complete_task`.

Gerekçesi K-75'in üçüncü gerekçesinin aynısı: her epizotta var,
uygulama-bağımsız, alakasız sürümü yok, çıkarıcı kontrol ayıramaz. Ölçülen
kaçak: boşluk 2 / destek 3'te altı becerinin beşi yalnız bu çağrıya dayanıyordu.

### K-77 — Belge çevirisi mekanizma pilotunun koşuları sırasında yapılacak

**Karar.** Çeviri işi pilot koşuları sürerken paralel gidiyor, kapı
daraltıldıktan sonra (K-76).

**Gerekçe.** Pilot koşuları saatler sürecek ve çeviri ölçümü belirleyen yollara
dokunmuyor. Daraltılmış kapı ikisinin çakışmasını yapısal olarak imkânsız
kılıyor: belge değişikliği listede olmadığı için koşuyu durdurmuyor.

**Kapsam, daha önce kararlaştırıldığı gibi.** Kaynak Türkçe. `.tr.md` ve
`.en.md` sonekleri. Her `.en.md` başlığında kaynak commit'i. CI üç denetim: eş
var mı, ikisi aynı commit'te mi değişti, kaynak commit güncel mi.

**Sayılar tek yerde.** Ölçüm sonuçları veri dosyasında duruyor, iki dildeki
düzyazı ona atıf veriyor. İki dilde ayrı ayrı yazılan bir sayı, iki dilde ayrı
ayrı eskir.

**Birinci dalga:** yedi tasarım belgesi, kurulum protokolü, `09-limitations`,
README. CI eş denetimi o dizin için açılıyor.
**İkinci dalga, bloke etmeden:** `08-decisions` ve raporların birikimi.

**Kod tarafı:** yorumlar ve çalışma zamanı metinleri İngilizce, commit mesajları
Türkçe, PR açıklamaları tek dil.

### K-76 — Kirli ağaç kapısı ölçümü belirleyen yollara daraltılıyor

**Karar.** Koşu başlatmayı engelleyen kirli ağaç kapısı bütün ağaca değil,
`MEASUREMENT_DEFINING_PATHS` listesine bakacak. Liste dışı değişiklikler ne
engelleniyor ne künyeye yazılıyor.

**Gerekçe.** Kapı bugün bütün ağaca bakıyor, yani bir koşu sürerken hiçbir
dosyaya dokunulamıyor — belgeye, rapora, ilgisiz bir betiğe de. O listenin var
olma sebebi zaten bu ayrım: hangi değişiklik ölçümü değiştirir, hangisi
değiştirmez.

**Liste dışı değişiklik künyeye de yazılmıyor.** Yazılırsa her koşu "kirli"
görünür ve işaret gürültüye boğulur; gürültülü bir işaret, işaret olmayan bir
işaretten kötüdür çünkü bakılmaz.

**Zamanlama.** Derleyici bitince, mekanizma pilotundan önce. Pilot koşuları
saatler sürecek ve çeviri işi o sırada paralel gidecek (K-77); daraltma o
paralelliğin ön şartı.

**Uygulandı, mekanizma pilotunun başında.** `working_tree()` artık
`git status --porcelain` çıktısındaki yolları `defines_measurement()` ile süzüyor;
üyelik kuralı `changed_files` ile paylaşılıyor, yani iki kapı tek yüklem
kullanıyor. Yeniden adlandırma satırının iki yolu da, `??` satırının yolu da
sayılıyor. Liste dışı değişiklik ne engelliyor ne künyeye yazılıyor.

**Daraltma listedeki iki eksiği ortaya çıkardı.** `retriever.py` ve `cards.py`
listede yoktu; kapı bütün ağaca bakarken bu yalnız devam denetimini
zayıflatıyordu, daraltmadan sonra kirli bir getiriciyle koşu başlatılabilir hâle
geliyordu. İkisi listeye eklendi (S-31'in altındaki not). Ders kaydediliyor: kapı
daraltıldığında liste tek savunma hattı olur ve eksik girdinin bedeli artar.

### K-75 — Salt okuma örüntüleri beceri kütüphanesine girmiyor

**Karar.** Kütüphaneye giren bir becerinin etki soneki boş olamaz. Etki soneki
boş olan örüntüler madencileniyor ama ayrı bir sınıf olarak — **keşif öneki** —
ayrı raporlanıyor, birincil kütüphaneye girmiyor, getiriciye verilmiyor.

**Gerekçe üç parçalı, üçüncüsü asıl olan.**

Birleştirme kuralı etki sonekine bakıyor; boş sonekler birbirine eşit,
dolayısıyla bütün salt okuma örüntüleri tek beceriye çöker ve kural bir ayrım
aracı olmaktan çıkar.

Son koşul durum farklarının kesişimi; salt okuma hiçbir durum farkı üretmiyor,
yani beceri kendini doğrulayamıyor ve yürütme sonrası doğrulama dalı ölü kalıyor.

**Alakasız getirme kontrolü evrensel boilerplate'i ayıramıyor.** Kontrolün
mantığı "başka uygulamadan yanlış içerik ver, kazanç kaybolmalı", ama
uygulama-bağımsız bir boilerplate'in alakasız sürümü yok: `api_docs` keşfi her
görevde aynı ve her görevde geçerli. Kontrol o kazancı içeriğe yazar ve atıf
yanlış olur. Kütüphaneye alınırsa ölçülen kazancın bir kısmı hiçbir kontrolle
ayrılamaz hâle gelir — ölçüm kusuru değil, **ölçülemezlik**.

**Bulgu kaybolmuyor.** "İskelenin her görevde tekrarlanan bir keşif öneki var"
kendi başına raporlanabilir bir olgu. Boilerplate önbelleklemesi bir kazanç
olarak iddia edilecekse ayrı ve açıkça etiketli olur, becerilere atfedilen
kazancın içinde değil.

**Karar sonuç görülmeden verildi.** Ön kayıt bu riski derleyici koşmadan önce
ilan etmişti; ölçülmüş desteklere göre en yüksek destekli bitişik çift zaten
salt okuma (`api_descriptions -> account_passwords`, destek 12) ve giriş
çiftleri 6'da kalıyor.

**Ölçüt etki soneki, son koşul değil.** Etki soneki dolu bir beceri de boş son
koşul üretebiliyor: yazması yalnız alan düzeyindeyse satır sayımı görmüyor. O
beceri kütüphaneye giriyor, yalnız doğrulama dalı çalışmıyor.

### K-74 — Yazma kümesinde yöntem karar veriyor, gövde taraması yalnız GET'e kalıyor

**Karar.** POST, PUT, PATCH ve DELETE, adreslendikleri uygulamaya yazar sayılır.
Gövde taraması yalnız GET uçları için koşar. Sınır geçen yardımcı taraması
yöntemden bağımsız olarak her uçta koşar. **Tek istisna oturum uçları**:
`login` ve `logout`, dokuz uygulamada toplam 18 uç.

**Gerekçe: kazayla doğru olanı ilan edilmiş hâle getirmek.** Bir DELETE ucunun
durum değiştirmesi kaza değil, protokolün anlamı. Bugüne kadar o doğru cevap
süsleme sızıntısı üzerinden alınıyordu — `ast.walk` süsleme listesini geziyor ve
`@app.delete("/yol")` bir yazma çağrısı sanılıyordu (S-38). Dokuz
`delete_account` ucu, yüzeydeki en yıkıcı işlemler, kümede yalnızca bu kaza
sayesinde duruyordu.

**İkinci fayda: kırılgan yarı daralıyor.** Fiil adı eşleştirme ve delegasyon
körlüğü — bu oturumda iki kez ısıran şeyler — artık 478 uç yerine yalnız 176 GET
ucuna uygulanıyor. Delegasyonu ampirik yarı zaten yakalayacak.

**İstisnanın gerekçesi K-69'dan türüyor, ölçümden değil.** Okuma koşulsuz
serbest. Giriş, okumanın ön koşulu. Dolayısıyla giriş de serbest olmalı, yoksa
K-69 uygulanamaz. Sayı türetmeyi doğruluyor, üretmiyor: giriş yazma sayılsaydı
yanlış pozitif %4,1'den %24,5'e çıkardı ve 30 yeni başarısızlığın 30'u da aynı
çağrı olurdu, `POST /auth/token`.

**Kabul gerekçesi hata yönü.** Okuyucuyu yazar saymak meşru okumayı engelliyor,
marjinal maliyeti ölçüldü ve **sıfır**: yanlış pozitif %4,1'de kaldı. Yazarı
okuyucu saymak gerçek bir yazmayı denetimsiz geçiriyor. Güvenlik mekanizmasında
fazla dahil etmek güvenli yön.

**Bedeli açıkça kabul ediliyor ve kayıtlı.** 64 GET dışı ucun gövdesinde yazma
yok ve hepsi kümede; ikisi doğrulanmış okuyucu (`admin.show_card_balance`,
`admin.validate_card`). Uç bazında `body_write` alanıyla kayda geçiyor. Ayrıntı
S-38'de.

**Sonuç.** Yazar uç 242 → 296, sınır geçen yazar 16 → 19, GET yazarı 12'de sabit,
`download_*` dokuzda sabit.

### K-73 — Künye kalkanın kipini ve yapılandırma özetini taşıyor

**Karar.** `run_manifests` iki field kazandı ve ikisi de devam korumasının
reddet listesinde.

`shield_mode` — `shadow`, `enforce`, `off`. Zorunlu; boş bırakılırsa koşu
başlamıyor. Varsayılan `off` yalnız taşınan eski satırlar için geçerli ve
onlar için **doğru**: o epizotlar kalkan var olmadan koşuldu.

`shield_config_digest` — yazma kümesini, içindeki sınır geçen eşlemeyi ve
izinli uygulama çıkarıcısının kaynağını kapsayan tek özet. `off` değilse
zorunlu; şemada CHECK, taşınmış dosyada Python katmanında.

**Gerekçe.** `shield_violations` satırları yalnız onları üreten yazma kümesine
göre anlam taşıyor. O küme **tek günde iki kez** değişti: çözümleyici yöntemi
almaya başlayınca 26 çağrı sınıf değiştirdi, `update` fiil listesinden düşünce
iki uç kümeden çıktı. İkisi de kipi değiştirmedi ve ikisi de kalkanın hangi
çağrıyı engellediğini değiştirdi. Kayıt bunu taşımasa fark görünmezdi.

**Özet, sürüm numarası değil.** Numara elle artırılıyor ve el unutuyor; özet
hesaplanıyor. Yukarıdaki iki değişikliğin ikisi de bir numarayı artırmazdı.

**Çıkarıcı bütün kaynağıyla giriyor.** Yalnız `APP_SURFACE_FORMS` özetlenseydi
eşleştirme mantığındaki bir değişiklik kaçardı, oysa hangi uygulamaların izinli
olduğunu o mantık da belirliyor.

### K-72 — Engelleme oranı ile yanlış pozitif oranı ayrı raporlanıyor

**Karar.** Kalkanın iki sayısı hiçbir raporda birleştirilmiyor ve birbirinin
yerine kullanılmıyor.

| | Ne ölçüyor | Nerede ölçülebilir | Değer |
|---|---|---|---|
| **Yanlış pozitif oranı** | Engellemenin **yanlış** olduğu durumlar | Yalnız train + dev | %4,1 (147 görevin 6'sı) |
| **Engelleme oranı** | Kalkanın **ateşlediği** durumlar, doğru ya da yanlış | Bütün korpus | %0,07 çağrı, %2,33 epizot |

**Düzeltme, 15 Kasım 2026: engelleme oranı.** Korpusa bir testin iki çıktısı girmişti
(S-83). Onlarsız %0,05 çağrı, %1,95 epizot. Yanlış pozitif oranı bu korpustan
ölçülmüyor ve değişmedi.

**Gerekçe.** Bir engellemenin yanlış olup olmadığını yalnız yer gerçeği söyler.
`test_normal` bölmesinde `required_apps.json` yok (S-03), yani orada bir
engellemenin doğruluğu **bilinemez**. Korpusun büyük kısmı orada.

İkisini birbirinin yerine koymak iki yönde de kategori hatası: yüksek engelleme
oranı zarar kanıtı değil, ve train + dev'deki düşük yanlış pozitif oranı
korpusun geri kalanında ne olacağını sınırlamıyor.

**Sonuç.** Mekanizma pilotunun dördüncü ölçümü tek sayı değil, iki sayı.

**Ve engelleme oranının bu korpustaki değeri kalkanın ucuzluğunu göstermiyor.**
Ölçülen altı engellemenin altısı da düzeneğin kendi yazma sondalarından geliyor
(`durum-sondasi-*`, `notlar`, `reset-check-1`, `sifirlama*`), tek görevde
(82e2fac_1, salt Spotify) ve tek uçta (`POST /simple_note/notes`). Model
yörüngelerinde engelleme oranı **sıfır**.

Bu, kalkanın ucuz olduğunun değil, **korpusun kalkanı sınamadığının** kanıtı:
58 görevin çoğu tek uygulamaya dokunuyor, yani sınır geçen yazma fırsatı hiç
doğmuyor. Pilot raporunda bu cümleyle yazılacak.

### K-71 — Kalkan bugün yalnız gölge modunda monte, zorlama kasten kurulmadı

**Karar.** `ShieldMount` yalnız `shadow` kabul ediyor; `enforce` ile kurulmaya
çalışılırsa **kurulum anında** düşüyor.

**Gerekçe.** Engellemek çağrının sunucuya hiç gitmemesi demek, yani ajanın
beklediği yanıtın yerine bir şey konması gerekiyor. İstisna, 403 gövdesi ve
sessiz boş sonuç üç farklı yörünge üretir. Yani ikame yanıtın biçimi bir koşul
değişkeni ve henüz kararlaştırılmadı; buraya bir tane uydurmak koşul değişkenini
ölçüme sokmak olurdu.

**Gölge modunun hiçbirine ihtiyacı yok.** Çağrı koşuyor, karar kaydediliyor,
yerine bir şey konmuyor. Engelleme oranı, engellemenin neye benzediği hiç
kararlaştırılmadan ölçülebiliyor — ve ölçüldü.

**Sessiz düşmek yerine gürültülü düşüyor.** `enforce` diyip gölge gibi davranan
bir montaj, künyesinde `enforce` yazan ve davranışı `shadow` olan bir koşu
üretirdi. Kurulumda düşmek bunu imkânsız kılıyor.

### K-70 — Kalkanın izinli uygulama kümesi görev metninden

**Karar.** İzinli uygulama kümesi görev yönergesinden çıkarılıyor
(`src/zihin/allowed_apps.py`). `ground_truth/required_apps.json` bu çıkarımın
**doğrulayıcısı, girdisi değil**.

**Gerekçe.** Kümeyi ground truth'tan türetmek kalkana kıyaslama dışında sahip
olmayacağı bir oracle vermek olurdu. Gerçek bir dağıtımda görev metni dışında
kaynak yok. Yani vekil bir yaklaşım değil, tanımın kendisi.

**Sonuç: kalkanın isabeti çıkarımın isabetiyle sınırlı.** Ölçüldü: tam eşleşme
%75,5, Jaccard 0,857 (147 görev, train + dev). Kaçaklar `phone` 30, `venmo` 6,
`file_system` 3; fazlalar `simple_note` 6.

**Sınırın büyük kısmı gerçek, vekilin kusuru değil.** Otuz `phone` kaçağında
yönerge uygulamayı hiç adlandırmıyor. Hiçbir metin tabanlı vekil kurtaramaz ve
bu deneysel bir artefakt değil dağıtım özelliği.

**Yüzey biçimi listesi ölçümden önce yazıldı ve sonra değiştirilmedi.**
Değiştirmek doğrulayıcıya uydurmak olurdu ve %75,5'i anlamsız kılardı.

### K-68 — Sandbox sıranın sonuna alındı

**Karar.** Mekanizma sırası şöyle: kalkan, beceri şartnamesi, derleyici v0, hata
indeksi, getirici v0, uçtan uca demo, **sonra** sandbox.

**Gerekçe üç parçalı.** Sandbox en pahalı madde ve bağımlılığı sıfır: kalkan,
derleyici, indeks ve getirici hiçbiri onu beklemiyor. Kapsam çalışması ayrıca
kayıt yolunun yeniden mimarisini gerektiren bir bloker çıkardı (K-65). Ve süre
biterse mekanizmasız bir sandbox, sandbox'sız mekanizmalardan kötü bir çıktı.

**Bedeli açıkça kabul ediliyor.** Sandbox gelene kadar ajanın ürettiği kod bizim
sürecimizde, host erişimiyle koşuyor. Tehdit modelinin birinci maddesine karşı
savunma yok. Bu kurulum rejiminde kabul edilebilir, çünkü koşulan kod kendi
seçtiğimiz modellerden geliyor ve makine bizim. Yayımlanabilir bir sonuç
üretilmeden önce sandbox kurulmuş olacak.

### K-67 — Sandbox kaynak sınırları ölçülecek, tahmin edilmeyecek

**Karar.** Bellek, süreç, süre ve disk sınırlarının sayıları gerçek kullanım
ölçülerek belirlenecek, üstüne pay konacak ve künyeye yazılacak.

**Gerekçe.** Kapsam belgesi 512 MiB öneriyordu; tam `appworld` paketi konteynerde
olacağı için o değer sınırda olabilir. Ama asıl sebep yöntemsel: tahmin edilen
bir sınır zaten K-D'yi ihlal ediyor. Bir sınırın bağlayıcı olmadığını gösterme
şartı, sınırın ölçülmüş bir tabana dayanmasını gerektiriyor.

**Bağlayıcılık göstergesi.** Sınıra çarparak biten epizot oranı. Sıfıra yakın
değilse sınır gevşetiliyor ve sonuç alt sınır olarak işaretleniyor. K-60'ın
sandbox'a uygulanmış hâli.

### K-66 — Konteynerde tam `appworld` paketi

**Karar.** Sandbox imajı `appworld` paketini tam hâliyle taşıyor, ince bir RPC
istemcisi yazılmıyor.

**Gerekçe.** İnce istemci ajanın gördüğü arayüzü sessizce değiştirirdi. K-19'un
şartı açık: aynı mesajlar gitsin ve aynı metin dönsün. Sessizce değişen bir
arayüz o şartı sınanmadan bozar.

**Bedeli.** İmaj büyüyor ve paket host'takiyle aynı sürümde tutulmak zorunda.
Sürüm damgası künyeye giriyor.

### K-65 — Sandbox'ta kayıt loopback vekilinde yapılacak

**Karar.** Ajan kodu konteynere taşındığında API kaydı, konteyner ile AppWorld
sunucusu arasında loopback üzerinde duran bir **kayıt vekilinde** yapılacak.

**Bağlam.** `ApiCapture` bugün `Requester` sınıfını bizim sürecimizde
sarmalıyor. Ajan kodu konteynere taşınırsa `Requester` de taşınır ve sarmalayıcı
hiçbir şey görmez. Biriktirme tek seferlik, geriye dönük eklenemez (S-16).

**Elenen iki yol.** Yakalayıcıyı konteynere koymak, kaydı korumak istediği şeye
teslim etmek olur; tehdit modelinin birinci maddesi tam olarak bu. Sunucu
tarafında kayıt ise yanıt gövdesini kaybediyor (S-05) ve düzeltmek AppWorld'ün
kendisini değiştirmek demek — yayımlanmış tabanlarla karşılaştırılabilirliği
bozardı.

**Üç şart.**

1. **Şeffaflık testi.** Aynı görev doğrudan ve vekil üzerinden koşulacak,
   yörüngeler birebir aynı çıkacak. Vekil ölçüme girmeyen bir katman olduğunu
   göstermek zorunda.
2. Vekil `OLCUMU_BELIRLEYEN_YOLLAR` listesine giriyor, yani değişikliği devam
   denetiminde uyarıdan redde yükseliyor.
3. Vekil sürümü künyeye yazılıyor.

**Yan kazanç.** Kalkanın doğal yeri de burası: reddedilen çağrı hiç iletilmez.

### K-64 — Durma kuralının bedeli bilerek ödeniyor: eşik 40, elli beş saat

**Karar.** Durma kuralının eşiği 40. Alternatifi 15'ti ve ana koşuyu yaklaşık
51 saatte bitirirdi; 40 yaklaşık 106 saat sürüyor. Aradaki **55 saat bilerek
ödeniyor.**

**Neden ödendiği, üç gerekçe.**

1. **Kural bir hesaplama optimizasyonu, geçerlilik mekanizması değil.** Tavana
   koşup başarısız olan epizot da doğru kaydediliyor. Kural doğruluğa hiçbir şey
   katmıyor, yalnız aynı cevaba daha çabuk varıyor. Geçerliliği hesaplama
   süresine takas etmek, bu projede tutarlı olarak reddedilen yön.

2. **Kayıp rastgele değil.** Eşik 15, sınır kontrolünün 20 geçen epizodundan
   birini kesiyordu: `8ce6779_2`. O epizot 107 adım boyunca farklı `task_id`'lerle
   yorum okuyup 138. adımda hepsini birden yazıyor. Yani uzun salt-okuma keşfiyle
   çözülen bir görev — tam olarak derlenmiş becerinin en büyük etkiyi göstermesi
   beklenen tür. Taban koşulunda bu görevler kesilirse kanıt birincil metrikten
   (adım farkı) ikincile (başarı oranı farkı) kayar. Hipotez adım farkı üzerine
   kurulu.

3. **Asimetri.** Ucuz seçip yanılmak tam bir yeniden koşu; pahalı seçip gereksiz
   olduğunu görmek 55 saat. Ana koşu arka planda koşacak.

**Kalibrasyon.** Küme sınır kontrolünün 30 tam yörüngesi (`sinir3` +
`sinir3-kapali`, seri 2), 20'si geçen. Ölçüt: geçen hiçbir epizot kesilmeyecek.
En düşük güvenli eşik 37; 40 üç adım marj bırakıyor. Eşik 40'ta düşen
epizotların 2/10'u kesiliyor, bant taramasında 17/30.

**Kalan şart.** Eşik tek modelden kalibre edildi. Aile seçildiğinde aktarım
kontrolü olarak yeniden kalibre edilecek.

**Bağlantı.** K-63 kimlik tanımını veriyor; eşik ancak o tanımla anlamlı.
Protokolün "bir epizodu sonlandırabilen her parametre ölçüm aletidir" kuralı
kalibrasyonun ölçümden önce yapılmasını istiyor, bu karar onun uygulanması.

### K-63 — İlerleme kimliği somut çağrı

**Karar.** Durma kuralının "yeni çağrı" ölçütünde kimlik, yapılan çağrının
kendisi: `uygulama.somut_yol|istek_parametreleri`. Yani
`todoist.tasks/2851/comments|{...}` ile `todoist.tasks/2854/comments|{...}`
ayrı kimlikler.

**Önce rota şablonu seçilmişti, ölçüm onu eledi.** Şablon kimliği
(`tasks/{task_id}/comments`) kimlik türünden bağımsızdı ve liste ile detayı
ayırıyordu; iyi özellikler. Ama `8ce6779_2` epizodu onu düşürdü: 117 kez farklı
kaynak okuyup sonunda hepsini birden yazıyor ve 9/9 test geçiyor. Şablonla o
epizot 107 adım durgun görünüyor, yani hiçbir makul eşik onu kurtaramıyor.
Somut kimlikle durgunluğu 36.

**S-25 hâlâ yakalanıyor ve ayrım ölçülmüş.** S-25'in özgün uyarısı şuydu:
"farklı kimliklerle dönen bir döngü her adımda yeni bir eylem üretir, kural hiç
ateşlemez." Uyarı varsayımsaldı. Gerçek patolojik epizot 736 çağrının hepsini
**aynı üç somut yola** yapıyor; somut kimlikle durgunluğu 146. İki vaka somut
düzeyde net ayrışıyor: 36'ya karşı 146.

**Parametre kimliğin parçası.** Aynı yola farklı sorguyla gitmek yeni bilgi
getiriyor. Bedeli kabul edilmiş: sayfalama kimliği her sayfada değiştirdiği için
sonsuz sayfalama kendiliğinden durgun görünmüyor. Eşik 40'ta ölçülen etki,
düşen epizotların daha azının kesilmesi.

**Serileştirme iki yerde aynı olmak zorunda.** Kimlik hem canlı kuralda hem
kalibrasyon aletinde kuruluyor; `insert_action` parametreleri `sort_keys=True`
ile yazıyor ve kimlik üretimi de öyle. Ayrı serileştirme sessiz bir ayrışma
üretirdi — S-32'nin sınıfı. Ayrı bir test bunu çiviliyor.

**Rota şablonu kodu kalıyor ama kuralın dışında.** "Epizot kaç farklı uca
dokundu" rapor edilen bir tanı ve şablon düzeyi onun doğru granülerliği.
Kural onu kullanmıyor.

**Bağlantı.** S-32 ölçütün neden taşıyıcı olduğunu ölçtü: ölçüt devre dışıyken
geçen epizotların yüzde kırkı kesildi. Eşik K-64'te.

### K-62 — Yorumlanma kuralı önceden yazılmamış ölçüm sonuç değildir

**Karar.** Bir ölçümün nasıl yorumlanacağı koşudan **önce** yazılmamışsa, o
ölçüm bir sonuç değil **kurulum tanısıdır** ve sonuç iddiasında kullanılamaz.

**Sebep bir denetimden çıktı.** Kurulum sonrası dört PR'da rapor edilen
sonuçların dördü geri alındı ya da geçersiz oldu, biri yanlış ölçütle
değerlendirildi, biri alt sınıra indi. Ortak sebep tekti: ölçümler yapıldıkça
yorumlanma çerçevesi de aynı anda türetildi.

Yazılı zemin olsaydı dördü de ölçüm öncesinde elenirdi. Sabit adım tavanı
K-43'e takılırdı. Dereceli skor metrik listesinde olmadığı için başlığa
çıkmazdı. Yüzde on ölçütü tavana çarpma ile sansür ayrımı sayesinde doğru yere
uygulanırdı. Çıktı bütçesi bağlayıcılık kuralıyla önceden denetlenirdi.

**Somut kural.** Bir ölçüm koşulmadan önce üç şey yazılı olacak: hangi niceliği
ölçtüğü, hangi eşikte ne söyleyeceği, ve hangi parametrenin bağlayıcı
olmadığının nasıl gösterileceği (K-60). Üçü de yoksa çıktı tanıdır.

**Bağlantı.** K-49 bir şeyin doğru sebeple çalıştığını sormayı istiyor; K-62
aynı disiplini ölçümün yorumuna uyguluyor. K-50'nin donma kuralı neyin
dondurulacağını söylüyor, K-62 dondurulmamışın statüsünü söylüyor.

### K-61 — Ana eksen aile şartları ve ayrılmış roller

**Karar.** Ölçek ekseninin ailesi şu dört şartı birlikte tutmalı. Bunlar tasarım
kararı, arama sonucu değil.

1. **Tek aile.** Boyut değişirken eğitim hattı, sözcük dağarcığı ve talimat
   biçimi sabit kalmalı. Aileler karışırsa eksende iki değişken birden değişir
   ve boyutun etkisi ayrılamaz.
2. **En az üç yoğun boyut, hepsinin 8 GB'a sığması.** Ölçülmüş referans:
   `qwen2.5-coder:7b-instruct-q4_K_M` kartta 5,16 GiB, 32K bağlamın q8_0 KV
   cache'i bir slot için yaklaşık 0,9 GiB (K-45). Ağırlık tavanı kabaca 5-6
   GiB.
3. **Akıl yürütme modu olmayan ya da tamamen kapatılabilen.** Kapatılamayan
   model eleniyor.
4. **Ollama'da mevcut ve instruct ayarlı.**

**Ayrılmış roller, ana eksene alınmıyor.**

**Aile kontrolü.** Ana eksenden **farklı** bir aile, ana eksenin **en büyük
noktası bandında**, ve **tek nokta**. Ana eksene alınamaz, alınırsa rolü yok
olur. Ön koşul kapısını o da geçmek zorunda. Hangi aile ve hangi boyut olacağı
ana eksen seçildikten sonra belirlenecek; `granite` yalnız aday, seçilmiş
değil.

`deepseek-v4-flash-0731` sınır kontrolü: API üzerinden, düşünme kapalı.

**Daha önce elenenler.**

| Model | Sebep |
|---|---|
| Qwen2.5-Coder 14B ve üstü | 8 GB'a sığmıyor |
| Kimi K3 | akıl yürütme kapatılamıyor |
| GLM-5.2 | yalnız High ve Max modlarında |

Son ikisi sınır kontrolü adayıydı, ana eksen adayı değildi.

**Seçim ölçütü.** Ailenin en büyük sığan boyutunun ön koşulu geçmesi yetmiyor.
**En az iki boyut geçmeli**, yoksa ölçek ekseni yaşamıyor ve ikinci araştırma
sorusu zaten ölüyor.

Aile elemesi için kaba ön koşul eşiği taban başarısının %25 üstünde olması;
kesin sayı pilottan gelecek.

Bütçeler bağlayıcı olmayacak şekilde ayarlanıp raporlanıyor (K-60), ve kodsuz
ile ayrıştırılamayan adım oranı her adayda ayrı veriliyor.

### K-60 — Sıfır yorumlanmadan önce bağlayıcı olmayan parametreler gösterilir

**Karar.** Bağlayıcı olabilecek her parametre, bir sıfır ya da taban sonucu
yorumlanmadan önce bağlayıcı olmadığı gösterilerek raporlanıyor. Kapsam dört
parametre:

| Parametre | Bağlayıcılık göstergesi |
|---|---|
| Çıktı bütçesi (`max_tokens`) | Kodsuz adım oranı |
| Bağlam penceresi (`num_ctx`) | Kesilen gözlem oranı, `was_truncated` |
| Adım tavanı | Tavana çarpma oranı |
| Durma kuralı | `no_progress` ile kapanan epizot oranı |

Gösterge sıfıra yakın değilse sonuç bir alt sınırdır ve öyle yazılır.

**Sebep ölçülmüş bir arıza.** Sınır kontrolünde aynı model ve aynı görevlerde
yalnız çıktı bütçesi değişince geçen görev 6/30'dan 20/30'a çıktı, kodsuz adım
oranı %25,0'ten %6,9'a düştü (S-26). Bütçe bağlayıcıydı ve ilk sayı modelin
değil yapılandırmanın sonucuydu.

**Yerel koşularda çıktı bütçesi künyeye yazılıyor**, ayarlanmamış olsa bile.
Ayarlanmamış bir değer de bir değerdir ve sonradan geri okunamazsa aynı soru
cevaplanamaz hâle gelir.

**Yerel sıfır bu kuralın altında zaten geçerli.** Teşhis 2'de 958 adımın hepsi
kod üretti: 785 eylem, 162 kategori 4, 11 sessiz boş başarı, kodsuz adım sıfır,
ayrıştırılamayan adım sıfır. Çıktı kesilmesi olsaydı bu iki kategoride
görünürdü. qwen2.5-coder akıl yürütme de üretmiyor, yani 400 jeton orada hiç
bağlayıcı olmadı. **7B'nin 0/30'u artefakt değil.**

### K-59 — İlgisiz getirme kontrastının üç sonucu, yorumları sonuç görülmeden yazılı

**Bağlam.** Teşhis, ajanın en tekrar eden arızasının yapısal olduğunu gösterdi:
giriş jetonu sözlük hâlinde dönüyor ve model sözlüğün tamamını `access_token`
parametresine geçiriyor; parola listesinden yanlış satır seçiliyor; aynı blok
onlarca kez tekrarlanıyor. Desen uygulamaya özgü değil, mekanik.

**İyi taraf.** Mekanizmalar gözlenen bir darboğazı hedefliyor, uydurulmuş bir
hedefi değil. Derlenmiş bir beceri ya da hata kartı tam olarak bu diziyi
kodlar.

**Riskli taraf.** Desen yapısal olduğu için içerikten bağımsız da öğrenilebilir.
Spotify görevinden derlenmiş alakasız bir kart da aynı şablonu taşır. Yani
`irrelevant_retrieval` koşulu da kazanç üretebilir ve çıkarıcı kontrol farkı
hacim tarafına yazar. Bu S-19'un somutlaşmış hâli.

**Karar.** Kontrolün üç sonucunun yorumu şimdi yazılıyor, sonuç görülmeden.

1. **Hem ilgili kartlar hem alakasız getirme kazanıyor.** Değer yapısal
   şablonda demektir: ajanın eksiği belirli bir uygulamanın bilgisi değil, iyi
   biçimli bir çağrı dizisi görmek. Bu gerçek ve raporlanabilir bir bulgu, ama
   **bizim hipotezimiz değil.** Ana iddia desteklenmemiş sayılıyor ve makale
   bulguyu bu adla yazıyor.
2. **Yalnız ilgili kartlar kazanıyor.** İçerik önemli demektir; ana hipotez
   destekleniyor.
3. **İkisi de kazanmıyor.** Mekanizma bu bantta işe yaramıyor demektir.

**Neden şimdi.** Birinci sonuç, sonradan yorumlanırsa "aslında bulduğumuz şey
buydu" diye yazılmaya çok açık. Yorum önceden sabitlenirse o kapı kapanıyor.

**Bağlantı.** K-56 koşulu zorunlu kılıyor, K-59 sonucunun nasıl okunacağını
sabitliyor.

---

## Açık sorular

Aşağıdakiler cevaplanmadan yazıldı. Yazılan değerler öneri. Cevap geldiğinde
düzeltilecek ve bu bölümden karar kaydına taşınacak.

### A-01 — `retrieval.mode` hangi ekseni taşıyor? Cevaplandı, K-28.

### A-02 — `fill.enabled` taban dışında açık mı? Cevaplandı, K-29.

### A-03 — `failures.source` enum'u kaç değer taşıyor? Cevaplandı, K-30.

### A-04 — `experiments/decisions.csv` hangi sütunları taşıyor?

Dosya taslak olarak isteniyor ama sütunları söylenmedi. Yazılan varsayım bu
belgenin kendi kayıt biçiminden türetildi:

```
decision_id,stage,title,status,supersedes,rationale_summary
```

`status` bu belgedeki üç hâli karşılıyor: `active`, `superseded` ve `open`.
`supersedes` üstü çizilen kararı gösteriyor, K-11 ve K-13 gibi. Sütunlar farklı
olacaksa dosya boşken düzeltmek en ucuzu.

### A-05 — `num_ctx` Ollama'ya hangi yoldan geçecek? Cevaplandı, K-37.

### A-06 — Ölçek ekseni yerel donanımla sınırlı kalıyor mu? Cevaplandı, K-133.

**Neden yeniden açıldı.** "Model yerel koşuyor, uzak sunucu yok" kısıtı
tasarımın en başından beri varsayılıyordu ve karar kaydında ayrı bir madde
olarak yazılmamıştı. Dayanağı 7B'nin ölçülebilir bir bantta olacağı
varsayımıydı. Bant taraması o varsayımı düşürdü: üç modelde de ikili başarı
sıfır, ve tabakalamanın üç ayrı biçimi de bant açmadı.

**Kısıtın bağlı olduğu şey.** Ölçek ekseni sıfırın üstünde en az iki nokta
istiyor. Sekiz gigabayt VRAM'e sığan en büyük model 7B ve o nokta sıfır verdi.
Eksen için üç seçenek görünüyor: 14B'yi kısmi CPU taşmasıyla koşturmak (yavaş
ama ölçüm için yeterli olabilir), kiralık GPU, ya da birincil hücreyi API
üzerinden sunulan bir modele taşımak.

**Karar verilmedi.** Önce sınır kontrolü koşuyor: düzenek doğrulanmadan eksen
kararı alınamaz, çünkü sıfırların sebebi düzenek olabilir.

**Not.** Bu madde bir kısıtın yeniden açıldığını kaydediyor, yeni bir kısıt
koymuyor. Ön kayda giren hâli, kararın hangi ölçüme bağlandığı.
