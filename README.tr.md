*[English](README.md)*

# zihin

Yusuf Eren GEREK

AppWorld üzerinde beceri ve hata belleği deneyleri için bir araştırma düzeneği. Bu
depo özel bir arşivin açık yansısı. Nasıl kurulduğu [PROVENANCE.md](PROVENANCE.md)
dosyasında yazılı.

Burası bir ürün deposu değil. Fazladan soyutlama, fazladan yapılandırma ve fazladan
bağımsızlık katmanı bilerek yok.

## Soru

Derlenmiş beceriler ve açık bir hata indeksi, daha önce görülmemiş görevleri çözmek
için gereken model çağrısı sayısını düşürüyor mu? Bu soru tek bir hücrede onaylayıcı
olarak sınanıyor: mekanizmaların açık olduğu koşul baseline'a karşı, model çağrısı
ölçütünde, görülmemiş alt kümede, iki yönlü. Birincil hücrenin modeli 25 Eylül 2026
ekinden beri `qwen2.5-coder:32b-instruct-q4_K_M`. İkinci soru keşif amaçlı: bu etki
incelenen model boyutları içinde sistematik olarak kayboluyor mu? İki soru da
`docs/02-research-question.tr.md` içinde, tasarım `docs/05-experiment-design.tr.md`
içinde.

## Durum

**Mekanizmalar kuruldu.** Beceri derleyicisi, hata indeksi, getirici, kalkan ve
sandbox yazıldı, üretim yolunda koşuyor ve `PILOT_REPORT.md` içinde ölçülüyor.

**Ön koşul kapısı özgün yerel eksende devreye girdi.** Qwen2.5-Coder 1,5B, 3B ve 7B aynı
otuz AppWorld görevinin hiçbirini çözemedi. Bu bulgu üç koşuya dayanıyor. Bunlardan
ikisi tavan sınırlı, biri kayıtta yok (S-63).

**Sınır kontrolü sıfırların düzenekten değil modelden geldiğini gösterdi.** Aynı otuz
görevde DeepSeek V4 Flash 0731 (`openrouter/deepseek/deepseek-v4-flash-0731`) bu
pipeline'da 20/30 çözdü. Tasarım bu koşuyu düşünme kipi
kapalı olarak tanımlamıştı, ama koşu düşünme kipi açıkken yapıldı. Yani bu sayı, düşünme
kipi açık bir modele ait. Kontrolün sorusu ise yine cevaplanıyor: bu pipeline'da herhangi bir
model başarılı olabiliyor mu (S-34)?

**Birincil hücre 32B'ye taşındı.** Colab'da bir A100 üzerinde Ollama ile sunulan
`qwen2.5-coder:32b-instruct-q4_K_M` (ön kayıt A.2, 25 Eylül 2026 eki) 11/30 çözdü.
Otuz görevin yirmi beşi dünyayı değiştirmeyi gerektiriyor ve bunlarda sonuç 7/25.
Mekanizmaların sınanabileceği bant bu.

**Deney tanımlandı, henüz koşulmadı.** Şartları kurulum protokolünün 19.6 bölümünde ve
ön kaydın eklerinde donduruldu. Sürücü, `scripts/run_experiment.py`, faz 1'i eylem
tabakasının 104 görevinde dilim dilim koşuyor: kapsanan 103 görevde 3 koşul (`baseline`,
`skills_failures`, `irrelevant_retrieval`) × 3 seed, `8ce6779_3`'te yalnız baseline × 3,
toplam 930 epizot.

**Tamamlanmış bir deney hücresi yok.** Arşivin 3 yerel kayıt veritabanında deneyin çalışma önekiyle (`dny`) başlayan tek bir epizot yok. Sayım bu ağacın ölçümü alınırken yapıldı. Colab'da da hiçbir dilim koşulmadı.

**Uçtan uca demonun davranış iddiası geri çekildi.** Demo, kartlı kolun başarılı
etkiye ulaştığını, kartsız kolun ise ulaşmadığını bildirmişti. Üç tekrarla
koşulunca on beş hücrenin (beş görev, üç kol) on birinde tekrarlar birbirini
tutmadı, kartsız kol da on beş epizodunun (beş görev, üçer tekrar) altısında etkiye
ulaştı. Kartların prompt'a bayt bayt girdiği iddiası
bundan etkilenmedi ve geçerli. Ayrıntısı `docs/reports/uc-kollu-kart-kosusu.md`
içinde.

