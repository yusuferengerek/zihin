# Boşluk raporu — 14 Ağustos 2026

Danışmanın 21 adımlık yol haritasına karşı deponun ölçülmüş durumu.

**Bu rapor iş önermiyor.** Durum tespiti; yol haritası önerisi değil. Her satır
bir dosya yoluna, commit hash'ine ya da test adına bağlı. İddia yazılmadı,
gösterilebilen yazıldı.

Ölçüm tabanı: `HEAD = abb2a6d`, dal `durma-kurali`, çalışma ağacı temiz.

---

## 1. Adım adım durum

| # | Adım | Durum | Kanıt |
|---|---|---|---|
| 1 | Teknik savunma | **bitti** | `PROJECT_STATUS.md`, 98 satır |
| 2 | Araştırma sorusunu sıkıştırma | **kısmi** | `docs/02-research-question.tr.md` 43 satır var; `experiments/preregistration.md` 3 satır, yer tutucu |
| 3 | Repo ve engineering standardı | **bitti** | PR #2 `stage-0-repo-skeleton`, PR #3; `.github/workflows/ci.yml` dört kontrol |
| 4 | AppWorld temiz kurulum | **bitti** | PR #4 `stage-1-appworld`, `REPRODUCE.md` 195 satır, `docs/reports/asama-1.md` |
| 5 | Baseline | **bitti** | PR #13 `band-taramasi`, `results/bant-taramasi.json`, `docs/reports/bant3-taramasi.md`; sonuç 0/30 |
| 6 | Veri modeli | **bitti** | PR #6 `stage-3-record-schema`, `src/zihin/schema.sql` 403 satır, `DATA_MODEL.md` 156 satır, `tests/test_record_schema.py` 20 test |
| 7 | Sandbox | **başlanmadı** | Yalnız kapsam: `docs/12-sandbox-scope.tr.md` 169 satır, commit `abb2a6d`. Kod yok, `Containerfile` yok, güvenlik testi yok |
| 8 | Shield | **başlanmadı** | `shield_violations` tablosu ve `insert_shield_violation` var (`src/zihin/records.py:650`); yüklem kodu yok, test yok. Yazma kümesinin statik yarısı türetildi: `scripts/setup/derive_write_set.py`, `inputs/write-set-static.json` |
| 9 | Retriever v0 | **başlanmadı** | Kod yok. Yalnız yapılandırma alanı: `config/*.yaml` içinde `retrieval.mode`, `src/zihin/config.py` `RetrievalMode` |
| 10 | Failure index | **kısmi** | Taksonomi yazılı: `docs/07-failure-taxonomy.tr.md` 126 satır. İndeks kodu ve tablosu yok |
| 11 | Skill dili | **kısmi** | `docs/06-skill-language.tr.md` 94 satır var; `SKILL_SPEC.md` **yok** |
| 12 | Compiler v0 | **başlanmadı** | Kod yok, `skills` tablosu şemada yok |
| 13 | Uçtan uca demo | **başlanmadı** | 7-12 arası bileşenler yok |
| 14 | Deney tasarımını dondurma | **kısmi** | `docs/05-experiment-design.tr.md` 291 satır var; `experiments/experiment-matrix.csv` yalnız başlık satırı |
| 15 | Pilot | **başlanmadı** | `PILOT_REPORT.md` 29 satır, kendini "taslak" ilan ediyor; `pilot/` klasöründe 1 dosya (`.gitkeep`) |
| 16 | Analiz | **başlanmadı** | Analiz betiği yok |
| 17 | Deneyi eleştirme | **bitti** | `docs/09-limitations.tr.md` 882 satır, S-01'den S-34'e |
| 18 | Reproducibility | **kısmi** | `REPRODUCE.md` 195 satır ve Aşama 1'de koşuldu; temiz makinede yeniden koşulma kaydı yok |
| 19 | Code review ve refactor | **kısmi** | 16 PR birleştirildi; son 25 commit dalda, review edilmemiş |
| 21 | Final savunma | **başlanmadı** | Sunum dosyası yok |

**Sayı:** bitti 6 (1, 3, 4, 5, 6, 17), kısmi 6 (2, 10, 11, 14, 18, 19),
başlanmadı 9 (7, 8, 9, 12, 13, 15, 16, 20, 21). Toplam 21.

---

## 2. Dosya envanteri

Yer tutucu ölçütü: markdown'da başlık dışı gövde beş satırdan azsa, CSV'de
başlık dışı satır yoksa yer tutucu sayıldı.

### İstenen `/docs`

