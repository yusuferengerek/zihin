# Kurulum sonrası 3 — Önyükleme öncesi üç koruma

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

Bu turda istenen üç şey vardı: önyükleme biriktirmesinin deneyin parçası
olmadığının yazılması, durma kuralına geçici bir eşik konması, ve yazma kümesi
kaydının ilk epizottan itibaren açılması. Üçü de bitti. Ayrıca artık varyans
ölçümü tek görevden çıkarılıp birkaç göreve yayıldı.

## Durum ölçümü — önce ne olmadığını buldum

Yazma kümesini kaydetmek için adım başına ölçülebilir bir durum imzası
gerekiyordu. İlk iki denemem işe yaramadı ve sebepleri kayda değer.

`model_hashes.json` bir şey değiştirmeyen koşularda `{}` dönüyor, yani hiç
çağrı yapmayan bir adım ile durumu değiştirmeyen bir adım aynı görünüyor.
`search_notes` ise sayfalanmış, ilk sayfada beş kayıt veriyor; sondaki
değişiklikler görünmüyor.

Çalışan imza canlı veritabanı sayımı oldu: `world.models.<app>.<Model>.count()`.
`create_note` çağrısından sonra `simple_note.Note.count()` 3083'ten 3084'e
çıkıyor. `state_probe.py` bunu her uygulama için toplayıp adım öncesi ve sonrası
farkı alıyor.

**Bu imzanın gördüğü ve görmediği.** Sayım ekleme ve silmeyi görüyor,
güncellemeyi görmüyor: bir notun metni değişirse sayı aynı kalıyor. Epizot
düzeyindeki `model_hashes.json` ikinci katman olarak duruyor ve güncellemeyi
yakalıyor. Adım düzeyinde tek katman var, bu yüzden sınır kodda ve şemada
yazılı.

**Okunamayan model `-1` yazılıyor, `0` değil.** Sebebi: `0` "hiç kayıt yok"
demek ve iki ardışık `0` "değişmedi" diye okunur. Okunamayan bir modelin
değişmediğini bilmiyoruz, o yüzden ayrı bir değer aldı.

`admin` ve `api_docs` altyapı uygulaması, taranmıyor.

**Şemada `state_change` üç hâl taşıyor.** `NULL` "ölçülmedi", `{}` "ölçüldü,
değişmedi", dolu sözlük "ölçüldü, şu kadar değişti". İlk ikisi
karıştırılmamalı; sütun yorumu bu yüzden şemada yorum satırı olarak duruyor.

## Durma kuralı

Kural: son `no_progress_limit` adımın hepsi ilerlemesizse epizot bitiyor.
Bir adım şu durumda ilerlemesiz sayılıyor — durum farkı boşsa **ve** ya hiç
eylem üretmemişse ya da ürettiği çağrıların hiçbiri başarılı olmamışsa.

Değer `config/recording.yaml` içinde `no_progress_limit: 4` ve künyeye
yazılıyor, yani hangi eşikle koşulduğu kayıttan geri okunabiliyor. Değer geçici;
kesin eşiği kurulum aşaması taraması verecek. Yapılandırma dosyasındaki yorum da
bunu söylüyor.

**Canlı doğrulama.** 1,5B `82e2fac_1` görevinde dört yüz bir alıp döngüye
giriyordu ve yirmi adımlık tavana kadar dönüyordu. Kural açıkken epizot dördüncü
adımda bitti:

```
epizot erken sonlandı: 4 adım üst üste ilerleme üretmedi; epizot sonlandırıldı.
adım            : 4
sonlanma sebebi : no_progress
```

Dört adımın dördünde de `state_change` `{}` ve üç eylemin üçü de 401 döndü.
Yani kural doğru sebeple ateşledi.

**Üretken adımları kesmiyor.** Aynı görev 7B ile koşulduğunda epizot dörtte
değil yedide bitti: 1-3 arası adımlar çağrı üretti, 4-7 arası boş geçti ve
pencere ancak orada doldu.

| Model | Adım | Adım başına eylem | Sonlanma |
|---|---|---|---|
| 1.5B | 4 | 0, 1, 1, 1 | `no_progress` |
| 7B | 7 | 1, 2, 1, 0, 0, 0, 0 | `no_progress` |

## Aşama 3'ün kabul ölçütüyle çakışma ve çözümü