**Ayna bulgusu ve sınırı.** Beceri kütüphanesi ile hata indeksi birbirinden bağımsız
iki korpustan çıkarıldı ve aynı mekanik darboğazda buluştu: kütüphane kimlik doğrulama
token'ını almayı öğretiyor, indeks de token'ı taşımadan çağrı yapmayı yasaklıyor. Ama o
darboğazı aşmak yetmiyor. Üç kollu koşuda token her kolda alındı, tamamlama ise 0/45
kaldı. Yani mekanizmaların buluştuğu yer, görevin çözüldüğü yer değil (S-57).

Burada numarasıyla anılan sınırlamalar `docs/09-limitations.tr.md` içinde.

## Yöntem

Mekanizmaların ötesindeki katkı, ölçümlerin nasıl dürüst tutulduğu. Kurulum
protokolü bir ölçümü sessizce bozan arızaları adlandırıyor ve her birini, onu doğuran
ölçülmüş olayla birlikte bir kurala çeviriyor (`experiments/setup-protocol.tr.md`,
6. bölüm). Kuralları bekçiler uyguluyor: `check_*` betikleri ve görünüm üreten
betiklerin `--check` kipleri. Hepsi CI'da ve `scripts/local_checks.sh` içinde koşuyor.
Bir bekçi, yakalamak için yazıldığı arızayı yakaladığı görülmeden kabul edilmiyor: arıza bilerek
yapılan bir düzenlemeyle, yani bir mutasyonla geri konuyor ve bekçinin onu
reddetmesi gerekiyor (K-49). Sınırlamalar ve kararlar tarihli kayıtlar olarak
tutuluyor: `docs/09-limitations.tr.md` içinde 83 sınırlama,
`docs/08-decisions.tr.md` içinde 207 karar.

Kod, yazarın yönetiminde bir yapay zekâ kodlama ajanıyla yazıldı. Her değişiklik pull
request'ler, testler ve bekçiler üzerinden yazarın incelemesinden geçti.

## Yeniden üretme

Kurulumun tamamı, Git LFS dahil ön koşullarıyla birlikte
[REPRODUCE.tr.md](REPRODUCE.tr.md) içinde. Kısa hâli:

```bash
git clone https://github.com/yusuferengerek/zihin.git zihin
cd zihin
uv sync --all-groups --frozen
uv run appworld install
uv run appworld download data
uv run python scripts/unpack_derived.py
uv run pytest -m "not model_server and not sandbox"
```

`scripts/unpack_derived.py`, AppWorld'den türetilmiş veri dosyalarını
`derived/appworld-derived.bundle` içinden özgün yollarına açıyor ve her birini
`derived/MANIFEST.json` ile karşılaştırıyor.

### Kayıt veritabanları

