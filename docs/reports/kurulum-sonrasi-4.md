# Kurulum sonrası 4 — Sansür hükümden tanımlanıyor

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

Dört karar işlendi: yazma kümesinin birleşim olması, sansürün doğrulayıcı
hükmüyle tanımlanması, kategori 4 oranının iki rejimi, ve artık varyansa üst
sınır yazılması. Sansür tanımı bir eksik ortaya çıkardı ve o eksik bu turda
kapandı.

## Önce bir cevap: depo neden Masaüstünde görünmüyor

Windows tarafındaki `mind` klasörü boş çünkü depo hiç orada olmadı. K-01 gereği
depo WSL'in kendi ext4 dosya sisteminde duruyor: `zihin` dağıtımında
`/home/yusuf/zihin`. Windows'tan `\\wsl.localhost\zihin\home\yusuf\zihin`
yolundan görünüyor.

İki sebep kayıtlı. Sandbox kararı kök yetkisiz podman olduğu için platform
Linux. Depo `/mnt/*` üzerinde dursaydı 9p dosya sistemi çok sayıda küçük
dosyada ve SQLite'ta çok yavaş kalırdı. `mind` klasörü ayrıca OneDrive altında;
oraya konsaydı SQLite dosyası bulut eşitlemesiyle de çakışırdı.

## Yazma kümesi birleşim, çünkü kör noktalar farklı yerde

Canlı sayımın güncellemeyi görmemesi kodun yorumunda yazılıydı ama sonucu
yazılı değildi. Sonuç şu: ampirik ölçüm tek başına statik taramanın üçüncü
grubunu hiç bulamaz.

| Kaynak | Gördüğü | Göremediği |
|---|---|---|
| Ampirik sayım | ekleme, silme, devretme | güncelleme |
| Statik tarama | işleyici gövdesindeki doğrudan çağrı | yardımcıya devredilen çağrı |

Statik taramanın üçüncü grubu — `phone.show_contact_relationships` ve
`todoist.show_projects` — türetilmiş bir alanı güncelliyor, yeni satır açmıyor.
Satır sayısı değişmediği için ampirik ölçüm bu iki ucu hiç işaretlemez. Ölçümü
daha uzun koşturmak da bunu değiştirmez; sınır yapısal.

Ters yönde statik tarama GET dışı 302 ucun 91'inde işi yardımcı fonksiyona
devredilmiş buldu ve aynı devretme GET tarafında da olabilir. Ampirik ölçüm
davranışa baktığı için orayı kapatıyor.

İkisi de alt sınır, alt sınırı farklı yerden veriyor. K-41 buna göre
güncellendi: yazma kümesi `statik ∪ ampirik` olarak donduruluyor, biri
diğerinin önsel hâli değil. Gerekçe karar kaydına yazıldı ki ileride "ampirik
ölçüm var, statik tarama gereksiz" diye elenemesin.

`model_hashes.json` üçüncü kat olarak duruyor ama kümeyi kuramıyor:
güncellemeyi görüyor, hangi çağrının yaptığını söylemiyor. Rolü alarm vermek.

## Sansür tanımı: hüküm, sebep değil

K-53 iki kez sebep listesiyle yazılmıştı. Önce yalnız `step_ceiling`, sonra
`no_progress` de eklenerek. İkisi de eksikti ve eksiklik aynı yerdeydi: ajanın
görevi bitirdiğini bildirip doğrulayıcıdan kaldığı hâl hiçbir listede yok.

O hâl K-36'nın beşinci kategorisi ve kurulum sonrası 2'de ölçülmüştü — 7B'nin
en çok ürettiği arıza biçimi, 120 adımın 60'ı. Sebeple tanımlanan bir sansür
en yetenekli modelimizin baskın arızasını sansürsüz sayardı.

Yeni tanım: **doğrulayıcının geçirmediği her epizot sansürlüdür.**
`termination_reason` ayrı bir tanı alanı olarak kaldı; hangi yoldan
sansürlendiği raporlanıyor ama ölçüt o dağılıma bakmıyor. Yeni bir sonlanma
yolu eklendiğinde tanımı güncellemek gerekmiyor.

