# Proje durumu

## Bu belge neden var

`docs/01`–`docs/07` **hedef tasarımı** anlatıyor. Kod onun bir alt kümesini
uyguluyor. Tasarım belgelerini okuyan biri, sistemin kalkanı, derleyiciyi,
getiriciyi ve bağlam montajcısını çalıştırdığını sanır. İlk üçü var ve ölçüldü
(mekanizma yol haritası maddeleri 1–5, kapanış notları
`docs/reports/mekanizma-kapanis-notlari.md`); sandbox da var (madde 8,
`docs/12-sandbox-scope.tr.md`). Kartlar epizot içinde modele gösterildi: uçtan uca
demo ve üç kollu kart koşusu (`docs/reports/uctan-uca-demo.md`,
`docs/reports/uc-kollu-kart-kosusu.md`). **Bağlam montajcısı hâlâ yok.**

## Bugünkü durum

13 Ekim 2026 itibarıyla. Ön koşul kapısı özgün yerel eksende ateşledi (1,5B, 3B ve
7B otuz görevde 0/30). Birincil hücre `qwen2.5-coder:32b-instruct-q4_K_M`'ye,
Colab A100'e taşındı (ön kayıt A.2'nin 25 Eylül eki); aynı otuz görevde 11/30.
Deneyin tanımı donduruldu: şartlar kurulum protokolünün 19.6 bölümünde, faz
tasarımı ve analiz kümeleri ön kaydın eklerinde ve 19.7'de. Sürücü
(`scripts/run_experiment.py`) hazır; faz 1 104 görevde 930 epizot. **Tamamlanmış
bir deney hücresi yok:** bu depodaki kayıt hiç deney epizodu taşımıyor, ve 26 Eylül
2026'dan sonra Colab'da bir dilim koşup koşmadığı depodan bilinmiyor.

Bu tablo o boşluğu kapatıyor: her tasarım öğesinin uygulama durumu.

**Durum üç değer alıyor.** *Tasarlandı*: belgede tanımlı, kod yok. *Uygulandı*:
kod var, kanıtı henüz yok. *Doğrulandı*: kanıt sütunu dolu.

**Kanıt**, durumun dayandığı somut şey. "Çalışıyor" kanıt sayılmıyor; geçen bir
test, yeşil bir CI koşusu ya da bir ölçüm sayılıyor.

CI'da koşmayan kontroller `REPRODUCE.md` içinde; her birleşmeden önce koşuluyor
ve sonucu o aşamanın raporuna tarihiyle yazılıyor (K-35).

## Yedi bileşen (`03-architecture.tr.md`)

