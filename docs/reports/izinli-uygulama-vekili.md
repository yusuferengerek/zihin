# İzinli uygulama vekilinin isabeti — 14 Ağustos 2026

Kalkanın izinli uygulama kümesi görev metninden türetiliyor. Bu rapor o
türetmenin isabetini ölçüyor.

Kod: `src/zihin/allowed_apps.py`. Ölçüm: `scripts/setup/measure_app_proxy.py`.
Ham çıktı: `results/app-proxy-accuracy.json`.

## Vekil bir yaklaşım değil, şartnamenin kendisi

Kilitli karar kalkanın birinci aşamasını şöyle tanımlıyor: okuma serbest, görev
metninde geçmeyen uygulamaya yazma girişimi işaretlenir. İzinli küme dolayısıyla
**görev metninden** geliyor.

`ground_truth/required_apps.json` bu modülün **doğrulayıcısı, girdisi değil.**
Kümeyi ground truth'tan türetmek kalkana kıyaslama dışında sahip olmayacağı bir
oracle vermek olurdu, ve aşağıdaki isabet sayısı da anlamsızlaşırdı.

**Kodun daha önce depoda olmaması bir boşluktu.** Vekil Aşama 2'de yazılmış ve
sayıları rapora girmiş ama kodu sürüm kontrolüne alınmamıştı. Ölçümü etkileyen
bir bileşen sürüm kontrolü dışındaydı. Şimdi depoda ve
`MEASUREMENT_DEFINING_PATHS` listesinde.

## Ölçüm

Referans listesi taşıyan tek iki bölme `train` ve `dev` (S-03). 147 görev.

| Ölçüt | Değer |
|---|---|
| Tam eşleşme | 111/147 = **%75,5** |
| Ortalama Jaccard | 0,857 |
| Referansın tamamen kapsandığı görev | 111/147 = %75,5 |

Aşama 2'nin kaydettiği sayı %75,5 ve Jaccard 0,878'di. Tam eşleşme birebir
yeniden üretildi; Jaccard'daki küçük fark yüzey biçimi listesinin
farklılığından.

### Hata profili

Tek bir isabet sayısı çağıranın işine yaramıyor; iki hata yönü asimetrik.

**Kaçan uygulama** — kalkan meşru bir yazmayı engeller. Yanlış pozitif.

| Uygulama | Kaçak |
|---|---|
| `phone` | 30 |
| `venmo` | 6 |
| `file_system` | 3 |

**Fazladan uygulama** — kalkan gayrimeşru bir yazmayı geçirir. Yanlış negatif.

| Uygulama | Fazla |
|---|---|
| `simple_note` | 6 |

Tam eşleşme ile tam kapsama sayısının aynı çıkması şunu söylüyor: eşleşmeyen 36
görevin hepsinde en az bir kaçak var. Yani **%24,5 yanlış pozitif üst sınırı**
kalkanın bugünkü hâliyle taşıdığı bedel.

## Kaçakların sebebi ölçüldü, ve ikisi farklı sınıf

### `phone`: gerçek bir sınır, vekilin kusuru değil

Otuz kaçağın hepsi aynı biçimde. Örnek yönergeler:

> `2a163ab_1` — yönerge metni AppWorld lisansı gereği çıkarıldı; özgün metnin
> özeti `sha256:8171d51f01bd488de4138feca6b3ffb19c89efb3b854da8f3e2729b19e156ca2` (`S-79`).

> `afc0fce_1` — yönerge metni AppWorld lisansı gereği çıkarıldı; özgün metnin
> özeti `sha256:2b1127911151dd1e34ed76e403c1109b09a26be2a41769650c880141d85e2166` (`S-79`).

Görev "roommates", "siblings", "coworkers" diyor. Bu ilişkiler `phone`
uygulamasının kişi kayıtlarında duruyor, ama yönerge uygulamayı **hiç
adlandırmıyor**.

Hiçbir metin tabanlı vekil bunu kurtaramaz. Görev metni ihtiyaç duyduğu her
uygulamayı adlandırmıyor ve bu **gerçek bir dağıtım özelliği**, deneysel bir
artefakt değil: gerçek bir kullanımda da elde yalnız kullanıcının cümlesi olur.

### `simple_note`: yüzey biçiminin belirsizliği

Altı fazlanın hepsi `note` sözcüğünden. Bu alanda "note" belirsiz: venmo
işleminin de bir "note"u var, ve yönergeler "with a description"/"note" diye
geçiyor.

**Skoru görerek ayar yapılmadı.** Yüzey biçimi listesi ölçümden önce yazıldı ve
ölçümden sonra değiştirilmedi. Değiştirmek doğrulayıcıya uydurmak olurdu ve
%75,5'i anlamsız kılardı.

## Kalkan açısından sonucu

Kalkanın isabeti çıkarımın isabetiyle **sınırlı**, ve sınır yukarıdaki iki
sınıfın toplamı. Kaçan uygulama meşru bir yazmayı engeller; fazladan uygulama
gayrimeşru bir yazmayı geçirir.

Bu sınır S-03'e yazıldı. Gölge modu tam da bunun için var: kalkan kararını
kaydeder ama engellemez, ve yanlış pozitif oranı mevcut epizotlar üzerinde
ölçülür.
