# Denetim boşluk raporu — ilan edilenler ile bağlı olanlar

**Soru.** Protokol ve tasarım belgeleri bir denetimden söz ettiğinde, o denetim
gerçekten koşuyor mu. Boşluk raporunun denetimlere uygulanmış hâli, tek geçiş.

**Neden gerekliydi.** Bu sınıfın bir örneği ölçüldü ve **üçte ikisi eksik
çıktı**: iki dilli dalganın tasarımı üç CI denetimi ilan etmişti, yalnız
birincisi kurulmuştu. Kalanında kaç tane olduğunu bilmemek, her denetim
iddiasını zayıflatıyor.

**Yöntem ve sınırı.** Bağlı taraf mekanik: `.github/workflows/ci.yml`,
`scripts/local_checks.sh`, `scripts/ci_simulasyonu.sh` ve kaynak ağacı tarandı.
İlan tarafı elle: protokol ve tasarım belgelerindeki denetim cümleleri okundu.
İkincisi bir yargı, ölçüm değil — bir denetimden düzyazıyla söz etmenin sabit
bir biçimi yok, dolayısıyla bu tarama **alt sınır**.

---

## Bağlı ve ilanıyla uyumlu

| Denetim | Nerede bağlı |
|---|---|
| `ruff check`, `ruff format --check` | CI, Lint |
| Belge adlandırması, çeviri eşi, çapa sayımı | CI, Lint |
| Sınırlamalar haritası tazeliği (iki dil) | CI, Lint |
| Sunum iskeleti kapsama özeti tazeliği | CI, Lint |
| `uv lock --check` | CI, bağımlılık işi |
| Paket import, build | CI |
| `pytest`, `appworld` verisi kurulu | CI |
| `pytest -m sandbox` | CI, sandbox işi |
| `missing_manifest_constraints` | üç koşucunun üçünde |
| Kirli ağaç kapısı (`MEASUREMENT_DEFINING_PATHS`, K-76) | `src/zihin/records.py` |
| Künye kapıları (`context_verified` vb.) | `scripts/record_run.py` |
| `check_language.py` | yalnız `local_checks.sh` |

---

## Boşluklar

### 1. Karar CSV'sinin bayatlık nöbetçisi hiç yoktu — bu turda kapatıldı

`experiments/decisions.csv` üretilen görünümlerin **en eskisi** ve tek bayatlık
nöbetçisi olmayanıydı. Ne CI ne `local_checks.sh` betiği koşuyordu;
`tests/test_decision_record.py` başlık şemasını çiviliyor ama **CSV'yi kaynakla
karşılaştırmıyor** (ölçüldü: dosyada karşılaştırma yok).

Yani `docs/08-decisions.tr.md` düzenlenip betik koşulmazsa CSV sessizce
bayatlıyordu. Bu, tam olarak iki kez gerçekleşmiş arıza sınıfı: 68 satır
kaybı (S-33) ve otuz sessizce yanlış gerekçe (K-103).

**Kapatıldı.** `--check` eklendi ve CI'ın Lint işine bağlandı. Nöbetçi üç
durumda görüldü: taze → çıkış 0; kaynak değişip CSV üretilmeyince →
`stale against docs/08-decisions.tr.md`, çıkış 1; geri alınınca → 0.

### 2. "Kesinti sonrası bütünlük denetimi" bir prosedür değil, bir kereye mahsus ölçüm

Protokol şöyle yazıyor: "Kesintiye açık kalmış bir veritabanına eklemeden önce
**dört şey ölçülüyor**", ardından `PRAGMA integrity_check` ile başlayan bir
tablo ve tarihli değerler.

Ölçüldü: `integrity_check` deponun **hiçbir dosyasında geçmiyor**. Yani cümle
geniş zamanda bir prosedür anlatıyor, gerçekte 13 Ağustos 2026'da elle yapılmış
tek bir ölçümün kaydı. Bir sonraki kesintide kimse hatırlamazsa koşmaz.

**Kapatılmadı.** Kapanma yolu iki tane ve ikisi de karar gerektiriyor: ya
denetim koşucuların ön kontrolüne bağlanır, ya da protokoldeki cümle geniş
zamandan geçmiş zamana çekilir ve bir kereye mahsus olduğu yazılır.

### 3. İki dilli dalganın ikinci ve üçüncü denetimi hiç yazılmamış

