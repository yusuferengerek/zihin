# Ölçülebilir bant taraması — 7B, referans uzunluğa göre tabakalanmış

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

Soru: deney yapılabilir mi. Sansür ölçümü üç modelde de %100 çıkmıştı ve 7B de
dahildi. Mekanizma becerileri yalnız başarılı epizotlardan madenciliyor, yani
başarı sıfırsa madencilenecek korpus yok (K-57).

## Önce tasarım gözetimi

Ölçek ekseni üç yerel kuantalanmış modele kurulurken AppWorld'ün yayımlanmış
taban oranlarına bu model sınıfı için hiç bakılmamıştı. Sonradan bakıldı;
`test_normal`, pass@1:

| Model | Görev tamamlama |
|---|---|
| Mistral 7B | %0,0 |
| Qwen3-8B, AWQ 4-bit, 32K bağlam | %3,0 |
| Qwen3-8B, FP16, 12K bağlam | %5,4 |
| DeepSeek-Coder 33B Instruct | %7,1 |
| LLaMA-3-70B-Instruct | %20,8 |
| GPT-4o | %48,8 |

Kaynaklar: <https://arxiv.org/abs/2407.18901>,
<https://arxiv.org/html/2604.11465v2>.

Bizim birincil modelimiz `qwen2.5-coder:7b-instruct-q4_K_M`, yani 7B ve dört
bit kuantalanmış. En yakın iki nokta %0,0 ve %3,0. Sınır S-23 olarak yazıldı.

## Tasarım

Bölme `test_normal`, çünkü bant sorusu değerlendirme örneklemi hakkında ve
değerlendirme oradan çekiliyor (K-42). test_normal'ın referans uzunlukları
train'inkinden kısa; train'de ölçmek yapılabilirliği olduğundan kötü
gösterirdi.

Otuz görev, bant başına altı, çapa `metadata.num_api_calls` (K-44). Seçim
rastgele değil: bant içinde görev adına göre sıralanıp eşit aralıkla alındı,
yani tekrar üretilebilir.

**Tavan görev başına.** `2 × çapa`, en az 20, en çok 150 model çağrısı. Sabit
tavan bandı ölçmez: çapası 195 olan bir görevde 20 model çağrısı görevi değil
tavanı ölçer. Sansür ölçümü tam olarak bu hatayı taşıyordu (S-22).

Durma kuralı açık, soğuk rejim, taban koşulu.

## Bant büyüklükleri, bütün bölme

| Bant | test_normal'daki görev |
|---|---|
| 1-10 | 17 |
| 11-20 | 37 |
| 21-40 | 74 |
| 41-89 | 32 |
| 90+ | 8 |

Toplam 168 görev, medyan çapa 30, en kısa 6, en uzun 130.

## Sonuç: ölçülebilir bant yok

| Bant | n | Geçen görev | Anlamlı test | Oran | Tavana dayanan | Tavan sınırına dayanan |
|---|---|---|---|---|---|---|
| 1-10 | 6 | 0 | 0/25 | %0,0 | 1 | 0 |
| 11-20 | 6 | 0 | 4/36 | %11,1 | 2 | 0 |
| 21-40 | 6 | 0 | 0/31 | %0,0 | 3 | 0 |
| 41-89 | 6 | 0 | 1/30 | %3,3 | 1 | 2 |
| 90+ | 6 | 0 | 1/30 | %3,3 | 2 | 6 |

Otuz epizot, **geçen görev sıfır**. Anlamlı testlerin 6/152'si geçildi, yani
%3,9.

**1. Bant başına başarı oranı: beş bantta da sıfır.** İkili başarı için
Clopper-Pearson tek yanlı %95 üst sınırı %9,5. Tarama "oran sıfır" ile "oran
%3" arasını ayıramaz: gerçek oran %3 olsaydı otuz görevde sıfır geçiş görme
olasılığı %40. Söylediği şey oranın %9,5'in altında olduğu, ki yayımlanmış
tabanlarla (bu sınıf için %0,0 ve %3,0) tutarlı.

**2. En kısa bantta 17 görev var** (bütün `test_normal`, örneklem değil). Bant
büyüklükleri yukarıdaki tabloda.

