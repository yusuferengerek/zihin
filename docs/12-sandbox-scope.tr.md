# Sandbox kapsamı (yol haritası madde 8)

Bu belgenin birinci sürümü kodlamadan önce yazılmış ve onay beklemişti. Dört
karar verildi (K-A…K-D), zorunlu ikinci değişiklik onaylandı, ve planlama
ölçümlerinin çıkardığı beş soru da karara bağlandı (K-92…K-97). Kodlama bu
sürümle başlıyor.

Sayılar üç dosyada tek yerde duruyor: `results/sandbox-onolcum.json` (planlama
ölçümleri), `results/wire-identity.json` (tel kimliği doğrulaması),
`results/container-network.json` (ağ kipleri, iki platform). Buradaki tablolar o
dosyalara atıf veriyor; okunurluk için belirleyici olan sayılar metne de girdi.

**Bu sürümün en sonuçlu bulgusu bir kolaylık değil, bir tehdit.** Sunulan kipe
geçmek host tarafında yirmi bir rotalı bir yönetim yüzeyi açıyor, konteyner o
yüzeye ulaşabiliyor, ve içindeki bir rota gönderilen yola dosya yazdırıyor.
Ayrıntısı §6.4. Kapsam belgesinin birinci sürümü bunu görmemişti.

---

## 1. Durum

| Karar | Durum |
|---|---|
| K-A — kayıt nerede yapılacak | **Kapandı:** loopback üzerinde kayıt vekili (seçenek 3), üç şartla |
| K-B — konteynerin içinde ne var | **Kapandı:** tam `appworld` paketi (seçenek 1) |
| K-C — kaynak sınırlarının değerleri | **Kapandı:** tahmin edilmeyecek, ölçülecek, üstüne pay konacak, künyeye yazılacak |
| K-D — sınırlar bağlayıcı olmamalı | **Kapandı:** gösterilecek; sınıra çarpan epizot oranı sıfıra yakın değilse sonuç alt sınır |
| Zorunlu ikinci değişiklik | **Kapandı:** AppWorld sunulan kipe geçiyor |
| Konteyner testleri CI'da koşabilir mi | **Ölçüldü:** evet, §9 |
| Ağ politikası | **Kapandı:** `--network=none` + salt okunur unix soket, iki platformda ölçüldü (§10, K-95) |
| Beş soru | **Kapandı:** §11, kararlar K-92…K-97 |

---

## 2. Kilitli olan

Tehdit modeli (`04-threat-model.tr.md`) ve mimari (`03-architecture.tr.md`) sandbox'ı
zaten tanımlıyor. Bu belge onların üstüne yazıyor, yerlerine geçmiyor.

| Şart | Kaynak |
|---|---|
| Kök yetkisiz konteyner (rootless podman) | tehdit modeli, K-01 gerekçe 1 |
| Salt okunur kök | tehdit modeli |
| Ağ ad alanı düzeyinde politika: yalnız loopback, sabit uygulama portları | tehdit modeli |
| Bellek, süreç, süre ve disk sınırlı | tehdit modeli |
| İmaj sürüm damgasıyla sabit | tehdit modeli |
| **Her epizotta yeniden doğuyor** | tehdit modeli, ikinci tehdide karşı asıl savunma |

Üç tehdit de değişmiyor: host tarafına sızma, epizotlar arası kirlenme, geri
alınamaz yan etki.

---

## 3. Bugün ne oluyor

Ajanın ürettiği kod **bizim Python sürecimizde** koşuyor. AppWorld
`InteractiveShellEmbed` ile gömülü bir IPython kabuğunda yürütüyor ve o kabuk
host dosya sistemine, kayıt veritabanına, yapılandırmaya ve ağa tam erişimli.

Yani birinci tehdide karşı **şu an hiçbir savunma yok**. Bu bir gözden kaçma
değil, sıraya konmuş bir iş: sandbox katmanı hiç kurulmadı.

AppWorld ayrıca API'leri **süreç içinde** sunuyor: `fastapi.testclient.TestClient`,
yani gerçek soket yok, port yok. Ölçüldü.

Yerel ortamda **podman kurulu değil**. Ubuntu noble deposu 4.9.3 veriyor.
Kök yetkisiz koşunun ön şartları duruyor: cgroup v2, kullanıcıya devredilen
denetleyiciler `cpu memory pids`, `subuid/subgid` tanımlı, systemd açık.
Kurulum madde 8'in ilk işi.

---

## 4. Zorunlu ikinci değişiklik ölçüldü

`appworld serve apis --port` komutu var ve `AppWorld(remote_apis_url=...)`
destekleniyor. Konteyner süreç içi ASGI istemcisine ulaşamaz, o yüzden bu
değişiklik zorunlu.

Geçiş yolu **yapılandırma**: `appworld_config` sözlüğü referans ajanın
`AppWorld.initializer(update_defaults=True, **appworld_config)` çağrısına
giriyor. `remote_apis_url` ve `remote_environment_url` oraya konarak açılıyor,
yani iskeleye dokunulmuyor (K-19).