Dört kayıt veritabanı ağaçta yok. Bu deponun
[release'lerinde](https://github.com/yusuferengerek/zihin/releases) şifreli dosyalar
olarak yayımlanıyorlar, her veritabanı için bir `.bundle` dosyası. Dört dosyayı aynı
dizine indirip geri yükleyin:

```bash
uv run python scripts/restore_records.py <indirilen dosyaların dizini>
```

Betik her dosyayı kurulu `appworld unpack` ile açıyor, açılan dosyanın boyutunu ve
sha256 değerini `records/MANIFEST.json` ile karşılaştırıyor ve dosyayı ancak ondan
sonra `results/` altına yazıyor. Depo dışındaki bir yolu reddediyor, sha256 değeri
farklı olan bir dosyanın üzerine de hiçbir zaman yazmıyor. Git commit'ine sabitlenen
`appworld` 0.2.0.dev0 ile de PyPI'daki 0.1.3.post1 ile de çalışıyor.

**Doğru bir koşu nasıl görünür.** Aşağıdaki iki sonuç da bu ağaçta ölçüldü.

Kayıt veritabanları olmadan, yukarıdaki komutlardan sonra: 815 test
toplanıyor, 797 test geçiyor, 18 test atlanıyor, düşen test yok.
18 atlama beklenen atlamalar ve 4 gruba ayrılıyor:

| Grup | Test | Gerekçe |
|---|---|---|
| özel şablonlar | `tests/test_build_public_tree.py::test_the_colab_defaults_name_the_archive_here_and_this_repository_in_public` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| özel şablonlar | `tests/test_build_public_tree.py::test_the_experiment_status_comes_from_the_count` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| özel şablonlar | `tests/test_build_public_tree.py::test_the_public_ci_is_the_archives_with_its_patches` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| özel şablonlar | `tests/test_build_public_tree.py::test_the_readmes_render_every_count_and_the_method_sentence[en]` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| özel şablonlar | `tests/test_build_public_tree.py::test_the_readmes_render_every_count_and_the_method_sentence[tr]` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| özel şablonlar | `tests/test_build_public_tree.py::test_two_builds_of_one_commit_differ_only_in_the_bundle` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| özel şablonlar | `tests/test_build_public_tree.py::test_unpack_manifest_refuses_paths_outside_the_repository` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| kayıt veritabanları | `tests/test_experiment_sets.py::test_the_committed_sets_are_what_the_slots_give_today` | results/zihin-3.sqlite is absent: restore it with scripts/restore_records.py |
| kayıt veritabanları | `tests/test_library_source.py::test_the_guard_passes_on_the_declared_pair` | results/zihin-3.sqlite is absent: restore it with scripts/restore_records.py |
| kayıt veritabanları | `tests/test_library_source.py::test_the_guard_refuses_a_library_that_is_not_the_declared_one` | results/zihin-3.sqlite is absent: restore it with scripts/restore_records.py |
| kayıt veritabanları | `tests/test_library_source.py::test_the_library_is_where_the_constant_says_it_is` | results/zihin-3.sqlite is absent: restore it with scripts/restore_records.py |
| kayıt veritabanları | `tests/test_recorded_run.py::test_actions_carry_full_raw_parameters` | results/zihin.sqlite is absent: restore it with scripts/restore_records.py, or take a run with scripts/record_run.py |
| kayıt veritabanları | `tests/test_recorded_run.py::test_at_least_one_step_produced_multiple_actions` | results/zihin.sqlite is absent: restore it with scripts/restore_records.py, or take a run with scripts/record_run.py |
| kayıt veritabanları | `tests/test_recorded_run.py::test_episode_carries_load_state_and_sequence` | results/zihin.sqlite is absent: restore it with scripts/restore_records.py, or take a run with scripts/record_run.py |
| kayıt veritabanları | `tests/test_recorded_run.py::test_run_manifest_records_the_verified_context_window` | results/zihin.sqlite is absent: restore it with scripts/restore_records.py, or take a run with scripts/record_run.py |
| kayıt veritabanları | `tests/test_recorded_run.py::test_whole_episode_reads_back_in_order` | results/zihin.sqlite is absent: restore it with scripts/restore_records.py, or take a run with scripts/record_run.py |
| tek commit'lik geçmiş | `tests/test_dates.py::test_a_correction_note_naming_the_right_commit_rescues` | no git history here: a shallow checkout, or the CI simulation's copy, which carries the tracked files without `.git`. The sweep reads the record and belongs to `local_checks.sh` for exactly this reason. |
| izlenmeyen AppWorld koşu çıktıları | `tests/test_api_routes.py::test_the_whole_local_corpus_resolves` | experiments/outputs holds no api_calls.jsonl log: the recorded AppWorld runs are untracked and are not in this checkout |

Dört kayıt veritabanı geri yüklendiğinde: 815 test toplanıyor,
806 test geçiyor, 9 test atlanıyor, düşen test yok.
Kalan 9 atlama 3 gruba ayrılıyor:

| Grup | Test | Gerekçe |
|---|---|---|
| özel şablonlar | `tests/test_build_public_tree.py::test_the_colab_defaults_name_the_archive_here_and_this_repository_in_public` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| özel şablonlar | `tests/test_build_public_tree.py::test_the_experiment_status_comes_from_the_count` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| özel şablonlar | `tests/test_build_public_tree.py::test_the_public_ci_is_the_archives_with_its_patches` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| özel şablonlar | `tests/test_build_public_tree.py::test_the_readmes_render_every_count_and_the_method_sentence[en]` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| özel şablonlar | `tests/test_build_public_tree.py::test_the_readmes_render_every_count_and_the_method_sentence[tr]` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| özel şablonlar | `tests/test_build_public_tree.py::test_two_builds_of_one_commit_differ_only_in_the_bundle` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| özel şablonlar | `tests/test_build_public_tree.py::test_unpack_manifest_refuses_paths_outside_the_repository` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| tek commit'lik geçmiş | `tests/test_dates.py::test_a_correction_note_naming_the_right_commit_rescues` | no git history here: a shallow checkout, or the CI simulation's copy, which carries the tracked files without `.git`. The sweep reads the record and belongs to `local_checks.sh` for exactly this reason. |
| izlenmeyen AppWorld koşu çıktıları | `tests/test_api_routes.py::test_the_whole_local_corpus_resolves` | experiments/outputs holds no api_calls.jsonl log: the recorded AppWorld runs are untracked and are not in this checkout |

Başka bir atlama ya da herhangi bir düşen test, koşunun beklenen koşu olmadığını
gösterir.

## AppWorld verisi

AppWorld'ün veri lisansı, korunan kısmının ya da ondan türetilenlerin herkese açık
her yeniden dağıtımının şifreli yapılmasını istiyor. Bu yüzden AppWorld'den türetilmiş
veri dosyaları, AppWorld'ün kendi `pack_bundle` işleviyle paketlenip
`derived/appworld-derived.bundle` içinde geliyor. Kayıt veritabanları da yalnız
şifreli release dosyaları olarak yayımlanıyor. Nasıl geri yüklendikleri yukarıda,
"Kayıt veritabanları" başlığı altında. Sabitlenen sürümün `pack_bundle` işleviyle
üretilen paketleri hem PyPI'daki `appworld` 0.1.3.post1 hem de git commit'ine
sabitlenen 0.2.0.dev0 açabiliyor. Bu, zararsız bir deneme paketinde ve dört kayıt
dosyasında doğrulandı, açılan her dosyanın sha256 değeri tuttu.

Arşivin kurulum için yedek olarak tuttuğu iki AppWorld wheel'i bu depoda yok. İkisi
de özel arşivde duruyor. Kaynakları, sabitlenen commit ve her wheel'in sha256 değeri
[vendor/appworld/README.md](vendor/appworld/README.md) içinde.

## Dil

CI iş adları, konteyner dosyası ve yapılandırma dosyalarındaki yorumlar
(`.github/workflows/ci.yml`, `Containerfile`, `config/*.yaml`) Türkçe. Bu dosyalar
deney tamamlanana kadar donduruldu ve deneyden sonraki eşitlemede İngilizceye
çevrilecek. Bu sayfanın sonundaki belgelerin ise yalnız Türkçesi var.

## Köken

Bu depo, asıl kayıt olmayı sürdüren özel bir arşivden bir betikle kuruluyor. Geçmiş
taşınmıyor. [PROVENANCE.md](PROVENANCE.md) arşiv commit'ini, yapı betiğini ve onun
hash'ini, neyin neden dışlandığını, ve yalnız bu ağaç için yapılan her düzenlemeyi ve
yazılan her dosyayı listeliyor. Buradaki her commit, yansıttığı arşiv commit'inin
adını taşıyor. Kayıt veritabanlarındaki `code_commit` anahtarları arşivi gösteriyor.
Arşiv, istek üzerine hakemlere açılıyor.

## Yalnız Türkçe belgeler

Şu 40 belgenin yalnız Türkçesi var. Liste ağaçtan üretiliyor: İngilizce
karşılığı olmayan ve metni Türkçe olan her Markdown dosyası.

- `CHANGELOG.md`
- `PILOT_REPORT.md`
- `PROJECT_STATUS.md`
- `PULL_REQUESTS.md`
- `docs/08-decisions.tr.md`
- `docs/10-external-review.tr.md`
- `docs/11-falsification.tr.md`
- `docs/appworld-facts.tr.md`
- `docs/reports/asama-0.md`
- `docs/reports/asama-1.md`
- `docs/reports/asama-2.md`
- `docs/reports/asama-3.md`
- `docs/reports/asama-4.md`
- `docs/reports/asama-5.md`
- `docs/reports/b32-olcumu.md`
- `docs/reports/bant-taramasi.md`
- `docs/reports/bant3-taramasi.md`
- `docs/reports/bosluk-raporu.md`
- `docs/reports/denetim-bosluk-raporu.md`
- `docs/reports/hizalama-denetimi.md`
- `docs/reports/izinli-uygulama-vekili.md`
- `docs/reports/kapanis-raporu.md`
- `docs/reports/kurulum-sonrasi-1.md`
- `docs/reports/kurulum-sonrasi-2.md`
- `docs/reports/kurulum-sonrasi-3.md`
- `docs/reports/kurulum-sonrasi-4.md`
- `docs/reports/mekanizma-kapanis-notlari.md`
- `docs/reports/model-ailesi-taramasi.md`
- `docs/reports/sinir-kontrolu.md`
- `docs/reports/sunum-iskeleti.md`
- `docs/reports/teknik-olgular.md`
- `docs/reports/teshis.md`
- `docs/reports/uc-kollu-kart-kosusu.md`
- `docs/reports/uctan-uca-demo.md`
- `experiments/colab/README.md`
- `experiments/pilot-plan.md`
- `experiments/preregistration.md`
- `inputs/README.md`
- `scripts/setup/README.md`
- `vendor/appworld/README.md`

## Lisans

Apache 2.0. Bkz. [LICENSE](LICENSE).
