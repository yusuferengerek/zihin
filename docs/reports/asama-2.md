# Aşama 2 raporu — AppWorld olgu raporu

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor. Ölçümlerin
tamamı `docs/appworld-facts.tr.md` içinde; burada özeti ve karşılaştığım
sürprizler var.

## Kabul ölçütü ne diyordu

> Belge yazılmış, her madde ya ölçülmüş bir sayı ya da gerekçeli bir ÖLÇÜLEMEDİ
> taşıyor.

Üstüne bu aşamaya iki madde eklendi: S-11 kapatılacak ve on iki epizotluk
ölçümdeki tek çağrılı epizot açıklanacak.

## Yedi sorunun durumu

| Soru | Durum |
|---|---|
| 1. Bölmeler ve görev sayıları | ölçüldü |
| 2. Zorluk bölmesi ne içeriyor | ölçüldü, uygulama adları için vekil kullanıldı ve vekil sınandı |
| 3. Referans çözümler | ölçüldü |
| 4. Görev başına API çağrısı dağılımı | ölçüldü, kaynağından |
| 5. Veritabanı sıfırlaması | ölçüldü |
| 6. Okuma ve yazma sınıflandırması | ölçüldü |
| 7. Tur başına API çağrısı | ölçüldü ama **kullanılamaz**, gerekçesi aşağıda |
| 8. Motorun ayrılabilirliği | incelendi |

## Karşılaştığım sürprizler

### Referans çözümler elimizdeymiş

S-02, `appworld download data` varsayılan kipte indiği için referans çözümlerin
elimize hiç geçmeyebileceğini söylüyordu. Yanlışmış. 147 görev `full` kipte
geliyor ve o 147 görev tam olarak train ile dev'in kendisi.
`metadata.json` içindeki `mode` alanı bunu açıkça yazıyor.

Bunun iki sonucu oldu. Üçüncü soru tahminle değil sayıyla cevaplandı: referans
çözüm başına ortalama 53,44 API çağrısı. Dördüncü soru da kendi koşularımdan
değil kaynağından cevaplandı, çünkü `metadata.num_api_calls` 732 görevin
hepsinde var ve 147 görevde `api_calls.json` uzunluğuyla birebir tutuyor.

### Eğitim bölmesi ortamın yarısını bile görmüyor

`required_apps.json` üzerinden saydım. Train ve dev'in 147 görevi, on bir
kullanıcı uygulamasının yalnız beşine dokunuyor: `spotify`, `phone`, `venmo`,
`file_system`, `simple_note`. `amazon`, `gmail`, `splitwise` ve `todoist` o 147
görevin hiçbirinde geçmiyor.

Bu, ikinci sorunun cevabını ilk baktığımdan daha keskin yapıyor. Zorluk bölmesi
yalnız daha çok uygulamaya dokunmuyor, eğitimde hiç bulunmayan uygulamalara
dokunuyor.

### Vekil ölçüm ilk hâliyle çöp çıktı

Test bölmelerinde `required_apps.json` yok, o yüzden uygulama adlarını çıkarmak
için vekil yazmam gerekti. İlk vekilim `evaluation.py` dosyasında uygulama adı
arıyordu. Referans listesi olan 147 görevde sınadım: 147'sinin sıfırında tam
isabet, Jaccard 0,227.

İki arızası vardı. `admin` ve `supervisor` her görevde yanlışlıkla sayılıyordu,
çünkü onlar değerlendirme altyapısının import'ları. Ve gerçek uygulamaların
yaklaşık yarısını kaçırıyordu.

Altyapı uygulamalarını eleyince yüzde 46,9'a çıktı. Görev yönergesinden okuyan
ikinci vekil yüzde 75,5 verdi, Jaccard 0,878. Rapora giren sayılar bu vekilden
ve hata profili de rapora yazıldı.

Sınamasaydım ilk vekilin ürettiği tabloyu olgu diye yazacaktım.

### Yedinci sorunun sayısı kullanılamaz

On iki epizot koştum. 223 model turunda toplam 1 API çağrısı çıktı, tur başına
0,0045. On bir epizot hiç API çağırmadan yirmi adımlık tavana dayandı.

Sayı ortamı değil modeli ölçüyor. `qwen2.5-coder:1.5b` bu görevde çoğunlukla
çalışmayan kod üretiyor. Ölçek ekseninin en küçük noktası taban etkisine
yapışmış durumda ve orada ölçülecek bant yok. S-14 olarak açtım; ölçüm Aşama
4'te 3B ve 7B ile tekrarlanacak.

Kullanılabilir tek sayı adım başına 5958 girdi tokenı. Bu bağlam bütçesi için
doğrudan kullanılabilir ve Aşama 1'de tahmin ettiğim 3800 rakamını düzeltiyor.

### Zaman ölçümü freezegun yüzünden bozuldu

Beşinci sorunun maliyet ölçümü ilk denememde anlamsız sayılar üretti. Dünya
açılışı 1684409978 saniye sürüyor görünüyordu. Sebebi AppWorld'ün freezegun ile
zamanı süreç geneli dondurması; `time.monotonic` de donuyor ve ölçüm görevin
simüle tarihine kayıyor.

Modülü import etmeden önce saklanan referans da kurtarmadı, yama daha derin.
Ölçümü `/proc/uptime` okuyarak yaptım. Sonuç: dünya açılışı medyan 0,150
saniye, kapanış 0,008 saniye.

## S-11 kapandı