### 4.1 Sunulan kip ajanın gördüğü metni değiştirmiyor

Aynı altı kod bloğu üç kipte koşuldu: süreç içi `TestClient`, uzak API sunucusu,
ve uzak ortam sunucusu + uzak API sunucusu. Bloklar bilerek karışık seçildi:
belge okuma, gizli veri okuma, başarılı giriş, yanlış jetonla 401, olmayan
kaynak.

| Kip | `world.execute` çıktısının özeti | `api_calls.jsonl` | `environment_io.md` |
|---|---|---|---|
| Süreç içi `TestClient` | `52de8119baea903e` | 424 bayt | 4302 bayt |
| Uzak API | `52de8119baea903e` | 424 bayt | 4302 bayt |
| Uzak ortam + uzak API | `52de8119baea903e` | 424 bayt | 4302 bayt |

Üçü de aynı. Yani belgenin birinci sürümünde "anlamı değiştirmiyor, gecikmeyi
değiştiriyor" diye yazılan şey artık bir tahmin değil, ölçüm. Ölçüm altı bloğu
kapsıyor, bütün API yüzeyini değil.

### 4.2 Sunulan kipte üç şey kırılıyor

**4.2.1 Durum ölçümü sessizce yalan söylemeye başlıyor.** `remote_apis_url` ya da
`remote_environment_url` verildiğinde AppWorld süreç içi model koleksiyonunu
kurmuyor: `world.models is None`. `state_probe.snapshot` o durumda `{}` dönüyor,
`diff({}, {})` de `{}` dönüyor — `None` değil, boş sözlük. Bu deponun
sözleşmesinde boş sözlük **"ölçüldü, değişmedi"** demek; `None` "ölçülmedi"
demek. Yani `probe_state` açık kalırsa `steps.state_change` her adımda ölçüm
yapıldığını iddia eder ve hiçbir ölçüm yapılmamış olur.

Ölçütün kayıttaki ağırlığı ayrıca ölçüldü, çünkü "kaybediyoruz" ile "önemli bir
şey kaybediyoruz" aynı şey değil:

| Ölçülen | Sayı |
|---|---|
| Kayıttaki toplam adım | 4102 |
| Durumu ölçülmemiş adım (`NULL`) | 0 |
| Ölçüldü, değişmedi | 4074 |
| Durum değişti | 28 |
| **Yalnız durum ölçütü sayesinde duraklama sayılmayan adım** | **0** |

Yani durum ölçütü 4102 adımda durma kuralının kararını **bir kez bile**
değiştirmemiş. Tehlike kuralda değil, kaydın yalan söylemesinde. Sonda bu yüzden
kapatılmadı, HTTP üzerine taşındı (K-93, §11.2).

**4.2.2 Host tarafında sarmalanacak `Requester` kalmıyor.** Uzak ortam kipinde
host'un `AppWorld` nesnesinde `requester` niteliği hiç yok
(`hasattr(world, "requester")` yanlış), `shell` de `None`. `ApiCapture` bugün
`Requester` sınıfının metotlarını sarmalıyor; sarmalanacak sınıf artık
konteynerin içinde. Bu, K-A'nın gerekçesinin ölçülmüş hâli.

**4.2.3 Günlükleri kim yazıyor.** `environment_io.md` ve `api_calls.jsonl` ortam
sunucusunun kendi `save_logs` çağrısıyla yazılıyor; ortam sunucusu konteynere
girdiğinde o iki dosya konteynerin içinde yazılır. Çıktı veritabanları öyle
değil: onları host tarafındaki API sunucusu yazıyor (`POST /dbs/save`), ve
doğrulayıcı zaten host tarafında `evaluate_dataset` ile o veritabanlarını
okuyor. Yani **verdict konteynere taşınmıyor**; taşınan şey iki günlük dosyası,
ve o ikisi epizot bittikten sonra `podman cp` ile alınıyor (K-94, §11.3).

### 4.3 Gecikme

| Ölçüm | Değer |
|---|---|
| Loopback API gidiş dönüş (n=30, curl süreç başlatması dahil) | ortanca 3,54 ms (3,19 – 15,80) |
| Adım başına, çekirdek saatiyle, süreç içi | ortanca 0 ms |
| Adım başına, çekirdek saatiyle, uzak API | ortanca 10 ms |
| Adım başına, çekirdek saatiyle, uzak ortam + uzak API | ortanca 10 ms |
| Kayıttaki tipik adım süresi | ≈ 2,2 s |

Çekirdek saati `/proc/uptime`'dan okunuyor ve çözünürlüğü 10 ms; tablodaki 0 ve
10 aynı büyüklüğün iki yuvarlaması olabilir. Söylenebilecek dürüst şey: eklenen
maliyet adım süresinin binde birkaçı. Vekil ikinci bir sekme eklediği için bu
sayı yaklaşık iki katına çıkar ve yine aynı mertebede kalır.