| Bileşen | Durum | Kanıt | Eksik |
|---|---|---|---|
| Politika | doğrulandı | Referans iskele değiştirilmeden kullanılıyor; boş slotlu prompt referansla bayt bayına aynı, `tests/test_scaffold_slot.py`. Dolu slot on epizotta koştu: blok bayt bayına prompt'ta, fark yalnız blok, kartsız kol referansla aynı (`docs/reports/uctan-uca-demo.md`) | Kartın modele ne kadar yardım ettiği ölçülmedi; hacim ile içerik ayrılmadı |
| Getirici | doğrulandı | `src/zihin/retriever.py` + `src/zihin/cards.py`; kapsama train %96,7 / dev %94,7 / test_normal %100, ayırt edicilik 21 kart kümesi, kart jetonu bütçe altında; `tests/test_retriever.py`, `tests/test_cards.py`; değer eşiği `min_expected_saving = 1` (K-175) | Teslim edilen kütüphanede kartlı kolun hiç kart vermediği bir görev var (`8ce6779_3`, K-184) |
| Kalkan | doğrulandı | `src/zihin/shield.py` + `shield_mount.py`; gölge modunda 258 epizot, yanlış pozitif %4,1, engelleme %0,07, fail-open dalı 0; `tests/test_shield.py` 15, `tests/test_shield_mount.py` 12 | Zorlama kipi kurulmadı (K-71); korpus kalkanı sınamıyor |
| Sandbox | uygulandı | `src/zihin/sandbox.py`, `src/zihin/recording_proxy.py`; kök yetkisiz podman konteyneri, kaynak sınırları ve imaj damgası künyede; CI'ın `Sandbox` işi `pytest -m sandbox` koşuyor; kapsam `docs/12-sandbox-scope.tr.md` | Deneyin sürücüsü sandbox'ı açmıyor (`--sandbox` geçmiyor) |
| Doğrulayıcı | doğrulandı | `src/zihin/verification.py`; kırk beş epizotta hüküm şemaya yazıldı, `tests/test_verifier_verdict.py` | S-04'ün iki bileşeni `NULL` kalıyor |
| Kayıt defteri | doğrulandı | Dört düzeyli şema, yalnız ekleme yedi tabloda ayrı ayrı sınandı, `tests/test_record_schema.py` ve `tests/test_recorded_run.py` | `actions.result_status` kısmen (S-05) |
| Derleyici | doğrulandı | `src/zihin/compiler.py` + `failure_index.py`; 4 beceri ve 15 hata kalıbı kayıttan üretildi, eşik ızgarası 21 hücre; `tests/test_compiler.py` 36, `test_skill_library.py` 15, `test_failure_index.py` 14 | Suç atfı sayaçları boş (çağrılma sicili yok); son koşullar boş (S-41) |

**Düzeltme, 15 Kasım 2026: kalkan satırı.** Gölge modunun 258 epizodundan ikisi bir
testin çıktısıydı (S-83). Onlarsız 256 epizot ve %0,05 engelleme.

**Kayıt/projeksiyon ayrımı:** kayıt tarafı doğrulandı (ham parametreler tam
hâliyle, K-15). Projeksiyon tarafı da var: `skills` ve `failure_patterns`
kayıttan türetiliyor, yalnız ekleme tetikleyicisi taşımıyor ve silinip yeniden
üretilebiliyorlar. Silme testi `tests/test_record_schema.py` içinde. Aynı
**kimlikle** yeniden üretme sınanmadı: kimlik derleyici commit'ini taşıyor.

**Bağlam montajcısı:** tasarlandı. Şu an iskelenin kendi kesme mantığı işliyor
ve montajcı geldiğinde çakışacak (S-07, K-26). Planda ne zaman çözüleceği yazılı
değil. Girdisi olan üç sayı ölçüldü: sabit blok pencerenin %9,7'si, kartlar
k=5+5'te %0,4–0,8, iskelenin karakter tavanı %39 (K-88, S-47).

## Deney tasarımı (`05-experiment-design.tr.md`)