Durma kuralı açılınca Aşama 3'ün "en az bir adım birden çok eylem üretmeli"
ölçütü 1,5B kayıtlarında sağlanamaz oldu: epizot, çok eylemli adımların
çıktığı bölgeye varmadan bitiyor.

Ölçütü gevşetmedim. Bunun yerine aynı görevi 7B ile kaydettim; orada ikinci adım
iki eylem üretiyor ve ölçüt sağlanıyor. Yani kabul ölçütü hâlâ gerçek bir
koşudan okunuyor, sentetik veriden değil.

Bu sırada koşucuda bir hata çıktı: `run_id` yalnız görev adından türüyordu, aynı
görevi ikinci bir modelle kaydedince birincil anahtar çakışıyor ve künye yazımı
düşüyordu. Kimliğe model eklendi.

## Kaydediciler tek yerde toplandı

`scripts/record_run.py` kendi `KaydedenAjan` sınıfını taşıyordu — kaydedici
pakete taşınırken kalmış bir kopya. O sınıf ne yakalayıcıyı ne durum ölçümünü ne
de durma kuralını tanıyordu. Silindi, betik paketteki `RecordingAgent`'ı
kullanıyor. Aynı kurulum `measure_models.py` ve `check_cold_determinism.py`
için de yapıldı.

## Artık varyans birkaç göreve yayıldı

Önceki turda ölçülen 1/20'lik ayrışma tek görevden (`82e2fac_1`) geliyordu.
Ölçüm beş farklı senaryodan birer göreve yayıldı, görev başına altı soğuk epizot
ve bir de ikinci tohum epizodu.

Ölçüm deneyin koşacağı rejimde yapıldı, yani durma kuralı açık. Kapalı ölçülürse
elde edilen gürültü tabanı analiz edilecek epizotları değil, tavana kadar dönen
daha uzun epizotları tarif eder.

### 1.5B

| Görev | Koşu | Farklı yörünge | Epizot uzunluğu | Boşaltma | İkinci tohum farklı |
|---|---|---|---|---|---|
| `82e2fac_1` | 6 | 1 | 4 adım | doğrulandı | evet |
| `692c77d_1` | 6 | 1 | 4 adım | doğrulandı | evet |
| `2a163ab_1` | 6 | 1 | 4 adım | doğrulandı | evet |
| `6104387_1` | 6 | 1 | 4 adım | doğrulandı | evet |
| `29caf6f_1` | 6 | 1 | 8 adım | doğrulandı | evet |

Otuz epizodun otuzunda da aynı görevin altı koşusu birebir aynı yörüngeyi verdi.
1.5B'nin artık varyansı beş görevde de sıfır, yani önceki turdaki sıfır ölçümü
göreve bağlı bir tesadüf değilmiş. Tohum ekseni beş görevde de canlı.

### 7B

| Görev | Koşu | Farklı yörünge | Epizot uzunluğu | Boşaltma | İkinci tohum farklı |
|---|---|---|---|---|---|
| `82e2fac_1` | 6 | 1 | 7 adım | doğrulandı | evet |
| `692c77d_1` | 6 | 1 | 6 adım | doğrulandı | evet |
| `2a163ab_1` | 6 | 1 | 20 adım (tavan) | doğrulandı | evet |
| `6104387_1` | 6 | 1 | 20 adım (tavan) | doğrulandı | evet |
| `29caf6f_1` | 6 | 1 | 4 adım | doğrulandı | evet |

**Önceki turdaki 1/20 ayrışma bu taramada hiç tekrarlamadı.** Beş görevde otuz
epizot, hepsi görev içinde birebir aynı. İki uzun epizot (yirmi adım, tavana
dayanan) da dahil, yani ayrışma fırsatının en çok olduğu koşularda bile sapma
çıkmadı.

Bu, önceki ölçümü çürütmüyor. Rejim değişti: durma kuralı açık ve epizotlar
kısaldı, dolayısıyla sapma için daha az adım var. Doğru okuma şu — **deneyin
koşacağı rejimde, beş göreve yayılmış otuz epizotta artık varyans sıfır.**
Gürültü tabanı bu ölçüme dayandırılacaksa dayanağı artık tek görev değil.

S-21 buna göre güncellendi.

## Taramanın yan ürünü: 1.5B'de kategori 4 oranı

Tarama artık varyans için koşuldu ama adım taksonomisini de topladı, ve oradaki
sayı beklediğimden büyük çıktı.