Bir yan bulgu: süreç içi ve uzak API kiplerinde freezegun host sürecinin saatini
donduruyor, `time.perf_counter` sıfır dönüyor. Uzak ortam kipinde host'un saati
donmuyor. Depo zaten çekirdek saatini kullandığı için kayıtlar etkilenmiyor;
ama host tarafında duvar saatini okuyan bir şey yazılırsa davranışı kipe göre
değişir.

### 4.4 Bellek — K-C'nin ilk sayısı

| Süreç | RSS |
|---|---|
| API sunucusu (bütün uygulama veritabanları bellekte) | 745 MiB |
| Ortam sunucusu (bir dünya, altı kod bloğu, `models=None`) | 185 MiB |

Konteynere giren şey ortam sunucusu, yani ölçülen taban **185 MiB**. 512 MiB
sınırı bu tabanla mümkün ama cömert değil: yaklaşık 320 MiB pay kalıyor ve
ajanın kodu liste biriktirmeye başlarsa o pay hızla erir. K-C'nin istediği ölçüm
tam bu: epizot içinde tepe kullanımı ölç, üstüne pay koy, künyeye yaz.

API sunucusunun 745 MiB'i host tarafında kalıyor ve konteyner sınırına girmiyor.

---

## 5. Verilen dört karar ve her birinin gerektirdiği

### K-A — Kayıt loopback üzerinde bir vekilde yapılacak

Konteyner vekile bağlanır, vekil AppWorld sunucusuna iletir ve iki yönü de
kaydeder. S-16 verisi (yanıt gövdesi ve durum kodu) korunur, kayıt konteynerin
dışında durur, kalkanın doğal yeri orası olur.

Üç şart:

1. **Şeffaflık testi.** Aynı görev doğrudan ve vekil üzerinden koşulur,
   yörüngeler birebir aynı olmalı. Referansı §7.
2. **Vekil `MEASUREMENT_DEFINING_PATHS` listesine girer.** Ölçümü tanımlayan bir
   yol, çünkü kaydın kendisi oradan geçiyor. Liste K-76'da daraltıldı ve
   daraltma listenin kendi eksiğini bulmuştu; bu ekleme aynı sınıftan.
3. **Vekilin sürümü künyeye yazılır.** Kalkanın yaptığı gibi: değişen bir şey
   varsa kayıttan okunabilsin.

### K-B — Konteynerde tam `appworld` paketi

İnce RPC istemcisi ajanın gördüğü arayüzü sessizce değiştirir; K-19'un şartı
aynı mesajların gitmesi ve aynı metnin dönmesi. Paket 5,9 MiB, yani imajın
büyük kısmı paket değil bağımlılıklar (`site-packages` 316 MiB).

`data/` dizini 198 MiB ve konteynerin ihtiyacı olan kısmı görev dizini
(64 KiB) ile görev verisi. Salt okunur bağlama ile mi verilecek, imaja mı
gömülecek — soru 5'in altında.

### K-C — Kaynak sınırları ölçülecek

Tehdit modelinin bıraktığı boşluk sayılarla doldurulacak. Birinci sayı §4.4'te:
ortam sunucusunun tabanı 185 MiB. Kalanı epizot koşarken ölçülecek: tepe RSS,
tepe süreç sayısı, tmpfs kullanımı, adım süresi. Ölçüm bittikten sonra sınır
"ölçülen tepe + pay" olarak yazılacak ve künyeye girecek.

Belgenin birinci sürümündeki tablo artık **öneri değil, sınanacak başlangıç
noktası**:

| Sınır | Başlangıç | Ölçülecek |
|---|---|---|
| Bellek | 512 MiB | Epizot içi tepe RSS |
| Süreç (pids) | 128 | Tepe süreç sayısı |
| Süre | adım başına 60 sn | Adım süresi dağılımı |
| Disk (tmpfs) | 64 MiB | Tepe tmpfs kullanımı |
| CPU | 1 çekirdek | Adım süresine etkisi |

### K-D — Sınırlar bağlayıcı olmayacak ve bu gösterilecek

Gösterge: sınıra çarparak biten epizot oranı. Sıfıra yakın değilse sınır
gevşetilir ve sonuç alt sınır olarak işaretlenir. K-60 ile aynı sınıf: bir sınır
bağlayıcıysa sonucu model değil sandbox belirler.

Bunun kayda geçmesi için sonlanma sebeplerine sandbox kaynaklı olanların
eklenmesi gerekiyor; bugünkü üç sebep `step_ceiling`, `no_progress`,
`agent_finished`.

---

## 6. Vekilin göreceği trafik bugünkü sarmalayıcının gördüğünden farklı

Kalkanın yüklemi saf fonksiyon olarak yazıldı ve montaj noktası taşınırken
mantığının değişmemesi gerekiyor. Ölçüm bu taşımanın dört yerde trafiği
değiştirdiğini gösteriyor; ikisi zararsız, biri kayda dokunuyor, biri tehdit.

