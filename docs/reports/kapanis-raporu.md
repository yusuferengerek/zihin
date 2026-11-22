# Kapanış raporu — kod tarafı

**Ölçüm tarihi:** 19 Ağustos 2026. **Commit:** `6c0ed5a`. Buradaki her sayı bir
dosyaya atıflı; hiçbiri bu belgeye elle kopyalanmış bir özet değil.

---

## 1. Depoda ne var

| | Sayı | Kaynak |
|---|---|---|
| Kod satırı (`src`, `scripts`, `tests`) | 24 311 | `git ls-files \| wc -l` |
| `src/zihin` modülü | 21 | `git ls-files "src/zihin/*.py"` |
| Test dosyası | 31 | `git ls-files "tests/test_*.py"` |
| Yeşil test (yerel filtre) | 440 | `pytest -m "not model_server and not sandbox and not appworld"` |
| CI işi | 5 | `.github/workflows/ci.yml` |
| Karar kaydı | 127 | `experiments/decisions.csv` |
| Sınırlama kaydı | 55 (39 açık, 16 kapandı) | `docs/09-limitations.tr.md` haritası |

**Kurulan mekanizmalar.** Beceri derleyicisi (kapalı ardışık kalıp madenciliği,
boşluk kısıtı, etki soneki birleştirme), hata indeksi (kapalı koşul dili,
karşıtsal ayırt etme), sembolik getirici, kart oluşturucu, kalkan (birinci aşama
yüklem, gölge kipi), kayıt vekili, podman sandbox. Kanıtları
`results/pilot-dataset.json` ve `docs/reports/mekanizma-kapanis-notlari.md`.

**Ölçüm altyapısı.** Yalnız ekleme yapılan SQLite kaydı, silinip yeniden
üretilebilen türetilmiş görünümler, künye sözleşmesi (K-46), kirli ağaç kapısı
(K-76), devam koruması ve ön kontrol üç koşucunun üçünde de (K-115).

---

## 2. Ne doğrulandı

### Bu oturumda ilk kez: REPRODUCE.md yürütüldü

Hiç yapılmamış doğrulamaydı. CI test koşuyor, **talimatı yürütmüyor**. Taze bir
dizine klonlanıp satır satır uygulandı.

**Tutan zincir:** `git clone` → `uv sync --all-groups --frozen` → `uv run
appworld install` → `uv run appworld download data` (198 MB) → `ruff check` →
`ruff format --check` → `import zihin` → `uv build` → `pytest` (432 geçti, 10
atlandı).

**Kırılan dört yer, dördü de düzeltildi:**

| Kusur | Ne oldu |
|---|---|
| `check_language.py` taze klonda **226 bulgu**, çalışan ağaçta sıfır | Karşılaştırma korpusu `results/` ve kayıttan geliyor; taze klonda yok, her veri anahtarı düzyazı sanılıyor. K-117'nin kendi nöbetçimizde ihlali. Artık korpus yoksa **cevap vermeyi reddediyor** |
| "CI'nın koştuğu **dört** kontrol" | CI beş iş koşuyor |
| `pytest -m "not appworld"` | K-100'den beri CI `-m "not model_server and not sandbox"` koşuyor; filtre bayattı |
| Lint işinin beş üretilmiş görünüm denetimi | Belgede hiç yoktu |
| `gh` önkoşullarda yok | `local_checks.sh` onu çağırıyor |

### Son durum, beş ölçüm

Hepsi `6c0ed5a` commit'inde, CI'ın **aynı commit'te** koştuğu doğrulanarak (K-116):

| Ölçüm | Sonuç |
|---|---|
| Beş CI işi | beşi de `SUCCESS`, `headSha` = `6c0ed5a` |
| Yapısal nöbetçi sayımı | 14 bölge, 7 çıplak, 7'si de gerekçesiyle ilan edilmiş |
| Bekleyen çeviri | **0** — 10 belge iki dilli, 4'ü gerekçesiyle yalnız Türkçe |
| Çapa denetimi | 795 çapa, iki tarafta birebir |
| Üretilen görünümler | sınırlama haritası (iki dilde, 55 kayıt), iskelet özeti (35 iddia), karar CSV'si (127 kayıt) — üçü de güncel |
| Birleşmiş PR eserleri | 6 PR, eksik eser **0** |
| Çalışma ağacı | temiz, uzakla eşleşiyor |

### Daha önce doğrulanmış olanlar

- **Kalkan gölge kipinde ölçüldü:** 9154 çağrıda 8 engelleme; sekizi tek tek
  incelendi ve ikisi bir kusuru açığa çıkardı (S-37).
