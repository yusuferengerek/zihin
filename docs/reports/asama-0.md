# Aşama 0 raporu — Depo iskeleti

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

## Kabul ölçütü ne diyordu

> Temiz bir makinede depo klonlanıp bağımlılıklar kurulabiliyor, CI'nın dördü de
> yeşil.

## Neyi doğruladım

### Bağımlılık kurulumu tekrarlanabilir

`uv.lock` içinde dokuz paket dondurulmuş durumda. Kurulum `--frozen` bayrağıyla
yapılıyor, yani çözümlemeyi kilit dosyası belirliyor. CI'da ayrıca `uv lock
--check` koşuyor ve kilit dosyası `pyproject.toml` ile uyumsuz kalırsa iş
düşüyor.

Kilitlenen bağımlılıklar bilerek az. Çalışma zamanında tek bir tane var,
`pyyaml`. Geliştirme tarafında `pytest` ve `ruff` duruyor.

AppWorld kasten bu listede yok. Aşama 0'ın ölçütü temiz makinede bağımlılıkların
kurulabilmesi. O ölçütü henüz gerekmeyen, ağır ve Git LFS isteyen bir
bağımlılıkla sınamak ölçütü doğrulamak değil bulandırmak olurdu. AppWorld Aşama
1'in PR'ında girecek.

### Python sürümü gerçekten sabit

`requires-python = "==3.11.*"` yazıldı ve `.python-version` içine `3.11` kondu.
Kurulum CPython 3.11.15 ile yapıldı. Bu bir aralık değil, sabit değer. 3.12'ye
kayma ihtimali yok.

Kullanılan araç uv 0.11.28. Hem yerelde hem CI'da aynı sürüme sabitlendi,
`astral-sh/setup-uv@v5` adımına sürüm açıkça yazıldı.

### Altı config dosyası gerçekten aynı şemayı taşıyor

Bu iddia yorum değil, test. `tests/test_config_schema.py` şunları denetliyor:

- `config/` altında tam olarak altı `.yaml` var ve adları beklenen altı koşul.
- Altı dosyanın anahtar ağacı birebir aynı. Değerler atılıp yalnız yapı
  karşılaştırılıyor.
- Her dosya yükleniyor ve `condition` alanı dosya adıyla eşleşiyor.
- Kalkan altı koşulun hepsinde açık. Kazara kapanması testi düşürür.
- Taban hiçbir kart taşımıyor, kalan beş koşul eşit slot taşıyor, beşer. Hacim
  kontrolü ancak bu eşitlik korunursa anlamlı.
- Bozuk yapılandırmalar reddediliyor: eksik alan, tanınmayan alan, tanımsız enum
  değeri, ve slot sayısı yerine boole. Sonuncusu sessizce geçebilirdi, çünkü
  Python'da `bool` bir `int` alt türüdür.

Toplam 17 test, hepsi geçiyor.

### Dört kontrol de yerelde geçiyor

| Kontrol | Sonuç |
|---|---|
| Bağımlılık kurulumu, `uv sync --frozen` ve `uv lock --check` | geçti |
| Lint, `ruff check` ve `ruff format --check` | geçti, 17 dosya biçimli |
| Testler, `pytest` | 17 geçti |
| Import ve build, `import zihin` ve `uv build` | geçti, sdist ve wheel üretildi |

CI dört ayrı iş olarak `ubuntu-24.04` üzerinde koşuyor. Koşucu sürümü açıkça
yazıldı, `ubuntu-latest` kullanılmadı. O etiket zamanla kayar ve geliştirme
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

Kabul ölçütünü harfi harfine sınamak için depoyu boş bir dizine sıfırdan
klonlayıp kurdum. Klonlanan dosya sayısı 35. `uv sync --frozen` dört paket
kurdu: `pytest`, `pyyaml`, `ruff` ve `zihin`. Python 3.11.15 çözümlendi. Dört
kontrolün dördü de bu temiz kopyada geçti.

Bu, CI'ın yaptığından ayrı bir doğrulama. CI zaten her koşuda temiz bir
`actions/checkout` yapıyor. Bu sınamanın gösterdiği başka: klon özel depo
üzerinden de sorunsuz çalışıyor ve `.gitignore` kuruluma gereken hiçbir dosyayı
dışarıda bırakmıyor.

### Lisans kanonik metin

Apache 2.0, `apache.org` üzerinden indirildi. 11358 bayt, sha256 değeri
`cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`. Elle
yazılmadı.

## Karşılaştığım sürprizler

### 1. AppWorld'ün deposu ile PyPI sürümü aynı şey değil

Kurulumun tamamını belirleyen olgu bu oldu. PyPI'daki son sürüm `0.1.3.post1`,
depo `main` ise `0.2.0.dev0`. Aşama 5'in ihtiyaç duyduğu referans ajan iskelesi
ve prompt dosyası yalnız `main` dalında. Dolayısıyla AppWorld yayımlanmış bir
sürüme değil, hareketli bir dalın tek bir commit'ine sabitlenecek. Bu bir
tekrarlanabilirlik borcu ve `docs/09-limitations.tr.md` içine S-01 olarak yazıldı.

### 2. Windows'ta yürütme zaman aşımı diye bir şey yok

AppWorld'ün `main` dalı Windows'u destekliyor ve kendi CI'ında `windows-latest`
üzerinde doğruluyor. Ancak `timeout_call` Windows'ta istisna fırlatıyor ve
`default_timeout_seconds` zorla `None` yapılıyor. Yani ajan kodu duvar saati
sınırı olmadan koşuyor. Platform kararının WSL2'ye dönmesinin sebeplerinden biri
bu oldu (K-01).

Buna ek olarak AppWorld'ün kendi Windows CI'ı doğrulamayı ilk dört göreve
kısıtlıyor ve yanında `super slow on windows / figure out why` notu taşıyor.

### 3. Referans çözümler elimize geçmeyebilir

`appworld download data` varsayılan olarak `minimal` modda iniyor. `partial` ve
`full` modlar bakımcıya özel anahtar istiyor, referans çözümler ise yalnız
`full` modda geliyor. Bunun doğrudan bir sonucu oldu: adım tavanının çapası
referans çözüm uzunluğundan, doğrulayıcının beklediği durum değiştiren çağrı
sayısına taşındı (K-11).

### 4. Bir sunucu süreci aynı anda tek bir dünya tutuyor

AppWorld motoru ajan sürecinden ayrı koşabiliyor. Ama bir süreç içinde ikinci
bir dünya başlatmak HTTP 400 döndürüyor, sebebi freezegun'ın zamanı süreç geneli
taklit etmesi. Paralel epizot, port başına ayrı sunucu süreci gerektiriyor. Bunu
`experiments/pilot-plan.md` içine bir bütçe kalemi olarak yazdım.

### 5. `.wslconfig` iptal edilmiş bir denemeden kalmıştı

Host geneli WSL yapılandırması WSL'i 4 GB'a kapatıyordu ve var olmayan bir
belgeye atıf yapıyordu. Yedeğini alıp bu proje için yeniden yazdım (K-02).

## Açık kalanlar

Üç config alanı cevap beklerken önerilen değerlerle yazıldı. Cevap geldiğinde
düzeltilecek. `docs/08-decisions.tr.md` içinde A-01, A-02 ve A-03 olarak duruyorlar.

- `retrieval.mode` hangi ekseni taşıyor. Varsayım: tabanda `none`, kalan beşinde
  `standard`.
- `fill.enabled` taban dışındaki beş koşulda açık mı. Varsayım: evet.
- `failures.source` enum'u üç değer mi taşıyor. Varsayım: evet, `naive` yok.

## Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet |
| Testi yazıldı | Evet, 17 test |
| Loglandı | CHANGELOG ilk girişi yazıldı |
| Belgesi yazıldı | README, 08-decisions, 09-limitations |
| Hata durumu düşünüldü | Bozuk config'lerin reddi test edildi |
| PR üzerinden gözden geçirildi | PR #1 açıldı |
| Temiz kurulumda baştan çalıştırıldı | Evet. Sıfırdan klon ve kurulum, dördü geçti |

---

# Ardıl — koşul şeması kapandı

Yukarıdaki rapor PR #2 ile birleştikten sonra üç açık soru cevaplandı. Bu bölüm o
cevapların ne değiştirdiğini ve neyi doğruladığımı taşıyor.

## Neyi doğruladım

### İki kritik kontrast artık iddia değil, test

Analiz planı iki kontrasta dayanıyor ve ikisi de belgede yalnız cümle olarak
duruyordu. Şimdi `tests/test_config_schema.py` içinde duruyorlar.

`test_pure_volume_contrast_carries_no_relevant_content`, taban ile alakasız
getirme arasındaki farkın saf hacim kalması için ikisinin de alakalı içerik
taşımaması gerektiğini denetliyor.

`test_pure_content_contrast_differs_in_one_field_only`, sadece beceriler ile
alakasız getirmenin yalnız `skills_source` alanında ayrıştığını denetliyor.
Karşılaştırma `dataclasses.fields` üzerinden bütün alanları dolaşıyor, yani
şemaya sonradan eklenecek bir alan da bu denetime kendiliğinden giriyor.

### Testler boşuna geçmiyor

Dört ayrı mutasyon denedim, dördü de doğru testler tarafından yakalandı:

| Mutasyon | Düşen testler |
|---|---|
| `skills.yaml`, `fill.enabled` kapatıldı | `test_non_baseline_conditions_carry_equal_slots`, `test_pure_content_contrast_differs_in_one_field_only` |
| `irrelevant_retrieval.yaml`, `skills.source` değeri `standard` yapıldı | `test_pure_content_contrast_differs_in_one_field_only`, `test_pure_volume_contrast_carries_no_relevant_content` |
| `failures.yaml`, `retrieval.mode` değeri `none` yapıldı | `test_retrieval_mode_is_none_only_in_baseline` |
| `skills_failures.yaml`, `failure_slots` 5'ten 3'e indirildi | `test_non_baseline_conditions_carry_equal_slots` |

Her mutasyondan sonra zemini geri getirip 20 testin tamamının geçtiğini
doğruladım.

### Belgede bir hata vardı

Saf içerik kontrastı, ikisi birden ile alakasız getirme çifti olarak yazılıydı.
Hem `config/irrelevant_retrieval.yaml` yorumunda hem README'de. O çift iki
alanda birden ayrışıyor, dolayısıyla tek eksenli değil. Doğrusu sadece beceriler
ile alakasız getirme çiftidir. Düzeltildi ve K-31'e not olarak geçti.

## Karşılaştığım sürpriz

Mutasyon denemesini yazarken her mutasyondan sonra `git checkout -- config/` ile
zemine dönüyordum. İlk koşuşta config değişikliklerim henüz işlenmemişti, geri
alma mutasyonla birlikte onları da sildi. İkinci ve üçüncü mutasyon bozuk
zeminde koştu: `retrieval.mode` değeri `standard`'a dönen dosyalar yeni enum'a
uymadığı için hepsi `test_each_config_loads` testinde düştü ve mutasyonun
kendisi hiç sınanmadı. Değişiklikleri işledikten sonra denemeyi tekrarladım.
İkinci koşuşta betik, zemin kirliyse baştan çıkıyor.

## Aşama 1'e taşınan

Aşama 1'in kabul ölçütüne bir madde eklendi: temiz makinede kurulum AppWorld
dahil yeniden doğrulanacak (K-32). Aşama 0 asıl ağır bağımlılığı hiç
sınamamıştı, bu boşluk orada kapanıyor. Git LFS önkoşulunu şimdiden REPRODUCE.md
içine yazdım, gerçekten gerekli olduğu Aşama 1'de ölçülecek.

## Hâlâ açık

`experiments/decisions.csv` sütunları söylenmedi. Dosya A-04 olarak açık
bırakıldı ve şimdilik yalnız önerilen başlık satırını taşıyor.
