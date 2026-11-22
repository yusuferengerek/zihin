# Pull request log

Every pull request of this repository, oldest first: number, title, branch, merge
date and the description as it was written. GitHub keeps this metadata outside the
tree; this file keeps the review trail inside it. A task instruction quoted in a
description is replaced by a placeholder naming the task and the sha256 of its
original instruction (S-82); everything else is verbatim. The file is regenerated
from the GitHub API after pull requests merge, so the newest ones may be missing.

## #1 — Aşama 0 — Depo iskeleti, bağımlılık kilidi, CI

- Branch: `stage-0-repo-skeleton`
- Merged: not merged (closed)

<!-- body, verbatim except for task text -->

# Aşama 0 raporu — Depo iskeleti

Bu rapor kodun ne yaptığını değil, neyi doğruladığını anlatıyor.

## Kabul ölçütü ne diyordu

> Temiz bir makinede depo klonlanıp bağımlılıklar kurulabiliyor, CI'nın dördü de
> yeşil.

## Neyi doğruladık

### Bağımlılık kurulumu tekrarlanabilir

`uv.lock` içinde **9 paket** dondurulmuş durumda. Kurulum `--frozen` bayrağıyla
yapılıyor, yani kilit dosyası çözümlemeyi belirliyor; CI'da ayrıca `uv lock
--check` koşuyor, kilit dosyası `pyproject.toml` ile uyumsuz kalırsa iş düşüyor.

Kilitlenen bağımlılıklar bilerek az. Çalışma zamanında tek bir tanesi var:
`pyyaml`. Geliştirme tarafında `pytest` ve `ruff`.

**AppWorld kasten bu listede yok.** Aşama 0'ın ölçütü "temiz makinede
bağımlılıklar kurulabiliyor"; o ölçütü henüz gerekmeyen ağır ve Git LFS isteyen
bir bağımlılıkla sınamak, ölçütü doğrulamak değil bulandırmak olurdu. AppWorld
Aşama 1'in PR'ında girecek.

### Python sürümü gerçekten sabit

`requires-python = "==3.11.*"` ve `.python-version` içinde `3.11`. Kurulum
CPython 3.11.15 ile yapıldı. Aralık değil, sabit: 3.12'ye kayma ihtimali yok.

Kullanılan araç **uv 0.11.28**. Hem yerelde hem CI'da aynı sürüme sabitlendi;
`astral-sh/setup-uv@v5` adımına sürüm açıkça yazıldı.

### Altı config dosyası gerçekten aynı şemayı taşıyor

Bu iddia yorum değil, test. `tests/test_config_schema.py` şunları denetliyor:

- `config/` altında tam olarak altı `.yaml` var, adları beklenen altı koşul.
- Altı dosyanın **anahtar ağacı birebir aynı** — değerler atılıp yalnız yapı
  karşılaştırılıyor.
- Her dosya yükleniyor ve `condition` alanı dosya adıyla eşleşiyor.
- Kalkan altı koşulun hepsinde açık. Kazara kapanması testi düşürür.
- `baseline` hiçbir kart taşımıyor; kalan beş koşul eşit slot taşıyor (beşer).
  Hacim kontrolü ancak bu eşitlik korunursa anlamlı.
- Bozuk yapılandırmalar reddediliyor: eksik alan, tanınmayan alan, tanımsız enum
  değeri, ve slot sayısı yerine boole (Python'da `bool` bir `int` alt türü
  olduğu için bu sessizce geçebilirdi).

Toplam **17 test**, hepsi geçiyor.

### Dört kontrol de yerelde geçiyor

| Kontrol | Sonuç |
|---|---|
| Bağımlılık kurulumu (`uv sync --frozen`, `uv lock --check`) | geçti |
| Lint (`ruff check`, `ruff format --check`) | geçti, 17 dosya biçimli |
| Testler (`pytest`) | 17 geçti |
| Import ve build (`import zihin`, `uv build`) | geçti, sdist + wheel üretildi |

CI dört ayrı iş olarak `ubuntu-24.04` üzerinde koşuyor. Koşucu sürümü açıkça
yazıldı, `ubuntu-latest` kullanılmadı — o etiket zamanla kayar ve geliştirme
ortamıyla eşleşme kaybolur.

### Dördü CI'da da yeşil

PR #1 üzerinde, `ubuntu-24.04` koşucusunda:

| İş | Sonuç | Süre |
|---|---|---|
| Bağımlılık kurulumu | pass | 11 s |
| Lint | pass | 13 s |
| Testler | pass | 10 s |
| Import ve build | pass | 11 s |

### Temiz klondan kurulum doğrulandı

Kabul ölçütünün harfi harfine sınanması için depo boş bir dizine sıfırdan
klonlandı ve kuruldu. Klonlanan **35 dosya**; `uv sync --frozen` dört paketi
(`pytest`, `pyyaml`, `ruff`, `zihin`) kurdu; Python **3.11.15** çözümlendi; dört
kontrolün dördü de bu temiz kopyada geçti.

Bu, CI'ın yaptığından ayrı bir doğrulama: CI zaten her koşuda temiz bir
`actions/checkout` yapıyor, ama bu sınama klonun **özel depo üzerinden** de
sorunsuz çalıştığını ve `.gitignore`'un kuruluma gereken hiçbir dosyayı
dışarıda bırakmadığını gösteriyor.

### Lisans kanonik metin

Apache 2.0, `apache.org` üzerinden indirildi. 11358 bayt, sha256
`cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`. Elle
yazılmadı.

## Karşılaşılan sürprizler

### 1. AppWorld'ün deposu ile PyPI sürümü aynı şey değil

Bu, kurulumun tamamını belirleyen olgu oldu. PyPI'daki son sürüm `0.1.3.post1`,
depo `main` ise `0.2.0.dev0`. Aşama 5'in ihtiyaç duyduğu referans ajan iskelesi
(`experiments/code/simplified/`) ve prompt dosyası yalnız `main`'de. Dolayısıyla
AppWorld yayımlanmış bir sürüme değil, hareketli bir dalın tek bir commit'ine
sabitlenecek. Bu bir tekrarlanabilirlik borcu; `docs/09-limitations.md` S-01'e
yazıldı.

### 2. Windows'ta yürütme zaman aşımı diye bir şey yok

AppWorld'ün `main` dalı Windows'u destekliyor ve kendi CI'ında `windows-latest`
üzerinde doğruluyor. Ancak `timeout_call` Windows'ta istisna fırlatıyor ve
`default_timeout_seconds` zorla `None` yapılıyor. Yani ajan kodu duvar saati
sınırı olmadan koşuyor. Bu, platform kararının WSL2'ye dönmesinin
sebeplerinden biri oldu (K-01).

Ek olarak AppWorld'ün kendi Windows CI'ı doğrulamayı ilk dört göreve kısıtlıyor
ve yanında `super slow on windows / figure out why` notu taşıyor.

### 3. Referans çözümler elimize geçmeyebilir

`appworld download data` varsayılan olarak `minimal` modda iniyor. `partial` ve
`full` modlar bakımcıya özel anahtar istiyor, ve referans çözümler yalnız `full`
modda. Bunun doğrudan bir sonucu oldu: adım tavanının çapası referans çözüm
uzunluğundan, doğrulayıcının beklediği durum değiştiren çağrı sayısına taşındı
(K-11).

### 4. Bir sunucu süreci aynı anda tek bir dünya tutuyor

AppWorld motoru ajan sürecinden ayrı koşabiliyor. Ama bir süreç içinde ikinci
bir dünya başlatmak HTTP 400 döndürüyor; sebep freezegun'ın zamanı süreç geneli
taklit etmesi. Paralel epizod, port başına ayrı sunucu süreci gerektiriyor. Bu
`experiments/pilot-plan.md` içine bir bütçe kalemi olarak yazıldı.

### 5. `.wslconfig` iptal edilmiş bir denemeden kalmıştı

Host geneli WSL yapılandırması WSL'i 4 GB'a kapatıyordu ve var olmayan bir
belgeye atıf yapıyordu. Yedeği alınıp bu proje için yeniden yazıldı (K-02).

## Açık kalanlar

Üç config alanı cevap beklerken önerilen değerlerle yazıldı. Cevap geldiğinde
düzeltilecek; `docs/08-decisions.md` içinde A-01, A-02, A-03 olarak duruyorlar.

- `retrieval.mode` hangi ekseni taşıyor (varsayım: `baseline`'da `none`, kalan
  beşinde `standard`).
- `fill.enabled` baseline dışındaki beş koşulda açık mı (varsayım: evet).
- `failures.source` enum'u üç değer mi taşıyor (varsayım: evet, `naive` yok).

## Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | evet |
| Testi yazıldı | evet, 17 test |
| Loglandı | CHANGELOG ilk girişi yazıldı |
| Belgesi yazıldı | README, 08-decisions, 09-limitations |
| Hata durumu düşünüldü | bozuk config'lerin reddi test edildi |
| PR üzerinden gözden geçirildi | PR #1 açıldı |
| Temiz kurulumda baştan çalıştırıldı | evet — sıfırdan klon + kurulum, dördü geçti |

## #2 — Aşama 0 — Depo iskeleti, bağımlılık kilidi, CI

- Branch: `stage-0-repo-skeleton`
- Merged: 2026-08-10

<!-- body, verbatim except for task text -->

# Aşama 0 raporu — Depo iskeleti

Bu rapor kodun ne yaptığını değil, neyi doğruladığını anlatıyor.

## Kabul ölçütü ne diyordu

> Temiz bir makinede depo klonlanıp bağımlılıklar kurulabiliyor, CI'nın dördü de
> yeşil.

## Neyi doğruladık

### Bağımlılık kurulumu tekrarlanabilir

`uv.lock` içinde **9 paket** dondurulmuş durumda. Kurulum `--frozen` bayrağıyla
yapılıyor, yani kilit dosyası çözümlemeyi belirliyor; CI'da ayrıca `uv lock
--check` koşuyor, kilit dosyası `pyproject.toml` ile uyumsuz kalırsa iş düşüyor.

Kilitlenen bağımlılıklar bilerek az. Çalışma zamanında tek bir tanesi var:
`pyyaml`. Geliştirme tarafında `pytest` ve `ruff`.

**AppWorld kasten bu listede yok.** Aşama 0'ın ölçütü "temiz makinede
bağımlılıklar kurulabiliyor"; o ölçütü henüz gerekmeyen ağır ve Git LFS isteyen
bir bağımlılıkla sınamak, ölçütü doğrulamak değil bulandırmak olurdu. AppWorld
Aşama 1'in PR'ında girecek.

### Python sürümü gerçekten sabit

`requires-python = "==3.11.*"` ve `.python-version` içinde `3.11`. Kurulum
CPython 3.11.15 ile yapıldı. Aralık değil, sabit: 3.12'ye kayma ihtimali yok.

Kullanılan araç **uv 0.11.28**. Hem yerelde hem CI'da aynı sürüme sabitlendi;
`astral-sh/setup-uv@v5` adımına sürüm açıkça yazıldı.

### Altı config dosyası gerçekten aynı şemayı taşıyor

Bu iddia yorum değil, test. `tests/test_config_schema.py` şunları denetliyor:

- `config/` altında tam olarak altı `.yaml` var, adları beklenen altı koşul.
- Altı dosyanın **anahtar ağacı birebir aynı** — değerler atılıp yalnız yapı
  karşılaştırılıyor.
- Her dosya yükleniyor ve `condition` alanı dosya adıyla eşleşiyor.
- Kalkan altı koşulun hepsinde açık. Kazara kapanması testi düşürür.
- `baseline` hiçbir kart taşımıyor; kalan beş koşul eşit slot taşıyor (beşer).
  Hacim kontrolü ancak bu eşitlik korunursa anlamlı.
- Bozuk yapılandırmalar reddediliyor: eksik alan, tanınmayan alan, tanımsız enum
  değeri, ve slot sayısı yerine boole (Python'da `bool` bir `int` alt türü
  olduğu için bu sessizce geçebilirdi).

Toplam **17 test**, hepsi geçiyor.

### Dört kontrol de yerelde geçiyor

| Kontrol | Sonuç |
|---|---|
| Bağımlılık kurulumu (`uv sync --frozen`, `uv lock --check`) | geçti |
| Lint (`ruff check`, `ruff format --check`) | geçti, 17 dosya biçimli |
| Testler (`pytest`) | 17 geçti |
| Import ve build (`import zihin`, `uv build`) | geçti, sdist + wheel üretildi |

CI dört ayrı iş olarak `ubuntu-24.04` üzerinde koşuyor. Koşucu sürümü açıkça
yazıldı, `ubuntu-latest` kullanılmadı — o etiket zamanla kayar ve geliştirme
ortamıyla eşleşme kaybolur.

### Dördü CI'da da yeşil

PR #1 üzerinde, `ubuntu-24.04` koşucusunda:

| İş | Sonuç | Süre |
|---|---|---|
| Bağımlılık kurulumu | pass | 11 s |
| Lint | pass | 13 s |
| Testler | pass | 10 s |
| Import ve build | pass | 11 s |

### Temiz klondan kurulum doğrulandı

Kabul ölçütünün harfi harfine sınanması için depo boş bir dizine sıfırdan
klonlandı ve kuruldu. Klonlanan **35 dosya**; `uv sync --frozen` dört paketi
(`pytest`, `pyyaml`, `ruff`, `zihin`) kurdu; Python **3.11.15** çözümlendi; dört
kontrolün dördü de bu temiz kopyada geçti.

Bu, CI'ın yaptığından ayrı bir doğrulama: CI zaten her koşuda temiz bir
`actions/checkout` yapıyor, ama bu sınama klonun **özel depo üzerinden** de
sorunsuz çalıştığını ve `.gitignore`'un kuruluma gereken hiçbir dosyayı
dışarıda bırakmadığını gösteriyor.

### Lisans kanonik metin

Apache 2.0, `apache.org` üzerinden indirildi. 11358 bayt, sha256
`cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`. Elle
yazılmadı.

## Karşılaşılan sürprizler

### 1. AppWorld'ün deposu ile PyPI sürümü aynı şey değil

Bu, kurulumun tamamını belirleyen olgu oldu. PyPI'daki son sürüm `0.1.3.post1`,
depo `main` ise `0.2.0.dev0`. Aşama 5'in ihtiyaç duyduğu referans ajan iskelesi
(`experiments/code/simplified/`) ve prompt dosyası yalnız `main`'de. Dolayısıyla
AppWorld yayımlanmış bir sürüme değil, hareketli bir dalın tek bir commit'ine
sabitlenecek. Bu bir tekrarlanabilirlik borcu; `docs/09-limitations.md` S-01'e
yazıldı.

### 2. Windows'ta yürütme zaman aşımı diye bir şey yok

AppWorld'ün `main` dalı Windows'u destekliyor ve kendi CI'ında `windows-latest`
üzerinde doğruluyor. Ancak `timeout_call` Windows'ta istisna fırlatıyor ve
`default_timeout_seconds` zorla `None` yapılıyor. Yani ajan kodu duvar saati
sınırı olmadan koşuyor. Bu, platform kararının WSL2'ye dönmesinin
sebeplerinden biri oldu (K-01).

Ek olarak AppWorld'ün kendi Windows CI'ı doğrulamayı ilk dört göreve kısıtlıyor
ve yanında `super slow on windows / figure out why` notu taşıyor.

### 3. Referans çözümler elimize geçmeyebilir

`appworld download data` varsayılan olarak `minimal` modda iniyor. `partial` ve
`full` modlar bakımcıya özel anahtar istiyor, ve referans çözümler yalnız `full`
modda. Bunun doğrudan bir sonucu oldu: adım tavanının çapası referans çözüm
uzunluğundan, doğrulayıcının beklediği durum değiştiren çağrı sayısına taşındı
(K-11).

### 4. Bir sunucu süreci aynı anda tek bir dünya tutuyor

AppWorld motoru ajan sürecinden ayrı koşabiliyor. Ama bir süreç içinde ikinci
bir dünya başlatmak HTTP 400 döndürüyor; sebep freezegun'ın zamanı süreç geneli
taklit etmesi. Paralel epizod, port başına ayrı sunucu süreci gerektiriyor. Bu
`experiments/pilot-plan.md` içine bir bütçe kalemi olarak yazıldı.

### 5. `.wslconfig` iptal edilmiş bir denemeden kalmıştı

Host geneli WSL yapılandırması WSL'i 4 GB'a kapatıyordu ve var olmayan bir
belgeye atıf yapıyordu. Yedeği alınıp bu proje için yeniden yazıldı (K-02).

## Açık kalanlar

Üç config alanı cevap beklerken önerilen değerlerle yazıldı. Cevap geldiğinde
düzeltilecek; `docs/08-decisions.md` içinde A-01, A-02, A-03 olarak duruyorlar.

- `retrieval.mode` hangi ekseni taşıyor (varsayım: `baseline`'da `none`, kalan
  beşinde `standard`).
- `fill.enabled` baseline dışındaki beş koşulda açık mı (varsayım: evet).
- `failures.source` enum'u üç değer mi taşıyor (varsayım: evet, `naive` yok).

## Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | evet |
| Testi yazıldı | evet, 17 test |
| Loglandı | CHANGELOG ilk girişi yazıldı |
| Belgesi yazıldı | README, 08-decisions, 09-limitations |
| Hata durumu düşünüldü | bozuk config'lerin reddi test edildi |
| PR üzerinden gözden geçirildi | PR #1 açıldı |
| Temiz kurulumda baştan çalıştırıldı | evet — sıfırdan klon + kurulum, dördü geçti |

## #3 — Aşama 0 ardılı — Koşul şeması kapandı, durum dosyaları eklendi

- Branch: `stage-0-followup-config-and-status`
- Merged: 2026-08-10

<!-- body, verbatim except for task text -->

# Aşama 0 ardılı — Koşul şeması kapandı, durum dosyaları eklendi

Bu PR bir aşama değil, Aşama 0'ın ardılı: üç açık config sorusunun cevabını
uyguluyor ve iskelete altı taslak dosya ekliyor.

Rapor metni `docs/reports/asama-0.md` altındaki **Ardıl** bölümünde.

## Neyi doğruladık

### İki kritik kontrast artık iddia değil, test

Analiz planı iki kontrasta dayanıyor ve ikisi de belgede yalnız cümle olarak
duruyordu:

- `baseline` ↔ `irrelevant_retrieval` — fark saf bağlam hacmi.
- `skills` ↔ `irrelevant_retrieval` — fark saf içerik.

Şimdi `tests/test_config_schema.py` içinde denetleniyorlar. İkincisi
`dataclasses.fields` üzerinden bütün alanları karşılaştırıyor, yani şemaya
sonradan eklenecek bir alan da denetime otomatik giriyor.

### Testler boşuna geçmiyor

Dört mutasyon denendi, dördü de doğru testler tarafından yakalandı:

| Mutasyon | Düşen test(ler) |
|---|---|
| `skills.yaml`: `fill.enabled` kapatıldı | `test_non_baseline_conditions_carry_equal_slots`, `test_pure_content_contrast_differs_in_one_field_only` |
| `irrelevant_retrieval.yaml`: `skills.source` → `standard` | `test_pure_content_contrast_differs_in_one_field_only`, `test_pure_volume_contrast_carries_no_relevant_content` |
| `failures.yaml`: `retrieval.mode` → `none` | `test_retrieval_mode_is_none_only_in_baseline` |
| `skills_failures.yaml`: `failure_slots` 5 → 3 | `test_non_baseline_conditions_carry_equal_slots` |

Her mutasyondan sonra zemin geri getirilip 20 testin tamamının geçtiği
doğrulandı.

### Dört kontrol yerelde geçiyor

`ruff check` temiz, `ruff format --check` temiz, 20 test geçti, `import zihin`
çalışıyor. CI koşusu bu PR üzerinde.

### Kodlama ve satır sonları

Yeni dosyaların tamamı UTF-8 (`experiments/decisions.csv` yalnız İngilizce
başlık taşıdığı için us-ascii). Depoda CRLF yok.

## Ne değişti

### `retrieval.mode` (A-01 → K-28)

Alan artık getirme yöntemini taşıyor, içerik alakasını değil. Değerler `none` ve
`symbolic` (önceden `none` ve `standard`). Önceki hâlde alan `skills.source` ile
aynı ekseni taşıyor gibi duruyordu ve `retrieval.mode: none` ile
`skills.source: standard` gibi tanımsız birleşimler yazılabiliyordu.

### `fill.enabled` (A-02 → K-29)

Taban kapalı, kalan beşi açık. Gerekçe karar kaydına yazıldı: `skills`
koşulunun hata slotları dolguyla doluyor, yoksa `skills_failures` ile kart
sayısı eşitlenmiyor ve iki koşul arasındaki fark içerikten çıkıp hacme kayıyor.

### `failures.source` (A-03 → K-30)

Üç değer: `none`, `standard`, `irrelevant`. `naive` eklenmedi — naif derleyici
yalnız beceri üretiyor, kullanılmayan enum değeri bırakılmıyor.

### Belgedeki bir hata düzeltildi

"Saf içerik" kontrastı `skills_failures` ↔ `irrelevant_retrieval` olarak
yazılıydı, hem `config/irrelevant_retrieval.yaml` yorumunda hem README'de. O
çift iki alanda birden ayrışıyor, tek eksenli değil. Doğrusu `skills` ↔
`irrelevant_retrieval` (K-31).

### Altı taslak dosya (K-33)

`PROJECT_STATUS.md`, `REPRODUCE.md`, `PILOT_REPORT.md`,
`docs/10-external-review.md`, `docs/11-falsification.md`,
`experiments/decisions.csv`.

`PROJECT_STATUS.md` bileşen, durum, kanıt, eksik sütunlarını taşıyor; ilk satırı
Aşama 0'dan doldu. `doğrulandı` yalnız kanıt sütunu doluysa yazılıyor.

İçerik taşıyan üç şey kendi aşamasında: `shield_violations` Aşama 3'te,
`DATA_MODEL.md` Aşama 3'ün çıktısı, `REPRODUCE.md`'nin içi Aşama 1'de.

### Aşama 1'in kabul ölçütü genişledi (K-32)

Temiz makinede kurulum AppWorld dahil yeniden doğrulanacak. Git LFS önkoşulu
`REPRODUCE.md`'ye yazıldı; gerçekten gerekli olduğu Aşama 1'de ölçülecek.

## Karşılaşılan sürpriz

Mutasyon denemesinin ilk koşuşu geçersizdi. Her mutasyondan sonra
`git checkout -- config/` ile zemine dönüyordum ama config değişikliklerim henüz
işlenmemişti; geri alma mutasyonla birlikte onları da sildi. İkinci ve üçüncü
mutasyon `retrieval.mode: standard`'a dönmüş dosyalarla koştu, hepsi yeni enum'a
takılıp `test_each_config_loads`'ta düştü ve mutasyonun kendisi hiç sınanmadı.
Değişiklikler işlendikten sonra deneme tekrarlandı; betik artık zemin kirliyse
baştan çıkıyor.

## Hâlâ açık

**A-04** — `experiments/decisions.csv` sütunları söylenmedi. Şimdilik önerilen
başlık satırı duruyor:

```
decision_id,stage,title,status,supersedes,rationale_summary
```

`status` karar kaydındaki üç hâli karşılıyor (`active`, `superseded`, `open`),
`supersedes` üstü çizilen kararı gösteriyor (K-11, K-13 gibi). Dosya boşken
düzeltmek en ucuzu.

## #4 — Aşama 1 — AppWorld kurulumu ve tek görev uçtan uca

- Branch: `stage-1-appworld`
- Merged: 2026-08-10

<!-- body, verbatim except for task text -->

# Aşama 1 raporu — AppWorld kurulumu ve tek görev

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

## Kabul ölçütü ne diyordu

> Bir görev başlıyor, ajan API çağrıları yapıyor, doğrulayıcı bir hüküm
> döndürüyor, ve bu hüküm okunabilir bir yerde duruyor. Aynı görevi ikinci kez
> koştuğunda veritabanının başlangıç durumuna dönmüş olduğunu doğrula.

Aşama 0'ın gözden geçirmesinde bir madde daha eklendi: temiz makinede kurulum
AppWorld dahil yeniden doğrulanacak, Git LFS önkoşulu REPRODUCE.md'ye yazılacak
(K-32).

## Kurulumu belgeden takip ettim

Resmî sıra şu: `pip install appworld`, sonra `appworld install`, sonra
`appworld download data`. Bizde ilk adım `uv sync --all-groups --frozen`, çünkü
paket PyPI'dan değil GitHub `main` dalından tek bir commit'e sabitlenerek
geliyor (K-10). Kalan iki adım olduğu gibi koşuldu.

Sabitlenen commit `a072b7a`. Kurulan sürüm `0.2.0.dev0`, toplam 114 paket. Veri
198 MB ve `data/` altına açılıyor, dizin izlenmiyor.

Bölme başına görev sayısı: train 90, dev 57, test_normal 168, test_challenge
417.

## Neyi doğruladım

### Görev uçtan uca koşuyor

`scripts/run_single_task.py` referans iskeleyi değiştirmeden kuruyor, tek görevi
koşturuyor ve ardından değerlendirmeyi çağırıyor. Kullanılan sınıf
`SimplifiedReActCodeAgent`, görev `82e2fac_1`, model
`qwen2.5-coder:1.5b-instruct-q4_K_M`.

Ajan API çağırıyor. `logs/api_calls.jsonl` dolu ve çağrılar gerçek uç noktalara
gidiyor: `/spotify/library/playlists`, `/supervisor/account_passwords` gibi.

Doğrulayıcı hüküm üretiyor ve hüküm iki yerde okunabiliyor. Birincisi
`tasks/82e2fac_1/evaluation/report.md`, içinde bir geçen ve bir düşen sınama
var. Geçen sınama `assert no model changes`. Düşen sınama `assert answers
match`, ayrıntısıyla birlikte: `'<<not_given>>' == 'a love that never was'`.
İkincisi `evaluations/on_only_82e2fac_1.txt` ve `.json`, toplu metrikleri
taşıyor ve `task_goal_completion` değerini 0.0 veriyor.

Görev çözülmedi. Kabul ölçütü bunu istemiyor, 1.5B bir modelden AppWorld'ü
çözmesini de beklemiyoruz.

### Veritabanı epizot başına sıfırlanıyor

Testi `tests/test_appworld_reset.py`. Koşu 1 not yaratıp aynı koşuda okuyor,
koşu 2 aynı görevi yeniden açıp o kimliği istiyor ve `409 The note with id 3084
does not exist` alıyor.

Buraya iki yanlış çapadan geçtim. İkisini de yazıyorum, çünkü ikisi de geçen ama
hiçbir şey kanıtlamayan sınamalardı.

İlki `dbs/model_hashes.json` karşılaştırmasıydı. Boş koşularda o dosya `{}`
geliyor. Yani tam durumu değil, yalnız değişen modelleri tutuyor. İki boş
koşunun eşit çıkması, sıfırlama hiç çalışmasa bile olacak bir şeydi.

İkincisi not sayısıydı. `search_notes` sayfalı ve beşte sabit kalıyor.
`create_note` başarıyla dönüp `note_id` verdiği hâlde sayaç kıpırdamadı, yani
sınama değişimi göremiyordu.

Testin gövdesindeki yaratma adımı bu yüzden var. Onsuz sınama, sıfırlama hiç
çalışmasa bile geçerdi.

### Temiz makine kurulumu AppWorld dahil sınanıyor

CI'a `git lfs install` adımı girdi ve `uv sync` artık AppWorld ile birlikte
koşuyor. K-32'nin istediği doğrulama her PR'da tekrarlanıyor.

## Karşılaştığım sürprizler

### Git LFS önkoşulu teoride değil pratikte ısırdı

`uv`, `[tool.uv.sources]` içinde `lfs = true` yazılmadıkça bundle dosyalarını
131 baytlık işaretçi olarak kuruyor. `appworld install` de şu satırla düşüyor:
`File .../apps.bundle is a Git LFS pointer and not a bundle file`. Bayrakla
gelen dosyalar 193950 ve 204426 bayt, elle klonlananla birebir aynı.

Makinede `git lfs` paketi kuruluydu ama `git lfs install` çalıştırılmamıştı,
yani filtre `~/.gitconfig` içinde yoktu. Paketin varlığı yetmiyor.

### Referans iskele `appworld` paketinde değil

`appworld run` komutu `appworld_agents` modülünü istiyor. O modül PyPI'da yok ve
deposu diye tahmin ettiğim adres 404 veriyor. Depodaki
`experiments/code/simplified/` dosyaları da kendi kendine yetmiyor, hepsi
`appworld_agents.*` import ediyor.

Kaynağı aynı depo. `experiments/pyproject.toml`, `appworld-agents` adıyla ikinci
bir dağıtım tanımlıyor ve `appworld_agents = "."` satırıyla `experiments/`
dizinini paket köküne bağlıyor. İkisini de aynı commit'e sabitledim, ikincisi
`subdirectory = "experiments"` ile geliyor.

Yönerge dosyası kurulu paketin içinde geliyor, boyutu 11350 bayt. Aşama 5'in
kopyalama kararı (K-23) bu dosyadan yapılacak.

### İskele `num_ctx` geçirmiyor

K-19 litellm yolunu birinci sıraya koymuştu. Bağlantı o yoldan kuruluyor ama
bağlam penceresi geçmiyor. Sebebi şu: iskelenin `LanguageModel` sınıfı hangi
anahtarların kabul edileceğini `litellm.completion` imzasından çıkarıp beyaz
liste uyguluyor. Listede 41 ad var, `num_ctx` yok. `api_base` de yok, onun
yerine `base_url` var.

Bunun ölçülen sonucu ağır. Ollama bağlam penceresini VRAM'e bakarak 4096
seçiyor. Yönerge dosyası tek başına 11350 bayt ve ajan adım başına yaklaşık 3800
girdi tokenı harcıyor. 4096'lık pencerede koşulan iki epizottan biri 18 API
çağrısı yaptı, diğeri sıfır. İkincisinde model `from apis import api_docs,
supervisor` yazdı, sandbox `Usage of the following module is not allowed: apis`
diyerek reddetti ve hiçbir çağrı sunucuya ulaşmadı.

Sunucu tarafında `OLLAMA_CONTEXT_LENGTH=32768` ile pencereyi açtım. Sıfır
ortadan kalktı ama davranış oynak kaldı, üç epizot 19, 1 ve 19 çağrı yaptı. Bu
yol K-19'un saydığı dördünden hiçbiri değil, beşinci bir yol. Kalıcı karar Aşama
4'ün ve A-05 olarak açık duruyor.

### Aynı seed aynı davranışı vermiyor

Yukarıdaki 19, 1, 19 dizisi aynı seed ve aynı sıcaklıkla alındı. Seed 123,
sıcaklık 0.2. Seed'in Ollama'ya ulaşıp ulaşmadığını doğrulamadım. S-11 olarak
kaydedildi, Aşama 4 ayrıca sınayacak.

### İskele anahtarsız açılmıyor

`LanguageModel`, istemci litellm olsa bile kurucusunda bir `OpenAI()` nesnesi
üretiyor ve o nesne `OPENAI_API_KEY` olmadan açılmıyor. Yerel modelde anahtar
kullanılmadığı için betik yer tutucu bir değer koyuyor. Gerçek bir sağlayıcıya
çağrı gitmiyor.

### Ağ köprüsü beklediğimden ucuza çözüldü

NAT kipinde WSL'den Windows'taki Ollama'ya erişimin üç adresten de kesildiğini
ölçtüm. Sebebi Hyper-V güvenlik duvarının `DefaultInboundAction` değerinin
`Block` olması. `networkingMode=mirrored` bunu güvenlik duvarı kuralı olmadan
çözdü ve sunucunun `0.0.0.0`'a bağlanmasını da gereksiz kıldı. Ollama şimdi
yalnız `127.0.0.1` dinliyor.

K-03'ün DNS kaygısını sınadım, çıkmadı. `pypi.org`, `github.com` ve
`registry.ollama.ai` çözüldü, HTTPS istekleri döndü, `uv lock --check` geçti.
S-10 kapandı.

## Ölçemediklerim

`num_ctx`'in isteğe gerçekten 32768 olarak yansıyıp yansımadığını istek
düzeyinde doğrulamadım. Yalnız sunucunun yapılandırma dökümünde
`OLLAMA_CONTEXT_LENGTH = 32768` yazdığını ve davranışın değiştiğini gördüm.
İstek düzeyinde doğrulama Aşama 4'ün kabul ölçütünde zaten var.

Seed'in Ollama'ya geçip geçmediğini ölçmedim.

Aşama 1'de hiçbir performans ölçümü yok. Sunucu şu an `OLLAMA_KV_CACHE_TYPE`
boş ve `OLLAMA_FLASH_ATTENTION` false ile koşuyor. Aşama 4 onu kendi betiğinden
yeniden başlatacak.

## Yerel-yalnız kontroller

`appworld` işaretli testler CI'da koşmuyor. Listesi REPRODUCE.md içinde,
koşucusu `scripts/local_checks.sh` (K-35).

Son koşu: `2026-08-10T20:57:13+03:00`, commit `68c69c8`. Bir test geçti, yirmi
test elendi.

## Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet |
| Testi yazıldı | Evet, 21 test. Biri `appworld` işaretli |
| Loglandı | CHANGELOG girdisi yazıldı |
| Belgesi yazıldı | REPRODUCE, 08-decisions, 09-limitations, PROJECT_STATUS |
| Hata durumu düşünüldü | `MODEL_SERVER_URL` yoksa betik açıklamayla duruyor, rapor dosyası yoksa çıktı bunu söylüyor |
| PR üzerinden gözden geçirildi | PR açıldı |
| Temiz kurulumda baştan çalıştırıldı | CI AppWorld dahil kuruyor. Adımlar REPRODUCE.md'de ve hepsi koşuldu |

## #5 — Aşama 2 — AppWorld olgu raporu

- Branch: `stage-2-appworld-facts`
- Merged: 2026-08-10

<!-- body, verbatim except for task text -->

# Aşama 2 raporu — AppWorld olgu raporu

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor. Ölçümlerin
tamamı `docs/appworld-olgular.md` içinde; burada özeti ve karşılaştığım
sürprizler var.

## Kabul ölçütü ne diyordu

> Belge yazılmış, her madde ya ölçülmüş bir sayı ya da gerekçeli bir ÖLÇÜLEMEDİ
> taşıyor.

Üstüne bu aşamaya iki madde eklendi: S-11 kapatılacak ve on iki epizotluk
ölçümdeki tek çağrılı epizot açıklanacak.

## Yedi sorunun durumu

| Soru | Durum |
|---|---|
| 1. Bölmeler ve görev sayıları | ölçüldü |
| 2. Zorluk bölmesi ne içeriyor | ölçüldü, uygulama adları için vekil kullanıldı ve vekil sınandı |
| 3. Referans çözümler | ölçüldü |
| 4. Görev başına API çağrısı dağılımı | ölçüldü, kaynağından |
| 5. Veritabanı sıfırlaması | ölçüldü |
| 6. Okuma ve yazma sınıflandırması | ölçüldü |
| 7. Tur başına API çağrısı | ölçüldü ama **kullanılamaz**, gerekçesi aşağıda |
| 8. Motorun ayrılabilirliği | incelendi |

## Karşılaştığım sürprizler

### Referans çözümler elimizdeymiş

S-02, `appworld download data` varsayılan kipte indiği için referans çözümlerin
elimize hiç geçmeyebileceğini söylüyordu. Yanlışmış. 147 görev `full` kipte
geliyor ve o 147 görev tam olarak train ile dev'in kendisi.
`metadata.json` içindeki `mode` alanı bunu açıkça yazıyor.

Bunun iki sonucu oldu. Üçüncü soru tahminle değil sayıyla cevaplandı: referans
çözüm başına ortalama 53,44 API çağrısı. Dördüncü soru da kendi koşularımdan
değil kaynağından cevaplandı, çünkü `metadata.num_api_calls` 732 görevin
hepsinde var ve 147 görevde `api_calls.json` uzunluğuyla birebir tutuyor.

### Eğitim bölmesi ortamın yarısını bile görmüyor

`required_apps.json` üzerinden saydım. Train ve dev'in 147 görevi, on bir
kullanıcı uygulamasının yalnız beşine dokunuyor: `spotify`, `phone`, `venmo`,
`file_system`, `simple_note`. `amazon`, `gmail`, `splitwise` ve `todoist` o 147
görevin hiçbirinde geçmiyor.

Bu, ikinci sorunun cevabını ilk baktığımdan daha keskin yapıyor. Zorluk bölmesi
yalnız daha çok uygulamaya dokunmuyor, eğitimde hiç bulunmayan uygulamalara
dokunuyor.

### Vekil ölçüm ilk hâliyle çöp çıktı

Test bölmelerinde `required_apps.json` yok, o yüzden uygulama adlarını çıkarmak
için vekil yazmam gerekti. İlk vekilim `evaluation.py` dosyasında uygulama adı
arıyordu. Referans listesi olan 147 görevde sınadım: 147'sinin sıfırında tam
isabet, Jaccard 0,227.

İki arızası vardı. `admin` ve `supervisor` her görevde yanlışlıkla sayılıyordu,
çünkü onlar değerlendirme altyapısının import'ları. Ve gerçek uygulamaların
yaklaşık yarısını kaçırıyordu.

Altyapı uygulamalarını eleyince yüzde 46,9'a çıktı. Görev yönergesinden okuyan
ikinci vekil yüzde 75,5 verdi, Jaccard 0,878. Rapora giren sayılar bu vekilden
ve hata profili de rapora yazıldı.

Sınamasaydım ilk vekilin ürettiği tabloyu olgu diye yazacaktım.

### Yedinci sorunun sayısı kullanılamaz

On iki epizot koştum. 223 model turunda toplam 1 API çağrısı çıktı, tur başına
0,0045. On bir epizot hiç API çağırmadan yirmi adımlık tavana dayandı.

Sayı ortamı değil modeli ölçüyor. `qwen2.5-coder:1.5b` bu görevde çoğunlukla
çalışmayan kod üretiyor. Ölçek ekseninin en küçük noktası taban etkisine
yapışmış durumda ve orada ölçülecek bant yok. S-14 olarak açtım; ölçüm Aşama
4'te 3B ve 7B ile tekrarlanacak.

Kullanılabilir tek sayı adım başına 5958 girdi tokenı. Bu bağlam bütçesi için
doğrudan kullanılabilir ve Aşama 1'de tahmin ettiğim 3800 rakamını düzeltiyor.

### Zaman ölçümü freezegun yüzünden bozuldu

Beşinci sorunun maliyet ölçümü ilk denememde anlamsız sayılar üretti. Dünya
açılışı 1684409978 saniye sürüyor görünüyordu. Sebebi AppWorld'ün freezegun ile
zamanı süreç geneli dondurması; `time.monotonic` de donuyor ve ölçüm görevin
simüle tarihine kayıyor.

Modülü import etmeden önce saklanan referans da kurtarmadı, yama daha derin.
Ölçümü `/proc/uptime` okuyarak yaptım. Sonuç: dünya açılışı medyan 0,150
saniye, kapanış 0,008 saniye.

## S-11 kapandı

Aşama 1'de aynı seed ve sıcaklıkla koşulan üç epizot 19, 1 ve 19 API çağrısı
vermişti. Bu, üç tohumlu varyans planının dayandığı seed kontrolünün hiç
olmadığı anlamına gelebilirdi.

Ölçtüm, öyle değilmiş. Seed geçiyor. Oynaklığın kaynağı modelin bellekte yüklü
olup olmaması.

Yol biraz dolambaçlı oldu ve ara sonuçlar yanıltıcıydı. İlk sınamam litellm
üzerinden aynı seed'le iki çağrı yaptı ve farklı çıktı verdi. Sonra Ollama'nın
kendi ucunda aynı sınama tuttu. Bu, suçlunun litellm olduğunu gösteriyordu ve
öyle yazsaydım yanlış olurdu. Deseni görmek için litellm üzerinden dört çağrı
yaptım, dördü de birbirinin aynısı çıktı ve yerli uçtan gelenle eşleşti.
Ayrışan tek şey bütün dizinin ilk çağrısıydı.

Sonra modeli açıkça boşaltıp sınadım. İki turda da aynı sonuç: soğuk çağrı
`0b9d5bfca170070e`, ısınmış çağrılar `fc4f39f3c60221c4`. İkisi de kendi içinde
kararlı.

Epizot düzeyinde de aynı. Aynı görevi soğuk, ısınmış, soğuk, ısınmış sırasıyla
koşturdum. İki soğuk koşu birebir aynı yörüngeyi verdi ve 19 API çağrısı yaptı.
İki ısınmış koşu birebir aynı yörüngeyi verdi ve 1 çağrı yaptı.

Ölçüm `scripts/check_determinism.py` içinde ve tekrarlanabilir.

**Kalan belirsizliği saklamıyorum.** "Isınmış" tek bir durum değil. Yukarıdaki
ısınmış koşu 1 çağrı verdi ama on iki epizotluk ölçümde aynı görev yine ısınmış
modelle koşuldu ve 0 çağrı verdi. Aradaki fark modelin daha önce hangi istekleri
gördüğü ve bunu istemciden görmüyoruz. S-13 olarak açtım.

Tasarıma sonucu şu: tekrarlanabilirlik için her epizottan önce modeli boşaltmak
gerekiyor. Bu K-21'in `keep_alive` gerekçesiyle çelişiyor, takas artık ölçülmüş
ve karar Aşama 4'ün.

## Tek çağrılı epizot açıklandı

Gerçek oynaklık değil, yakalanmamış bir arıza biçimiymiş. Görev şuydu: "[`692c77d_1`: task instruction removed under AppWorld's license; `sha256:a950a91993090db7f485be0426584f1860ec42f296285eec93e92d53eb7bc1cf` (S-82)]"

Adım 1'de model `for playlist in playlists:` yazdı, `playlists` tanımlı değildi,
yürütme `NameError` ile düştü ve hiçbir eylem üretilmedi. Adım 2'de model hatayı
`playlists = []` yazarak düzeltti. Döngü hiç dönmedi, ortam `Execution
successful.` dedi. Adım 3'te model işin bittiğine hükmedip
`apis.supervisor.complete_task()` çağırdı. Kaydedilen tek API çağrısı bu.

Epizot dışarıdan temiz görünüyor. Üç adım, hata yok, tamamlandı bildirimi var.
Oysa hiçbir şey yapılmadı.

Adım 1 sizin tanımladığınız dördüncü kategoriye giriyor. Adım 2 girmiyor, çünkü
yürütme hata vermedi. Beşinci bir etiket önerdim ve K-36'ya yazdım: yürütme
başarılı ama hiç eylem üretilmedi. İkisini ayırmak gerekiyor. Yürütme hatası
modelin kod yazamadığını söyler, boş başarı ise modelin görevi sessizce
etkisizleştirdiğini söyler ve doğrulayıcıya kadar hiçbir yerde alarm üretmez.

## Karara bağlananlar

- **K-36.** Adım düzeyi taksonomisi beş kategori taşıyor.
- **K-37.** Bağlam penceresi sunucu tarafındaki `OLLAMA_CONTEXT_LENGTH` ile
  veriliyor. Koşu başına doğrulanacak ve künyeye yazılacak. A-05 kapandı.
- **K-22.** Sunucu betikten ve oturumdan bağımsız başlatılacak.
- **K-21.** Yeniden açıldı, kararı Aşama 4 verecek.
- **S-02** kısmen çürüdü, **S-03** aşıldı, **S-11** kapandı. Yerlerine **S-13**
  ve **S-14** açıldı.

## Yerel-yalnız kontroller

Son koşu: `2026-08-10T22:59:31+03:00`, commit `8c1697b`. Bir test geçti, yirmi
test elendi.

## Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet, iki ölçüm betiği |
| Testi yazıldı | Bu aşamanın çıktısı belge. Ölçümlerin kendisi `scripts/check_determinism.py` ve `scripts/measure_episodes.py` ile tekrarlanabiliyor |
| Loglandı | CHANGELOG girdisi yazıldı |
| Belgesi yazıldı | `docs/appworld-olgular.md`, 08-decisions, 09-limitations, PROJECT_STATUS |
| Hata durumu düşünüldü | Vekil ölçüm referans kümede sınandı, tutmasaydı soru ÖLÇÜLEMEDİ olarak kapanacaktı |
| PR üzerinden gözden geçirildi | PR açıldı |
| Temiz kurulumda baştan çalıştırıldı | CI AppWorld dahil kuruyor, dört kontrol yeşil |

## #6 — Aşama 3 — SQLite kayıt şeması

- Branch: `stage-3-record-schema`
- Merged: 2026-08-10

<!-- body, verbatim except for task text -->

# Aşama 3 raporu — SQLite kayıt şeması

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor. Şemanın neden
öyle olduğu `DATA_MODEL.md` içinde.

## Kabul ölçütü ne diyordu

> Aşama 1'deki tek görev koşusu bu şemaya yazılıyor. Bir epizod, birden çok
> adım, adım başına birden çok eylem, eylem başına bir gözlem. Bir sorguyla
> epizodun tamamını sırayla okuyabiliyorsun. Testler bunu doğruluyor.

Üstüne bu aşamaya `shield_violations` tablosu, epizot başına model yükleme
durumu ve sıra numarası eklendi.

## Neyi doğruladım

### Gerçek bir koşu şemaya yazıldı

`scripts/record_run.py` görev `82e2fac_1` üzerinde koşuldu. Sonuç: 1 epizot,
20 adım, 19 eylem, 20 gözlem, 1 doğrulayıcı satırı.

Sayı Aşama 2'nin soğuk rejim ölçümüyle birebir aynı: orada da aynı görev 19 API
çağrısı üretmişti. Bu, kaydın koşuyu doğru yakaladığının bağımsız kontrolü.

Toplamda beş görev kaydedildi: 5 künye, 5 epizot, 86 adım, 56 eylem, 86 gözlem.

### Adım başına birden çok eylem gerçek koşuda da çıktı

İlk kaydettiğim görevde her adım tek çağrı yaptı, yani ölçütün bu maddesi
gösterilemedi. Şemanın taşıyabildiğini sentetik test zaten kanıtlıyordu ama
gerçek koşuda görmek istedim. Dört görev daha kaydettim; `6104387_1` toplam 33
eylem üretti ve bir adımında iki çağrı yaptı.

### Yalnız ekleme tetikleyiciyle zorlanıyor

Yedi tablonun her biri için ayrı ayrı sınandı: `UPDATE` ve `DELETE` denemesi
`IntegrityError` fırlatıyor. Sözleşme değil, makine kuralı.

Yabancı anahtarlar da zorlanıyor. Olmayan bir koşuya epizot yazmak reddediliyor.
Bunun bir tuzağı vardı: SQLite'ta yabancı anahtarlar varsayılan olarak kapalı ve
şemadaki `PRAGMA` satırı dosyaya yazılmıyor. Her bağlantıda açıkça açılıyor,
yoksa kısıt sessizce uygulanmıyordu.

### Epizodun tamamı tek sorguyla okunuyor

`episode_timeline` görünümü. Sol dış birleşim kullanıldı, böylece eylem
üretmeyen adımlar da satır veriyor. Bunun ayrı bir testi var: K-36'nın dördüncü
ve beşinci kategorileri hiç eylem üretmiyor ve o adımlar çizelgeden düşerse
sıfır eylemli epizot, ajanın çağırmamayı seçtiği epizotla aynı görünür.

### Testler

43 test CI'da koşuyor, sentetik veriyle. 6 test `appworld` işaretli ve gerçek
koşuyu okuyor. Tam takım 49 test.

## Karşılaştığım sürprizler

### Eylemler koşu bittikten sonra adımlara bağlanamıyor

`logs/api_calls.jsonl` düz bir liste ve hangi çağrının hangi adıma ait olduğunu
söylemiyor. Koşu bittikten sonra bakıldığında eylemleri adımlara dağıtmanın
güvenilir bir yolu yok.

K-14 bunu zaten öngörmüş: kayıt her `execute()` çağrısından sonra yürütücü
süreçte alınacak. Uyguladığım hâli şu: dosyanın o adımda uzadığı kadarı o adımın
eylemleridir.

İskeleye dokunmadım. `SimplifiedReActCodeAgent` olduğu gibi kuruluyor, yalnız
ortamın `execute` metodu dışarıdan sarmalanıyor. Prompt, ayrıştırıcı ve döngü
aynı kalıyor.

### K-37'nin kapısı ilk denemede koşuyu durdurdu

Doğrulama şartını yazdım, koştum, koşu durdu: etkin bağlam penceresi `None`
geldi. Kapı çalışıyordu ama sebebi benim yöntemimdi. `/api/ps` yalnız o an
yüklü modeli bildiriyor; model soğukken pencere okunamıyor.

Doğrulamanın modeli yüklemesi gerekiyor. Bunun bir yan etkisi var ve
saklamıyorum: doğrulama modeli ısıtıyor, yani epizot ısınmış rejimde başlıyor.
Aşama 2'de ölçüldüğü gibi o rejimde aynı görev 19 yerine 1 çağrı üretiyor.

Çözüm olarak doğrulamadan sonra modeli tekrar boşaltıyorum ve epizot soğuk
rejimde başlıyor. Aşama 2'de ölçülen tek tekrarlanabilir protokol bu. Karar
geçici; K-21'in nihai hâlini Aşama 4 belirleyecek.

### `api_calls.jsonl` beklenenden dar

S-05 yanıt gövdesinin olmayabileceğini söylüyordu. Ölçtüm: dosya yalnız
`method`, `url` ve `data` taşıyor. Yanıt gövdesi de yok, durum kodu da yok.

Yani `actions.result_status` ve `actions.error_class` bu kaynaktan
doldurulamıyor. Sütunlar duruyor ama `NULL`. Adımın başarılı olup olmadığı
yalnız gözlem metninden okunabiliyor, tek tek çağrı düzeyinde değil.

### Yalnız ekleme kuralı yazma sırasını belirledi

Epizodun bitiş zamanı ve toplamları ancak epizot bitince biliniyor, `UPDATE` de
yasak. Bu yüzden epizot bellekte biriktirilip sonunda tek işlemde yazılıyor.
Koşu ortasında çökme olursa AppWorld'ün kendi kayıtları diskte duruyor, yani
veri kaybolmuyor, yalnız veritabanına girmemiş oluyor.

## Kalkanın yüklemi için ölçüm

Kalkanın okuma/yazma ayrımının güvenilirliğini sordunuz. Önce bir düzeltme:
Aşama 2'deki yüzde 75,5'lik vekil o yüklem değildi, görev başına uygulama
listesi çıkarma vekiliydi. Kalkanın yüklemi `method` alanına dayanıyor ve o
alan doğrudan veri, 473 API'nin yüzde yüzünü kapsıyor.

Ama işaret ettiğiniz asıl risk gerçekti ve ölçtüm: durum değiştiren GET uçları
var mı? Her API işleyicisi `ast` ile ayrıştırılıp gövdesinde yazma çağrısı
arandı. On beş GET ucu yazma çağrısı içeriyor ve dağılım rastgele değil:

| Grup | Uç | Ne yapıyor |
|---|---|---|
| `download_*` | 9 | `file_system` uygulamasına dosya yazıyor, ayrı erişim jetonu alıyor |
| Tembel ilklendirme | 4 | İlk okumada varsayılan satırı yaratıyor |
| Türetilmiş alan güncellemesi | 2 | Önbellek alanını güncelliyor |

İkisini elle doğruladım. `spotify.show_volume` gerçekten `MusicPlayer.create()`
çağırıp satır yazıyor. `amazon.download_order_receipt` gerçekten `create_file()`
ile dosya oluşturuyor.

Tarama akıl kontrolünden geçti: GET dışı 302 ucun 211'inde yazma çağrısı
bulundu. Ama kalan 91'i işi yardımcı fonksiyona devrediyor, yani aynı devretme
GET tarafında da olabilir. **On beş bir alt sınır.** S-15 olarak açtım; liste
Aşama 4 öncesinde çalışma zamanı ölçümüyle genişletilecek.

## Şartnameden bir sapma

Kabul ölçütü "eylem başına bir gözlem" diyor. Şema gözlemi adıma bağlıyor,
eyleme değil. Sapma değil, K-13'ün uygulanması: şartname bu noktada
düzeltilmişti. Sebebi ölçülmüş bir olgu, `execute()` adım başına tek çıktı
dizesi döndürüyor ve eylem düzeyinde tam çıktı diye bir kavram ortamda yok.

## Karara bağlananlar

- **K-38.** Epizotlar koşullara serpiştirilerek atanıyor, bloklu değil.
- **K-39.** Model yükleme durumu ve sıra numarası epizot başına kaydediliyor.
- **K-40.** Çözülmeyen epizot, gerçekte kaç adım sürerse sürsün tavanda
  sansürleniyor.
- **K-41.** Kalkanın yüklemi `method` alanından, on beş uçluk açık istisna
  listesiyle.
- **K-42.** Biriktirme havuzu normal test görevleriyle genişletiliyor,
  değerlendirme örneklemi yalnız biriktirmede temsil edilen uygulamalardan
  çekiliyor. İkisi de ön kayda giriyor.
- **K-11.** İkinci çapa eklendi. Referans uzunluk ile doğrulayıcının beklediği
  çağrı sayısı arasındaki ilişki kalibre edilip test bölmelerine uygulanacak.
  Kalibrasyon henüz yapılmadı, Aşama 4 öncesinde çıkarılacak.
- **S-05** doğrulandı ve daraltıldı. **S-15** açıldı.

## Yerel-yalnız kontroller

Son koşu: `2026-08-10T23:35:47+03:00`, commit `49e348a`. Altı test geçti, 43
test elendi.

## Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet, şema, kayıt katmanı ve yürütücü |
| Testi yazıldı | Evet, 49 test. 43'ü CI'da, 6'sı gerçek koşuyu okuyor |
| Loglandı | CHANGELOG girdisi yazıldı |
| Belgesi yazıldı | `DATA_MODEL.md`, 08-decisions, 09-limitations, PROJECT_STATUS, REPRODUCE |
| Hata durumu düşünüldü | Yabancı anahtar, yalnız ekleme, enum kısıtları ve bağlam penceresi kapısı ayrı ayrı sınandı |
| PR üzerinden gözden geçirildi | PR açıldı |
| Temiz kurulumda baştan çalıştırıldı | CI AppWorld dahil kuruyor, dört kontrol yeşil |

## #7 — Aşama 4 — Ollama model sunum katmanı

- Branch: `stage-4-model-serving`
- Merged: 2026-08-11

<!-- body, verbatim except for task text -->

# Aşama 4 raporu — Ollama model sunum katmanı

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

## Kabul ölçütü ne diyordu

> Üç model de tek bir görevde koşuyor. Her biri için VRAM kullanımı ölçülüp
> raporlanıyor, özellikle 7B'nin 8 GB'a sığdığı ve ne kadar pay bıraktığı.
> num_ctx'in gerçekten 32768 olduğu doğrulanmış. Her koşunun künyesi tabloya
> yazılmış.

Paralel iş olarak adım tavanı kalibrasyonu da bu aşamada yapıldı.

## Neyi doğruladım

### Üç model de koştu ve üçü de tamamen VRAM'de

| Model | VRAM | Toplam | Tamamen GPU'da | Pencere | Adım | API çağrısı | Süre |
|---|---|---|---|---|---|---|---|
| `qwen2.5-coder:1.5b-instruct-q4_K_M` | 1,560 GiB | 1,560 GiB | evet | 32768 | 20 | 19 | 24,1 s |
| `qwen2.5-coder:3b-instruct-q4_K_M` | 2,602 GiB | 2,602 GiB | evet | 32768 | 20 | 4 | 51,2 s |
| `qwen2.5-coder:7b-instruct-q4_K_M` | 5,160 GiB | 5,160 GiB | evet | 32768 | 20 | 5 | 72,1 s |

Kart 8,0 GiB taşıyor. 7B yüklüyken 5,16 GiB dolu, yani 2,84 GiB pay kalıyor.
Ama sunucunun kendi ölçümü boştaki VRAM'i 6,9 GiB gösteriyor; masaüstünün
kullandığı kısım düşüldüğünde gerçek pay 1,74 GiB. Bu ikinci sayı planlama için
doğru olan.

Üçünde de `size_vram` değeri `size` değerine eşit, yani hiçbiri kısmen CPU'ya
taşmıyor. 32k bağlamın KV cache'i q8_0 ile bu rakamların içinde.

### Bağlam penceresi model başına doğrulandı

Üç modelde de sunucudan okunan etkin pencere 32768. Yapılandırmada yazması
yetmiyor; K-37'nin bütün gerekçesi bu. Ölçüm `tests/test_model_serving.py`
içinde model başına ayrı test olarak duruyor.

### Sunucu ayarları künyeye gerçekten yazıldı

| Ayar | Değer |
|---|---|
| `OLLAMA_CONTEXT_LENGTH` | 32768 |
| `OLLAMA_KV_CACHE_TYPE` | q8_0 |
| `OLLAMA_FLASH_ATTENTION` | true |
| `OLLAMA_KEEP_ALIVE` | 30m0s |
| `OLLAMA_HOST` | http://127.0.0.1:11434 |
| Ollama sürümü | 0.32.3 |

Kaynak sunucunun kendi yapılandırma dökümü, başlatıcı betiğin iddiası değil.
Ayrımı önemsiyorum: betik bir değeri geçirdiğini söyleyebilir ama sunucu onu
uygulamamış olabilir.

### Seed türetmesi deterministik ve etkili

Seed `run_id`, `task_id` ve `seed_index` üçlüsünden türetiliyor (K-20). Üç
model için çıkan değerler: 3907020950, 3001428063, 2725799904.

`tests/test_model_config.py` aynı üçlünün aynı seed'i verdiğini ve üç
bileşenden herhangi biri değiştiğinde seed'in değiştiğini sınıyor.
`tests/test_model_serving.py` ise sunucu tarafında aynı seed'in aynı çıktıyı,
farklı seed'in farklı çıktıyı verdiğini sınıyor. İkincisi olmadan birincisi
hiçbir şey kanıtlamaz: düşük sıcaklık da çıktıyı sabitleyebilirdi.

## Sayıların okunmaması gereken biçimi

Tablodaki API çağrısı sütununa bakıp "1.5B, 7B'den iyi" sonucu çıkarılamaz. Üç
model üç farklı seed'le koştu, çünkü seed `run_id` üzerinden türetiliyor ve
`run_id` model adını taşıyor. Üstelik tek görev ve tek tohum.

Söylenebilecek tek şey şu: üç model de yirmi adımlık tavana dayandı ve hiçbiri
görevi bitirmedi. S-14 ölçek ekseninin en küçük noktası için açılmıştı; bu
ölçüm taban etkisi endişesinin 3B ve 7B'yi de kapsayabileceğini gösteriyor.
Ama tek görev ve tek tohumla bunu söyleyemem, o yüzden S-14'ün kapsamını
genişletmiyorum, yalnız uyarıyı ekliyorum. Karar pilotun.

## Adım tavanı kalibrasyonu

K-11 iki çapayı birleştirmemi istemişti: train ve dev'deki referans uzunlukları
ile doğrulayıcının beklediği çağrı sayısı arasındaki ilişkiyi kalibre et, sonra
test bölmelerine uygula.

**Kalibrasyon tutmadı.** Doğrulayıcı tarafındaki aday nicelik
`ground_truth/test_data.json` içindeki `no_op_fail` sayısı. Etiketin anlamı şu:
hiçbir şey yapmayan bir ajan `no_op_pass` gereksinimini zaten geçer,
`no_op_fail` gereksinimini geçemez. Yani bu sayı doğrulayıcının aktif iş
beklediği gereksinim sayısı ve 732 görevin hepsinde var.

147 görev üzerinde ölçtüm:

- Referans çözüm uzunluğuyla korelasyon: **0,088**
- Yalnız yazma çağrılarıyla korelasyon: **0,122**
- Gereksinim başına çağrı oranı: medyan 10,75, p95 58,0, en yüksek 139,0

Çarpımsal bir çapa bu dağılımla 261 ile 986 arasında tavanlar üretiyor. Kullanılamaz.

**Ama kalibrasyona gerek yokmuş.** K-11 çapayı referans uzunluktan almaktan
vazgeçmişti ve gerekçesi test bölmelerinde referansın olmamasıydı. Çözüm dosyası
gerçekten yok. Ama `ground_truth/metadata.json` içindeki `num_api_calls` alanı
732 görevin hepsinde dolu, hiçbirinde boş değil, ve referans çözümü olan 147
görevde `api_calls.json` uzunluğuyla birebir tutuyor.

Yani çapa doğrudan `metadata.num_api_calls` olabilir. Bölme başına p95: train
144, dev 139, test_normal 81, test_challenge 178.

Bunu Aşama 2'de zaten kullanmıştım, dördüncü sorunun dağılımını oradan
çıkarmıştım. Aradaki bağlantıyı o zaman kurmamışım.

## Yanıt verisi enstrümantasyonu: birinci tercih çalışıyor

S-16 için önerdiğiniz sıranın ilkini denedim ve tuttu.

`Requester._get`, `_post`, `_patch` ve `_delete` metotları ham yanıt nesnesini
döndürüyor; o nesnede hem durum kodu hem gövde var. İstek bilgisi de aynı
çağrının argümanlarında. Tek bir sarmalama ikisini birden yakalıyor ve bu taşıma
katmanı, ajanın prompt'una, ayrıştırıcısına ve döngüsüne dokunmuyor.

Sondada yakalananlar:

```
GET  /supervisor/profile            200  {"first_name": "Joyce", ...}
GET  /supervisor/account_passwords  200  [{"account_name": "amazon", ...}]
POST /spotify/auth/token            200  {"access_token": "eyJhbGci..."}
POST /spotify/auth/token            401  {"message": "Invalid credentials"}
```

Bir tuzağı vardı ve ilk denememde tam olarak ilgilendiğim vakayı kaçırdım.
`_get` ve `_post` içinde `raise_if_failure` çağrılıyor ve başarısız yanıtta
istisna fırlatıyor. Sarmalayıcı kaydı istisnadan sonra almaya çalışırsa
başarısız çağrılar hiç kaydedilmiyor. İlk sondam yedi çağrının yedisini de 200
olarak gösterdi, oysa iki tanesi başarısızdı. Sarmalayıcı istisnayı yakalayıp
kaydettikten sonra yeniden fırlatacak şekilde düzeltildi.

Şu an yalnız yapılabilirliği gösterdim; kaydediciye bağlanması ayrı bir iş ve
biriktirme başlamadan yapılacak. `actions.result_status` ve `error_class`
sütunları zaten şemada duruyor.

## Karşılaştığım sürprizler

### Künyeye sunucu ayarları boş yazılmış

İlk koşuda künyedeki KV cache tipi, flash attention ve `keep_alive` alanları
`None` çıktı. Sebebi şu: ayarlar Windows'taki Ollama sürecinin ortamında, ölçüm
betiği ise WSL içinde koşuyor. `os.environ` oradan bunları göremiyor.

Bu K-37'nin ikinci şartının sessizce boşa çıkması demekti. Düzeltme sunucunun
kendi yapılandırma dökümünü okumak oldu.

### Model indirmesini kendi betiğim kesti

7B indirmesi yüzde yüze geldiğinde `serve_models.ps1` betiğini çalıştırdım.
Betik çalışan ollama süreçlerini durduruyor ve pull istemcisi sunucuya bağlı
olduğu için indirme manifest yazılmadan kesildi. Model listede görünmedi.
Blob'lar önbellekte kaldığı için yeniden çekmek hızlı oldu.

### Ölçüm betiği epizot yazıp adım yazmıyordu

İlk sürüm modelleri ölçüyor, künye ve epizot satırını yazıyor ama adım, eylem
ve gözlem yazmıyordu. Sonuç, `total_model_calls` alanında 20 yazan ama hiç adım
satırı olmayan bir kayıttı. Aşama 3'ün testleri bunu yakaladı ve düştü.

Düzeltme kaydedici ajanı betikten pakete taşımak oldu
(`src/zihin/recording_agent.py`). Artık iki betik de aynı kaydediciyi
kullanıyor ve her epizot dört düzeyiyle yazılıyor.

## Kalanlar

Aşama 4'ün iki kararı bilerek açık bırakıldı ve ikisi de aşağıdaki her şeyi
kilitliyor: yükleme protokolü (K-21) ve ona bağlı doğrulama zamanlaması (K-37).
Şu anki geçici çözüm her epizottan önce boşaltmak. Kalıcı hâli S-13 ile birlikte
verilecek.

## Yerel-yalnız kontroller

Son koşu: `2026-08-11T00:38:07+03:00`, commit `ec1e68d`. On dört test geçti,
56 test elendi.

## Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Sunucu betiği, ölçüm betiği, kaydedici ajan modülü |
| Testi yazıldı | Evet, 70 test. 56'sı CI'da, 14'ü yerel |
| Loglandı | CHANGELOG girdisi yazıldı |
| Belgesi yazıldı | REPRODUCE, 08-decisions, 09-limitations, PROJECT_STATUS |
| Hata durumu düşünüldü | Bağlam penceresi tutmayan model atlanıyor, sunucu ayarları sunucunun kendi beyanından okunuyor |
| PR üzerinden gözden geçirildi | PR açıldı |
| Temiz kurulumda baştan çalıştırıldı | CI dört kontrolü geçiyor |

## #8 — Aşama 5 — İskele ve boş kart slotu

- Branch: `stage-5-scaffold-slot`
- Merged: 2026-08-11

<!-- body, verbatim except for task text -->

# Aşama 5 raporu — İskele ve boş kart slotu

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

## Kabul ölçütü ne diyordu

> Aynı görev, aynı seed, aynı model. Referans iskele ve slotlu iskele aynı
> yörüngeyi üretiyor. Fark varsa nerede olduğunu göster.

## Neyi doğruladım

### Boş slot bayt bayına aynı prompt üretiyor

Referans dosya 11350 bayt. Slot işaretçisi eklenmiş kopya 11371 bayt, aradaki
21 bayt tam olarak işaretçinin kendisi. İşaretçi boş dizeyle değiştirildiğinde
üretilen metin referansla birebir aynı, sha256 özetleri eşit.

Bu prompt düzeyindeki kat ve CI'da koşuyor, çünkü yalnız dosya karşılaştırması.

### Yörüngeler birebir aynı

Aynı görev (`82e2fac_1`), aynı seed (2773802488), aynı model
(`qwen2.5-coder:1.5b-instruct-q4_K_M`). İki epizot koştu:

| Koşu | API çağrısı | Yörünge özeti |
|---|---|---|
| Referans prompt | 19 | `d2b4954cc6fc05e3` |
| Boş slotlu prompt | 19 | `d2b4954cc6fc05e3` |

Karşılaştırma `environment_io.md` dosyasının tamamı üzerinden, yani üretilen
kodun ve ortam çıktısının her satırı dahil. Fark yok, dolayısıyla gösterilecek
fark da yok.

İkisi de soğuk rejimde koştu. Rejim sabitlenmeseydi bu sınama slotu değil
yükleme durumunu ölçerdi (S-13).

### Slot konumu belgede ve config'de

Konum `before_user_task`: yönergelerin sonu ile görev talimatı bloğunun başı
arası (K-24). `config/scaffold.yaml` içinde okunabilir, şu an tek geçerli
değerde sabit.

Testler konumun gerçekten orada olduğunu denetliyor: işaretçi `USER:` bloğunun
hemen öncesinde ve kart bloğu verildiğinde tam oraya düşüyor.

## Kilitlenen kuralları uyguladım

### Seed türetmesi düzeltildi

Seed artık yalnız `task_id` ve `seed_index` ikilisinden türüyor. Model de koşul
da girmiyor.

İmzayı ayrı bir test sabitliyor. Üçüncü bir argüman geri gelirse
`test_seed_signature_takes_only_task_and_index` düşüyor. Bu, kuralın yorumla
değil makineyle korunması demek.

### Künye sözleşmesi kondu

Zorunlu alanlardan biri boşsa künye yazılmıyor ve koşu düşüyor. Sözleşme on üç
alanı kapsıyor ve her biri için ayrı bir test var. Ayrıca `context_verified`
1 değilse ve sunucu ortamındaki bir `OLLAMA_` ayarı okunamamışsa da düşüyor.

Bir testi ayrıca ekledim: sözleşme düştüğünde tabloya hiçbir satır yazılmamış
olmalı. Yarım yazılmış künye, hiç yazılmamıştan kötü.

### Model başına yükleme süresi ölçüldü

Üçer ölçümün medyanı:

| Model | Medyan yükleme | Ölçümler | VRAM |
|---|---|---|---|
| 1.5B | 2,72 s | 2,72 / 2,72 / 2,72 | 1,560 GiB |
| 3B | 3,01 s | 3,97 / 3,01 / 2,98 | 2,602 GiB |
| 7B | 3,55 s | 5,76 / 3,55 / 3,54 | 5,160 GiB |

Her modelde ilk ölçüm diğer ikisinden yüksek; disk önbelleği ısınıyor. Medyan
bu yüzden ortalamadan daha temsili.

**Üç bin epizotta soğuk protokolün maliyeti.** Epizotlar üç modele eşit
bölünürse toplam yükleme 9280 saniye, yani 2,6 saat. Epizot süreleri 24 ile 72
saniye arasında ölçüldüğü için toplam koşu 40 saatin üzerinde, yükleme payı
kabaca yüzde altı.

Karar sizin. Ölçülmüş biçimde tekdüze olan tek seçenek soğuk rejim ve bedeli
yüzde altı.

## Karşılaştığım sürprizler

### Slot Jinja değişkeni olarak yazılmadı

İlk düşündüğüm çözüm prompt'a `{{ cards }}` gibi bir Jinja değişkeni koymaktı.
İki sebeple vazgeçtim.

Birincisi, iskele render parametrelerini kendisi kuruyor
(`instruction`, `main_user`, `app_descriptions`). Yeni bir parametre eklemek
için `initialize` metodunu geçersiz kılmak gerekirdi ve o metot iskelenin
mantığı; dokunmamam gereken yer tam orası.

İkincisi, parametre geçirmeden de çalışırdı ama yanlış sebeple: Jinja tanımsız
değişkeni sessizce boş render ediyor. Sessizce çalışan bir şeye dayanmak,
sessizce bozulacak bir şeye dayanmak demek.

Seçtiğim yol: işaretçi Jinja söz dizimi kullanmıyor ve yerine koyma iskele
dosyayı okumadan önce bizim tarafımızda yapılıyor. Jinja işaretçiyi hiç
görmüyor.

### Künye sözleşmesi üç betiği birden kırdı

Sözleşmeyi ekleyince `record_run.py` ve `measure_models.py` künyeleri
reddedildi, çünkü ikisi de bazı alanları `os.environ` üzerinden okuyordu ve o
alanlar WSL tarafında boş. Sözleşme tam olarak bu arızayı yakalamak için vardı
ve ilk işi kendi kodumu yakalamak oldu.

Düzeltme sunucu introspection'ını `src/zihin/model_server.py` altına toplamak
ve iki betiğin de oradan okuması oldu.

## Kalanlar

Yükleme protokolü (K-21) hâlâ açık, ama artık ölçülmüş iki sayıya bakarak
kapatılabilir.

S-16 bağlanmadı. Yapılabilirliği Aşama 4'te gösterdim; bağlarken kayıt
noktasının `raise_if_failure` çağrısından önce olduğunu ayrı bir test
sabitleyecek.

## Yerel-yalnız kontroller

Son koşu: `2026-08-11T09:42:52+03:00`, commit `b68cabc`. On dört test geçti,
87 test elendi.

## Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Slot katmanı, sunucu introspection modülü, doğrulama betiği |
| Testi yazıldı | Evet, 87 test CI'da, 14'ü yerel |
| Loglandı | CHANGELOG girdisi yazıldı |
| Belgesi yazıldı | 08-decisions, 09-limitations, PROJECT_STATUS, REPRODUCE |
| Hata durumu düşünüldü | İşaretçi eksik ya da çift olduğunda, slot kuralı kapatılmaya çalışıldığında ve künye eksik olduğunda ayrı ayrı düşüyor |
| PR üzerinden gözden geçirildi | PR açıldı |
| Temiz kurulumda baştan çalıştırıldı | CI dört kontrolü geçiyor |

## #9 — Kurulum sonrası 1 — S-16 bağlandı, soğuk rejim ölçüldü

- Branch: `post-setup-s16-and-load-protocol`
- Merged: 2026-08-11

<!-- body, verbatim except for task text -->

# Kurulum sonrası 1 — S-16 bağlandı, yükleme protokolü kilitlendi

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

Kurulum altı aşamayla kapandı. Bu iş zincirin ilk halkası: K-50'nin birinci
maddesi ve K-21'in iki şartı.

## Zincirin kapısı: eylem düzeyi yanıt verisi

`src/zihin/api_capture.py` AppWorld'ün `Requester` sınıfının `_get`, `_post`,
`_patch`, `_delete` ve `_put` metotlarını sarmalıyor. Yakalanan her çağrı istek
bilgisini, durum kodunu ve yanıt gövdesini taşıyor.

Kaydedici artık eylemleri buradan yazıyor. `actions.result_status` ve
`actions.error_class` sütunları S-05'ten beri boştu, şimdi doluyor.

### Kayıt sırası testle sabitlendi

Asıl kural burada bir davranış değil, bir sıra. `Requester._get` ve kardeşleri
dönmeden önce `raise_if_failure` çağırıyor ve başarısız yanıtta istisna
fırlatıyor. Kayıt istisnadan sonra alınırsa başarısız çağrılar hiç
kaydedilmiyor.

Bu tam olarak bir kez oldu ve ölçüm yeşil göründü: ilk sondada yedi çağrının
yedisi de 200 raporlandı, oysa ikisi başarısızdı.

`tests/test_api_capture.py` sırayı sabitliyor. Sahte bir `Requester` kullanıyor,
yani AppWorld kurulumu istemiyor ve CI'da koşuyor. Sekiz test var; biri
doğrudan "başarısız çağrı istisna yayılmadan önce kaydediliyor mu" sorusunu
soruyor, biri de sarmalayıcının istisnayı yutmadığını denetliyor.

### İki kaynak birlikte tutuluyor ve ilk işi bir arıza yakalamak oldu

Yakalayıcının saydığı çağrı ile `api_calls.jsonl` deltasının saydığı çağrı adım
başına karşılaştırılıyor. Tek kaynağa geçmedim, çünkü yakalayıcının bir çağrıyı
kaçırması ya da fazladan sayması sessiz kalırdı.

İlk determinizm koşusunda karşılaştırma tuttu: yakalayıcı adım başına 2, günlük
1 çağrı gördü. Toplamda 38'e 19.

Sebep, yakalayıcının çerçevenin kendi iç çağrısını da sayması. Her adımda
AppWorld `/supervisor/active_task` çağırıyor; o çağrı ajanın eylemi değil ve
`api_calls.jsonl`'e girmiyor. Yani her adıma hayalet bir eylem ekleniyordu.
Üstelik hayalet eylem 200 dönüyordu, ajanın gerçek çağrısı ise 401. Hata
indeksi bu veriyle beslenseydi her adımda başarılı bir çağrı görecekti.

Düzeltmeyi bayrağa değil davranışa bağladım. Yakalayıcı artık AppWorld'ün kendi
istek sayacına bakıyor: sayaç büyüdüyse çağrı ajanın eylemi sayılıyor. `track`
bayrağına güvenmek de bir varsayım olurdu. Düzeltmeden sonra iki kaynak birebir
tutuyor.

Üç test eklendi: iç çağrı yakalanmıyor, izlenmeyen başarısız çağrı da
yakalanmıyor, ve yakalanan sayı çerçevenin saydığına eşit.

Düzeltmeden sonra 1.5B ölçümü yeniden koşuldu: on epizotta da yakalanan 19,
günlükteki 19, hiç ayrışma yok. Determinizm hükmü değişmedi, çünkü yörünge
özetleri `environment_io.md` üzerinden hesaplanıyor ve kayıt katmanından
etkilenmiyor.

## K-21'in ikinci şartı: boşaltma ölçülüyor

`unload_model` artık boşaltma isteğinden sonra `/api/ps` üzerinden kontrol
ediyor. Model hâlâ yüklü görünüyorsa hata fırlatıyor ve epizot başlamıyor.

Protokol iddia değil ölçüm. Boşaltma sessizce başarısız olsaydı epizot ısınmış
rejimde başlar, rejimler karışır ve fark edilmezdi.

## K-21'in birinci şartı: iki modelde tuttu, birinde tutmadı

Model başına on soğuk epizot, aynı görev (`82e2fac_1`), aynı seed
(2773802488). Her epizottan önce model boşaltıldı ve boşaldığı doğrulandı.
Aynı koşuda ikinci bir tohumla tek epizot daha koşuldu.

| Model | Tekdüze | Farklı yörünge | Boşaltma | İkinci tohum farklı |
|---|---|---|---|---|
| 1.5B | evet | 1 | 10/10 doğrulandı | evet |
| 3B | evet | 1 | 10/10 doğrulandı | evet |
| 7B | **hayır** | **2** | 10/10 doğrulandı | evet |

7B'nin on koşusundan dokuzu `6fb9c5fc4d8d62b2`, biri `a224f9753ae5c0e7` verdi.
Ayrışan koşu 12 adım yerine 6 adımda bitti. API çağrısı sayısı onunda da 5,
yani ayrışan koşu aynı eylemleri üretip erken sonlandı.

Boşaltma her üç modelde de her epizotta doğrulandı, yani ayrışmanın sebebi
rejim karışması değil.

**Bu K-48'in tetiklendiği durum.** Kural sonuç görülmeden yazılmıştı: on
epizotluk sınama düşerse determinizm hedefinden vazgeçilip yükleme durumu
kaydedilen ortak değişkene indirilir. Sınama 7B'de düştü.

Bir belirsizlik var ve karar vermiyorum: K-48 kuralın model başına mı yoksa
tümü için mi uygulanacağını söylemiyor. İki model tekdüze, biri değil. Kuralı
tümü için uygulamak, tekdüzeliği ölçülmüş iki modelde de determinizmden
vazgeçmek demek; model başına uygulamak ise ölçek ekseninin üç noktasının
farklı analiz varsayımları taşıması demek. İkisi de bedelli.

Ayrışma oranını yükseltmek için tekrar koşmadım. Şart "hepsi birebir aynı
çıkmalı" diyordu ve çıkmadı; tekrarlayıp daha iyi bir sonuç aramak, ölçümü
sonuca göre seçmek olurdu.

**Yan bulgu.** 3B on epizodun onunda da sıfır API çağrısı yaptı ve yirmi adım
tavanına dayandı. S-14 ölçek ekseninin en küçük noktası için açılmıştı; 3B de
aynı yerde. 7B beş çağrı yapıp on iki adımda bitirdi, yani üç nokta içinde
yalnız o taban etkisinin dışında.

## Karşılaştığım sürprizler

### Sunucu betiği ayaktaki sunucuyu düşmüş sanıyordu

Determinizm koşusu ilk denemede bağlantı zaman aşımıyla düştü. Sebep sunucunun
kapalı olmasıydı, ama onu yeniden başlatmaya çalışınca betik "sunucu ayağa
kalkmadı" dedi ve çıktı.

Oysa sunucu ayaktaydı. Betik başlattıktan sonra sekiz saniye bekleyip tek bir
sağlık yoklaması yapıyordu; bu makinede GPU keşfi 23 saniye sürüyor. Log'da
başlangıç 11:03:07, `inference compute` satırı 11:03:30.

Düzeltme sabit bekleme yerine yoklama koymak oldu, ve ikinci bir yoklama daha
eklendi: `inference compute` satırı log'a düşene kadar bekleniyor. Sebebi
ölçümle ilgili; GPU hazır olmadan alınan bir yükleme süresi ölçümü yanıltıcı
olurdu.

Bu, K-49'un altıncı örneği. Betik daha önce "başarılı" raporlamıştı ve o rapor
doğruydu ama yanlış sebeple: o seferki GPU keşfi sekiz saniyeden kısa sürmüştü.

### Prompt yolu eşzamanlılıkta çakışacaktı

Prompt dosyası epizot başına yeniden üretiliyor, çünkü slot içeriği epizoda
göre değişecek. Yol sabitti. Küçük modellerde eşzamanlı epizot koşacak ve iki
epizot birbirinin dosyasını ezecekti.

Ezilme sessiz olurdu: ikisi de geçerli bir prompt okuyup koşmaya devam ederdi
ve fark yalnız sonuçlarda görünürdü. `episode_prompt_path` yolu koşu kimliği,
görev kimliği ve tohum indisinden türetiyor.

## Karara bağlananlar

- **K-21.** Soğuk rejim, iki şartıyla.
- **K-47.** Gereken determinizmin türü: aynı görev, seed, koşul ve model
  dörtlüsünün tekrarında aynı sonuç; tohumlar arası fark kalıyor.
- **K-48.** Tekdüzelik tutmazsa determinizm hedefinden vazgeçilip yükleme
  durumu kaydedilen ortak değişkene indiriliyor. Kural sonuç görülmeden
  yazıldı.
- **K-49.** Bir şeyin çalıştığı görüldüğünde doğru sebeple mi çalıştığı ayrıca
  sorulacak. Altı örneğiyle birlikte kayıtta.
- **K-50.** Kurulum sonrası bağımlılık zinciri ve ön kaydın donma kuralı: kural
  donuyor, sayılar donmuyor.

## K-42 için ölçülmüş taban

Zincirin ikinci maddesi K-42'nin karara bağlanması. Karar sizin ama sayılar
çıkarıldı.

"Değerlendirme örneklemi yalnız biriktirmede temsil edilen uygulamalardan
çekilir" kuralı uygulandığında zorluk bölmesinden ayakta kalan görev:

| Havuz | Uygulama | test_normal | test_challenge |
|---|---|---|---|
| Yalnız train + dev | 5 | 141/168 | 37/417 |
| + test_normal'ın tamamı | 8 | 165/168 | 193/417 |
| Bütün kullanıcı uygulamaları | 9 | 165/168 | 405/417 |

Havuz genişletilmezse zorluk bölmesinin yüzde dokuzu kalıyor.

**Yapısal sorun.** Zorluk bölmesini en çok açan uygulama `amazon`, tek başına
185 görev getiriyor. Ama `amazon` train'de, dev'de ve test_normal'da hiç
geçmiyor. Havuza girmesinin tek yolu zorluk görevleri üzerinde biriktirme
yapmak, o da görülmemiş görev özelliğini bozar.

Biriktirmeyle erişilebilen tavan sekiz uygulama ve 193/417. `amazon`'a dokunan
212 zorluk görevi, kural korunursa değerlendirme örnekleminin dışında kalıyor.
Diğer üçünün katkısı: `gmail` +150, `todoist` +3, `splitwise` +0.

Sayılar vekil ölçümden geliyor, tam isabet yüzde 75,5. Yön güvenilir çünkü
vekil `amazon`, `splitwise` ve `todoist` için hiç fazladan sayma yapmadı.

## Sırada

K-42'nin karara bağlanması, sonra önyükleme biriktirmesi. Ayrıca K-48'in model
başına mı yoksa üç nokta için birden mi uygulanacağı.

## Yerel-yalnız kontroller

Son koşu: `2026-08-11T12:26:24+03:00`, commit `1b72bf7`. On dört test geçti,
99 test elendi.

## #10 — Kurulum sonrası 2 — Artık varyans ve adım taksonomisi

- Branch: `post-setup-2-noise-and-taxonomy`
- Merged: 2026-08-11

<!-- body, verbatim except for task text -->

# Kurulum sonrası 2 — Artık varyans ve adım taksonomisi

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

## Önce bir cevap: 7B temiz sayaçla mı koştu

Evet. Yakalayıcı düzeltmesi 3B ve 7B koşularından **önce** yapıldı; ilk 1.5B
koşusu düzeltmeden önceydi ve tek ayrışma gösteren o oldu.

Kanıt kayıtta duruyor. Kirli sayaç her adımda çerçevenin iç çağrısını fazladan
sayıyordu, yani eylem üreten her epizot ayrışma gösterirdi. Kayıtlarda 3B ve
7B'nin sayım ayrışması yok; ilk 1.5B koşusunda on koşunun onunda da var.

Yine de 7B ölçümü tekrarlandı, çünkü artık varyans ölçümü ikinci bir bağımsız
örneklem istiyor. Sonuçlar aşağıda.

## Artık varyans

Aynı görev (`82e2fac_1`), aynı seed (2773802488), aynı koşul, model başına on
soğuk epizot. Her epizottan önce model boşaltıldı ve boşaldığı doğrulandı.

| Model | Koşu | Farklı yörünge | Dağılım |
|---|---|---|---|
| 1.5B | 10 | 1 | `d2b4954cc6fc05e3` ×10 |
| 3B | 10 | 1 | `e85fb237a7fcf621` ×10 |
| 7B, birinci parti | 10 | 2 | `6fb9c5fc4d8d62b2` ×9, `a224f9753ae5c0e7` ×1 |
| 7B, ikinci parti | 10 | 1 | `6fb9c5fc4d8d62b2` ×10 |

**7B'nin ayrışma oranı 1/10 değil, yirmi epizotta bir.** İkinci parti tamamen
tekdüze çıktı. İki parti arasında modeli etkileyen hiçbir şey değişmedi; ilk
parti de düzeltilmiş sayaçla koşmuştu.

Bu, K-51'in istediği şeyin ta kendisi: ikili bir varsayım değil, ölçülmüş bir
büyüklük. 1.5B ve 3B'de artık varyans sıfır, yani gürültü tabanına katkıları da
sıfır. 7B'de yirmide bir ve ayrışan koşu 12 adım yerine 6 adımda bitiyor,
API çağrısı sayısı ikisinde de aynı.

Boşaltma kırk epizodun kırkında da doğrulandı, yani ayrışmanın sebebi rejim
karışması değil. Tohum ekseni de üç modelde de canlı: ikinci tohum her seferinde
farklı yörünge verdi.

**Ölçümün sınırı.** Tek görev ve iki parti. Yirmide bir oranı bir nokta
kestirimi; pilotun tekrar koşuları bunu daraltacak.

## Sıfır çağrılı epizotların sınıflandırması

S-19'u taban ilan etmeden önce adımları K-36'nın kategorilerine dağıttım.
Sonuç teşhisi değiştiriyor.

### 3B: 200 adımın 200'ü de aynı hata

On epizot, epizot başına yirmi adım, hepsi `execution_error_no_action`. Yani
kod üretildi, ayrıştırıldı, ama hiç eylem üretmeden yürütme düştü. Ve hepsinde
aynı satır:

```
NameError: name 'playlists' is not defined
```

**Mekanizma prompt'un içinde.** Referans yönergenin örnek çözümü `playlists = []`
tanımlayıp sayfa sayfa dolduruyor, sonra `for playlist in playlists:` ile
geziyor. Model örneğin ikinci kısmını kopyalıyor ama tanımı taşımıyor. Aynı
hata Aşama 2'de 1.5B'nin boş başarı epizodunda da çıkmıştı, yani desen modele
değil iskeleye ait.

**Teşhis "model zayıf" değil.** Yetenek tabanı olsaydı 3B'nin 1.5B'den kötü
olması beklenmezdi; oysa 1.5B aynı görevde on dokuz çağrı yapıyor.

### 7B: üç kategori bir arada

Yüz yirmi adımın dağılımı: 40 adım eylem üretti, 60 adım
`execution_ok_no_action`, 20 adım `no_code`.

Epizot başına dörde bölünürse: dört adım eylem üretiyor, altı adım yürütmeyi
başarıyla bitirip hiç eylem üretmiyor, iki adım hiç kod üretmiyor.

Altı adımlık `execution_ok_no_action` payı dikkat çekici. Bu K-36'nın beşinci
kategorisi, yani Aşama 2'de "sessiz boş başarı" diye tanımladığımız durum. 7B
epizot başına altı kez o durumu üretiyor.

### 1.5B: adımlar eylem üretiyor ama eylemlerin hepsi düşüyor

İki yüz adımın 190'ı eylem üretti, 10'u `execution_error_no_action`, yani epizot
başına yalnız ilk adım hata veriyor.

Ama eylemlerin kendisi başarısız. On dokuz çağrının on dokuzu da
`POST /spotify/auth/token` ve hepsi 401 dönüyor. Model yanlış parolayla giriş
denemesini yirmi adım boyunca tekrarlıyor.

Bu, K-20'nin öngördüğü davranışın ta kendisi: sabit sıcaklık ve sabit seed
altında ajan başarısız bir çağrıyı tekrarlıyor, çünkü dağılım değişmiyor.

### Üç model, üç farklı arıza biçimi

| Model | Eylem üreten adım | Baskın arıza | Çağrıların durumu |
|---|---|---|---|
| 1.5B | 190/200 | Yanlış parolayla giriş döngüsü | 19/19 çağrı 401 |
| 3B | 0/200 | `NameError`, tanımsız değişken | çağrı yok |
| 7B | 40/120 | Sessiz boş başarı (60/120) | 5/5 çağrı 200 |

Hiçbiri görevi çözmüyor ama sebepleri birbirinden tamamen farklı. Üçü de aynı
"taban etkisi" başlığı altında toplanamaz.

7B'nin baskın arızası K-36'nın beşinci kategorisi, yani dışarıdan temiz görünen
ve doğrulayıcıya kadar alarm üretmeyen tür. En yetenekli noktamızın en çok
ürettiği hata biçimi bu; K-40'ın tavanda sansür kuralı tam olarak bunun için
konmuştu.

### Bunun ikili sonucu

Bir yandan ölçülecek bant var, çünkü baştaki hata düzeltilebilir bir hata.

Öte yandan bir geçerlilik riski doğuyor: mekanizma bu hatayı düzeltirse
ölçtüğümüz etki "biriken deneyimin katkısı" değil "tek bir prompt kopyalama
hatasının kapanması" olabilir. Etki büyük çıkarsa ikisini ayrıştırmak gerekecek.
S-19'a yazıldı.

**Yapılmayacak olan.** Prompt düzeltilmiyor. Referans iskele değiştirilmeden
alınıyor (K-23, K-26) ve bu hata iskelenin kendi davranışı. Düzeltmek
mekanizmanın işi.

## Karara bağlananlar

- **K-51.** Determinizm bir analiz varsayımı olarak alınmıyor. Artık varyans
  model başına ölçülüp gürültü tabanına ekleniyor. K-48'in ikili seçimi
  yerine geçti.
- **K-42, nihai hâli.** Zorluk bölmesi bütün ve dokunulmamış kalıyor.
  Biriktirme train, dev ve kullanılmayan normal test görevlerinden.
  Değerlendirme normal testten, örneklem biriktirmede temsil edilen
  uygulamalarla sınırlı. Uygulamalar arası aktarım erişilebilir 37 görevle
  koşacak ve küçük n'iyle raporlanacak.

## Sırada

Önyükleme biriktirmesi (K-50'nin üçüncü maddesi). Havuz tanımı artık kapalı, yani
neyin biriktirileceği belli.

## Yerel-yalnız kontroller

Son koşu: `2026-08-11T13:05:57+03:00`, commit `935a603`. On dört test geçti,
99 test elendi.

## #11 — Önyükleme öncesi üç koruma: durma kuralı, yazma kümesi kaydı, K-52

- Branch: `post-setup-3-bootstrap-guards`
- Merged: 2026-08-11

<!-- body, verbatim except for task text -->

Önyükleme biriktirmesinden önce istenen üç şey, artı artık varyans ölçümünün
birkaç göreve yayılması.

## Durma kuralı

Son `no_progress_limit` adımın hepsi ilerlemesizse epizot `no_progress`
sebebiyle bitiyor. Bir adım, durum farkı boşsa ve ya hiç eylem üretmemişse ya
da çağrılarının hiçbiri başarılı olmamışsa ilerlemesiz sayılıyor.

Eşik `config/recording.yaml` içinde 4 ve künyeye yazılıyor. Değer geçici,
yorumda da öyle yazıyor.

Canlı doğrulama: 1,5B'nin 401 döngüsüne giren epizodu yirmi adım yerine dörtte
kapandı. Dört adımın dördünde de durum farkı boş, üç eylemin üçü de 401. 7B
aynı görevde yedide kapandı; ilk üç adım çağrı üretti, pencere 4-7 arasında
doldu. Kural üretken adımları kesmiyor.

## Yazma kümesi kaydı

Adım öncesi ve sonrası canlı veritabanı sayımı. İki yanlış çapa denendi:
`model_hashes.json` değişiklik olmayan koşuda boş sözlük dönüyor,
`search_notes` beş kayıtta sayfalanıyor. Çalışan imza modellerin `count()`
değeri.

Sayım ekleme ve silmeyi görüyor, güncellemeyi görmüyor. İkinci katman epizot
düzeyindeki `model_hashes.json`. Sınır kodda ve şemada yazılı.

`steps.state_change` üç hâl taşıyor: `NULL` ölçülmedi, boş sözlük ölçüldü ve
değişmedi, dolu sözlük değişti. Okunamayan model `-1`, çünkü sıfır ile
"değişmedi" karışırdı.

## Artık varyans beş göreve yayıldı

Model başına beş görev, görev başına altı soğuk epizot, artı ikinci tohum.

| Model | Epizot | Farklı yörünge |
|---|---|---|
| 1.5B | 30 | görev içinde 1, beş görevin beşinde de |
| 7B | 30 | görev içinde 1, beş görevin beşinde de |

Önceki turdaki 1/20 ayrışma tekrarlamadı. Tavana dayanan yirmi adımlık
epizotlarda bile sapma yok. Ölçüm durma kuralı açıkken yapıldı, yani ilk
ölçümle doğrudan karşılaştırılamaz; sonuç "deneyin koşacağı rejimde artık
varyans sıfır".

## Taramanın yan ürünü

1.5B'nin 144 adımının 90'ı kategori 4 (%62,5), beş görevin üçünde epizottaki
her adım. 7B'de aynı oran %15,8. İki model de hiçbir görevi bitirmedi, yani
başarı oranı ikisinde de sıfır — K-54'ün neden ayrı bir metrik istediği burada
görünüyor.

Uyarı raporda: dört adımlık eşik, ilk dört adımı kategori 4 olan epizodu hemen
kesiyor, dolayısıyla oran eşiğe koşullu. Eşiği kesinleştirecek tarama bunu
ölçmeli.

## Dikkatinize sunulan iki nokta

**K-53'ün ifadesi genişletildi.** Ölçüt "tavana dayanan epizot oranı" diye
yazılmıştı. Durma kuralı eklenince tavana dayanan epizot neredeyse kalmadı;
yalnız tavan sayılsaydı hiçbir şey çözmeyen bir model sıfır sansür gösterirdi.
Sansür artık `step_ceiling` ve `no_progress` sonlanmalarını birlikte sayıyor.
Kastınız buysa değişiklik yok, değilse söyleyin.

**Aşama 3'ün ölçütü ile çakışma.** Durma kuralı açılınca "en az bir adım birden
çok eylem üretmeli" ölçütü 1,5B kayıtlarında sağlanamaz oldu. Ölçütü
gevşetmedim; aynı görevi 7B ile kaydettim, orada ikinci adım iki eylem üretiyor.

## Kararlar ve sınırlar

K-52 önyükleme biriktirmesi deney dışı. K-53 sansür oranı ölçütü. K-54 kategori
4 oranı koşul başına. K-55 güç hesabı çıkarılan nicelik üzerinden. K-56
`irrelevant_retrieval` zorunlu.

S-20 küçük modellerin baskın hatası (1.5B verisiyle genişletildi). S-21 artık
varyans kapsamı.

## Kontroller

11 Ağustos 2026: lint temiz, biçim temiz, 128 test geçti, import ve build
tamam. Kayıt uçtan uca koşuldu.

Rapor: `docs/reports/kurulum-sonrasi-3.md`

## #12 — Sansür doğrulayıcının hükmünden tanımlanıyor, hüküm artık kayıtta

- Branch: `post-setup-4-sansur-hukmu`
- Merged: 2026-08-11

<!-- body, verbatim except for task text -->

Dört karar işlendi. Sansür tanımı bir eksik ortaya çıkardı, o eksik de bu
turda kapandı.

## Yazma kümesi birleşim (K-41)

Canlı sayımın güncellemeyi görmemesi kodun yorumunda yazılıydı, sonucu değildi.
Sonuç şu: ampirik ölçüm statik taramanın üçüncü grubunu yapısal olarak
bulamaz.

| Kaynak | Gördüğü | Göremediği |
|---|---|---|
| Ampirik sayım | ekleme, silme, devretme | güncelleme |
| Statik tarama | işleyici gövdesindeki doğrudan çağrı | yardımcıya devredilen çağrı |

`phone.show_contact_relationships` ve `todoist.show_projects` türetilmiş bir
alanı güncelliyor, satır açmıyor; sayım bunları hiç işaretlemez, ölçüm ne kadar
uzun koşarsa koşsun. Ters yönde GET dışı 302 ucun 91'i işi yardımcıya
devrediyor ve statik tarama orayı görmüyor.

Yazma kümesi `statik ∪ ampirik` olarak donduruluyor. Gerekçe karar kaydında,
"ampirik ölçüm var, statik tarama gereksiz" diye elenmesin diye.

## Sansür tanımı hükümden (K-53)

Doğrulayıcının geçirmediği her epizot sansürlü. `termination_reason` ayrı bir
tanı alanı olarak kaldı, tanıma girmiyor.

Sebeple tanımlamanın iki sakıncası vardı. Sebep listesi ajanın bitirdiğini
bildirip doğrulayıcıdan kaldığı hâli kaçırıyor — K-36'nın beşinci kategorisi,
7B'nin en çok ürettiği arıza. Ve her yeni sonlanma yolunda tanımın
güncellenmesi gerekirdi; unutulduğunda sansür sessizce küçülürdü.

`passed` üç hâl taşıyor. `NULL` "geçmedi" değil "hüküm okunamadı" demek;
analize giren epizotta çıkarsa ölçüm arızası, sansüre yazılmıyor.

K-40 ile bağı da yazıldı: K-53 hangi epizodun sansürlü olduğunu, K-40 o
epizodun analize hangi değerle gireceğini söylüyor.

## Tanımın açtığı eksik

Sansürü hükümden hesaplayacaksak hükmün kayıtta olması gerekiyor. Kayıtta
değildi.

`verifier_results` satırı Aşama 3'ten beri açılıyordu ama `passed` her satırda
`NULL`'du. Kaydedici değerlendirmeyi hiç koşturmuyordu; yalnız rapor dosyasının
yolunu yazıyordu. Önceki raporlardaki "hiçbir model görevi bitirmedi" bu yüzden
bir çıkarımdı, ölçüm değil — dayanağı hiçbir epizodun `agent_finished` ile
bitmemesiydi.

`src/zihin/verification.py` eklendi. Sonraya bırakılamıyor: değerlendirme görev
çıktı dizinindeki son veritabanı durumunu okuyor ve o dizin aynı görev başka
bir modelle koşulduğunda üzerine yazılıyor. Yazma kümesi için istenen "ilk
epizottan itibaren açık olsun" kuralının aynısı.

## Ölçüm: sansür oranı

Beş görev, model başına görev başına bir soğuk epizot, taban koşulu, kural
açık.

| Model | Epizot | Geçen | Sansür | %95 alt sınır | Kategori 4 |
|---|---|---|---|---|---|
| 1.5B | 5 | 0 | %100 | %54,9 | %62,5 |
| 3B | 5 | 0 | %100 | %54,9 | %90,0 |
| 7B | 5 | 0 | %100 | %54,9 | %15,8 |

Ölçüt %10'un altını istiyor, alt sınır %54,9. Üç modelde de reddediliyor.

1.5B ve 3B bekleniyordu. **7B beklenmiyordu ve asıl bulgu bu:** bu beş görevde
ölçek ekseninin hiçbir noktasında birincil metrik tanımlı değil.

İki ayrıntı. Geçen testler ilerleme kanıtı değil — hepsi "assert no model
changes" türünden, ajan hiçbir şey yapmadığı için geçiyor; `6104387_1`'de ajan
bir şeye dokunduğu an 0/10'a düşüyor. Ve on beş sansürlü epizodun on üçü
`no_progress`, ikisi `step_ceiling`; bu ölçümde iki tanım da aynı sonucu
verirdi, ayrım 7B'nin sessiz boş başarısında açılıyor.

Örneklem sınırı S-22'de: beş görev rastgele seçilmedi, artık varyans
taramasından geldiler, ve model başına tek epizot var.

## Artık varyans üst sınırı (S-21)

| Ölçüm | Rejim | Ayrışma | Üst sınır |
|---|---|---|---|
| 1.5B, beş görev | kural açık | 0/30 | %9,5 |
| 7B, beş görev | kural açık | 0/30 | %9,5 |
| İkisi havuzlanmış | kural açık | 0/60 | %4,9 |
| 7B, tek görev | kural kapalı | 1/20 | %21,6 |

Clopper-Pearson tek yanlı %95. Gürültü tabanına giren sayı model başına %9,5.
%2 için sıfır ayrışmayla 149 epizot gerekiyor; elimizde model başına otuz var.

## Yan bulgu: sunucu yeniden başlatması yörüngeyi değiştirmedi

Ollama süreci bu oturumda ölmüştü, `serve_models.ps1` ile yeniden başlattım.
Sansür ölçümü yeni süreçte ve kayıt betiğiyle koşuldu; tarama eski süreçte ve
başka betikle koşmuştu. On yapılandırmanın onunda da adım ve çağrı sayıları
birebir aynı çıktı, 7B'nin tavana dayanan iki epizodu (20 adım, 19 ve 20 çağrı)
dahil.

Eşleşme adım ve çağrı düzeyinde, yörünge özeti düzeyinde değil — kayıt betiği o
özeti hesaplamıyor. S-21'e not olarak geçti.

## Kategori 4'ün iki rejimi (K-54)

Ana deneyde oran kural açıkken ölçülüyor; koşullama bütün koşullarda aynı
olduğundan koşullar arası karşılaştırma geçerli kalıyor. Kural kapalı ölçüm
yalnız eşik seçimine hizmet ediyor. Makalede hangi oranın hangi rejimden
geldiği yazılıyor.

## Kontroller

11 Ağustos 2026: ruff temiz, 133 test geçti, atlanan yok, import ve build
tamam. On beş epizot uçtan uca koşuldu ve on beşinin de hükmü şemaya yazıldı.
Ölçümden önce sunucu betikten yeniden başlatıldı, ayarlar log'dan doğrulandı.

Rapor: `docs/reports/kurulum-sonrasi-4.md`

## #13 — Bant taraması: geçen görev sıfır, önyükleme durduruldu

- Branch: `band-taramasi`
- Merged: 2026-08-11

<!-- body, verbatim except for task text -->

Önyükleme biriktirmesi durduruldu, yerine ölçülebilir bant taraması koşuldu.

## Neden durduruldu (K-57)

Sebep analiz değil, mekanizmanın kendisi. Beceriler yalnız başarılı
epizotlardan madenciliyor. Sansür ölçümünde üç modelin üçü de hiçbir görevi
geçmedi, yani madencilenecek korpus yok. Boş korpusla kurulan bir derleyicinin
çalıştığı da gösterilemez: boş girdide her derleyici boş çıktı verir.

## Önce tasarım gözetimi (S-23)

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
<https://arxiv.org/html/2604.11465v2>. Bizim model 7B ve dört bit
kuantalanmış; en yakın iki nokta %0,0 ve %3,0.

## Tarama tasarımı

`test_normal`, çünkü bant sorusu değerlendirme örneklemi hakkında (K-42) ve o
bölmenin referans uzunlukları train'inkinden kısa. Otuz görev, bant başına
altı, seçim bant içinde ada göre sıralanıp eşit aralıkla — tekrar üretilebilir.

**Tavan görev başına: `2 × num_api_calls`, en az 20, en çok 150.** Sabit tavan
bandı ölçmez. Sansür ölçümü tam bu hatayı taşıyordu ve S-22'ye yazıldı: orada
beş görevin çapaları 10 ile 195 arasındayken tavan hepsinde 20'ydi.

## Dört sayı

| Bant | n | Geçen | Anlamlı test | Oran | Tavana dayanan | Sınıra dayanan |
|---|---|---|---|---|---|---|
| 1-10 | 6 | 0 | 0/25 | %0,0 | 1 | 0 |
| 11-20 | 6 | 0 | 4/36 | %11,1 | 2 | 0 |
| 21-40 | 6 | 0 | 0/31 | %0,0 | 3 | 0 |
| 41-89 | 6 | 0 | 1/30 | %3,3 | 1 | 2 |
| 90+ | 6 | 0 | 1/30 | %3,3 | 2 | 6 |

**1. Bant başına başarı: beş bantta da sıfır.** %95 üst sınır %9,5. Tarama
"sıfır" ile "%3" arasını ayıramaz — gerçek oran %3 olsaydı otuz görevde sıfır
görme olasılığı %40. Yayımlanmış tabanlarla tutarlı.

**2. En kısa bantta 17 görev** (bütün `test_normal`; 168 görev, medyan çapa 30).
Bant büyüklükleri: 1-10 → 17, 11-20 → 37, 21-40 → 74, 41-89 → 32, 90+ → 8.

**3. Kısmi tamamlama resmî olarak dereceli değil, dereceli skor kurulabiliyor.**
`task_goal_completion` ve `scenario_goal_completion` ikili. Ama `TestTracker`
her gereksinimi etiketliyor: `no_op_fail` hiçbir şey yapmayan ajanın düşürdüğü
test, `no_op_pass` hiçbir şey yapmasa da geçen test. Dereceli skor `no_op_fail`
testlerinin geçilen oranı: **6/152 = %3,9**. Ayrım boş değil — bu otuz epizotta
37 `no_op_pass` testi geçildi ve hiçbiri ilerleme kanıtı değil.

**4. Geçen epizotta harcanan çağrı yok, çünkü geçen epizot yok.** K-43'ün
çarpanı geçen epizotların çağrı sayısından seçilecekti; o veri üretilemedi.

## Üç yola söylediği

**Birinci yol zayıfladı.** En kısa bant hem ikili başarıda hem dereceli skorda
sıfır, ve bu tavandan değil: orada çapa 6-9 iken tavan 20, yani `k` 2,2-3,3 ve
altı epizodun yalnız biri tavana dayandı. Dereceli skorun sıfırdan farklı
olduğu üç görevin çapaları 16, 87 ve 94 — hiçbiri kısa bantta değil.

**İkinci yol sinyal taşıyan tek değişken.** İkili başarı otuz epizotta sabit
sıfır, varyansı yok, üzerine test kurulamaz. Dereceli skor görevler arasında
0/6 ile 4/6 arasında değişiyor.

**Üçüncü yol** taramanın kapsamı dışında.

## Beşinci kategori canlı

Otuz epizodun beşi `agent_finished` ile bitti ve doğrulayıcıdan kaldı. K-53
sansürü sonlanma sebebine bağlasaydı bu beşi sansürsüz sayardı. Kalanı 16
`no_progress`, 9 `step_ceiling`.

## Sınırlar

Bant başına altı görev; 11-20'deki %11,1'in tamamı tek görevden geliyor. Uzun
bantlar 150 adımlık tavan sınırına dayandı (90+ bandında altıda altı), o iki
bandın sıfırı tavandan da gelebilir. Kısa bantlarda bu kuşku yok. Model tek:
7B.

## Kontroller

11 Ağustos 2026: ruff temiz, 133 test geçti, atlanan yok, import ve build
tamam. Otuz epizodun otuzu hükmüyle şemada; ham çıktı
`results/bant-taramasi.json`.

Rapor: `docs/reports/bant-taramasi.md`

## #14 — Teşhis: duvar auth'ta değil, kategori 4 baskın değil, güçlü modelin alt kümesi bant açmıyor

- Branch: `teshis`
- Merged: 2026-08-11

<!-- body, verbatim except for task text -->

Üç teşhis koşuldu. İkisi yeni koşu istemedi.

## Teşhis 1: duvar kimlik doğrulamada değil, ama orada gerçek bir kayıp var

Otuz epizotta 1717 çağrı: 1445 × 200, 263 × 401, 5 × 422, 4 × 409. Supervisor
dışı uygulamalardan 1106 çağrı 200 döndü ve otuz epizodun 23'ü en az bir tane
aldı. 1,5B'deki "on dokuz çağrının on dokuzu 401" tablosu 7B'de yok.

401'ler uygulamaya göre keskin ayrılıyor: `spotify` 758'de 757 başarılı,
`venmo` 159'da 108 başarısız, `simple_note` 245'te 118, `file_system` 58'de 29.

**Venmo'nun 401'i model hatası, ortam hatası değil.** Kayıttaki kod:

```text
spotify_password = [p["password"] for p in passwords if p["account_name"] == "spotify"][0]
venmo_access_token = apis.venmo.login(username='st-maldonado@gmail.com', password=spotify_password)
```

Ajan spotify parolasını alıp venmo'ya giriyor ve aynı bloğu 88 kez
tekrarlıyor. 89 e-posta biçimli 401'in 88'i tek bir epizottan. Doğru satırı
seçtiği dört çağrının dördü de 200 döndü.

**simple_note ile file_system'de arıza farklı.** `simple_note.auth/token` 119
denemenin 118'inde 200 dönüyor, yani jeton alınıyor; ama `simple_note.notes`
117 kez 401 dönüyor. Sebep kayıtta görünüyor: `login()` sözlük döndürüyor —
`{"access_token": "...", "token_type": "Bearer"}` — ve model sözlüğün tamamını
`access_token` parametresine geçiriyor.

`supervisor.account_passwords` 334 çağrının 334'ünde 200. Parola arama adımı
çalışıyor; arıza sonrasında.

## Teşhis 2: kategori 4 baskın değil

958 adım: %81,9 eylem üretti, %16,9 kategori 4, %1,1 sessiz boş başarı, kod
üretilmeyen adım yok.

Önceden yazılan koşul "kategori 4 baskın çıkarsa iskele uyarlaması meşru"
idi. Sağlanmadı, kapı açılmadı.

Dağılım iki tepeli: altı epizot hiç çağrı üretmeden dörtte kapandı, `09b0ee6_2`
ise 150 adımda 736 çağrı yaptı ve hepsi 200 döndü.

## Teşhis 3: güçlü modelin çözdüğü alt küme bant açmıyor

Yayımlanmış koşular indirildi; toplamlar yayımlanmış sayılarla birebir tuttu
(gpt-4o %48,8, gpt-4-turbo %26,8, LLaMA-3-70B %20,8, DeepSeek-33B %7,1).

**Yan bulgu: referans uzunluk gpt-4o için de zorluk sinyali değil.** Bant başına
çözme oranı %59, %51, %42, %59, %38 — neredeyse düz.

| Alt küme | Görev | 7B geçen | Anlamlı test |
|---|---|---|---|
| gpt-4o çözdü | 30 | 0 | 6/126 = %4,8 |
| gpt-4o çözemedi | 15 | 0 | 5/93 = %5,4 |

Fark yok, nokta kestirim ufak bir farkla ters yönde.

## Uygulama kümesine göre tabakalama

Görev başına uygulama listesi test bölmelerinde yok (S-03) ama yayımlanmış
koşunun `api_calls.jsonl` dosyalarından çıkarılıyor. `test_normal`'ın 168
görevinin 99'u tek uygulamalı: 37 venmo, 30 spotify, 16 simple_note, 7 phone,
6 file_system, 3 todoist.

| Alt küme | Görev | 7B geçen | Anlamlı test |
|---|---|---|---|
| Yalnız `spotify`/`todoist` | 11 | 0 | 7/51 = %13,7 |
| Diğerleri | 34 | 0 | 4/168 = %2,4 |

Dereceli skorda beş buçuk kat fark; uzunluk tabakalamasının veremediği sinyal
bu. İkili başarı yine sıfır.

**Karıştırıcı büyük.** `spotify` tam olarak referans yönergenin örnek
çözümünde gösterilen uygulama. "Auth'un çalıştığı uygulama" ile "yönergenin
gösterdiği uygulama" aynı. Örneklemi spotify'a daraltmak, tabanı yönergenin
zaten çözdüğü göreve daraltmak demek — S-19'un riskini azaltmıyor, büyütüyor.

## 736 çağrılık epizot

150 adım, 736 çağrı, 736'sının 736'sı 200, ve 150 adımın 150'sinde de
`state_change` boş. Veritabanı bir kez bile değişmedi. Çağrılar:
`spotify.library/playlists` 441, `supervisor.account_passwords` 148,
`spotify.auth/token` 147 — her adımda baştan giriş yapıp kütüphaneyi yeniden
sayfalıyor. Epizot `NameError: name 'playlists' is not defined` ile açılıyor,
yani S-20.

**Durma kuralında kör nokta.** Kural hiç ateşlemedi çünkü `_ilerlemesiz_mi` bir
adımı, çağrılarından biri başarılıysa ilerlemiş sayıyor. Kör nokta "amaçsız
durum değişimi" değil, amaçsız **başarılı okuma**. Ayrım düzeltmeyi
değiştiriyor: "durum değişmeli" diye sıkılaştırmak salt okuma evrelerini ve
doğrulayıcısı "assert no model changes" olan cevap görevlerini yanlış keserdi.
S-25.

## Yönergenin kendi kusuru

Teşhis 1'in izini sürerken bulundu.
`prompts/react_code_agent/instructions.reference.txt`, 153. satır:

```text
spotify_password = [account_password["account_name"] == "spotify" for account_password in passwords][0]["password"]
```

Liste kavraması boole üretiyor, `[0]` bir boole veriyor, `["password"]`
`TypeError: 'bool' object is not subscriptable` fırlatıyor. Yönerge bu satırın
ardından başarılı bir giriş çıktısı gösteriyor. İkinci eksik:
`login_result["access_token"]` çıkarımı hiç gösterilmiyor.

45 epizotta bozuk kalıp 34 kez kopyalandı (13 epizotta), 11 `TypeError` üretti.
Aynı epizotlarda doğru filtre yazımı 488 kez geçiyor — kusur gerçek ama tek
başına baskın sebep değil. Yönerge değiştirilmedi (K-19, K-23).

## Karara bağlananlar

- **K-58 ön koşul kapısı.** Taban koşulu ayrılmış kümede ilan edilen asgari
  başarı oranını tutturamazsa hipotez test edilmemiştir ve mekanizma sonuçları
  raporlanmaz. Üç parçası yazılı: ayrılmış küme, ilan edilmiş oran, geçilmezse
  ne yayımlanacağı. Kural sonuç görülmeden donduruldu.
- **K-59 üç sonucun yorumu.** İkisi de kazanırsa değer yapısal şablonda demek
  ve ana iddia desteklenmemiş sayılıyor; yalnız ilgili kartlar kazanırsa içerik
  önemli; ikisi de kazanmazsa mekanizma bu bantta işe yaramıyor. Yorum önceden
  sabitlendi.

## Sınırlar

S-24 dış inceleme ön koşul sorusunu sormadı. S-25 durma kuralının kör noktası.
S-20 sertleştirildi.

## Kontroller

11 Ağustos 2026: ruff temiz, 133 test geçti, atlanan yok, import ve build
tamam. Teşhis 3 için 15 yeni epizot hükmüyle şemaya yazıldı. İndirilen taban
koşuları `.gitignore` altında.

Rapor: `docs/reports/teshis.md`

## #15 — Sınır kontrolü: düzenek çalışıyor, 20/30

- Branch: `sinir-kontrolu`
- Merged: 2026-08-12

<!-- body, verbatim except for task text -->

Sınır kontrolü koşuldu. Bir bant araması değil, düzenek doğrulaması.

## Sonuç: düzenek çalışıyor

`openrouter/deepseek/deepseek-v4-flash-0731`, bant taramasının aynı otuz
görevinde, `max_tokens=4000`:

| Ölçüt | Değer |
|---|---|
| Geçen görev | 20/30 = %66,7 |
| %95 alt sınır | %50,1 |
| Anlamlı test (no-op düzeltilmiş) | 95/152 = %62,5 |
| Kodsuz adım | 62/902 = %6,9 |
| Maliyet | 0,62 dolar |

### Aynı otuz görevde üç nokta

| Model | Hat | Geçen |
|---|---|---|
| DeepSeek V4 Flash 0731 | bizim hattımız | 20/30 = %66,7 |
| gpt-4o-2024-05-13 | yayımlanmış koşu, durma kuralı yok | 15/30 = %50,0 |
| qwen2.5-coder 7B q4_K_M | bizim hattımız | 0/30 = %0 |

gpt-4o satırı bizim koşumuz değil; indirilen yayımlanmış çıktıdan aynı otuz
göreve süzüldü. **Bizim hattımız güçlü bir modele, yayımlanmış bir koşunun aynı
görevlerdeki oranından daha yüksek oran veriyor.** Düzenek yalnız "bozuk değil",
tam olarak çalışıyor. Bant taramasındaki sıfırlar model kapasitesinden.

## Ne sabit tutuldu

Aynı otuz görev, görev başına aynı tavan (`2 × çapa`, 20-150), aynı durma
kuralı, aynı yakalayıcı, aynı durum sondası, aynı doğrulayıcı, aynı yönerge
dosyası, aynı sıcaklık. Değişen: model, onu sunan katman, ve çıktı bütçesi —
sonuncusunun sebebi aşağıda.

Koşu künyeye yazmıyor. Künye sözleşmesi `num_ctx_effective`, `kv_cache_type`,
`keep_alive` ve `context_verified` alanlarını zorunlu tutuyor; hepsi yerel
Ollama kavramı ve barındırılan bir modelde etkin bağlam penceresi
doğrulanamıyor. Koşu deneyin parçası olmadığı için kendi JSON çıktısına
yazıyor — K-52'nin kurduğu ayrımın aynısı.

## Çıktı bütçesi: yakaladım, yanlış doğruladım, sonra ölçtüm

Model akıl yürütme üretiyor ve `reasoning_content` ile `content` aynı bütçeden
yiyor. Bunu koşmadan önce fark ettim, tek görevle "ölçtüm" (16 adımın 14'ü
eylem üretti) ve "bütçe yetiyor" diye yazdım. **Yetersiz kontroldü**: sorun ilk
adımlarda değil, bağlam uzadıkça çıkıyor.

Erken kesilen üç epizot, yalnız `max_tokens` değiştirilerek tekrar koşuldu:

| Görev | 400 jeton | 2000 jeton |
|---|---|---|
| `1150ed6_1` | 6 adım, 1 eylem, 5 kodsuz, kesildi, kaldı | 12 adım, 14 eylem, 0 kodsuz, **geçti** 6/6 |
| `09b0ee6_3` | 6 adım, 2 eylem, 4 kodsuz, kesildi, kaldı | 8 adım, 14 eylem, 0 kodsuz, **geçti** 1/1 |
| `652485c_2` | 5 adım, 1 eylem, 4 kodsuz, kesildi, kaldı | 55 adım, 124 eylem, 18 kodsuz, kesildi, kaldı |

Tam koşu 4000 jetonla tekrarlandı:

| | 400 jeton | 4000 jeton |
|---|---|---|
| Geçen görev | 6/30 | 20/30 |
| Kodsuz adım | 125/501 = %25,0 | 62/902 = %6,9 |
| `no_progress` ile kapanan | 21 | 4 |

**Yerel ölçümler etkilenmiyor.** qwen2.5-coder akıl yürütme üretmiyor ve bant
taramasının 958 adımında kodsuz adım sayısı sıfır; 400 orada hiç bağlayıcı
olmadı. 7B'nin 0/30'u ayakta.

Kodsuz adım oranı 4000'de de sıfır değil (%6,9), yani bütçe uzun bağlamlarda
kısmen bağlayıcı kalıyor ve **%66,7 bir alt sınır.**

## İki değerlendirmemin düzeltmesi

**"Durma kuralı yetenekli modeli de kesiyor" geri alındı.** 400 jetonda 21
epizot `no_progress` ile kapanmıştı; 4000'de dört. O dördün yalnız biri
gpt-4o'nun çözdüğü görev. Kesilmelerin büyük kısmı kuralın katılığı değil,
bizim bütçemizdi. Kural zaten doğru sebeple ateşliyordu: `b9c5c9a_3`
epizodunda son dört etkileşimin dördü de boş kod bloğuydu; kural boşluğu doğru
okuyordu, boşluğun sebebi başkaydı.

**"Kısa görevler daha kolay değil" sonucu bilgi taşımıyordu.** 7B her bantta
tabandaydı ve sıfırlar arasında fark görünmez. DeepSeek'in bant profili:

| Bant | n | Geçen | Anlamlı test |
|---|---|---|---|
| 1-10 | 6 | 4/6 | 22/25 |
| 11-20 | 6 | 6/6 | 36/36 |
| 21-40 | 6 | 2/6 | 8/31 |
| 41-89 | 6 | 4/6 | 13/30 |
| 90+ | 6 | 4/6 | 16/30 |

Referans uzunluk burada da zorluğu tahmin etmiyor — en kötü bant 21-40. Bu,
gpt-4o'nun yayımlanmış koşusundaki düz profille aynı yöne işaret ediyor.

## Yazılanlar

- **S-26** aynı çıktı bütçesi model ailesine göre aynı koşul demek değil.
  Eşitlenecek olan sayı değil, bütçenin bağlayıcı olmaması; denetim göstergesi
  kodsuz adım oranı.
- **K-58'e ek:** ön koşul kapısı bağlayıcı bütçe altında ölçülemez, kapı
  koşusunda kodsuz adım oranı raporlanıyor.

## Karar ağacına söylediği

Düzenek sağlam, yani eşiğin nerede olduğunu arama yolu açık. 7B'nin sıfırı
model kapasitesi; bant taramasının ve teşhislerin sonuçları ayakta. A-06'nın
sorduğu şey için ölçülmüş bir nokta var: eksen yerel donanımın dışına
taşındığında sonuç alınıyor.

## Kontroller

12 Ağustos 2026: ruff temiz, 133 test geçti, atlanan yok, import ve build
tamam. Ollama koşu sırasında düşmüştü; `serve_models.ps1` ile yeniden başlatılıp
testler tekrar koşuldu.

Rapor: `docs/reports/sinir-kontrolu.md`

## #16 — Hizalama Adım 0: tasarım katmanı yazıldı, kurulum protokolü donduruldu

- Branch: `tasarim-katmani`
- Merged: 2026-08-12

<!-- body, verbatim except for task text -->

Hizalama Adım 0. Yalnız belge; kod ve şema değişikliği ayrı PR'da.

## Neden

Denetim tek bir merkezî bulgu verdi: **uyulacak yazılı zemin büyük ölçüde
yoktu.** Yedi tasarım belgesi, ön kayıt, deney matrisi ve yanlışlama kayıtları
üçer satırlık yer tutucuydu; on beş PR bunların üstüne birleştirildi.

Tasarım konuşmada duruyordu. Depoda yalnız karar kaydı vardı ve karar kaydı
"neden şunu seçtik" tutuyor, "tasarım nedir" tutmuyor. Altmış bir karar var ama
altı koşulun tanımı hiçbir yerde yazılı değildi.

## Yedi tasarım belgesi

| Dosya | İçerik |
|---|---|
| `01-problem-definition.md` | Problem, bilinen çözümün bedeli, sınanan alternatif, kapsam dışı |
| `02-research-question.md` | İki soru; birincisi tek hücrede onaylayıcı, ikincisi keşifsel ve birinciye bağlı |
| `03-architecture.md` | İki güven bölgesi, yedi bileşen, kayıt/projeksiyon ayrımı ve silme testi, bağlam montajcısı |
| `04-threat-model.md` | Üç somut tehdit, sandbox, kalkanın denetim zamanlaması, cezalandırmanın reddi |
| `05-experiment-design.md` | Dört hata sınıfı, altı koşul, iki kritik kontrast, model ekseni, metrikler, analiz planı, kapılar |
| `06-skill-language.md` | Madencilik, üç argüman sınıfı ve sıra kuralı, birleştirme, atomik yürütme, üç kapılı suç atfı |
| `07-failure-taxonomy.md` | Üç düzey, tekrar ekseni, bağlam koşulu zorunluluğu, kapalı koşul dili, karşıtsal indirgeme |

Hiçbir yeri türetilmedi; hepsi tam bağlam belgesinden. Belgelerin sessiz kaldığı
yerler ("henüz yazılmamış olanlar") açıkça işaretli.

## Ön koşul kapısı

`05-experiment-design.md` içinde, **ateşleme tarihiyle: 11 Ağustos 2026.** Üç
boyut otuz görevde sıfır çözdü. 12 Ağustos'ta sınır kontrolü sıfırların
düzenekten değil modelden geldiğini gösterdi (20/30'a karşı yayımlanmış gpt-4o
15/30).

Aile taraması başlamadan yazılmazsa post-hoc görünürdü.

## Kurulum protokolü ayrı belge olarak donuyor

Ayrımın sebebi: aile seçimi bir ölçüm ve K-62 gereği yorumlanma kuralı koşudan
önce yazılı olmalı. Ama deney ön kaydının sayıları aile seçilmeden bilinemiyor.
Tek belge yapılsaydı deney başlamadan tadilat kaydı birikmiş olurdu.

`experiments/setup-protocol.md` içinde: aile seçim ölçütü ve eleme tasarımı, ayar
bütçesinin tükettiği dört revizyon, kurulumda dokunulan görev kimlikleri,
taranacak on parametre ve her birinin karar kuralı, tanı metriklerinin tanımı.

**Dereceli skorun tanımı aile taramasından önce yazıldı** ve statüsü net: tanı
metriği, ikincil sonuç değil, birincil metriğe ve kapılara girmiyor, veriyi
gördükten sonra doğduğu yazılı.

## Dokunulan görevler ölçüldü

| Bölme | Dokunulan | Toplam |
|---|---|---|
| train | 13 | 90 |
| dev | 0 | 57 |
| test_normal | **45** | 168 |
| test_challenge | **0** | 417 |

Zorluk bölmesi ve dev hiç dokunulmamış. `test_normal`'dan çıkarılan kırk beş
görev kimliği protokolde listeli; değerlendirmeye **123 görev** kalıyor.

Çıkarma sebebi sızıntı değil görülmüşlük: bu görevlerde hangisinin zor
hangisinin kolay olduğunu gördük ve yayımlanmış gpt-4o koşusunun görev başına
sonuçlarını inceledik.

## PROJECT_STATUS.md yeniden yazıldı

Her tasarım öğesi uygulama durumuna eşlendi: **tasarlandı, uygulandı,
doğrulandı.** Tasarım belgeleri hedef tasarımı anlatıyor, kod alt kümesini
uyguluyor — kalkan, derleyici, getirici ve bağlam montajcısı tasarlandı ama kod
olarak yok. Tablo bunu açıkça gösteriyor, çünkü belgeleri okuyan biri aksini
sanabilir.

Kapanmış S-11'e yapılan bayat atıf da düzeltildi.

## İki düzeltme

**K-43 ve S-22** ikisi de "sansür oranı %10'un altında kalacak" diyordu. Yanlış:
yüzde on kuralı yalnız **tavana çarpma oranına** ait, sansür oranı bir sonuç.
K-53'ün ayırdığı iki nicelik bu iki yerde birleşik kalmıştı; arandı ve başka
canlı normatif yerde birleşik hâl bulunmadı.

**Birincil metriğin ölçülmemesi** denetim raporunda sapma listesinden çıkarıldı.
Ön koşul kapısının ateşlemesinin sonucu; ölçülemedi, atlanmadı.

## Karara bağlananlar

- **K-62** yorumlanma kuralı koşudan önce yazılmamış bir ölçüm sonuç değil,
  kurulum tanısıdır. Somut hâli: bir ölçüm koşulmadan önce hangi niceliği
  ölçtüğü, hangi eşikte ne söyleyeceği ve hangi parametrenin bağlayıcı olmadığının
  nasıl gösterileceği yazılı olacak. Üçü birden olmadan ölçüm sonuç üretemez.
- **K-61** hizalandı: aile kontrolü ana eksenden farklı bir aile, en büyük
  noktanın bandında, tek nokta, ön koşulu o da geçmiş. `granite` seçilmiş değil,
  yalnız aday.

## Bekleyen tek karar

**Ayar bütçesinin sayısı.** Dört revizyon tüketildi (tavan çapası, soğuk rejim,
ön koşul eşiği, model ailesi) ama izin verilen toplam yazılmadı. Protokol o sayı
konmadan tam anlamıyla donmuş sayılmıyor.

## Kontroller

12 Ağustos 2026: ruff temiz, 135 test geçti, atlanan yok, import ve build tamam.
Kod dokunulmadı — `git diff --stat main` yalnız belge gösteriyor.

Denetim raporu: `docs/reports/hizalama-denetimi.md`

## #17 — Model ailesi

- Branch: `model-ailesi`
- Merged: not merged (closed)

<!-- body, verbatim except for task text -->

_(no description)_

## #18 — Künye sözleşmesi sunum kipine göre daraltılıyor, betikler ayrıldı

- Branch: `kunye-serving-mode`
- Merged: 2026-08-12

<!-- body, verbatim except for task text -->

Kod ve şema katmanı. Belgeye dokunulmadı — `git diff --stat main -- docs/
experiments/ PROJECT_STATUS.md` boş.

## Künye sözleşmesi kipe göre daraltılıyor, atlanmıyor

`serving_mode` alanı iki değer taşıyor: `local` ve `hosted`.

Yerele özgü dört alan — `num_ctx_requested`, `num_ctx_effective`,
`kv_cache_type`, `keep_alive` — yalnız `local` kipte zorunlu. Barındırılan
modelde karşılıkları yok: etkin bağlam penceresi doğrulanamıyor, KV cache tipi
ve `keep_alive` bizim ayarımız değil.

Ortak alanlar her iki kipte de zorunlu kalıyor, `model_server_env` dahil;
barındırılan koşuda sağlayıcı ve taşıma katmanı oradan okunuyor.

### Fail-closed yorumla değil makineyle tutuluyor

Şemadaki `CHECK`, yerel kipte dört alanın dolu ve `context_verified = 1`
olmasını istiyor:

```sql
CHECK (serving_mode <> 'local' OR (
    num_ctx_requested IS NOT NULL
    AND num_ctx_effective IS NOT NULL
    AND kv_cache_type IS NOT NULL
    AND keep_alive IS NOT NULL
    AND context_verified = 1
))
```

İki test bunu Python katmanını atlayıp doğrudan `INSERT` ile sınıyor.

**Ters yönde de kapalı.** `hosted` kipte `context_verified = 1` yazılamıyor:
doğrulanamayan bir şeyi doğrulanmış göstermek olurdu.

## Diğer üç madde

**`max_output_tokens` künyeye giriyor** (K-60). Şema yalnız yeni dosyada
uygulandığı için `open_database` eksik sütunları ekliyor; `serving_mode` da aynı
listede. Taşıma yolunun testi var.

**`config/models.yaml` artık en az üç model istiyor**, tam üç değil.
Yapılandırma tasarımdan daha katı bir kısıt kodlayamaz (K-61) — dört boyut
sığdıran bir aile eskiden buradan geçemiyordu.

**Üç keşifsel betik `scripts/setup/` altına alındı** ve orada belgelendi:
kurulum aracı, deney yolunda değil, deney matrisine girmiyor. Ayrım K-52'nin
önyükleme için kurduğu ayrımın aynısı.

## Bilinen sınır

Şema `CHECK`'leri yalnız bu şema sürümünden oluşturulan veritabanlarında
geçerli. Mevcut kurulum veritabanı sütunları taşımayla alıyor ama `CHECK`
kısıtlarını almıyor; orada sözleşmeyi Python katmanı tutuyor. Deney kaydı
sıfırdan açılacağı için pratik etkisi yok.

## Kontroller

ruff temiz, **152 test geçti**, atlanan yok, import ve build tamam.

## #19 — Durma kuralı uç nokta kümesi üzerinden, eşik 10

- Branch: `durma-kurali`
- Merged: 2026-08-12

<!-- body, verbatim except for task text -->

Durma kuralı, aile taraması başlamadan önce düzeltildi. Zamanlama sebebi:
taramanın sayıları aile seçiminde alıntılanacak, kural sonradan değişirse o
sayılar sonraki koşularla karşılaştırılamaz hâle gelir.

## Eski kural neyi kaçırıyordu

"Başarılı çağrı ilerlemedir" diyordu. Ölçülmüş arıza: bir epizot 150 adımda 736
çağrı yaptı, hepsi 200 döndü, veritabanı bir kez bile değişmedi, ve kural hiç
ateşlemedi (S-25).

## Neden eylem kümesi değil, uç nokta kümesi

İlk formülasyon "farklı normalize eylem kümesi büyümeyi durdurdu" idi ve
**kendi motive edici vakasını kaçırırdı.** Normalizasyon değer soyutlaması
yapmıyor: farklı kimliklerle dönen bir döngü her adımda yeni bir normalize eylem
üretir, küme büyümeye devam eder, kural hiç ateşlemez.

Uç nokta kümesi parametreyi soyutluyor. `spotify.library/playlists` sayfa
numarasından bağımsız tek bir uç.

**Yeni kural:** N ardışık adımda doğrulanabilir durum değişmemişse **ve** daha
önce dokunulmamış bir API uç noktasına ulaşılmamışsa epizot kapanır.

## Yazmadan önce ölçüldü

İki motive edici epizodun verisi zaten kayıttaydı.

| Epizot | Adım | Uç nokta | Kümenin son büyüdüğü adım | En uzun durgunluk |
|---|---|---|---|---|
| `09b0ee6_2` | 150 | 3 | 4 | **146** |
| `c77c005_3` | 92 | 4 | 5 | **87** |

İkisinde de kural ateşliyor. Endişe edilen durum — kümenin büyümeye devam etmesi
— gerçekleşmiyor, çünkü uç nokta parametreyi soyutluyor.

## Eşik: 4'ten 10'a, cömert ve geçici

Kayıtlı 62 epizotta en uzun durgunluk dağılımı:

| N | Ateşleyecek epizot |
|---|---|
| 4 | 46/62 |
| 6 | 19/62 |
| **8** | **18/62** |
| **10** | **18/62** |
| **12** | **18/62** |
| 15 | 17/62 |
| 20 | 13/62 |

Sekiz ile on iki arasında **boş bir bant** var. Sağlıklı epizotların en uzun
durgunluğu 6 (`0de03ea_3`, 11 adımda 10 uç nokta), patolojik olanların en kısası
13.

**10 o boşluğun ortasında.** Mevcut eşiğin 2,5 katı, sağlıklı maksimumun
üstünde, on sekiz patolojik epizodun hepsini kesiyor. Amacı yalnız 88 tekrarlı
döngü gibi bariz patolojiyi kesmek; gerçek keşif yeni uçlara ulaşıyor, meşru
sayfalama cömert eşikle tamamlanıyor.

Değer geçici ve künyeye yazılıyor. Kesin sayı eşik taramasından çıkacak.

## Testler

On yedi test. Üçü doğrudan iki arızayı sabitliyor: tekrar eden başarısız giriş,
aynı uçlara yapılan başarılı okumalar, ve her adımda yeni uca ulaşan epizodun
kesilmemesi.

**Kuralı düşürecek mutasyon da test altında.** Uç nokta yerine parametreli çağrı
kimliği kullanılsaydı sayfalama döngüsü her adımda "yeni" görünür ve kural hiç
ateşlemezdi. `test_endpoint_set_abstracts_parameters` tam olarak onu sabitliyor.

**Bir test yazarken düştü ve doğru olan koddu.** İlk adım yeni uca ulaştığı için
ilerleme sayılıyor, dolayısıyla üç adımda yalnız iki durgun adım oluyor. Testi
düzelttim, kodu değil.

## Taksonomi

Tekrar ekseni `07-failure-taxonomy.md` içine ölçülmüş dayanağıyla girdi: adım
etiketi, uç nokta kümesinin doyması, ve dört epizotluk karşılaştırma tablosu.

S-25 kapandı; özgün metni kayıtta duruyor.

## Kontroller

ruff temiz, **157 test geçti**, atlanan yok, import ve build tamam.

## #20 — Kurulum sonrası: durma kuralı, devam mantığı, boşluk raporu (yol haritası maddesi değil)

- Branch: `kurulum-sonrasi-hizalama`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

Yol haritası maddesi **değil**, ve bu yüzden kapanış notu yok. Dal
`kurulum-sonrasi-hizalama`.

## Bu PR neden var

PR akışı #19'dan sonra durdu ve o tarihten bugüne kadar biriken iş tek dalda
kaldı. Talimat "yol haritası maddesi başına bir PR" idi; ama #19 ile yol
haritasının birinci maddesi arasında **maddelere ait olmayan 24 commit** var:
durma kuralının yeniden kurulması, devam mantığı, çıktı bütçesinin
yapılandırmaya taşınması, karar kaydının makine tarafı, düşünme kapatma
doğrulayıcısı ve boşluk raporu.

Bu commit'ler madde 1'in altına konsaydı "madde 1 kalkan" başlığı yanlış olurdu:
içindeki işin çoğu kalkanla ilgisiz. Ayrı bir PR olarak açılıyorlar ve maddelere
ait olmadıkları açıkça yazılıyor.

**Commit'ler, sırayla:**

```
de32822 fix: eşiği yanlış pozitif tarafında da kalibre et, 10 yerine 15
3ffc407 docs: tarama sırasını geçme olasılığına bağla, iki koşullu adayı yaz
fc9101a docs: bant taramasının kirliliğini ölç, üç sonucun kuralını yaz
f7fcbd2 feat: kesinti dayanıklılığı, kirli ağaç kapısı, ön kontrol
6f14db6 docs: bant taraması düzeltilmiş kuralla 0/30 verdi, sonuç yeniden üretti
79c43bd feat: yarıda kesilen koşu için devam mantığı, testli
e8627b4 docs: kural kapalıyken de sıfır, ön koşul kapısı temiz veriye dayandı
4abd99b feat: sınır kontrolüne devam mantığı ve ilk epizotta durma
78ca4c1 feat: çıktı bütçesi yapılandırmaya, devam ederken koşul denetimi
8fe23af docs: S-30 ve S-31, iki protokol kuralı
fd28a43 fix: durma kuralının uç nokta ölçütünü rota şablonuna bağla
97d3668 docs: S-32 ve tekrarını önleyen dört protokol kuralı
e83871b feat: durma kuralının kimliği somut çağrı, eşik 40
e1be4d0 docs: K-63 yeniden yazıldı, K-64 eşiğin bedeli
0b731e0 feat: işlem ve nesne sayısı epizot başına kaydediliyor
30b7995 refactor: tanımlayıcıları İngilizceye çevir
58027ce fix: azınlık ad düzeltmeleri ve çakışan sözlük anahtarı
09cbde6 fix: kalibrasyon çıktısında kalan `step` anahtarı
7a5a9e1 feat: karar CSV'sine tamlık denetimi, üç protokol kuralı ve S-33
c86e375 fix: künye yazma yolunda imza uyuşmazlığı, şema yorumları İngilizce
94d3f09 feat: duman ön kontrolü sınır kontrolü koşucusuna bağlandı
0840b4a docs: S-34 düşünme ihlali, iki karar notu, kestirim yenilendi
89ae8e5 feat: boyut başına düşünme kapatma doğrulayıcısı
abb2a6d docs: adım 7 sandbox kapsamı, iki dilde
```

## Ne kuruldu

| Parça | Yer |
|---|---|
| Durma kuralının kimliği | `src/zihin/recording_agent.py` — somut çağrı, rota şablonu değil (K-63, S-32) |
| Eşik 40 ve bedeli | `config/recording.yaml` — 20 geçen yörüngeye karşı kalibre edildi (K-64) |
| Devam mantığı | `records.resume_check` — koşul alanı uyuşmazlığı reddediliyor (S-31) |
| Çıktı bütçesi | Ortamdan yapılandırmaya taşındı; sessiz varsayılan kaldırıldı (S-30) |
| Kesinti dayanıklılığı | `boot_id`, `wall_clock_utc`, depo dayanıklılığı, kirli ağaç kapısı |
| İşlem/nesne sayısı | `episodes.distinct_endpoints`, `distinct_resources` |
| Karar kaydının makine tarafı | `scripts/build_decisions_csv.py` + tamlık denetimi (S-33) |
| Düşünme kapatma doğrulayıcısı | `scripts/setup/verify_thinking_off.py` (S-34) |
| Sandbox kapsamı | `docs/12-sandbox-kapsami.tr.md` ve `.en.md` |
| Boşluk raporu | `docs/reports/bosluk-raporu.md` — 21 adımlık yol haritasına karşı ölçüm |

## Ne ölçüldü

| Ölçüm | Sonuç |
|---|---|
| Bant taraması, düzeltilmiş durma kuralıyla | test_normal 30 görevde **0 geçti** |
| Aynı tarama, kural kapalıyken | 26 görevde **0 geçti** — ön koşul kapısı temiz veriye dayandı |
| Durma kuralının iki kimliği | Şablon kimliğiyle `8ce6779_2` 107 adım durgun, somut kimlikle 36 |
| Eşiğin bedeli | Eşik 15'te geçen bir epizot kesiliyor, 40'ta hiçbiri; ana koşu 51 → 106 saat |
| Düşünme kapatma | Üç boyutta sıfır akıl yürütme jetonu ve boş alan, üç ayrı soruda |

## Bitmiş sayılma şartları

Bu blok bir yol haritası maddesi olmadığı için yedi şartlık tablo taşımıyor.
Yerine şunlar geçerli: dört CI kontrolü yeşil, testler yerelde tam takım geçiyor,
ve her ölçüm `results/` altında çıktısıyla duruyor. Kararlar `docs/08-decisions.md`
(K-63, K-64 ve komşuları) ve sınırlamalar `docs/09-limitations.md` (S-30..S-34)
içinde.

## Neden şimdi açılıyor

Talimat: her yol haritası maddesi kendi PR'ıyla kapanacak, kapanış notu PR
açıklamasına girecek, madde bitmeden PR açılmayacak ve PR açılmadan sonraki
maddeye geçilmeyecek. Bu blok o kuraldan önce birikti; kural bundan sonra
geçerli ve bu PR birikmiş olanın ilk parçası.

## Sonradan eklenen bir commit: CI'ın hiç görmediği 45 test

`ba88f44` bu dala PR açıldıktan sonra eklendi ve sebebi CI'ın kendisi: `Testler`
işi kırmızı çıktı, 30 test `ModuleNotFoundError: No module named
'appworld.apps.admin'` verdi.

`route_table()` uç nokta çözümlemesini AppWorld'ün **uygulama modüllerinden**
kuruyor ve o modüller `appworld install` ile geliyor, paketle değil: pakette
yalnız `appworld.apps.lib` var. CI paketi kuruyor, `appworld install` koşmuyor
(K-32). O testler `appworld` işaretini taşımadığı için `-m "not appworld"` onları
elemiyordu — yerelde geçiyor, CI'da düşüyorlar. **Bu dal hiç itilmediği için CI
onları hiç görmemişti**, ve PR akışının durmasının doğrudan bedeli bu.

Ölçüldü: HEAD'de dört modülde 45 test bu durumda — `test_api_routes` 16,
`test_stopping_rule` 16, `test_shield_mount` 10, `test_compiler` 3.

Yama AppWorld'ün kendi `import_apis_module`'una konuyor, bizim
`route_table`'ımıza değil: testler `route_table`'ı doğrudan import ediyor, o
yüzden modül özniteliğini yamalamak çağıranın elindeki adı değiştirmiyor ve test
yine düşüyor. Eksik olan yetenek bir alt katmanda.

Elle tutulan bir işaret listesi yerine çağrı anında atlama, çünkü hangi modülün
çözümlemeye dokunduğu zamanla değişiyor: iki modülle başladı, dört oldu. Liste
sessizce eskir; çağrı anındaki atlama yeni testi kendiliğinden kapsıyor.

Uygulama modülleri varken davranış aynı: yerelde tam takım 398 test geçiyor.

## #21 — Madde 1 — Kalkan ve birim test takımı

- Branch: `madde-1-kalkan`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

Yol haritasının 1. maddesi. Dal `madde-1-kalkan`.

Açıklama, maddenin kapanış notunun kendisi (`docs/reports/mekanizma-kapanis-notlari.md`).

**Commit'ler, sırayla:**

```
4d6a0ac docs: boşluk raporu, 21 adımlık yol haritasına karşı ölçüm
27f356a feat: yazma kümesinin statik yarısı, ve S-35 açık maddesi
8fb86ec feat: kalkanın birinci aşama yüklemi, saf ve testli
04c488a feat: izinli uygulama vekili depoya alındı, isabeti yeniden ölçüldü
2b3a7ec fix: rota çözümleyicisi yöntemi de alıyor (S-36), ve okuma kararı kayda geçti
a8369ae fix: ölçüm betiği de çözümleyiciye yöntemi geçiriyor
10e11a2 fix: `update` bir model fiili değil, yazma kümesinden çıkarıldı (S-37)
26103da feat: kalkan gölge modunda yakalama noktasına monte edildi
916ccaf feat: künye kalkanın kipini ve yapılandırma özetini taşıyor (K-73)
c2ce910 feat: yazma kümesinde yöntem karar veriyor (K-74), ve S-35 hükümle kapandı
```

---

## Madde 1 — Kalkan ve birim test takımı

**Durum: kapandı.** Commit'ler `4d6a0ac`..`c2ce910`, on commit: `4d6a0ac`,
`27f356a`, `8fb86ec`, `04c488a`, `2b3a7ec`, `a8369ae`, `10e11a2`, `26103da`,
`916ccaf`, `c2ce910`.

**Liste düzeltildi.** İlk hâlinde altı commit yazıyordu ve birincisi `9e055f9`
idi; o özet artık dalda değil, aynı içeriğin amend edilmiş öncesi. Ayrıca yazma
kümesi türetmesini ve yüklemi getiren üç commit listede yoktu. Doğrusu yukarıda,
ve PR açıklamasındaki commit listesi bu aralıktan üretiliyor.

`4d6a0ac` iki maddeye dokunuyor: boşluk raporu kurulum sonrası işin parçası, ama
`scripts/setup/derive_write_set.py` ilk kez o commit'te doğuyor ve yazma kümesi
kalkanın artefaktı. Doğrusal tarihte ayrılamıyor, o yüzden madde 1'in başına
konuldu.

### Ne kuruldu

| Parça | Yer |
|---|---|
| Saf yüklem | `src/zihin/shield.py` — beş dal, kapalı ret sözlüğü |
| İzinli uygulama çıkarıcısı | `src/zihin/allowed_apps.py` — görev metninden, ground truth'tan değil (K-70) |
| Montaj noktası | `src/zihin/shield_mount.py` + `api_capture._wrap` — çözümleme, kayıt, adım sınırında boşaltma |
| Yazma kümesi türetmesi | `scripts/setup/derive_write_set.py` — yöntem kuralı + GET için gövde taraması |
| Kayıt | `shield_violations` tablosu; künyede `shield_mode`, `shield_config_digest` |

Yüklem montaj noktasından ayrı. Sandbox'a geçişte (K-65) montaj yeniden
yazılacak, yüklem kıpırdamayacak.

### Ne ölçüldü

| Ölçüm | Değer | Nerede |
|---|---|---|
| Yanlış pozitif oranı | **6/147 = %4,1** | `results/shield-cost.json`, train+dev |
| Engelleme oranı, çağrı | **6/9154 = %0,07** | `results/shadow-mode.json`, 258 epizot |
| Engelleme oranı, epizot | 6/258 = %2,33 | aynı |
| Engelleme oranı, görev | 1/58 = %1,72 | aynı |
| Yüklem dağılımı | okuma %94,29, izinli yazma %5,65 | aynı |
| Fail-open dalı | 5213 kayıtlı çağrının **0'ı** | `results/shield-cost.json` |
| Yazma kümesi kapsaması | 478 API, 478 anahtar, yöntemsiz uç 0 | aynı |
| Yazar uç | 296 (sınır geçen 19, GET yazarı 12, `download_*` 9) | `results/write-set-static.json` |
| Uygulama kümesi çıkarımı | tam eşleşme %75,5, Jaccard 0,857 | `docs/reports/izinli-uygulama-vekili.md` |

**İki oran birbirinin yerine geçmiyor (K-72).** Yanlış pozitif yalnız yer
gerçeği olan train + dev'de ölçülebiliyor; engelleme oranı bütün korpusta
ölçülüyor ama orada bir engellemenin doğru olup olmadığı bilinemiyor.

**Engelleme oranı kalkanın ucuzluğunu göstermiyor.** Altı engellemenin altısı da
düzeneğin kendi yazma sondalarından (`durum-sondasi-*`, `notlar`,
`reset-check-1`, `sifirlama*`), tek görevde ve tek uçta. Model yörüngelerinde
engelleme oranı **sıfır**, ve bu korpusun kalkanı sınamadığının kanıtı: 58
görevin çoğu tek uygulamaya dokunuyor, sınır geçen yazma fırsatı hiç doğmuyor.

### Ölçüm sırasında bulunan ve düzeltilen kusurlar

| | Kusur | Etki |
|---|---|---|
| S-36 | Çözümleyici yöntemi almıyordu, iki `phone` şablonu aynı yolu eşliyor | 26 çağrı bilinmeyen uca düşüyordu; bu korpusta latent |
| S-37 | `update` model fiili değil, Python kap metodu | İki saf okuma yazar sayılıyordu, ikisi gölge modunda engellendi |
| S-38 | `ast.walk` süsleme listesini geziyordu | Dokuz `delete_account` kümede yalnız kaza sonucu duruyordu |
| S-35 | K-41 ile bir uç anlaşmazlığı | **Kapandı**: K-41 fazladan saydı |

### Bilerek açık bırakılanlar

- **Zorlama kipi kurulmadı (K-71).** İkame yanıtın biçimi bir koşul değişkeni
  ve karar verilmedi. `enforce` ile kurulmaya çalışılırsa montaj kurulum anında
  düşüyor.
- **Bilinen fazla dahil etme (S-38).** 64 GET dışı ucun gövdesinde yazma yok ve
  hepsi kümede; ikisi doğrulanmış okuyucu. Uç bazında `body_write` alanıyla
  kayıtlı. Bir adım öteye de yayıldı: üç `add_payment_card` ucu bu iki okuyucu
  üzerinden sınır geçen yazar oldu. Pratik etkisi sıfır, çünkü `admin` altyapı
  uygulaması ve koşulsuz izinli — ve bu artık varsayım değil, `allowed_apps.py`
  içinde kural ve `test_allowed_apps.py` içinde çivili. Üç uçtan biri doğrudan
  yüklem üzerinden sınanıyor.
- **Ampirik yarı boş (S-35, K-41).** Küme `statik ∪ ampirik` olarak tanımlı,
  ampirik yarı henüz toplanmadı.

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Yüklem, çıkarıcı, montaj, türetme, künye alanları |
| Testi yazıldı | Evet. `test_shield.py` 15, `test_shield_mount.py` 13, `test_allowed_apps.py` 16, künye sözleşmesi 6, devam koruması 2 |
| Loglandı | Commit gövdelerinde; ölçüm çıktıları `results/` altında |
| Belgesi yazıldı | K-69..K-74, S-35..S-38, bu not |
| Hata durumu düşünüldü | Bilinmeyen uç adlandırılmış dal; zorlama kipi kurulumda düşüyor; kalkanlı koşu özetsiz künye yazamıyor; türetme kapısı dört değişmezi sınıyor |
| PR üzerinden gözden geçirildi | **Henüz hayır.** Çalışma `durma-kurali` dalında, `origin/main`'in önünde. Depoda PR akışı **var** (18 birleştirilmiş PR); bu iş henüz açılmadı. İnceleme yapıldı, yukarıdaki tanımla |
| Temiz kurulumda baştan çalıştırıldı | Test takımı tam geçiyor; türetme sıfırdan koşup kapıyı geçiyor; künye göçü gerçek seri 2 kopyasında sınandı |

**Sağlanmayan tek şart PR incelemesi**, ve sebebi zamanlama: dal henüz
açılmadı. İnceleme yapıldı ama diff üzerinden değil, yukarıdaki tanımla.

**Düzeltme.** Bu satır ilk yazıldığında "bu depoda PR akışı yok" diyordu ve
yanlıştı: 19 PR var, 18'i birleştirilmiş. Doğrusu yukarıda.

### Bu maddede kayda geçen genel kurallar

Kalkan işi dört protokol kuralı doğurdu; hepsi
`experiments/setup-protocol.md` içinde ve hepsi ölçülmüş bir arızadan geliyor.

| Kural | Doğuran arıza |
|---|---|
| Bir fonksiyonun davranışı değişince çağıranın düzeltilmiş yolu koştuğu ayrıca doğrulanır | Çözümleyici düzeltildi, ölçüm betiği eski yolda kaldı |
| Küçük olmak doğru olmak değil | %0,09 engelleme oranının içindeki iki saf okuma |
| Bir ölçüm, ölçtüğü şeyin üretim uygulamasını çağırır | Yeniden yazılan `writes_of` sıfır verdi, üretim yolu altı |
| Doğrulayıcıya karşı ölçülmüş olmak dal testlerinin yerine geçmez | `allowed_apps.py` %75,5 ile ölçüldü, sıfır testi vardı |

---

## Sonradan eklenen bir commit: test takımı çağırma biçimine bağlıydı

`cfdc1e1` PR açıldıktan sonra eklendi ve sebebi CI'ın kırmızısı:
`ModuleNotFoundError: No module named 'tests'`, tahsilat aşamasında.

`tests/test_shield_mount.py` sahte istekçiyi `tests.test_api_capture` üzerinden
alıyor — bu maddenin kendi testi. Depo kökü sys.path'te olmadığında import
düşüyor, ve kökün orada olup olmaması **çağırma biçimine** bağlı: `python -m
pytest` çalışma dizinini ekliyor, `pytest` betiği eklemiyor. Yerelde birincisi
koşuyordu, CI ikincisini koşuyor.

Düzeltme testte değil yapılandırmada: `pyproject.toml` içinde `pythonpath = ["."]`.
Aynı takımın iki çağırma biçiminde farklı sonuç vermesi testin değil
yapılandırmanın kusuru, ve düzeltmesi ikisini eşitliyor.

**Yerel ön kontrol bunu kaçırdı** çünkü ön kontrol de `python -m pytest`
kullanıyordu — yani kusuru gizleyen biçimin aynısı. Ön kontrol artık betik
biçimini koşuyor.

## #22 — Madde 2 — Beceri şartnamesi

- Branch: `madde-2-skill-spec`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

Yol haritasının 2. maddesi. Dal `madde-2-skill-spec`.

Açıklama, maddenin kapanış notunun kendisi (`docs/reports/mekanizma-kapanis-notlari.md`).

**Commit'ler, sırayla:**

```
51f3e0d docs: madde bir kapanış notu, ve SKILL_SPEC son koşul tanımıyla
3cbd9eb test: altyapı uygulaması kuralı çivilendi, ve son koşul şekil okumasına bağlandı
78134d1 docs: madde 3 ön kaydı, ve iki kural daha kayda geçti
c30ff34 docs: salt okuma örüntüleri kütüphaneye girmiyor (K-75), kapı ve çeviri kararları
```

---

## Madde 2 — Beceri şartnamesi

**Durum: kapandı.** Commit'ler `51f3e0d`, `3cbd9eb`, `78134d1`, `c30ff34`.

### Ne kuruldu

Bu madde belge üretti, kod üretmedi; kodu madde 3.

| Parça | Yer |
|---|---|
| Yedi bölümlü şartname | `SKILL_SPEC.md` — kimlik, gövde, destek, ön koşul, son koşul, beklenen tasarruf, sicil |
| Son koşulun tanımı | Destekleyen epizotlardaki durum farklarının **şekil** kesişimi (kullanıcı tanımı) |
| Dokuz değişmez | Derleyicinin çıktısının sağlaması gerekenler; madde 3'ün doğrulama kapısı bunları sınıyor |
| Kütüphaneye girme şartı | Etki soneki boş olamaz (K-75); boş olanlar **keşif öneki** olarak ayrı raporlanıyor |

Son koşulun okuma düzeyi karara bağlandı — şekil, büyüklük değil — ve gerekçesi
ölçüm değil dilin kendi tasarımı: serbest parametresi olan bir beceride fark
büyüklüğü tanımı gereği değişiyor, dolayısıyla sıkı okuma hiçbir destekleyen
epizotta tutmazdı.

### Ne ölçüldü

Kayıtlı 3909 adımda (`results/pilot-dataset.json` → `record`):

| Ölçüm | Değer |
|---|---|
| Durum değişimi gösteren adım | 28 (%0,7) |
| Değişen farklı model | 18 |
| Aynı modelde birden fazla büyüklük görülen | 9 (18'in yarısı) |
| `supervisor`'ın durum farklarında görünmesi | hiç |

Son ölçüm bir kaygıyı kapattı: `state_probe` ile `allowed_apps` içindeki altyapı
listeleri farklı, ve bu fark son koşulu kirletiyor olabilirdi. Kirletmiyor.

**Üç yorum sonuç görülmeden yazıldı** (şartnamenin içinde): büyüklük sabitse sıkı
okuma geri gelir; parametreyi izliyorsa şekil okuması doğrudur; hiçbir şeyi
izlemiyorsa sonda gürültülüdür ve mekanizma askıya alınır. Madde 3'te
gerçekleşen ikincisi oldu.

### Bilerek açık bırakılanlar

- **Değer eşiği, sabit ilan etme eşiği, boşluk kısıtı** sayı olarak yazılmadı
  (K-50). Karar kuralları ön kayıtta, sayıları kurulum sonrasında.
- **Bilinen sınır yazıldı:** durum farkı satır sayımına dayanıyor, güncelleme
  görünmüyor (S-35). Son koşul aynı yerde kör.

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | **Bu madde kod üretmiyor.** Şartname belge; kodu madde 3'te ve orada sayılıyor |
| Testi yazıldı | Kısmen. Şekil okuması `3cbd9eb` ile çivilendi; dokuz değişmezin testi madde 3'te |
| Loglandı | Commit gövdelerinde |
| Belgesi yazıldı | Şartnamenin kendisi belge; K-75, S-35 |
| Hata durumu düşünüldü | Boş son koşul ile NULL ayrı; boş etki soneki kütüphaneden çıkıyor; üç yorum önceden yazıldı |
| PR üzerinden gözden geçirildi | Hayır, madde 1'deki sebeple: dal açılmadı. İnceleme rapor üzerinden yapıldı |
| Temiz kurulumda baştan çalıştırıldı | Uygulanmaz, koşulacak bir şey yok |

---

## #23 — Madde 3 — Derleyici v0 ve skills tablosu

- Branch: `madde-3-derleyici`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

Yol haritasının 3. maddesi. Dal `madde-3-derleyici`.

Açıklama, maddenin kapanış notunun kendisi (`docs/reports/mekanizma-kapanis-notlari.md`).

**Commit'ler, sırayla:**

```
1d76cd4 feat: derleyici v0 madencilik çekirdeği, ve eşik duyarlılığı ölçüldü
7266048 feat: derleyicinin dört kararı uygulandı, giriş ailesi gerçek beceri oldu
f4d7471 style: ruff biçimlendirmesi
e22b103 feat: birleştirme koştu ve kontrol kanalı gövdeden çıktı — 40 örüntü, 4 beceri
afbef92 fix: bağlılık gövde içinde aranıyor (S-42), ve boşluk üst sınırı ölçüldü (K-81)
142662f feat: skills tablosu ve kütüphane derleyicisi
30233e4 fix: beklenen tasarruf model çağrısıyla ölçülüyor (K-82)
```

---

## Madde 3 — Derleyici v0 ve `skills` tablosu

**Durum: kapandı.** Commit'ler `1d76cd4`, `7266048`, `f4d7471`, `e22b103`,
`afbef92`, `142662f`, `30233e4`.

### Ne kuruldu

| Parça | Yer |
|---|---|
| Madencilik çekirdeği | `src/zihin/compiler.py` — kapalı sıralı örüntü, boşluk kısıtı, destek görev üzerinden |
| Etki ayrımı | Yazma kümesine göre etki soneki; boş olan keşif öneki (K-75) |
| Birleştirme | Aynı etki soneki aynı beceri; arama öneki farkı beceriyi çoğaltmıyor |
| Argüman sınıflandırması | Bağlı / serbest / sabit; sıra bağlılık→değişkenlik |
| Son koşul | Destekleyen epizotların durum farklarının şekil kesişimi |
| Kontrol kanalı ayrımı | `supervisor.message` ve `complete_task` gövdeden de çıkıyor (K-80) |
| Tablo ve yazma yolu | `schema.sql` `skills`, `records.insert_skill`, `replace_library` |
| Ölçüm ve inşa betikleri | `scripts/setup/mine_skills.py` (3×7 ızgara), `build_skill_library.py` |

### Ne ölçüldü

Korpus: 22 geçen epizot, 20 görev, 854 çağrı, 46 elemanlı alfabe
(`pilot-dataset.json` → `mining_grid`).

Kurşun yapılandırma boşluk 2 / destek 3:

| Ölçüm | Değer |
|---|---|
| Kapalı örüntü | 100 |
| Etki soneki dolu | 38 |
| Birleştirme sonrası beceri | **4** |
| Keşif öneki | 62 |
| Bağlı argüman / serbest parametre | 13 / 14 |
| Son koşul | 4'ünde de boş |

Eşik duyarlılığı 21 hücrede süpürüldü: destek 2'ye inince beceri sayısı boşluk
2'de 11, boşluk 5'te 35; destek 8'de 1, destek 10'da 0.

Beklenen tasarruf iki birimde: adım tabanlı 8, 7, 20, 30; çağrı tabanlı 8, 14,
20, 30. Dört beceriden üçünde iki sayı aynı, `spotify` becerisinde iki kat fark
var — çünkü üç çağrıyı iki adımda yapıyor.

### Ölçüm sırasında bulunan ve düzeltilen kusurlar

| | Kusur | Etki |
|---|---|---|
| S-42 | Bağlılık epizot boyunca aranıyordu, gövde içinde değil | En yüksek destekli beceri parametresiz çıkıyordu ve çalışma anında parolayı elde edemezdi. Bağlı 22→13, serbest 5→14 |
| K-82 | Şartname "uzunluk eksi bir" diyordu, yani API çağrısı sayıyordu | Birincil metrik model çağrısı; tasarruf adım tabanlı oldu, çağrı tabanlı tanı olarak yanında duruyor |
| K-79 | İlk atıf uygulaması "herhangi bir adım yalıtılmışsa ölçülebilir" sayıyordu | Bir kirli epizot dört oluşumun anlaştığı kesişimi boşaltıyordu. Artık etki sonekindeki her çağrının yalıtılmış olması gerekiyor |
| — | İlk madenci sonlanmıyordu: her düzeyde bütün alfabeyi deniyor ve her oluşumu tutuyordu | Aday güdümlü genişletme, yalnız bitiş konumları |
| — | İki test yanlıştı, kod doğruydu | Kapanış filtresinin doğru davranışı boşluk hatası sanılmıştı |

### Bilerek açık bırakılanlar

- **Son koşullar boş** ve iki sebebi var (S-41): giriş çağrısı satır üretmiyor, ve
  atıf yalıtılmış adım gerektiriyor.
- **Değer eşiği uygulanmadı**, saklandı; eşik pilottan önce seçilmeyecek (K-50).
- **Destek 2 hücrelerinin beceri kimlikleri kaydedilmedi**, yalnız sayıları.

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Madenci, birleştirme, argüman sınıflandırması, son koşul, tablo, iki betik |
| Testi yazıldı | Evet. `test_compiler.py` 36, `test_skill_library.py` 15 |
| Loglandı | Commit gövdelerinde; `results/mined-skills.json` ızgarayla birlikte |
| Belgesi yazıldı | K-75, K-79…K-82, S-41, S-42; `SKILL_SPEC.md` güncellendi |
| Hata durumu düşünüldü | Dokuz değişmez doğrulama kapısında; NULL ile boş ayrı; projeksiyon silinip yeniden üretilebiliyor |
| PR üzerinden gözden geçirildi | Hayır, dal açılmadı. İnceleme rapor üzerinden |
| Temiz kurulumda baştan çalıştırıldı | Kısmen, ve sınırı yazılıyor. Kütüphane kayıttan üretiliyor, projeksiyonun silinip yeniden üretilebilmesi testte çivili. **Aynı kimlikle** yeniden üretme sınanmadı: kimlik derleyici commit'ini taşıyor (`v0-gap2-sup3-142662f`), yani bugün yeniden üretmek yeni bir kütüphane kimliği yazar ve ölçülmüş artefaktı yerinden oynatır |

---

## #24 — Madde 4 — Hata indeksi ve failure_patterns tablosu

- Branch: `madde-4-hata-indeksi`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

Yol haritasının 4. maddesi. Dal `madde-4-hata-indeksi`.

Açıklama, maddenin kapanış notunun kendisi (`docs/reports/mekanizma-kapanis-notlari.md`).

**Commit'ler, sırayla:**

```
ecc70d9 feat: hata indeksinin alt tabakası ölçüldü, inşadan önce
771b94f feat: hata indeksi ve failure_patterns tablosu
4bb340a fix: projeksiyon testi failure_patterns tablosunu da tanıyor
```

---

## Madde 4 — Hata indeksi ve `failure_patterns` tablosu

**Durum: kapandı.** Commit'ler `ecc70d9`, `771b94f`, `4bb340a`.

### Ne kuruldu

| Parça | Yer |
|---|---|
| Alt tabaka ölçümü | `scripts/setup/measure_failure_substrate.py` — **inşadan önce** koşuldu |
| Madenci | `src/zihin/failure_index.py` — gruplama, karşıtsal küme, koşul arama |
| Koşul dili | Kapalı, üç biçim; kayıtta yalnız üçüncüsü gözlenebiliyor (K-83) |
| Tablo ve yazma yolu | `schema.sql` `failure_patterns`, `records.insert_failure_pattern`, `replace_index` |
| İnşa betiği | `scripts/setup/build_failure_index.py` |

### Ne ölçüldü

Alt tabaka (`pilot-dataset.json` → `failure_substrate`): 5213 eylem, 767
başarısızlık; 401 → 498, 422 → 235, 409 → 34; 20 farklı başarısız uç, 18'inin
karşıtsal eşi var, 5'i iki ya da daha fazla görevde başarısız.

İndeks (`pilot-dataset.json` → `failure_patterns`): 15 kalıp; 11 `401`, 3 `422`,
1 `409`; 13'ünün karşıtsal eşi var, 2'sinin yok ve o ikisi koşul taşımıyor;
koşullu 13 kalıbın 12'sinde koşul çağrının kendi uygulamasına ait.

**Alt tabakanın inşadan önce ölçülmesi bir kararı önceden verdirdi:** `error_class`
tek değerli çıktı (S-44), yani sinyal durum kodunda ve indeks onun üzerine
kuruldu.

### Ölçüm sırasında bulunan ve karara bağlanan şeyler

| | Ne | Sonuç |
|---|---|---|
| K-84 | Ayna bulgusu: kütüphane jetonu almayı öğretiyor, indeks jetonu taşımamayı yasaklıyor | İki mekanizma bağımsız değil; toplanabilirlik bu korpusta muhtemelen tutmayacak |
| K-83 | Koşul dilinin dördüncü biçimi eklenmedi | Argüman bileşeni **normalize şekil**, değer değil; `access_token` şekilde kalıyor |
| K-85 | Karşıt başarısı sıfır olan kalıpta ayırt etme boş bir iddia | O kalıplar koşul taşımıyor; dört CHECK zorluyor. `splitwise.auth/logout`'un 59 koşulu böyle düştü |
| S-45 | Koşul tesadüfen ayırabiliyor | Ad hoc kısıt konmadı; kart iki tanı alanı taşıyor ve getirici okuma anında filtreliyor |
| S-43 | 409'un gerçek sebebi nesne durumu | Sınıf v0 kapsamı dışında; kapanma yolu yanıt gövdesinin kalıcılaştırılması |

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Madenci, tablo, yazma yolu, iki betik |
| Testi yazıldı | Evet. `test_failure_index.py` 14; projeksiyon testi tabloyu tanıyor (`4bb340a`) |
| Loglandı | Commit gövdelerinde; `results/failure-substrate.json` |
| Belgesi yazıldı | K-83…K-85, S-43…S-45; `07-failure-taxonomy.md` ile tutarlılık denetlendi |
| Hata durumu düşünüldü | Dört CHECK koşul/işaret tutarlılığını zorluyor; kalkan ihlali tek başına kayıt üretmiyor; indeks silinip yeniden üretilebiliyor |
| PR üzerinden gözden geçirildi | Hayır, dal açılmadı. İnceleme rapor üzerinden |
| Temiz kurulumda baştan çalıştırıldı | Kısmen, kütüphaneyle aynı sebeple: indeks kayıttan üretiliyor ama kimliği (`v0-sup1-4bb340a`) derleyici commit'ini taşıdığı için aynı kimlikle yeniden üretme sınanmadı |

---

## #25 — Madde 5 — Getirici v0

- Branch: `madde-5-getirici`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

Yol haritasının 5. maddesi. Dal `madde-5-getirici`.

Açıklama, maddenin kapanış notunun kendisi (`docs/reports/mekanizma-kapanis-notlari.md`).

**Commit'ler, sırayla:**

```
4136d71 feat: getirici v0 ve kapsama ölçümü, ve S-45 kararları uygulandı
```

---

## Madde 5 — Getirici v0

**Durum: kapandı.** Commit `4136d71`.

### Ne kuruldu

| Parça | Yer |
|---|---|
| Getirici | `src/zihin/retriever.py` — sembolik eşleşme, sembol uygulama |
| Eşleşme ölçütü | Becerinin **etki soneki**, gövdesi değil |
| Altyapı ayrımı | Getiricide düşüyor, kalkanda düşmüyor; tek çıkarım iki kullanım (K-86) |
| Filtreler | Üçü de varsayılansız argüman: değer eşiği, ayıran koşul üst sınırı, doğrulanmamış kart anahtarı |
| Ölçüm betiği | `scripts/setup/measure_retrieval.py` — 50 hücreli duyarlılık ızgarası, bölme başına |

### Ne ölçüldü

Kapsama, filtresiz tavan (`pilot-dataset.json` → `coverage`): train %96,7 /
%90,0 / %96,7; dev %94,7 / %89,5 / %94,7; test_normal %100 / %94,6 / %100
(herhangi / yalnız beceri / yalnız hata). Yanlışlama kapısı %25; dokuz ölçümün
(üç bölme × üç okuma) dokuzu üstünde.

Madencilenmemiş görevlerde kapsama düşmüyor: test_normal'ın 150 görülmemiş
görevinde %100.

**Ayırt edicilik ayrıca ölçüldü**, çünkü yüksek kapsama tek başına onu
göstermiyor: test_normal'da 21 farklı kart kümesi, en sık küme görevlerin
%20,8'i. Getirici ayırıyor — ama ayırdığı şey hangi uygulamanın girişi.

Duyarlılık: değer eşiği 10'da beceri kapsaması %94,6→%50,6, 30'da %35,7; ayıran
koşul üst sınırı 1'de hata kapsaması %100→%38,1.

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Getirici, üç filtre, ölçüm betiği |
| Testi yazıldı | Evet. `test_retriever.py` 14; ikisi mutasyon testi (gövdeye eşleşme, altyapı) |
| Loglandı | Commit gövdesinde; `results/retrieval-coverage.json` |
| Belgesi yazıldı | K-86; kapsama kapısı `05-experiment-design.md` ile bağlandı |
| Hata durumu düşünüldü | Filtre verilmezse `TypeError`; NULL tasarruf küçük sayılmıyor; iki kütüphane birbirine karışmıyor |
| PR üzerinden gözden geçirildi | Hayır, dal açılmadı. İnceleme rapor üzerinden |
| Temiz kurulumda baştan çalıştırıldı | Evet. Ölçüm salt okunur bağlantıyla, sıfırdan koşuyor |

### Bu maddede kayda geçen genel kural

| Kural | Doğuran arıza |
|---|---|
| Bir kapıya zincirlenen her komutun çıkış durumu kapıya bağlanır, ve bağ komut kasten düşürülerek sınanır | Doğrulama aleti alt süreç çıkışını denetlemiyordu; pytest çıkışı commit kapısına bağlı değildi ve takım düşerken commit geçti |

---

## #26 — Madde 6 — Mekanizma pilotu

- Branch: `madde-6-mekanizma-pilotu`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

Yol haritasının 6. maddesi. Dal `madde-6-mekanizma-pilotu`.

Açıklama, maddenin kapanış notunun kendisi (`docs/reports/mekanizma-kapanis-notlari.md`).

**Commit'ler, sırayla:**

```
b0f9051 feat: mekanizma pilotu — kart biçimi, iki eksik ölçüm, pilot veri seti ve rapor
```

---

## Madde 6 — Mekanizma pilotu

**Durum: kapandı.** Raporu `PILOT_REPORT.md`, verisi
`results/pilot-dataset.json`.

### Ne kuruldu

| Parça | Yer |
|---|---|
| Kart biçimi | `src/zihin/cards.py` — beceri kartı yedi alan, hata kartı beş alan (K-87) |
| Jeton sayacı | `model_server.count_tokens`, `count_chat_tokens` — sunucunun kendi tokenizer'ı |
| Kart jeton ölçümü | `scripts/setup/measure_card_tokens.py` |
| Bağlam maliyeti ölçümü | `scripts/setup/measure_context_cost.py` — üretim yolu dünya açılarak doğrulanıyor |
| Pilot veri seti | `scripts/setup/build_pilot_dataset.py` → tek dosya, kaynak özetleri, tutarlılık kapısı (K-89) |
| Kirli ağaç kapısının daraltılması | `records.working_tree` + `defines_measurement` (K-76) |
| Pilot raporu | `PILOT_REPORT.md` |

### Ne ölçüldü

Şartnamede duran ama hiç sınanmamış iki ölçüm:

| Ölçüm | Sonuç |
|---|---|
| Beceri kartı | 4 kart, 78–122 jeton (medyan 88), bütçe ≤180, **aşan 0** |
| Hata kartı | 14 kart, 36–48 jeton (medyan 42), bütçe ≤120, **aşan 0** |
| Alan sayısı | Beceride 7, hatada 5; hepsinde |
| Üç modelin uyumu | Her kart için aynı sayı |
| k=5+5 blok | En çok 523 jeton; bütçe tavanı 1500 |
| Sabit blok | Medyan 3172–3185 jeton, pencerenin %9,7'si |
| Kartlarla toplam | Medyan 3296–3447 (%10,1–10,5), en çok 3645 (%11,1) |
| Tur maliyeti | Medyan 182, ortalama 419, p90 1066 jeton |
| İskelenin karakter tavanı | 50000 karakter = **12799 jeton**, pencerenin %39'u |

Korpus çeşitliliği doğrudan ölçüldü (ızgaradan çıkarım yerine): 20 geçen görev, 6
uygulama, 8 farklı uygulama kümesi; 3+ görevde tekrarlayan 14 çağrının 4'ü
altyapı, 4'ü oturum, 5'i sıradan okuma, **1'i sıradan yazma**.

### Ölçüm sırasında bulunan kusurlar

| | Kusur | Etki |
|---|---|---|
| S-46 | Mimari belgesindeki sabit blok payı ölçülmemişti ve yanlıştı | Beşte bir değil onda bir; belge düzeltildi |
| S-47 | Bağlayıcı sınırın hangi birimde olduğu bilinmiyordu | Karakter tavanı bağlıyor; pencere hiç dolmuyor |
| S-48 | İndeksin en sık kalıbı hiçbir görev tarafından getirilemiyor | Terk kriteri getirilebilir kalıp sayısına bakacak |
| K-76 | Kapı listeye daraltılırken listenin kendisi eksik çıktı | `retriever.py` ve `cards.py` eklendi; eksik girdinin bedeli daraltmayla arttı |
| — | `num_predict: 0` "üretme" demiyor | Sayaç `num_predict: 1` kullanıyor; ölçüm takıldığı için fark edildi |
| — | S-45'in kendi uygulama sayısı K-85'ten sonra eskimişti | 15 kartın 14'ü değil, koşullu 13 kartın 12'si; bölen değişmiş |

### Bilerek açık bırakılanlar

- **Pilot koşusu koşulmadı** ve koşulamaz: ön koşul kapısı ateşledi, taban sıfır
  çözüyor, adım farkı tanımsız. Raporun ilk bölümü bunu kanıtıyla söylüyor.
- **Eşikler seçilmedi** (K-50): değer eşiği, ayıran koşul üst sınırı,
  doğrulanmamış kart anahtarı. Üçü de duyarlılık ızgarasında.
- **Kart biçimi modele hiç gösterilmedi.** Bütçeye sığdığı ölçüldü; bir modelin
  onu okuyup kullanabildiği gösterilmedi. O madde 7, uçtan uca demo.
- **Zorlama kipi kurulmadı** (K-71).

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Kart biçimi, jeton sayacı, iki ölçüm betiği, veri seti kurucusu, daraltılmış kapı |
| Testi yazıldı | Evet. `test_cards.py` 14, `test_manifest_contract.py` 68'e çıktı (kapı kapsamı için 9 yeni) |
| Loglandı | `results/card-tokens.json`, `results/context-cost.json`, `results/pilot-dataset.json` |
| Belgesi yazıldı | K-76 uygulama notu, K-87…K-89, S-46…S-48; `03-architecture.md` düzeltildi; protokole bir kural |
| Hata durumu düşünüldü | Veri seti eksik girdiyle kurulmuyor; kütüphane kimliği ayrışırsa duruyor; iki AppWorld commit'i varsa duruyor; kart bütçeyi aşarsa betik düşüyor; sayaç sıfır dönerse hata fırlatıyor |
| PR üzerinden gözden geçirildi | Hayır, dal açılmadı. İnceleme rapor üzerinden |
| Temiz kurulumda baştan çalıştırıldı | Evet. Üç ölçüm de sıfırdan koştu; bağlam ölçümü kendi üretim yolunu dünya açarak doğruladı |

### Bu maddede kayda geçen genel kural

| Kural | Doğuran ihtiyaç |
|---|---|
| Rapor sayıyı kopyalamaz, veri setine atıf verir | Sekiz ölçüm çıktısı, sekiz ayrı gün; yazma kümesi tek günde iki kez değişti ve aynı ölçüm iki farklı sayı verdi |

---

## #27 — Madde 7 — Uçtan uca demo

- Branch: `madde-7-demo`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

Yol haritasının 7. maddesi. Dal `madde-7-demo`.

Açıklama, maddenin kapanış notunun kendisi (`docs/reports/mekanizma-kapanis-notlari.md`).

**Commit'ler, sırayla:**

```
5a21312 feat: karakter tavanı künyeye girdi (K-90), ve kart demosunun koşucusu
63fa7ba feat: madde 7, uçtan uca demo — kart bağlama girdi, bir görevde kullanıldı
```

**Birinci commit iki maddeye ait ve bölme zorlanmadı.** `5a21312` iki iş taşıyor:
karakter tavanının künyeye girmesi (K-90) madde 6'nın S-47 bulgusunun devamı, ve
`record_run.py --cards` yolu madde 7'nin aracı. Doğrusal tarihte `b0f9051`'den
sonra geliyor, yani ayırmak commit'i bölmek — tarihi yeniden yazmak — olurdu.
Commit'lerin doğrusal kalması istendiği için madde 7'nin başına konuldu; K-90'ın
gerekçesi madde 6'nın raporunda (`PILOT_REPORT.md`, S-47) duruyor.

---

## Madde 7 — Uçtan uca demo

**Durum: kapandı.** Raporu `docs/reports/uctan-uca-demo.md`, verisi
`results/card-demo.json`.

### Ne kuruldu

| Parça | Yer |
|---|---|
| Kartlı koşu | `scripts/record_run.py --cards` — getiricinin kartlarını slota koyuyor, koşul adını kart yapılandırmasından alıyor, `library_id`'yi künyeye yazıyor |
| Demo ölçümü | `scripts/setup/measure_card_demo.py` — giriş ve kullanım ayrı, kartlı/kartsız eşleştirilmiş |
| Eşleşme araması | Derleyicinin kendi `occurrences_of`'u, boşluk 2 (K-81) |
| Devam edebilirlik | Kayıtlı epizot yeniden koşulmuyor; `UNIQUE (run_id, task_id, condition, seed)` zaten reddediyor ve yerel 7B'de bir epizot on beş dakikayı aşıyor |
| Karakter tavanı | Aynı maddede künyeye girdi (K-90); demo epizotlarının hepsi 50000 ile koştu ve künyede yazılı |

**Kart bulunamayan görevde kartlı koşu başlamıyor.** Boş slotla koşan bir epizot
künyede `library_id` taşır ve kartlı görünürdü.

### Ne ölçüldü

On epizot, beş çift, tek model (`qwen2.5-coder:7b-instruct-q4_K_M`).

**Giriş, modele bakmadan, 3/3:** blok prompt'un içinde bayt bayına; iki prompt
yalnız blok kadar farklı; kartsız kolun prompt'u referansla bayt bayına aynı
(K-25); künye özetleri farklı. Blok 125 ve 166 jeton, yani kart bütçesinin
(≤180+≤120) yarısından küçük.

**Kullanım:**

| Ölçüm | Sonuç |
|---|---|
| Soru sorulabilir görev | 2/3 (birinde iki kol da hiç çağrı üretmedi) |
| Yörünge kartsızdan farklı | 1/2 sorulabilir görevde; beş çiftin üçünde |
| Gövde eşleşmesi, kartlı | 1/3 (`0de03ea_1`: 3/3 eleman; kartsız 1/3) |
| Başarılı etkiye ulaşma | kartlı 2 çift, kartsız **0** çift |
| Doğrulayıcıyı geçen epizot | **0/10** |

En açık hâl `0de03ea_1`: kartlı kol adım 4'te başarılı giriş yaptı, adım 13'te
kendi kendine durdu; kartsız kol yirmi adımın yirmisinde aynı `api_docs` çağrısını
yaptı ve tavana çarptı. Çağrı 20 → 11.

### Ölçüm sırasında bulunan kusurlar

| | Kusur | Etki |
|---|---|---|
| Görev seçimi | İlk üç eşleşme aynı senaryonun üç varyantıydı | "Üç görev" tek kartın üç kez sınanmasıydı; ölçüte farklı senaryo şartı eklendi, koşmuş epizotlar senaryo içi tekrar olarak ayrı etiketli |
| Ön kayıt | Dört yorum "iki kol da hiç çağrı üretmedi" hâlini öngörmüyordu | Beşinci yorum eklendi: o görevde soru **sorulamaz**; iki boş dizinin eşitliği kimlik iddiası değil (K-79'un ayrımı) |
| Kullanım ölçümü | "Etkiye ulaştı" ile "başarıyla ulaştı" ayrılmamıştı | Taban kolunda iki `401` giriş denemesi etkiye ulaşma sayılıyordu ve kartın kazandığı yer beraberlik görünüyordu |
| S-45 | Kartın koşulu canlı olarak yanlış çıktı | `simple_note.notes` gerçekten `401` döndü ama kartın koşulu (`profile` çağrılmış olması) korelasyon; etiket doğru, koşul yanlış |

### Bilerek açık bırakılanlar

- **Atomik yürütme yok.** Kart diziyi yazıyor, modeli kendisi yapıyor; kırılan
  becerinin yapılandırılmış dönüşü ve üç kapılı suç atfı çalışmadı.
- **Hacim ile içerik ayrılmıyor.** Yörünge değişikliği kartın içeriğinden mi 125
  jeton fazladan metinden mi geldiği ayrılamıyor; ayrımı `irrelevant_retrieval`
  koşulu verir ve o koşul koşmadı.
- **Tek model, üç görev, kazanç iddiası yok.** Hiçbir epizot geçmedi ve geçmesi
  beklenmiyordu; ön koşul kapısı bu eksende ateşledi.
- **Kartın zarar verdiği bir çift var** (`0a9d82a_3`: kartsız 4 çağrı, kartlı 0) ve
  n=1 ile sebebi söylenemez.

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. `--cards` yolu, demo ölçümü, devam edebilirlik |
| Testi yazıldı | Evet. `tests/test_card_demo.py` 13 test; başarılı etki ayrımı, boşluk kısıtı, kısmi eşleşme, sıfır çağrılı epizot |
| Loglandı | `results/card-demo.json`; on epizot kayıtta, künyeleriyle |
| Belgesi yazıldı | K-91, ön kayıt madde 7 (dört yorum + beşinci), `docs/reports/uctan-uca-demo.md` |
| Hata durumu düşünüldü | Kart bulunamazsa koşu başlamıyor; blok girmezse betik düşüyor; kayıtlı epizot yeniden koşulmuyor; sorulamayan hâl ayrı sayılıyor |
| PR üzerinden gözden geçirildi | Hayır, önceki maddelerdeki sebeple: dal açılmadı. İnceleme rapor üzerinden |
| Temiz kurulumda baştan çalıştırıldı | Evet. Ölçüm kayıttan yeniden koşuluyor ve aynı sayıları veriyor; epizotlar üretim yürütücüsünden geçti |

### Kirli ağaç kapısının daraltılması burada işe yaradı

Demo saatler sürdü ve o sürede belgeler, ön kayıt ve demo betiği düzenlendi.
Kapı bütün ağaca bakıyor olsaydı her düzenleme koşan epizodu durduracaktı; liste
dışı olduğu için `working_tree()` "clean" kaldı ve koşu kesilmedi (K-76). Kararın
gerekçesi tam olarak buydu ve ilk kez burada denendi.

## #28 — PR akışı kural oldu, ve CI akışın bedelini gösterdi (S-49)

- Branch: `pr-akisi-kurali`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

Yol haritası maddesi **değil**: kuralın kendisini ve akışın bedelini yazıyor.
Dal `pr-akisi-kurali`.

## Ne değişti

**Protokole kural girdi, dört parçalı.** Her yol haritası maddesi kendi PR'ıyla
kapanıyor; kapanış notu PR açıklamasına giriyor; madde bitmeden PR açılmıyor ve PR
açılmadan sonraki maddeye geçilmiyor; dal adı çalışılan maddeyi taşıyor.

**S-49 yazıldı: kırk beş test CI'da hiç koşmamıştı.** Akış #19'dan sonra durunca
yedi madde tek dalda 52 commit olarak birikti ve dört CI kontrolü o commit'lerin
hiçbirini görmedi. İtildiğinde iki ortam farkı çıktı, ikisi de yerelde görünmez:

1. `route_table()` AppWorld'ün uygulama modüllerini okuyor; onlar `appworld install`
   ile geliyor, paketle değil. CI `appworld install` koşmuyor (K-32) ve ilgili
   testler `appworld` işaretini taşımıyordu — `test_api_routes` 16,
   `test_stopping_rule` 16, `test_shield_mount` 10, `test_compiler` 3.
2. `tests/test_shield_mount.py` sahte istekçiyi `tests.test_api_capture` üzerinden
   alıyor; depo kökünün sys.path'te olması çağırma biçimine bağlı. `python -m
   pytest` ekliyor, `pytest` betiği eklemiyor.

Düzeltmeler #20 ve #21 içinde birleşti. Bu PR onları **kayda geçiriyor**: sınırın
kalan kısmı da yazılı — o 45 test CI'da hâlâ koşmuyor, atlanıyor, ve kapanma yolu
CI'da `appworld install` koşturmak.

**Kapanış notları güncellendi.** Yedi maddenin "PR üzerinden gözden geçirildi"
satırı artık PR numarasını taşıyor; madde başına PR tablosu notların başına
eklendi; madde 1'in commit listesi düzeltildi — bir özet amend edilmiş bir
öncesine aitti ve üç commit listede yoktu.

## Geriye dönük bölmenin iki sınırı

`4d6a0ac` boşluk raporunu ve yazma kümesi türetmesini birlikte taşıyor; `5a21312`
karakter tavanını (madde 6) ve demo koşucusunu (madde 7) birlikte taşıyor. İkisi
de bölünemedi, çünkü bölmek commit'i ikiye ayırmak — tarihi yeniden yazmak —
olurdu, ve commit'lerin doğrusal kalması istendi. İkisi de ilgili PR
açıklamasında ve kapanış notlarında yazılı.

## Dört CI kontrolü

Yeşil. Ayrıca bu PR'dan önce sekiz PR'ın hepsi yerelde önceden doğrulandı: CI'ın
iki farkını taklit eden bir kanca (uygulama modüllerini reddeden import bulucusu +
betik biçiminde `pytest`) kurulup birleşme sırası adım adım koşuldu. Sekizinin
sekizi yerelde yeşil çıktı, sonra GitHub'da da yeşil çıktı.

## #29 — Madde 8 — Sandbox

- Branch: `madde-8-sandbox`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

## Madde 8 — Sandbox

**Durum: kapandı.** Kapsamı `docs/12-sandbox-kapsami.tr.md`, ölçümleri
`results/sandbox-olcum.json`, `results/transparency.json`,
`results/container-network.json`, `results/wire-identity.json`.

Ajanın ürettiği kod artık kök yetkisiz, ağsız, salt okunur kökte bir konteynerde
koşuyor; kayıt konteynerin dışındaki bir vekilden geliyor.

### Ne kuruldu

| Parça | Yer |
|---|---|
| İmaj | `Containerfile` — tam `appworld` paketi (K-B), kilit dosyasından, 643 MB; `data/` içeride değil, salt okunur bağlanıyor |
| Konteyner yaşam döngüsü | `src/zihin/sandbox.py` — epizot başına doğ, sınırları uygula, günlükleri `podman cp` ile al, yık |
| Kayıt vekili | `src/zihin/kayit_vekili.py` — iki yönü kaydeder, tipi rota imzasından türetir, kalkanı çağırır, yönetim rotalarını alan ölçütüyle süzer |
| Köprü | `src/zihin/soket_koprusu.py` — konteyner içindeki TCP portunu bağlanan unix sokete bağlıyor; stdlib, yeni bağımlılık yok |
| Konteyner girişi | `src/zihin/konteyner_girisi.py` — köprü + AppWorld'ün kendi ortam sunucusu, miras alınan tanımlayıcı üzerinde |
| Yapılandırma | `config/sandbox.yaml` — sınırlar, imaj damgası, ağ kipi, soket yolları |
| Kayıt şeması | Künyede dokuz sandbox alanı; `steps.state_hashes` (K-93) |
| Koşucu | `scripts/record_run.py --sandbox` |

**Topoloji: iki unix soket, iki yönde, ve konteynerin hiç ağı yok.** Konteyner →
host yönü salt okunur bağlanan soketle; host → konteyner yönü host'un bağlayıp
tanımlayıcısını `--preserve-fds` ile geçirdiği soketle. İkincisi konteynerin
dizine yazmasını gerektirmiyor, yani "yazılabilir bağlama yok" kuralı (K-94) ile
"host içeri ulaşabilsin" şartı çakışmıyor.

### Ne ölçüldü

**Şeffaflık testi — K-A'nın birinci şartı.** Üç kol, aynı görev, aynı yedi kod
bloğu; ölçüt ajanın gördüğü metnin tamamı:

| Kol | `sha256(environment_io.md)` |
|---|---|
| Süreç içi | `5e4812502f278f0b` |
| Sunulan, vekilsiz | `5e4812502f278f0b` |
| Sunulan + vekil | `5e4812502f278f0b` |

Üç kol, çünkü kip değişimi ile vekil aynı testte karışırsa çıkan fark
atfedilemez.

**Kimlik doğrulaması — K-92.** Kayıttaki 5261 eylemin **5261'i** imzadan
türetilen tiple eşleşiyor; imzaya bakmayan kontrol kolunda **1090'ı**
eşleşmiyor, ve o sayı bağımsız ölçülen "metin olmayan değer taşıyan GET"
sayısıyla birebir aynı.

**Ağ politikası — iki platformda.** `--network=none` sıfır erişim veriyor;
varsayılan netavark, `pasta` ve `slirp4netns` üçü de dış ağa çıkıyor (1.1.1.1
403 dönüyor, yani istek internete ulaşıyor). Salt okunur bağlanan sokete
`connect` çalışıyor — bu bir riskti, ölçüldü.

**Kaynak sınırları — K-C.** `6104387_1` konteynerde üç kez koşuldu, kullanım iki
saniyede bir örneklendi:

| | Ölçülen tepe | Sınır | Pay | Kullanım |
|---|---|---|---|---|
| Bellek | 158,0 MiB | 512 MiB | 3,2 kat | %29,4 |
| Süreç | 4 | 128 | 32 kat | %3 |
| tmpfs | ~32 KiB | 64 MiB | 2000 kat | %0,05 |
| CPU | %62,5 | 1 çekirdek | — | %62,5 |

**Hiçbiri bağlamadı** ve K-D'nin göstergesi bu: sınıra çarparak biten epizot
0/3. Ölçümün sınırı yazılı: tek görev, tek model, 20 adım, ve örnekleme aralığı
bir tepeyi kaçırabilir.

**Yönetim trafiği.** Ortam sunucusunun kendisi on bir yönetim çağrısı yapıyor.
Politika gerçek trafiğin 11'ini geçiriyor, kurcalanmış 12 denemenin 12'sini
kesiyor.

**S-50'nin kalan sınırı.** Ajan tetikli bir `/dbs/save` sondanın göreceği
değişiklikleri **tüketmiyor** (ölçüldü); `SO_PEERCRED` ayıramıyor çünkü ajanın
kodu konteynerde pid 1, yani ortam sunucusuyla aynı süreç; ve ajanın kodundan
çalışan bir yol bulunamadı (beş deneme, AppWorld'ün kendi guard'ı dördünü
kesiyor).

### Ölçüm sırasında bulunan kusurlar

Yedisi de "çalışıyor gibi görünüp yanlış sebeple çalışan" sınıfından ve altısı
bizim kendi kodumuzda.

| | Kusur | Etki |
|---|---|---|
| Kaydedici | Referans ajan `batch_execute` çağırıyor, `execute` değil; uzak kipte sarmalayıcı hiç ateşlemiyordu | Epizot koştu, 32 KB yörünge üretti, kayda **sıfır adım** yazdı ve sessiz kaldı (S-53) |
| Eylem kaynağı | `api_calls.jsonl` sandbox kipinde konteynerin içinde; yokluğu "sıfır çağrı" diye okunuyordu | Adımlar geldi, eylemler sıfır kaldı |
| Tanımlayıcı | `dup2(fd, 3)` ebeveynde yapılıyordu ve vekil önce başladığında onun soketini eziyordu | Hata vermeyen ama çalışmayan bir köprü |
| Kabuk | dash tek haneli olmayan tanımlayıcıyı `Bad fd number` ile reddediyor | Taşıma belirlenimci bir Python fırlatıcısına taşındı |
| Hazırlık denetimi | Yalnız "200 döndü mü" diye soruyordu | Yanlış portta host'un API sunucusu cevap verdi ve "ortam hazır" sanıldı |
| Köprü portu | Bir iş parçacığında bağlanıyordu, "port meşgul" yutuluyordu | Koşu artakalan bir sunucuya gitti |
| `podman cp` | Var olan dizine kopyalarken içine yerleştiriyor | Günlükler `logs/logs/` altına düştü |

Bir de birinci turdaki güvenlik ölçümünde üç adım yeşil yanıp hiçbir şey
kanıtlamıyordu (bellek `/dev/shm` varsayılanına çarpmış, tmpfs çıkış kodu
`tail`den gelmiş, loopback testinde host'ta dinleyici yok).

### Bilerek açık bırakılanlar

- **Konteynerin içi güvenli değil ve olması amaçlanmıyor** (S-51). Ortam sunucusu
  ajanın koduyla aynı süreç; bu K-B'nin doğrudan sonucu. Korunan şey host.
- **`error_class` sandbox kipinde NULL** (S-52). Telde istisna yok. Alan zaten
  durum kodundan bire bir türetilebiliyordu; uydurulmadı.
- **Durum sondasının kör noktası ileriye dönük kapandı** (S-54). Mevcut kütüphane
  ve indeks eski sondayla madenlendi.
- **Kalkanın uygulama kipi hâlâ yok** (K-71). Vekilin rota filtresi ondan ayrı
  bir katman.

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. İmaj, konteyner yaşam döngüsü, vekil, köprü, giriş noktası, yapılandırma, şema alanları, koşucu bayrağı |
| Testi yazıldı | Evet. 55 yeni test: `test_sandbox_security.py` 11 (hepsi iki kollu), `test_kayit_vekili.py` 33, `test_sandbox_config.py` 11 |
| Loglandı | `results/sandbox-olcum.json`, `transparency.json`, `container-network.json`, `wire-identity.json`; epizot 118 kayıtta, künyesinde sandbox alanları dolu |
| Belgesi yazıldı | K-92…K-98, `docs/12-sandbox-kapsami.tr.md` (+ İngilizce eşi), tehdit modeli güncellemesi, S-50…S-54 |
| Hata durumu düşünüldü | Kimlik teyidi (K-98); port meşgulse koşu düşüyor; imaj yoksa düşüyor; kaydedici takılmamışsa epizot satırı yazılmıyor; reddedilen istek sesli |
| PR üzerinden gözden geçirildi | **Evet, PR #29.** Açıklaması bu kapanış notu; beş CI kontrolü yeşil |
| Temiz kurulumda baştan çalıştırıldı | Kısmen. Güvenlik testleri ve ağ ölçümü CI'da temiz makinede koşuyor (beşinci kontrol). Uçtan uca epizot yerelde koştu: CI'da `appworld install` ve 198 MB veri yok |

### Bu maddede kayda geçen genel kural

**Bir koşu, başlattığı şeyle konuştuğunu doğrulamadan sayılmaz** (K-98).
Artakalan bir durum bu depoda üç kez yanlış yeşil üretti: mutasyon betiği kirli
zeminde koştu, doğrulama aleti bayat dosya okudu, ve burada konteyner hiç
başlamadığı hâlde epizot artakalan bir sunucuya koşup temiz göründü.

## #30 — CI simülasyonu depoya girdi, ve test işaretleri bağımlılığa bağlandı

- Branch: `ci-simulasyonu`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

kontrol: CI simülasyonu depoya girdi, ve test işaretleri bağımlılığa bağlandı

Aynı yerde iki kez tökezledik ve sebebi ikisinde de aynıydı.

S-49'da kırk beş test CI'da kırıldı çünkü gereksinimleri işaretlerinde
yazmıyordu. O turda CI ortamını yerelde yeniden üreten bir simülasyon elle
kuruldu, iki arızayı da yakaladı, ve iş bitince silindi. Madde 8'de iki sandbox
testi aynı sınıftan bir sebeple beşinci kontrolü kırmızı yaktı: `specs.json`
okuyor ve uygulama modüllerini istiyorlardı, ama "sandbox hakkında" oldukları
için yalnız `sandbox` işareti taşıyorlardı.

İKİ KURAL (K-99, protokol §6)

1. Bir testin işaretleri konusuna göre değil bağımlılıklarına göre belirlenir.
   İşaret bir etiket değil, bir sözleşme: "bu test şu olmadan koşamaz".
2. Bir arızayı yakalamak için kurulan kontrol depoya girer ve standart ön
   kontrolden çağrılır. Geçici kurulup silinen kontrol kurulmamış sayılır.

SİMÜLASYON

`scripts/ci_simulasyonu.sh`, `scripts/local_checks.sh` içinden çağrılıyor. Üç
farkı taklit ediyor ve üçü de ölçülmüş arızalardan geliyor: `data/` yok,
uygulama modülleri yok (`appworld install` koşmamış), ve `pytest` betiği
çağrılıyor — `python -m pytest` değil, sys.path farkı. CI'ın iki test işinin
koştuğu seçimlerin aynısını koşuyor.

Taklit etmediği şey de yazılı: temiz bir `uv sync`. Bir bağımlılık arızası
buradan görünmez, CI'ın kendi işinden görünür.

KONTROLÜN KENDİSİ ATEŞLEDİĞİ GÖRÜLEREK KABUL EDİLDİ

İlk hâli çalışma dizinini `git worktree add HEAD` ile kuruyordu ve commit
edilmemiş değişikliği hiç görmüyordu. Sınadım: işareti kaldırıp koştuğumda
yeşil yandı. Yani kontrol kurulduğu ilk hâliyle tam olarak yakalaması gereken
şeyi kaçırıyordu.

Çalışma ağacından kurulan hâliyle — izlenen dosyalar artı gitignore dışındaki
izlenmeyenler — aynı deneme kırmızı yanıyor:

    FAILED test_the_proxy_refuses_a_management_write_to_an_arbitrary_path
    SONUÇ: CI SİMÜLASYONU DÜŞTÜ

İşaret geri konduğunda yeşil. Bir kontrolün yeşil yanması, doğru şeye bakarak
yandığı anlamına gelmiyor (K-49).

## #31 — CI appworld kurulumu ve verisi, önbellekli

- Branch: `ci-appworld-install`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

## CI'a `appworld install` ve verisi girdi

Kırk beş test CI'da hiç koşmuyordu (S-49). O turun çözümü testleri işaretleyip
elemekti: gereksinim görünür oldu ama kapsama kapanmadı ve yedi kapanış notunun
"temiz kurulumda baştan çalıştırıldı" satırı eksik kaldı. Bu PR onu kapatıyor.

### Ölçüm — bedeli bilerek ödendi, sayısı burada

Sayılar `results/ci-kapsam.json` içinde. İki koşunun ölçümü, kestirim değil.

| | Önce | Sonra |
|---|---|---|
| Testler: geçen | 356 | **435** |
| Testler: atlanan | 47 | **7** |
| Testler: elenen | 58 | 19 |
| Sandbox: geçen | 9 | **11** |
| **Toplam koşan** | **365** | **446** |
| Testler işi | 53 s | 53 s |
| Sandbox işi | 66 s | 92 s |
| **Duvar saati (en uzun iş)** | **66 s** | **92 s** |

Kurulum adımı 9,6 s (Testler) ve 10,0 s (Sandbox). Testler işinin toplam süresi
değişmedi çünkü pytest adımı 33,0 s'den 17,3 s'ye indi — beklenmedik ve tek
koşudan, koşucu değişkenliği olabilir. Net bedel duvar saatinde **26 saniye**.

Veri dizini önbellekte; anahtar sabitlenmiş AppWorld commit'i taşıyor.

### Kurulumun başarılı olması yetmez: koştuğu doğrulandı

İşaretler ya da kancalar hâlâ dışlıyor olsaydı kurulum boşa giderdi ve bunu
hiçbir şey söylemezdi. Ayrı bir adım üç şeye bakıyor:

- "kurulu AppWorld uygulama modülleri yok" gerekçesiyle atlanan test kaldı mı →
  **0**
- `appworld` işaretli testler toplanıyor mu → sıfırdan büyük
- rota tablosu kuruluyor mu → **12 uygulama**

### Kalan yedi atlama yapısal

| Test | Sebep |
|---|---|
| `test_api_routes.py:198` | `experiments/outputs` bu makinede yok |
| `test_recorded_run.py` (5 test) | `results/zihin.sqlite` yok; kayıtlı koşu gerektiriyor |
| `test_shield.py:267` | `results/write-set-static.json` yok |

Üçü de üretilmiş artefaktlara bağlı ve o dizinler bilerek gitignore'da: kod ile
sonuç aynı commit'i paylaşmıyor. Gizlenmiş bir arıza değil, tasarımın sonucu.

### Yan sonuç: simülasyon da değişti

`ci_simulasyonu.sh` artık uygulama modüllerinin yokluğunu taklit etmiyor —
olmayan bir makineyi taklit etmek yanlış kırmızı üretirdi. Kalan iki farkı
taklit ediyor: temiz checkout ve `pytest` betiğinin sys.path'i.

### Yedi DoD satırı güncellendi

Altısına "CI artık `appworld install` ve veriyi kuruyor" eki girdi. Madde 8'in
satırı açıkça "CI'da `appworld install` ve 198 MB veri yok" diyordu; artık
yanlış olduğu için yeniden yazıldı. Madde 2'nin "Uygulanmaz" satırına
dokunulmadı: koşulacak bir şey yok.

Karar kaydı K-100.

## #32 — Kaydedicinin montaj noktası çivilendi (S-53)

- Branch: `kaydedici-montaj-testi`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

Bütün projenin kaydı, hiç bilmediğimiz bir uygulama detayının üstünde durmuş: referans ajan **batch_execute** çağırıyor, **execute** değil. Süreç içi kipte batch_execute her kod için self.execute çağırdığı için execute sarmalamak yetiyordu; tesadüf tuttuğu sürece kimse fark etmedi. Uzak kipte tesadüf bozuldu ve epizot 32 KB yörünge üretip kayda sıfır adım yazdı (S-53).

Yedi test sahte bir dünya nesnesiyle iki kipin de sarmalandığını çiviliyor. AppWorld kurulumu, konteyner ve model gerekmiyor.

Mutasyonla sınandı:

| Mutasyon | Düşen test |
|---|---|
| Uzak kipte batch_execute sarmalanmıyor | 3 |
| Süreç içi kipte execute sarmalanmıyor | 2 |
| Geri alındı | 0, yedisi de geçiyor |

İkinci kat arıza da çivili: yakalanan çağrının adımın eylemlerine geçtiği sınanıyor — ikinci kaynağın yokluğu bir süre sıfır çağrı diye okunuyordu.

Takım 453 → 460 geçen.

## #33 — Yazı işi: ön kayıt gövdesi, deney matrisi, veri modeli, yanlışlama kapıları

- Branch: `yazi-isi`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

Dört belge yer tutucudan çıktı.

**experiments/preregistration.md** — Bölüm A olarak deneyin kendi ön kaydı eklendi: hipotez ve iki araştırma sorusu, birincil hücrenin tanımı, estimand ve sansürün iki ayrı nicelik olduğu, altı koşul ve çıkarıcı kontrol, metrikler, ön koşul kapısı ateşleme tarihiyle, üç yanlışlama kapısı, mekanizma başına terk kriteri, ayar bütçesi ve değişiklik türü taksonomisi, bölme kullanımı ve dokunulan görevler, ölçek ekseni yorum tablosu. Kurulum fazının madde kayıtları Bölüm B olarak olduğu yerde duruyor; sonuç bölümlerine dokunulmadı.

**experiments/experiment-matrix.csv** — 54 satır: 6 koşul x 3 model x 3 tohum. Koşulamayan hücreler boş değil, sebebiyle işaretli: 36 satır alakasız kart havuzu ya da naif derleyici olmadığı için koşulamaz, 18 satır ön koşul kapısı ateşlediği için bekliyor.

**DATA_MODEL.md** — tablo envanteri, silme testi, PROJECTION_TABLES kuralı ve künye sözleşmesinin zorunlu alanları eklendi. Yazarken iki bölüm eskimiş çıktı ve düzeltildi: result_status artık doluyor (S-16 kapandı), ve sarmalanan metot kipe göre değişiyor (S-53).

**docs/11-falsification.md** — şablondan çıktı: altı kapı (Y-1..Y-6) artı ön koşul kapısı, her biri iddia / yanlışlayan gözlem / ne zaman / sonuç biçiminde.

Eksik kalan tek şey: docs/10-external-review.tr.md dosya olarak verilmedi. Ön kaydın A.12 bölümü ona atıf verecek biçimde bırakıldı.

## #34 — Sunum iskeleti ve teknik olgular

- Branch: `sunum-iskeleti`
- Merged: 2026-08-17

<!-- body, verbatim except for task text -->

İki belge.

**docs/reports/sunum-iskeleti.md** — sunum bir kapsama testi olarak kuruldu: 28 iddia, her birinin yanında atıf yuvası. Sonuç:

| Katman | İddia | Atfı olan | Boş |
|---|---|---|---|
| Problem ve tasarım | 4 | 4 | 0 |
| Kurulan mekanizmalar | 7 | 7 | 0 |
| Ölçüm altyapısı | 6 | 6 | 0 |
| **Nedensel iddialar** | **6** | **0** | **6** |
| Sınırlamalar | 5 | 5 | 0 |

Boş yuvaların hepsi tek katmanda toplandı ve bu tesadüf değil: nedensel katmanın tamamı boş, çünkü ön koşul kapısı ateşledi. Slayt sırası önerisi kapı ateşlemesini sona bırakmıyor — sona bırakmak dinleyiciye sonucu olan bir çalışma izlenimi verip sonunda geri almak olurdu.

**docs/reports/teknik-olgular.md** — CV değil; CVyi besleyecek teknik olgular. Ne kuruldu, atıf verilebilir ölçümler, ve **kurulamayan cümleler** tablosu (beş cümle, her biri ölçülmüş bir sebeple).

Yazarken iki sayı yanlış çıktı ve düzeltildi: satır sayısı ve sınırlama kaydı sayısı. Kaynaktan doğrulandı.

## #35 — dil: kod, yorum ve calisma zamani metinleri Ingilizce

- Branch: `dil-ingilizce`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

Kod, yorum, docstring ve çalışma zamanı metinleri İngilizceye çevrildi. Md dosyaları
kapsam dışı: onlar iki dilli kalıyor (`.tr.md` kaynak, `.en.md` çeviri).

## Ne değişti

| Katman | Durum |
|---|---|
| `src/zihin/` (10 dosya) | düzyazı, dizge ve tanımlayıcılar İngilizce |
| `tests/` (26 dosya) | aynı |
| `scripts/` (25 dosya) | aynı |
| Modül adları | üç modül ve bir test dosyası yeniden adlandırıldı |

Çeviri iki ayrı commit ailesine bölündü, çünkü doğrulamaları farklı:

- **Düzyazı ve dizge commit'leri** (`f15541f` … `acef1d8` öncesi). Hiçbir yapı
  değişmedi.
- **Tanımlayıcı ve modül adı commit'i** (`acef1d8`). Hiçbir dize değişmedi, tek
  istisna aşağıda.

## Doğrulama

**Düzyazı commit'leri.** `main` ile AST karşılaştırması, docstring'ler soyulmuş:
47 dosyada 854 AST satırı değişti, **854'ü de `Constant(value=...)`**. Yapısal
değişiklik sıfır.

**Tanımlayıcı commit'i.** Yeniden adlandırma haritası eski ağaca uygulanıp yeni
ağaçla karşılaştırıldı, dizgeler iki tarafta da boşaltılmış: **82 dosyanın
81'i harita altında birebir aynı.** Kalan bir dosyada üç AST satırı ayrışıyor ve
sebebi tek: `records.py`'deki bir hata mesajında Türkçe `geldi` sözcüğü sona
yazılıydı, İngilizcede `got` başa geçti, yani f-string'in son `Constant` parçası
kayboldu. Mesajın kendisi dışında hiçbir şey değişmedi.

Doğrulama betikleri kalıcı değil; ikisi de tek seferlik ve depoya girmiyor.

**Takım.** 471 geçti, 8 atlandı. `ruff check`: temiz. `ruff format --check`: 83
dosya biçimli.

## K-102: eklenen modül adları ve yeni public tanımlayıcılar

**Yeni dosya.**

- `tests/test_decision_record.py`

**Yeniden adlandırılan modüller.**

| Eski | Yeni |
|---|---|
| `src/zihin/kayit_vekili.py` | `src/zihin/recording_proxy.py` |
| `src/zihin/konteyner_girisi.py` | `src/zihin/container_entry.py` |
| `src/zihin/soket_koprusu.py` | `src/zihin/socket_bridge.py` |
| `tests/test_kayit_vekili.py` | `tests/test_recording_proxy.py` |

**`src/` içindeki public tanımlayıcı değişiklikleri** (modül düzeyi ve sınıf
üyeleri):

| Eski | Yeni |
|---|---|
| `records.ZORUNLU_KUNYE_ALANLARI` | `records.REQUIRED_MANIFEST_FIELDS` |
| `records.YERELE_OZGU_KUNYE_ALANLARI` | `records.LOCAL_ONLY_MANIFEST_FIELDS` |
| `records.KUNYE_KISITLARI` | `records.MANIFEST_CONSTRAINTS` |
| `RouteClass.UYGULAMA` | `RouteClass.APP` |
| `RouteClass.YONETIM` | `RouteClass.MANAGEMENT` |
| `RouteClass.BILINMEYEN` | `RouteClass.UNKNOWN` |

**`scripts/build_decisions_csv.py` içindeki yeni public adlar.**

`check_heading_schema`, `all_records`, `RATIONALE_HEADING`, `HEADING`,
`FIRST_WORD`, `STRUCTURAL_STEMS`, `WITHOUT_DECISION_HEADING`, `STEM_FOLDS`.

Yerel değişken ve test yardımcısı adları listeye girmiyor; toplam harita 139 ad
taşıyor ve tamamı `acef1d8` içinde.

## Türkçe kalan üç yer, ve sınırın kuralı

Kural şu: **diskte duran bir veriyi adlandıran dize değişmiyor; insanın okuduğu
metin değişiyor.**

1. `scripts/build_decisions_csv.py` (23 satır). Türkçe karar belgesini eşleyen
   düzenli ifadeler ve onları alıntılayan docstring satırları. İngilizceye
   çevrilirse CSV sessizce boşalır.

2. `scripts/setup/measure_card_demo.py` (6 satır). `"kartlı"` ve `"taban"`
   sözlük anahtarları ile `demo-<görev>-kart-…` koşu kimliği parçaları. İkisi de
   `results/card-demo.json` içinde ve `record.sqlite`'ta yazılı; demonun üçüncü
   kolu bu dosyayı genişletecek, yani anahtarları değiştirmek kolları
   karşılaştırılamaz kılardı.

3. `tests/test_decision_record.py` (16 satır). Türkçe karar belgesini sınayan
   testlerin Türkçe örnekleri.

Aynı kural gereği şunlar da olduğu gibi kaldı: `results/` altındaki ölçüm
dosyalarının Türkçe JSON anahtarları (`yakalanan_cagri`, `adim_kategorileri`,
`olcumler`, `kosu_esigi`, `ornek_sayisi`), `asama-2-olcum` gibi deney önekleri,
ve `bant3` / `sinir3` gibi kayıtta duran koşu önekleri.

Konteyner içi yollar bu sınıfa girmiyor — her koşuda yeniden yaratılıyorlar — ve
çevrildi: `/kopru` → `/bridge`, `/gizli` → `/secret`, podman ağı `ortam-koprusu`
→ `environment-bridge`.

## Yol boyunca bulunan iki arıza

**`conftest.py`'nin atlama mesajı CI tarafından grep'leniyordu.** `.github/workflows/ci.yml`
adımı tam olarak "AppWorld kurulumu boşa mı gitti" kontrolü. Mesaj tek başına
çevrilseydi kontrol hiçbir şey yakalamadan yeşil kalırdı. İkisi aynı commit'te
değişti.

**Bir testin geçersiz verisi çevrilince geçerli oldu.** `test_model_load_state_is_constrained`
`"ılık"` değeriyle `CHECK (model_load_state IN ('cold','warm','unknown'))`
kısıtını sınıyordu. Düz çeviri `"warm"` yapardı ve kısıt hiç ateşlemezdi; değer
`"lukewarm"` oldu.

## Karar kaydına eklenen üç madde

**K-101 — aile taraması iptal.** #22 kapatıldı, eksen Qwen2.5-Coder olarak
kalıyor. `docs/reports/model-ailesi-taramasi.md` yalnız `origin/model-ailesi`
dalında duruyordu; main'e alındı, başına iptal notu düşülerek. Ölçüm, ait olduğu
karar iptal edildi diye geçersizleşmiyor.

**K-102 — PR raporu yeni modül adlarını ve public tanımlayıcıları listeliyor.**
Yukarıdaki bölüm bu maddenin ilk uygulanışı. Maddenin kendi sınırı yazılı: bu bir
koruma değil görünürlük kuralı.

**K-103 — karar girdilerinin başlık kümesi şemaya karşı doğrulanıyor.** K-102
yazılırken başlık `**Gerekçe ölçüldü.**` konmuştu; ayrıştırıcı `**Gerekçe.**`
dizgesinde bölüyordu, tutmadı, ve CSV gerekçe özeti olarak "Karar." taşıdı.
Testler yeşildi.

Düzeltme tek başlığa özel değil. Gerekçe başlığı artık **aile** olarak
ayrıştırılıyor (`Gerekçe` ve `Sebep` ile başlayan her başlık), ve `check_heading_schema`
her girdinin başlık kümesini şemaya karşı doğruluyor: her `K-` girdisi bir
`Karar` başlığı taşıyacak (üç kayıtlı istisnayla), ve diakritikler kalkınca
yapısal bir kökün üstüne düşen hiçbir başlık o kök gibi yazılmamış olmayacak.

**Ölçüm.** Aile ayrıştırması on yedi kaydın gerekçe özetini düzeltti; hepsi
"Karar." yazıyordu. Geri düşüş kuralı ilk başlığı atlayacak şekilde düzeltilince
on üç kayıt daha düzeldi. Yani sessiz yanlış satır sınıfının K-102'den önce
otuz örneği vardı ve hiçbir şey itiraz etmemişti. Yeni `tests/test_decision_record.py`
on bir testle bunu CI kapısına bağlıyor.

## Bu PR'ın kapsamadığı

Md dosyalarının çevirisi, ve dördüncü maddedeki temizlik kalemleri
(`origin/tasarim-katmani` ve `sim2` dallarının kapatılması, `pyproject.toml:76`
yorumunun düzeltilmesi, `docs/10-external-review.md`'nin değiştirilmesi).

## #36 — dil: diakritiksiz Turkce artigi, ve dil denetimi depoya girdi

- Branch: `dil-artigi`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

İlk dil PR'ının tarayıcısı diakritik arıyordu. Diakritiksiz Türkçe elekten geçti
ve birleşmeden sonra bulundu: `kart: 1 beceri, 1 hata; slota giren 1+1, 457
karakter` hâlâ basılıyordu. Bu PR artığı temizliyor ve tarayıcıyı depoya sokuyor.

## Tarayıcı: `scripts/check_language.py`

Ölçüt diakritik değil, **sözcük**. Karşılaştırma diakritikleri soyulmuş biçimde
yapılıyor, yani `Gerekçe` ile `Gerekce` bu tarayıcı için aynı belirteç.

**Hangi Türkçenin kalmasına izin verildiği makineyle belirleniyor.** Bir dize
kayıtta ya da `results/` altında geçiyorsa arayüzdür; çevirmek onu farklı bir
dize yapar, yazılmış veriyle bağını koparır ve devam korumasını bozar. Tarayıcı
`results/`, `experiments/` ve `docs/` altındaki dosya adlarını, o dizinlerdeki
JSON anahtarlarını ve boşluksuz değerlerini, ve `results/*.sqlite` içindeki sütun
adlarıyla boşluksuz hücre değerlerini topluyor — **10.015 dize**. Bir aday bu
kümedeyse, kümedeki bir üyenin baş parçasıysa (`bant3` → `bant3-g1-g1-7b`), ya da
aynı önek ailesindense (`sinir2` → `sinir3-…`) veri sayılıyor.

Düzyazı değerler kümeye girmiyor: ayırt edici boşluk. Bir `results` dosyasındaki
Türkçe açıklama cümlesi aksi hâlde içindeki her sözcüğü veri gibi gösterirdi.

**`scripts/local_checks.sh` içinden çağrılıyor**, 3/3 adım olarak. Gerekçe
betikte yazılı: bir kereye mahsus kurulan kontrol kurulmamış kontroldür (K-99).
Bu maddenin kendisi o kuralın ikinci ölçülmüş örneği.

**Sınırı yazılı.** Sözcük dağarcığı sabit bir liste; henüz kullanılmamış bir
Türkçe sözcük bu tarayıcıya görünmez. Yakaladığı şey bu deponun gerçekten yazdığı
sözcükler, ki iki ölçülmüş kaçak da onlardan yapılmıştı.

## Ölçüm

Tarayıcı ilk koşusunda **326** bulgu verdi. Bunun bir kısmı tarayıcının kendi
hatasıydı ve düzeltildi: `slot` İngilizce bir sözcük ve dağarcıkta işi yoktu
(−160); düzyazının içinde anılan veri adları maskelenmeliydi (`sinir3-32616b5_1`
demek Türkçe yazmak değil). Gerçek artık **151**'di ve beş turda sıfıra indi.

| tur | kalan |
|---|---|
| ilk ölçüm | 151 |
| adlar + ilk dize kümesi | 62 |
| korpus genişletildi, dördüncü tur | 33 |
| beşinci tur | 10 |
| son | **0** |

Çevrilen kalemler: 8 Türkçe yorum, ~60 çalışma zamanı dizesi, 23 tanımlayıcı
(`izinli`→`allowed`, `istek`→`request`, `kart`→`card`, `jeton`→`token`,
`medyan`→`median`, `pencere`→`window`, `yorunge`→`trajectory` ve diğerleri), ve
**on ortam değişkeni**: `ZIHIN_CARPAN`→`ZIHIN_MULTIPLIER`,
`ZIHIN_TABAN_TAVAN`→`ZIHIN_FLOOR_CEILING`,
`ZIHIN_TAVAN_SINIRI`→`ZIHIN_CEILING_LIMIT`, `ZIHIN_CIKTI`→`ZIHIN_OUTPUT`,
`ZIHIN_GIRDI_MALIYETI`→`ZIHIN_INPUT_COST`,
`ZIHIN_CIKTI_MALIYETI`→`ZIHIN_OUTPUT_COST`,
`ZIHIN_BANT_BASINA`→`ZIHIN_PER_BAND`, `ZIHIN_TARAMA`→`ZIHIN_SCAN`,
`ZIHIN_GOREVLER`→`ZIHIN_TASKS`, `ZIHIN_ADET`→`ZIHIN_COUNT`. Bunlar kayıtta hiç
geçmiyor (`os_environment` sütununda arandı, yok), yani ölçüte göre düzyazı.
`docs/reports/hizalama-denetimi.md`'deki listesi aynı commit'te güncellendi.

## Doğrulama

**AST karşılaştırması, `main` ile.** 34 dosyada 320 AST satırı değişti; 252'si
`Constant`, 68'i tanımlayıcı. Tanımlayıcılar için ikinci ölçüt koşuldu: 23 adlık
yeniden adlandırma haritası eski ağaca uygulanınca **82 dosyanın 82'si** yeni
ağaçla birebir aynı. Yani 68 satırın tamamı haritanın kendisi, yapısal değişiklik
sıfır.

**Şeffaflık özeti.** `6104387_1`, süreç içi kol: `5e4812502f278f0b`, 5291 bayt —
kayıtlı değerin aynısı.

**Takım.** 471 geçti, 8 atlandı. ruff temiz. `check_language.py`: 0.

## Bu turda kendi kırdığım şey

`measure_transparency.py`'deki sabit kod dizisi `sifreler`, `hesap`, `jeton`
değişkenlerini kullanıyor. Toplu değiştirme bunlara da dokundu ve dizi bozuldu:
`hesap['password']` ile `jeton[:8]` tanımsız kaldı, dizi erken düştü, ve
şeffaflık özeti `5e4812502f278f0b`/5291 bayt yerine `b60ad2838ae96f4a`/4071 bayt
verdi. Yani **birleşme sonrası karşılaştırılabilirlik kapısının referansını
kırmıştım** ve bunu ancak kapıyı yeniden koşarken gördüm.

Dizi `main`'deki baytlarına geri alındı ve özet tekrar tuttu. Üstüne iki koruma
kondu: dosyada baytların donmuş olduğunu söyleyen bir yorum, ve
`check_language.py` içinde o satır aralığını adıyla muaf tutan `SUBJECT_LINES`
girdisi — gerekçesiyle birlikte, çünkü korpus testi bir dizenin **sonucunu**
göremiyor. Kaydedilmiş bir özet, onu üreten baytların da arayüz olduğu anlamına
geliyor; bu, veri kuralının ağaçtaki en güçlü örneği.

Aynı sınıftan üç test de kırıldı ve düzeltildi: kabuk komutu ile iddiası ayrı
değiştirilmişti (`echo wrote` ile `assert "yazdi"`, `echo cikis:$?` ile
`assert "exit:0"`, `:/dis:rw` ile `touch /outside/trace`). Üçü de aynı commit'te
hizalandı.

## Türkçe kalan üç dosya, ve neden

`SUBJECT_FILES` üç dosya taşıyor ve üçünde de Türkçe **konu**, araç değil:

1. `scripts/build_decisions_csv.py` — Türkçe karar belgesini eşleyen düzenli
   ifadeler.
2. `tests/test_decision_record.py` — o belgeyi sınayan testlerin Türkçe örnekleri.
3. `scripts/check_language.py` — sözcük dağarcığı Türkçe sözcüklerden oluşuyor;
   kendini işaretleyen bir tarayıcı yeşil tutulamazdı.

## K-102: eklenen modül adları ve yeni public tanımlayıcılar

**Yeni dosya.** `scripts/check_language.py`.

**Yeni public adlar** (hepsi o dosyada): `VOCABULARY`, `REPOSITORY`,
`SUBJECT_FILES`, `SUBJECT_LINES`, `WORD`, `FAMILY`, `CAMEL`, `STEMS`, `fold`,
`turkish_words`, `mask_data`, `data_corpus`, `is_data`, `scan`, `main`.

**Yeniden adlandırılan public tanımlayıcı yok**; 23 adın tamamı yerel değişken,
argüman ya da modül düzeyi sabit ve `src/` içindeki public yüzey değişmedi.

## #37 — olcum: uc kollu kart kosusu (45 epizot), ve demo iddiasinin geri cekilmesi

- Branch: `uc-kol`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

# Üç kollu kart koşusu — 45 epizot, tek commit

**Gösterimsel, istatistiksel değil.** Beş görev ve üç tekrar ayırt edici güç
vermiyor. Bu koşu bir kazanç iddiası taşımıyor; taşıdığı tek şey, demonun
iddiasının tekrar altında ayakta kalıp kalmadığı.

Sayılar `results/card-arms.json` içinde. Koşu öneki `uckol`, commit `9a42ac4`,
model `qwen2.5-coder:7b-instruct-q4_K_M`, hepsi aynı commit'te. Yorum
`experiments/setup-protocol.md` §12'de **koşudan önce** ilan edildi.

## 1. Görev başına, kol başına, tekrar başına

`geçti/adım/sonlanma`. Kırk beş epizodun **hiçbiri görevi geçmedi.**

| görev | kol | r0 | r1 | r2 |
|---|---|---|---|---|
| `0de03ea_1` | cards | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| | baseline | fail/20/ceiling | fail/4/finished | fail/11/finished |
| | irrelevant | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| `1150ed6_2` | cards | fail/9/finished | fail/20/ceiling | fail/20/ceiling |
| | baseline | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| | irrelevant | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| `0a9d82a_1` | cards | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| | baseline | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| | irrelevant | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| `0a9d82a_2` | cards | fail/11/finished | fail/20/ceiling | fail/20/ceiling |
| | baseline | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| | irrelevant | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| `0a9d82a_3` | cards | fail/20/ceiling | fail/8/finished | fail/20/ceiling |
| | baseline | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| | irrelevant | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |

Kolların birbirinden gerçekten farklı olduğu künyeden okunuyor: aynı görevde üç
kolun `instruction_file_digest` değeri üç ayrı değer (`a4c24f4b…` / `c41f7852…` /
`dc4cf77a…`).

## 2. Demonun kendi ölçütü: etkiye ulaşma

Görev geçme ölçütü sıfır olduğu için asıl karşılaştırma demonun kullandığı ölçüt:
kartın etki soneki (`POST <uygulama>.auth/token`) epizotta geçti mi, ve **2xx ile
mi** geçti.

Üç tekrarın kaçında başarılı etkiye ulaşıldı:

| görev | cards | baseline | irrelevant |
|---|---|---|---|
| `0de03ea_1` | 2/3 | 2/3 | 2/3 |
| `1150ed6_2` | 2/3 | 0/3 | 0/3 |
| `0a9d82a_1` | 1/3 | 1/3 | 1/3 |
| `0a9d82a_2` | 1/3 | 2/3 | 0/3 |
| `0a9d82a_3` | 1/3 | 1/3 | 0/3 |
| **toplam** | **7/15** | **6/15** | **3/15** |

## 3. Kararlılık — önceden ilan edilen kurala göre

Bir hücre, üç tekrarı da aynı cevabı veriyorsa kararlı. Demonun ölçütünde:

**Üç tekrarın uyuştuğu hücre: 4/15. Ayrıştığı: 11/15.**

Protokol §12.3 şunu yazıyordu: *"Çoğunda ayrışıyorsa demonun 'kartlı 2 çift,
kartsız 0' iddiası desteklenmiyor ve geri çekilir."*

**On beş hücrenin on biri ayrışıyor. İddia geri çekiliyor.**

Geri çekilen tam olarak şu: demonun tek epizotluk kollarında kartlı kol iki
çiftte başarılı etkiye ulaşmış, kartsız kol hiçbirinde ulaşmamıştı. Üç tekrarda
kartsız kol 15 hücrenin 6'sında başarılı etkiye ulaşıyor. Tek epizot, kolları
ayırmıyordu; ayırdığını sandığımız şey gürültüydü.

## 4. Kol karşılaştırması

Önceden ilan edilen tablo üç sonuç öngörüyordu: alakasız kol kartlıya yakınsa
etki hacim ve biçimden, kartsıza yakınsa içerikten, arada kalırsa n=5'te
yorumlanamaz.

Çıkan desen üçüne de uymuyor: **alakasız kol her ikisinin de altında**
(3/15 karşı 7/15 ve 6/15). Kartlı ile kartsız arasında ise fark yok denecek
kadar az (7 karşı 6).

On beş hücrenin on biri kararsızken bu farkların hiçbiri yorumlanamaz. Doğru
ifade şu: **bu düzenekte üç kol birbirinden ayrılmıyor, ve ayrılmama sebebi
gürültü tabanının kolların arasındaki farktan büyük olması.**

Alakasız kolun düşük çıkması bir "kart zararlı" bulgusu **değil**; 3/15 ile 6/15
arasındaki fark, aynı hücrede üç tekrarın kendi arasında ayrıştığı bir düzenekte
gürültünün içinde kalıyor.

## 5. Alakasız kolun sınırı — koşmadan önce yazılmıştı

`experiments/setup-protocol.md` §12.2'de ölçülerek yazıldı: kütüphanedeki dört
becerinin dördünün de etki soneki bir `auth/token` POST'u, ve gövdeler aynı
iskeleti taşıyor. Başka uygulamadan gelen kart da aynı dersi veriyor.

Dolayısıyla bu kütüphanede alakasız kontrol **içerik ile şablonu ayıramaz**;
ayırdığı tek şey kart biçimli metin ile kart biçimli olmayan metin. Bu koşu o
sınırı değiştirmiyor, ve zaten değiştiremezdi.

Ek bir homojenlik koşarken ölçüldü: beş görev yalnız iki uygulamaya değiyor
(`spotify` ×2, `simple_note` ×3), yani beş görev beş bağımsız deneme değil.

## 6. Ne öğrenildi

1. **Tek epizotluk kol karşılaştırması bu modelde bilgi taşımıyor.** Gürültü
   tabanı sıfır değil ve kolların arasındaki farktan büyük.
2. **Demonun kartlı/kartsız iddiası geri çekildi.** Kayıt silinmiyor; epizotlar
   eski commit ölçümü olarak yerinde duruyor.
3. **Kütüphane içerik atfı için fazla homojen.** Bu, koşudan önce yazılmış
   beklentinin gerçekleşmesi; bir başarısızlık değil, ölçülmüş bir sonuç.
4. Bir sonraki turda kart mekanizması hakkında bir şey söylenecekse, önce
   yapısal olarak farklı beceriler taşıyan bir korpus, sonra hücre başına üçten
   fazla tekrar gerekiyor.

## #38 — hasar kapsami: geri cekmenin siniri, dorduncu dal kurali, dis inceleme kaydi

- Branch: `hasar-kapsami`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

Üç kollu koşunun sonucu bir geri çekme içerdi. Bu PR o geri çekmenin
**kapsamını** yazıyor, kuralı genelliyor, ve dış inceleme kaydını yerine
koyuyor.

## 1. Dördüncü dal (K-104)

Her önceden ilan tablosu artık açık bir "hiçbirine uymuyorsa" dalı taşıyor:
**tablo yanlıştı, sonuç yorumsuz raporlanır, ve tablonun neyi kaçırdığı
yazılır.** Protokol §13, karar K-104.

Gerekçe ölçüldü: üç kollu koşunun tablosu üç satır taşıyordu — alakasız kol
kartlıya yakın, kartsıza yakın, ya da arada. Çıkan desen dördüncüydü: alakasız
kol her ikisinin de **altında** (3/15, karşısında 7/15 ve 6/15). Üç satır yazmak
sonuç uzayının kapsandığını varsaymak demek ve kapsanmadığında sonucu satırlardan
birine zorlamaya davet ediyor.

Sonradan dördüncü bir satır eklemek ön kaydın işlevini bitirirdi: yorum o noktada
veriye bakılarak seçilmiş olurdu. Dal bu yüzden bir yorum üretmiyor, yorumu
durduruyor.

## 2. Hasarın kapsamı

**Gürültü tabanı bir sonuç (S-56).** On beş hücrenin on biri üç tekrarda
ayrışıyor — sabit tohum, sıcaklık 0,2, aynı prompt, soğuk rejim. Bu, iki kolu tek
epizotla karşılaştıran her ölçümü geçersiz kılıyor. Bu düzenekte öyle olan tek
ölçüm uçtan uca demoydu.

**Sıfırlar ayakta.** `bant2`, `bant3` ve `bant3-kapali` üç bağımsız koşu ve üçü de
sıfır verdi. Gürültü bir sıfırı imal edemez. Ön koşul bulgusu (K-58) etkilenmiyor.

**Keskinleşme (S-57).** Üç kolun her birinde giriş etkisine on beş hücrenin üçü
ile yedisi arasında ulaşıldı; tamamlama 0/45. Jeton bariyerini aşmak gerekli ama
yeterli değil, ve bu örneklemde sıfır tamamlama üretti.

Bunun ayna bulgusuna sonucu var ve ikisi birlikte yazıldı: kütüphane jetonu
almayı öğretiyor, indeks jetonu taşımamayı yasaklıyor, iki bağımsız korpus aynı
mekanik darboğaza yakınsadı — **ve** ölçülen bariyer jeton değil. Yakınsama
gerçek; o darboğazı aşmanın görevi çözmediği de gerçek.

## 3. Sunum tarafında ayrım

| iddia | durum |
|---|---|
| Kartlar bağlama ulaşıyor | **ayakta** — giriş ölçümü, modele bakmadan, 3/3, prompt bayt bayına |
| Kartlar davranışı değiştiriyor | **desteklenmiyor** — geri çekildi |

Sunum iskeletinde **2.8** dolduruldu (giriş iddiası, atıf `results/card-demo.json`
→ `entry`), **4.7** açıldı ve boş işaretlendi (davranış iddiası, sebebiyle),
**4.2**'nin boş olma sebebi güncellendi: alakasız kol artık koşuldu ama kütüphane
içerik atfı için fazla homojen ve kol ayrımı gürültü tabanının altında kaldı.

`PILOT_REPORT.md` iki iddiayı ayrı başlıklar altında yazdı ve hasarın kapsamını
oraya da koydu. Demo raporunun başına geri çekme notu düşüldü; kapanış
notlarındaki sayı silinmedi, üstü çizilip sebebi yazıldı. Epizotlar kayıttan
silinmedi.

## 4. `docs/10-external-review.md`

Yer tutucu (22 satır) yerine gerçek kayıt (181 satır): iki tur, beş model (birinci turda beşi, ikinci turda o beşin üçü), jüri
protokolü, yakınsayan itirazlar tabloları, turlardan doğan kararlar, ve
incelemenin kendi sınırı — beş modelin hiçbirinin "bu model sınıfı bu
kıyaslamada herhangi bir görevi çözebiliyor mu" diye sormamış olması.

## K-102: eklenen modül adları ve public tanımlayıcılar

Yok. Bu PR yalnız belge değiştiriyor.

## #39 — docs: tek adlandirma semasi, CI es denetimi, yedi tasarim belgesinin cevirisi

- Branch: `docs-iki-dilli`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

## Adlandırma şeması (K-105)

`docs/` altındaki her belge artık `NN-ingilizce-kebab.tr.md` / `.en.md`. Kök
İngilizce ve kebab-case, numara öneki korunuyor, dil son sonek.

`12-sandbox-kapsami` → `12-sandbox-scope` yeniden adlandırıldı. Gerekçe: dosya
adı da bir tanımlayıcı (K-102), ve Türkçe bir kökün altında İngilizce bir çeviri
tam olarak koddan temizlediğimiz karışık hâlin kendisiydi. `appworld-olgular.md`
→ `appworld-facts.tr.md`.

Göç tek turda bütün dizine uygulandı. Yarım göç bırakılmadı: iki adlandırma
kuralı aynı anda yürürlükte olsaydı eş denetimi temiz açılamaz ve okuyan iki
kural öğrenmek zorunda kalırdı.

## CI eş denetimi

`scripts/check_docs_parity.py`, CI'ın Lint işinde. Üç şey denetliyor: adlandırma
şeması, çeviri eşi, ve öksüz çeviri — `.en.md` var ama `.tr.md` yok.

Üç kategori taşıyor ve her biri bir konum: **BILINGUAL** çevirisi var ve
denetleniyor, **PENDING** çeviri borcu var ve dalgası yazılı, **TURKISH_ONLY**
çevirisi olmayacak ve sebebi yazılı. Üçüne de girmeyen bir belge denetimi
düşürüyor — "unuttuk" ile "karar verdik" birbirine benzemesin diye.

Şu an 8 iki dilli, 4 Türkçe-yalnız, 3 bekleyen. **Denetim yeşil açılıyor.**

## Çevrilenler

Yedi tasarım belgesinin tamamı: `01-problem-definition`, `02-research-question`,
`03-architecture`, `04-threat-model`, `05-experiment-design`, `06-skill-language`,
`07-failure-taxonomy`.

05'e K-104'ün dördüncü dalı da eklendi, çünkü o belge yorum tablolarının
tanımlandığı yer.

## Bekleyenler, ve neden

| belge | satır | durum |
|---|---|---|
| `docs/09-limitations` | 1677 | PENDING, dalga 1 |
| `experiments/setup-protocol` | 978 | PENDING, dalga 1 |
| `README` | 120 | PENDING, K-105 altında |

Bu üçü bu oturumda bitmedi. Tahmin edip yarım bırakmak yerine PENDING olarak
yazıldı ve denetim onları her koşuda adıyla listeliyor.

## README ayrı ele alındı (K-105)

`README.md` depo kökünde ve adını platform koyuyor; GitHub yalnız o adı işliyor.

Karar: kanonik ad kaynağın adı kalıyor — `README.md` Türkçe kaynak,
`README.en.md` çeviri, ikisinin başında karşılıklı dil bağlantısı. Şemanın
"Türkçe kaynak" ilkesi böylece kökte de geçerli.

Bedeli de yazıldı: dışarıdan gelen okur GitHub'da önce Türkçe metni görüyor.
Alternatif — `README.md` İngilizce, `README.tr.md` Türkçe — kaynağı kanonik
addan çıkarırdı. Tercih değiştirilmek istenirse iki dosyanın yer değiştirmesi ve
`PENDING` girdisinin güncellenmesi yetiyor; karar bu maliyetiyle birlikte
kaydedildi.

## K-102: eklenen modül adları ve public tanımlayıcılar

**Yeni dosya:** `scripts/check_docs_parity.py`.

**Yeni public adlar** (hepsi o dosyada): `NAME`, `LOOSE_NAME`, `BILINGUAL`,
`PENDING`, `TURKISH_ONLY`, `naming_problems`, `parity_problems`,
`orphan_problems`, `uncategorized_problems`, `main`.

**Yeniden adlandırılan public tanımlayıcı yok.** Yeniden adlandırılan dosyalar
yukarıda.

## #40 — readme: Ingilizce on kapi, ve istisnanin denetimi

- Branch: `readme-ingilizce`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

Öneriniz alındı ve uygulandı: `README.md` İngilizce ön kapı, `README.tr.md`
Türkçe kaynak, ikisinin başında karşılıklı dil bağlantısı.

Gerekçenizi K-105'e olduğu gibi yazdım, çünkü asıl mesele orada: "kanonik ad
kaynağın adı" ilkesinin **amacı dar** — ayrıştırılan ya da atıf verilen bir
belgede hangi yarının yetkili olduğu belli olsun. README ne ayrıştırılıyor ne
atıf alıyor, yani ilkenin koruduğu şey burada risk altında değil. İstisna bu
sebeple meşru, kitle tercihi olduğu için değil.

## İstisnanın bedeli koda yazıldı

Depoda tek bir adlandırma istisnası var ve okuyanın onu öğrenmesi gerekiyor.
Bedel `readme_problems` ile karşılanıyor: iki yarının varlığı ve **karşılıklı
bağlantısı** denetleniyor. Bağlantı şartı gereksiz görünebilir ama değil — bir
yarıya düşen okurun diğerine yolu olmazsa iki dilli olmanın anlamı kalmıyor.

## Denetim ateşlerken görüldü

Bunu yazarken kendi hatamı yakaladım: `readme_problems` tanımlıydı ama `main`
içinden **çağrılmıyordu**. `ruff format` benim eşleştirmeye çalıştığım satırı
yeniden biçimlendirmişti ve `replace` sessizce tutmamıştı. Yeşil bir denetim,
hiçbir şey denetlemiyordu.

Bağladım ve üç durumda ölçtüm:

| durum | çıktı | çıkış |
|---|---|---|
| `README.tr.md` yok | `README.tr.md: missing` | 1 |
| bağlantı kopuk | `README.md: no link to README.tr.md` | 1 |
| düzeltilmiş | `naming and parity: clean` | 0 |

K-49'un kuralı: bir doğrulamanın yeşil yanması, doğru sebeple yandığının kanıtı
değil. Bu turda o kural bir kez daha karşılığını verdi.

## Bir uyarı: README içeriği bayat

Çeviri sadık yapıldı, içerik değiştirilmedi. Ama metin şunu diyor:

> Mekanizmaların kendisi sonraki görevlerin konusu. Beceri derleyicisi,
> getirici, kalkan, hata indeksi ve bağlam montajcısı henüz yazılmadı.

Bu artık doğru değil — beşi de yazıldı ve `PILOT_REPORT.md` onları ölçüyor. Aşama
tablosu da 5'te duruyor.

İçeriği sessizce güncellemedim: bu bir çeviri PR'ı ve olgu düzeltmesi ayrı bir
karar. Ama artık **İngilizce ön kapıda** duruyor, yani danışmanın göreceği ilk
metin. Bir sonraki turda düzeltilmesi gerekiyor.

## K-102: eklenen modül adları ve public tanımlayıcılar

Yeni modül yok. `scripts/check_docs_parity.py` içinde bir yeni public ad:
`readme_problems`. `PENDING` sözlüğünden `README` girdisi çıktı; kalan iki borç
`docs/09-limitations` ve `experiments/setup-protocol`.

## #41 — 09-limitations: uretilmis harita, K-106, ve README asgari duzeltmesi

- Branch: `limitasyon-yapisi`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

Çeviriden önce sorduğunuz yapı sorusunun cevabı: **evet, ama dar bir evet.**
Ölçüm önce, karar sonra.

## Ölçüm — sayı sizinkinden farklı

| | siz | ölçülen |
|---|---|---|
| kayıt | 34 | **56 başlık, 55 kayıt** (biri ek) |
| kayıt başına | ~50 satır | **medyan 26, ortalama 30** |

Yani **kayıt başına şişkinlik sorun değil**: bir sınırlamanın gerekçesi ve
ölçümüyle 26 satır makul. Dağılım çarpık — en uzun beş kayıt 144, 84, 69, 56, 53
satır, en kısaları 7. Uzun olanlar gerçekten çok şey taşıyor.

**Asıl eksik harita.** 1677 satır, 56 başlık, ve dosyanın başında hiçbir dizin
yok. Belgeyi eline alan S-01'den başlayıp yürüyor. Hangi sınırın hâlâ açık
olduğu, hangisinin kapandığı, hangisinin okunan iddiayla ilgili olduğu ancak
tamamı okununca görülüyor.

Ölçülen: **46 açık, 9 kapandı** — ve bunu bugün öğrenmenin tek yolu 56 başlığı
tek tek okumak.

## Yapılan

`scripts/build_limitations_index.py` haritayı **üretiyor**, elle tutulan kopya
yok. Belgenin başında işaretli bir blok içine yazıyor; `--check` belge ile
haritanın ayrışmasını yakalıyor ve CI'ın Lint işinde koşuyor.

Üretilmiş olması şart, çünkü elle tutulan bir dizin ikinci bir doğruluk kaynağı
olur ve bu deponun o bedeli ölçtüğü bir vakası var: karar CSV'si otuz satırda
gerekçe özeti olarak "Karar." taşıyordu ve hiçbir şey itiraz etmemişti (K-103).

**Durum başlıktan okunuyor, yeni bir alan eklenmedi.** Üstü çizili ya da
KAPANDI/DÜZELTİLDİ taşıyan başlık kapalı, kalanı açık. Belgeye yeni sözdizimi
girmiyor.

**`(özgün metin)` ek olarak tanınıyor.** Bir sınırlama kapandığında özgün metni
aynı kimlik altında altta duruyor; harita onu ayrı kayıt saymıyor. `S-25`'in iki
kez görünmesi kusur değil, o pratiğin kendisi.

Denetim ateşlerken görüldü: başlık değişince `the map is stale`, çıkış 1; geri
alınınca temiz, çıkış 0.

## Yapılmayan, ve neden

Uzun kayıtlar (144, 84, 69 satır) **bölünmedi**. O içerik işi ve çeviri turuna
karıştırmak iki değişikliği aynı commit'e koymak olurdu. Harita onları zaten
görünür kılıyor; bölünmeleri gerekiyorsa ayrı bir karar.

## K-106 — kendi bulduğum arıza kayda geçti

İki parçalı: hiçbir şeyi değiştirmeden başarı bildiren bir düzenleme arızadır, ve
bir biçimlendirici koştuktan sonra önceki dize eşleşmeleri bayattır.

K-49'un alt deseni olarak yazıldı, çünkü daha dar ve daha sinsi: yeşil yanan şey
hiç koşmamış olabiliyor, ve koşmadığını gösteren tek şey negatif test.

## README asgari düzeltmesi — üç olgu

Sizin sınırladığınız kapsam uygulandı, iki dilde:

1. Mekanizmalar yazıldı ve üretim yolunda ölçülüyor.
2. Ön koşul kapısı ateşledi; birincil karşılaştırma bu yapılandırmada koşulamadı.
3. Demonun davranış iddiası geri çekildi; giriş iddiası ayakta.

Yirmi satır. Tam yeniden çerçeveleme yapılmadı.

## K-102: eklenen modül adları ve public tanımlayıcılar

**Yeni dosya:** `scripts/build_limitations_index.py`.

**Yeni public adlar:** `SOURCE`, `BEGIN`, `END`, `HEADING`, `IDENTIFIER`,
`CLOSED_WORDS`, `records`, `table`, `rendered`, `main`.

`check_language.py`'nin `SUBJECT_FILES` kümesine bir girdi eklendi: üreteç Türkçe
belgeye Türkçe yazıyor, yani Türkçesi araç değil konu.

## #42 — 09-limitations: iddia ekseni siniflandirmasi ve K-107

- Branch: `limitasyon-eksen`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

İki iş vardı. **Birincisi bitti, ikincisi başlamadı** — ve bunu tahmin edip yarım
yapmaktansa açık yazıyorum.

## 1. İddia ekseni sınıflandırması — bitti

Sözdizimi: her kaydın başlığının altındaki **ilk alıntı satırı**.

```
> **İddiayı sınırlıyor.** K-51 — artık varyansın model başına ölçüldüğü
> **Kapsam.** 8 GB VRAM'e üç modelin sığmadığını kaydediyor; donanım kısıtı
> **Sınıflandırılmadı.** düzeltilmiş bir olay kaydı; bugünkü rolü karara bağlanmadı
```

Harita bu satırı okuyor. **İkinci doğruluk kaynağı yok**, durum alanında olduğu
gibi; `--check` ayrışmayı yakalıyor ve CI'da koşuyor.

**İşlemsel test uygulandı:** 34 maddenin her birinde sınırladığı iddia **adıyla**
yazılı. Ad veremediklerim kapsama gitti.

### Ölçülen dağılım

| eksen | sayı |
|---|---|
| bir iddiayı sınırlıyor | **34** |
| kapsam | **6** |
| sınıflandırılmadı (K-104'ün dördüncü dalı) | **6** |
| işaretsiz | **0** |

46 açık maddenin tamamı işaretli. Kapanmış 9 kaydın ekseni sorulmuyor — kapanmış
bir sınırlama hiçbir şeyi kısıtlamıyor, sütunda tire duruyor.

Sınıflandırılmayan altısı **aynı sınıftan**: düzeltilmiş bir arıza kaydının
bugünkü rolü — sınırladığı bir iddia mı, yoksa kapanmış bir olay mı. Zorlamadım.

### Yan ürün: iddia → sınırlama haritası

34 maddenin adlandırdığı iddialar toplandığında sunumun istediği eşleme çıkıyor.
En çok atıf alanlar: K-58 ön koşul kapısı (3), K-51 artık varyans (2),
07-failure-taxonomy eylem düzeyi (3), 04-threat-model kalkan (2).

## 2. Kırk altı maddede kapanma gözden geçirmesi — YAPILMADI

Bu turda bağlam bütçem bitti. Yapmadığım işi yapılmış gibi raporlamamak için
açık yazıyorum: **46 maddenin hiçbiri bu turda kapanma ölçütüne karşı
değerlendirilmedi.**

Yalnız bir gözlem, ölçüt uygulanmadan: `S-12` (sıfırlama testi CI koruması
altında değil) K-100'den sonra kapanmış olabilir — CI artık `appworld install`
ve veriyi kuruyor, yani `appworld` işaretli testler koşuyor. Bu bir kapanma
iddiası değil, sıradaki turda ilk bakılacak yer.

## K-107

Karar, işlemsel test, K-104 bağlantısı ve ölçülen ilk dağılım kaydedildi.
Kapanmış kaydın ekseninin sorulmadığı da yazılı.

## Bu turda K-106 kendi kuralıyla yakalandı

Üreteci yamalarken `ruff format` daha önce koşmuştu ve `table` fonksiyonunun
imzası yeniden biçimlenmişti; `assert old_tab in t` durdu. Hiçbir şey yazılmadı,
çünkü yazma bütün assert'lerden sonra. Yama yerine dosyayı bütün olarak yeniden
yazdım.

## K-102: eklenen modül adları ve public tanımlayıcılar

Yeni modül yok. `build_limitations_index.py` içinde yeni public adlar: `AXIS`,
`AXIS_SHORT`, `bodies`. `records` artık dört alanlı demet döndürüyor.

## #43 — 09-limitations: iddia anahtarli eslem, ve S-12 kapandi

- Branch: `iddia-haritasi`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

## 1. İddia anahtarlı eşleme — üretilen eser oldu

`build_limitations_index.py` artık iki tablo basıyor. Birincisi sınırlama
anahtarlı (hangi kayıt neyi kısıtlıyor), ikincisi **iddia anahtarlı**: her
iddianın altında kaç sınırlama durduğu.

Anahtar, işaretteki ilk uzun tireden önceki metin — `K-51 — ...` ve
`K-51 — başka bir cümle` aynı iddiaya düşüyor.

**24 iddia, 34 sınırlama.** En çok yük taşıyanlar:

| iddia | sınırlama |
|---|---|
| `05-experiment-design` | 3 |
| `07-failure-taxonomy` | 3 |
| `K-58` ön koşul kapısı | 3 |
| `04-threat-model`, `DATA_MODEL.md`, `K-51`, sınır kontrolü | 2'şer |

Ters yönden bakınca bir keying kusuru da göründü ve düzeltildi: `S-16` işareti
`07-failure-taxonomy ve üç kapılı suç atfı` diye yazılmıştı ve zaten var olan bir
iddia için ikinci bir anahtar üretiyordu. İşaret tek iddiayı adlandıracak biçimde
yeniden yazıldı, üç kapılı suç atfı parantez içine alındı. **Eşlemenin eser
olmasının ilk kazancı bu oldu** — gözlem olsaydı görünmezdi.

## 2. Kapanma turu başladı: S-12 kapandı

**Ölçüt uygulandı, iddia edilmedi.**

Ölçüt: *tasarım boşluğuydu ve dolduruldu.* K-100 CI'a `appworld install` ve
`download data` adımlarını ekledi, ve `pytest` filtresi
`-m "not model_server and not sandbox"` oldu — `appworld` işareti artık
elenmiyor.

Kanıt iki parça, ikisi de ölçüldü:

1. Test `tests/test_appworld_reset.py` içinde ve `pytestmark = pytest.mark.appworld`
   taşıyor.
2. CI'ın kullandığı filtreyle toplama koşuldu:
   `pytest -m "not model_server and not sandbox" --collect-only` çıktısında
   `test_appworld_reset` bir kez görünüyor.

Kayıt silinmedi: başlığın üstü çizildi, kapanma notu ve kanıtı altına yazıldı.

**Neyin kapanmadığı da yazıldı:** testin CI'da koştuğu gösterildi; testin doğru
şeyi ölçtüğü ayrı bir soru ve bu kayıt onu hiç sormamıştı.

Açık madde 46'dan **45**'e indi.

## Üçüncü kategori eklenmedi

Talimatınıza uyuldu. Altı sınıflandırılmamış madde `> **Sınıflandırılmadı.**`
işaretiyle duruyor ve kapanma turunu bekliyor.

## Kalan kapanma turu

45 maddenin 44'ü bu turda ölçüte karşı değerlendirilmedi. Bağlam bütçesi bitti.
Sıradaki tur oradan devam ediyor.

## K-102: eklenen modül adları ve public tanımlayıcılar

Yeni modül yok. `build_limitations_index.py` içinde yeni public adlar: `CLAIM`,
`CLAIMS_BEGIN`, `CLAIMS_END`, `claims`, `claims_table`, `with_claims`.

## #44 — 09-limitations: kapanma turu (46 -> 39 acik) ve K-108

- Branch: `kapanma-turu`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

## Kapanma turu — 46 → 39 açık

S-12'nin kalıbı yedi kayda uygulandı: **ölçüt adıyla, kanıt ölçülmüş parçalar
hâlinde, ve neyin kapanmadığı ayrıca yazılı.**

| kayıt | ölçüt | kanıt |
|---|---|---|
| `S-12` | tasarım boşluğu doldu | test `appworld` işaretli; CI filtresiyle `--collect-only` çıktısında bir kez toplanıyor |
| `S-28` | tasarım boşluğu doldu | iki koşucuda `def preflight`; otuz epizot başlamadan yazma yolu tek epizotla koşuluyor |
| `S-29` | tasarım boşluğu doldu | `missing_manifest_constraints` üç koşucuda çağrılıyor; kısıt eksikse koşu başlamıyor |
| `S-30` | tasarım boşluğu doldu | `max_output_tokens` `config/recording.yaml`'da; `ZIHIN_MAX_TOKENS` `record_run.py`'de sıfır eşleşme |
| `S-31` | tasarım boşluğu doldu | `resume_check` `records.py`'de tanımlı, iki koşucuda çağrılıyor |
| `S-36` | ölçüldü, cevap geldi | `api_routes.py` yöntemi çözümlemeye alıyor; `verify_wire_identity` kayıttaki her eylemi ölçüyor |
| `S-37` | ölçüldü, cevap geldi | `WRITE_METHODS` kümesinde `update` yok, sıfır eşleşme |

Yedisinde de üstü çizildi, kanıt altına yazıldı, **kayıt silinmedi**.

**Aşırı kapatmama uygulandı.** Her birinde neyin kapanmadığı ayrı paragraf: ön
kontrol yazma yolunun koştuğunu gösteriyor, yazılan değerlerin doğruluğunu değil;
var olan veritabanı hâlâ kısıtsız sütun taşıyor; kalan sekiz yazma fiilinin
gerçek kullanımı ayrı ayrı doğrulanmadı.

## Sınıflandırılmamış altı madde kendiliğinden düştü

Tahmininiz doğru çıktı: altısı da kapandı, ve **sınıflandırılmadı sayacı sıfıra
indi**. Üçüncü kategoriye gerek kalmadı.

| eksen | önce | sonra |
|---|---|---|
| sınırlıyor | 34 | 33 |
| kapsam | 6 | 6 |
| sınıflandırılmadı | 6 | **0** |

## Kalan 33 madde — süpürüldü, kapanan yok

Üç ölçüt kalan otuz üçe uygulandı. Hiçbiri geçmiyor, ve sebepleri üç sınıfta
toplanıyor:

- **Dış olgular** (`S-01` AppWorld dalı, `S-02` referans çözümler, `S-05`/`S-16`
  yanıt verisi yok, `S-06` süreç başına tek dünya): kapanmaları bizim elimizde
  değil.
- **Ölçülmüş ve doğru çıkmış kısıtlar** (`S-47` karakter tavanı, `S-44`
  `error_class` tek değerli, `S-48` en sık kalıp getirilemiyor, `S-56` gürültü
  tabanı): ölçüm cevabı verdi ve cevap "kısıt var".
- **Ön koşul kapısına bağlı olanlar** (`S-14`, `S-19`, `S-22`, `S-23`, `S-27`,
  `S-57`): kapanmaları bir sonraki ölçüm turunu bekliyor.

Süpürme başlıklar ve açılış paragrafları üzerinden yapıldı; kanıt yalnız bir
ölçütü geçenler için kuruldu, sizin verimlilik notunuza uygun olarak.

## K-108 — türetilmiş görünümün şekli girdilerinin kontrolü

İlkeyi genel olarak yazdım, ve sınırını da: ikinci yön yalnız **gruplama
tutarsızlığını** gösteriyor; bir girdinin yanlış ama tutarlı adlandırılması iki
yönde de doğru görünür.

## Yapılmayan: sunum iskeleti çapraz kontrolü

28 iddia ile 24 iddianın birleştirilmesi ve altı boş nedensel yuvanın ayrılması
bu turda yapılmadı. Bağlam bütçesi bitti. Sıradaki turun ilk işi.

## K-102: eklenen modül adları ve public tanımlayıcılar

Yok. Bu PR yalnız belge değiştiriyor.

## #45 — Sınırlamalar: her açık kayda kapanma sınıfı, harita onu basıyor (K-109)

- Branch: `kapanma-sinifi`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

## Süpürmenin sonucu belgeye taşındı

Kapanma turunda otuz üç madde üç ölçütle süpürülmüştü ve sonuç **yalnız PR
gövdesinde** duruyordu. Rapor kapanınca o değerlendirme kaybolacaktı; belge
tarafında otuz dokuz madde düz liste hâlinde, yani "otuz dokuz çözülmemiş
sorun" diye okunacaktı.

Artık her açık kayıt eksen işaretinin altında bir satır taşıyor:

    > **İddiayı sınırlıyor.** K-58 — ön koşul kapısının tasarım öncesi öngörülebilir olduğu
    > **Kapanma sınıfı.** Kalıcı kayıt — tasarımdan önce bakılmamış olmak geri alınamaz

**İşlemsel test tek soru:** bu kaydı kapatacak iş kimin elinde? Sınıf kaydın
konusuna değil kapanma yoluna bakıyor.

| sınıf | sayı | ne demek |
|---|---|---|
| Dış olgu | 10 | yukarı akış, donanım, K-19 ile dondurulmuş iskele |
| Ölçüldü | 10 | soru soruldu, cevap geldi, cevabın kendisi kısıt |
| **Sonraki tur** | **17** | planlanmış bir ölçüm ya da yapım kapatabilir |
| Kalıcı kayıt | 2 | kendi tarihimizde olmuş, hiçbir iş geri almaz |

Haritanın başlığı bunu cümle olarak da basıyor: **otuz dokuz açık maddenin on
yedisi geçici, yirmi ikisi belgede kalıcı.**

## Süpürme on beş örnekti, bu otuz dokuzun tamamı

PR #44'ün gövdesi üç sınıfı **örnekleyerek** yazmıştı; kalan yirmi dördün
ataması yapılmamıştı. Tam geçişte üç kayıt farklı yere düştü, düzeltildi:

- `S-16` — süpürme onu `S-05` ile birlikte dış olgu saymıştı. `S-05` yukarı
  akışın günlük biçimi; `S-16` **bizim kurmadığımız** enstrümantasyon ve tercih
  sırası kayıtta yazılı. Sonraki tur.
- `S-27` — bant taraması bugünkü durma kuralıyla yeniden koşulabilir. Sonraki tur.
- `S-47` — elli bin karakterlik tavan referans iskelenin içinde ve K-19 onu
  dondurdu. Dış olgu.

## Dördüncü sınıf önceden ilan edilmedi

`S-23` (taban oranlarına tasarımdan önce bakılmadı) ve `S-24` (dış inceleme ön
koşul sorusunu sormadı) üç sınıfın üçüne de uymuyor: dış değil, ölçüm sonucu
değil, ve hiçbir tur onları kapatmıyor. K-104 tam bu dalı zorunlu kılıyor —
hiçbirine uymuyorsa tablo yanlıştı. Zorlamak yerine dördüncü sınıf açıldı.

Bu geçen turun tersi bir durum: eksen tarafında üçüncü kategoriyi **eklememek**
doğruydu, çünkü o altı madde bayattı ve kendiliğinden düştü. Burada iki madde
bayat değil, gerçekten başka bir şey.

## Nöbetçi ateşliyor

Üç durumda görüldü (K-49):

1. Bir `Kapanma sınıfı` satırı silindi → `--check` bayat dedi, yeniden üretimde
   `1 without a closure class` ve tabloda bir `işaretsiz` satır.
2. Etiket diakritiksiz bozuldu (`Dis olgu`) → `S-01: unknown closure class
   "Dis olgu"`, çıkış kodu 1.
3. Geri alındı → `limitations map: current, 55 records`, çıkış kodu 0.

## K-109

Şemayı ve işlemsel testi yazıyor. **Sınırı da yazılı:** sınıf bir yargı, ölçüm
değil. "Sonraki tur" bir kaydın kapanacağını değil, kapanma yolunun bizde
olduğunu söylüyor; o tur koşulmazsa sınıf yanlışlanmıyor, yalnız geçici kısım
geçici kalıyor.

## Yan düzeltme

`check_docs_parity.py` içindeki bekleyen-çeviri notu `09-limitations` için 1677
satır diyordu; belge 2037 satır. Güncellendi.

## Yapılmayan

Sunum iskeleti çapraz kontrolü hâlâ sırada; bu PR onu içermiyor.

## K-102: eklenen modül adları ve public tanımlayıcılar

`scripts/build_limitations_index.py` içinde `CLOSURE`, `CLOSURE_LABELS`. Yeni
modül yok; `records()` artık beş alanlı demet döndürüyor (dörttü).

## #46 — Çapraz kontrol: sunum iddiaları ile sınırlama haritası; kapsama özeti üretiliyor

- Branch: `capraz-kontrol`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

## Çapraz kontrol — 35 iddia, 33 açık sınırlama

İki liste birleştirildi. **Birleşme elle kuruldu ve bu yazılı:** iskelet kanıt
eserlerine anahtarlıyor (`results/*.json`, belge bölümleri), harita belge ve
kararlara (`07-failure-taxonomy`, `K-58`). Ortak anahtar yok, yani bağ türetme
değil yargı — K-107'nin ölçütünün ters yönde uygulanmış hâli ve o yönde ad
verme disiplini yok.

On dokuz iddianın en az bir sınırlaması var. On altısının hiç yok, ve üç gruba
ayrılıyor.

| grup | sayı | hangileri |
|---|---|---|
| A. İddia yok — boş nedensel yuva | 3 | `4.1`, `4.3`, `4.5` |
| B. Kendisi sınırlama | 3 | `6.2`, `6.3`, `6.4` |
| **C. Gerçek soru** | **10** | `1.1`–`1.4`, `2.5`, `2.8`, `3.2`, `3.3`, `3.4`, `5.5` |

**A grubu beklediğinizden küçük.** "Altı boş nedensel yuva birinci grupta çıkıp
gürültü yapacak" demiştiniz; yalnız üçü çıktı. Yedi boş yuvanın dördü zaten
sınırlama taşıyor (`S-56`, `S-14`, `S-57`, `S-56`), çünkü sınırlama iddianın
neden **kurulamadığını** da kaydediyor. Boş yuva ile sınırlamasız yuva aynı şey
değilmiş.

**B grubu önceden görülmemişti.** Bölüm 6'nın iddiaları zaten sınırlama;
üstlerine sınırlama aramak sınırlamanın sınırlamasını aramak olurdu. `6.1` ve
`6.5` buraya düşmüyor çünkü kimlik adlandırıyorlar.

## C grubunun okunuşu

Her satırın yanında **bir okuma** var, ölçüm değil. İkisi anahtarlama boşluğu —
kayıt var ama iddiaya bağlanmamış:

- `2.5` "kart biçimi jeton bütçesine sığıyor" ← `S-47` bağlayıcı sınırın jeton
  değil **karakter** olduğunu söylüyor, ve `03-architecture`'a anahtarlanmış.
- `1.2` "ölçülecek şey yolun uzunluğu" ← `S-17` yolun birimini tartışıyor, yalnız
  sansür oranına anahtarlanmış.

Yedisi yazılmamış görünüyor (`1.1`, `1.3`, `1.4`, `2.8`, `3.2`, `3.4`, `5.5`),
biri muhtemelen yeterli (`3.3`). **Adaylar sınırlama belgesine yazılmadı** —
yazılmaları ayrı bir karar ve az önce kapadığınız çeviri borcunu büyütüyor.

## `3.4` yöntem olarak dikkate değer

`S-36`'nın kapanış notundaki "neyin kapanmadığı" paragrafı bir artığı adıyla
yazmıştı: *kayıtta hiç görülmemiş bir yol/yöntem çifti sınanmadı.* O artığı
taşıyan **açık kayıt yok**. Aşırı kapatmama disiplini artığı görünür kıldı;
artığı bir kayda taşımak ayrı bir adım ve atlandı.

## Ters yön

Beş kayıt bir iddiayı sınırlıyor ama sunum o iddiayı kurmuyor: `S-04`
(doğrulayıcı hükmü), `S-22` (sansür oranı), `S-24` (dış inceleme), `S-33`
(karar projeksiyonu), `S-50` (yönetim rotaları). `S-33` iç araç; kalan dördü
sunumun kurmadığı ama ölçümün dayandığı cümleleri kısıtlıyor.

## Çapraz kontrolden önce çıkan üç ölçüm

**1. İskeletin kendi kapsama özeti bayattı.** 28 iddia / 22 dolu / 6 boş
diyordu; satırlar **35 / 28 / 7**. Bölüm 2 `2.8`i, bölüm 4 `4.7`yi sonradan
kazanmış, ve **bölüm 5 — beş iddia — özete hiç girmemiş.**

Sizin "sunum iskeletinde yirmi sekiz iddia var" premisiniz bu tablodan geliyordu.
28 sayısı bugün *dolu* iddiaların sayısı; tesadüf.

Özet artık üretiliyor (`scripts/build_skeleton_coverage.py`), `--check` CI'da.

**2. `6.1` bayat ve yanlış bir kayda atıf veriyordu.** `S-31` devam mantığıyla
ilgili ve bu turda kapandı; kapsamayla ilgisi yok. Kapsamadan söz eden tek açık
kayıt `S-48` ve içeriği tam olarak "kapsama tek boyutlu"; atıf ona çevrildi.

**3. Slayt sırasındaki `2.1–2.7` ve `4.1–4.6` aralıkları** satırlarla
uyuşmuyordu.

## K-104 — uymamanın iki türü

İstediğiniz ayrım yazıldı. Ölçüt: **bekleyen bir adım bu uymamayı çözüyor mu.**

*Geçici uymama* → kategori eklenmiyor. Altı sınıflandırılamayan kayıt bayattı,
kapanma turu onları çözdü, ve kategori eklenseydi bugün boş dururdu.

*Yapısal uymama* → taksonomi eksiktir. `S-23` ve `S-24`e hiçbir bekleyen adım
dokunmuyor; dördüncü sınıf o yüzden açıldı (K-109).

Yani K-104 "asla kategori ekleme" demiyor; uymamayı sonuca zorlamayı yasaklıyor.

## Nöbetçi

Kapsama sayacı satırları **kendi bölümlerinin içinde** sayıyor ve satır
numarasını bölümle karşılaştırıyor — çapraz kontrol tablosunun satırları iddia
sanılmasın diye. Üç durumda görüldü:

1. Bölüm 1'e satır eklendi → `the coverage summary is stale`, çıkış 1.
2. `3.6` satırı bölüm 2'ye taşındı → `claim 2.6 sits under section 3`, çıkış 1.
3. Geri alındı → `current, 35 claims`, çıkış 0.

## Yan düzeltme

`check_language.py`'nin konu dosyaları listesindeki bir yorumda **belge adı
düşmüştü** ("It writes the map into , so the strings…") — İngilizce geçişinde
kaybolmuş. Ölçümle geri konuldu. Yeni üreteç de aynı gerekçeyle listeye alındı.

## Sınıra uyum

`09-limitations`'a **hiçbir şey eklenmedi**: ne kayıt, ne yapı. Bu PR sunum
tarafında duruyor ve çeviri borcunu büyütmüyor.

## K-102: eklenen modül adları ve public tanımlayıcılar

`scripts/build_skeleton_coverage.py` — `layers`, `table`, `rendered`, `main`,
`BEGIN`, `END`, `SECTION`, `CLAIM`.

## #47 — 09-limitations çevirisi ve gömülü ad denetimi; K-110, K-111, K-112

- Branch: `ceviri-hazirligi`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

## Çeviriden önce kuruldu, çünkü dikkat nöbetçi değil

"Çeviri turunda dize içine gömülü ad, yol ve tanımlayıcıya özel dikkat"
dediniz. Dikkat tekrarlanabilir değil; bu tur onun yerine bir denetim koyuyor,
ve **çeviriye başlamadan önce** koyuyor.

`check_docs_parity.py` artık her iki dilli çiftte **çapa** sayıyor: ters tırnak
içindeki her dize, `S-NN`/`K-NN` kimlikleri, ve çıplak dosya yolları.

**Küme değil, sayı.** `S-05`'i dört kez anan bir belgenin çevirisinde iki kez
geçmesi iki atıf kaybıdır; küme karşılaştırması buna "eşit" der.

**Dil eki katlanıyor.** İngilizce belge `03-architecture.en.md`'ye bağ verir,
Türkçesi `.tr.md`'ye — değişmesi *gereken* tek çapa bu. İkisi `.md`'ye katlanıyor,
yani düşen bir bağ hâlâ düşüyor.

## Sekiz belgede 208 çapa, dört gerçek uyuşmazlık

Ham sonuç 24 satırdı; 18'i dil eki, 2'si ters tırnak içinde düzyazı olan bir
küme ifadesi (`statik ∪ ampirik`, listeye yazıldı). Kalan dört tanesi gerçek:

**1. `05-experiment-design`: çeviri kaynağından ileride.** İngilizce sürüm,
Türkçe kaynağında **hiç olmayan** bir paragraf taşıyor — K-104'ün dördüncü dalı.
Türkçe kaynak, çevirisi kadar güncel değildi. Kural doğru ve yeri orası, o yüzden
paragraf **kaynağa eklendi**.

**2. `12-sandbox-scope`: iki tanımlayıcı ters tırnaklarını kaybetmiş.** `pop` ve
`connect` çeviride düzyazıya dönüşmüş — tam olarak uyardığınız arıza sınıfı, ve
denetim kurulur kurulmaz çıktı. Geri konuldu.

**3. Sekiz çeviriden yalnız biri kaynağını ilan ediyordu.** `12-sandbox-scope.en.md`
"Turkish is the source: …" satırıyla açılıyordu, diğer yedisi açılmıyordu. Kural
tekdüzeleştirildi ve denetim bu **tek** asimetriyi tanıyor.

## Nöbetçi görüldü

- Gömülü bir yol (`config/recording.yaml`) düzyazıya döndü →
  `only in the source`, çıkış 1.
- Bir atıf sayısı düştü → `09-limitations.md — 2× vs 1×`, çıkış 1.
- Geri alındı → `208 anchors carried through`, çıkış 0.

## K-110 — kapanış artığı

İstediğiniz kural yazıldı: bir kapanışın "neyin kapanmadığı" paragrafında adı
geçen artık **ya kendi kaydına dönüşecek ya da kayda gerek olmadığı açıkça
yazılacak**. Üçüncü seçenek — adlandırıp orada bırakmak — kapalı.

Gerekçesi ölçülmüş hâliyle duruyor: `S-36`'nın artığı adıyla yazılmıştı, hiçbir
açık kayda geçmedi, ve çapraz kontrol bunu `3.4`'ün sıfır sınırlaması olarak
gösterdi. Sizin cümlenizle: görünür kılıp buharlaştırmak, hiç görünür
kılmamaktan yanıltıcı.

**Sırası yazılı.** On altı mevcut kapanışın geriye dönük taraması **çeviriden
sonraya** bırakıldı, çünkü tarama yeni kayıtlar üretebilir. Aynı kuyrukta çapraz
kontrolün yedi adayı ve ters yöndeki beş kaydı var.

**Sınırı da yazılı.** Kural artığın *adlandırılmış* olmasına dayanıyor; hiç
yazılmamış bir artığı yakalayan şey bu kural değil.

## K-109 — ikinci kanıt

Gözleminiz kayda geçti: dördüncü kapanma sınıfı da, çapraz kontroldeki B grubu
da **tam geçişte** çıktı, örneklemede değil. Örnekleme beklenen sınıfları
doğruluyor; beklenmeyeni yalnız tam geçiş veriyor.

## Sırada

`09-limitations` çevirisi. Bu PR ona hazırlık; çeviri bu denetim altında
yazılacak.

## K-102: eklenen modül adları ve public tanımlayıcılar

`scripts/check_docs_parity.py` içinde `anchors`, `anchor_problems`, `add`,
`CODE_SPAN`, `RECORD_ID`, `BARE_PATH`, `LANGUAGE_SUFFIX`, `TRANSLATED_SPANS`.


---

## Çeviri: 2037 satır, 55 kayıt, 644 çapa

`docs/09-limitations.en.md` yazıldı. Çeviri yukarıdaki denetim altında
yapıldı ve **644 çapanın 644'ü iki tarafta birebir tutuyor**.

### Denetimin kendi iki kusuru çeviri sırasında çıktı

**1. Satır sonuna bölünmüş ters tırnak çifti.** Regex `\n` içermeyen span
arıyordu; `` `appworld\ninstall` `` gibi bir span atlanıyor, ve atlanınca
**yanlış ters tırnakları eşleyip düzyazıyı kod sanıyordu**. Span içi boşluk
artık daraltılıyor.

**2. Üçlü ters tırnaklı bloklar.** Çit de ters tırnakla sınırlı olduğu için
kapanış çiti sonraki satır içi ters tırnakla eşleşiyordu. Çitler artık önce
ayrılıyor ve kendi başlarına çapa sayılıyor.

İkisi de ilk koşuda yakalanmadı; **belge büyüdükçe ortaya çıktılar**, ve ikisi
de yanlış-pozitif değil yanlış-negatif üretiyordu.

### Kaynakta üç bayat tanımlayıcı

Üçü de İngilizce geçişinde yeniden adlandırılmış, belge güncellenmemiş:

| kaynakta | gerçekte |
|---|---|
| `on_kontrol` | `preflight` |
| `_ilerlemesiz_mi` | `_made_no_progress` |
| (düşmüş belge adı) | `docs/09-limitations.tr.md` |

Üçü de düzeltildi. Bu, uyardığınız arıza sınıfının **kaynak tarafındaki**
hâli: mekanik yeniden adlandırma kodu değiştiriyor, belgeyi bırakıyor.

### Harita iki dilde

Yapı **yalnız Türkçe kaynaktan** okunuyor — tek belge, tek ayrıştırıcı — ve
İngilizce tablo yalnız sözcükleri çeviriden alıyor. Kaynakta olup çeviride
olmayan bir kayıt üreteci düşürüyor.

### K-111 ve K-112

**K-111** çapa denetimini ve genel ilkeyi yazıyor: nicelik "kaç kez geçiyor"
olduğunda küme karşılaştırması kaybı sessizce kabul eder. **Sınırı** da yazılı:
yön ihlalini yalnız eklenen içerik çapa taşıyorsa yakalıyor; çapasız düzyazı
iki tarafta da sayısız kalır ve sızar.

**K-112** denetlenecek alan yoksa denetimin düşmesini şart koşuyor, ve önce
kendi kodumuza uygulandı: çapa denetimi bir taraf eksikken `continue`
ediyordu.

**Premisinizden ağır bir ölçüm.** Üçüncü CI denetiminin boşlukta geçtiğini
söylemiştiniz. Ölçtüm: iki dilli dalganın tasarımı üç denetim ilan etmiş —
"eş var mı, ikisi aynı commit'te mi değişti, kaynak commit güncel mi" — ve
**yalnız birincisi kurulmuş**. İkincisi ve üçüncüsü hiç yazılmamış, ve
dayandıkları alan (her `.en.md` başlığındaki kaynak commit'i) sekiz çevirinin
**sıfırında** var. Yani boşlukta geçen bir denetim değil, hiç olmayan iki
denetim. K-112 bu ayrımı da yazıyor.

### Sırada

`experiments/setup-protocol` çevirisi; sonra kuyruktakiler — K-110'un geriye
dönük taraması, çapraz kontrolün yedi adayı, ters yöndeki beş kayıt.

## #48 — Yapısal nöbetçi sayımı, iki koşucu boşluğu; K-115, K-116

- Branch: `yapisal-sayim`
- Merged: 2026-08-18

<!-- body, verbatim except for task text -->

## Önce bir kayıp, ve onu bulan şey

**Süpürme commit'i (`7feb45c`) `main`'e hiç girmedi.** İtilmemiş; hemen ardından
CI sorgulanıp beş iş yeşil görülünce "birleşmeye hazır" diye raporladım. **Yeşil
olan koşu bir önceki commit'e aitti.** PR #47 birleşti ve süpürmenin tamamı
kayboldu: `--check` bayrağı, CI adımı, boşluk raporu, K-113, K-114.

Cherry-pick ile geri alındı ve bu PR'da.

**Kaybı bulan şey yapısal sayımın kendisi oldu** — `build_decisions_csv.py`'yi
hâlâ nöbetçisiz gösterdi, oysa "nöbetçi eklendi" diye raporlamıştım.

`K-116` bunu kural yapıyor: CI'ın yeşil olduğu değil, **hangi commit'te** yeşil
olduğu doğrulanıyor. Sınıfı tanıdık — K-49 "yeşil bir kontrol koştuğunun kanıtı
değil" diyordu; bu onun bir katman yukarısı.

## Yapısal sayım: alt sınırdan üst sınıra

`scripts/count_guards.py`, CI'da. Koruma gerektiren **türler** adlandırılıyor,
her türün her üyesi sayılıyor, her üyede nöbetçi aranıyor. On dört bölge.

| Tür | Üye | Nöbetçisi |
|---|---|---|
| Üretilen görünümler | 3 | `--check` + CI'a bağlı olmak |
| Ölçüm koşucuları | 7 | `preflight`, `resume_check`, `missing_manifest_constraints` |
| Ayrıştırılan arayüzler | 4 | şekli çivileyen bir test |

**İlk koşuda haklı çıktı.** Düzyazı taraması **üç** ölçüm koşucusu tanıyordu;
yapısal sayım **yedi** buldu. `measure_card_arms`, `measure_card_demo`,
`measure_context_cost` ve `measure_gpt4o_subset` hiçbir belgede denetimleriyle
anılmamıştı — ilan taraması onları göremezdi, çünkü ortada ilan yoktu.

**Bilinen çıplaklar ilan ediliyor.** `ACCEPTED` listesi yedi bölgeyi gerekçesiyle
taşıyor. Listede olmayan çıplak bir bölge kontrolü düşürüyor, **ve listede olup
artık korunan bir bölge de düşürüyor** — bayat bir muafiyet muafiyet sayılmıyor.
Liste olmasaydı kontrol ilk koşuda kırmızı yanar ve kapatılırdı.

## İki koşucu boşluğu kapandı

`measure_band`'e devam koruması, `measure_rule_off`'a ön kontrol eklendi. Üç
koşucunun üçünde de ikisi var.

Eksiklerin birbirini tamamlamaması tam da gizleyen şeydi: uzaktan bakınca ikisi
de korunmuş görünüyordu, çünkü her biri ikisinden birini taşıyordu.

## K-115 — yaş sırası

Gözleminizi kural yaptım: korumalar dersler biriktikçe eklendi, yani **en önce
kurulan en az korunuyor**, çünkü koruma ondan sonra icat edildi.
`experiments/decisions.csv` üretilen görünümlerin en eskisiydi ve tek nöbetçisi
olmayanıydı — tesadüf değil, şeklin kendisi. Sonraki süpürmeler yaş sırasına
göre.

**Sınırı yazılı:** sayım nöbetçinin *varlığını* ölçüyor, doğruluğunu değil.
Hiçbir şeyi karşılaştırmayan bir `--check` buradan geçer (K-106 bunun bir kez
olduğunun kaydı).

## Protokoldeki bayat sayı

"Dört CI kontrolü her PR'da yeşil" → "Beş CI işinin beşi de". Tarihsel
anlatıdaki "o günkü dört kontrol" tarihsel bırakıldı. Çeviriden önce, dediğiniz
sırayla.

## Kuyruk teslim listesine göre sıralandı

Rapora eklendi. **A:** setup-protocol çevirisi, skill spec, experiment matrix,
preregistration, analysis script, CV, sunum. **B:** pilot dataset ve raporu
(ön koşula bağlı). **C:** kalite pasları, yaş sırasına göre — ve K-110'un
geriye dönük taraması, yedi aday sınırlama, ters yöndeki beş kayıt **sona
gitti**, çünkü hiçbiri teslim listesini bloke etmiyor ve üçü de artık iki dile
çevrilen bir belgeyi büyütüyor.

## K-102: eklenen modül adları ve public tanımlayıcılar

`scripts/count_guards.py` — `generated_views`, `runners`, `parsed_interfaces`,
`main`, `ACCEPTED`, `WRITES`, `RUNNER_MARK`, `RUNNER_GUARDS`, `DOCUMENT`.
`scripts/setup/measure_band.py` — `run_identity`, `guard_written_condition`.
`scripts/setup/measure_rule_off.py` — `preflight`.

## #49 — setup-protocol çevirisi (978 satır, 795 çapa); çit ölçümü; kuyruk

- Branch: `protokol-cevirisi`
- Merged: 2026-08-26

<!-- body, verbatim except for task text -->

## setup-protocol çevirisi tamamlandı — iki dilli dalganın son borcu

978 satır çevrildi. **795 çapa iki tarafta birebir tutuyor** (644'tü). Bekleyen
çeviri **sıfır**: on belge iki dilli, dördü gerekçesiyle yalnız Türkçe.

Bölüm 6 belgenin yarısı ve en zoru — her maddesi ölçülmüş bir arızanın kuralı,
ve arızaların hepsi aynı aileden: bir şeyin kimse fark etmeden eksilmesi.

Kısmi iş K-119 gereği iki oturum boyunca `.en.partial.md` olarak dalda durdu ve
**o süre boyunca hiçbir denetim yanılmadı** — `PENDING` durumu değişmedi.

## Çit içi ölçümü: sınır kabul ediliyor, genişletilmiyor

İstediğiniz ölçüm koştu. Fenced bloklardaki **200** tanımlayıcı şekilli token,
**7** çözülmeyen ayrık token — ve yedisi de yanlış pozitif:

| token | ne olduğu |
|---|---|
| `Joyce`, `first_name` | örnek çıktıdaki kişi adı ve alan adı |
| `account_password`, `spotify_password` | alıntılanmış AppWorld prompt'undaki yerel değişkenler |
| `operate` | düz İngilizce sözcük |
| `retmedi`, `sonland` | satır sonuna bölünmüş Türkçe sözcük parçaları |

**Gerçek bayat ad sayısı sıfır.** Ölçütünüz gereği (sıfır ya da bir → kabul et)
nöbetçinin sınırı kabul edildi ve genişletilmedi. Fence ayrımı zor bir iş ve
ölçüm ödemeye değmediğini gösterdi.

Bulduğum tek bayat ad (`depolama_dayanikliligi`) elle yakalanmıştı ve zaten
düzeltildi — yani sınırın bilinen maliyeti dört addan biri, ve bir daha
tekrarlanmasını bekleyecek bir birikim yok.

## Ölçüm ikinci bir şey buldu

`experiments/` altında **17286** `.md` dosyası var ve **17282'si** `outputs/`
altındaki üretilmiş epizot günlüğü. Tanımlayıcı nöbetçisi hepsini tarıyordu.

Dışlandı: **12,78 saniye → 1,10 saniye**, aynı sonuç, aynı 795 çapa. Üretilmiş
metin hakkında bulgu üretmek zaten anlamsızdı.

## Kuyruk, ölçülerek

Rapora eklendi. Boşluk raporunun §5'i kaynak alındı ama **iki satırı bayat
çıktı** ve ölçümle düzeltildi: skill spec 318 satırla **var**, experiment matrix
**var**. Gerçekten olmayan üç madde: **CV, sunum, analiz betiği.**

**A — teslim listesi, yolu var:** CV → sunum → analiz betiği → preregistration →
experiment matrix → skill spec.

**B — sonuca bağlı:** pilot dataset, pilot report.

**C — kalite pasları, hepsi A ve B'nin arkasında**, yaş sırasına göre. Geriye
dönük kapanış taraması, yedi aday sınırlama, ters yöndeki beş kayıt ve nöbetçi
doğruluğu süpürmesi **bilerek en sonda**: hiçbiri teslim maddesini bloke etmiyor
ve dördü de artık iki dile çevrilen belgeleri büyütüyor.

## K-102: eklenen modül adları ve public tanımlayıcılar

`scripts/check_docs_parity.py` içinde `documents`. Yeni modül yok.

## #50 — Protokol çevirisi tamamlandı ve 32B ölçümü koştu (yığın 1/4)

- Branch: `protokol-ve-32b`
- Merged: 2026-08-26

<!-- body, verbatim except for task text -->

Yığılı dört PR'ın **birincisi** (K-141). PR #49 otuz dokuz commit taşıyordu ve
incelenemezdi; dört konuya bölündü, tarih yeniden yazılmadan, yalnız dal
işaretçisiyle. Bu PR'ın farkı tam olarak kendi on iki commit'i.

## Ne var

**Protokol çevirisi tamamlandı.** `experiments/setup-protocol.tr.md` kaynağı ve
`experiments/setup-protocol.en.md` çevirisi: 978 satır, 795 çapa. Kısmi iş dala
commit'lendi ve neden (K-119) yazıldı — tek bir devasa çeviri commit'i incelenemez.
Çeviri sırasında kaynakta dördüncü bir bayat tanımlayıcı çıktı ve düzeltildi.

**Çit içi ölçümü ve nöbetçi hızlandırması.** `scripts/count_guards.py` ölçülerek
sıralanmış bir kuyruk basıyor.

**Analiz betiği ön kaydın bağladığı analizi koşuyor** ve sentetik veriye karşı
sınandı: `scripts/analyze_pilot.py`, yapılandırması `config/analysis.yaml`,
testi `tests/test_analysis.py`.

*(Düzeltme: bu satır önce scripts/analyze_record.py diyordu — ters tırnaksız, çünkü öyle bir dosya
yok ve denetim ters tırnak içindekilere bakıyor. Yanlışı bulan şey `scripts/check_merged_artefacts.py` oldu — birleşmiş bir
PR gövdesinde adı geçen her eserin ağaçta olup olmadığını soruyor, ve bu onun
ilk gerçek yakalayışı.)*

**CV atıfları depodan çıkarıldı.** Kişisel gelişim malzemesi depoda durmuyor.

**Yollar yapılandırmaya taşındı** ve `REPRODUCE.md` temiz bir klondan baştan
yürütüldü (K-120, K-121).

**Kapanış raporu:** `docs/reports/kapanis-raporu.md` — depoda ne var, ne
doğrulandı, ne açık. Ölçüm tarihi 19 Ağustos 2026, commit `6c0ed5a`.

**32B ölçümü.** Şartlar ve yorum tablosu **koşudan önce** protokole yazıldı;
§14.4 daraltıldı ve §14.5 ölçümle düzeltildi. Künye nöbetçisi ilk denemeyi
reddetti — sebebi S-29'un artığıydı — ve seri 3 açıldı. Koşu sıfırdan büyük
çıktı: raporu `docs/reports/b32-olcumu.md`.

## Bu PR'ın kurmadığı

32B sonucu ilan edilen iki koşulda sapmış koştu; bunu ölçen tur C PR'ında.
Sapmanın kaydı `docs/09-limitations.tr.md` içinde `S-58`.

## #51 — Colab koşum ortamı kuruldu — koşu yok (yığın 2/4)

- Branch: `colab-ortami`
- Merged: 2026-08-26

<!-- body, verbatim except for task text -->

Yığılı dört PR'ın **ikincisi** (K-141). Farkı tam olarak kendi on dört commit'i;
öncesi PR #50 ile birleşti.

## Ne var: Colab koşum ortamı kuruldu

Yerel donanım 14B'yi taşımıyordu, yani eksenin uzatılabilmesi için bir koşum
ortamı gerekiyordu. Bu PR o ortamı kuruyor — **koşu yok**, ilk commit bunu
başlığında söylüyor.

**Önyükleme ve oturum bütçesi.** `scripts/colab_bootstrap.sh` ve
`experiments/colab/` altındaki defter; sonuçlar depoya itiliyor, oturum bütçesi
yazılı. Protokol §15 koşulları koşudan önce ilan ediyor (K-122).

**Klon adımı: sır komut satırından çıktı.** Jeton `argv`'ye giriyordu ve bir
`CalledProcessError` onu tam metin bastı. `GIT_ASKPASS` ile değiştirildi, ve
arıza artık kendini adlandırıyor. Doğrudan URL'nin özel depoda çalıştığı
ölçüldü; README'deki yanlış satır çıkarıldı.

**Yukarı akış LFS'i kapandı ve yansı kuruldu.** Ölçüldü, yansı `vendor/appworld/`
altına kondu, geri düşüşün sessiz olmadığı kanıtlandı. İki aday ortam ölçümle
ayrıldı; kaynağın kökeni `results/appworld-kaynak.json` içinde.

**Ollama adımı hiç koşmamıştı.** Sebep veri adımındaydı, sessizlik `set -e`'de
(K-127): boş bir dizin `[ -d ]` testinden geçiyordu.

**Ön koşullar önden ve topluca soruluyor.** `scripts/setup/check_prerequisites.py`
bütün eksikleri tek seferde raporluyor, ve zstd kuruluyor — Colab imajının onu
taşımaması bir ortam olgusu olarak kayda geçti.

**Yerleşiklik ölçümü hiç çalışmıyordu.** `residency()` var olmayan anahtarları
okuyordu, yani `fully_resident` her yerde False'tu. Canlı sunucuya karşı
kanıtlandı ve düzeltildi (K-131, K-132); üç madde de ölçüldü.

**Eksen 14B ile uzatıldı** (K-133) — bu da ilan; koşusu C ve D'de.

**Kalkanın girdisi `inputs/` altına taşındı.** Bir dizin dosyanın rolünü ilan
ediyor: `inputs/write-set-static.json` çıktı değil girdi.

**Sunucu günlüğü yolu tek çözümde birleşti** ve kapı ayarları koşudan önce
okunuyor.

## Bu PR'ın kurmadığı

İlan edilen koşullarla koşucunun okuduğu koşulların tuttuğu. O zincir C PR'ında
ölçüldü ve kopmuştu.

## #52 — Koşul zinciri ölçüldü, 32B ilan edildi, model adı tek kaynağa indi (yığın 3/4)

- Branch: `kosul-zinciri`
- Merged: 2026-08-26

<!-- body, verbatim except for task text -->

Yığılı dört PR'ın **üçüncüsü** (K-141). Üç commit.

## Ne var

**Koşul zinciri ölçüldü ve iki yerde kopmuştu.** Protokol §15.2 koşulları
**mutlak** yazıyordu — `max_output_tokens: 400`, `no_progress_limit: 15` — ve
yine tutmadı. Sebep ölçüldü:

- `max_output_tokens`: protokol 400 diyor, `config/recording.yaml` 4000 taşıyor
  ve koşucu oradan okuyor. 400 hiçbir zaman yapılandırmada olmadı.
- `no_progress_limit`: defter `--stop-threshold 15` geçiyordu ama
  `scripts/setup/measure_band.py` o bayrağı hiç tanımıyordu ve gerisini sessizce
  düşürüyordu.
- `shield_mode`: protokol `off` diyor, koşucu `shadow` kaydediyor. `ShieldMode`'un
  `off` üyesi yok; bu alan bir bayrakla düzeltilemiyor, ölçüm kararı bekliyor.

**Ders mutlaklık değil, tek kaynak** (K-136): yazılan yer ile okunan yer aynı
olmalı. `scripts/check_declared_conditions.py` ikisini karşılaştırıyor, ve
`src/zihin/declared.py` ilan edilen koşulların tek kaynağı oldu.

Kayıt `docs/09-limitations.tr.md` içinde `S-58`'in üçüncü örneği.

**32B eksene beşinci nokta, koşulları koşudan önce ilan edildi** (K-137).
Protokol §16, ve §16.3 gerekçesi. 14B koşusunun bu deklarasyondan **önce**
koştuğu ve değerlerle tesadüfen uyuştuğu açıkça yazıldı; tesadüf saklanmadı.

**Model adı altı yerden bire indi** (K-138). Önyükleme 14B hazırlarken ölçüm
32B istiyordu: doğru koşan ama yanlış özne üzerinde koşan bir denetim, düşen
denetimden kötü, çünkü başarı bildiriyor. Denetim artık öznesini kendi buluyor.

## Bu PR'ın kurmadığı

Beşinci noktanın koşusu; o D PR'ında.

## #53 — Eksen uzatıldı, seri birleşti, üç denetim kuruldu (yığın 4/4)

- Branch: `eksen-uzatma`
- Merged: 2026-08-26

<!-- body, verbatim except for task text -->

Yığılı dört PR'ın **sonuncusu** (K-141). On bir commit.

## Ne var

**Yerel eksen 4000 jetonla yeniden koşuldu.** Üç yerel nokta sıfırlarını 400
jetonlu bir bütçeyle almıştı; bütçe bağlayıcı olabilirdi. Yeniden koşuldu ve
sıfır kaldı: bütçe bağlayıcıydı ama bandı açan şey değildi. Koşulların üç ayrı
bölümü **koşudan önce** ilan edildi, ve koşu komutu tek kaynaktan geliyor.

**Geçiş incelemesi aleti.** `scripts/analyze_passes.py` bir taramanın geçişlerini
her görevin `ground_truth/evaluation.py` dosyasıyla birleştiriyor. Aynı turda
ilan tablosunun **başlığının** koşul sanılması düzeltildi.

**32B kaydı depoya girdi** (K-139). Colab oturumu kapandığı için tarama JSON'u
kaybolmuştu; veritabanı elle taşındı, provenance sekiz koşul alanı artı `boot_id`
ve `wall_clock_utc` üzerinden doğrulandı, ve JSON kayıttan yeniden üretildi —
neyin tam, neyin referanstan, neyin yeniden üretilemez olduğu alan alan yazılı.

**Seri 3 birleşti.** `scripts/merge_series.py` çakışan koşu kimliğinde duruyor,
tamsayı anahtarlarını ve yabancı anahtarları aynı miktarda kaydırıyor, sonra
sayıları ve `PRAGMA foreign_key_check`'i doğruluyor.

**Geriye dönük tavan denetimi koştu.** K-60'ın %10 eşiği vardı ve ön koşul
bulgusunun dayandığı üç koşu ona karşı hiç ölçülmemişti: `bant3` %0,0,
`bant3-kapali` %96,2, `bant2` kayıtta yok. Bulgu ayakta ama iki sıfır **alt
sınır**. Kayıt `S-63`.

**Eksen uzatma raporu**, iki dilli: `docs/reports/eksen-uzatma.tr.md` ve
`docs/reports/eksen-uzatma.en.md`.

**20/30 geri alındı ve tam hâli yazıldı.** Otuz görevin yirmisi bu hatla
çözülebiliyor; on üçü durma kuralı açıkken, yedisi kuralın kestiği görevler kural
kapalıyken tekrar koşulduğunda, ve o koşularda düşünme açıktı (`S-34`).

**Üç denetim kuruldu ve üçü de bulgu çıkardı.**

- `scripts/check_citations.py` — iki bayat atıf ve eseri olmayan bir sayı.
  Ardından: atıf alan eser **izlenmeli** kuralı (K-142). Taze klonda otuz atıfın
  on sekizi çözülmüyordu; dokuz eser izlenmeye alındı.
- `scripts/check_dates.py` — kendi tarihini yazan iki ek kayıtla tutmuyordu
  (K-140). Biri ilanı koşudan dört gün önceye taşıyordu; gerçek pay dört saat
  kırk dokuz dakika.
- `scripts/setup/measure_retriever_discrimination.py` — üç belgeye kopyalanmış
  bir sayının eseri: `results/retriever-discrimination.json`.

**`S-64`** birleşmemiş işin hiçbir denetimin öznesi olmadığını kaydediyor;
bu yığının kendisi o kaydın sebebi.

## Bu PR'dan sonra main güncel

Otuz dokuz commit dört PR'a bölündü, tarih yeniden yazılmadan. Dördünün de
sınır commit'i CI'da yeşil koştu.

## #54 — 32B deney hazırlığı: kırık işaretçi onarıldı, üç ölçüm alındı

- Branch: `deney-hazirligi`
- Merged: 2026-08-26

<!-- body, verbatim except for task text -->

32B deney ortamının kurulmasından **önceki** iş: karar gerektirmeyen bir onarım
ve üç ölçüm. Hiçbiri koşu başlatmıyor, hiçbiri üç açık kararı vermiyor.

## 1. Kırık işaretçi (K-143)

`ACTIVE_SERIES` "koşu nereye yazıyor" sorusunun cevabı, ve bir seri **şema**
sebebiyle açılıyor. Kütüphane ise madenlendiği serinin içinde duruyor. İki soru
tek işaretçiye bağlıydı; seri 3 açılınca cevaplar ayrıştı ve **yedi çağrı**
yanlış dosyaya sordu — en tehlikelisi `scripts/record_run.py`, çünkü kart isteyen
bir koşu epizot başladıktan sonra düşerdi.

`zihin.records.LIBRARY_SERIES` ve `open_library()` eklendi; yedisi de oradan
geçiyor. Cevap artık koşudan **önce** geliyor:
`scripts/setup/check_prerequisites.py` bir kütüphane satırı taşıyor. Desenin
kendisi `tests/test_library_source.py` ile çivilendi ve ateşlediği kanıtlandı.

İkinci eksen aynı hastalıktan: `scripts/setup/build_pilot_dataset.py` epizot
tarafını da hareketli işaretçiden okuyordu. `--database` açık bir argüman oldu.

## 2. Üç ölçüm

| Ölçüm | Eser | Sonuç |
|---|---|---|
| Maliyet | `results/compute-cost.json` | epizot 0,02695 sa; tasarım 2214 epizot = 66,3 sa oturum saati |
| Tip dağılımı | `results/task-types.json` | 123 görevin 105'i dünyayı değiştiriyor (%85,4), 18'i yalnız cevap |
| Biriktirme | `results/accumulation.json` | beceri eğrisi dışbükey (doygunluk yok), hata eğrisi düzleşiyor |

Üçü de deterministik ve model çağrısı gerektirmiyor. Sınıflandırıcı
`scripts/analyze_passes.py`'den alındı, ikinci bir kopya yazılmadı.

## 3. Bu turda açılan sınırlama

`S-65` — kayıtlı hata indeksi on beş kart taşıyor, bugünün korpusu yirmi
veriyor. Üç kollu koşunun kırk beş epizodu indeks kurulduktan sonra girdi ve hiç
madenlenmedi. Getiricinin bütün kapsama sayıları o eksik indeksten okundu, yani
**alt sınır**. Yeniden madenlemek bir tasarım kararı; bu PR yalnız boşluğu
ölçüyor.

## Kurmadığı

Üç karar açık: unit bütçesi, biriktirme durma ölçütü, ve indeksin ne zaman
tazeleneceği. Deney onlar verilmeden tanımlanmış olmuyor.

## #55 — Deney tanımını kapatacak üç ölçüm: aralık genişliği, tip tabakalaması, naif madenci

- Branch: `deney-tanimi`
- Merged: 2026-08-28

<!-- body, verbatim except for task text -->

Deney tanımını kapatacak üç ölçüm. Hiçbiri karar vermiyor; üçü de karar
girdisi üretiyor. Koşu başlatılmadı.

## 1. Asgari geçiş sayısı — `results/interval-width.json`

Soru dar tutuldu: birincil kestirim tavanda sansürlü kısıtlanmış ortalama ve
bütün görevleri kullanıyor, yani eşleştirilmiş kümeye ihtiyacı yok. Geçiş
oranının belirlediği şey kaç görevin **sıfırdan farklı** bir fark taşıdığı —
iki kolun da düştüğü bir görev tavan eksi tavan, yani sıfır katkı.

**Kestirici yeniden yazılmadı.** `scripts/analyze_pilot.py`'nin `paired`,
`restricted` ve `bootstrap_ci` fonksiyonları içe aktarıldı, tohum ve yineleme
sayısı `config/analysis.yaml`'dan geldi. İkinci bir kopya, koşulmayan bir analiz
hakkında cevap verirdi.

**İki ızgara, çünkü etkinin iki kanalı var ve ölçekleri bir mertebe farklı.**
Aynı görevi iki kol da çözerse fark birkaç çağrı; biri çözüp öteki çözemezse
fark tavan eksi o çağrılar, yani 20-150. Bir sansür dönmesi on tasarruftan
fazla oynatıyor, ve kapalı bir formül bunu vermiyor.

Kalibrasyon kayıttan: çapalar örneklemin kendi görev verisinden, tavan
protokolün `max(20, min(150, 2 x çapa))` kuralı, geçen epizot maliyeti kayıttaki
42 geçen epizottan, gürültü ölçülmüş değişim katsayısından.

## 2. Görev tipi tabakalaması — `results/task-types.json`

Karar uygulandı: cevap tipi görevler **çıkarılmıyor**, tabakalanıp **ayrı**
raporlanıyor. Ön kayda 28 Ağustos 2026 tarihli ve **keşifsel** etiketli bir ek
girdi; tip ayrımının sonuçlar görüldükten sonra yapıldığı orada yazılı.

Gerekçe ölçüldü: cevap tipi görevlerin **hepsi** "hiçbir model değişmedi" testi
taşıyor — hiçbir şey yapmayan bir ajanın tanım gereği geçtiği test — ve test
medyanları **iki**. Eylem tipinde o test **hiç yok** ve medyan **yedi**.

Karar kaydı `K-144`.

## 3. Naif madenci — `results/naive-miner.json`

`scripts/setup/compare_naive_miner.py`: sabit uzunlukta **bitişik** n-gram, aynı
alfabe, destek yine ayrık göreve göre. Beş şey kaldırıldı — kapalı örüntü
süzgeci, boşluk toleransı, argüman sınıflandırması, etki soneki şartı, etki
sonekine göre birleştirme.

Ölçüt koşudan önce ilan edilmişti ve hükmünü verdi. Karar kaydı `K-145`.

## Bu turda açılan sınırlama

`S-66` — aralık genişliği taramasının gürültü modeli kayıttaki **iki** tekrarlı
geçen hücreden geliyor. Yönü belli: gerçek değişkenlik büyükse aralıklar
raporlanandan geniş olur, yani tablodaki her genişlik bir **alt sınır**.
Tablonun şekli bundan etkilenmiyor, çünkü şekli sansür belirliyor.

## Kurmadığı

Üç karar açık: hangi geçiş oranıyla koşulacağı, biriktirmenin durma ölçütü, ve
hata indeksinin ne zaman tazeleneceği (`S-65`).

## #56 — Geçiş oranı eşiği ön kayıttan türetildi; üç sonucun üçü de çıktı

- Branch: `esik-turetmesi`
- Merged: 2026-08-28

<!-- body, verbatim except for task text -->

Eşik seçilmedi, türetildi. Ön kayıttaki her ayrım örtük bir aralık genişliği
şartı taşıyor; şartlar çıkarıldı, `results/interval-width.json`'daki ölçülmüş
genişliklerle çaprazlandı, ve eşik **en büyük şartın** okunur hâle geldiği oran
olarak alındı.

## Yöntem

**Her şart tek bir ölçülen niceliğe indirgeniyor.** Birincil aralığın genişliği
`w`, birincil etki `d`. Türetilmiş bir nicelik hakkındaki ilan — bir alt küme,
iki farkın farkı, tek bir kol — o niceliğin genişliğini ister, ve o genişliğin
`w`'ye oranı **örneklemin yapısal bir olgusu**. İki oran ölçüldü: alt küme
1,42×, çıkarıcı kontrol 0,82×. Geriye kalan her şart `w/|d|` üzerinde bir sınır.

**Üç pay ilan edildi, ölçülmedi, ve adları yazılı.** Ön kayıt hacim etkisinin
payını, tek kolun payını, ve iki eksen noktasının ayrışma miktarını söylemiyor.
Muhafazakâr ve cömert iki küme tarandı; **ikisi de aynı eşiği** verdi, çünkü
bağlayıcı şart bu paylardan bağımsız.

## Üç sonuç önceden yazılmıştı, üçü de çıktı

1. **Beş ayrım bir oranda okunur hâle geliyor** — 0,10 ile 0,65 arasında.
2. **İki ayrım hiçbir oranda okunmuyor**, beklenen etki %10 iken. Kusur değil,
   tasarımın taşıyamadığı iddialar: `S-67`.
3. **Türetilen eşik ölçülen oranın üstünde.** 32B nitelemiyor ve deney bu
   hâliyle güçsüz: `S-68`.

## Bir düzeltme, ölçümden çıktı

Ölçülen oran **0,367 değil 0,280**. 11/30 iki tabakayı karıştırıyor; K-144'ten
sonra birincil örneklem eylem tabakası ve orada 7/25. Fark tam da hiçbir şey
yapmayan bir ajanın bedava test topladığı tabakadan geliyor.

## Türetilmeyenler de sayıldı

Kapsama ve tavana çarpma eşikleri farklı nicelikler. Tanı metriğinin eşiği ve
ayar bütçesinin sayısı **hiç ilan edilmemiş**. Ters U ilanın kendisinde
onaylayıcı sayılmıyor. **Negatif aktarım eşiği diye bir ilan depoda yok.**

`S-66` her satırda: gürültü katsayısı iki hücreden ölçüldü, yani her genişlik
alt sınır ve türetilen her eşik iyimser tarafta.

Karar `K-146`; ön kayda 28 Ağustos 2026 tarihli, keşifsel etiketli ek girdi.

## #57 — Staj sonuç raporu depoya girdi, iki dilli

- Branch: `staj-raporu`
- Merged: 2026-08-28

<!-- body, verbatim except for task text -->

Staj sonuç raporu `docs/` altına, iki dilli konvansiyona uygun:
`docs/13-internship-report.tr.md` kaynak, `docs/13-internship-report.en.md`
çeviri. Eş denetiminde ilan edildi; çapa sayımı temiz (1001 çapa).

## Sayılar kayda karşı tarandı

Rapordaki her sayı kayıttan doğrulanmaya çalışıldı. **Doğrulananlar** (eseriyle):

296/19 (`inputs/write-set-static.json`), %4,1 ve %0,07
(`results/shield-cost.json`, `results/shadow-mode.json`), 100/38/4 ve 69 kart
(`results/naive-miner.json`), 767 (`results/failure-substrate.json`), 15 kart ve
11 yetki reddi (`results/zihin-2.sqlite`), kapsama %94,7-100
(`results/retrieval-coverage.json`), 21 kümesi ve %20,8
(`results/retriever-discrimination.json`), 45 epizot ve 4/15-11/15
(`results/card-arms.json`), eksenin dört satırı (`results/b15l-taramasi.json` ve
kardeşleri), 105/18 (`results/task-types.json`), 7/25 ve 4/5, 0,280, 0,75-0,85,
1,42 (`results/pass-threshold.json`), 66 saat (`results/compute-cost.json`),
13/16/7/20 (`results/sinir3-kontrolu.json`), demo 20 -> 11
(`results/card-demo.json`), telefon 30 (`results/app-proxy-accuracy.json`),
146 karar ve 57 sınırlama.

**Sayılar bu PR'da değiştirilmedi.** Tutmayanlar ve eseri olmayanlar ayrıca
listelendi; düzeltme kararı kullanıcıda.

## #58 — Rapor denetiminin eser gerektiren beş bulgusu kapandı

- Branch: `rapor-duzeltmeleri`
- Merged: 2026-08-28

<!-- body, verbatim except for task text -->

Denetimin dokuz bulgusundan **eser gerektiren beşi** kapandı. Dört metin
düzeltmesi kullanıcıda ve bu PR onlara dokunmuyor.

## Bir düzeltme: maliyet hesabım yanlıştı

`105 × 5 × 3` kullanmıştım. K-144 tabakalıyor, **çıkarmıyor** — cevap tipi
görevler de koşuluyor, yalnız ayrı raporlanıyor. Doğrusu `123 × 5 × 3 = 1845`
epizot = **55,2 oturum-saati**, ve alt sınır. Varsayım `results/compute-cost.json`
içine yazıldı.

## 1. Deney matrisi ve aynı desenin taraması

Dokuz `naive_compiler` satırı yerinde duruyor, durumları K-145'in gerekçesini
taşıyor; canlı hücre **45**. `config/naive_compiler.yaml` künyesini aldı ama
silinmedi — silinip silinmeyeceği bir tasarım kararı.

K-145'ten sonra "altı koşul" diyen **sekiz** yer bulundu ve üçe ayrıldı:
tasarımı anlatanlar beşe çevrildi, ilan olanlara ek yazıldı, `config/` altındaki
dosya sayısını anlatanlara dokunulmadı.

## 2. Üç eser

| Eser | Ne söylüyor |
|---|---|
| `results/failure-index-build.json` | indeks kurulurken **22 grup, 15 kart, 7 elenen**; bugün 28/20/8 |
| `results/gpt4o-kesisim.json` | yayımlanmış koşu otuz görevin **15**'ini çözüyor |
| `results/recorded-faults.json` | **22** sessiz arıza (tanımıyla), **16** tasarım kararı |

Raporun 22'si ve 15'i **doğruydu**; eksik olan eserdi.

## 3. İki sayı

Sessiz arızanın tanımı üç sınamayla yazıldı ve sınıflandırma saklandı, çünkü
sayı değil tanım tartışılır olmalı. Dış incelemenin kararları paragraf paragraf
sayıldı — belgenin kendi yapısı bir paragraf bir karar.

## 4. Rapor güncellendi

Atıf tablosu eklendi ve `scripts/check_citations.py` artık raporun iki dilini de
okuyor. **Seksen iki atıfın seksen ikisi çözülüyor**, ve her biri hem var hem
git tarafından taşınıyor.

## #59 — Raporun üç metin düzeltmesi ve sessiz arıza tanımı

- Branch: `rapor-kapanis`
- Merged: 2026-08-28

<!-- body, verbatim except for task text -->

Denetimin dokuz bulgusundan kalan üçü, iki dilde de. Rapor bununla kapanıyor.

| # | Düzeltme | Sebep |
|---|---|---|
| 1 | `%7,0` → `%6,7` | 2/30 = 6,67; eksen uzatma raporu zaten %6,7 diyordu |
| 2 | "üç şey" → "dört şey" | §5'in giriş cümlesi altındaki tabloyu yanlış sayıyordu |
| 3 | "görevi yaptı" → "kartın etki sonekine ulaştı" | `results/card-demo.json` geçiş kaydetmiyor; ölçtüğü şey `successful_effect_step` |

Üçüncüsü en önemlisi: "görevi yaptı" kaydın desteklediğinden fazlası, ve tam
olarak **geri çekilen iddianın sınıfından** — tek bir epizottan davranış sonucu
okumak.

## Sessiz arıza sayısı tanımıyla §11'e girdi

Üç sınama açıkça yazıldı (arıza mı, sessiz miydi, başkası mı buldu), sayı
**sınırlama kayıtlarının elli yedisinden yirmi ikisi**, ve **tabanlık** niteliği
yanında: sayım yalnız sınırlama kayıtlarını kapsıyor, karar kaydı aynı türden
başka arızalar taşıyor — §11'in kendi örneklerinden biri, yerleşiklik denetimi,
orada — ve yüz kırk altı karar bu tanıma karşı sınıflandırılmadı.

Sınıflandırma kayıt kayıt `results/recorded-faults.json` içinde. Tartışılması
gereken şey tanım, ve listesiz bir sayı tartışılamaz.

## `config/naive_compiler.yaml` kalıyor

Silinmedi. Silmek K-145'i **doğrulanamaz** kılardı: ölçütün neyi düşürdüğü,
düşürülen şeyin ne olduğu görülmeden okunamaz. Dosya künyesini taşıyor, koşacak
bir koşul olarak okunmuyor.

**Seksen dört atıfın seksen dördü çözülüyor.**

## #60 — İki kapanış yolu fiyatlandırıldı; (a) ölçülen her model için kapalı

- Branch: `yol-fiyatlandirmasi`
- Merged: 2026-08-28

<!-- body, verbatim except for task text -->

Güç sorununun üç kapanış yolundan ikisi fiyatlandırıldı. **Yol seçilmedi.**

## Yorum ölçümden önce yazılmıştı

DeepSeek'in eylem tabakasındaki oranı 0,75 ve üstündeyse (a) ilkece var; altındaysa
(a) ölçülen her model için kapalı ve seçim (b) ile (c) arasına iner.

## (a) yolunun tavanı — `results/stratum-rates.json`

| Koşu | Toplam | **Eylem tabakası** | Cevap |
|---|---|---|---|
| DeepSeek V4 Flash, birleşim | 20/30 | **15/25 = 0,600** | 5/5 |
| — durma kuralı açıkken | 13/30 | 8/25 = 0,320 | 5/5 |
| — kuralın kestiklerinde kural kapalıyken | 7/30 | 7/25 = 0,280 | 0/5 |
| gpt-4o, yayımlanmış | 15/30 | **10/25 = 0,400** | 5/5 |
| `qwen2.5-coder:32b` | 11/30 | 7/25 = 0,280 | 4/5 |
| `qwen2.5-coder:14b` | 3/30 | 1/25 = 0,040 | 2/5 |

**İkinci dal ateşledi.** DeepSeek bu projenin ölçtüğü en yüksek nokta ve eşiğin
altında.

Manşet oranın neden yanılttığı sayıyla görünüyor: yeterince güçlü her koşu cevap
tabakasının **beşte beşini** çözüyor. O tabaka doyuyor, çünkü orada hiçbir şey
yapmayan bir ajanın bedava geçtiği bir test var (K-144).

Yan gözlem: kural kapalıyken gelen **yedi geçişin yedisi de eylem tipi**. Durma
kuralı kestiği yerde seçici değildi.

## (b) yolunun fiyatı — `results/sample-size.json`

Oran 0,280'de sabit, yalnız örneklem büyüyor. Ezberleme kapısı **500 eylem
görevinde** menzile giriyor (beklenen etki %20 ve üstü); %10'da havuzun tamamında
bile girmiyor.

Beş yüz görev = bugünkü 105 + `test_challenge`'ın 408 eylem görevinden **395**'i.
Ayrılmış küme tanımı değişir. Hesap tarafı **~225 oturum-saati**, bugünkünün dört
katı.

Kaba kestirim ~282 diyordu, ölçüm **500** dedi; fark genişliğin kök-n ile
gitmemesinden.

`S-66` iki fiyatın da altında: gerekli boyut bir **alt sınır**.

## #61 — (c) yolu seçildi ve koşudan önce ilan edildi; alternatifler defteri açıldı

- Branch: `onaylayici-daraltma`
- Merged: 2026-08-28

<!-- body, verbatim except for task text -->

Güç sorununda **(c)** seçildi ve **koşudan önce** ilan edildi.

## 1. Onaylayıcı küme daraltıldı

`Y-2` (ezberleme) ve `Y-6`'nın birinci dalı (hacim kontrolü) onaylayıcı kümeden
çıktı. İkisi de **yönsel** raporlanmaya devam ediyor — kazanç görülmüş ve
görülmemiş görevlerde ayrı ayrı, alakasız kolun tabana göre farkı ayrı.
Yazılmayan tek şey **hüküm**.

Kalan onaylayıcı ayrımlar: `Y-1`, `Y-6`'nın ikinci dalı, `Y-4`/`Y-5`.

**Korunması istenen ayrım kayda geçti.** Bu kapılar sonuç hoşa gitmediği için
değil — sonuç yok, deney koşmadı — **bu örneklem boyutunda hüküm üretemedikleri**
için çıkarıldı, ve bunu ölçen kayıt `S-67`. İkisi dışarıdan aynı görünür; ayıran
şey zamanlama ve gerekçenin kaynağı, ikisi de kayıtlı.

**Kapılar silinmedi.** Özgün ilanları `docs/11-falsification.tr.md` içinde
yerinde, altlarına tarihli ek düşüldü.

## 2. Tırmanma tetiği

Deney 105 eylem görevinde koşulduğunda `Y-1`'in aralığı sıfırı **dışlayamazsa**
(b) yoluna geçiliyor. Birincil sonuç okunuyorsa (b) gerekmez. Tetik sonuç
görülmeden konuldu.

## 3. "Ne gerekirdi" bir sonuç olarak — `K-149`

500 eylem görevi, `test_challenge`'ın 408'inin 395'i, 7500 epizot, ~225
oturum-saati.

Ve asıl nitelik **ölçüldü**: bu hassasiyeti artırmak değil **ölçülen şeyi
değiştirmek** olurdu.

| eylem görevleri | n | çapa medyanı | ortalama | en büyük | çapa ≥75 |
|---|---|---|---|---|---|
| `test_normal` | 105 | 31,0 | 32,8 | 126 | **%2,9** |
| `test_challenge` | 408 | 25,0 | **47,6** | **649** | **%12,5** |

Kuyruk uzuyor, tavan dağılımı kayıyor, popülasyon değişiyor.

## 4. Alternatifler defteri — `docs/14-alternatives-ledger.tr.md`

Kapanmıyor. (a) ölçümle kapalı, (b) ertelendi ve fiyatlı, (c) seçildi, (d)
çerçeve dışı ve **slot boş** — boşluğu da yazılı, çünkü adaylandırılmadı.

`S-66` dört satırın da altında: eşik de 500 de alt sınır.

**Doksan atıfın doksanı çözülüyor.**

## #62 — Tetiğin onayı kayda geçti; biriktirme koşusu koşudan önce ilan edildi

- Branch: `biriktirme-hazirligi`
- Merged: 2026-08-28

<!-- body, verbatim except for task text -->

Tetiğin onayı kayda geçti, biriktirme koşusu **koşudan önce** ilan edildi.

## 1. Tetiğin ara durumu

Metin değişmedi. Eklenen tek şey **onayın nasıl alındığı**: tetik 28 Ağustos'ta
yazıldı ve o anda onayı **varsayılmıştı**; aynı gün ayrı ve açık bir beyanla
onaylandı. İki an arasında metin değişmedi ve hiçbir sonuç görülmedi — ama
"varsayımla yazıldı, sonra onaylandı" ile "açık onayla yazıldı" aynı şey değil,
ve ikincisi gibi göstermek bu belgenin engellemek için var olduğu düzleştirme
olurdu.

## 2. Protokol §18, iki dilde

Şartlar mutlak değerle (`bir1`), durma ölçütü iki dallı, indeks kütüphaneyle
aynı blokta (`S-65`), yorum üç dal artı `K-104`.

**Şartlar tek kaynaktan doğrulandı, koşudan önce:**

```
declared in section 18.2 : 11 field(s)
declared conditions and the run agree
```

On alanın onu koşunun okuyacağı yerle karşılaştırıldı ve tuttu. `S-58` üç kez
koşudan *sonra* koşmuştu.

## 3. Koşucu

`scripts/setup/run_accumulation.py` — `train`'in doksan görevi, tek tohum, her
otuz epizotta iki üretici **birlikte**, durma kararı defterden.

Dört nöbetçinin dördü yerinde: şema kısıtı, koşul guard'ı, devam denetimi, ön
kontrol. Yapısal sayım `resume_check`'in eksik olduğunu yakaladı ve eklendi.

## 4. `K-143`'ün açık bıraktığı boşluk kapandı

O kayıt "kütüphane yeniden madenlenirse `LIBRARY_SERIES` satırının taşınması
gerekir; bunu hatırlatan bir denetim yok" diyordu. Bu koşu **her otuz epizotta**
madenliyor, yani boşluk ilk blokta ısırırdı.

Ön koşul denetimi artık aktif seride daha çok beceri varsa **düşüyor**:

```
MISSING | library pointer | results/zihin-3.sqlite now carries 1 skill(s)
          but LIBRARY_SERIES still names results/zihin-2.sqlite
```

Ateşlediği kanıtlandı. Koşucu da blok sınırında aynı şeyi yazıyor.

## 5. Önyükleme süresi ölçülüyor

`scripts/colab_bootstrap.sh` adım adım kendini zamanlıyor ve
`results/colab-bootstrap.json` yazıyor. 55 saatin alt sınır olmasının sebebi
buydu ve hiç ölçülmemişti.

`K-150`. Doksan atıfın doksanı çözülüyor.

## #63 — Defter main'i çekiyor, ve bayat bir kopya kendini söylüyor

- Branch: `colab-dal-ve-bayat-kopya`
- Merged: 2026-08-28

<!-- body, verbatim except for task text -->

İki şey, ve ikisi de aynı arızanın iki yüzü.

## 1. Defter `main`'i çekiyor, ve ad tek yerde

Defter `protokol-cevirisi`'ni çekiyordu. O dal birleşti, `main` ilerledi, ve
defter eski tepeyi çekmeye devam etti — temiz bir Colab kurulumunda
`run_accumulation.py` yoktu.

Ad **üç yerde** duruyordu: defterin `ZIHIN_REF` varsayılanı, README'nin doğrudan
bağlantısı, README'nin adım listesi. Her birleşmeden sonra üçü elle
güncellenmeliydi ve bir kez unutulunca hiçbir şey itiraz etmedi.

Üçü de `main`, ve `tests/test_colab_ref.py` üçünün **aynı** adı söylediğini,
o adın `main` olduğunu, ve bayat dal adının hiçbir yerde kalmadığını çiviliyor.
Ateşlediği kanıtlandı.

## 2. Bayat kopya kendini söylüyor

Asıl mesele buydu: `FileNotFoundError` "bu dosya hiç yazılmadı" diye okunur, ve
ilk okuma "ajan eksik yapmış" oldu. Dosya yazılmıştı; **kopya bayattı**.

Ön koşul denetimi artık soruyor. `S-64` bu komutu zaten adlandırmıştı:

```
MISSING | working copy | HEAD at e6cc828 is 23 commit(s) BEHIND origin/main;
          files added in those commits are absent here and will look like
          they were never written
        | git fetch origin && git checkout main && git reset --hard origin/main
```

Bu çıktı gerçek: `e6cc828`'e alınmış bir worktree'de koşturuldu, tam olarak
kullanıcının gördüğü durum.

**Tazeliyor**, çünkü kendisi bayat bir `origin/main` ile karşılaştırmak hiçbir
şey cevaplamaz. Tazeleme başarısızsa cevap **bilinmiyor**, ki *güncel* ile aynı
şey değil (`K-131`).

`S-64`'e tarihli ek düşüldü ve **öbür yarısının açık kaldığı** yazıldı: hiç
birleşmemiş iş hâlâ hiçbir denetimin öznesi değil.

`K-151`. Doksan atıfın doksanı çözülüyor.

## #64 — Defter depodan açılıyor; denetimin öznesi olmayan kopyalar S-69'a girdi

- Branch: `defter-tek-kaynak`
- Merged: 2026-08-28

<!-- body, verbatim except for task text -->

**Doğru denetim, yanlış özne — bu turda üçüncü kez.**

Depodaki defter `main`'i çekecek şekilde düzeltildi ve `tests/test_colab_ref.py`
bunu çiviledi. Koşan eser o dosya değildi: Drive'a kaydedilmiş kopya hâlâ
birleşmiş bir dalı çekiyor. **Test yeşildi, koşan eser bayattı.**

## 1. Kural yazıldı

Defter her oturumda **depodan** açılıyor; Drive'a kaydedilmiş bir kopya
kullanılmıyor. `experiments/colab/README.md`'nin en başında bir kutu olarak, ve
`REPRODUCE.md`'de "Elinizdeki kopya denetimin öznesi değil" başlıklı bir bölüm
olarak.

## 2. `S-69` — sınır kaydedildi

**Bir denetim okuduğu ağaç hakkında konuşuyor.** Kullanıcının elindeki kopyalar o
ağacın dışında, ve bunu kapatan bir mekanizma yok. İki sebep yazılı:

- **Defterin içine konan bir öz-denetim kapatmıyor.** Kaydedilmiş **bayat** bir
  kopya **bayat bir denetim** taşır; bir denetim kendisinden önceki bir sürümünü
  yakalayamaz. Bugün eklenecek bir öz-denetim yarınki kopyalara yarar, bugün elde
  olana yaramaz.
- **Bayatlık denetimi bir tur geç.** `K-151` klonlamadan **sonra** koşuyor;
  klonlamayı yapan eser zaten bayatsa, yanlış dalı çekmesi denetimden önce olup
  bitiyor.

**Sınırın sınırı da yazılı:** bu yalnız defter için değil. Drive'daki veritabanı,
indirilmiş bir tarama, bir hafta önce çekilmiş bir klon, elle taşınmış bir kayıt
— hepsi aynı durumda. `K-139` elle taşınan bir kaydı doğrulamayı kural yapmıştı;
`S-69` o kuralın **neden** gerektiğini genelleştiriyor.

**Sınıfın üç örneği yan yana yazıldı:** `K-138` doğru koşup yanlış model hakkında
cevap verdi, `K-142` doğru soruyu yanlış kümede sordu, bu üçüncüsünde doğru dosya
doğrulandı ama başka dosya koştu. Ortak yanları: denetim **öznesini kendi
seçmiyor**.

**Kapanma sınıfı kalıcı kayıt.** Yazılan şey bir azaltma, kapatma değil — ve bir
kural bir denetim değil; uyulduğunu gösteren şey yok.

## #65 — Temiz kurulumun çıkardığı üç arıza: özne, taban, ve eksik bir satır

- Branch: `temiz-kurulum-uc-ariza`
- Merged: 2026-08-28

<!-- body, verbatim except for task text -->

Üçü de ölçüldü, sonra düzeltildi.

## 1. Kütüphane gereksinimi — cevap **hayır**, ve döngüsellik gerçek

Biriktirme koşusu kütüphaneyi **okumuyor**: `scripts/setup/run_accumulation.py`
hiçbir kart bayrağı geçmiyor, `scripts/record_run.py` kütüphaneyi yalnız
`--cards` ya da `--irrelevant-cards` verildiğinde çözüyor.

**Ve okumamalı da.** Kartlı koşsaydı korpus sınanacak mekanizmayla kirlenir, o
korpustan madenlenen kütüphane **döngüsel** olurdu.

Protokol §18.2'ye `Koşul | baseline` satırı girdi ve
`scripts/check_declared_conditions.py` onu **koşucunun kaynağından** çözüyor. Ön
koşul denetimi `--prefix` alıyor:

```
[  ok  ] skill library    not read by bir1: its declared condition is baseline
[  ok  ] library pointer  not read by bir1
```

**Bu sınıfın dördüncü örneği**: `K-138` yanlış model, `K-142` yanlış küme,
`S-69` yanlış dosya, bu da yanlış koşu tipi.

## 2. `check_language` — ikisi de doğru değil

| Korpus kaynağı | Dizge |
|---|---|
| dosya ve dizin adları | 194 |
| izlenen `results/*.json` | 1832 |
| izlenmeyen `results/*.json` | 854 |
| **kayıt (`*.sqlite`)** | **12308** |

Taze klonun korpusu **2026**, tabanı **1000** — taban aşılıyordu, denetim eksik
korpusla cevap veriyordu, ve yalnız kayıtta bulunan 67 veri anahtarı düzyazı
sanıldı.

**Taban bir kez ateşliyordu.** `K-142` on iki eseri izlemeye alınca taze klon
korpusu **254 → 2026** çıktı ve tabanı aştı. Bir boşluğu kapatan değişiklik başka
bir nöbetçiyi sessizce silahsızlandırdı.

Taban artık **kaydın katkısına** bakıyor. Taze klon cevap vermiyor, **çekiliyor**
(çıkış 1).

**Ve CI bu denetimi hiç koşmuyor.** "CI yeşil, taze klon kırmızı" iki cevap
değil — **bir cevap ve bir sessizlik**.

## 3. Jeton boşluğu — iki satır

Defter `os.environ`'a yalnız `GITHUB_TOKEN` yazıyordu. `GIT_ASKPASS` ve
`GIT_TERMINAL_PROMPT` yalnız o hücrenin yerel sözlüğündeydi, ve `K-124` jetonu
URL'den çıkardığı için klonda `credential.helper` de yok. Sonraki her süreç
jetonu **taşıyor ama git'in alacağı bir yol yok**.

İkisi de artık `os.environ` içinde. Jeton hâlâ URL'de değil, `argv`'de değil, git
config'inde değil.

`K-152`.

## #66 — Yetenek eklendi, çağıran öğretilmedi; ve 'önek yok' artık bir cevap değil

- Branch: `cagiran-ve-varsayilan`
- Merged: 2026-08-28

<!-- body, verbatim except for task text -->

Haklısın: yeteneği ekledim, çağıranı kontrol etmedim. **Beşinci kez aynı desen.**

## 1. Defter öneği geçmiyordu — ve iki kat bayattı

`%env ZIHIN_PREFIX` yoktu, yani `--prefix` hiç ulaşmıyordu.

**Ama daha kötüsü vardı:** `run_command()` defterde `measure_band.py` arıyordu.
Defter başka bir koşucuya geçtiği gün arama **sessizce boş** dönecekti — yani
"defterden türet" yolu da çalışmayacaktı.

**Ve defterin koşu hücresi zaten bayattı:** `measure_band.py b32c` koşuyordu.
Uçtan uca koşulsaydı biriktirme değil, **önceki 32B bant taraması** yeniden
koşacaktı.

Kural değişti ve bayatlayamaz hâle geldi: bir koşu komutu, **protokolün şartlar
bölümü ilan ettiği bir öneği adlandıran** kabuk satırıdır. Önekler protokolden
geliyor, yani liste tek kaynaktan.

```
ilan edilen önekler: ['b14', 'b15l', 'b32c', 'b3l', 'b7l', 'bir1']
koşu komutu        : uv run python scripts/setup/run_accumulation.py bir1
önek               : bir1
```

Çevre değişkenine gerek kalmadı — denetim öneği defterin **kendi koşu
komutundan** türetiyor, yani `ZIHIN_PREFIX` diye ikinci bir yer yok.

## 2. Varsayılan sorusu — haklısın, değiştirdim

Geniş koşmak **olmayan bir gereksinimi sorup koşuyu durdurmak** demekti. Üç
kaynak sırayla deneniyor — komut satırı, defterin koşu komutu, koşucunun kendisi
— ve hiçbiri cevap vermezse:

```
[  ??  ] skill library    b32c declares no condition and its runner could not be
                          read, so whether it needs the library is not known
[  ??  ] library pointer  not asked: the run type is not known
```

`K-131`'in deseni: belirlenemedi bir hayır değil, ve varsayılan bir cevap değil.

**Geri düşüş öneğe bağlandı:** defterin komutu yalnız **o öneği adlandırıyorsa**
o koşunun komutu sayılıyor. Başka bir koşunun komutunu okumak tam olarak bu
çözümleyicinin engellemek için var olduğu şey olurdu.

## Çağıran teste bağlandı

`tests/test_colab_ref.py` artık defterin koşu komutunun ilan edilen bir öneği
adlandırdığını **ve** şartlar bölümündeki komutla aynı olduğunu çiviliyor.
Ateşlediği kanıtlandı.

Bir test de düzeltildi: `test_declared_conditions` defterin o anki öneğini
**harfiyen** bekliyordu (`b32c`), yani her koşu değişiminde kırılıyor ve
çözümlemenin çalışıp çalışmadığı hakkında hiçbir şey söylemiyordu. Artık
değişmezi sınıyor.

`K-153`.

## #67 — Dokunulan liste kayıttan, seri 3 tek dosyada, birincil model ilan edildi; üç tasarım ilanı

- Branch: `touched-list-and-primary-model`
- Merged: 2026-09-25

<!-- body, verbatim except for task text -->

İki turun işi: dokunulan görev listesi kayıttan üretiliyor, seri 3 tek dosyada, birincil hücrenin modeli ilan edildi, ve üç tasarım ilanı. Her düzeltmenin ateşlediği mutasyonla gösterildi; ayrıntı commit iletilerinde ve kararlarda.

## 1. Dokunulan görev listesi (K-166)

`results/dokunulan-gorevler.json` → `results/touched-tasks.json`, artık `scripts/setup/build_touched_tasks.py` ile kayıttan üretiliyor. `test_normal` 45 → **49** (`0a9d82a_1/2/3`, `0de03ea_1` kayıtta vardı, listede yoktu), `train` 13 → 90, `test_challenge` 0. Değerlendirme örneklemi 123 → 119; eylem tabakası 105 → **104**.

Nöbetçi üç katmanlı: dört okuyucu listeyi yalnız `load_touched` üzerinden okuyor (kayıt tamsa türetip farkta, `test_challenge`'da tek epizotta reddediyor); `local_checks.sh`'de `--check`; CI'da yapı, köken ve sentetik kayıtta mutasyon testleri.

## 2. Seri 3 (K-165, K-171, K-172, K-173; S-74)

Yerel yarı (`b3l`, `b7l`, `b15l`, `b32`, 120 epizot) kayda geri kondu: 389 epizot. Bölünme 26 Ağustos'tan beri sürüyordu ve 13 Eylül'de yerel yarı depodaki kayıttan düşmüştü. `run_ledger` gerçek kayda hiç girmemişti (şema değişikliği son `bir1` epizodundan bir saat sonra geldi); göç önce kopyada, sonra kayıtta uygulandı. `verify_series_merge.py --check` sürekli denetim; Colab önyüklemesi Drive'daki seriyi bağlamadan önce onunla doğruluyor ve tutmazsa ya da yoksa duruyor.

## 3. Aşağı akış

Beş çıktı birleşik kayıtla yeniden üretildi; `measure_sample_size`'daki üç kopya sayı türetiliyor; `derive_pass_threshold`'un varsayılanı 9 (S-75). K-149'un 500'ü bir dağılım: %20'de 400–557, %30'da 500–557 (2/7 ulaşılamaz), %50'de 400–500 (1/7), %10'da hiçbirinde (K-168). Aralık genişliği taraması eylem tabakasında (`results/interval-width-action.json`); havuzlanmış tablo süperseded işaretli, Grid B medyanda %26 daha geniş (K-174).

## 4. Birincil hücre ve ön kayıt

A.2'ye ek: model `qwen2.5-coder:32b-instruct-q4_K_M`; keşifsel etiket yalnız seçime bağlı, `Y-1` onaylayıcı (K-169). K-133'e onay kaydı; S-14'ün "yukarı kaydırılır" aşırı aktarımına K-133, A.11 ve eksen uzatma raporunda düzeltme. A.5'in örneği tek epizot ve tekrarlanmadı (S-77). `check_dates` işaretleri çift çift tutuyor (Düzeltme / Correction).

## 5. Üç tasarım ilanı

- **`min_expected_saving = 1`** (A.4, K-175): en yüksek destekli beceri (`POST spotify.auth/token`, destek 27) düşüyor — 28 oluşumun 28'i tek adım, kazandırabileceği model çağrısı yok. Getirilebilir beceri 11 → 8; 25 görev bir kart kaybediyor, kapsama değişmiyor.
- **Alakasız kol** (A.4, K-176): iki kol tek seçimden geçiyor, yalnız alaka ters. Eski kolun slotu 86 görevde kartlı koldan küçüktü, yenisininki 2'de.
- **Ayar bütçesi 0** (A.9, K-177): Bölüm A donmuş.

## Yeni modüller ve public tanımlayıcılar (K-102)

- `src/zihin/touched.py`: `load_touched`, `derive`, `render`, `structural_problems`, `split_membership`, `run_family`, `Touched`, `TouchedListError`, `RECORD_SERIES`, `TOUCHED`, `SPLITS`
- `src/zihin/records.py`: `schema_statement`, `table_matches_schema`
- `src/zihin/retriever.py`: `retrieve_irrelevant` artık `retrieve`'in bütün süzgeç argümanlarını istiyor
- `src/zihin/config.py`: `ConditionConfig.min_expected_saving`, şemada `retrieval.min_expected_saving`
- `src/zihin/verification.py`: `graded_detail` `trivial_total` döndürüyor
- Betikler: `scripts/setup/build_touched_tasks.py`, `scripts/verify_series_merge.py`, `scripts/setup/measure_no_op_example.py`, `scripts/setup/measure_declared_filters.py`
- Eserler: `results/touched-tasks.json`, `results/series-3-merge.json`, `results/interval-width-action.json`, `results/no-op-example.json`, `results/declared-filters.json`

Kararlar K-165 – K-177, sınırlamalar S-74 – S-77.

## Açık kalan

- Drive'daki kopya, birleşik dosya kopyalanana kadar yarım; önyükleme onu reddediyor.
- İki kolda görev başına kart sayısını eşitlemek (A.4, K-29) koşucuda kurulu değil.
- `--allow-dirty-tree` kaçışının deneyin komutunda olmadığını denetlemek, koşul tablosuyla kurulacak.
- Dokunulan liste kuralı "deney öncesi her koşu" diyor ama deney sınırını bilmiyor: deneyin kendi epizotları değerlendirme görevlerine dokunacak.
- K-170'in kuyruğu: kod tarafında kalan Türkçe (S-76), `config/models.yaml`'ın tarihi.

## #68 — Deney sınırı dny öneki, iki kolda eşit kart sayısı, deneyde kirli ağaç yok

- Branch: `experiment-boundary`
- Merged: 2026-09-25

<!-- body, verbatim except for task text -->

#67'nin üstüne yığılı. #67 birleşince bu PR'ın tabanı `main`'e çevrilecek.

## Deney sınırı: `dny` öneki (K-178)

- Deney koşuları `dny` önekiyle; dokunulan liste üreteci `dny` ailesini saymıyor.
  Sınır bir commit'e değil öneğe bağlı: deney birden çok oturum sürecek ve bir
  düzeltme devamı daha sonraki bir commit'e taşır; önek değişmiyor (protokol §19,
  iki dilde).
- A.10'a 25 Eylül eki: "deney öncesi her koşu" → "`dny` dışındaki her koşu".
- Ölçüm olmayan deney koşuları (ön kontrol, sağlık denetimi) `dnyk` önekiyle;
  onlar dokunuş sayılıyor. `dny-onkontrol…` ve test_normal dışındaki ya da
  listede olan bir göreve düşen `dny` epizodu yükleyicide reddediliyor.
- Testler: `dny` epizodu listeyi değiştirmiyor, yeni `dny` dışı koşu değiştiriyor.

## A.4: kart sayısı iki kolda eşit (K-179)

- Kontrol kolu her görevde kartlı kolun kart sayısını alıyor, tür başına
  (`matched_to`); kartlı kol sıfırsa kontrol de sıfır.
- 104 görevde ölçüldü (`results/declared-filters.json`, `equal_counts`):
  102 görevde eşitlenebiliyor. `d194965_1` ve `d194965_3`'te havuz yetmiyor;
  o iki görevde kontrol kolu koşmuyor (kısa koşmuyor), koşucu reddediyor.
  `8ce6779_3`'te hiç kart yok, iki kol da sıfır.

## Deneyin komutu `--allow-dirty-tree` taşıyamaz (K-180)

- `check_declared_conditions.py`, `dny` komutunda bayrağı ya da argparse'ın
  ona çözdüğü herhangi bir kısaltmasını (`--allow`, `--allow-dirty`, `--al`)
  görürse reddediyor.
- Mutasyonla gösterildi: eşleştirme tam yazıma indirilince üç kısaltma testi,
  betiğin çağrısı kaldırılınca uçtan uca test düşüyor.
- Açık kalan: `record_run.py` bayrağı `dny` için kendisi reddetmiyor.

Yerel kapı her commit'te: 679 test geçti, yerel denetimler temiz.

## #69 — Deney sınırı, eşit kart sayısı ve kirli ağaç denetimi main'e

- Branch: `touched-list-and-primary-model`
- Merged: 2026-09-25

<!-- body, verbatim except for task text -->

#68 `main`'e değil #67'nin dalına (`touched-list-and-primary-model`) birleşti: #67 önce birleşti ve #68'in tabanı `main`'e çevrilmeden birleştirildi. Üç commit bu yüzden `main`'de yok:

- `e45dac4` Deney sınırı dny öneki; ölçüm olmayan deney koşuları dnyk (K-178)
- `55db270` Kart sayısı iki kolda eşit (K-179)
- `95b31f9` Deneyin komutu --allow-dirty-tree taşıyamaz (K-180)

Colab defteri `main`'i klonluyor (`REF = "main"`); bu PR birleşmeden bir `dny` koşusu sınırsız bir kodla başlar.

Yeni içerik yok: #68'de incelenmiş ve CI'da yeşil olan üç commit, ve #68'in birleştirme commit'i.

## #70 — Deneyin faz 1'i: beş koşullu koşucu, sıra, dilimler, sürücü, şartlar ve ön kayıt ekleri

- Branch: `experiment-phase-one`
- Merged: 2026-09-27

<!-- body, verbatim except for task text -->

Deneyin faz 1'i için gereken her şey, ilk `dny` epizodundan önce. Sekiz commit, her biri ayrı bir karar (K-181 – K-188). Her nöbetçinin ateşlediği mutasyonla gösterildi.

## Koşucu (donduruldu)
- **K-181:** beş koşul tek seçimden (`src/zihin/slots.py`). Alakasız havuzdan gelen her tür, kartlı kolun sayısına kesiliyor. Havuz yetmezse kol eksik koşuyor ve `volume_matched = 0` yazıyor. Kartsız görevde kart taşıyan hiçbir koşul koşmuyor. A.4'ün üçüncü ekine Düzeltme.
- **K-182:** iki yeni tablo, `experiment_slices` ve `experiment_episodes`. İkincisine her epizodun satırı epizotla aynı işlemde yazılıyor. Koşucu `dny` koşusunu ayrıştırılmış seçeneklerle kendisi reddediyor: `--allow-dirty-tree` (kısaltmalar dahil), `--condition`'sız koşul, dilimsiz ya da oturumsuz koşu. `record_run.py` bu commit'ten sonra donuk. Donduğu commit'ten beri ölçümü tanımlayan hiçbir yol değişmedi.

## Deneyin tanımı
- **K-183:** görev sırası `sha256("123:" + task_id)` ile belirleniyor (`results/experiment-order.json`). Test sırayı yeniden üretip karşılaştırıyor.
- **K-184:** analiz kümeleri koşucunun kendi slotlarından türetiliyor. Sonuç: Y-1 103, Y-6.2 101, Y-4 101, Y-5 103. Faz 1 930 epizot.
- **K-187:** §19.6'da `dny` şartları, §19.7'de analiz kümeleri. `check_declared_conditions` deneyin 22 değer satırının hepsini kaynağıyla karşılaştırıyor; okunamayan ya da karşılaştırılamayan bir satır denetimi düşürüyor. Defter artık `run_experiment.py dny --tasks 10` koşuyor.
- **K-188:** ön kayda faz tasarımı, K2 (Y-6.2 faz 1'de `skills_failures` ile okunuyor) ve K3 (Y-1 kapsanan görevlerde okunuyor).

## Sürücü ve analiz
- **K-185:** `scripts/run_experiment.py`. Özellikleri:
  - Yarım kalan dilim, yenisi açılmadan önce tamamlanıyor.
  - Ölçümü tanımlayan bir yol ilk epizottan beri değiştiyse duruyor. `--accept-path-change` devam ettiriyor ve her epizoda yazılıyor.
  - Ön kontrol `dnyk-onkontrol<n>` olarak koşuyor.
  - Özet yalnız biten görev sayısı, epizot sayısı ve tüm koşulların ortalama süresi.
- **K-186:** kısmi okuma yasağı (A.7'ye ek). `scripts/analyze_experiment.py` dilim içi ve dilimler arası kırılmayı adlandırıyor; tam küme bitmeden `--confirmatory`'yi reddediyor.

## Ölçülen bir etkileşim
Dokunulan liste her ön kontrol ailesini kaynak olarak tutuyor. Her oturumun `dnyk` ön kontrolü listeyi kayıttan ayırır ve ikinci oturumu durdururdu. Sürücü bu yüzden üyeliği işlenmiş listeden okuyor ve deney sınırını kayda karşı doğrudan denetliyor. Bedeli: kayıt geri getirildiğinde liste yerelde yeniden üretilecek.

Yerel kapı her commit'te: 752 test geçti, yerel denetimler temiz.

## #71 — Herkese açılma temizliği: mekanik düzeltmeler, README durumu, AppWorld türevleri, kararlar D1-D12

- Branch: `public-readiness`
- Merged: 2026-10-13

<!-- body, verbatim except for task text -->

Herkese açılma temizliği, PR 1. Her commit bir mantıksal değişiklik ve her biri yerel kapıdan geçti: 752 test, bütün bekçi betikleri temiz, defter bekçisi dahil.

## Değişiklikler ve kararları

| Commit | Ne | Karar |
|---|---|---|
| `a46e937` | Kökteki boş `oom` dosyası çıktı | Faz A, güvenli mekanik |
| `1ecb0fd` | `.gitignore`'a `.DS_Store`, `.ipynb_checkpoints/`, `*.log`, `.vscode/`, `.idea/`, `*.swp` (izlenen hiçbir dosyaya uymuyor) | Faz A, güvenli mekanik |
| `b9b12a1` | `ci.yml`'ye üst düzeyde `permissions: contents: read` | Faz A, güvenli mekanik |
| `5eb0cdc` | README'lerin durum bölümü bugüne çekildi ve olgu düzeltmeleri yapıldı; yalnız Türkçe belgeler listesi eklendi; `PROJECT_STATUS.md` güncellendi | D11, D12 |
| `e46d91c` | AppWorld görev metinleri kimlik ve sha256 ile değiştirildi; rota testinin örneği bir `train` görevinden alındı; sınırlama kayıtları S-78, S-79, S-80 | D5 (a), (b), (c) |
| `3a03961` | D1–D12 karar kaydında: K-189 ile K-200 | D1–D12 |

**README'lerin durum bölümü taslak.** Onay, bu PR'ın incelenmesi.

## Uygulanmayan bir madde: PR dökümü

İstenen ad `docs/pull-request-log.md` belge adlandırma denetimini düşürüyor (*does not match NN-english-kebab.(tr|en).md*). Kural gereği denetime dokunmadım ve maddeyi uygulamadım. Döküm hazır ve depo dışında duruyor: 70 PR, gövdeler harfi harfine, asistan adı yok, görev yönergesi yok. Denenen konumlar:

| Konum | Belge denetimleri |
|---|---|
| `docs/pull-request-log.md` | adlandırma düşüyor |
| `docs/reports/pull-request-log.md` | tanımlayıcı denetimi düşüyor (iki çözülemeyen ad) |
| kökte `PULL_REQUESTS.md` | üçü de geçiyor |

Konum kararı sahibinde.

## Bildirilen uyumsuzluklar

- **D5 (b):** yeni örnek AppWorld'ün yayımladığı gpt-4o koşusundan. Testi değiştirmeden geçen tek `train` günlükleri o koşuya ait (diskteki 132 günlükten altısı). Dosya yine bir AppWorld deney çıktısı ve türevi; lisans sorusu kapanmıyor (S-80). Test modülünün açıklaması ve 42. satırdaki yorum eski örneği anlatıyor; yalnız 41. satır değişti.
- **D6:** `appworld pack` yalnız bir beyaz listedeki deney çıktısı dosyalarını paketliyor, `.sqlite` dosyalarını almıyor. Önerilen yol karar kaydında: aynı paketleme fonksiyonu ve AppWorld'ün kendi anahtar sabitleri, `appworld unpack` ile açılan yerleşim (K-194). Onay gelmeden hiçbir ek üretilmiyor.
- **D12:** `docs/reports/` altındaki yalnız Türkçe belge sayısı 27 değil 26: `eksen-uzatma.tr.md`'nin İngilizce eşi var (K-200).

## Birleşmeden sonra kalanlar

- `colab-sonuclari` dalını ve birleşmiş 56 dalı silmek (D3, D4).
- `ceviri-hazirligi` ve `tasarim-katmani` için fark raporu.
- PR 2: üç çeviri.
- Kısım 2: süzülmüş açık kopya.

## #72 — Üç giriş belgesinin İngilizce çevirisi (D12)

- Branch: `english-entry-docs`
- Merged: 2026-10-13

<!-- body, verbatim except for task text -->

Üç giriş belgesinin İngilizce çevirisi, PR 2 (D12). Her commit yerel kapıdan geçti: 752 test, bütün bekçi betikleri temiz.

## Değişiklikler ve kararları

| Commit | Ne | Karar |
|---|---|---|
| `a627e2d` | `REPRODUCE.md`, `DATA_MODEL.md` ve `SKILL_SPEC.md` içerik değişmeden `.tr.md` adına taşındı; ad değişikliği ayrı commit'te, `git log --follow` Türkçe metnin geçmişini izliyor | D12 |
| `5d892b1` | `REPRODUCE.md` İngilizce | D12 |
| `355633b` | `DATA_MODEL.md` İngilizce | D12 |
| `55379cf` | `SKILL_SPEC.md` İngilizce | D12 |
| `f49538f` | Türkçe README Türkçe kaynaklara bağlanıyor; iki README'de iki dilli kök belgeleri anan bir cümle | D12 |
| `161a1d8` | Karar kaydı: `K-200`'e tarihli ek (adlar ve kaynaktaki eskimiş yerler), `K-192`'ye tarihli düzeltme (birleşmiş dal 56 değil 54) | D12, D4 |

## Adlandırma: README kuralı. Onay bu PR'ın incelenmesi

İngilizce çeviri uzantısız `.md` adını, Türkçe kaynak `.tr.md` adını taşıyor. Kökte iki dilli tek emsal README (`K-105`).

`docs/` altındaki şema (`.tr.md` kaynak, `.en.md` çeviri) eski adları ortadan kaldırırdı. Onlara 25 izlenen dosya bağlanıyor. Bunlardan dördü ölçümü tanımlayan yollarda: `config/models.yaml`, `src/zihin/model_server.py`, `src/zihin/compiler.py`, `src/zihin/schema.sql`. Bağlantıyı düzeltmek sürücünün durma kuralını tetiklerdi, düzeltmemek ölü bağlantı bırakırdı. Bu adlarla hiçbir bağlantı kopmuyor ve hiçbir ölçüm yoluna dokunulmadı.

## Çeviri nasıl denetlendi

Belge bekçisi kök belgeleri taramıyor: adlandırma, eşlik ve tanımlayıcı denetimi `docs/` ve `experiments/` altında. Bu yüzden her çift ayrıca karşılaştırıldı: kod blokları, ters tırnaklı adlar, K-/S- atıfları, sayılar, kalın vurgular, başlık ağacı ve tablo satırları. Farklar yalnız beklenen yerlerde:
- iki yer tutucu (`<depo-url>`, `<görev>`);
- `DATA_MODEL`'in dört düzey şemasındaki açıklamalar;
- `SKILL_SPEC`'in belge bağlantıları `.en.md` eşlerine gidiyor. `06-skill-language`'in eski ifadesini anan tarihsel cümle Türkçe kaynağa bağlı kaldı.

Terimler mevcut İngilizce belgelerden alındı: künye → *manifest*, düşürme kuralı → *demotion rule*, suç atfı → *attribution of blame*, ön kayıt → *pre-registration*, soğuk rejim → *cold regime*.

## Kaynakta eskimiş yerler: çeviri onları taşıyor, düzeltilmedi

D12 bir çeviri kararı; içerik düzeltmesi ayrı bir karar. Ölçülen yerler `K-200`'ün ekinde de yazılı:
- `DATA_MODEL`: dokuz tablo sayıyor, şemada bugün on iki tablo var (`run_ledger`, `experiment_slices`, `experiment_episodes` sonradan girdi). Künye sabitini eski Türkçe adıyla anıyor, kodda `REQUIRED_MANIFEST_FIELDS`. "Tek gerçek kaynağı" bölümü iki projeksiyon tablosunun "burada olmadığını" söylüyor, kendi tablo listesi ikisini de sayıyor.
- `SKILL_SPEC`: bir şartname, ve `skills` tablosu ondan ayrışıyor. Tabloda `free_parameters` ve `body` var; `kind`, `precondition` ve sicil sayaçları yok.
- `REPRODUCE`: `appworld` işaretli testlerin CI'da koştuğunu bir bölümde söylüyor, sonraki bölümde koşmadığını. Model sunucusu bölümü 1.5B, 3B ve 7B'yi ve Aşama 4 öncesini anlatıyor.

## Ayrıca: `K-192`'nin sayısı

Denetim raporu birleşmiş dal sayısını 56 yazmıştı. Denetimin kendi dökümünde 54'tü. Silmeden önce her dal yeni `main`'e karşı yeniden ölçüldü. Silinenler o 54 dal ve `colab-sonuclari`, toplam 55. `public-readiness` D4'ün kapsamında olmadığı için duruyor.

## #73 — Rota testinin örnek günlüğü sentetik; S-80 kapandı (D5 b)

- Branch: `synthetic-api-fixture`
- Merged: 2026-10-13

<!-- body, verbatim except for task text -->

Rota testinin örnek günlüğü sentetik, PR 3 (D5 b). Her commit yerel kapıdan geçti: 752 test, bütün bekçi betikleri temiz.

## Önce: adlar açık mı

Örnekteki on uç noktanın onu da AppWorld'ün açık API Explorer'ında uygulama, API adı, yöntem ve yolla görünüyor: https://appworld.dev/appworld/api-explorer. Örnek: `spotify : remove_song_from_library`, Route `DELETE /spotify/library/songs/{song_id}`. Adlar yalnız şifreli paketin içinde değil.

İki çekince:
- **Site belgeyi düz metin yayımlamıyor.** Sayfa veriyi `api-docs.js`'ten alıyor. Dosyada şifreli bir blob duruyor ve tarayıcıda, sayfaya gömülü bir anahtarla çözülüyor. 457 kaydın her biri AppWorld'ün canary dizgesini taşıyor. Aranan on yolun hiçbiri dosyada düz metin geçmiyor.
- **AppWorld'ün README'si bir ricada bulunuyor** (satır 338): paketlerden türetilen veri internete düz metin olarak konmasın. Rota adları paket kaynaklı.

Aynı rotaların çoğu ağaçta başka yerlerde de duruyor (`inputs/write-set-static.json`, testler). Örnek dosyanın tek başına kattığı ad yok. Bu soru açık deponun tasarımına ait.

## Değişiklikler

| Commit | Ne | Karar |
|---|---|---|
| `ecc324f` | `scripts/build_api_calls_fixture.py` (`--check` kipli) `tests/data/api_calls-synthetic.jsonl`'i yazıyor; `api_calls-229360a_2.jsonl` çıktı; testte yalnız dosya yolu, 42. satırdaki yorum ve modül açıklaması değişti | D5 (b) |
| `1911c1d` | `S-80` kaydın kendi biçimiyle kapandı, iki dilde; harita yeniden üretildi | D5 (b) |

**Örnek:**
- 22 çağrı, on rota.
- `spotify/library/songs/{song_id}`'ye beş, `spotify/library/albums/{album_id}`'ye üç farklı uydurma kimlikle gidiliyor.
- Her çağrının `data` alanı boş.
- Görev metni, model çıktısı ve yörünge yok.

## Mutasyonla kanıt

Testin örnekten istediği beş koşul tek tek bozuldu; her mutasyon hedeflediği testi düşürdü, sonra örnek geri yüklendi ve `--check` temiz.

| Mutasyon | Düşen test |
|---|---|
| bir satıra dördüncü anahtar (`app`) | `test_log_lines_have_exactly_the_three_documented_keys` |
| çözülmeyen bir URL | `test_every_recorded_url_resolves` |
| 19 çağrı, on uç nokta korunarak | `test_a_many_call_episode_touches_more_than_one_endpoint` |
| dokuz uç nokta | `test_a_many_call_episode_touches_more_than_one_endpoint` |
| şablon başına tek kimlik | `test_identity_collapses_ids_but_not_operations` |

Beşinci koşul talimattaki dört koşulun dışındaydı. `test_identity_collapses_ids_but_not_operations` aynı örneği okuyor ve en az bir şablona birden fazla kimlikle gidilmesini istiyor.

## Bildirilenler

- **CI'da gerçek bir günlüğün biçimine karşı sınama kalmadı.** Eski örnek bir koşunun kopyasıydı, üretimdeki biçim değişirse CI'da düşerdi. Sentetik örnek yalnız üreticinin verdiği biçimi taşıyor. Gerçek biçimi bundan sonra yalnız yerel korpus testi sınıyor, o da `experiments/outputs` varken. CI'da o dizin yok, yani bu sınama CI'da atlanıyor. Modül açıklaması bunu yazıyor.
- **Test fonksiyonlarından birinin açıklaması eski.** `test_a_many_call_episode_touches_more_than_one_endpoint` hâlâ "55-call episode" diyor. Değişiklik izni modül açıklamasıyla ve 42. satırla sınırlıydı.
- **`K-193` güncel değil.** (b) maddesi hâlâ `train` örneğini anlatıyor. Bir ek gerekirse PR 4'e girebilir.

## #74 — Belge doğruluğu: eskimiş ifadeler, S-81, K-201 ve ekler, PULL_REQUESTS.md

- Branch: `doc-accuracy`
- Merged: 2026-10-18

<!-- body, verbatim except for task text -->

Belge doğruluğu, PR 4. Çeviri sırasında bulunan eskimiş ifadeler kendi belgelerinin tarihli düzeltme biçimiyle, iki dilde düzeltildi; karar kaydı ve PR dökümü eklendi. Her commit yerel kapıdan geçti: 752 test, bütün bekçi betikleri temiz.

## Değişiklikler

| Commit | Ne |
|---|---|
| `3798bb4` | `DATA_MODEL`: tablo sayısı 12. `run_ledger` `579d4f1` ile, 10 Eylül'de, PR'sız doğrudan `main`'e girdi; `experiment_slices` ve `experiment_episodes` #70 ile. Üçü kayıt sınıfında ama tetikleyici taşımıyor (K-182); "bütün kayıt tabloları" cümlesine not düşüldü. Sabit `acef1d8`'den beri `REQUIRED_MANIFEST_FIELDS`. |
| `9d7fdb5` | `REPRODUCE`: `ci.yml`'nin bugün koştuğu yazıldı. Testler işi `appworld` testlerini koşuyor, Sandbox işi `-m sandbox`, `model_server` hiçbir işte yok. Yerel-yalnız tablosundaki üç testin CI'daki durumu da yazıldı. |
| `354e697` | `SKILL_SPEC`: `kind` alanının tabloda olmadığı düzeltildi (K-75). |
| `44f00b1` | `S-81`: şartname ile `skills` tablosu dokuz alanda ayrışıyor, defterde karar yok; ikisine de dokunulmadı. |
| `b9f565c` | `test_a_many_call_episode_touches_more_than_one_endpoint`'in açıklaması ("55-call episode"); yalnız metin. |
| `db9a716` | `K-201` (dallar ve arşiv etiketi); `K-193`, `K-194` ve `K-189`'a tarihli ekler; karar CSV'si. |
| `71be1ca` | `PULL_REQUESTS.md` kökte, #1'den #73'e; iki README'de yalnız Türkçe belgeler arasında. |

## SKILL_SPEC: hangisi otoritatif

Şartnamenin tabloyla ayrışan her alanı için karar defterine bakıldı.
- **`kind`: belge eskimiş.** `K-75` boş etki sonekli örüntülerin kütüphaneye hiç girmediğini yazıyor. Tablo buna uyuyor: boş soneki `CHECK` ile reddediyor. Ayırt edici bir alana gerek kalmıyor. Belge tarihli bir düzeltmeyle düzeltildi.
- **Öbür dokuz alanda kayıtlı bir karar yok:**
  - `signature` → `free_parameters` ve `calls` → `body`/`body_length` başka adla duruyor;
  - `effect_suffix` aynı adla ama başka içerikle duruyor (şartname indeks istiyor, tablo çağrıları tutuyor);
  - `precondition` ve beş sicil sayacı hiç yok.

  Defter şartnamenin donduğunu da yazmıyor. Talimat gereği ikisine de dokunulmadı; sınırlama `S-81` olarak kaydedildi ve kararını bekliyor.

## K-194: açık bir soru

Kurulu paket `appworld` 0.2.0.dev0, git commit'i `a072b7a`'dan. PyPI'daki son yayımlanmış sürüm 0.1.3.post1. Gösterim şartındaki "yalnız yayımlanmış paket" hangisi? 0.1.3.post1 aynı `unpack` komutunu ve aynı sabitleri taşıyor mu? Bu ölçülmedi; paketi indirmek gerekiyor.

## Bildirilenler, dokunulmadı

- **`REPRODUCE`'ta düzeltme listesi dışında kalan bir eskimiş ifade.** "Betik tam test takımını koşturuyor" diyor; `scripts/local_checks.sh` ise `pytest -m "appworld or model_server"` koşuyor. Betiğin kendi başlık yorumu da `appworld` testlerinin CI'da koşmadığını söylüyor.
- **`DATA_MODEL`'in "Tek gerçek kaynağı" bölümü** iki projeksiyon tablosunun "burada olmadığını" söylüyor. Bu talimattaki listede yoktu.
- **`PROJECT_STATUS.md`** suç atfı satırında "sicil sütunları boş" diyor; o sütunlar tabloda hiç yok (`S-81`).
- **`K-190` ve `K-197`** hâlâ süzülmüş açık kopyayı anıyor. İptal `K-189`'un ekinde yazılı.
- **`PULL_REQUESTS.md` bu PR'ı kapsamıyor.** Bir PR kendi birleşme tarihini taşıyamaz. Turun sonunda yeniden üretilecek.

## #75 — Belge doğruluğu 2: local_checks, DATA_MODEL, K-202 ve S-81, K-190/K-194/K-197 ekleri, PULL_REQUESTS.md

- Branch: `doc-accuracy-2`
- Merged: 2026-11-08

<!-- body, verbatim except for task text -->

Belge doğruluğu, PR 5. Her commit yerel kapıdan geçti: 752 test, bütün bekçi betikleri temiz. Kod değişikliği yok; `scripts/local_checks.sh`'te yalnız başlık yorumu değişti.

## Değişiklikler

| Commit | Ne |
|---|---|
| `bb86800` | `local_checks.sh`'in başlık yorumu betiğin sırayla koştuğunu yazıyor; REPRODUCE'a iki dilde tarihli düzeltme: "tam test takımı" üç seçimin birleşimi |
| `36a128c` | DATA_MODEL'in "tek gerçek kaynağı" bölümü: iki projeksiyon tablosu bu şemada (`142662f`, `771b94f`); cümle `09ed3fb`'de, şemada yalnız kayıt tabloları varken yazılmıştı |
| `6673e73` | `K-190` ve `K-197`'ye süzülmüş kopyanın iptali eki |
| `aaa08d2` | `K-202`: şartname düzeltiliyor, kod değil; SKILL_SPEC'e iki dilde tarihli not |
| `a02a46e` | `S-81` kendi kapanış biçimiyle kapandı, `K-202`'ye dayanarak |
| `9457bdb` | PROJECT_STATUS: var olmayan sicil sütunları |
| `aac4044` | `K-194`'e "yayımlanmış paket" kararı ve uyumluluk ölçümü eki |
| `239be07` | `PULL_REQUESTS.md` #1'den #74'e |

## Bildirilenler

- **"Tam test takımı" cümlesi aslında doğruydu.** Önceki raporda betiğin yalnız `appworld or model_server` koştuğunu yazmıştım. Bu eksikti: `ci_simulasyonu.sh` temiz bir checkout'ta CI'ın iki seçimini de koşuyor. Üçü birlikte takımın tamamı; podman yoksa yalnız sandbox testleri atlanıyor. Düzeltme bunu yazıyor. Gerçekten eskimiş olan başlık yorumuydu.
- **"Tasarlandı, uygulanmadı" listesi iki gruba ayrıldı.** Dokuz alanın altısı hiç uygulanmadı, gerekçe talimattaki gibi. Öbür üçü (*signature*, *calls*, *effect_suffix*) tabloda başka biçimde duruyor (`free_parameters`, `body`/`body_length`, sonekin çağrıları); onlar "tablonun biçimi geçerli" diye yazıldı.
- **`K-194` eki talimatta yoktu.** Kayıttaki açık soruyu kapatıyor: karar ve uyumluluk ölçümü.
- **Başlık yorumu İngilizce.** Depo kuralı gereği İngilizce yazıldı; betiğin geri kalan yorumları ve `echo` satırları hâlâ Türkçe.
- **`doc-accuracy` dalı uzakta duruyor.** #74 ile birleşti; silinmesi için bir karar yok.

## #76 — Betik yorumları ve iletileri İngilizceye çevrildi

- Branch: `english-script-messages`
- Merged: 2026-11-10

<!-- body, verbatim except for task text -->

Betiklerdeki Türkçe yorum ve iletiler İngilizceye çevrildi. Mantık değişmedi. Commit yerel kapıdan geçti: 752 test, bütün bekçi betikleri temiz.

## Kapsam

| Dosya | Değişen satır | Ne |
|---|---:|---|
| `scripts/local_checks.sh` | 36 | yorum blokları, `echo` iletileri |
| `scripts/ci_simulasyonu.sh` | 46 | yorum blokları, `echo` iletileri |
| `scripts/serve_models.ps1` | 23 | yorumlar, `Write-Output` / `Write-Error` iletileri; dosya ASCII kaldı (PowerShell 5.1) |

Öbür betiklerde Türkçe düzyazı kalmadı. Python yorumlarındaki Türkçe, İngilizce cümle içinde alıntılanmış veri (defterin `**Düzeltme.**` gibi başlıkları). `colab_publish_results.sh`'in yazdığı commit iletisi K-77 gereği Türkçe.

## Mantığın değişmediğinin kanıtı

Her dosyanın iskeleti çıkarıldı: tam satır yorumlar atıldı, ileti satırlarındaki (`echo`, `printf`, `Write-*`) her tırnaklı dizge içerdiği `$` ifadelerinin sıralı listesine indirgendi, öbür satırlar harfi harfine bırakıldı. Üç dosyanın iskeleti HEAD ile birebir aynı. `bash -n` iki kabuk betiğinde, PowerShell ayrıştırıcısı `serve_models.ps1`'de hatasız.

Denetleyicinin kendisi mutasyonla sınandı:

| Mutasyon | Sonuç |
|---|---|
| `pytest -m "appworld or model_server"` → `-m "appworld"` | yakalandı |
| iletideki `$yerel` → `$yerell` | yakalandı |
| yalnız bir yorum cümlesi | geçti, beklendiği gibi |

## Bilerek dokunulmayanlar

- Türkçe değişken adları (`yerel`, `CALISMA`, `kos`, `mevcut` ve öbürleri): kod, yorum değil.
- `ci_simulasyonu.sh` dosya adı: `local_checks.sh` onu adıyla çağırıyor.
- CI iş adları `"Testler"` ve `` `Bağımlılık kurulumu` ``: CI'daki adlarla aynı kalmalı.
- `count_guards.py`, `local_checks.sh`'in metnini okuyor; komut satırları değişmedi, `guards` denetimi temiz.

## Kapsam dışı kalan Türkçe

| Dosya | Türkçe harfli satır | Neden bu PR'da değil |
|---|---:|---|
| `.github/workflows/ci.yml` | 70 (51 yorum, 15 iş/adım adı, 4 echo) | iş akışı tanımı; iş adları belgelerde ve CI denetim adlarında geçiyor |
| `Containerfile` | 28 | ölçümü tanımlayan yol: yorum değişikliği bile sürücünün durma kuralını tetikler |
| `config/*.yaml` (10 dosya) | 194 | ölçümü tanımlayan yol, aynı sebep |