| Öğe | Durum | Kanıt | Eksik |
|---|---|---|---|
| Altı koşulun yapılandırması | doğrulandı | Altı YAML tek şemada; şema eşitliği, enum sayısı, iki kritik kontrast ve bool/int tuzağı `tests/test_config_schema.py` altında; beş deney koşulu tek seçimden kuruluyor (`src/zihin/slots.py`, K-181) | Deney beşini koşuyor; `naive_compiler` deneye yazılmadı (K-145) |
| Kart sayısı kuralı | uygulandı | Kart taşıyan her koşul, tür tür, kartlı kolun o görevdeki sayısını alıyor (K-179); havuz yetmezse kol eksik koşuyor ve `volume_matched = 0` taşıyor (K-181); k=5+5 bloğu ölçüldü (en çok 523 jeton) | Dolgu yok; `d194965_1` ve `d194965_3`'te iki kol eksik (K-184) |
| Model ekseni | uygulandı | Birincil hücre `qwen2.5-coder:32b-instruct-q4_K_M`, Colab A100 (ön kayıt A.2'nin 25 Eylül eki); ölçek ekseni keşifsel (A.11) | — |
| Sabitler: Q4_K_M, q8_0, 32K, sıcaklık, seed | doğrulandı | Üç model tamamen VRAM'de (1,56 / 2,60 / 5,16 GiB), etkin pencere üçünde de 32768, ayarlar künyede, `tests/test_model_serving.py` | — |
| Soğuk yükleme rejimi | doğrulandı | Boşaltma sunucuya sorularak doğrulanıyor; beş görevde otuzar epizot tekdüze, artık varyans üst sınırı %9,5 (S-21) | — |
| Birincil metrik: görev başına model çağrısı | uygulandı | `episodes.total_model_calls` kayıtta | **Henüz ölçülmedi**: deney tanımlı ve sürücü hazır, tamamlanmış hücre yok |
| Zorunlu tanı metriği | tasarlandı | Bileşenleri kayıtta (`steps`, `actions.result_status`) | Hesaplayan kod ve yorum kuralı |
| On dört ikincil metrik | tasarlandı | Bir kısmı kayıtta türetilebilir | Tanımları ve hesaplama |
| Dereceli tanı skoru | doğrulandı | `zihin.verification.graded_detail`, `tests/test_verifier_verdict.py` | Tanımı kurulum protokolüne yazılacak; birincil metriğe ve kapılara girmiyor |
| Adım tavanı, görev başına | uygulandı | `ZIHIN_MAX_STEPS` ile görev başına veriliyor; bant taraması `2 × çapa` kullandı | `k` taraması yapılmadı; tavana çarpma oranı ölçütü uygulanmadı |
| Durma kuralı | doğrulandı | `no_progress_limit`, künyede, `tests/test_stopping_rule.py`; eşik 40 (`config/recording.yaml`, kurulum protokolü 19.6) | Kör noktası açık (S-25), tekrar tespiti yok |
| Estimand, kısıtlanmış ortalama, bootstrap, Wilcoxon | tasarlandı | `scripts/analyze_experiment.py` tam küme bitmeden yalnız betimsel (K-186) | Onaylayıcı analiz kodu yok |
| Duyarlılık: tavanın 1,5 ve 2 katı | tasarlandı | — | — |
| Çıkarıcı kontrol ve toplanabilirlik sınaması | tasarlandı | — | — |
| Ezberleme kapısı | tasarlandı | — | Normalize eylem dizisi eşleşmesi |
| Ön koşul kapısı | doğrulandı | **11 Ağustos 2026'da ateşledi.** Üç boyut otuz görevde sıfır çözdü; 12 Ağustos'ta sınır kontrolü sıfırların modelden geldiğini gösterdi (20/30); 32B aynı otuz görevde 11/30 | Kapıyı otomatik uygulayan kod yok, elle koşuldu |
| Üç yanlışlama kapısı | tasarlandı | — | `11-falsification.tr.md` kayıtları boş |
| Mekanizma başına terk kriteri | tasarlandı | — | İndeksin asgari boyutu yazılmadı; sayılacak şeyin **getirilebilir** kalıp olduğu S-48 ile netleşti |
| Ayar bütçesi | doğrulandı | Sıfır (ön kayıt A.9'un 25 Eylül eki, K-177); ölçümü tanımlayan bir yol ilk deney epizodundan beri değişirse sürücü duruyor (K-185) | — |
| Ölçek ekseni yorum tablosu | tasarlandı | — | Dört şekil için yorum yazılmadı |

## Beceri dili ve hata taksonomisi

| Öğe | Durum | Kanıt | Eksik |
|---|---|---|---|
| Beceri madenciliği, argüman sınıfları, birleştirme | doğrulandı | `src/zihin/compiler.py`; 4 beceri, bağlı 13 / serbest 14, `SKILL_SPEC.md`'nin dokuz değişmezi doğrulama kapısında | Sabit sınıfı tek beceride görüldü (`page_limit`) |
| Suç atfı, üç kapı | tasarlandı | — | Beceri hiç çağrılmadı; sicil sütunları `skills` tablosunda yok, uygulanmadılar (`S-81`, `K-202`) |
| Adım düzeyi taksonomisi, beş kategori | doğrulandı | `zihin.recording_agent.adim_kategorisi`; şemada `CHECK` kısıtı; 958 adımda profil ölçüldü | — |
| Eylem düzeyi taksonomisi, on etiket | tasarlandı | Durum kodu ve hata sınıfı kayıtta | Öncelik sırası ve etiketleme kodu |
| Epizot düzeyi, beş etiket | uygulandı | `episodes.termination_reason` ve doğrulayıcı hükmü | Beş etiketin tamamına eşleme yok |
| Tekrar ekseni | tasarlandı | İki epizotta ölçüldü ve merkezî çıktı (S-25) | Etiket olarak yok; ne durma kuralında ne taksonomide |
| Bağlam koşulu, kapalı koşul dili, karşıtsal indirgeme | doğrulandı | `src/zihin/failure_index.py`; 15 kalıp, koşullu 13'ünde koşul, karşıtsal küme aynı ucun başarıları; `tests/test_failure_index.py` 14 | Dilin üç biçiminden yalnız biri gözlenebiliyor (K-83); 409 kapsam dışı (S-43) |

## Altyapı

| Bileşen | Durum | Kanıt | Eksik |
|---|---|---|---|
| Depo iskeleti, bağımlılık kilidi, CI | doğrulandı | PR #2; CI beş iş koşuyor (bağımlılık kurulumu, lint, testler, import ve build, sandbox), temiz klon kurulumu elle koşuldu | — |
| AppWorld kurulumu | doğrulandı | `appworld install` ve `download data` geçti, dört bölme 90/57/168/417 görev döndürdü, CI AppWorld dahil kuruyor (K-32) | — |
| Epizot başına veritabanı sıfırlaması | doğrulandı | `tests/test_appworld_reset.py`; koşu 1'in notu koşu 2'de `409` veriyor | CI'da koşmuyor (S-12) |
| Tek görev uçtan uca | doğrulandı | `scripts/run_single_task.py`; ajan çağırıyor, doğrulayıcı hüküm üretiyor | — |
| WSL–Windows model sunucusu köprüsü | doğrulandı | Mirrored ağ kipi, DNS ayrıca sınandı (K-34) | — |
| Eylem düzeyi yanıt ve durum kaydı | doğrulandı | `src/zihin/api_capture.py`; 401 dahil yakalanıyor, kayıt noktası `raise`'den önce, `tests/test_api_capture.py` | — |
| Durum sondası, canlı veritabanı sayımı | doğrulandı | `src/zihin/state_probe.py`; `steps.state_change` üç hâl taşıyor, `tests/test_stopping_rule.py` | Güncellemeyi görmüyor; yazma kümesi `statik ∪ ampirik` (K-41), statik yarı kod olarak yok |
| Künye sözleşmesi | doğrulandı | Zorunlu-dolu alanlar, `tests/test_manifest_contract.py`; çıktı bütçesi alanı, `serving_mode` ve eski veritabanı taşıması dahil | — |

## Kurulum aracı betikleri

`measure_band.py`, `measure_gpt4o_subset.py` ve `measure_boundary_control.py`
**kurulum aracı**, deney yolunda değil. `scripts/setup` altındalar ve deney
matrisine girmiyorlar.

## Bir sonraki adım

Sıradaki adım deneyin faz 1'i: ilk dilim Colab'da
(`scripts/run_experiment.py dny --tasks N`, kurulum protokolü 19.6). Pilot raporu
`PILOT_REPORT.md`, demo raporu `docs/reports/uctan-uca-demo.md`, kapanış notları
`docs/reports/mekanizma-kapanis-notlari.md` içinde.
