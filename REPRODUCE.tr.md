# Yeniden üretme

Temiz bir makinede baştan kurma yönergesi. Buradaki her adım Aşama 1'de
koşuldu. Koşulmamış hiçbir komut yazılmadı.

## Önkoşullar

| Önkoşul | Sürüm veya not |
|---|---|
| Ubuntu 24.04, WSL2 üzerinde ya da yerel | K-01 |
| Python 3.11 | `uv` kendisi kuruyor, `.python-version` sabit |
| `uv` | 0.11.28 |
| Git LFS | Zorunlu, aşağıya bakın |
| GitHub CLI (`gh`) | Yalnız `scripts/local_checks.sh` için; kimlik doğrulanmış olmalı |

### Git LFS

AppWorld'ün `apps.bundle` ve `tests.bundle` dosyaları depoda Git LFS ile
duruyor ve `appworld install` onları açıyor. Filtre kurulmadan `uv` bu
dosyaları 131 baytlık işaretçi olarak indiriyor. Kurulum da şu satırla düşüyor:

```
Exception: File .../appworld/.source/apps.bundle is a Git LFS pointer and not a bundle file.
```

Kurulumu şöyle:

```bash
sudo apt-get install git-lfs
git lfs install
```

İkinci komut şart. Paketin kurulu olması yetmiyor, filtrenin `~/.gitconfig`
içine yazılması gerekiyor. Filtre kuruluyken gelen dosyalar 193950 ve 204426
bayt, elle klonlananla birebir aynı.

Depo tarafındaki karşılığı `pyproject.toml` içindeki `lfs = true` satırıdır.
CI'da da `git lfs install` adımı var, yani bu önkoşul her PR'da sınanıyor.

Yukarı akışın Git LFS'i sabitlenen commit'in bundle nesnelerini sunmazsa `uv sync`
tamamlanamıyor. Bu 20 Ağustos 2026'da oldu: HTTP 403 ve `This repository exceeded its
LFS budget`. Bu deponun kurulduğu arşiv, sabitlenen commit'ten üretilmiş iki AppWorld
tekerleğinin bir yansısını tutuyor. Bu depo onları taşımıyor; hakemler istek üzerine
alabilir.

| | |
|---|---|
| Yukarı akış kaynağı | `https://github.com/StonyBrookNLP/appworld.git` |
| Sabitlenen commit | `a072b7a86e7c1d5b1d7175659d750ebb9b79f10a` |
| `appworld-0.2.0.dev0-py3-none-any.whl` | sha256 `13965100b4e6191e5503c06a24f9b9140b0f04a95a56c8394c29bc6f094c67e3` |
| `appworld_agents-0.1.0.dev0-py3-none-any.whl` | sha256 `32fcd23f68b86c08fdf357fe409a8823fdc7ae64582d784dcf046374cd739e73` |

Yansının nasıl üretildiği ve nasıl yeniden üretileceği `vendor/appworld/README.md`'de.

## WSL kullanıyorsanız: ağ kipi

Model sunucusu Windows tarafında koşuyor, deney WSL içinde. Varsayılan NAT
kipinde WSL'den Windows'a gelen bağlantıyı Hyper-V güvenlik duvarı kesiyor,
çünkü `DefaultInboundAction` değeri `Block`. Sonuç olarak `127.0.0.1:11434`
erişilemiyor.

`~/.wslconfig` içine şunu ekleyin:

```ini
[wsl2]
networkingMode=mirrored
```

Ardından `wsl --shutdown` çalıştırıp dağıtımı yeniden açın. Mirrored kipte WSL
host'un ağ ad alanını paylaşıyor. `127.0.0.1` iki yönde de çalışıyor, güvenlik
duvarı kuralı gerekmiyor ve Ollama'yı `0.0.0.0`'a bağlamak gerekmiyor. Sunucu
LAN arayüzünde dinlemediği için dışarıya açık kalmıyor.

Bu kipin bilinen riski dışarı yönlü DNS'i bozmasıdır. Geçişten sonra sınandı:
`pypi.org`, `github.com` ve `registry.ollama.ai` çözüldü, HTTPS istekleri
döndü, `uv lock --check` geçti.

Alternatif yol yalnız 11434 portunu WSL sanal makinesine açan bir Hyper-V
kuralıydı. O yol yönetici yetkisi istiyor ve sunucunun `0.0.0.0`'a bağlanmasını
gerektiriyor. Mirrored çalıştığı için kullanılmadı.

