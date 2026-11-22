# Kurulum araçları

Buradaki betikler **kurulum aracı**, deney yolunda değil. Deney matrisine
girmiyorlar ve ürettikleri sayılar sonuç iddiası taşımıyor.

Ayrım K-52'nin önyükleme için kurduğu ayrımın aynısı: aracı ayarlamak için
koşulan ölçüm, aracın çıktısını ölçen koşudan ayrı tutuluyor.

| Betik | Ne yapıyor | Ne zaman koşuldu |
|---|---|---|
| `measure_band.py` | Referans uzunluğa göre tabakalanmış başarı taraması. Ön koşul kapısını ateşleyen ölçüm | 11 Ağustos 2026 |
| `measure_gpt4o_subset.py` | Yayımlanmış gpt-4o koşusunun çözdüğü alt kümede yerel modeli koşturuyor | 11 Ağustos 2026 |
| `measure_boundary_control.py` | Düzenek doğrulaması: aynı görevleri API üzerinden sunulan bir modelle koşturuyor. Aile taramasında yerel adaylar için de kullanılıyor | 12 Ağustos 2026 |

Üçü de `scripts/record_run.py` ile aynı kaydediciyi, aynı yakalayıcıyı ve aynı
doğrulayıcıyı kullanıyor. Değişen şey görev seçimi ve raporlama.

**Kurulum protokolü** `experiments/setup-protocol.tr.md` içinde: hangi
parametrelerin taranacağı, her taramanın karar kuralı, ve tanı metriklerinin
tanımı.