Otuz epizottaki 144 adımın **90'ı kategori 4**: kod çalıştı, hiç API çağrısı
üretmedi. Oran %62,5. Beş görevin üçünde (`692c77d_1`, `2a163ab_1`,
`6104387_1`) epizottaki **her** adım bu kategoride.

| Kategori | 1.5B adım | Oran | 7B adım | Oran |
|---|---|---|---|---|
| `execution_error_no_action` | 90 | %62,5 | 54 | %15,8 |
| `eylem_uretti` | 48 | %33,3 | 264 | %77,2 |
| `execution_ok_no_action` | 0 | %0 | 18 | %5,3 |
| `no_code` | 6 | %4,2 | 6 | %1,8 |
| **Toplam** | **144** | | **342** | |

Bu, S-20'de 3B için yazılan baskın hatanın 1.5B'yi de kapsadığını gösteriyor.
S-20 buna göre genişletildi.

Aynı tablo K-54'ün neden ayrı bir metrik istediğini de gösteriyor. İki model de
hiçbir görevi bitirmedi, yani başarı oranı ikisinde de sıfır. Ama kategori 4
oranları dört kat farklı (%62,5'e %15,8) ve 7B'nin adım sayısı 1.5B'nin iki
katından fazla. Tek sayıya bakan biri iki modeli aynı görürdü.

**Bir uyarı: eşik ile bu oran birbirini besliyor.** Dört adımlık eşik, ilk dört
adımı kategori 4 olan bir epizodu hemen kesiyor. O epizot beşinci adımda
toparlanacak olsaydı bunu göremezdik. Üç görevin %100 kategori 4 çıkması kısmen
bu kesmenin sonucu olabilir. Eşiği kesinleştirecek tarama bu etkileşimi ölçmeli:
aynı görevler kural kapalıyken de koşulup toparlanma olup olmadığına bakılmalı.
Şimdiki sayı bu yüzden bir üst sınır değil, eşiğe koşullu bir gözlem.

## Kararlar

- **K-52** — Önyükleme biriktirmesi deneyin parçası değil. `run_id` öneki
  `bootstrap-`, kütüphanesi atılıyor, ön kayda giren hiçbir sayı oradan gelemez.
- **K-53** — Ölçek ekseninde işletme ölçütü sansür oranı: taban koşulunda
  tavana dayanan epizot oranı %10'un altında olmalı. Tanı ile ölçüt ayrı şeyler.
- **K-54** — Kategori 4 oranı koşul başına raporlanıyor. Mekanizmanın çalışıp
  çalışmadığını başarı oranından önce gösteren tanı metriği.
- **K-55** — Güç hesabı ham kazanç üzerinden değil, çıkarılan nicelik üzerinden.
- **K-56** — `irrelevant_retrieval` isteğe bağlı değil, ana tasarımda zorunlu.

## Sınırlar

- **S-20** — 3B'nin baskın hatasını yönergeye eklenecek iyi biçimli tek bir
  örnek kapatabilir. Yönerge değiştirilmiyor (K-19); ayrım
  `irrelevant_retrieval` koşuluna bırakıldı.
- **S-21** — Artık varyans ölçümü tek görevden geliyordu. Bu turda yayıldı;
  sonuç yukarıdaki tabloda.

## Yerel-yalnız kontroller

11 Ağustos 2026, `MODEL_SERVER_URL` verili ve AppWorld verisi indirilmiş
durumda koşuldu.

| Kontrol | Sonuç |
|---|---|
| `ruff check` | temiz |
| `ruff format --check` | temiz |
| `pytest` | 128 test geçti, atlanan yok |
| import | `zihin`, `zihin.state_probe`, `zihin.recording_agent` |
| `uv build` | tamam |

Bunlara ek olarak kayıt uçtan uca koşuldu: 1.5B ve 7B ile iki epizot şemaya
yazıldı, künyedeki eşik geri okundu, `state_change` dört adımın dördünde de
dolu ve eylem durum kodları (401) kayıtta.

## Sırada ne var

Zincirin üçüncü adımı, yani önyükleme biriktirmesi. Üç koruma da yerinde:
durma kuralı açık ve eşiği künyede, yazma kümesi ilk adımdan itibaren
kaydediliyor, biriktirmenin deney dışı olduğu K-52'de yazılı.

Eşiğin kesin değerini verecek tarama da bekliyor. Yukarıdaki uyarı gereği o
tarama iki şeyi birlikte ölçmeli: farklı eşiklerde sansür oranı, ve kural
kapalıyken epizotların toparlanıp toparlanmadığı.
