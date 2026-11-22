# Bant taraması, düzeltilmiş durma kuralıyla

**Seri 2** (`results/zihin-2.sqlite`), önek `bant3`, 13 Ağustos 2026.

Bant taraması S-27 yüzünden tekrarlandı: ilk tarama eski durma kuralıyla koşulmuş
ve otuz epizodun on altısı `no_progress` ile kapanmıştı, on beşi düzeltilmiş
kuralla kesilmeyecek olanlardı. Ön koşul kapısı o sonuca dayanarak ateşlemişti.

Değişen tek şey durma kuralı: uç nokta kümesi ölçütü ve eşik 15. Model, görevler,
tohumlar, görev başına tavan, çıktı bütçesi ve doğrulayıcı aynı.

## Sonuç: aynı

| | Eski tarama (seri 1) | `bant3` (seri 2) |
|---|---|---|
| Geçen | **0/30** | **0/30** |
| Dereceli skor | 6/152 = %3,9 | 5/152 = %3,3 |

**Sonuç yeniden üretti.** Düzeltilmiş kural ne ikili başarıyı ne de dereceli
skoru anlamlı biçimde değiştirdi. S-27'nin kirlilik endişesi meşruydu ve
ölçülmesi doğruydu; sonucu değiştirmedi.

**Ama ön koşul kapısı henüz tam doğrulanmadı ve bu açıkça yazılıyor.** Yirmi altı
epizot durma kuralıyla kesildi, yani bu otuz epizodun çoğu da tavanına kadar
gitmedi. Düzeltilmiş kural doğru sınıfı kesiyor — sonlanma sınıfının yer
değiştirmesi bunu gösteriyor — ama "kesilen epizotlar devam etseydi de sıfır mı
kalırdı" sorusu bu taramadan cevaplanamıyor. Kural-kapalı koşu tam olarak o
soruyu kapatıyor.

## Bant başına

| Bant | n | Geçen | Anlamlı test |
|---|---|---|---|
| 1-10 | 6 | 0 | 0/25 |
| 11-20 | 6 | 0 | 4/36 |
| 21-40 | 6 | 0 | 0/31 |
| 41-89 | 6 | 0 | 1/30 |
| 90+ | 6 | 0 | 0/30 |

## Sonlanma sebebi: sınıf yer değiştirdi

| Sonlanma | Eski kural | Düzeltilmiş kural |
|---|---|---|
| `no_progress` | 16 | **26** (%87) |
| `step_ceiling` | 9 | **0** |
| `agent_finished` | 5 | 4 |

Eski kuralda tavana çarpan dokuz epizot, düzeltilmiş kuralda durma kuralına
takılıyor. **Yeni kural tam da o "üretken görünüp hiçbir yere varmayan" sınıfı
yakalıyor:** on beş ardışık adımda yeni uç nokta yok ve durum değişmiyor.

**Bu, sonuçtan bağımsız bir bulgu.** Bu model sınıfının baskın arızası bütçe
tükenmesi değil, döngüye girme. Adım tavanını büyütmek bu sınıfa bir şey
kazandırmaz — tavana zaten çarpılmıyor.

## Epizot süresi

`duration_seconds` yalnız ajan döngüsünü ölçüyor. Ana koşu tahmini için gereken
gerçek duvar saati, künyedeki `wall_clock_utc` üstünden hesaplandı.

| | Saniye |
|---|---|
| Ajan döngüsü, ortanca | 39 |
| Ajan döngüsü, ortalama | 53 |
| Ajan döngüsü, en kısa / en uzun | 13 / 159 |
| **Epizot başına gerçek duvar saati** | **69** |
| Bunun ajan dışı kısmı (model yükleme, ortam kurulumu, doğrulama) | 14 (%20) |

Otuz epizot 33,1 dakika sürdü. **Ajan döngüsü üstünden yapılan bir tahmin %20
eksik çıkar.**

Bu sayıların bir uyarısı var: epizotların %87'si on beş adım civarında kesildi,
yani süreler kesilmiş epizotların süreleri. Kural-kapalı koşu bittiğinde kesilmemiş
epizot süresi de elde olacak ve ana koşu tahmini onunla yapılmalı.

## Kesinti dayanıklılığı

Otuz epizodun künyesi tek bir açılış kimliği taşıyor (`7e28e0b1`), yani tarama
kesintisiz koştu ve epizot kümesi dikilmiş değil. Bu, `boot_id` alanının ilk
kullanımı.