| Dosya | Satır | Durum |
|---|---|---|
| `01-problem-definition.tr.md` | 36 | içerik var |
| `02-research-question.tr.md` | 43 | içerik var |
| `03-architecture.tr.md` | 103 | içerik var |
| `04-threat-model.tr.md` | 73 | içerik var |
| `05-experiment-design.tr.md` | 291 | içerik var |
| `06-skill-language.tr.md` | 94 | içerik var |
| `07-failure-taxonomy.tr.md` | 126 | içerik var |
| `08-decisions.tr.md` | 1518 | içerik var |
| `09-limitations.tr.md` | 882 | içerik var |

Dokuzu da var ve dolu.

### İstenen `/experiments`

| Dosya | Satır | Durum |
|---|---|---|
| `preregistration.md` | 3 | **yer tutucu** — gövdesi "İçerik sonraki görevde yazılacak" |
| `experiment-matrix.csv` | 1 | **yer tutucu** — yalnız başlık satırı, sıfır kayıt |
| `pilot-plan.md` | 22 | içerik var |

### İstenen `/config`

Beşi de var ve dolu: `baseline.yaml` 22, `skills.yaml` 23, `failures.yaml` 22,
`skills_failures.yaml` 22, `irrelevant_retrieval.yaml` 24 satır. Şema uyumu
`tests/test_config_schema.py` 14 testle sınanıyor.

### Kök

`README.md` 120, `CHANGELOG.md` 557, `LICENSE` 202, `uv.lock` 1742 satır.
Dördü de var.

### Teknik doküman seti

| İstenen | Karşılığı | Durum |
|---|---|---|
| Project_Status | `PROJECT_STATUS.md` 98 satır | var |
| Architecture | `docs/03-architecture.tr.md` 103 satır | var |
| Data_Model | `DATA_MODEL.md` 156 satır | var |
| **Skill_Spec** | — | **YOK** |
| Failure_Taxonomy | `docs/07-failure-taxonomy.tr.md` 126 satır | var |
| Threat_Model | `docs/04-threat-model.tr.md` 73 satır | var |
| **Experiment_Matrix** | `experiments/experiment-matrix.csv` | **yer tutucu** |
| **Preregistration** | `experiments/preregistration.md` | **yer tutucu** |
| Pilot_Report | `PILOT_REPORT.md` 29 satır | taslak, kendini öyle ilan ediyor |
| Reproduce | `REPRODUCE.md` 195 satır | var |

### Klasörler

`src` 21 dosya, `tests` 35, `results` 193, `pilot` 1, `scripts` 27,
`experiments` (çıktı dizini dahil, sürüm kontrolü dışı), `config` 9, `docs` 29.
Hepsi var.

### Veri modelinde istenen tablolar

| Tablo | Durum |
|---|---|
| `episodes` | var |
| `steps` | var |
| `observations` | var |
| `actions` | var |
| `verifier_results` | var |
| `shield_violations` | var |
| `run_manifests` | var |
| **`skills`** | **YOK** |
| **`failure_patterns`** | **YOK** |

Yedi tablo var, ikisi yok. Eksik ikisi projeksiyon; mimari onları "kayıttan
yeniden hesaplanabilir" diye tanımlıyor (`docs/03-architecture.tr.md`).

İkisi ayrı bir iş kalemi değil: `skills` derleyici maddesinin, `failure_patterns`
hata indeksi maddesinin içinde. Projeksiyonu üreten kod yazılmadan tabloyu
açmak, doldurulmayacak bir şema eklemek olurdu.

### Skill_Spec'te istenen alanlar

Dosya olmadığı için hiçbiri yok. `docs/06-skill-language.tr.md` içinde tanım, girdi
parametreleri ve precondition kavramsal olarak geçiyor; postcondition, source
episodes, support ve success rate alanları hiçbir belgede tanımlı değil.

### CI

Dört kontrolün dördü de var: bağımlılık kurulumu (`Kilitli bağımlılıkları kur`,
`Kilit dosyası güncel mi`), lint (`ruff check`, `ruff format`), test (`pytest`),
import/build (`Paket import ediliyor`, `Build`, `Üretilen dosyalar`).

### Testler

184 test fonksiyonu, 16 dosya. Koşum: 219 geçti, 8 atlandı.

---

## 3. Planda olmayan iş

Ölçüm, savunma değil.