- **Tel kimliği:** kayıttaki her eylem vekilden geçirilip geri kuruldu; imzasız
  kontrol kolu ölçümün boş olmadığını gösteriyor (`results/wire-identity.json`).
- **Sandbox:** altı güvenlik korumasının her biri **korumasız kolda başarılı
  olduğu gösterilerek** yazıldı (`tests/test_sandbox_security.py`, CI'da).
- **Şeffaflık:** sandbox katmanının ajanın gördüğü metni değiştirmediği sabit bir
  CODE dizisiyle ölçüldü (`results/transparency.json`).
- **Determinizm:** artık varyansa nokta kestirim değil üst sınır yazıldı, model
  başına %9,5, ölçüldüğü rejim belirtilerek (S-21).

**Düzeltme, 15 Kasım 2026: kalkan satırı.** Sekiz engellemeden biri bir testin kendi
açtığı nottu (S-83). O testin iki çıktısı olmadan gölge koşusu 9145 çağrıda 7
engelleme veriyor.

---

## 3. Ne açık

### Bulgunun kendisi olan sınırlar

39 açık sınırlamanın kapanma sınıfı: **10 dış olgu** (yukarı akış, donanım,
dondurulmuş iskele), **10 ölçüldü ve kısıt gerçek çıktı**, **17 sonraki tur**,
**2 kalıcı kayıt**. Yani belgenin **17/39'u geçici**, 22'si kalıcı.

En ağır üçü:

- **Ön koşul kapısı ateşledi** (K-58). Üç yerel model otuz görevde 0/30. Üç
  bağımsız tekrarla doğrulandı (`bant2`, `bant3`, `bant3-kapalı`). Birincil hücre
  hiç koşulmadı, mekanizma sonuçları raporlanmadı.
- **Gürültü tabanı sıfır değil** (S-56). Sabit tohum ve sıcaklıkta on beş hücrenin
  on biri üç tekrarda ayrışıyor. Tek epizottan okunan her kol karşılaştırması
  geçersiz; uçtan uca demonun davranış iddiası bu yüzden **geri çekildi**.
- **Kütüphane içerik atfı için fazla homojen** (protokol §12.2). Dört becerinin
  dördünün de etki soneki bir `auth/token` POST'u, yani alakasız kart kontrolü
  içerik ile şablonu ayıramıyor.

### Yapılmayan işler, kuyruk sırasıyla

| İş | Neden açık |
|---|---|
| **Final sunum** | Tek eksik teslim maddesi. İskeleti var (35 iddia, 28 atıflı, 7 boş), kendisi yok |
| Pilot dataset / raporu | Ön koşul kapısının aşılmasına bağlı |
| Naif madenci karşılaştırması | Derleyici karşılaştırması olarak; kütüphane karşılaştırması yapılmadı |
| K-110'un geriye dönük kapanış taraması | On altı kapanışın artıkları kayda taşınmadı |
| Çapraz kontrolün yedi aday sınırlaması | Yazılmadı; `09-limitations`'ı büyütür |
| Ters yöndeki beş kayıt | Bir iddiayı sınırlıyorlar ama sunum o iddiayı kurmuyor |
| Nöbetçi doğruluğu süpürmesi | 14 nöbetçinin **varlığı** ölçüldü, **doğruluğu** ölçülmedi (K-115'in sınırı) |

### Durdurulanlar

| Ne | Neden durduruldu |
|---|---|
| Uçtan uca demonun davranış iddiası | Gürültü tabanının altında kaldı, geri çekildi (S-56) |
| "DeepSeek V4 Flash 0731, düşünme kapalı, 20/30" cümlesi | O koşuda düşünme açıktı, ilan edilen koşul değildi (S-34) |
| Sınır kontrolünün düşünme-kapalı tekrarı | Aile taramasından sonraya bırakıldı |
| `sinir3` koşusu ve eşik kalibrasyonu | Bozuk durma kuralıyla koşuldu, geçersiz (S-32) |
| Geçmişin yeniden yazılması | Ölçüm kişisel içerik olmadığını gösterdi; bedeli var, etkisi yok (K-120) |
| Model ailesi Qwen2.5-Coder | Ön koşulu geçemedi; aile yeniden seçiliyor (A-06, K-61) |

---

## 4. Sunum için kurulamayan cümleler

`docs/reports/teknik-olgular.md` bu listeyi taşıyor ve sunum ondan besleniyor.
Özeti: mekanizmalar kuruldu ve çalıştıkları gösterildi; **hipotez test edilmedi**
ve sebebi ölçüldü. Kazanç, ölçek, içerik-hacim ayrımı ve toplanabilirlik üzerine
hiçbir cümle kurulamaz, çünkü karşılık gelen hücreler hiç koşulmadı.