Tasarım üç denetim ilan etmişti: eş var mı, ikisi aynı commit'te mi değişti,
kaynak commit güncel mi. Yalnız birincisi kuruldu. Dayandıkları alan — her
`.en.md` başlığındaki kaynak commit'i — dokuz çevirinin **sıfırında** var.

**Kapatılmadı.** K-112 ile kayda geçti; kapanma yolu her çevirinin kaynağının
sürümünü taşıması.

### 4. Devam koruması ve ön kontrol üç koşucunun ikisinde

Ölçüldü:

| Nöbetçi | Bağlı olduğu koşucular |
|---|---|
| `missing_manifest_constraints` | `measure_band`, `measure_boundary_control`, `measure_rule_off` |
| `resume_check` | `measure_boundary_control`, `measure_rule_off` — **`measure_band` yok** |
| `def preflight` | `measure_band`, `measure_boundary_control` — **`measure_rule_off` yok** |

İki koruma da "koşucular" diye ilan edilmiş, ve ikisi de üçte ikisinde.
Eksikler birbirini tamamlamıyor, ayrı ayrı iki boşluk.

**Kapatılmadı.** Koşucu davranışı ölçümü etkiliyor; hangi koruma hangi koşucuda
anlamlı olduğu ayrı bir karar ve talimatsız değiştirilmedi.

### 5. Protokoldeki "dört CI kontrolü" sayısı bayat

Protokol "**Dört CI kontrolü her PR'da yeşil**" diyor. CI'da bugün **beş iş**
var, ve aynı belge daha aşağıda "Beşinci CI kontrolü kırmızı yandı" diyor. Belge
kendi içinde tutarsız ve dışarıya karşı bayat.

**Kapatılmadı.** `setup-protocol` çeviri kuyruğunda; sayının düzeltilmesi o
turun işi ve bayat ilanı çevirmek borcu iki katına çıkarır.

---

## Boşluk olmayan, ama yazılmamış olan

`check_language.py` yalnız `local_checks.sh` içinden koşuyor ve bu doğru:
`data_corpus()` `results/` altındaki dosyaları ve sqlite kaydını okuyor, ikisi
de `.gitignore`'da. CI'da o korpus boş olur, veri anahtarları düzyazı sanılır ve
denetim **yanlış pozitif** üretir.

Yani yerel olması bir eksiklik değil bir gereklilik — ama bu gerekçe hiçbir yerde
yazılı değildi ve süpürmede ölçülerek bulundu. Şimdi burada yazılı.

---

## Sayım

| | |
|---|---|
| İlan edilip bağlı | 12 |
| İlan edilip bağlı olmayan | 5 |
| Bu turda kapatılan | 1 |
| Yerel olması gerekçeli | 1 |

**Beşte biri kapatıldı, dördü açık ve kayıtlı.** Süpürmenin kendi sınırı yukarıda:
ilan tarafı düzyazı okunarak çıkarıldı, yani bu bir alt sınır.

---

## Kuyruk, teslim listesine göre sıralı

Danışmanın asgari setindeki maddeler önce, kalite pasları sonra
(`docs/reports/bosluk-raporu.md` §5).

### A. Teslim listesinde, yolu var

| Sıra | Madde | Neden burada |
|---|---|---|
| 1 | `experiments/setup-protocol` çevirisi | İki dilli dalganın son borcu; bayat "dört CI kontrolü" ilanı bu turda düzeltildi, yani çevrilmeye hazır |
| 2 | Skill specification | Teslim listesinde; girdisi mevcut belgeler ve korpus |
| 3 | Experiment matrix | Yer tutucu; `library_id` dışında pilot beklemiyor |
| 4 | Preregistration | Yer tutucu |
| 5 | Analysis script | Pilot verisi beklemeden yazılabilir, sentetik veriye karşı sınanabilir |
| 7 | Final sunum (20–30 dk) | İskeleti var, kendisi yok |

### B. Teslim listesinde, yolu bir sonuca bağlı

| Madde | Neye bağlı |
|---|---|
| Pilot dataset / results | Ön koşul kapısının aşılmasına |
| Pilot report | Pilot verisine |

### C. Kalite pasları — teslim listesindeki hiçbir şeyi bloke etmiyor

Yaş sırasına göre (K-115), önem sırasına göre değil:

1. `measure_card_arms` ve `measure_card_demo` nöbetçileri — bir sonraki kullanımdan önce
2. `build_limitations_index` ve `build_skeleton_coverage` için şekil testleri
3. Naif madenci karşılaştırması — kütüphane karşılaştırması olarak
4. K-110'un geriye dönük kapanış taraması (on altı kapanış)
5. Çapraz kontrolün yedi aday sınırlaması
6. Ters yöndeki beş kayıt
7. **Nöbetçi doğruluğu süpürmesi** — yapısal sayım on dört bölgede nöbetçinin
   *varlığını* ölçüyor, doğruluğunu değil (K-115'in sınırı). Her nöbetçi için bir
   negatif test: kaldırıldığında düşüyor mu. Bilerek ertelendi — kalite pasları
   kendi kendini besliyor ve bir yerde durmak gerekiyor.

**4, 5 ve 6 sona gitti**, çünkü hiçbiri teslim listesindeki bir maddeyi bloke
etmiyor ve üçü de `09-limitations`'ı büyütüyor — belge iki dile çevrildiği için
her ekleme borcu iki katına çıkarıyor.

---

## Kuyruk — ölçülmüş durum, teslim listesine göre sıralı

**Sıralama ölçütü:** danışmanın asgari setinde adı geçen maddeler önce, kalite
pasları sonra. Boşluk raporunun §5'i sıralamanın kaynağı, ama bazı satırları
bayat çıktı ve aşağıdaki durum sütunu **ölçülerek** yazıldı.

### A. Teslim listesinde, yolu var, sırayla

| # | Madde | Ölçülen durum |
|---|---|---|
| 1 | **Final sunum (20–30 dk)** | İskelet var (218 satır, 35 iddia, kapsama özeti üretiliyor); sunumun kendisi yok. **Kuyruğun tepesi.** |
| 2 | Analysis script | `scripts/analyze_pilot.py`, on beş test, sentetik veriye karşı sınandı. |
| 3 | Preregistration | 662 satır, yer tutucu değil; aile seçilince sayıları dolacak. |
| 4 | Experiment matrix | `experiments/experiment-matrix.csv` var; `library_id` derleyici çıktısını bekliyor. |
| 5 | Skill specification | **318 satır, var.** Boşluk raporu "dosya yok" diyordu; satır bayat. |

**Boşluk raporundaki iki bayat satır düzeltildi:** skill spec var, experiment
matrix var. Analiz betiği yazıldı. Kalan tek eksik teslim maddesi **sunum**.

### B. Teslim listesinde, yolu bir sonuca bağlı

| Madde | Neye bağlı | Bugünkü durum |
|---|---|---|
| Pilot dataset / results | Ön koşul kapısının aşılmasına | aile taraması koşuyor |
| Pilot report | Pilot verisine | `PILOT_REPORT.md` 390 satır, kurulum bulgularıyla dolu |

### C. Kalite pasları — hepsi A ve B'nin **arkasında**

Yaş sırasına göre (K-115):

| # | Pas | Neden burada |
|---|---|---|
| 1 | `measure_card_arms` ve `measure_card_demo` nöbetçileri | Bir sonraki kullanımdan önce; şu an kullanılmıyor |
| 2 | `build_limitations_index` ve `build_skeleton_coverage` şekil testleri | Ayrıştırıcılar test edilmemiş; sınıf bir kez ısırdı (K-103) |
| 3 | Naif madenci karşılaştırması | Kütüphane karşılaştırması olarak; derleyici gerekiyor |
| 4 | K-110'un geriye dönük kapanış taraması | On altı kapanış; yeni kayıt üretebilir |
| 5 | Çapraz kontrolün yedi aday sınırlaması | `09-limitations`'ı büyütür |
| 6 | Ters yöndeki beş kayıt | Aynı sebep |
| 7 | Nöbetçi doğruluğu süpürmesi | On dört nöbetçinin her biri için negatif test |

**4, 5, 6 ve 7 bilerek en sonda.** Hiçbiri teslim listesindeki bir maddeyi bloke
etmiyor, ve dördü de artık iki dile çevrilen belgeleri büyütüyor — her ekleme
borcu iki katına çıkarıyor.

### Kapanan borç

İki dilli dalga bitti: **bekleyen çeviri sıfır.** On belge iki dilli, dördü
gerekçesiyle yalnız Türkçe. Çapa denetimi 795 çapayı iki tarafta da doğruluyor.