**Zaman aralığı:** 10–14 Ağustos 2026, beş takvim günü. 79 commit, 16 PR
birleştirildi (#2–#18). Son 25 commit birleştirilmemiş dalda.

Günlük commit: 10 Ağustos 24, 11 Ağustos 24, 12 Ağustos 8, 13 Ağustos 9,
14 Ağustos 14.

Planın hiçbir adımında geçmeyen, tamamı bizim eklediğimiz işler:

| İş | Kanıt | Kapsam |
|---|---|---|
| Bant taraması ve tekrarları | PR #13, `results/bant-taramasi.json`, `bant2`, `bant3`, `bant3-kapali` | 4 koşu, ~116 epizot |
| Sınır kontrolü (düzenek doğrulaması) | PR #15, `results/sinir-kontrolu*.json`, `sinir3*` | 5 koşu, ~106 epizot |
| Durma kuralı: tasarım, üç kez yeniden kurulum, kalibrasyon | `820458e`, `de32822`, `fd28a43`, `e83871b`, K-63, K-64 | 5 commit + 2 ölçüm koşusu |
| Kesinti dayanıklılığı, devam mantığı, kirli ağaç kapısı | `f7fcbd2`, `79c43bd`, `4abd99b`, `78ca4c1` | `tests/test_resumption.py` 20 test |
| Künye sözleşmesi ve seri 2'ye geçiş | PR #18, `tests/test_manifest_contract.py` 27 test | S-29 |
| Teşhis koşuları (gpt-4o alt kümesi, jeton bütçesi) | PR #14, `results/gpt4o-*.json`, `sinir-jeton-2000.json` | 3 koşu |
| Hizalama denetimi | `docs/reports/hizalama-denetimi.md` | 1 rapor |
| Dış inceleme ve yanlışlama belgeleri | `docs/10-external-review.tr.md`, `docs/11-falsification.tr.md` | 49 satır |
| Kurulum protokolü | `experiments/setup-protocol.tr.md` 672 satır | 4 kurulum-sonrası PR (#9–#12) |
| Karar kaydının CSV projeksiyonu | `scripts/build_decisions_csv.py`, `experiments/decisions.csv` 74 kayıt | tamlık denetimiyle |
| Dil geçişi (tanımlayıcılar) | `30b7995`, `58027ce`, `09cbde6` | 39 dosya, 3628 yeniden adlandırma |
| Yazma kümesinin statik yarısı | `scripts/setup/derive_write_set.py`, `inputs/write-set-static.json` | 478 adlandırılmış API tarandı |
| Düşünme kapatma doğrulayıcısı | `89ae8e5`, `scripts/setup/verify_thinking_off.py` | — |

**Sınırlama kaydı:** planın hiçbir adımı sınırlama numaralandırması istemiyor;
`docs/09-limitations.tr.md` içinde S-01'den S-34'e 34 kayıt var, 882 satır.

**Karar kaydı:** plan "decision log" istiyor, sayı vermiyor;
`docs/08-decisions.tr.md` 1518 satır, 74 karar kaydı.

---

## 4. Yolu olmayan adımlar

### 15 (pilot) ve 16 (analiz)

Ön koşul kapısı ateşledi ve öyle duruyor: yerel eksende taban 0/30 çözüyor
(`docs/reports/bant3-taramasi.md`, `results/bant3-taramasi.json`). Kural kapalı
tekrar da aynı sonucu verdi (`e8627b4`, `results/bant3-kapali-taramasi.json`).

Pilotun tanımı `experiments/pilot-plan.md` içinde altı koşulun karşılaştırması.
Karşılaştırmanın birincil metriği adım farkı; taban sıfır çözdüğü için adım
farkı tanımsız, çünkü karşılaştırılacak başarılı epizot yok.

**Şu an bir yolu yok.** İki bileşen eksik ve ikisi de bu depoda üretilmedi:
sıfırın üstünde skor alan bir yerel model, ya da pilotun yerel olma şartının
kaldırılması. Sınır kontrolü barındırılan bir modelin 20/30 aldığını gösteriyor
(`results/sinir-kontrolu-4000.json`), yani hat çalışıyor; ama o model yerel
eksende değil ve düşünme açık koştu (S-34).

Aile taraması bu boşluğu kapatmak için planlanmıştı ve **iptal edildi**
(kullanıcı kararı, 14 Ağustos). Model ekseni `qwen2.5-coder` 1.5b/3b/7b olarak
sabit kaldı, yani 0/30 veren eksen.

### 13 (uçtan uca demo)

7'den 12'ye kadar altı bileşenin hiçbiri yok. Demo tanımı gereği hepsini
gerektiriyor: kartlar bağlamda, kalkan açık, sandbox içinde, kayıt tam.

### 14 (deney tasarımını dondurma)

`experiment-matrix.csv` yalnız başlık satırı taşıyor ve satırların içereceği
`library_id` alanı, beceri kütüphanesi üretilmeden doldurulamaz. Matris tasarımı
`docs/05-experiment-design.tr.md` içinde yazılı; makine okunur hâli boş.

### 20 ve 21

Depoda hiçbir dosya yok. Bu adımların bir yolu var, yalnız başlanmadı.

---

## 5. Risk altındaki teslim maddeleri

11 iş günü kaldı. Riskin iki ayrı sınıfı var ve karıştırılmamalı.

### 5.1 Yolu olmayanlar

Zaman meselesi değil; üretilebilir olup olmadıkları başka bir sonuca bağlı.

| Madde | Neye bağlı |
|---|---|
| **Pilot dataset / results** | Tabanın sıfır çözmesi (bölüm 4) |
| **Pilot report** | Pilot verisine |

### 5.2 Yalnız zaman riski taşıyanlar

Hiçbiri pilota bağlı değil; hepsinin bugün bir yolu var.

| Madde | Durum |
|---|---|
| **Skill specification** | Dosya yok; girdisi mevcut belgeler ve korpus |
| **Experiment matrix** | Yer tutucu; `library_id` alanı derleyici çıktısını bekliyor, matrisin kalanı beklemiyor |
| **Preregistration** | Yer tutucu |
| **Analysis script** | Pilot verisi beklemeden yazılabilir ve sentetik veriye karşı sınanabilir |
| **20-30 dakikalık final sunum** | Başlanmadı |

Risk altında **olmayanlar**, çünkü hâlihazırda var ve dolu: temiz git repo,
README, architecture document, decision log, threat model, data model,
failure taxonomy, otomatik testler, CI, reproduction instructions, limitations.

---

## 6. Ek: yol haritası güncellendi, 14 Ağustos

Rapor yazıldıktan sonra sıra değişti ve bölüm 4'ün bir bulgusunu geçersiz
kılıyor. Ek olarak yazılıyor, bölüm 4 olduğu gibi bırakılıyor: raporun ölçtüğü
durum o andaki durumdu.

**Pilot, deneyin pilotu olmak zorunda değil; mekanizmaların pilotu olacak.**

Yeni sıra: kalkan → `SKILL_SPEC.md` → derleyici v0 ve `skills` tablosu → hata
indeksi ve `failure_patterns` tablosu → getirici v0 → **mekanizma pilotu** →
uçtan uca demo → sandbox.

### Mekanizma pilotunun ölçeceği dört sayı

Hiçbiri çalışan bir taban gerektirmiyor.

1. **Derleyici çıktısı.** Sınır kontrolünün 20 geçen epizodundan kaç beceri
   çıktı; destek ve başarı oranı dağılımları.
2. **Hata indeksi çıktısı.** Yerel başarısızlıklardan kaç kalıp çıktı; kaçının
   karşıtsal eşi var, kaçı "bilinen başarı yok" işaretli.
3. **Getirici kapsaması.** Ayrılmış görevlerde kaç görev en az bir ilgili kart
   alıyor. Model koşmadan ölçülüyor: görev listesi artı kütüphane yetiyor.
4. **Kalkan gölge modu.** Karar kaydedilir ama engellenmez; mevcut epizotlar
   üzerinde koşulup yanlış pozitif oranı ölçülür.

### Bölüm 4'ün hangi kısmı değişti

"15 ve 16'nın yolu yok" tespiti **deneyin pilotu** için geçerliliğini koruyor:
taban sıfır çözdüğü sürece adım farkı tanımsız kalıyor. Ama mekanizma pilotu
ayrı bir yol ve dört ölçümü de bugünkü korpusla üretilebilir.

Getirici kapsaması ayrıca bir yanlışlama kapısını değerlendirilebilir kılıyor:
kapsama %25'in altında çıkarsa bu "test edemedik" değil, sembolik getiricinin bu
ortamda ilgili deneyim bulamadığı **bulgusudur**.

Pilot raporunun dürüstlük şartı: mekanizmalar kuruldu ve çalıştıkları
gösterildi, birincil karşılaştırma ön koşul kapısı yüzünden koşulamadı. Kapının
ateşleme tarihi ve kanıtı raporda duracak.

## 7. Ölçümün kendi sınırı

Bu rapor dosya varlığını, satır sayısını, commit ve test sayısını ölçüyor.
Ölçmediği şey **içeriğin yeterliliği**: 156 satırlık bir `DATA_MODEL.md`'nin
danışmanın beklediği ayrıntıyı taşıyıp taşımadığı buradan görünmüyor. "İçerik
var" yalnız yer tutucu olmadığını söylüyor.

`SKILL_SPEC.md` gibi eksik dosyalarda ise ölçüm net: dosya yok.