### 6.1 `access_token` kayıtta zaten yok — zararsız

Vekil `Authorization: Bearer` başlığını gövdeden ayrı görür, yani gövdeden
okunan parametrelerde jeton olmaz. Kayıt bu yüzden değişecek sanılabilir.
Ölçüldü: **5261 eylemin 0'ında** `access_token` var. Sebebi
`Requester.prepare()`: jetonu bizim sarmalayıcının elinde tuttuğu **aynı
sözlükten** `pop` ediyor ve sarmalayıcı kaydı çağrı döndükten sonra alıyor. Yani
başlığa taşınma bugünkü kayıtta çoktan olmuş. Vekilin gördüğü gövde bugünkü
kayıtla bu eksende uyuşuyor.

### 6.2 Telin dışında üretilen çağrı yok — zararsız

`Requester` üç durumda HTTP'ye hiç çıkmadan yanıt üretiyor: geçersiz URL (404),
sözlük olmayan gövde (400), ASCII olmayan jeton (400). Vekil bunları göremez.
Ölçüldü: kayıttaki durum kodları yalnız 200 (4489), 401 (503), 422 (235),
409 (34). 400, 404, 405 hiç yok, ve `Exception` sayısı 772 = 503+235+34. Yani
115 epizotta **5261 eylemin hepsi sunucuya ulaştı**; bu sınıf hiç ateşlememiş.
Ateşlerse `RecordingAgent`'ın sayım karşılaştırması ayrışma olarak yazar, yani
sessiz kalmaz.

### 6.3 GET parametrelerinin türü telde kayboluyor — kayda dokunuyor

`Requester._get` gövdeyi sorgu dizesi olarak gönderiyor
(`requests.get(url, params=data)`). Sorgu dizesinde tür yok: `page_index=0`
telde metin. Bugünkü kayıt tür taşıyor ve durma kuralının gördüğü kimlik o
sözlüğün JSON'u.

| Ölçülen | Sayı |
|---|---|
| Toplam eylem | 5261 |
| GET eylem | 4242 |
| **Metin olmayan değer taşıyan GET** | **1090 (GET'lerin %25,7'si)** |
| Değer türleri | str 4316, int 1417, bool 172, list 26, float 22, None 3 |

Vekil sorgu dizesinden sözlüğü metin değerlerle kurarsa 1090 eylemin kimliği
değişir. Durma kuralı kimlikleri epizot içinde karşılaştırdığı için davranışı
büyük ölçüde korunur, ama **bugüne kadarki 115 epizotla karşılaştırılabilirlik
kırılır**: derleyicinin madenlediği gövdeler, hata indeksinin `argument_shape`
alanı ve durma kuralının kalibrasyonu hep tür taşıyan kimlikten çıktı.

Tür bu yüzden rotanın kendi imzasından türetiliyor, ve karar 5261 eylemin
hepsinde doğrulandı: imzayla 5261/5261 eşleşiyor, imzasız kontrol kolunda 1090
eylem eşleşmiyor (K-92, §11.1).

### 6.4 Sunulan kip host tarafında bir yönetim yüzeyi açıyor — tehdit

`appworld serve apis` on iki uygulamayı `/{app}` altına bağlıyor, ama kökte
kendi yönetim rotaları da var. Sayıldı: **21 rota**. İçlerinden ölçümü
bozabilenler:

| Rota | Ne yapıyor |
|---|---|
| `POST /dbs/save` | **Gönderilen yola veritabanı yazıyor.** Yazan süreç host tarafındaki API sunucusu. |
| `POST /dbs` | Veritabanı yollarını değiştiriyor |
| `POST /seed` | Rastgelelik tohumunu değiştiriyor |
| `POST /date_time`, `DELETE /date_time` | Dünyanın saatini değiştiriyor |
| `POST /activate/task/{task_id}` | Etkin görevi değiştiriyor |
| `POST /activate/supervisor/{id}` | Etkin süpervizörü değiştiriyor |

Üç şey bir arada tehdit oluyor:

1. Bu rotalar **bugünkü kayıtta hiç görünmüyor**, çünkü AppWorld onları
   `Requester` üzerinden değil düz `requests.post` ile çağırıyor
   (`appworld/apps/lib/apis/local_remote.py`). Yani sarmalayıcımızın hiç
   görmediği bir trafik sınıfı var ve vekil onu görecek.
2. Konteynerin içindeki kod, `apis.*` ile aynı kanaldan bu rotalara ulaşabilir.
   `POST /dbs/save` ile host tarafındaki sunucuya istediği yola yazdırabilir.
   Salt okunur kök ve ağ yalıtımı bunu durdurmaz, çünkü yazan süreç konteynerin
   içinde değil.
