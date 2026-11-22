# Tehdit modeli

Bu belge sandbox ve kalkanın neye karşı kurulduğunu yazıyor.

## Neye karşı korunuyoruz

Ajanın ürettiği kod güvenilmez. Kaynağı bir dil modeli, doğrulanmamış, ve
epizot boyunca değişiyor. Tehdit kötü niyet değil, **denetimsiz eylem**: modelin
istemeden geri alınamaz bir şey yapması, ölçümü bozması ya da host tarafına
sızması.

Üç somut tehdit:

1. **Host tarafına sızma.** Ajanın kodu kayıt defterine, derleyiciye ya da
   yapılandırmaya erişirse ölçüm kendi kendini yazar.
2. **Epizotlar arası kirlenme.** Bir epizodun bıraktığı durum sonrakine geçerse
   epizotlar bağımsız olmaktan çıkar ve eşleştirilmiş tasarım bozulur.
3. **Geri alınamaz yan etki.** Kıyaslamanın durumunu değiştiren bir çağrı,
   doğrulayıcının hükmünü de değiştirir.

## Sandbox

Kök yetkisiz konteyner. Salt okunur kök. Ağ ad alanı düzeyinde politika: yalnız
loopback üzerinde sabit uygulama portları. Bellek, süreç, süre ve disk sınırlı.
İmaj sürüm damgasıyla sabit.

**Her epizotta yeniden doğuyor.** Bu ikinci tehdide karşı asıl savunma.

### Kurulmuş hâli

Ağ politikası harfiyen uygulandı: konteynerin **hiç ağı yok** (`--network=none`) ve
tek kanalı salt okunur bağlanan bir unix soket. "Yalnız loopback" cümlesi bu
kipte tam olarak doğru — dış ağ, host portları ve ağ geçidi adı üçü de erişilemez,
ve ölçüldü (WSL ve GitHub koşucusu, `results/container-network.json`). Diğer üç
kip — varsayılan netavark, `pasta`, `slirp4netns` — dış ağa çıkıyor, o yüzden
yapılandırma başka bir değeri kabul etmiyor.

Sınırların **sayıları henüz dondurulmadı.** `config/sandbox.yaml` başlangıç
noktalarını taşıyor ve dosya bunu açıkça söylüyor. K-C tahmin değil ölçüm
istiyor: epizot içi tepe RSS, tepe süreç sayısı, tepe tmpfs kullanımı. İlk gerçek
okuma alındı — bellek 161,7 MiB / 536,9 MiB, süreç 4, ağ giriş çıkış 0B — ama tek
epizottan ve model çağrısı olmadan. Sınır sayıları model koşusundan sonra
yazılacak ve künyeye o hâliyle girecek.

### Sunulan kip yeni bir saldırı yüzeyi açtı

Tehdit modelinin ilk hâli konteynerin **dışarı** ne yapabileceğini sayıyordu.
Sandbox kurulurken üçüncü bir yol çıktı ve konteynerin dışına hiç çıkmıyor:
AppWorld'ün API sunucusu, on iki uygulamanın yanında kökte **yirmi bir yönetim
rotası** sunuyor. `POST /dbs/save` gönderilen yola veritabanı yazıyor ve yazan
süreç host tarafındaki sunucu; `POST /seed`, `POST /date_time` ve
`POST /activate/task/{id}` doğrudan ölçümü bozuyor. Konteynerin içindeki kod bu
rotalara `apis.*` ile aynı kanaldan ulaşabiliyor, ve salt okunur kök ile ağ
yalıtımı bunu durdurmuyor çünkü yazan süreç konteynerin içinde değil.

Sunucuların bağlanma adresi de bizim elimizde değil: `uvicorn.run(host="0.0.0.0")`
AppWorld'ün içinde gömülü ve bayrağı yok.

**Kapatan şey vekil.** Konteynerin API sunucusuna tek yolu o, ve yönetim
rotalarını gövde alanlarına bakarak süzüyor. Hepsini kesmek mümkün değil (S-50):
ortam sunucusunun kendisi on bir yönetim çağrısı yapıyor. Kaçış yolunun durduğu
yer `to_db_home_path` alanının tam eşleşme şartı.

**Bu katman kalkandan ayrı.** Kalkan görev kapsamlı izin veriyor — hangi
uygulamaya yazılabilir. Vekilin beyaz listesi hangi rotaların var olduğunu
belirliyor. İkisi karıştırılırsa kalkanın ölçülmüş maliyeti bu filtrenin
maliyetiyle toplanır.

### Konteynerin içi güvenli değil, ve olması amaçlanmıyor

Ortam sunucusu ajanın kodunu aynı süreçte yürütüyor, yani ajan o sürecin
yapabildiği her şeyi yapabiliyor (S-51). Bu K-B'nin doğrudan sonucu: konteynerde
tam paket olacaksa kodu yürüten şey de o paket. Korunan şey host — kayıt
veritabanı, doğrulayıcı ve API sunucusunun yönetim yüzeyi dışarıda, ve dünyaya
yapılan her değişiklik vekilden geçmek zorunda.

## Kalkan

Eylemi yürütmeden önce süzen bir yüklem, beş koşulun hepsinde açık.

**Denetim zamanlaması argümanın türüne bağlı.** Statik argümanlı çağrılar beceri
başlamadan denetleniyor; dinamik argümanlılar kendi yürütülmelerinden hemen
önce, çünkü değerleri ancak o anda biliniyor.

**Atomiklik yalnız model çağrısı düzeyinde bir özellik, denetim düzeyinde
değil.** Bir beceri atomik çağrılıyor ama içindeki her çağrı ayrı ayrı
denetleniyor.

### Okuma/yazma yüklemi

Yüklem API dokümanlarındaki `method` alanına dayanıyor. Alan 473 API'nin
yüzde yüzünü kapsıyor.

Varsayımı — hiçbir GET ucunun durumu değiştirmediği — sınandı ve yanlış çıktı.
Statik tarama on beş GET ucunun yazma çağrısı içerdiğini gösterdi. Ayrıntı ve
üç sistematik grup `08-decisions.tr.md` K-41'de.

**Yazma kümesi `statik ∪ ampirik`.** İki kaynağın kör noktaları farklı yerde:
canlı sayım güncellemeyi göremiyor, statik tarama yardımcı fonksiyona
devredilen çağrıları göremiyor.

### Kalkan ihlalleri hata indeksine doğrudan gitmiyor

İndekse girmesi için aynı kalıbın kalkanın engellemediği bir durumda da
başarısızlıkla sonuçlanmış olması gerekiyor. Kalkan sinyali tek başına kayıt
üretmiyor, sadece güçlendiriyor. Gerekçe `07-failure-taxonomy.tr.md` içinde.

## Reddedilen savunma: cezalandırma

Zararlı eylemin ceza ile öğretilmesi reddedildi.

İki sebep. Bir eylemi cezalandıracak kadar iyi tespit edebilen sistem, onu
engelleyebilecek kadar da iyi tespit ediyor demektir; o hâlde engellemek varken
cezalandırmak gereksiz. Ve ceza ödül sinyaline karışırsa ajan zarardan kaçınmayı
değil **tespitten kaçınmayı** öğrenir.

## Bu belgenin sessiz kaldığı yer

Sandbox imajının somut yapılandırması, kaynak sınırlarının sayısal değerleri ve
kalkanın istisna listesinin dondurulmuş hâli burada değil. Sandbox katmanı henüz
kurulmadı; kurulduğunda bu belge o sayılarla tamamlanacak.