## Kural-kapalı koşu: birinci yorum ateşledi

Tetikleyici sonuç sıfır çıktığı için ateşledi ve `no_progress` ile kapanan 26
epizot kural kapalı olarak (eşik 0) tekrar koşuldu. Üç yorumun kuralı koşudan
önce yazılmıştı.

**Kural kapalıyken de sıfır: 0/26.** Yirmi beşi tavanına kadar gitti, biri ajan
tamamladı bildirerek kapandı.

| | Kural açık | Kural kapalı |
|---|---|---|
| Geçen | 0/26 | **0/26** |
| Dereceli skor (bu 26 epizot) | 0/139 | 1/139 |
| Toplam adım | 420 | 2023 |

**Birinci yorum:** durma kuralı sebep değil, 0/30 temiz, ön koşul kapısı sağlam
veriye dayanmış oldu.

Üçüncü yorum ateşlemedi. Dereceli skor 0/139'dan 1/139'a çıktı; bir epizotta bir
test. "Belirgin yükseliş" değil.

### Kural ne kesmiş: neredeyse hiçbir şey

Kesim noktasından sonra atılan 1603 adımda:

| | |
|---|---|
| Hiçbir şey olmayan epizot | **24/26** |
| Yeni uç nokta | 5 (iki epizotta) |
| Durum değiştiren adım | **0** |
| Kazanılan anlamlı test | 1 |

Sıfırların ölçüm boşluğu olmadığı ayrıca doğrulandı: aynı epizotlarda kesim
öncesi 62 yeni uç nokta sayılıyor ve `state_change` hiçbir adımda NULL değil.
Alet çalışıyor, kesimden sonra kaydedecek bir şey bulmuyor.

Bir şey olan iki epizot: `09b0ee6_1` 134 ek adımda 3 yeni uç nokta buldu ve hiçbir
test kazanmadı; `8ce6779_1` 43 ek adımda 2 yeni uç nokta buldu ve yedi anlamlı
testin birini geçti. **Kuralın toplam bedeli 139 testten biri.**

### Yapısal bulgu: model ya tutunuyor ya döngüye giriyor

| Alt küme | Dereceli skor |
|---|---|
| Durma kuralıyla kesilen 26 epizot | **0/139** |
| Normal biten 4 epizot | **5/13** |

Taramanın bütün dereceli skoru, normal biten dört epizottan geliyor. Kesilen
yirmi altısı, tavana kadar koşturulduklarında bile, anlamlı testlerin hiçbirini
geçmiyor. Arada bir orta bölge yok.

### Kesinti ve devam: dikiş veride

Koşu 21/26'da dışarıdan sonlandırıldı — OOM değil (`dmesg` temiz, 7,8 GB'ın 6
GB'ı boş), WSL o anda düşmemişti (`boot_id` denetimde değişmemişti), Python
istisnası yok. Oturum düzeyinde bir sonlandırma.

Küme sıfırdan koşulmadı, epizot düzeyinde devam edildi. Sebep zaman değil: ana
koşunun ihtiyaç duyacağı devam yolu şimdiye kadar yalnız kâğıt üzerindeydi ve
hatalarını altı epizotluk bir kurulum koşusunda bulmak, kırk saatlik ana koşunun
ortasında bulmaktan ucuz.

Dikiş veriden okunuyor:

| Commit | Epizot | Açılış |
|---|---|---|
| `6f14db6` | 20 | `7e28e0b1` |
| `79c43bd` | 6 | `41763e55` |

`79c43bd` yalnız devam mantığını ve testlerini ekliyor; ajan döngüsüne, tohuma,
tavana ve durma kuralına dokunmuyor. Atlamanın kalan epizodu değiştiremeyeceği
ayrı bir testle sabitlendi.

### Ana koşu tahmini

Kırk saatlik eski sayı, Aşama 5'in tek görevlik 24–72 saniyelik **ajan döngüsü**
ölçümüne dayanıyordu. Elimizde artık iki gerçek dağılım var ve ikisi de duvar
saati.

| Rejim | Epizot başına | 3000 epizot |
|---|---|---|
| Kural açık, takılan model (bant3) | 69 sn | **57 saat** |
| Tutunan model (sınır kontrolü, 30 epizot) | ~130 sn | ~107 saat |
| Kural kapalı, hepsi tavana kadar | 346 sn | **288 saat — üst sınır** |