`passed` üç hâl taşıyor ve üçüncüsü tanıma girmiyor: `NULL` "geçmedi" değil
"hüküm okunamadı" demek. Analize giren epizotta `NULL` bulunursa bu bir ölçüm
arızası, sansür sayısına yazılmamalı.

## Tanımın açtığı eksik: hüküm hiçbir epizotta kayıtlı değildi

Sansür oranını hükümden hesaplayacaksak hükmün kayıtta olması gerekiyor. Kayıtta
değildi.

`verifier_results` tablosu Aşama 3'ten beri duruyor ve her epizot için satır
açılıyordu, ama `passed` alanı her satırda `NULL`'du. Kaydedici doğrulayıcıyı
hiç koşturmuyordu; yalnız rapor dosyasının yolunu, o da varsa, yazıyordu.
Değerlendirmeyi koşturan tek yer Aşama 1'in tek görevlik betiğiydi.

Bunun somut sonucu: daha önceki raporlarda "hiçbir model görevi bitirmedi"
cümlesi bir çıkarımdı, ölçüm değil. Dayanağı hiçbir epizodun `agent_finished`
ile bitmemesiydi. Doğru cümle ama doğrulayıcının hükmü değil.

`src/zihin/verification.py` eklendi. Epizot bittiği anda `evaluate_dataset`
koşuyor ve hüküm künyeyle birlikte yazılıyor. Sonraya bırakılamıyor:
değerlendirme görev çıktı dizinindeki son veritabanı durumunu okuyor ve aynı
görev başka bir modelle koşulduğunda o dizin üzerine yazılıyor. Bu, yazma kümesi
kaydı için istenen "ilk epizottan itibaren açık olsun" kuralının aynısı.

## Ölçüm: model başına sansür oranı

Beş görev, model başına görev başına bir soğuk epizot, taban koşulu, durma
kuralı açık. On beş epizot.

| Model | Epizot | Geçen | Sansür | %95 alt sınır | Kategori 4 |
|---|---|---|---|---|---|
| 1.5B | 5 | 0 | %100 | %54,9 | 15/24 = %62,5 |
| 3B | 5 | 0 | %100 | %54,9 | 18/20 = %90,0 |
| 7B | 5 | 0 | %100 | %54,9 | 9/57 = %15,8 |

Ölçüt sansür oranının %10'un altında olmasını istiyor. Alt sınır %54,9, yani
beş epizot ölçütü reddetmeye yetiyor. **Üç modelde de reddediliyor.**

1.5B ve 3B için bu bekleniyordu. 7B için beklenmiyordu ve asıl bulgu bu: bu beş
görevde ölçek ekseninin hiçbir noktasında birincil metrik tanımlı değil.

Epizot ayrıntısı:

| Model | Görev | Adım | Sonlanma | Geçen/düşen test |
|---|---|---|---|---|
| 1.5B | `82e2fac_1` | 4 | `no_progress` | 1/1 |
| 1.5B | `692c77d_1` | 4 | `no_progress` | 1/6 |
| 1.5B | `2a163ab_1` | 4 | `no_progress` | 1/5 |
| 1.5B | `6104387_1` | 4 | `no_progress` | 0/10 |
| 1.5B | `29caf6f_1` | 8 | `no_progress` | 1/7 |
| 3B | `82e2fac_1` | 4 | `no_progress` | 1/1 |
| 3B | `692c77d_1` | 4 | `no_progress` | 1/6 |
| 3B | `2a163ab_1` | 4 | `no_progress` | 1/5 |
| 3B | `6104387_1` | 4 | `no_progress` | 0/10 |
| 3B | `29caf6f_1` | 4 | `no_progress` | 1/7 |
| 7B | `82e2fac_1` | 7 | `no_progress` | 1/1 |
| 7B | `692c77d_1` | 6 | `no_progress` | 1/6 |
| 7B | `2a163ab_1` | 20 | `step_ceiling` | 1/5 |
| 7B | `6104387_1` | 20 | `step_ceiling` | 0/10 |
| 7B | `29caf6f_1` | 4 | `no_progress` | 1/7 |