3. Sunucular `host="0.0.0.0"` ile bağlanıyor ve bu **yapılandırılabilir değil**:
   `appworld/serve/apis.py:31` ve `appworld/serve/environment.py:301` içinde
   gömülü, bayrağı yok. Yani API sunucusu bütün arayüzlerde dinliyor. S-47'nin
   sorusu burada da geçerli ve cevabı bu kez tersi: bu değer bizim değil,
   referansın gömülü davranışı.

**Sonuç:** K-A seçeneği 3 yalnız kaydı korumak için değil, tehdit modelinin
birinci tehdidini kapatmak için de gerekli çıktı. Vekil konteynerin API
sunucusuna tek yolu olmak zorunda, ve yönetim rotalarını yapısal olarak
geçirmemeli. Bu bir kalkan kararı değil: referans ajan `apis.*` üzerinden bu
rotalara ulaşamaz, yani onları kesmek meşru bir yörüngeyi değiştiremez. Yine de
"değiştiremez" bir iddia ve testi §8'in yedinci testi (K-95, §11.4).

### 6.5 Vekil ham URL değil istek yolunu kaydetmeli

`split_endpoint` göreli yol bekliyor: `/venmo/x` → `venmo`, `x`. Mutlak URL
verilirse `http://127.0.0.1:8123/venmo/x` → uygulama adı `http:` olur ve
uç nokta çözümlemesi sessizce çöker. S-32 tam bu sınıftan bir arızaydı. Vekil
istek yolunu kaydederse bugünkü ayrıştırıcı hiç değişmeden çalışır.

---

## 7. Şeffaflık testinin referansı

Yörünge özeti aracı zaten var: `scripts/check_determinism.py`,
`sha256(logs/environment_io.md)[:16]`. Ajanın gördüğü metnin tamamı o dosyada,
yani karşılaştırılacak şey doğru şey.

Demonun hangi epizodu kullanılacak sorusu ölçümle karşılaşınca ikiye ayrıldı.

| Aday | Çağrı | Neden yeterli / yetersiz |
|---|---|---|
| `0a9d82a_1` (demo, iki kol aynı yörünge) | 0 | Sıfır çağrı vekili hiç sınamaz |
| `1150ed6_2` (demo, iki kol aynı yörünge) | 2 | Sınar, ama iki çağrıyla |
| `0de03ea_1` kartlı kol (demo, en çağrı zengini) | 11 | İki kol aynı yörünge üretmedi, yani bu görevde tekrar kararlılığı ölçülmedi |
| `6104387_1` (determinizm ölçümü) | 20 | 6 tekrar, 1 farklı yörünge; 20 çağrı, hepsi 200 |
| `2a163ab_1` (determinizm ölçümü) | ≈19/koşu | 6 tekrar, 1 farklı yörünge; hata veren adımlar da var |

İki ayrı şey karışıyor: demonun `identical_trajectory` alanı **kartlı kol ile
taban kolun** aynı çıktığını söylüyor, tekrar kararlılığını söylemiyor. Tekrar
kararlılığı ölçülmüş görevler determinizm ölçümündekiler ve altı tekrarda tek
yörünge veriyorlar. Şeffaflık testi tekrar kararlılığına dayanıyor, o yüzden
referans `6104387_1` (K-96, §11.5).

Bir de "doğrudan" ne demek sorusu var. Vekili yalıtmak için "doğrudan" =
sunulan kip, vekil yok. Süreç içi kipten sunulan kipe geçiş ayrı bir
karşılaştırma, ve §4.1'de altı blokla ölçüldü. Yani üç kol: süreç içi, sunulan
kip, sunulan kip + vekil. İkisini tek testte birleştirmek bir fark çıktığında
onu atfedilemez hâle getirir.

---

## 8. Güvenlik testleri

Danışmanın Section D soruları, teste çevrilmiş hâlleriyle:

| Soru | Test | Geçme ölçütü |
|---|---|---|
| Host neden tehlikede | Konteynerden host dosya sistemine, kayıt veritabanına ve yapılandırmaya erişim denemesi | Hepsi başarısız |
| Fork bomb | `:(){ :\|:& };:` benzeri süreç patlaması | pids sınırı devreye girer, host etkilenmez, epizot temiz sonlanır |
| Disk doldurma | tmpfs'i doldurmaya çalışan yazma döngüsü | tmpfs sınırında durur, host diski etkilenmez |
| Konteyner root | Konteyner içinde root olma ve host'a yansıma denemesi | Kök yetkisiz eşleme sayesinde host'ta yetkisiz kullanıcı kalır |
| Ağ kaçışı | Loopback dışına, dış ağa ve host servislerine bağlanma denemesi | Yalnız izinli uygulama portları erişilebilir |
| Epizotlar arası kirlenme | Bir epizotta dosya bırakıp sonrakinde okuma denemesi | Okunamaz; konteyner her epizotta yeniden doğuyor |

