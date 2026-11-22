# Mimari

## İki güven bölgesi

**Host güvenilir ve kalıcı.** Politika modeli, kayıt defteri, getirici,
derleyici ve kalkan burada koşuyor.

**Sandbox güvenilmez ve her epizotta yeniden doğuyor.** Kök yetkisiz konteyner,
salt okunur kök, ağ ad alanı düzeyinde politika (yalnız loopback üzerinde sabit
uygulama portları), bellek, süreç, süre ve disk sınırlı, imaj sürüm damgasıyla
sabit.

Ayrımın sebebi tehdit modelinde: `04-threat-model.tr.md`.

## Yedi bileşen

### Politika

Sıradaki araç çağrısını üretir. **Mimarideki tek değiştirilebilir slot.**
Koşullar arasında değişen tek şey buraya giren bağlam; bileşenin kendisi
değişmiyor.

### Getirici

Göreve bakıp beceri ve hata kartı çıkarır. **Sembolik eşleşme kullanıyor,
anlamsal gömme kullanmıyor.**

Gömmenin reddedilme sebebi tasarımın parçası: gömme çalışma zamanına yeni bir
kiralık bileşen ve yeni bir karıştırıcı ekliyor. Kazancın ne kadarının
mekanizmadan, ne kadarının gömme modelinden geldiği ayrılamaz hâle gelirdi. Bu
bir sınırlama olarak `09-limitations.tr.md` içinde yazılı.

### Kalkan

Eylemi yürütmeden önce süzen bir yüklem. **Beş koşulun hepsinde açık.**

Statik argümanlı çağrılar beceri başlamadan denetleniyor, dinamik argümanlılar
kendi yürütülmelerinden hemen önce. Atomiklik yalnız model çağrısı düzeyinde bir
özellik, denetim düzeyinde değil.

### Sandbox

Çağrıyı yalıtılmış ortamda yürütür.

### Doğrulayıcı

Sonucu geçti veya kaldı bilgisine indirir. **Kıyaslamadan geliyor, proje içinde
yazılmıyor.** Kendi doğrulayıcımızı yazsaydık ölçtüğümüz şey kendi tanımımız
olurdu.

### Kayıt defteri

Her gözlem ve eylemi sırayla yazar. **Yalnızca ekleme yapılır, tek gerçek
kaynağıdır.**

### Derleyici

Beceri kütüphanesini ve hata indeksini üretir. **Çevrimdışı ve belirlenimci,
model kullanmıyor.** Derleyicinin içine model koymak, ölçtüğümüz kazancın bir
kısmını o modele kaptırmak demek.

## Kayıt ve projeksiyon ayrımı

Beceri kütüphanesi ve hata indeksi **türetilmiş projeksiyon**. Silinip kayıttan
yeniden hesaplanabilirler.

**Ayrım testi:** bu tabloyu silsem kayıttan geri getirebilir miyim.

Ham parametreler bu yüzden özet değeriyle değil tam hâliyle saklanıyor.
Normalizasyon kuralı değişecek ve projeksiyonun kayıttan yeniden
hesaplanabilmesi gerekiyor.

## Bağlam yönetimi

Montajcı **saf bir fonksiyon**, beş bölüm taşıyor.

**Sabit blok hiç düşmüyor:** sistem yönergesi, görev metni, kimlik bilgisi,
getirilen kartlar.

**Baş ve kuyruk turları korunuyor.** Yalnız ortadaki turlar boşaltılıyor ve
yerine işaret konuyor. Boşaltma toptan: bütçenin dörtte biri kadar yer bir
kerede açılıyor.

**Uzun araç çıktıları bağlama girerken kesiliyor**, taşma anında değil.

### Politika kasten aptal

Alaka puanı yok, özet yok, model yok.

Sebebi ölçüm: akıllı bir bağlam politikası kendi başına bir mekanizma olur ve
becerilere atfedilen kazancın bir kısmını o yapar.

### Ölçülmüş sayılar

Adım başına yaklaşık 5958 girdi tokenı (Aşama 2). Bu sayı **birikmiş geçmişi de
içeriyor**, yani sabit bloğun kendisi değil.

Sabit blok ayrı ölçüldü (`results/context-cost.json`, ölçüm üretim yolunda
doğrulandı):

| | Jeton, medyan | 32K pencerenin payı |
|---|---|---|
| Sabit blok, kartsız | 3172–3185 | %9,7 |
| Kart bloğu, k=5+5 | 125–264 | %0,4–0,8 |
| İkisi birlikte | 3296–3447 | %10,1–10,5 |

Yani sabit blok **onda bir**, kartlarla birlikte yine onda bir. Buradaki cümle
önceden "beşte biri, kartlarla dörtte biri" diyordu ve ölçülmemişti; düzeltmesi
S-46, kararı K-88.

**Bağlayıcı sınır bu pencere değil.** Referans iskele bağlamı karakterle kesiyor
ve 50000 karakter ölçülen içerikte 12799 jeton, pencerenin %39'u (S-47). Yani
etkin bağlam 32K değil, 13K civarı ve pencere hiç dolmuyor.

**Montajcının bütçesi bu yüzden karakterle yazılıyor** (K-90). Bağlayıcı birim o;
jetonla yazan bir bütçe pencerenin %61'ini var sanar. Tavanın değeri
`config/recording.yaml` içinde ve künyeye yazılıyor, çünkü değişmesi etkin bağlamı
değiştiriyor. Ölçüldü: kayıtlı 105 epizodun 31'i tavanı geçti.

### Bilinen çakışma

Referans iskelenin kendi bağlam kesme mantığı var ve eski gözlemleri bir yer
tutucuyla değiştiriyor. Bizim montajcımız devreye girdiğinde ikisi çakışacak.
Şimdi dokunulmuyor; risk `09-limitations.tr.md` S-07 altında ve karar `08-decisions.tr.md`
K-26'da.