Üst sınır işaretli, çünkü ana koşuda kural açık olacak. Ama alt sınır da yanıltıcı:
57 saat hiçbir şey yapmayan bir modelin sayısı. Ana eksende tutunan bir model
seçilirse epizotlar uzar ve gerçek değer orta satıra yaklaşır.

**Kırk saat her hâlükârda az.** En iyimser rejimde bile 57 saat.

### Kestirim yeniden yapıldı, 14 Ağustos

Yukarıdaki tablo iki yerden eskidi: eşik 15'ten 40'a çıktı (K-64) ve adım
dağılımı artık **uygulanan** kuralın oynatılmasından geliyor, amaçlananın
değil (S-32).

**Duvar saatinin yeri ölçüldü ve şüpheli değil: %99'u model üretimi.** Kayıt
katmanı adım başına 0,08 saniye, yani %1-2, ve bağlam büyüdükçe büyümüyor.
Kodda hızlandırılacak bir şey yok.

**Adım maliyeti eğrisi.** Bağlam her adımda büyüdüğü için i'nci adımın maliyeti
`c(i) = 3,296 + 0,0182·i` saniye; toplam süre `D(n) = 3,296·n + 0,0091·n(n+1)`,
yani adım sayısında ikinci dereceden. Düz hesap ("ortalama adım süresi çarpı
adım sayısı") 20 adımda %6 fazla, 150 adımda %26 eksik tahmin ediyor. Yani
düzeltme kural-kapalı rejimde önemli, kural-açık rejimde değil.

Eğrinin R²'si 0,044. Yani biçimi doğru ama kestirim gücü zayıf: belirsizliği
adım sayısı değil epizot heterojenliği belirliyor. Bu yüzden nokta kestirim
değil aralık veriliyor.

| Eşik | Ortalama adım | Nokta | %5 | %95 |
|---|---|---|---|---|
| 8 | 12,0 | 34,3 | 28,0 | 41,1 |
| 10 | 13,7 | 39,3 | 32,4 | 47,2 |
| 12 | 15,3 | 44,2 | 36,7 | 53,1 |
| 15 | 17,7 | 51,4 | 42,5 | 61,7 |
| 20 | 21,6 | 63,2 | 52,0 | 75,3 |
| Kapalı | 68,5 | 243,9 | 170,8 | 325,8 |

4000 tekrarlı bootstrap, sabit tohum. Belirsizliğin iki kaynağı da içeride:
hangi otuz görev (epizotlar yerine konarak) ve maliyetin eğri etrafında
saçılması (gözlenen/öngörülen oranı, %5'te 0,49, ortancada 0,82, %95'te 2,29).

**Planlama sayısı üst yüzdelikten alınıyor**, nokta kestirimden değil: artık
dağılımı sağa çarpık, yani eğri tipik epizodu fazla, kuyruğu eksik tahmin
ediyor.

**Eşiğin bedeli ölçülü.** Beş birim yaklaşık on iki saat. Eşik 40'ta ana koşu
nokta 106 saat, %95 dilim 129 saat; eşik 15'te 51 ve 62 olurdu. Aradaki 55 saat
bilerek ödeniyor ve gerekçesi K-64'te.

### Yerel donanım: kapanmış bir hipotez

Elli yedi saatin CPU'ya düşmüş bir modelden gelip gelmediği soruldu ve ölçüldü.
Gelmiyor: `qwen2.5-coder:7b-instruct-q4_K_M`, 32768 bağlam ve q8_0 KV ile
**29/29 katman GPU'da**, `size` = `size_vram` = 5,16 GB, yani %100. KV cache
952 MiB ve o da kartta. Üretim 50 jeton/sn, prefill 2255 jeton/sn. Önek
önbelleği de çalışıyor: ikinci turda 2149 jeton "işlendi" ama prefill süresi
0,04 saniye.

Elli yedi saat zaten bir GPU sayısı. Bu kaldıraçta bedava kazanç yok.

## Ne kirlenmedi

Ön kontrol epizodu (`bant3-onkontrol-024c982_1`) taramanın parçası değil ve
yukarıdaki hiçbir sayıya girmiyor; ayrı bir önek taşıyor. Görevi kaydedicinin
baştan sona yazdığını göstermekti, üç adımlık tavanla koştu.