**Testler geçmeden sandbox kullanılmıyor.** Ve testin ateşlediği görülmeden test
sayılmıyor: her testin önce korumasız ortamda **başarılı** olduğu gösterilecek,
sonra korumalı ortamda başarısız olduğu. Bu depoda bir korumanın yerinde
sayılması birkaç kez yanıltıcı çıktı.

§6.4 bir yedinci test getiriyor: konteynerin içinden `POST /dbs/save` denemesi.
Korumasız ortamda host'a dosya yazmalı, korumalı ortamda vekil tarafından
kesilmeli.

---

## 9. Konteyner testleri CI'da koşabilir — ölçüldü

Soru şuydu: podman GitHub Actions içinde çalışıyor mu. Çalışmıyorsa altı test de
yerel-yalnız listeye girer ve S-49'un "temiz kurulumda yeniden çalıştırıldı"
boşluğu büyür. Ölçüm iki koşuyla yapıldı; iş dalın push'unda ateşleyen geçici
bir iş, cevap alındıktan sonra siliniyor.

| Ölçülen | `ubuntu-24.04` koşucusu |
|---|---|
| podman | **var**, 5.8.4, `/usr/local/bin/podman` |
| Kök yetkisiz | `rootless=true`, `subuid runner:165536:65536` |
| cgroup | v2, devredilen denetleyiciler `cpu memory pids` |
| Çalışma zamanı / ağ arka ucu | `crun` / `netavark` |
| İmaj çekme ve koşma | çalışıyor, konteyner başlatma 0,09 – 0,13 s |

Beş koruma **ateşlerken** görüldü:

| Koruma | Kanıt |
|---|---|
| Salt okunur kök | `touch /kok-yazma-denemesi` → `Read-only file system` |
| Kök yetkisiz eşleme | konteynerde `uid=0(root)`, host'ta süreç sahibi `runner` |
| pids sınırı | `--pids-limit 32` altında `sh: can't fork: Resource temporarily unavailable` |
| Bellek sınırı | `--memory 64m` altında 256 MiB yazma `Killed`, `dd` çıkışı 137; sınırsız kolda aynı yazma başardı |
| tmpfs sınırı | `dd` çıkışı 1, dosya tam 8388608 baytta durdu |
| Epizotlar arası kirlenme | ikinci konteyner ilkinin `/tmp/iz` dosyasını bulamadı |

**Cevap: evet, altı güvenlik testi CI'da koşabilir.** Yerel-yalnız listeye
girmiyorlar ve S-49'un boşluğu büyümüyor.

**Birinci turda üç adım yeşil göründü ve hiçbir şey kanıtlamıyordu.** K-49
gereği ayrıca sorulduğu için yakalandı:

- Bellek testi `/dev/shm`in kendi 64 MiB varsayılanına çarpmıştı; 62,5 MiB
  yazıldı, sınıra hiç dokunulmadı. `--shm-size=512m` ile düzeltildi ve sınırsız
  bir kontrol kolu eklendi.
- tmpfs testinin çıkış kodu `tail`den geliyordu, `dd`den değil.
- Loopback testinde host'ta hiçbir şey dinlemiyordu; "bağlanamadı" boş bir
  kanıttı. İkinci turda host'ta gerçek bir dinleyici açıldı.

Bir sürüm asimetrisi kalıyor: yerelde podman 4.9.3 (apt), koşucuda 5.8.4. Ama ağ
arka ucu ikisinde de **netavark** ve §10'un ölçümü iki platformda aynı cevabı
verdi, yani asimetri kararı etkilemiyor.

---

## 10. Ağ politikası: `--network=none` artı salt okunur unix soket

Tehdit modeli "yalnız loopback, sabit uygulama portları" diyor. Şart şu:
konteyner **tam olarak tek host portuna** ulaşsın — vekile — başka hiçbir yere.

Dört kip iki platformda ölçüldü. Ölçen betik aynı:
`scripts/setup/measure_container_network.py`. Sayılar
`results/container-network.json`.

| Kip | Dış ağ | Host portu | Soket köprüsü | İki platformda |
|---|---|---|---|---|
| **A — `--network=none`** | **erişilemez** (`Network unreachable`) | erişilemez | **200** | aynı |
| B — varsayılan (netavark) | **erişilebilir** (1.1.1.1 → 403) | erişilemez | 200 | aynı |
| C — `slirp4netns:allow_host_loopback` | erişilebilir; host 10.0.2.2 üzerinden **açık** | açık | 200 | koşucuda `slirp4netns` yok (çıkış 127) |
| D — `pasta` | **erişilebilir** | erişilemez | 200 | aynı |

Dış ağa erişim üçünde de gerçek: 1.1.1.1'e yapılan istek **403** dönüyor, yani
istek internete çıkıp cevap alıyor. "Bağlanamadı" değil. Yalnız `none`
`Network unreachable` veriyor.