## Kurulum

```bash
git clone <depo-url> zihin
cd zihin
uv sync --all-groups --frozen
uv run appworld install
uv run appworld download data
```

`--frozen` kilidi olduğu gibi uyguluyor. Kilit ile `pyproject.toml` ayrışmışsa
sessizce güncellemek yerine hata veriyor.

`appworld download data` 198 MB veriyi `data/` altına açıyor. Dizin izlenmiyor.
Görev verisi canary damgası taşıyor ve komutla her zaman yeniden üretilebiliyor.

### AppWorld'den türetilmiş veri

AppWorld'den türetilmiş veri dosyaları (rota listeleri, rota taşıyan ölçüm çıktıları,
bir test örneği) AppWorld'ün paylaşım şartı gereği şifreli olarak
`derived/appworld-derived.bundle` içinde geliyor. Testleri ya da bekçileri koşmadan
önce onları özgün yollarına açın:

```bash
uv run python scripts/unpack_derived.py
```

Betik paketi `appworld unpack` ile açıyor ve her dosyayı yazmadan önce
`derived/MANIFEST.json` içindeki sha256'yla karşılaştırıyor. Açılan yollar
`.gitignore`'da listeli.

### Kayıt veritabanları

Dört kayıt veritabanı bu deponun
[release'lerinde](https://github.com/yusuferengerek/zihin/releases) şifreli dosyalar
olarak yayımlanıyor, her veritabanı için bir `.bundle` dosyası. Onlar olmadan kaydı
okuyan testler atlanıyor, kaydı okuyan bekçiler de koşamıyor. Dört dosyayı aynı dizine
indirip geri yükleyin:

```bash
uv run python scripts/restore_records.py <indirilen dosyaların dizini>
```

Betik her dosyayı `appworld unpack` ile açıyor ve açılan dosyanın boyutunu ve sha256
değerini `results/` altına yazmadan önce `records/MANIFEST.json` ile karşılaştırıyor.
sha256 değeri farklı olan bir dosyanın üzerine hiçbir zaman yazmıyor. Veritabanları
olmadan ve onlarla alınan test sonucu README'de, "Doğru bir koşu nasıl görünür"
başlığı altında.

## Model sunucusu

Windows tarafında, proje betiğiyle:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/serve_models.ps1
```

Betik sunucuyu oturumdan bağımsız bir süreç olarak başlatıyor ve dört ayarı
sunucu sürecine geçiriyor: bağlam penceresi, KV cache tipi, flash attention ve
`keep_alive`. Ayarların gerçekten uygulandığını çıktıya basıyor. Durdurmak için
`Stop-Process -Name ollama`.

Üç model:

```powershell
ollama pull qwen2.5-coder:1.5b-instruct-q4_K_M
ollama pull qwen2.5-coder:3b-instruct-q4_K_M
ollama pull qwen2.5-coder:7b-instruct-q4_K_M
```

Etiketler `config/models.yaml` içinde boyut ve kuantalama dahil tam hâliyle
sabit. Kısaltılmış etiket kullanılmıyor, çünkü künyeden hangi ağırlıkların
koştuğu okunamaz hâle gelir.

`OLLAMA_CONTEXT_LENGTH` verilmezse Ollama bağlam penceresini VRAM'e bakarak
4096 seçiyor. Sunucu logundaki satır şu:
`vram-based default context ... default_num_ctx=4096`. Yönerge dosyası tek
başına 11350 bayt ve ajan adım başına yaklaşık 3800 girdi tokenı harcıyor, yani
4096'lık pencerede prompt kesiliyor. Ölçülen etkisi Aşama 1 raporunda.

Aşama 4 bu sunucuyu kendi betiğinden başlatacak ve KV cache tipi ile flash
attention ayarlarını ortam değişkenleriyle verecek. Şu anki süreçte o ayarlar
yok: `OLLAMA_KV_CACHE_TYPE` boş, `OLLAMA_FLASH_ATTENTION` false. Buradan alınan
hiçbir performans ölçümü Aşama 4 için geçerli değil.

## Tekrarlanabilirlik ne kadar

Bunu net söylemek gerekiyor, çünkü üç model aynı değil.

Epizotlar soğuk rejimde koşuyor: her epizottan önce model bellekten indiriliyor
ve indiği sunucuya sorularak doğrulanıyor. Aynı görev, seed, koşul ve model
dörtlüsü tekrarlandığında:

| Model | Tekrarlanabilirlik |
|---|---|
| 1.5B | Birebir. On koşu, tek yörünge |
| 3B | Birebir. On koşu, tek yörünge |
| 7B | Ölçülmüş varyans içinde. On koşudan dokuzu bir yörünge, biri başka |

7B'nin ayrışması bir arıza değil, ölçülen bir büyüklük. Determinizm varsayılmıyor;
artık varyans model başına ölçülüp gürültü tabanına ekleniyor (K-51).

Ölçümü tekrarlamak için:

```bash
MODEL_SERVER_URL=http://127.0.0.1:11434 \
  ZIHIN_MODEL=7b ZIHIN_REPEATS=10 \
  uv run python scripts/check_cold_determinism.py
```

## Tek görevi uçtan uca koşturma

```bash
MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/run_single_task.py
```

`MODEL_SERVER_URL` referans iskelenin kendi değişkeni. `base_url` alanındaki
şablonu o dolduruyor.

Koşu `experiments/outputs/asama-1-tek-gorev/` altına yazıyor. Doğrulayıcı hükmü
iki yerde duruyor:

- `tasks/<görev>/evaluation/report.md`, görev başına ayrıntı
- `evaluations/on_only_<görev>.txt` ve `.json`, toplu metrikler

## Elinizdeki kopya denetimin öznesi değil

Bu depodaki her denetimin öznesi **deponun ağacı**. Sizde duran kopyalar —
Drive'a kaydedilmiş bir Colab defteri, indirilmiş bir veritabanı, bir hafta
önce çekilmiş bir klon — o denetimlerin dışında.

**Colab defteri için kural.** Defter her oturumda **depodan** açılıyor; Drive'a
kaydedilmiş bir kopya kullanılmıyor. Kaydedilmiş bir kopya kaydedildiği anda
donuyor ve depodaki hiçbir düzeltme ona ulaşmıyor. Bir kez oldu: kopya
birleşmiş bir dalı çekmeye devam etti, sonradan eklenen dosyalar yoktu, ve arıza
kendini "dosya hiç yazılmadı" diye adlandırdı.

**Klon için kural.** Koşudan önce ön koşul denetimini koşturun; ilk satırı
çalışma kopyasının `origin/main`'in kaç commit gerisinde olduğunu söylüyor:

```bash
uv run python scripts/setup/check_prerequisites.py --prefix bir1
```

`--prefix` koşacak koşuyu adlandırıyor, ve denetim gereksinimleri o koşunun
ilan edilmiş şartlarından okuyor. Öneksiz koşarsa her gereksinimi soruyor —
kart okumayan bir koşudan beceri kütüphanesini istemek dahil (`K-152`).

**Bu kuralların kapatmadığı şey `S-69`'da yazılı.** Bayatlık denetimi klonlamadan
**sonra** koşuyor, yani bir tur geç, ve elinizdeki kopyayı klonlamadan önce
kontrol eden bir mekanizma yok.

## Doğrulama

CI beş iş koşuyor. Yereldeki karşılıkları:

```bash
uv run ruff check .
uv run ruff format --check .
uv run python -c "import zihin"
uv build
uv run pytest -m "not model_server and not sandbox"
```

Test filtresi `appworld` işaretini **elemiyor**: K-100'den beri CI `appworld
install` ve veriyi kuruyor, yani o testler CI'da da koşuyor. Elenen iki işaret
ayrı işlerde koşuyor — `sandbox` kendi işinde, `model_server` yalnız yerelde.

Lint işi ayrıca beş üretilmiş görünümü denetliyor; hiçbiri veri istemiyor:

```bash
uv run python scripts/check_docs_parity.py
uv run python scripts/build_limitations_index.py --check
uv run python scripts/build_skeleton_coverage.py --check
uv run python scripts/build_decisions_csv.py --check
uv run python scripts/count_guards.py --check
```

## Yerel-yalnız kontroller

`appworld` işaretli testler indirilmiş 198 MB veriyi istiyor ve CI'da koşmuyor.
Aralarında projenin en önemli değişmezlerinden biri var: epizot başına
veritabanı sıfırlaması. CI koruması altında olmadıkları için her aşama
birleşmesinden önce elle koşuluyorlar.

**Düzeltme, 13 Ekim 2026: CI bugün ne koşuyor.** Bu paragraf K-100'den önceki durumu
anlatıyor; yukarıdaki "Doğrulama" bölümü doğru. `.github/workflows/ci.yml` bugün
şunları koşuyor:

- Testler işi (`Testler`) `appworld install` ve `appworld download data`'dan sonra
  `pytest -m "not model_server and not sandbox"` koşuyor; `appworld` işaretli testler
  bunun içinde. Ardından bir adım, uygulama modülleri yüzünden atlanan test
  kalmadığını ve `appworld` işaretli testlerin gerçekten toplandığını denetliyor.
- Sandbox işi (`Sandbox`) aynı kurulumdan sonra `pytest -m sandbox` koşuyor.
- `model_server` işaretli testler hiçbir CI işinde koşmuyor.

Aşağıdaki tabloda `tests/test_appworld_reset.py` CI'da koşuyor;
`tests/test_recorded_run.py` CI'da toplanıyor ama orada atlanıyor, çünkü CI'da
`results/zihin.sqlite` yok (kayıt veritabanları geri yüklenince koşuyor); yalnız
`tests/test_model_serving.py` CI'ın dışında kalıyor.

```bash
bash scripts/local_checks.sh
```

Betik tam test takımını koşturuyor ve sonucu tarihiyle birlikte basıyor. Her
aşama raporu bu çıktının en son ne zaman ve hangi sonuçla alındığını yazıyor.

**Düzeltme, 18 Ekim 2026: betik neyi koşuyor.** "Tam test takımı" üç seçimin
birleşimi: önce `pytest -m "appworld or model_server"`, sonra
`scripts/ci_simulasyonu.sh` temiz bir checkout'ta CI'ın iki seçimini koşuyor,
`not model_server and not sandbox` ve podman varsa `sandbox`. Podman yoksa sandbox
testleri atlanıyor. Ardından dil denetimi; atıf, tarih, birleşmiş PR eseri ve Colab
defteri denetimleri; dokunulan görev listesi, seri birleşmesi ve deney kümelerinin
`--check` kipleri.

**Taze bir klonda bu betik geçmez, ve geçmemesi doğrudur.** İki adımı çalışan bir
kuruluma dayanıyor: dil denetimi karşılaştırma korpusunu `results/` altından ve
kayıttan okuyor, birleşmiş PR eseri denetimi de kimlik doğrulanmış `gh` istiyor.
Kayıt yoksa dil denetimi **cevap vermeyi reddediyor** — yanlış cevap vermek
yerine düşüyor. Kayıt veritabanları geri yüklenince cevap veriyor, ama bir klonda yine
düşüyor, çünkü korpusunun bir kısmı yalnız arşivin makinesinde duran, izlenmeyen koşu
çıktısı. Ölçülen sayılar S-84'te.

| Kontrol | Neyi koruyor |
|---|---|
| `tests/test_appworld_reset.py` | Epizotlar arasında veritabanı sızıntısı yok |
| `tests/test_recorded_run.py` | Gerçek bir koşu kayıt şemasına dört düzeyiyle yazılıyor |
| `tests/test_model_serving.py` | Sunucudaki etkin bağlam penceresi 32768, üç model de tamamen VRAM'de, seed çıktıyı kontrol ediyor |

İkinci kontrol `results/zihin.sqlite` dosyasını okuyor. Dosya yoksa test
atlanıyor. `records/MANIFEST.json`'ın listelediği kayıt veritabanlarını
`scripts/restore_records.py` ile geri yükleyin ya da kendiniz bir koşu alın:

```bash
MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/record_run.py
```

## Açık yansı

Açık depo yusuferengerek/zihin, bu arşivin ağacından `scripts/build_public_tree.py` ile kuruluyor
(K-205). Bir eşitleme aynı betiği daha yeni bir arşiv commit'ine karşı koşuyor ve farkı
açık depoya tek bir commit olarak uyguluyor: `Sync with archive <hash>`. README'lerin
aktardığı test sonucu ve deney epizodu sayısı, eşitlemeden önce `--measure` ile yeniden
ölçülüyor. Ağaç ölçümden sonra değiştiyse yapı açık ağacı kurmayı reddediyor.