**Geçen testler ilerleme kanıtı değil.** Her epizotta bir test geçiyor gibi
görünüyor ama geçen test hep aynı türden: `82e2fac_1`'de "assert no model
changes", `2a163ab_1`'de "assert no new venmo.Transaction was added". Bunlar
ajanın hiçbir şey yapmadığı için geçiyor. `6104387_1`'de ajan bir şeye
dokunduğu an o test de düşüyor ve sayı 0/10 oluyor.

**Sonlanma sebebi dağılımı tanıyı taşıyor, ölçütü değil.** On beş sansürlü
epizodun on üçü `no_progress`, ikisi `step_ceiling`. Bu ölçümde iki tanım da
aynı sonucu verirdi; ayrım 7B'nin sessiz boş başarı ürettiği epizotlarda
açılıyor ve K-53 tam onun için hükme bağlandı.

**Kategori 4 iki modelde birebir tekrarladı.** 1.5B'de %62,5 ve 7B'de %15,8,
taramadaki oranların aynısı. 3B'de %90; kurulum sonrası 2'de %100'dü, aradaki
fark durma kuralının epizodu dörtte kesmesi.

Ölçümün kapsamı S-22'de yazılı: beş görev rastgele örneklem değil, model başına
tek epizot var.

## Bir yan bulgu: sunucu yeniden başlatması yörüngeyi değiştirmedi

Ollama süreci bu oturumda ölmüştü, betikten yeniden başlattım (K-22). Sansür
ölçümü o yeni süreçte ve kayıt betiğiyle koşuldu; tarama ise eski süreçte ve
başka bir betikle koşmuştu.

On yapılandırmanın onunda da adım ve çağrı sayıları birebir aynı çıktı:

| Model | Görev | Tarama | Sansür ölçümü |
|---|---|---|---|
| 1.5B | `82e2fac_1` | 4 adım, 3 çağrı | 4 adım, 3 çağrı |
| 1.5B | `692c77d_1` | 4 adım, 0 çağrı | 4 adım, 0 çağrı |
| 1.5B | `2a163ab_1` | 4 adım, 0 çağrı | 4 adım, 0 çağrı |
| 1.5B | `6104387_1` | 4 adım, 0 çağrı | 4 adım, 0 çağrı |
| 1.5B | `29caf6f_1` | 8 adım, 5 çağrı | 8 adım, 5 çağrı |
| 7B | `82e2fac_1` | 7 adım, 4 çağrı | 7 adım, 4 çağrı |
| 7B | `692c77d_1` | 6 adım, 2 çağrı | 6 adım, 2 çağrı |
| 7B | `2a163ab_1` | 20 adım, 19 çağrı | 20 adım, 19 çağrı |
| 7B | `6104387_1` | 20 adım, 20 çağrı | 20 adım, 20 çağrı |
| 7B | `29caf6f_1` | 4 adım, 0 çağrı | 4 adım, 0 çağrı |

Sunucu süreci artık varyans ölçümünün değişkenleri arasında yoktu; bu karşılaştırma
kazara oldu. Eşleşme adım ve çağrı düzeyinde, yörünge özeti düzeyinde değil —
kayıt betiği o özeti hesaplamıyor. S-21'e not olarak geçti.

## Artık varyans: nokta kestirim değil üst sınır

Otuz epizotta sıfır ayrışma görmek oranın sıfır olduğunu göstermiyor, küçük
olduğunu gösteriyor. S-21 üst sınırla yeniden yazıldı.

| Ölçüm | Rejim | Ayrışma | Üst sınır |
|---|---|---|---|
| 1.5B, beş görev | kural açık | 0/30 | %9,5 |
| 7B, beş görev | kural açık | 0/30 | %9,5 |
| İkisi havuzlanmış | kural açık | 0/60 | %4,9 |
| 1.5B, tek görev | kural kapalı | 0/10 | %25,9 |
| 3B, tek görev | kural kapalı | 0/10 | %25,9 |
| 7B, tek görev | kural kapalı | 1/20 | %21,6 |