**Seçilen: A, artı salt okunur bağlanan bir unix soket.** Konteynerin içinde
soketi yerel bir TCP portuna bağlayan bir köprü koşuyor, çünkü referansın
`Requester`ı `requests` ile konuşuyor ve `requests` yalnız TCP biliyor.
`--network=none` altında `lo` ayakta kalıyor, yani o dinleyici çalışıyor.

Bir risk vardı ve ölçüldü: **unix sokete `connect` yazma izni istiyor, salt
okunur bağlama onu kesebilirdi.** Kesmiyor. `ro` bağlamada da bağlantı kuruldu ve
köprü üzerinden host 200 döndü — iki platformda da. Yani "tek kanal" şartı ile
"yazılabilir bağlama yok" kuralı çakışmıyor.

Köprü stdlib ile yazılıyor: imajda Python zaten var (K-B), yeni bağımlılık
eklenmiyor.

---

## 11. Beş sorunun cevabı

Beşi de karara bağlandı. İkisi cevaplanabilmek için ölçüm istedi ve ölçümler
alındı; ikisi de kararın şartını taşıyor, o yüzden sayılarıyla birlikte burada.

### 11.1 Tür rota imzasından türetiliyor (K-92)

Çeviriyi yapan şey bizim yazdığımız bir tablo değil, sunucunun kendi kullandığı
`ModelField.validate`. K-63'ün tekniğinin aynısı, yalnız yol parametresi yerine
sorgu parametresine uygulanmış hâli.

Doğrulama bedavaydı ve yapıldı — `scripts/setup/verify_wire_identity.py`
kayıttaki 5261 eylemin hepsini telden geçirip geri kuruyor:

| Kol | Kayıtlı kimlikle eşleşen |
|---|---|
| İmzadan tür türetilerek | **5261 / 5261** |
| İmzaya bakmadan (kontrol kolu) | 4171 / 5261 |

İmzasız kolda eşleşmeyen 1090 eylem, bağımsız olarak ölçülen "metin olmayan
değer taşıyan GET eylemi" sayısıyla birebir aynı. Kontrol kolu olmadan tam
eşleşme hiçbir şey kanıtlamazdı; K-49 bu ölçümün içine yerleştirildi.

Doğrulama bir ayrıntı buldu: `page_limit` alanı `int` ama üstünde `le=20` var ve
ajanın 50 yazdığı iki çağrıda doğrulama düşüyordu. Aranan şey geçerlilik değil
tür, o yüzden kısıt düştüğünde doğrudan bildirilen türe çevriliyor.

### 11.2 Durum sondası kapatılmıyor, HTTP'ye taşınıyor (K-93)

Sorulan şey buydu: sunulan kipte durum sondası ortama sorularak yapılabilir mi.
Yapılabiliyor, ve dört şey ölçüldü:

| Ölçülen | Sonuç |
|---|---|
| Ayrım gücü | `{"spotify": {"MusicPlayer": 1}}` — bugünkü sondayla aynı `app.Model` düzeyi |
| Duyarlılık | `set_volume` (satır sayısını değiştirmeyen `PATCH`) **görüldü**; bugünkü sonda onu göremiyor |
| Maliyet | çağrı başına **2,0–2,5 ms**, adım süresi ~2,2 s |
| Epizoda etkisi | sondalı ve sondasız koşuların geçen/düşen test kümeleri **birebir aynı** |

Dördüncüsü zorunlu bir kontroldü: sonda değişiklik kaydını tüketirse kapanışta
yazılan `model_hashes.json` eksik kalır ve doğrulayıcının
`models.changed_model_names()` testi yanlış düşerdi.

Yani durma kuralı **iki ölçütlü kalıyor**. Kapatma seçeneğinin eşdeğerliğinin
dayanağı olan sayı da kayda geçiyor: 4102 adımda durum ölçütü kuralın kararını
bir kez bile değiştirmemiş, yani kapatılsaydı da kuralın davranışı bu kayıtta
değişmezdi. Taşıma seçildi çünkü bedeli binde bir ve kazandığı şey `PATCH`
duyarlılığı.

Semantik farkı **yeni bir kolona** giriyor: `steps.state_change` işaretli satır
farkı taşıyor, özet tabanlı sonda "hangi model değişti" taşıyor. Aynı kolona iki
anlam koymak bu deponun kaçınmaya çalıştığı sessiz yalanın kendisi.

### 11.3 Günlükler `podman cp` ile alınıyor (K-94)

Yazılabilir bağlama yok. Konteyner dosya sistemi koşu boyunca salt okunur
kalıyor; iki günlük dosyası epizot bittikten sonra kopyalanıyor.
`experiments/outputs`u yazılabilir bağlamak birinci tehdidin tam yüzeyi: o dizin
doğrulayıcının okuduğu veritabanlarını da taşıyor.

### 11.4 Ağ: tek kanal, ve yönetim rotaları yapısal olarak kesiliyor (K-95)

`--network=none` artı salt okunur bağlanan bir unix soket. Ölçüm §10'da, iki
platformda aynı. Yirmi bir yönetim rotası vekilde sabit bir beyaz listeyle
kesiliyor.