**3. Kısmi tamamlama resmî olarak dereceli değil, ama dereceli skor
kurulabiliyor.** `task_goal_completion` görev başına `success` boole'unun
yüzdesi, `scenario_goal_completion` senaryo içindeki minimum — ikisi de ikili.
Buna karşılık `TestTracker` her gereksinimi etiketliyor: `no_op_fail` hiçbir şey
yapmayan ajanın düşürdüğü test, `no_op_pass` hiçbir şey yapmasa da geçen test.
Dereceli skor `no_op_fail` testlerinin geçilen oranı.

Ayrım boş değil: bu otuz epizotta 37 `no_op_pass` testi geçildi ve hiçbiri
ilerleme kanıtı değil. Düzeltilmemiş bir skor onları sayardı.

**4. Geçen epizotta harcanan model çağrısı yok, çünkü geçen epizot yok.**
Bunun sonucu K-43'e dokunuyor: tavan çarpanı `k`, geçen epizotların çağrı
sayısından seçilecekti. O veri üretilemedi.

## Bunun üç yola söylediği

**Birinci yol — örneklemi kısa görevlerden çekmek — bu veriyle
desteklenmiyor.** En kısa bant hem ikili başarıda hem dereceli skorda sıfır
çıktı, üstelik tavan orada en cömerti: çapa 6-9 iken tavan 20, yani `k` 2,2 ile
3,3 arasında. O bandın altı epizodunun yalnız biri tavana dayandı. Yani sıfır
sonucu tavandan değil.

Dereceli skorun sıfırdan farklı olduğu üç görevin üçü de kısa bantta değil:
çapaları 16, 87 ve 94. Kısa görevlerin daha kolay olduğuna dair bir işaret bu
taramada yok.

**İkinci yol — dereceli sonuç — sinyal taşıyan tek değişken.** İkili başarı otuz
epizotta sabit sıfır, yani varyansı yok ve üzerinde test kurulamaz. Dereceli
skor görevler arasında değişiyor: 0/6'dan 4/6'ya. Az ama sıfır değil.

**Üçüncü yol** taramanın kapsamı dışında.

## Beşinci kategori canlı çıktı

Otuz epizodun beşi `agent_finished` ile bitti: ajan görevi bitirdiğini bildirdi,
doğrulayıcı geçirmedi. K-53 sansürü sonlanma sebebine bağlasaydı bu beş epizot
sansürsüz sayılırdı. Kalanı 16 `no_progress` ve 9 `step_ceiling`.

## Ölçümün sınırları

Bant başına altı görev. Bir bandın oranı ±birkaç görevlik gürültü taşıyor;
11-20 bandındaki %11,1'in tamamı tek bir görevden (`1150ed6_1`, 6 testin 4'ü)
geliyor.

Uzun bantlar tavan sınırına dayandı. `2 × çapa` kuralı 150 model çağrısında
kesildi; 90+ bandının altı epizodunun altısında ve 41-89 bandının ikisinde
sınır bağladı. O iki bandın sıfırı tavandan da gelebilir. Kısa bantlarda böyle
bir kuşku yok.

Model tek: 7B. 1.5B ve 3B taranmadı, çünkü soru en yetenekli noktanın bant
üretip üretmediğiydi.

## Yerel-yalnız kontroller

11 Ağustos 2026: `ruff check` temiz, `ruff format --check` temiz, 133 test
geçti ve atlanan yok, import ve build tamam. Otuz epizodun otuzu da şemaya
hükmüyle birlikte yazıldı; ham çıktı `results/bant-taramasi.json`.

## Sırada ne var

Karar sizin. Tarama üç yoldan birincisini zayıflattı, ikincisini tek yaşayabilir
seçenek olarak bıraktı.

İkinci yol seçilirse ön kaydın yeniden yazılması gerekiyor: sonuç değişkeni,
hipotez ifadesi, güç hesabı ve K-43'ün çarpan seçimi. Çarpan artık geçen
epizottan seçilemez, çünkü geçen epizot yok; yerine dereceli skorun tavana göre
doyma noktası kullanılabilir.

Önyükleme biriktirmesi K-57 ile durduruldu ve bu tarama onu geri açmıyor.