Clopper-Pearson tek yanlı %95. Gürültü tabanına giren sayı model başına %9,5,
yanında ölçüldüğü rejim yazılı.

%2'lik bir üst sınır sıfır ayrışmayla 149 epizot istiyor; elimizde model başına
otuz var. İki rejim havuzlanamaz, çünkü kural açıkken epizotlar kısalıyor ve
sapma fırsatı azalıyor.

## Kategori 4'ün iki rejimi

Kendi uyarım karara bağlandı ve ikiye ayrıldı.

Ana deneyde oran durma kuralı **açıkken** ölçülüyor, çünkü deney o rejimde
koşuyor. Oran eşiğe koşullu ama koşullama bütün koşullarda aynı olduğundan
koşullar arası karşılaştırma geçerli kalıyor; mekanizmanın etkisi farkta
aranıyor, düzeyde değil.

Kural **kapalıyken** ölçüm yalnız kurulum aşamasının eşik seçimine hizmet
ediyor: kesilen epizot sonraki adımlarda toparlanıyor mu. Oradan çıkan oran ana
deneyin sayısı değil, eşiğin gerekçesi.

Makalede her oranın hangi rejimden geldiği yazılıyor, iki rejimin sayıları aynı
tabloda yan yana konmuyor.

## Yerel-yalnız kontroller

KONTROLLER-BURAYA

## Kararlar ve sınırlar

- **K-41** genişletildi. Yazma kümesi `statik ∪ ampirik`, biri diğerinin yerine
  geçmiyor.
- **K-53** yeniden yazıldı. Sansürü doğrulayıcının hükmü tanımlıyor.
  `termination_reason` tanı alanı olarak kaldı.
- **K-54** genişletildi. Kategori 4 oranı ana deneyde kural açıkken, kural
  kapalı ölçüm yalnız eşik seçimine.
- **S-04** güncellendi. İki bileşenin nereden çıkarılabileceği yazıldı; sütunlar
  hâlâ `NULL`.
- **S-21** yeniden yazıldı. Üst sınır, rejimiyle birlikte.
- **S-22** açıldı. Sansür ölçümünün örneklem sınırı.

## Yerel-yalnız kontroller

11 Ağustos 2026, `MODEL_SERVER_URL` verili ve AppWorld verisi indirilmiş
durumda.

| Kontrol | Sonuç |
|---|---|
| `ruff check` | temiz |
| `ruff format --check` | temiz |
| `pytest` | 133 test geçti, atlanan yok |
| import | `zihin`, `zihin.verification`, `zihin.state_probe`, `zihin.recording_agent` |
| `uv build` | tamam |

Bunlara ek olarak on beş epizot uçtan uca koşuldu ve on beşinin de doğrulayıcı
hükmü şemaya yazıldı.

**Bir işletme notu.** Ollama süreci bu oturumda ölmüştü; ölçümden önce
`scripts/serve_models.ps1` ile yeniden başlatıldı ve ayarlar log'dan
doğrulandı: `OLLAMA_CONTEXT_LENGTH=32768`, `KV_CACHE_TYPE=q8_0`,
`FLASH_ATTENTION=true`, `KEEP_ALIVE=30m`. Bu ölçüm o yeniden başlatmadan
sonrasına ait.

## Sırada ne var

Önyükleme biriktirmesi. Üç koruma yerinde, sansür artık hükümden hesaplanabilir
ve hüküm ilk epizottan itibaren kayıtta.

İki ölçüm bekliyor. Birincisi eşik taraması: farklı eşiklerde sansür oranı, ve
kural kapalıyken epizotların toparlanıp toparlanmadığı. İkincisi ölçek ekseni:
7B'nin de ölçütü karşılamaması beş görevlik bir gözlem, pilotun kendi
örnekleminde doğrulanması gerekiyor. İkisi de önyükleme biriktirmesini
engellemiyor, çünkü biriktirme deneyin parçası değil (K-52).