Beyaz liste kalkanın yükleminden ayrı bir katman: **kalkan görev kapsamlı izin
veriyor** (hangi uygulamaya yazılabilir), **beyaz liste hangi rotaların var
olduğunu belirliyor**. İkisi karıştırılırsa kalkanın ölçülmüş maliyeti bu
filtrenin maliyetiyle toplanır ve ikisi de okunamaz hâle gelir.

### 11.5 Şeffaflık testi üç kollu, referans `6104387_1` (K-96)

Üç kol: süreç içi, sunulan kip vekilsiz, sunulan kip vekilli. Kip değişimi ile
vekil aynı testte karışmıyor.

Referans demodan değil determinizm ölçümünden geliyor: demonun aynı yörünge
üreten iki epizodu 0 ve 2 çağrı taşıyor ve hiçbir şeyi ayırt etmez. `6104387_1`
altı tekrarda tek yörünge veriyor, 20 çağrı taşıyor, hepsi 200.

`data/` dizini konteynere **salt okunur bağlanıyor**. Gömmek imaj damgasının
veriyi de kapsamasını sağlardı ama veriyi ikinci bir yerde çoğaltırdı; bağlama
tek kaynak bırakıyor ve veri sürümü künyede `appworld_version` ile birlikte
`data/version.txt`ten yazılıyor.

### 11.6 Güvenlik testleri beşinci CI kontrolü (K-97)

Mevcut "Testler" işinin içine girmiyorlar. "Dört CI kontrolü" betimleyici bir
kayıttı, korunacak bir kısıt değil: podman testleri test işini uzatır ve bir
düşüşün hangi katmandan geldiğini belirsizleştirir.

---

## 12. Kapsam dışı

- **Kalkanın uygulama kipi.** Gölge kip dışında bir kip yok (K-71) ve ikame
  yanıtın biçimi karara bağlanmadı. §6.4'ün yapısal filtresi bundan ayrı bir
  şey: kalkanın yüklemi değil, vekilin rota beyaz listesi.
- **Paralel epizot.** Sandbox paralelliği kolaylaştırıyor ama paralellik yerel
  koşuda ölçümü değiştiriyor (K-12 düzeltmesi). Ayrı iş.
- **Windows.** Sandbox Linux kararıydı (K-01). WSL içinde koşuyor.
- **Ölçüm koşusu.** Bu madde hiçbir ölçüm üretmiyor; ürettiği tek sayı sandbox'ın
  kendi maliyeti.

---

## 13. Teslim listesi

1. `Containerfile` — sürüm damgalı imaj, `appworld` paketi sabit sürümde, içinde
   soket köprüsü.
2. `src/zihin/sandbox.py` — konteyner yaşam döngüsü: epizot başına oluştur, kod
   çalıştır, günlükleri `podman cp` ile al, yık. Sınırlar yapılandırmadan.
3. `src/zihin/kayit_vekili.py` — unix soket üzerinde vekil: iki yönü kaydeder,
   tipi rota imzasından türetir, kalkanı çağırır, yönetim rotalarını beyaz
   listeyle keser. `MEASUREMENT_DEFINING_PATHS` listesine girer.
4. `config/sandbox.yaml` — kaynak sınırları, imaj damgası, soket yolu, ağ kipi.
   Ölçümü etkileyen her değer burada, ortamda değil.
5. Künyeye sandbox alanları: imaj damgası, sınırlar, sandbox sürümü, vekil
   sürümü, sunum kipi, ağ kipi.
6. Kayıt şemasına özet tabanlı durum kolonu (K-93) — `state_change`'in yanına,
   içine değil.
7. `tests/test_sandbox_security.py` — §8'deki altı test artı `POST /dbs/save`
   testi, her biri korumasız ortamda ateşlediği gösterilerek.
8. Şeffaflık testi — üç kol, referans `6104387_1`.
9. CI'a beşinci kontrol: sandbox işi (K-97).
10. `docs/04-threat-model.tr.md` güncellemesi: sayılar, dondurulmuş yapılandırma, ve
    §6.4'ün yeni saldırı yüzeyi.
11. `docs/09-limitations.tr.md` — ölçülemeyen ya da kapatılmayan ne kaldıysa.

---

## 14. Kodlamayı hâlâ bekleyen ölçüm

Beş soru kapandı, ama K-C'nin istediği sayılar kodlama bitmeden alınamaz: epizot
içi tepe RSS, tepe süreç sayısı, tepe tmpfs kullanımı ve adım süresi ancak
konteyner ayakta koşan bir epizottan ölçülür. §5'teki tablo o yüzden hâlâ
"başlangıç noktası" diyor, "sınır" demiyor. Sınır sayıları ölçümden sonra
yazılacak ve künyeye o hâliyle girecek; K-D'nin bağlayıcılık göstergesi de aynı
koşudan çıkacak.