Aşama 1'de aynı seed ve sıcaklıkla koşulan üç epizot 19, 1 ve 19 API çağrısı
vermişti. Bu, üç tohumlu varyans planının dayandığı seed kontrolünün hiç
olmadığı anlamına gelebilirdi.

Ölçtüm, öyle değilmiş. Seed geçiyor. Oynaklığın kaynağı modelin bellekte yüklü
olup olmaması.

Yol biraz dolambaçlı oldu ve ara sonuçlar yanıltıcıydı. İlk sınamam litellm
üzerinden aynı seed'le iki çağrı yaptı ve farklı çıktı verdi. Sonra Ollama'nın
kendi ucunda aynı sınama tuttu. Bu, suçlunun litellm olduğunu gösteriyordu ve
öyle yazsaydım yanlış olurdu. Deseni görmek için litellm üzerinden dört çağrı
yaptım, dördü de birbirinin aynısı çıktı ve yerli uçtan gelenle eşleşti.
Ayrışan tek şey bütün dizinin ilk çağrısıydı.

Sonra modeli açıkça boşaltıp sınadım. İki turda da aynı sonuç: soğuk çağrı
`0b9d5bfca170070e`, ısınmış çağrılar `fc4f39f3c60221c4`. İkisi de kendi içinde
kararlı.

Epizot düzeyinde de aynı. Aynı görevi soğuk, ısınmış, soğuk, ısınmış sırasıyla
koşturdum. İki soğuk koşu birebir aynı yörüngeyi verdi ve 19 API çağrısı yaptı.
İki ısınmış koşu birebir aynı yörüngeyi verdi ve 1 çağrı yaptı.

Ölçüm `scripts/check_determinism.py` içinde ve tekrarlanabilir.

**Kalan belirsizliği saklamıyorum.** "Isınmış" tek bir durum değil. Yukarıdaki
ısınmış koşu 1 çağrı verdi ama on iki epizotluk ölçümde aynı görev yine ısınmış
modelle koşuldu ve 0 çağrı verdi. Aradaki fark modelin daha önce hangi istekleri
gördüğü ve bunu istemciden görmüyoruz. S-13 olarak açtım.

Tasarıma sonucu şu: tekrarlanabilirlik için her epizottan önce modeli boşaltmak
gerekiyor. Bu K-21'in `keep_alive` gerekçesiyle çelişiyor, takas artık ölçülmüş
ve karar Aşama 4'ün.

## Tek çağrılı epizot açıklandı

Gerçek oynaklık değil, yakalanmamış bir arıza biçimiymiş. Görev `692c77d_1` idi;
yönerge metni AppWorld lisansı gereği çıkarıldı, özgün metnin özeti
`sha256:a950a91993090db7f485be0426584f1860ec42f296285eec93e92d53eb7bc1cf` (`S-82`).

Adım 1'de model `for playlist in playlists:` yazdı, `playlists` tanımlı değildi,
yürütme `NameError` ile düştü ve hiçbir eylem üretilmedi. Adım 2'de model hatayı
`playlists = []` yazarak düzeltti. Döngü hiç dönmedi, ortam `Execution
successful.` dedi. Adım 3'te model işin bittiğine hükmedip
`apis.supervisor.complete_task()` çağırdı. Kaydedilen tek API çağrısı bu.

Epizot dışarıdan temiz görünüyor. Üç adım, hata yok, tamamlandı bildirimi var.
Oysa hiçbir şey yapılmadı.

Adım 1 sizin tanımladığınız dördüncü kategoriye giriyor. Adım 2 girmiyor, çünkü
yürütme hata vermedi. Beşinci bir etiket önerdim ve K-36'ya yazdım: yürütme
başarılı ama hiç eylem üretilmedi. İkisini ayırmak gerekiyor. Yürütme hatası
modelin kod yazamadığını söyler, boş başarı ise modelin görevi sessizce
etkisizleştirdiğini söyler ve doğrulayıcıya kadar hiçbir yerde alarm üretmez.

## Karara bağlananlar

- **K-36.** Adım düzeyi taksonomisi beş kategori taşıyor.
- **K-37.** Bağlam penceresi sunucu tarafındaki `OLLAMA_CONTEXT_LENGTH` ile
  veriliyor. Koşu başına doğrulanacak ve künyeye yazılacak. A-05 kapandı.
- **K-22.** Sunucu betikten ve oturumdan bağımsız başlatılacak.
- **K-21.** Yeniden açıldı, kararı Aşama 4 verecek.
- **S-02** kısmen çürüdü, **S-03** aşıldı, **S-11** kapandı. Yerlerine **S-13**
  ve **S-14** açıldı.

## Yerel-yalnız kontroller

Son koşu: `2026-08-10T22:59:31+03:00`, commit `8c1697b`. Bir test geçti, yirmi
test elendi.

## Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet, iki ölçüm betiği |
| Testi yazıldı | Bu aşamanın çıktısı belge. Ölçümlerin kendisi `scripts/check_determinism.py` ve `scripts/measure_episodes.py` ile tekrarlanabiliyor |
| Loglandı | CHANGELOG girdisi yazıldı |
| Belgesi yazıldı | `docs/appworld-facts.tr.md`, 08-decisions, 09-limitations, PROJECT_STATUS |
| Hata durumu düşünüldü | Vekil ölçüm referans kümede sınandı, tutmasaydı soru ÖLÇÜLEMEDİ olarak kapanacaktı |
| PR üzerinden gözden geçirildi | PR açıldı |
| Temiz kurulumda baştan çalıştırıldı | CI AppWorld dahil kuruyor, dört kontrol yeşil |
