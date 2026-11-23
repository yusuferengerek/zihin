# Sınırlamalar

Bildiğimiz kısıtlar. Ölçülmemiş olanlar ölçüldükçe buraya sayı girecek.
Kapatılabilenlerin üstü kapatıldıklarında çizilecek.

<!-- HARITA BASLANGIC: uretilmis, elle duzenlenmiyor -->

**83 sınırlama: 65 açık, 18 kapandı.** Bu tablo üretiliyor; elle düzenlenen bir kopyası yok (`scripts/build_limitations_index.py`). Kayda gitmek için kimliği arayın.

**Açık maddelerin ekseni:** 53 bir iddiayı sınırlıyor, 12 kapsam, 0 sınıflandırılmadı, 0 henüz işaretsiz. Eksen her kaydın başlığının altındaki ilk alıntı satırından okunuyor; bir maddeyi “sınırlıyor” saymak için sınırladığı iddia adıyla yazılıyor (K-107).

**Açık maddelerin kapanma sınıfı:** 11 dış olgu, 11 ölçüldü ve kısıt gerçek çıktı, 30 sonraki tur, 13 kalıcı kayıt, 0 sınıfsız. Ölçüt tek soru: *bu kaydı kapatacak iş kimin elinde?* Yalnız üçüncü sınıf kapanabilir — yani 65 açık maddenin 30 tanesi geçici, kalan 35 tanesi belgede kalıcı.

| | Sınırlama | Durum | Eksen | Kapanma |
|---|---|---|---|---|
| `S-01` | AppWorld yayımlanmış bir sürüme değil, hareketli bir dala sabitli | açık | sınırlıyor | Dış olgu |
| `S-02` | Referans çözümler yalnız train ve dev'de var | açık | kapsam | Dış olgu |
| `S-03` | Görev başına uygulama listesi test bölmelerinde yok | açık | sınırlıyor | Dış olgu |
| `S-04` | Doğrulayıcı hükmünün iki bileşeni ayrı ayrı çıkarılamayabilir | açık | sınırlıyor | Sonraki tur |
| `S-05` | Eylem düzeyinde yanıt gövdesi yok, durum kodu da yok | açık | sınırlıyor | Dış olgu |
| `S-06` | Bir sunucu süreci aynı anda tek bir dünya tutuyor | açık | kapsam | Dış olgu |
| `S-07` | İskelenin kendi bağlam kesme mantığı var | açık | kapsam | Dış olgu |
| `S-08` | 8 GB VRAM'e üç model aynı anda sığmıyor | açık | kapsam | Dış olgu |
| `S-09` | WSL bellek sınırı host geneli | açık | kapsam | Dış olgu |
| `S-10` | ~~WSL içinden Windows host'taki Ollama'ya erişim henüz çözülmedi~~ | kapandı | — | — |
| `S-11` | ~~Ajan davranışı aynı seed'de bile oynak~~ | kapandı | — | — |
| `S-12` | ~~Sıfırlama testi CI koruması altında değil~~ | kapandı | — | — |
| `S-13` | Sunucu tarafında görmediğimiz bir durum daha var | açık | sınırlıyor | Sonraki tur |
| `S-14` | Ölçek ekseninin en küçük noktası taban etkisine yapışmış | açık | sınırlıyor | Sonraki tur |
| `S-15` | Yazma yapan GET uçlarının listesi alt sınır | açık | sınırlıyor | Sonraki tur |
| `S-16` | Eylem düzeyi yanıt verisi enstrümantasyonu henüz yok | açık | sınırlıyor | Sonraki tur |
| `S-17` | Adım tavanı ile çapa farklı birimde | açık | sınırlıyor | Sonraki tur |
| `S-18` | Soğuk rejim 7B'de tekdüze değil | açık | sınırlıyor | Ölçüldü |
| `S-19` | 3B'nin sıfır çağrısı yetenek tabanı değil, sistematik bir hata | açık | sınırlıyor | Sonraki tur |
| `S-20` | Küçük modellerin baskın hatasını iyi biçimli tek bir örnek kapatabilir | açık | kapsam | Sonraki tur |
| `S-21` | Artık varyansa nokta kestirim değil üst sınır yazılıyor | açık | sınırlıyor | Ölçüldü |
| `S-22` | Sansür oranı beş göreve ve model başına tek epizoda dayanıyor | açık | sınırlıyor | Sonraki tur |
| `S-23` | Bu model sınıfı için yayımlanmış taban oranlarına tasarımdan önce bakılmadı | açık | sınırlıyor | Kalıcı kayıt |
| `S-24` | Dış inceleme ön koşul sorusunu sormadı | açık | sınırlıyor | Kalıcı kayıt |
| `S-25` | ~~Durma kuralı başarılı okumayı ilerleme sayıyor~~ | kapandı | — | — |
| `S-26` | Aynı çıktı bütçesi model ailesine göre aynı koşul demek değil | açık | sınırlıyor | Ölçüldü |
| `S-27` | Bant taraması eski durma kuralıyla koşuldu, ön koşul kapısı ona dayanıyor | açık | sınırlıyor | Sonraki tur |
| `S-28` | ~~Künye alanı yanlış çağrı yerine yazıldı, otuz epizot düştü, nöbetçi ateşlemedi~~ | kapandı | — | — |
| `S-29` | ~~Künye sözleşmesinin makine tarafı yalnız sıfırdan kurulan veritabanında geçerli~~ | kapandı | — | — |
| `S-30` | ~~Çıktı bütçesi ortamdan okunuyordu ve sessiz varsayılanı yanlış koşu başlattı~~ | kapandı | — | — |
| `S-31` | ~~Devam mantığı iki farklı ölçüm koşulunu sessizce birleştirebiliyordu~~ | kapandı | — | — |
| `S-32` | Durma kuralının uç nokta ölçütü hiç yürürlükte olmamıştı | açık | sınırlıyor | Sonraki tur |
| `S-33` | Makine okunur karar kaydı düzyazı ayrıştırılarak üretiliyor | açık | sınırlıyor | Sonraki tur |
| `S-34` | Sınır kontrolü ilan edilen koşulda koşmadı: düşünme açıktı | açık | sınırlıyor | Sonraki tur |
| `S-35` | ~~Yazma kümesinin iki kaynağı bir uçta anlaşmıyordu~~ | kapandı | — | — |
| `S-36` | ~~İki rota şablonu aynı yolu eşliyor, çözümleyici yanlış cevap veriyordu~~ | kapandı | — | — |
| `S-37` | ~~`update` bir model fiili değil, ve iki saf okumayı yazar yaptı~~ | kapandı | — | — |
| `S-38` | ~~Yazma kümesi türetmesi `@app.delete` süslemesini yazma çağrısı sanıyordu~~ | kapandı | — | — |
| `S-40` | Bağlı argüman tespiti ajanın yazdırdığı kadarıyla sınırlı | açık | sınırlıyor | Sonraki tur |
| `S-41` | Son koşulların çoğu v0'da boş, çünkü atıf yalıtım gerektiriyor | açık | sınırlıyor | Ölçüldü |
| `S-42` | ~~Bağlılık epizot boyunca aranıyordu, gövde içinde değil~~ | kapandı | — | — |
| `S-43` | 409 sınıfı v0 indeksinin kapsamı dışında | açık | sınırlıyor | Ölçüldü |
| `S-44` | `actions.error_class` tek değerli, sinyal durum kodunda | açık | sınırlıyor | Ölçüldü |
| `S-45` | İndeks kartlarının koşulu tesadüfen ayırabiliyor, ve kart bunu kendi üstünde taşıyor | açık | sınırlıyor | Ölçüldü |
| `S-46` | ~~Mimari belgesindeki sabit blok payı ölçülmemişti ve yanlıştı~~ | kapandı | — | — |
| `S-47` | Bağlayıcı bağlam sınırı jeton penceresi değil, iskelenin karakter tavanı | açık | sınırlıyor | Dış olgu |
| `S-48` | İndeksin en sık kalıbı hiçbir görev tarafından getirilemiyor | açık | sınırlıyor | Ölçüldü |
| `S-49` | ~~Kırk beş test CI'da hiç koşmamıştı, ve iki ortam farkı yerelde görünmüyordu~~ | kapandı | — | — |
| `S-50` | Yönetim rotalarının hepsi kesilemiyor: on biri dünyayı kurmak için gerekli | açık | sınırlıyor | Ölçüldü |
| `S-51` | Konteynerin ortam sunucusu ajanın koduyla aynı süreçte | açık | sınırlıyor | Dış olgu |
| `S-52` | Vekil `error_class` alanını dolduramıyor, çünkü telde istisna yok | açık | sınırlıyor | Sonraki tur |
| `S-53` | ~~Kaydedicinin montaj noktası uzak kipte ateşlemiyordu, ve sessizdi~~ | kapandı | — | — |
| `S-54` | Durum sondasının kör noktası kapandı, ama **ileriye dönük** | açık | sınırlıyor | Sonraki tur |
| `S-56` | Gürültü tabanı sıfır değil: tek epizottan çıkarılabilecek her iddianın üst sınırı | açık | sınırlıyor | Ölçüldü |
| `S-57` | Kimlik doğrulama bariyerini aşmak gerekli ama yeterli değil | açık | sınırlıyor | Sonraki tur |
| `S-58` | 32B ölçümü ilan edilen iki koşulda sapmış koştu | açık | sınırlıyor | Sonraki tur |
| `S-59` | 32B sonucu eksik kümeden ve bağlayıcı tavandan okundu | açık | sınırlıyor | Sonraki tur |
| `S-60` | Tekrarlanabilirlik doğrulaması bir ana ait; dış bir servis onu geriye dönük geçersizleştirebiliyor | açık | sınırlıyor | Kalıcı kayıt |
| `S-61` | Ölçek ekseninin noktaları üç farklı kartta ölçüldü | açık | sınırlıyor | Kalıcı kayıt |
| `S-62` | Bant etiketi zorluğu değil referans çözümün yolunu gösteriyor | açık | sınırlıyor | Dış olgu |
| `S-63` | Ön koşul bulgusunun dayandığı üç koşudan ikisi tavan sınırlı, biri kayıtta yok | açık | sınırlıyor | Kalıcı kayıt |
| `S-64` | Birleşmemiş iş hiçbir denetimin öznesi değil | açık | sınırlıyor | Sonraki tur |
| `S-65` | Hata indeksi korpusun gerisinde kaldı: kayıttaki on beş kart, bugünün korpusu yirmi veriyor | açık | sınırlıyor | Sonraki tur |
| `S-66` | Aralık genişliği taramasının gürültü modeli iki hücreden geliyor | açık | sınırlıyor | Sonraki tur |
| `S-67` | Ezberleme kapısı, tasarımın taşıyamadığı bir ayrım | açık | sınırlıyor | Sonraki tur |
| `S-68` | Türetilen geçiş oranı eşiği ölçülenin iki buçuk katı: deney bu hâliyle güçsüz | açık | sınırlıyor | Sonraki tur |
| `S-69` | Denetimlerin öznesi depo; kullanıcının elindeki kopyalar dışarıda | açık | sınırlıyor | Kalıcı kayıt |
| `S-70` | Defter denetiminin iki kuralı düzyazıyı örüntüyle okuyor | açık | sınırlıyor | Sonraki tur |
| `S-71` | Devam eden bir epizodun künyesi ilk denemenin makinesini anlatıyor | açık | sınırlıyor | Sonraki tur |
| `S-72` | Madenci koşunun epizotlarını değil dosyanın tamamını okuyor | açık | sınırlıyor | Sonraki tur |
| `S-73` | A dalının ilk 188 epizot için hiçbir gözlemi yok | açık | sınırlıyor | Kalıcı kayıt |
| `S-74` | Seri 3, 26 Ağustos'tan beri iki dosyada; 13–25 Eylül arasında yarısı depodaki kayıtta yoktu | açık | sınırlıyor | Sonraki tur |
| `S-75` | Eşik türetmesinin eseri ilan edilmemiş bir argümanla üretilmişti | açık | sınırlıyor | Kalıcı kayıt |
| `S-76` | Dil denetimi yalnız Python dosyalarını tarıyor | açık | sınırlıyor | Sonraki tur |
| `S-77` | A.5'in eylemsizlik örneği tek bir epizot ve tekrarlanmadı | açık | sınırlıyor | Kalıcı kayıt |
| `S-78` | Bir test görevinin yönergesi eserden çıkarıldı; özgün metin bu deponun geçmişinde | açık | kapsam | Kalıcı kayıt |
| `S-79` | Üç train görevinin yönergesi belgelerden çıkarıldı; özgün metinler bu deponun geçmişinde | açık | kapsam | Kalıcı kayıt |
| `S-80` | ~~Rota testinin örnek günlüğü artık bir train görevinden, ama hâlâ bir AppWorld türevi~~ | kapandı | — | — |
| `S-81` | ~~`SKILL_SPEC.tr.md` ile `skills` tablosu dokuz alanda ayrışıyor ve defterde karar yok~~ | kapandı | — | — |
| `S-82` | Eski taramalar boşlukları normalleştirmiyordu; bir train talimatı alıntısı iki yerde kaldı | açık | kapsam | Kalıcı kayıt |
| `S-83` | Bir testin AppWorld çıktıları gölge kipi korpusuna girdi; engellemelerden biri testin kendi çağrısıydı | açık | kapsam | Kalıcı kayıt |
| `S-84` | Dil denetimi açık bir klonda, kayıt veritabanları geri yüklense bile geçemiyor | açık | kapsam | Ölçüldü |
| `S-85` | Kayıtlı koşular eski kilitle alındı, deney yenisiyle koşacak | açık | kapsam | Sonraki tur |

<!-- HARITA BITIS -->

**Ek — 15 Kasım 2026: S-39 ve S-55 hiç verilmedi.** Sayaç S-39'u, 15 Ağustos 2026'da
S-40 S-38'in hemen ardından yazılırken (`7266048`), S-55'i de 18 Ağustos 2026'da S-56
S-54'ün hemen ardından yazılırken (`4c573ce`) atladı. Hiçbir kayıt kaybolmadı.
Haritadaki 81, kayıtların sayısı.

<!-- IDDIA HARITASI BASLANGIC: uretilmis, elle duzenlenmiyor -->

**39 iddia, 53 sınırlama.** Bu tablo yukarıdakinin ters yönü: her iddianın altında kaç sınırlama durduğu. Sekiz sınırlaması olan bir iddia zar zor iddiadır ve bu ancak buradan görünüyor. Üretiliyor; elle düzenlenen kopyası yok (K-107).

| İddia | Sınırlama | Kimlikler |
|---|---|---|
| 07-failure-taxonomy | 4 | `S-05`, `S-16`, `S-43`, `S-44` |
| K-58 | 4 | `S-19`, `S-23`, `S-27`, `S-63` |
| 05-experiment-design | 3 | `S-04`, `S-17`, `S-32` |
| 02-research-question ikinci soru | 2 | `S-14`, `S-61` |
| 04-threat-model | 2 | `S-15`, `S-51` |
| K-51 | 2 | `S-18`, `S-21` |
| REPRODUCE.md | 2 | `S-01`, `S-60` |
| docs/reports/b32-olcumu.md | 2 | `S-58`, `S-59` |
| sınır kontrolü | 2 | `S-26`, `S-34` |
| 03-architecture | 1 | `S-47` |
| 06-skill-language | 1 | `S-40` |
| 10-external-review | 1 | `S-24` |
| A.1 | 1 | `S-68` |
| A.5 | 1 | `S-77` |
| Bant başına raporlanan her sonuç | 1 | `S-62` |
| Bu depodaki her denetim | 1 | `S-69` |
| DATA_MODEL.md | 1 | `S-52` |
| Getiricinin kapsama ve ayırt edicilik sayıları | 1 | `S-65` |
| K-21 | 1 | `S-13` |
| K-53 | 1 | `S-22` |
| K-85 | 1 | `S-45` |
| K-93 | 1 | `S-54` |
| K-95 | 1 | `S-50` |
| PILOT_REPORT.md | 1 | `S-48` |
| PILOT_REPORT.md ayna bulgusu | 1 | `S-57` |
| PILOT_REPORT.md kalkan bölümü | 1 | `S-03` |
| PILOT_REPORT.md ve uçtan uca demo | 1 | `S-56` |
| SKILL_SPEC.md | 1 | `S-41` |
| Y-2 | 1 | `S-67` |
| `K-139` | 1 | `S-74` |
| `K-77` | 1 | `S-76` |
| `results/interval-width.json` | 1 | `S-66` |
| `results/pass-threshold.json` | 1 | `S-75` |
| `run_manifests.boot_id` ve `created_at` | 1 | `S-71` |
| `scripts/check_colab_notebook.py` | 1 | `S-70` |
| `scripts/check_merged_artefacts.py` | 1 | `S-64` |
| experiments/decisions.csv | 1 | `S-33` |
| §18.1 | 1 | `S-72` |
| §18.3 dal A | 1 | `S-73` |

<!-- IDDIA HARITASI BITIS -->

---

## S-85 — Kayıtlı koşular eski kilitle alındı, deney yenisiyle koşacak

> **Kapsam.** Deneyden önceki koşulardan gelen sayılarla deneyin epizotları arasındaki bağımlılık farkı (`K-207`)

> **Kapanma sınıfı.** Sonraki tur — kayıtlı bir epizot kümesini yeni kilitle yeniden koşup yörüngeleri karşılaştırmak bu kaydı kapatır

**Ne değişti.** `K-207` sekiz paketi güncelledi: aiohttp, certifi, dnspython, filelock,
multidict, pyjwt, urllib3 ve yarl. Kaydın bütün koşuları önceki kilitle alındı, deneyin bütün
epizotları yenisiyle alınacak. Deneyin kendi karşıtlıkları bundan etkilenmiyor, çünkü
koşulların hepsi aynı kilitle koşacak.

**Neyi etkiliyor.** Ön kayıt ve kurulum protokolü bazı sayıları deneyden önceki koşulardan
alıyor ve deneyde değiştirmeden kullanıyor:
- adım tavanının çapaları, bant taramasından,
- güç hesabının dayandığı eylem tabakası oranı (`results/stratum-rates.json`),
- 32B'nin kendi `train` epizotlarından madenlenen kütüphane ve indeks.

Bunlar eski kilitle ölçüldü. Değişen paketlerin hiçbiri modelde, iskelenin ajan mantığında ya
da ölçümü tanımlayan kodda değil. AppWorld'ün sunucusunda duruyorlar (pyjwt fastapi-login
üzerinden, dnspython email-validator üzerinden, filelock), HTTP istemcilerinde (urllib3
requests üzerinden, certifi httpx ve requests üzerinden) ve litellm'in bağımlılıklarında
(aiohttp, multidict, yarl). Bir epizodun yörüngesini değiştirip değiştirmedikleri ölçülmedi.
`K-19`'un taşıma katmanı şartı, "aynı mesajlar gitsin ve aynı metin dönsün", bu sürümler için
sınanmadı.

**Görmeyen bir denetim.** `uv.lock` ölçümü tanımlayan yollar listesinde değil
(`zihin.records.MEASUREMENT_DEFINING_PATHS`). Kilit deney sırasında yeniden değişirse
`scripts/analyze_experiment.py` dilimleri bu değişikliğe göre ayırmaz. Sandbox imajı da
`uv.lock`'u içine kopyalıyor, yani `Containerfile` değişmeden imajın içeriği değişebiliyor.

---

## S-84 — Dil denetimi açık bir klonda, kayıt veritabanları geri yüklense bile geçemiyor

> **Kapsam.** Açık deponun bir klonunda `scripts/check_language.py`, bekçi değişmeden

> **Kapanma sınıfı.** Ölçüldü — dört kayıt veritabanı geri yüklense de derlemde yalnız arşivin makinesinde duran koşu çıktıları eksik

**Ne ölçüldü.** 22 Kasım 2026'da `41be190` arşiv commit'inin açık ağacı kuruldu, tek
commit'lik bir depoya dönüştürüldü ve dört kayıt veritabanı eklerinden
`scripts/restore_records.py` ile içine geri yüklendi. Orada `scripts/check_language.py`
1 ile çıkıyor ve 58 Türkçe dizge bırakıyor: 13 dosyada 36 ayrı dizge. Arşivde aynı
commit'te ve aynı gün 0 ile çıkıyor. İkisi de aynı 160 dosyayı tarıyor.

| | Açık klon, veritabanları geri yüklü | Arşiv |
|---|---|---|
| Derlemdeki veri dizgeleri | 20 215 | 22 519 |
| Bunlardan kayıttan gelen | 17 929 | 17 915 |
| Kalan Türkçe dizge | 58 | 0 |

Klonun kayıt payı daha büyük, çünkü klonda arşivin yalnız geçmişinde tuttuğu
`results/zihin-3-colab.sqlite` da var.

**Neden.** Bekçinin derlemi, kayıttaki ve `results/` ile `experiments/` altındaki her
anahtar ve tanıtıcı biçimli değer, ve oradaki her dosya adı. Arşivde kayıt veritabanları
dışında `results/` altındaki 34 girdi ve `experiments/outputs` altındaki 437 girdi
(1,9 GB) git'in izlemediği koşu çıktıları. Ne açık ağaç ne de kayıt ekleri onları
taşıyor. Klonun atılabilir kopyalarına konduklarında farkın tamamını açıklıyorlar:

| Klona eklenen | Kalan Türkçe dizge |
|---|---|
| hiçbir şey | 58 |
| izlenmeyen 34 `results/` girdisi | 2 |
| `experiments/outputs` | 56 |
| ikisi birden | 0 |

**Ne anlama gelmiyor.** Bekçinin bildirdiği dizgeler Türkçe düzyazı değil, o izlenmeyen
çıktıların tanımladığı adlar. Bekçi arşivde `scripts/local_checks.sh` üzerinden koşmaya
devam ediyor ve orada geçiyor. CI onu koşmuyor. Açık bir klonda geçmesi ya o çıktıların
dağıtılmasını ya da bekçinin değişmesini gerektirir. Burada ikisi de yapılmıyor.

## S-83 — Bir testin AppWorld çıktıları gölge kipi korpusuna girdi; engellemelerden biri testin kendi çağrısıydı

> **Kapsam.** `results/shadow-mode.json`'dan alıntılanan engelleme sayılarını düzeltiyor; sonuç dosyası yeniden yazılmıyor

> **Kapanma sınıfı.** Kalıcı kayıt — sayılar alıntılandıkları belgelerde tarihli düzeltmelerle düzeltildi

**Ne oldu.** `tests/test_appworld_reset.py`, eklendiği `e26e09c`'den (10 Ağustos 2026)
`a995af7`'ye (14 Kasım 2026) kadar AppWorld'ün iki koşusunu çalışma dizinine,
`experiments/outputs/reset-check-1` ve `reset-check-2` altına yazdı.
`scripts/setup/measure_shadow_mode.py` o dizindeki her `api_calls.jsonl`'ı kayıtlı bir
epizot sayıyor. 28 Ağustos'ta `d76d932` ile giren `results/shadow-mode.json`'ın kendi
girdi listesi (`per_experiment`) iki dizini de taşıyor: 2 epizot, 9 çağrı, 1 engelleme.
Engellenen çağrı testin `simple_note`'ta açtığı not. `82e2fac_1`'in talimatından
çıkarılan izinli uygulamalar `simple_note`'u içermiyor.

**Nasıl bulundu.** Açık ağaçta derlem testi ilk koşuda atlanıp ikinci koşuda geçiyordu,
çünkü birinci koşu bu iki dizini yazıyordu. Kullanıcı, `experiments/outputs`'u okuyan her
betiğin girdisinde bu iki dizinin olup olmadığının ölçülmesini istedi.

**Okuyucular.** Dizinin tamamını tarayan tek ölçüm betiği `measure_shadow_mode.py`. Öbür
betikler yalnız kendi adlandırdıkları deneyleri okuyor ve hiçbir `reset-check-*` adı
onların öneklerine uymuyor. `scripts/check_language.py` `experiments/**/*.json`'ı da
okuyor, ama o bir bekçi ve kayıtlı bir sayı üretmiyor.

**Yeniden hesap.** Betik geçici bir dizinde, kaydın girdi listesindeki deneylerle, iki
dizinle ve onlarsız koşuldu. Kayıt dosyasına dokunulmadı. Diskte duran 243 deneyin her
satırı kayıttakiyle aynı çıktı. Kayıttan tek fark sonradan silinmiş üç `durum-sondasi`
dizini, ve onların payı kaydın kendi satırlarından alındı.

| Sayı | Kayıttaki | Test çıktıları olmadan |
|---|---|---|
| Epizot | 258 | 256 |
| Çağrı | 9154 | 9145 |
| Engellenen çağrı | 6 = %0,07 | 5 = %0,05 |
| Engellenen epizot | 6 = %2,33 | 5 = %1,95 |
| Engellenen görev | 1/58 = %1,72 | 1/58 = %1,72 |
| Okuma / izinli yazma / izinsiz yazma | 8631 / 517 / 6 | 8623 / 517 / 5 |
| İlk gölge koşu, S-37'den önce | 8/9154 = %0,09 | 7/9145 = %0,08 |

Son satır yeniden koşulamadı, çünkü o günün yazma kümesi depoya hiç girmedi. Türetildi:
S-37'ye göre o küme bugünkünden yalnız `update` fiilinin iki uç noktasıyla ayrılıyordu,
ve test bu ikisini çağırmıyor.

**Belirlenemeyen.** `src/zihin/api_routes.py`, `tests/test_api_routes.py` ve S-36 "239
kayıtlı epizottaki 7138 çağrının 7138'i çözülüyor" diyor (`fd28a43`, 14 Ağustos). Bu
ölçümün girdi listesi yok. Günlüklerin zaman damgalarıyla da kurulamadı: o saatten önce
yazılmış günlükler bugün 235 epizot ve 7121 çağrı veriyor, ve iki test dizini ile
silinmiş üç `durum-sondasi` dizininin hiçbir bileşimi 239/7138'i tam vermiyor. Test
çıktıları girdiyse sayı 237 epizotta 7129/7129 olurdu. Bütün çağrıların çözüldüğü iddiası
iki durumda da doğru.

**Kapandı, 15 Kasım 2026: sonda koşuları korpusta kalıyor.** Karar kullanıcıya ait.
Korpusun tanımı değişmiyor. İki `reset-check` dizini içerikleri yüzünden çıkarılmadı.
Onları oraya bir kusur koymuştu: test depoya yazıyordu ve bu `a995af7`'de düzeltildi.
Sonda koşuları ise bilerek yapılmış koşular ve betiğin tanımının içinde kalıyor:
`experiments/outputs` altında, `legacy_` ile başlayanlar dışındaki her koşu. Sonucu
gördükten sonra tanımı daraltmak kabul edilemez. Ölçülen şu: kalan beş engellemenin beşi
de sonda koşularından geliyor (`durum-sondasi-2`, `durum-sondasi-3`, `notlar`,
`sifirlama2-1`, `sifirlama3-1`) ve hiçbiri bir model epizodundan gelmiyor. `sifirlama3-1`,
`reset-check-1`'in çağrı dizisini birebir tekrarlıyor. Bu, staj raporunun model
yörüngelerinde engellemenin sıfır olduğunu söyleyen cümlesiyle örtüşüyor. Yalnız model
epizotlarını sayan bir oran açık bir olasılık olarak duruyor, yapılacak bir iş olarak
değil. Hesaplanırsa önce kuralı tarihli bir ek olarak yazılır, bütün deneylere aynı
biçimde uygulanır ve mevcut sayının yanında verilir. Hiçbir zaman onun yerine geçmez.

**Ne yapıldı.** Test artık AppWorld'ün kökünü kendi geçici dizinine taşıyor (`a995af7`).
Sayılar alıntılandıkları belgelerde tarihli düzeltmelerle düzeltildi: `PILOT_REPORT.md`,
`PROJECT_STATUS.md`, K-72, `docs/reports/kapanis-raporu.md`,
`docs/reports/mekanizma-kapanis-notlari.md`, `experiments/setup-protocol.tr.md` ve
`experiments/setup-protocol.en.md`, S-37 ve staj raporu. `PULL_REQUESTS.md` değişmedi,
çünkü PR gövdelerini yazıldıkları gibi taşıyor ve onların düzeltmesi bu kayıt.
`results/shadow-mode.json` yeniden yazılmadı.

## S-82 — Eski taramalar boşlukları normalleştirmiyordu; bir train talimatı alıntısı iki yerde kaldı

> **Kapsam.** bir talimat alıntısının nerede kaldığını ve hangi taramaların onu kaçırdığını kaydediyor; ölçülmüş bir sonucu değiştirmiyor

> **Kapanma sınıfı.** Kalıcı kayıt — commit iletileri yeniden yazılmıyor; düzeltme bu kayıt ve ayıklama

**Ne oldu.** `train` görevi `692c77d_1`'in talimatının 129 karakterinden 77'si iki yerde
harfi harfine duruyordu: `docs/reports/asama-2.md` (satır 131–132, `ddcc320` ile, #5'te
girdi) ve aynı raporu taşıyan PR gövdesinin `PULL_REQUESTS.md`'deki kopyası. Alıntı bir
satır sonunu aşıyordu. D5'in taraması ve sonraki taramalar boşlukları normalleştirmeden
arıyordu, bu yüzden satır sonunu aşan alıntıyı görmedi.

**Yanlış olan ifade.** `71be1ca`'nın commit iletisi `PULL_REQUESTS.md` için "Asistan adı ve
görev talimatı taraması temiz" diyor. Bu alıntı için yanlıştı. `239be07`'nin iletisi
yalnız asistan adı taramasından söz ediyor; görev talimatı için bir iddiası yok. İletiler
yeniden yazılmıyor; düzeltme bu kayıt.

**Ne yapıldı.** Rapordaki alıntı D5 biçimine çevrildi: görev kimliği ve özgün talimatın
sha256'sı. `PULL_REQUESTS.md`'yi üreten araç, bir PR gövdesinde talimat metni bulduğunda
aynı biçimde bir yer tutucu koyuyor, ve dosyanın başlığı bunu söylüyor. Açık depo yapısı
her bölmedeki her talimatın her 40 karakterlik normalleştirilmiş penceresini arıyor;
satır sonu, blok alıntı işareti ve kalın vurgu bu taramayı atlatamıyor.

**Kalan.** Özgün metin bu deponun geçmişinde duruyor: `asama-2.md`'nin `ddcc320` ile
giren sürümleri ve `PULL_REQUESTS.md`'nin `71be1ca` ile `239be07` sürümleri.

## ~~S-81 — `SKILL_SPEC.tr.md` ile `skills` tablosu dokuz alanda ayrışıyor ve defterde karar yok~~ — KAPANDI: şartname düzeltildi, ölçüleni tablo tanımlıyor (K-202)

> **Kapsam.** şartnamenin alanları ile derleyicinin yazdığı tablo arasındaki farkları kaydediyor; hangisinin otoritatif olduğuna hükmetmiyor

> **Kapanma sınıfı.** Sonraki tur — şartnamenin mi kodun mu düzeltileceği deponun sahibinin kararı

**Kapandı, 18 Ekim 2026.** Karar verildi: şartname düzeltildi, koda dokunulmadı
(`K-202`).

**Kanıt.** `SKILL_SPEC.tr.md` ve `SKILL_SPEC.md` tarihli bir düzeltmeyle tabloyu
ölçülenin otoritatif tanımı sayıyor ve dokuz alanı, tasarlanıp o biçimiyle
uygulanmamış olarak listeliyor. `src/zihin/schema.sql` değişmedi.

**Neyin kapanmadığı.** Altı alanın uygulaması yok, çünkü beceriler çağrılmıyor.
Şartnamenin suç atfı ve düşürme kuralıyla ilgili bölümleri bu yüzden tasarım olarak
kalıyor ve ölçülmüş bir şeyi anlatmıyor.

**Ne ölçüldü.** Şartname 15 Ağustos 2026'da girdi (`51f3e0d`), `skills` tablosu bir gün
sonra (`142662f`). Tablo şartnamenin dokuz alanını başka adla tutuyor, başka içerikle
tutuyor ya da hiç tutmuyor:

| Şartnamedeki alan | `skills` tablosunda |
|---|---|
| *signature* | başka adla: `free_parameters` |
| *calls* | başka adla: `body`, uzunluğu `body_length` |
| *effect_suffix* | aynı ad, başka içerik: şartname yazan çağrıların indekslerini istiyor, tablo sonekin çağrılarını tutuyor |
| *precondition* | yok |
| *invocations*, *blamed_failures*, *postcondition_misses*, *model_failures_gate_1*, *model_failures_gate_2* | yok |

**Defter ne diyor.** Bu alanların adlandırılması ya da düşürülmesi için kayıtlı bir
karar yok, ve defter şartnamenin donduğunu da yazmıyor. `PROJECT_STATUS.md` suç
atfının üç kapısını "tasarlandı" diye gösteriyor: beceriler epizotlara kart olarak
verildi ve hiç çağrılmadı, yani sicil sayaçlarını dolduracak bir olay da olmadı.

**Neye dokunulmadı.** Ne şartname ne kod değişti. *kind* bu listede değil: K-75
kütüphaneye yalnız becerilerin girdiğini yazıyor, tablo buna uyuyor, ve şartname o
noktada tarihli bir düzeltmeyle düzeltildi.

## ~~S-80 — Rota testinin örnek günlüğü artık bir train görevinden, ama hâlâ bir AppWorld türevi~~ — KAPANDI: örnek günlük sentetik, AppWorld çıktısı taşımıyor

> **Kapsam.** `tests/test_api_routes.py`'nin okuduğu örnek günlüğün kaynağını ve lisans durumunu kaydediyor; buna dayanan bir iddiamız yok

> **Kapanma sınıfı.** Sonraki tur — örneğin şifrelenmesi ya da açık kopyadan çıkarılması deponun sahibinin kararı

**Kapandı, 13 Ekim 2026.** Örnek günlük sentetik oldu.

**Kanıt.** `tests/data/api_calls-synthetic.jsonl`'i `scripts/build_api_calls_fixture.py`
yazıyor: on rota üzerinde 22 çağrı, iki şablona birden fazla uydurma kimlikle gidiliyor,
her çağrının `data` alanı boş. Görev metni, model çıktısı ve yörünge yok.
`tests/data/api_calls-229360a_2.jsonl` ağaçtan çıktı. Testte dosya yolu, 42. satırdaki
yorum ve modül açıklaması değişti; test mantığı aynı. Beş koşulun her biri mutasyonla
sınandı ve her mutasyon hedeflediği testi düşürdü.

**On rota neden bunlar.** Eski örneğin rotaları, yani sabitlenmiş on uç nokta sayısı
değişmiyor. AppWorld'ün açık API Explorer'ı (https://appworld.dev/appworld/api-explorer)
onunu da uygulama, API adı, yöntem ve yolla gösteriyor.

**Neyin kapanmadığı.**
- Rota adları AppWorld'ün paketlerinden türetilmiş adlar. Site onları her ziyaretçiye
  gösteriyor, ama belgeyi şifreli gönderip tarayıcıda çözüyor ve her kayda bir canary
  dizgesi koyuyor; AppWorld'ün README'si de paketlerden türetilen verinin internete düz
  metin olarak konmamasını rica ediyor. Aynı rotaların çoğu ağaçta başka yerlerde de
  duruyor (`inputs/write-set-static.json`, testler). Bu, açık deponun tasarımına ait bir
  soru.
- Sentetik bir günlük üretimdeki biçim değişikliğini fark edemiyor. O denetim yerel
  korpus ölçümünde: `experiments/outputs` varken kayıttaki her çağrının aynı üç anahtarı
  taşıdığı sınanıyor.
- Eski iki örnek bu deponun geçmişinde duruyor.

**Ne değişti.** Rota testinin örnek günlüğü bir `test_normal` görevinden geliyordu:
`tests/data/api_calls-32616b5_1.jsonl`, `32616b5_1` görevinin `sinir3` koşusundaki 55
çağrı. Dosya ağaçtan çıktı; bu deponun geçmişinde duruyor (`fd28a43` ile girdi).
Yerine `tests/data/api_calls-229360a_2.jsonl` geldi: `train` görevi `229360a_2`, 43
çağrı, 10 uç nokta. Testin yalnız dosya yolu satırı değişti ve test geçiyor.

**Kaynağı neden bizim koşumuz değil.** Test tam 10 farklı uç nokta, en az 20 çağrı ve
birleşen kimlikler istiyor. Diskteki 132 `train` günlüğü ölçüldü. Testi değiştirmeden
geçen altı günlüğün hepsi AppWorld'ün yayımladığı gpt-4o koşusundan
(`legacy_react_code_agent/openai/gpt-4o-2024-05-13/train`); bizim koşularımızın hiçbir
`train` günlüğü bu koşulları karşılamadı. Temizlik eski örnekteki gibi: e-postalar takma
adlara, parola ve jeton alanları sabit bir dizgeye.

**Kapanmayan.** Yeni dosya da bir AppWorld deney çıktısı ve türevi. Lisansın şifreli
dağıtım şartı `train` ile `test`'i ayırmıyor, ve AppWorld'ün leaderboard yönergesi deney
çıktılarının şifresiz yayımlanmamasını istiyor. Değişiklik test bölmesinin kirlenmesini
kaldırıyor; lisans sorusunu kaldırmıyor.

**Eskiyen iki yer.** Modülün açıklaması ve 42. satırdaki yorum hâlâ eski örneği
anlatıyor (`sinir3-32616b5_1`, 55 çağrı). Bu değişikliğe yalnız dosya yolu satırının
değişmesi izin verildi.

## S-79 — Üç train görevinin yönergesi belgelerden çıkarıldı; özgün metinler bu deponun geçmişinde

> **Kapsam.** iki belgedeki alıntıların yerine ne konduğunu kaydediyor; belgelerin savunduğu şey değişmiyor

> **Kapanma sınıfı.** Kalıcı kayıt — bu depoda geçmiş yeniden yazılmıyor; açık kopya süzülmüş geçmişle kuruluyor

**Ne değişti.** Üç alıntı, AppWorld `train` görevlerinin yönergeleriydi. Yerlerine görev
kimliği ve özgün yönerge metninin sha256'sı kondu. Özet,
`data/tasks/<task_id>/specs.json` içindeki `instruction` alanının UTF-8 baytlarından:

| Yer | Görev | sha256 |
|---|---|---|
| `docs/reports/izinli-uygulama-vekili.md`, satır 66–67 | `2a163ab_1` | `sha256:8171d51f01bd488de4138feca6b3ffb19c89efb3b854da8f3e2729b19e156ca2` |
| `docs/reports/izinli-uygulama-vekili.md`, satır 69–70 | `afc0fce_1` | `sha256:2b1127911151dd1e34ed76e403c1109b09a26be2a41769650c880141d85e2166` |
| `docs/appworld-facts.tr.md`, satır 340–341 | `692c77d_1` | `sha256:a950a91993090db7f485be0426584f1860ec42f296285eec93e92d53eb7bc1cf` |

**Gerekçe.** AppWorld'ün veri lisansı, görev verisinin ve türevlerinin herkese açık
dağıtımının şifreli yapılmasını istiyor (`data/LICENSE`). Şart `train` ile `test`'i
ayırmıyor.

**Kalan.** Belgelerin savunduğu şey aynı. Vekil raporu hâlâ yönergenin hangi ilişki
sözcüklerini taşıdığını adıyla söylüyor ("roommates", "siblings", "coworkers"). Özgün
metinler bu deponun geçmişinde duruyor: `04c488a` ve `b863acf` ile giren sürümlerde.

## S-78 — Bir test görevinin yönergesi eserden çıkarıldı; özgün metin bu deponun geçmişinde

> **Kapsam.** `results/demo-eklenti.json`'un bir alanında ne durduğunu kaydediyor; ondan okunan sayılar değişmiyor

> **Kapanma sınıfı.** Kalıcı kayıt — bu depoda geçmiş yeniden yazılmıyor; açık kopya süzülmüş geçmişle kuruluyor

**Ne değişti.** `results/demo-eklenti.json`, satır 71, "gorev_metni" alanı, `test_normal`
görevi `0de03ea_1`'in yönergesini harfi harfine taşıyordu. Yerine görev kimliği ve özgün
yönerge metninin sha256'sı kondu:
`sha256:97d2ae07f37901ada1385075a28412fa3799f9bdd7c13a40e16853aefb0fdcbb`. Özet,
`data/tasks/0de03ea_1/specs.json` içindeki `instruction` alanının UTF-8 baytlarından.

**Gerekçe.** AppWorld'ün veri lisansı, görev verisinin ve türevlerinin herkese açık
dağıtımının şifreli yapılmasını istiyor (`data/LICENSE`). Bu bir test görevi; yönergesi
açık webe girerse gelecekteki eğitim taramalarının toplayabileceği yere girer.

**Kalan.** Dosyanın diğer alanları ve atıf alan sayıları aynı. Özgün metin bu deponun
geçmişinde duruyor: dosyanın `93889e5` ile giren ve bu değişiklikten önceki sürümleri.

## S-77 — A.5'in eylemsizlik örneği tek bir epizot ve tekrarlanmadı

> **İddiayı sınırlıyor.** A.5 — "eylemsizliğin ödüllendirilebildiği ölçüldü"

> **Kapanma sınıfı.** Kalıcı kayıt — bir kez gözlenmiş bir örnek geriye dönük çoğaltılamaz

Ön kayıt A.5 dereceli skorun neden tanı metriği olduğunu `0de03ea_1` üzerinden
anlatıyor: kartlı kol eyleme geçti, hiçbir şey yapmayan bir ajanın geçtiği bir
testi düşürdü, ve bedava bir geçişi kaybetti; no-op'a göre düzeltilince 2/3'e 0/3.
Bu gözlem **tek bir epizottan**: `demo` koşusunun kartlı epizodu.

**Ölçüldü** (`results/no-op-example.json`, `zihin.verification.graded_detail` ile).
Aynı görev kayıtta on iki kez koştu. Kartlı beş epizodun:

| Epizot | Anlamlı testler | Kaybedilen bedava test |
|---|---|---|
| `demo` kartlı — A.5'in alıntısı | 2/3 | **1** |
| karşılaştırılabilirlik koşusu, kartlı | 0/3 | 0 |
| üç kollu koşu, kartlı kol, üç tekrar | 0/3, 0/3, 0/3 | 0, 0, 0 |

Sonraki dört kartlı epizodun **hiçbirinde** kol bir bedava testi kaybetmedi, ve
anlamlı testlerin hiçbirini geçmedi. Örnek tekrarlanmadı; `S-56`'nın sınıfında:
tek epizottan okunan bir kol karşılaştırması, gürültü tabanının altında.

**A.5'in kuralını bağlamıyor.** Dereceli skorun tanı metriği olması ve ham geçiş
sayısının birincil olmaması, test dosyasının yapısına dayanıyor: eyleme geçen bir
ajanın düşürebileceği bir `no_op_pass` testi var, ve bu her epizotta aynı. Bağlanan
şey kuralın gerekçesi olarak sunulan **gözlem**: "ölçüldü" değil, "bir kez
gözlendi". Görev artık değerlendirme örnekleminde de değil (`K-166`).

## S-76 — Dil denetimi yalnız Python dosyalarını tarıyor

> **İddiayı sınırlıyor.** `K-77` — "yorumlar ve çalışma zamanı metinleri İngilizce"

> **Kapanma sınıfı.** Sonraki tur — denetimin kapsamı genişletilir ve kapsama giren dosyalar çevrilirse kapanır

`scripts/check_language.py` Türkçe arıyor ama yalnız `src/`, `tests/` ve
`scripts/` altındaki `.py` dosyalarında. "Turkish left: 0" bu kapsam hakkında
doğru; kod tarafının tamamı hakkında değil.

**Ölçüldü, 25 Eylül 2026.** Kapsamın dışında, izlenen **20 dosya** Türkçe
düzyazı taşıyor. En çoğu:

| Dosya | Türkçe harfli satır |
|---|---|
| `config/recording.yaml` | 72 |
| `.github/workflows/ci.yml` | 70 |
| `experiments/colab/zihin-colab.ipynb` | 57 |
| `config/sandbox.yaml` | 56 |
| `scripts/ci_simulasyonu.sh` | 44 |
| `pyproject.toml` | 42 |
| `scripts/local_checks.sh` | 37 |
| `config/models.yaml` | 35 |

Kalan on iki dosya: `.gitignore`, `Containerfile`, `scripts/serve_models.ps1`,
`scripts/colab_publish_results.sh`, `.gitattributes`, ve `config/` altında yedi
yapılandırma dosyası daha. Sayım Türkçeye özgü harflere bakıyor, yani diyakritiksiz Türkçe
satırlar bu sayıya girmiyor; sayılar bir alt sınır. Bir dosya adı da kuralın
dışında: `scripts/ci_simulasyonu.sh`.

**Kural ihlali olmayan Türkçe ayrı.** `experiments/decisions.csv` Türkçe karar
kaydından üretiliyor ve birkaç sonuç eseri kayıttaki Türkçe veri dizgelerini
taşıyor; bunlar kaynaklarının dili, ve `scripts/check_language.py`'nin veri kuralı
onları zaten ayırıyor.

**Neden bugüne kadar görünmedi.** Dil geçişi Python ağacı üzerinden yürüdü ve
denetim o ağaç için yazıldı. Yapılandırma yorumları, CI adımları ve kabuk
betikleri hiçbir denetimin öznesi olmadı.

## S-75 — Eşik türetmesinin eseri ilan edilmemiş bir argümanla üretilmişti

> **İddiayı sınırlıyor.** `results/pass-threshold.json` — "eşik ön kayıttan türetildi"

> **Kapanma sınıfı.** Kalıcı kayıt — bir eserin hangi komutla üretildiği geriye dönük ilan edilemez

28 Ağustos'ta işlenen `results/pass-threshold.json` `replicates: 9` taşıyor.
`scripts/setup/derive_pass_threshold.py`'nin varsayılanı 8'di, ve belgelenen komut
— argümansız çağrı — o eseri üretmiyordu. Hiçbir yerde "9 ile koşuldu" yazmıyordu.

**Ölçüldü.** Aynı liste ve aynı kayıtla (28 Ağustos'un birleşik seri 3'ü)
varsayılan 8 ile koşunca eserden 236 yaprak farklı çıktı; `--replicates 9` ile
sıfır. Betik belirlenimci: aynı argümanla iki koşu birebir aynı.

**Ne gizliydi, ne değildi.** Sayı gizli değildi: eser kendi tekrar sayısını
taşıyordu. Gizli olan onu üreten komuttu, ve bir eseri yeniden üretememek onu
denetleyememek demek. `K-146`, `S-68` ve `K-148` bu esere dayanıyor.

**Eşiğin kendisi etkilenmiyor.** 8 ile de 9 ile de türetilen eşik aynı: beklenen
etki 0,2'de 0,85, 0,3 ve 0,5'te 0,75. Farklı olan, ayrım başına okunabilir oranların
bir kısmı.

**Bundan sonrası.** Varsayılan 9 (`K-167`); argümansız komut bugün işlenen eseri
üretiyor.

## S-74 — Seri 3, 26 Ağustos'tan beri iki dosyada; 13–25 Eylül arasında yarısı depodaki kayıtta yoktu

> **İddiayı sınırlıyor.** `K-139` — "bir ölçüm serisi iki makinede koşabilir, ama iki dosyada kalamaz"

> **Kapanma sınıfı.** Sonraki tur — Drive'daki kopyanın birleşik dosyayla değiştirilmesi, ve bölünmeyi soran bir denetim

`K-139` seri 3'ü 26 Ağustos'ta birleştirdi ve kuralı yazdı. Kural bir
**prosedürdü**: birleştirmeyi elle koşulan `scripts/merge_series.py` yapıyor,
ve iki dosyanın aynı seriyi taşıyıp taşımadığını soran hiçbir şey yok. Bölünme
iki aşamada geri geldi.

| Tarih | Ne oldu | Kaynak |
|---|---|---|
| 26 Ağustos, 14:58 | Seri yerelde birleşti: 182 epizot. Drive'daki kopya Colab yarısında kaldı: 62 epizot (`b14`, `b32c`) | commit `1023098`; dosya tarihleri |
| 2 Eylül, 17:58 UTC | İlk `bir1` epizodu **Drive'daki kopyaya** yazıldı. İki dosya o andan itibaren birbirinde olmayan satırlar taşıyor | `run_manifests.wall_clock_utc` |
| 3 Eylül | `S-72` yerel dosyanın altı önekini saydı; bir saat sonra §18.1'in eki Colab dosyasını ölçtü ve üç önek saydı (`b14`, `b32c`, `bir1`). İki tarif aynı depoda yan yana durdu | commit `92396ea`, `fc83a92` |
| 13 Eylül, 20:59 | `results/zihin-3.sqlite` Colab kaydıyla (269 epizot) **üzerine yazıldı**. Yerel yarı — `b3l`, `b7l`, `b15l`, `b32`, 120 epizot — depodaki kayıttan çıktı; yalnız ev dizinindeki yedeklerde kaldı | dosya tarihleri; `sha256` eşleşmesi |
| 25 Eylül | Yerel yarı geri kondu: 389 epizot | `results/series-3-merge.json` |

**Neden fark edilmedi.** Dört sebep, dördü de ölçülmüş.

1. `ACTIVE_SERIES` bir **yol**, bir kimlik değil. O yoldaki dosya bütünüyle
   değiştirildiğinde her okuyucu hâlâ "seri 3'ü okuyor".
2. Kayıt git'te değil (`*.sqlite` yok sayılıyor). Üzerine yazma bir diff, bir
   commit ya da bir inceleme üretmedi.
3. Dört tarama eseri (`results/b3l-taramasi.json`, `results/b7l-taramasi.json`,
   `results/b15l-taramasi.json`, `results/b32-taramasi.json`) `database` alanında
   `results/zihin-3.sqlite` diyor. 13 Eylül'den bu yana o dosyada o öneklerden tek
   satır yoktu ve bu iddiayı okuyan bir denetim yoktu.
4. Aynı serinin iki çelişen tarifi depoya aynı gün, bir saat arayla girdi, ve düzyazıyı
   kayıtla karşılaştıran bir şey yok. `S-72`'nin "Colab'da bu yirmi `bir1`'in
   altmışıyla aynı korpusta madenleniyor" cümlesi de bu yüzden yanlıştı: Colab
   dosyasında `b32`'nin altı geçeni yoktu.

**Yarım kayıtla ne üretildi.** Colab'da, 2–10 Eylül arasında, biriktirmenin her
blok madenciliği ve ön kontrolü — teslim edilen `v0-gap2-sup3-0c3f4ac` ve
`v0-sup1-0c3f4ac` dahil. Yerelde, 13 Eylül'den sonra,
`results/accumulation-closure.json`. **Ölçülen etkileri sıfır:** korpus kuralı
(`K-159`: ilan edilen model **ve** `train`) birleşmeden önce 207 epizot seçiyordu,
sonra da 207. Kayıp yarının hiçbir epizodu o kurala girmiyor — dört önekin
dördü de `test_normal`'da ve dördünün de model etiketi başka. Listeyi okuyan
dört betiğin ve ardılının beş çıktısı (`results/task-types.json` ve ardılları)
28 Ağustos'ta tam dosyadan üretilmişti; o dosyayla yeniden koşunca beşi de
yaprak yaprak aynı çıktı.

**Birleşme nasıl sınandı.** `scripts/merge_series.py`: sayılar, yabancı anahtar
denetimi, koşu başına epizot. Yerel yarıyı zaten taşıyan bir dosyaya
birleştirmeye kalkınca 120 çakışmayla **reddetti**. `scripts/verify_series_merge.py`:
iki yarının her koşusu birleşik dosyada **içerikçe** aynı, dört tarama eserinin
öneki yerinde, korpus kuralı kıpırdamadı; birleşmemiş dosyaya karşı koşunca altı
problemle reddetti. `scripts/verify_carried_record.py`: `b3l`, `b7l`, `b15l`,
`b32c` ve `bir1`'in künyeleri ilan edilen şartlarla tutuyor. `b14`'ün üç
farkı yeni değil: `S-58`'in üçüncü örneği.

**Açık kalan.** Drive'daki kopya hâlâ 269 epizotluk yarım dosya. Bir sonraki
Colab koşusu ona yazarsa bölünme üçüncü kez başlar; o dosyanın birleşik dosyayla
değiştirilmesi Colab'a erişen tarafın işi. Ve bölünmeyi soran sürekli bir denetim
yok: `scripts/verify_series_merge.py` bir kez koştu.

**Ek — 25 Eylül 2026.** Açık kalan iki işin biri kapandı: bölünmeyi soran sürekli
denetim artık var (`K-172`) ve yerel denetimlerin parçası. Öbürü — Drive'daki
kopyanın değiştirilmesi — Colab tarafında.

## S-73 — A dalının ilk 188 epizot için hiçbir gözlemi yok

> **İddiayı sınırlıyor.** §18.3 dal A — "iki ardışık blok sıfır yeni beceri eklerse koşu duruyor"

> **Kapanma sınıfı.** Kalıcı kayıt — geçmemiş bir gözlem geriye dönük kurulamaz

Defter oturumla siliniyordu (`K-162`), yani her blok sınırında koşucu boş bir
defter okudu ve bulduğu her beceriyi **yeni** saydı. Yedi madencilik olayının
yedisinde de `new_skills` sıfırdan büyük çıktı; "iki ardışık sessiz blok"
ölçütü bir kez bile değerlendirilmedi.

**Geriye dönük kurulamaz, ve sebebi ölçüldü.** Kütüphane kimliği
`v0-gap{gap}-sup{support}-{commit}` biçiminde ve bir oturumdaki bütün
madencilikler aynı commit'te koştu, yani hepsi **aynı kimliği** aldı;
`replace_library` her seferinde öncekini sildi. Commit değişince yeni bir kimlik
doğuyor, o yüzden kayıtta oturum başına bir anlık görüntü kalıyor — taze kopyada
iki tane, yedi madencilik için (`K-163`).
Hangi blokta hangi becerilerin bulunduğu hiçbir yerde durmuyor, dolayısıyla
"blok 3 ile blok 4 arasında yeni beceri eklendi mi" sorusu bugün cevaplanamaz.

**Neyi bağlamıyor.** Epizotları, geçenleri ve son kütüphaneyi değil: bunlar
kayıtta ve korpus süzgeci (`K-159`) blok boyunca yürürlükteydi, yani her
madencilik doğru korpustan koştu. Bağlanan şey **verim** dalının bu koşunun ilk
188 epizodu hakkındaki hükmü. B dalı (tavan) etkilenmedi; o sayı kayıttan
geliyor (`K-160`).

**Bundan sonrası bağlı değil.** `run_ledger` kayda girdi; sonraki her blok sınırı
kalıcı bir satır bırakıyor ve A dalı oturumlar arasında değerlendirilebiliyor.
Koşu buradan devam ederse A dalının gözlemleri **188'inci epizottan itibaren**
birikir; öncesi için raporda "değerlendirilmedi" yazar, "ateşlemedi" değil.

**Ek — 25 Eylül 2026.** Yukarıdaki "`run_ledger` kayda girdi" cümlesi o gün doğru
değildi: tablo koda girmişti, gerçek kayda değil. 25 Eylül'e kadar kayıtta yoktu,
yani bir sonraki koşu da A dalını değerlendiremezdi. Tablo o gün kuruldu ve ön
koşul denetimi artık onu soruyor (`K-171`).

## S-72 — Madenci koşunun epizotlarını değil dosyanın tamamını okuyor

> **İddiayı sınırlıyor.** §18.1 — "korpus değerlendirilecek modelin kendi epizotlarından"

> **Kapanma sınıfı.** Sonraki tur — koşucunun üreticiye bir süzgeç geçirmesi, ve süzgecin ölçütünün kararı

`passing_sequences` veritabanındaki **her** geçen epizodu okuyor; önek, koşul
ya da model süzgeci yok. Hata indeksinin `observed_episodes`'u da öyle, üstelik
geçme şartı bile aramadan. Biriktirme koşusu `results/zihin-3.sqlite`'e yazıyor
ve o dosya `bir1`'den önce altı önekten 182 epizot taşıyor: `b14` (14B), `b15l`,
`b3l`, `b7l`, `b32` (OpenRouter, kuantalaması bilinmeyen, `S-58`), `b32c`.

**Ölçüldü.** Bu dosyanın buradaki kopyasında madencinin gördüğü küme 20 geçen
epizot, 13 görev, 540 çağrı: `b14` 3, `b32` 6, `b32c` 11 (`K-158`). Colab'da bu
yirmi `bir1`'in altmışıyla **aynı korpusta** madenleniyor.

**Neyi bozar.** İlan "modelin kendi epizotları" diyor. `b32c` aynı model
etiketi; `b14` ve `b32` değil. Kütüphaneye girebilen her örüntü bu üç kaynaktan
destek toplayabiliyor, yani "32B'nin kendi epizotlarından madenlendi" cümlesi
bugünkü dosyada doğru değil. Eşiklerin kalibre edildiği korpus da (`zihin-2`,
`sinir3`) bu dosyada yok, yani kalibrasyon ile üretim aynı seçim kuralıyla
yapılmıyor.

**Neden burada kapatılmadı.** Süzgecin ölçütü bir karar: **önek** (`bir1`,
yalnız bu koşu) mı, **model etiketi** (32B q4_K_M, `b32c`'nin 11 geçeni de
girer) mi. İlan "model" diyor, "koşu" demiyor; ikisi farklı korpus ve farklı
kütüphane verir. Bu kullanıcının kararı ve tarihli bir ek ister; koşu ortasında
madencinin seçim kuralını değiştirmek ölçümü değiştirir.

**Neyi bağlamıyor.** Kaydın kendisini değil: her epizot kendi önekiyle ve
`model_ref` ile duruyor, süzgeç sonradan uygulanabilir ve kütüphane türetilmiş
bir projeksiyon olarak yeniden üretilebilir (`03-architecture.tr.md`).

## S-71 — Devam eden bir epizodun künyesi ilk denemenin makinesini anlatıyor

> **İddiayı sınırlıyor.** `run_manifests.boot_id` ve `created_at` — "künye, altındaki epizodun koştuğu makineyi ve anı anlatıyor"

> **Kapanma sınıfı.** Sonraki tur — denemeyi ayrı bir satırda kaydetmek

Künye yazımı devam-farkında oldu (`K-155`): aynı `run_id` ikinci kez geldiğinde
koşullar karşılaştırılıyor ve aynıysa **yazılmıyor**. Yani ayakta kalan künye,
o id'yi **ilk isteyen** denemenin künyesi.

**Koşullar için bu doğru, iki alan için değil.** `MANIFEST_CONDITION_FIELDS`'in
hepsi karşılaştırılıyor, `code_commit` farkı ölçüm tanımlayan bir yol değiştiyse
redde yükseliyor. Karşılaştırılmayan ikisi denemeye özgü: `boot_id` ve
`created_at`. Colab timeout'undan sonra yeni oturum yeni bir makine, yani
epizot B önyüklemesinde koşarken künyesi A'yı söylüyor.

**Neyi bozar.** `boot_id` koşu ortasında makinenin yeniden başladığını yakalamak
için var. Devam etmiş bir epizot için o soruya **yanlış** cevap verir: künye ile
epizot farklı önyüklemelere ait ama künye bunu söylemez. `created_at` da
`uptime:` göreli, yani ilk denemenin saatine göre.

**Neden üzerine yazılmadı.** Üzerine yazmak, kısmen yazılmış bir epizodun (künye
ve epizot var, hüküm yok) altındaki satırı değiştirmek demek; o epizot ilk
denemeye ait. Bir satırı doğru yapmak için başka bir satırı yanlış yapmak.

**Kapanışı.** Denemeyi kendi satırında kaydetmek: `run_id` başına bir künye değil,
deneme başına bir satır ve epizodun hangisine ait olduğunu söyleyen bir bağ. Bu
şema değişikliği ve koşudan önce yapılmıyor.

**Neyi bağlamıyor.** Koşulların tutarlılığını değil: iki deneme farklı koşullarda
olsaydı ikincisi reddedilirdi ve bu `tests/test_resumption.py` içinde dokuz alan
için ayrı ayrı kanıtlanıyor.

## S-70 — Defter denetiminin iki kuralı düzyazıyı örüntüyle okuyor

> **İddiayı sınırlıyor.** `scripts/check_colab_notebook.py` — "denetim geçtiyse defterin düzyazısı ilan edilene uyuyor"

> **Kapanma sınıfı.** Sonraki tur — kuralları ilan edilen alanlara bağlamak

Denetimin yedi kuralından beşi yapısal: bir yol var mı, bir değişkeni kim
okuyor, bir yol sabit mi yazılmış, koşu komutu nöbetçinin satırında mı. Bunlar
düzyazıdan bağımsız. İkisi değil, ve ikisinin sınırı ayrı yazılmalı.

**Bir. Koşudan bağımsız atıfların listesi mutlak bölüm numaralarıyla tutuluyor.**
`15.3` ve `15.7` gerekçeleriyle listede: biri "ölçülmemiş çalışma zamanında
epizot başlamaz", öteki "sonuçlar yapıştırılmaz, itilir" kuralı, ve ikisi de
`bir1`'in bölümüne ait değil çünkü o kurallar hiçbir koşuya ait değil. Protokol
yeniden numaralandırılırsa liste sessizce başka bölümleri serbest bırakır.
Kapanışı: kuralların kendilerinin koşudan bağımsız bir bölüme taşınması, ki o
zaman liste de gerekmez.

**İki. Kadans ile toplam kelimeyle ayrılıyor.** "Her otuz epizotta bir" bir oran,
"Otuz epizot başlamadan" bir iddia, ve sayı ikisini ayırmıyor — otuz hem bloğun
boyutu hem `b14`'ün tüm koşusu. Denetim sayının **önündeki kelimeye** bakıyor:
`every`, `each`, `per`, `her`, `beher`. Listede olmayan bir kuruluş — "otuzluk
bloklar hâlinde" — toplam sanılır ve yanlış ateşler; ya da bir toplam kadans
kelimesiyle yazılırsa kaçar. Ölçülmüş hâli: kural ilk biçiminde bir sayının
**eskiden ne olduğunu** kaydeden yorumu ve bir SQL dizgesindeki `episodes`
kelimesini işaretledi, ve iki kez daraltıldı.

**Neyi bağlamıyor.** Denetimin bulduğu on iki arızanın hiçbiri bu iki kurala
bağlı değildi tek başına: on ikisi de `tests/test_colab_notebook.py` içinde geri
konuyor ve yakalanıyor. Bağlanan şey **gelecekteki** bir arızanın aynı örüntüye
düşeceği varsayımı.

**Ve bu `S-69` değil.** O, koşan kopyanın bu dosya olup olmadığını kapsıyor. Bu,
dosyanın kendisi doğru olduğunda denetimin onu ne kadar okuyabildiğini.

## S-69 — Denetimlerin öznesi depo; kullanıcının elindeki kopyalar dışarıda

> **İddiayı sınırlıyor.** Bu depodaki her denetim — "denetim geçtiyse koşan eser doğrudur"

> **Kapanma sınıfı.** Kalıcı kayıt — deponun içinden bir denetim, deponun dışındaki bir kopyanın öznesi olamaz

Bir denetim okuduğu ağaç hakkında konuşuyor. `tests/test_colab_ref.py` deponun
`experiments/colab/zihin-colab.ipynb` dosyasını doğruluyor ve doğru doğruluyor —
ama koşan eser o dosya değilse, denetim doğru soruyu **yanlış özne** üzerinde
sormuş oluyor.

**Ölçülmüş hâli.** Depodaki defter `main`'i çekecek şekilde düzeltildi ve test
bunu çiviledi. Kullanıcı Drive'a kaydedilmiş kendi kopyasını koşturuyordu; o
kopya hâlâ birleşmiş bir dalı çekiyor ve düzeltme ona ulaşmadı. Test yeşildi,
koşan eser bayattı.

**Bu sınıf bu turda üçüncü kez göründü.** K-138'de bir denetim doğru koşup yanlış
model hakkında cevap verdi; K-142'de doğru soru yanlış kümede soruldu; burada
doğru dosya doğrulandı ama koşan dosya başkasıydı. Üçünün ortak yanı denetimin
**öznesini kendi seçmemesi**.

**Neden defterin içine konan bir mekanizma kapatmıyor.** Kendini denetleyen bir
defter, denetimi de içinde taşır — yani kaydedilmiş **bayat** bir kopya
**bayat bir denetim** taşır. Bir denetim, kendisinden önceki bir sürümünü
yakalayamaz. Bugün eklenecek bir öz-denetim yarından sonraki kopyalara yarar,
bugün elde olana yaramaz.

**Bayatlık denetimi bir tur geç.** `scripts/setup/check_prerequisites.py` çalışma
kopyasının geriliğini söylüyor (`K-151`), ama klonlamadan **sonra** koşuyor.
Klonlamayı yapan eser zaten bayatsa, o eserin yanlış dalı çekmesi denetimden
önce olup bitiyor.

**Sınırın sınırı: bu yalnız defter için değil.** Kullanıcının elindeki her kopya
aynı durumda — Drive'daki veritabanı, indirilmiş bir tarama JSON'u, bir hafta
önce çekilmiş bir klon, elle taşınmış bir kayıt. K-139 elle taşınan bir kaydı
doğrulamayı kural yapmıştı; bu kayıt o kuralın neden gerektiğini genelleştiriyor.

**Neyi bağlamıyor.** Deponun kendi içinde tutarlı olduğu iddiası ayakta: 90 atıf
çözülüyor, 1059 çapa eşleşiyor, tarih denetimi 26/26. Bağlanan şey o tutarlılığın
**dışarıdaki bir kopyaya taşındığı** iddiası.

**Azaltma, kapatma değil.** Kural yazıldı: defter her oturumda depodan açılıyor
(`experiments/colab/README.md` ve `REPRODUCE.md`). Bir kural bir denetim değil;
uyulduğunu gösteren şey yok.

## S-68 — Türetilen geçiş oranı eşiği ölçülenin iki buçuk katı: deney bu hâliyle güçsüz

> **İddiayı sınırlıyor.** A.1 — birinci araştırma sorusunun onaylayıcı olarak cevaplanabileceği

> **Kapanma sınıfı.** Sonraki tur — daha yüksek geçiş oranı, daha büyük örneklem ya da daha az ayrım isteyen bir tasarımla kapanır

Ön kayıttan türetilen eşik (K-146) beklenen etki büyüklüğüne göre **0,75 ile
0,85** arasında. Birincil tabakada ölçülen geçiş oranı **0,280**. Aradaki fark
iki buçuk kattan büyük.

**Ne demek.** Ön kaydın ilan ettiği ayrımların hepsi aynı anda okunur olsun
isteniyorsa, bu model ve bu örneklemle o okunurluk elde edilemiyor. Sonuçlar
yine üretilebilir, ama ilanların bir kısmı hüküm veremeyecek durumda çıkacak.

**Yön belli.** Eşik `S-66` yüzünden iyimser tarafta: gürültü olduğundan büyükse
eşik yükselir, düşmez.

**Bunu kapatabilecek üç yol var ve üçü de tasarım kararı, ölçüm değil.** Daha
yüksek geçiş oranı veren bir model; örneklemi büyütmek (tabaka 105 görev, ve
ezberleme kapısı onun yarısını okuyor); ya da hangi ayrımların onaylayıcı
sayılacağını daraltmak. Bu kayıt hangisinin seçileceğini söylemiyor.

**İkisi fiyatlandırıldı, 28 Ağustos 2026 (K-147).** Birincisi **kapalı**: bu
projenin ölçtüğü en yüksek nokta olan DeepSeek V4 Flash eylem tabakasında
15/25 = **0,600** veriyor, eşiğin altında; gpt-4o 10/25 = 0,400. İkincisi
**500 eylem görevi** istiyor — bugünkü 105'in üstüne `test_challenge`'ın
neredeyse tamamı — ve o da ayrılmış küme tanımını değiştirmek demek.

**Ek — 25 Eylül 2026.** "500 eylem görevi" yedi tekrarın medyanı; tekrar başına
aralık 400–557 ve bazı tekrarlarda ulaşılamaz (`K-168`). Tabaka artık 104.

## S-67 — Ezberleme kapısı, tasarımın taşıyamadığı bir ayrım

> **İddiayı sınırlıyor.** Y-2 — kazancın ezberlemeden gelmediği iddiası

> **Kapanma sınıfı.** Sonraki tur — alt küme büyütülürse ya da kapı betimleyici bir istatistiğe indirilirse kapanır

Y-2 "görülmemiş kazanç, görülmüşün **yarısının** altındaysa ezberleme
doğrulanmıştır" diyor. Yarısını hiçbirinden ayırmak için aralığın etkinin
yarısından dar olması gerekiyor, ve kapı örneklemin **yarısını** okuduğu için o
aralık birincil aralığın 1,42 katı. Şart birincil genişlik üzerinde **0,35**'e
düşüyor — taranan altı şartın en sıkısı.

**Ölçüm sonucu.** Beklenen etki %10 ise bu şart taranan en yüksek orana (0,85)
kadar hiçbir oranda sağlanmıyor. %20'de 0,85, %30 ve %50'de 0,75 gerekiyor.

**Bu bir kusur değil, bir bulgu.** Kapı ölçümden önce yazıldı ve doğru yazıldı;
taşıyamayan şey kapı değil, kapının okuduğu alt kümenin boyutu. Eylem tabakası
105 görev, kapının yarısı ~52 görev.

**Neyi bağlamıyor.** Kapının **yönü** hâlâ raporlanabilir: görülmüş ve
görülmemiş kazançlar ayrı ayrı yazılabilir. Yapılamayan şey oranın yarımın
altında olup olmadığına **hüküm vermek**.

## S-66 — Aralık genişliği taramasının gürültü modeli iki hücreden geliyor

> **İddiayı sınırlıyor.** `results/interval-width.json` — geçiş oranına göre raporlanan güven aralığı genişlikleri

> **Kapanma sınıfı.** Sonraki tur — tekrarlı geçen epizot biriktiğinde yeniden ölçülürse kapanır

Tarama epizot başına çarpımsal bir gürültü kullanıyor ve katsayısı kayıttan
ölçüldü: **iki** tekrarlı geçen hücre. Aynı hücrede iki epizot demek, dağılımın
şeklini değil yalnız bir dağılım noktasını görmek demek.

**Yönü belli.** Gerçek epizot içi değişkenlik ölçülenden büyükse aralıklar
raporlanandan **geniş** olur. Yani tablodaki her genişlik bir **alt sınır**, ve
"şu oran yetiyor" diye okunan her satır iyimser tarafta.

**Neyi etkilemiyor.** Tablonun **şekli** gürültüden değil sansürden geliyor:
geçen bir epizot on iki çağrı, sansürlü bir epizot yirmi ila yüz elli.
İkisi arasındaki fark gürültüden bir mertebe büyük, yani grid B'nin grid A'dan
çok daha geniş çıkması bu sınırlamadan etkilenmiyor.

**Kapanışı ucuz.** Biriktirme koşusu aynı göreve birden çok tohum koşturduğunda
katsayı gerçek dağılımdan yeniden ölçülebilir ve tarama tekrarlanabilir.

**Ek — 25 Eylül 2026.** Tarama eylem tabakasında yeniden koşuldu
(`results/interval-width-action.json`, `K-174`); aynı gürültü modelini kullanıyor,
yani bu sınırlama yeni tabloyu da bağlıyor. Yukarıdaki "grid B'nin grid A'dan çok
daha geniş çıkması" eylem tabakasında da tutuyor: medyanda 8,2 kat.

## S-65 — Hata indeksi korpusun gerisinde kaldı: kayıttaki on beş kart, bugünün korpusu yirmi veriyor

> **İddiayı sınırlıyor.** Getiricinin kapsama ve ayırt edicilik sayıları — hepsi kayıtlı indeksten okundu

> **Kapanma sınıfı.** Sonraki tur — indeks yeniden madenlenirse kapanır, ama bu bir deney tasarımı kararı

Kayıtlı indeks `v0-sup1-4bb340a` on beş kart taşıyor. Aynı madenci aynı
`min_support` ile bugünün korpusuna koşturulduğunda **yirmi** kart çıkarıyor.
Fark korpusun büyümesinden: üç kollu koşunun `uckol` önekli kırk beş epizodu
indeks kurulduktan sonra `results/zihin-2.sqlite`'a girdi ve hiç madenlenmedi.

**Beceri tarafında aynı boşluk yok ama oran sert.** Geçen epizotlar değişmedi;
madenci bugün de yüz beş örüntü buluyor ve kütüphane dört beceri taşıyor. Yüz
beşten dörde inen şey birleştirme ve süzme zinciri, ve bu oran hiç
raporlanmamıştı.

**Neyi sınırlıyor.** Getiricinin kapsama ve ayırt edicilik ölçümlerinin hepsi
kayıtlı indeksten okundu, yani mevcut korpusun **eksik** bir madenlemesinden.
Yönü belli: daha çok kart, daha çok kapsama; yani bugünkü kapsama sayıları
**alt sınır**.

**Yeniden madenlemek bir ölçüm değil, bir karar.** İndeksi tazelemek getiricinin
girdisini değiştirir, ve bunun ne zaman yapılacağı deney tasarımına ait. Bu
kayıt yalnız boşluğu ölçüyor; kapatmıyor. Eğri
`results/accumulation.json` içinde, madenci
`scripts/setup/build_failure_index.py`.

## S-64 — Birleşmemiş iş hiçbir denetimin öznesi değil

> **İddiayı sınırlıyor.** `scripts/check_merged_artefacts.py` — "raporlarda adı geçen her eser depoda duruyor"

> **Kapanma sınıfı.** Sonraki tur — birleşmemiş işi ölçen bir denetim yazılırsa kapanır

`scripts/check_merged_artefacts.py` `gh pr list --state merged --limit 6`
çağırıyor ve o PR'ların gövdesinde adı geçen dosyaların `origin/main` ağacında
olup olmadığına bakıyor. Yakaladığı risk dar ve bilinçli: bir dalın son commit'i
itilmez, önceki itmeler CI'ı yeşil tutar, PR birleşir, ve rapor "girdi" derken o
commit'teki her şey yoktur (`K-116`).

**Kör noktası tanımının içinde.** Öznesi *birleşmiş* PR'lar; hiç birleşmemiş iş
onun için yok. On dokuz Ağustos'tan yirmi altı Ağustos'a kadar otuz beş commit
tek bir dalda (`protokol-cevirisi`) durdu ve `main` yerinde kaldı. Denetim bu
süre boyunca hiçbir şey söylemedi, çünkü sorduğu soru "birleşenlerin eserleri
yerinde mi"; "birleşmemiş iş var mı" değil. `--limit 6` ikinci bir daralma: daha
eski bir PR'ın eseri hiç sorulmuyor.

**Bunu gösteren şey denetim değil, elle bakış oldu.** Aynı bakış ikinci bir şey
daha gösterdi: `origin/colab-sonuclari` dalı 14B noktasının iki eserini
(`results/b14-taramasi.json`, `results/colab-ortam.json`) taşıyor ve hiçbir dalın
atası değil. `scripts/analyze_passes.py` kullanım örneğinde birincisini anıyor,
ve dosya çalışma ağacında yok.

**Ek, 28 Ağustos 2026 — adlandırdığı komut artık soruluyor.** Bu kayıt "dal ile
`origin/main` arasında kaç commit var" sorusunun sorulmadığını yazmıştı ve soru
ısırdı: Colab defteri birleşmiş bir dalı çekmeye devam etti, o daldan sonra
eklenen dosyalar temiz kurulumda yoktu, ve arıza kendini `FileNotFoundError`
diye adlandırdı — yani "hiç yazılmadı" gibi okundu. Ön koşul denetimi artık
`origin`'i tazeleyip farkı sayıyor ve geride ise düşüyor (K-151). **Kaydın öbür
yarısı açık:** hiç birleşmemiş iş hâlâ hiçbir denetimin öznesi değil.

**Ölçülmeyen şey mekanik.** "Dal ile `origin/main` arasında kaç commit var" tek
bir komut, ve şu an hiçbir denetim onu sormuyor.

## S-63 — Ön koşul bulgusunun dayandığı üç koşudan ikisi tavan sınırlı, biri kayıtta yok

> **İddiayı sınırlıyor.** K-58 — ön koşul bulgusu, "ilan edilen eksende bant yok"

> **Kapanma sınıfı.** Kalıcı kayıt — koşular yapıldığı tavanla yapıldı; sonradan gevşetmek onları yeniden koşmak olur

K-60 bir sıfır yorumlanmadan önce bağlayıcı olabilecek parametrelerin bağlayıcı
olmadığının gösterilmesini istiyor, ve tavana çarpma oranı için eşik **%10**.
Ön koşul bulgusunun dayandığı üç koşu bu eşiğe karşı hiç ölçülmemişti. Ölçüldü:

| Koşu | Epizot | Tavana çarpma | Durum |
|---|---|---|---|
| `bant2` | 30 (JSON'da) | **kayıtta yok** | sonlanma sebebi hiç yazılmamış; epizotları hiçbir seride bulunamadı |
| `bant3` | 30 | **%0,0** | eşiğin altında; bu sıfır tavan sınırlı değil |
| `bant3-kapali` | 26 | **%96,2** | eşiğin çok üstünde |

**`bant3-kapali` için bu bir sürpriz değil, ama not gerekiyordu.** O koşuda durma
kuralı **tamamen kapalıydı**, yani epizodu durduran tek şey tavandı. Tasarım
gereği yüksek olması, sonucun tavan sınırlı olmadığı anlamına gelmiyor: tam
tersine, o sıfır bir **alt sınırdır** ve öyle raporlanmalıydı.

**`bant2` için cevap "sıfır" değil, "belirlenemedi".** JSON'unda otuz epizodun
otuzunda `termination` alanı boş, ve hiçbir seri veritabanında o önekli
epizot yok. Boş bir alanı %0 saymak, yokluğu olumsuzluğa çevirmek olurdu
(K-131). Bu koşu tavan açısından **hiçbir şey söylemiyor**.

**Ne değişiyor, ne değişmiyor.** Ön koşul bulgusunun kendisi ayakta: üç koşu da
sıfır verdi ve bir tavan sıfırı imal edemez, yalnız gizleyebilir. Değişen şey
bulgunun **gücü**: "ilan edilen eksende bant yok" cümlesi, üç bağımsız temiz
ölçüme değil, bir temiz ölçüme (`bant3`) ve bir alt sınıra (`bant3-kapali`) ve
bir belirsize (`bant2`) dayanıyor.

**Bu denetimin kendisi bir bulgu.** Kural (K-60) vardı, eşik (%10) vardı, ve üç
koşu ona karşı hiç ölçülmemişti. Bir kuralın yazılı olması onun uygulandığı
anlamına gelmiyor; uygulandığını gösteren şey ölçüm.

## S-62 — Bant etiketi zorluğu değil referans çözümün yolunu gösteriyor

> **İddiayı sınırlıyor.** Bant başına raporlanan her sonuç — bant taramasının `1-10`, `90+` etiketleri

> **Kapanma sınıfı.** Dış olgu — `num_api_calls` AppWorld'ün alanı ve onun tanımı bizim elimizde değil

Adım tavanı çapadan türüyor ve bant etiketi çapadan geliyor. Çapa
(`num_api_calls`) **referans çözümün** kaç API çağrısı yaptığını sayıyor, görevin
neyi gerektirdiğini değil.

**Ölçüldü.** 14B koşusunda `09b0ee6_1` çapa **102** taşıyor, yani `90+` bandında,
ve **altı adımda** geçildi. Görev metni altı sanatçı adı isteyen bir **cevap
görevi**; `ground_truth/evaluation.py` iki test taşıyor ve yalnız biri
`no_op_fail` — bir dize eşitliği. `09b0ee6_2` aynı şekilde: çapa 97, altı adım.

**Etkisi iki yönlü.** Bant başına oranlar "zor bantta da geçti" diye okunamaz;
ve tavan formülü bu görevlere gerçek ihtiyaçtan çok daha yüksek bir tavan
veriyor, yani tavana çarpma oranı bu görevlerde düşük görünüyor.

**Azaltma.** Bant başına sonuç raporlanırken etiketin ne ölçtüğü yanına
yazılıyor. Ayrıca `meaningful_total` zaten kayıtta: bir görevin kaç testinin
hiçbir şey yapmayan bir ajanı eleyeceği ölçülü, ve bir geçişin ağırlığı oradan
okunabiliyor.

## S-61 — Ölçek ekseninin noktaları üç farklı kartta ölçüldü

> **İddiayı sınırlıyor.** 02-research-question ikinci soru — etkinin model boyutuyla nasıl değiştiği

> **Kapanma sınıfı.** Kalıcı kayıt — ölçümler alındığı donanımda alındı; sonradan tek karta taşımak onları yeniden üretmek olur

1.5B, 3B ve 7B yerel **RTX 4070**'te (Ada, compute 8.9), 14B Colab **L4**'ünde
(Ada, 8.9), 32B Colab **A100**'ünde (**Ampere, 8.0**) ölçülüyor. Ampere farklı
bir nesil, ve flash attention ile `q8_0` KV önbelleği desteği aynı olmayabilir.

**Neden bir sınırlama.** Eksen boyut ekseni olmalı. Kart değişince ikinci bir
değişken giriyor: aynı istek farklı bir kartta farklı bir çekirdeğe düşebilir,
ve KV önbelleği desteklenmiyorsa sessizce `f16`'ya çıkar — iki katı bellek, başka
bir hesap.

**Azaltma, ve neden yeterli değil.** `runtime_facts` sunucunun kendi günlüğünden
**istenen** ile **etkin** değeri ayrı okuyor: kaç katman GPU'da, flash attention
etkin mi, KV'nin gerçek tipi ne. `comparability` hükmü koşudan önce basılıyor ve
`COMPARABLE` değilse sonuç "yerelle karşılaştırılamaz" diye etiketleniyor. L4'te
okundu ve tuttu (49/49, enabled, q8_0). Ama bu hüküm **ölçülen üç şeyi**
karşılaştırıyor; kartlar arasında ölçmediğimiz her fark açık kalıyor.

## S-58 — 32B ölçümü ilan edilen iki koşulda sapmış koştu

> **İddiayı sınırlıyor.** docs/reports/b32-olcumu.md — 32B sonucunun sınır kontrolüyle karşılaştırılabilirliği

> **Kapanma sınıfı.** Sonraki tur — ölçüm doğru koşulda yeniden koşulursa kapanır

Protokol §14.2 "durma kuralı, eşik ve kalkan kipi sınır kontrolüyle aynı"
diyordu. Künyeler karşılaştırıldı: `no_progress_limit` `sinir3`'te 15, `b32`'de
**40**; `shield_mode` `sinir3`'te `off`, `b32`'de **shadow**.

**Sebep koşucuda değil şartın yazımında.** Koşucu `config/recording.yaml`'daki
güncel değeri okudu ve yapılandırma sınır kontrolünden bu yana 15'ten 40'a
değişmiş. Şart **göreli** yazılmıştı ("sınır kontrolüyle aynı") ve gönderme
yaptığı şey altından kaydı.

**Etkinin yönü ölçülebilir ve bulguyu yıkmıyor.** Gevşek eşik epizotları daha
uzun koşturuyor, yani geçişi kolaylaştırır; altı geçiş sıkı bir kuralın
artefaktı değil. Yıkılan şey `sinir3`'ün 20/30'uyla **doğrudan karşılaştırma**.

**Neyin sapmadığı.** Model etiketi, çıktı bütçesi (4000), sıcaklık, taban tohum,
görev kümesi ve bölme aynı; görev kümesinin `sinir3`'ünkiyle birebir aynı olduğu
ayrıca doğrulandı.

**Üçüncü örnek, 25 Ağustos 2026, ve mekanizması farklı.** *(Tarih düzeltmesi,
26 Ağustos 2026: bu paragraf önce 20 Ağustos 2026 diye tarihlendi. 20 Ağustos
§15'in koşullarının ilan edildiği gün; bulgunun günü değil. Anlattığı koşu
`b14`, künyesindeki ilk epizot `2026-08-25 08:51` UTC, ve bulguyu yazan commit
`f01132e`, aynı günün `10:55`'i UTC.)* İlk iki örnekte koşul
**göreli** yazılmıştı ("sınır kontrolüyle aynı") ve altındaki değer kaymıştı.
Bu kez koşul **mutlak** yazıldı — protokol §15.2 `max_output_tokens: 400` ve
`no_progress_limit: 15` diyor — ve yine tutmadı. Sebep ölçüldü:

- `max_output_tokens`: protokol 400 diyor, `config/recording.yaml` 4000 taşıyor
  ve koşucu oradan okuyor. 400 hiçbir zaman yapılandırmada olmadı; protokole
  `bant3` künyesinden kopyalandı, ve `bant3` o değeri yapılandırmada o anahtar
  **hiç yokken** almıştı (commit `fc9101a`).
- `no_progress_limit`: defter `--stop-threshold 15` geçiyordu, ama
  `measure_band.py` o bayrağı hiç tanımıyordu; `sys.argv` içinde yalnız
  `--allow-dirty-tree` arıyordu ve gerisini **sessizce düşürüyordu**. Koşucu
  yapılandırmanın 40'ını okudu.
- `shield_mode`: protokol `off` diyor, koşucu `shadow` kaydediyor.
  `ShieldMode`'un `off` üyesi **yok**; `off` yalnız kalkan mount edilmeden
  önceki koşuların künyelerinde var. Yani bu alan bir bayrakla düzeltilemez, bir
  ölçüm kararı bekliyor.

**Ders mutlaklık değil, tek kaynak.** Mutlak yazmak yetmiyor: yazılan yer ile
okunan yer aynı olmalı. Düzeltme K-136'da, ve artık bir denetim ikisini
karşılaştırıyor (`scripts/check_declared_conditions.py`).

## S-59 — 32B sonucu eksik kümeden ve bağlayıcı tavandan okundu

> **İddiayı sınırlıyor.** docs/reports/b32-olcumu.md — 32B'de ölçülen geçiş sayısı

> **Kapanma sınıfı.** Sonraki tur — daha yüksek maliyet tavanı ve daha yüksek adım tavanıyla yeniden koşulursa kapanır

İki ayrı eksiklik aynı sayıyı sınırlıyor.

**Küme eksik.** Otuz görevin 27'si yazıldı; maliyet tavanı (3,00 dolar) koşuyu
durdurdu ve iki epizot yazılamadı. §6 eksik bir epizot kümesinin
alıntılanmasını yasaklıyor.

**Tavan bağlayıcıydı.** Tavana çarpma oranı **%22,2** (6/27) ve K-60 bunu %10'un
altında istiyor. Bağlayıcı tavanın altındaki her sonuç bir alt sınır.

**Eksikliğin yönü asimetrik.** Koşulmamış epizotlar bir geçişi gizleyebilir,
gözlenmiş bir geçişi üretemez. Bu yüzden **varlık iddiası** ("bant var") ayakta,
**oran iddiası** ("şu kadarı geçti") ayakta değil. Raporda hiçbir oran
yazılmadı.

## S-60 — Tekrarlanabilirlik doğrulaması bir ana ait; dış bir servis onu geriye dönük geçersizleştirebiliyor

> **İddiayı sınırlıyor.** REPRODUCE.md — "temiz bir klondan baştan kurulabilir"

> **Kapanma sınıfı.** Kalıcı kayıt — zincirin dış halkaları bizim değil; yukarı akış düzelse bile doğrulamanın ana ait olması değişmiyor

REPRODUCE.md temiz bir klondan yürütüldü ve geçti. O yürütme, yukarı akıştaki
AppWorld deposunun Git LFS nesneleri **hâlâ sunulurken** yapıldı. 20 Ağustos
2026'da sunulmaz oldular: GitHub `This repository exceeded its LFS budget`
diyerek 403 döndürüyor. Aynı yanıt hem Colab çalışma zamanından hem geliştirme
makinesinden alındı, yani ağa değil yukarı akışa ait bir olgu.

**Doğrulanan şey bir zincirdi, ve zincirin halkaları bizim değil.** "Temiz
makinede kurulabilir" tek bir iddia gibi görünüyor ama en az dört dış servise
dayanıyor: GitHub'ın git erişimi, GitHub'ın LFS depolaması ve **bütçesi**, PyPI,
ve AppWorld'ün veri indirmesi. Bunlardan biri kapandığında iddia, biz hiçbir şey
değiştirmeden yanlışlanıyor. Yeşil bir doğrulama "bu kurulur" demiyor; "bu, o
gün, o servislerle kuruldu" diyor.

**Bloke olan yalnız taze kurulum.** Geliştirme makinesindeki kurulum
etkilenmedi: nesneler zaten çekilmişti ve `.venv` yerinde duruyor. Ölçümler,
raporlar ve kayıt veritabanı da etkilenmedi. Kırılan tek şey, elinde kurulum
olmayan birinin bugün baştan kurabilmesi — ki tekrarlanabilirlik iddiasının tam
olarak kendisi.

**S-01 bu sınıfı önceden yazmıştı, ama başka bir mekanizmayla.** Orada risk
"dal yeniden yazılır ya da commit erişilemez hâle gelir" diye anlatılıyor.
Gerçekleşen bu olmadı: commit erişilebilir, ağaç yerinde, yalnız LFS nesneleri
sunulmuyor. Sabitlenen şeyin erişilebilirliği ile **ona bağlı nesnelerin**
erişilebilirliği ayrı iki şey, ve ikincisi sabitlemeyle korunmuyor.

**Azaltma, ve azaltmanın sınırı.** `vendor/appworld/` altında sabitlenen
commit'ten üretilmiş bir yansı duruyor; önyükleme önce yukarı akışı deniyor ve
yalnız LFS reddederse yansıya düşüyor. Yansı kullanıldığında künye
`appworld: mirror a072b7a86 (2026-08-20)` taşıyor, yani ölçümün kaynağı gizli
kalmıyor. Bu tekrarlanabilirliği **kurtarmıyor**, taşıyor: yansıyı kullanan biri
artık bize güveniyor, yukarı akışa değil. Bundle'ların sha256'sı LFS nesne
kimliğine eşit olduğu için aynılık ölçülebiliyor; ama nesne kimliğinin doğru
kimlik olduğu, yukarı akış geri gelene kadar bizim kaydımıza dayanıyor.

## S-01 — AppWorld yayımlanmış bir sürüme değil, hareketli bir dala sabitli

> **İddiayı sınırlıyor.** REPRODUCE.md — “temiz makinede baştan kurulabilir”

> **Kapanma sınıfı.** Dış olgu — yukarı akış dalı bizim değil; kapanması AppWorld'ün sürüm yayımlamasına bağlı

`main` dalı `0.2.0.dev0` sürümünü taşıyor, yani yayımlanmamış bir geliştirme
dalı. Tekrarlanabilirlik tamamen commit sabitlemesine dayanıyor. Yukarı akış
dalı yeniden yazarsa ya da commit erişilemez hâle gelirse kurulum yeniden
üretilemez.

**Etki.** Orta. **Azaltma.** Commit hash'i künyeye yazılıyor. Uzun vadede
deponun bir kopyasını kendi tarafımızda tutmak gerekebilir.

**Gerçekleşti, 20 Ağustos 2026, ama burada yazılan mekanizmayla değil.** Dal
yeniden yazılmadı ve commit erişilemez olmadı; yukarı akışın Git LFS bütçesi
tükendi ve commit'in bağlı olduğu `.bundle` nesneleri sunulmaz oldu. "Uzun
vadede gerekebilir" denen kopya o gün gerekti ve alındı (`vendor/appworld/`).
Ayrıntı ve genelleşmiş hâli S-60'ta.

## S-02 — Referans çözümler yalnız train ve dev'de var

> **Kapsam.** referans çözümlerin hangi bölmelerde bulunduğunu kaydediyor; buna dayanan bir iddiamız yok

> **Kapanma sınıfı.** Dış olgu — referans çözümlerin hangi bölmede yayımlandığı yukarı akışın kararı

~~`appworld download data` varsayılan olarak `minimal` modda iniyor ve referans
çözümler elimize hiç geçmeyebilir.~~

**Aşama 2'de ölçüldü, kısmen çürüdü.** Varsayılan indirme 147 görevi `full`
kipte getiriyor: train'in 90'ı ve dev'in 57'si. `metadata.json` içindeki `mode`
alanı bunu açıkça söylüyor. O görevlerde `solution.py`, `compiled_solution.py`,
`api_calls.json`, `required_apps.json`, `required_apis.json` ve `generator.py`
hepsi var. Kalan 585 görev `minimal` kipte ve hiçbirini taşımıyor.

**Kalan etki.** Orta. Test bölmelerinde referans çözüm yok, dolayısıyla oradaki
görevlerin adım tavanı referans uzunluğa bağlanamaz. Ama görev başına API
çağrısı sayısı `metadata.num_api_calls` üzerinden 732 görevin hepsinde
okunabiliyor ve o alan 147 görevde `api_calls.json` ile birebir tutuyor.

## S-03 — Görev başına uygulama listesi test bölmelerinde yok

> **İddiayı sınırlıyor.** PILOT_REPORT.md kalkan bölümü — izinli uygulama kümesinin göreve özel olduğu

> **Kapanma sınıfı.** Dış olgu — `allowed_apps`ın şekli ve `required_apps.json`ın dağıtımı yukarı akışta

`world.task.allowed_apps` her görev için bütün uygulamaları döndürüyor, göreve
özel liste vermiyor. Göreve özel liste `ground_truth/required_apps.json` içinde
ve yalnız train ile dev'de var. Test bölmeleri için elde sayılar duruyor:
`metadata["num_apps"]` ve `metadata["num_apis"]`, ikisi de 732 görevin hepsinde.

**Aşama 2'de nasıl aşıldı.** Görev yönergesinden uygulama adı çıkaran bir vekil
yazıldı ve referans listesi olan 147 görevde sınandı. 147 görevin 111'inde küme
birebir tuttu, yüzde 75,5. Jaccard benzerliği 0,878.

**Kalan etki.** Orta. Test bölmelerindeki uygulama adları vekil ölçümden geliyor
ve her dört görevden birinde küme tam tutmuyor. Vekilin hata profili belli:
`simple_note`'u fazladan sayıyor, `phone` ve `venmo`'yu kaçırıyor. `amazon`,
`splitwise` ve `todoist` için hiç fazladan sayma yapmadı, yani zorluk
bölmesinde bu üçünü gördüğünde güvenilir.

**14 Ağustos eki: vekil kalkanın şartnamesi, ve isabeti kalkanın sınırı.**

Kalkanın izinli uygulama kümesi görev metninden türetiliyor; ground truth'tan
türetmek kalkana kıyaslama dışında sahip olmayacağı bir oracle vermek olurdu.
Yani vekil bir yaklaşım değil, tanımın kendisi — ve isabeti doğrudan kalkanın
isabeti.

Vekil depoya alındı (`src/zihin/allowed_apps.py`) ve
`MEASUREMENT_DEFINING_PATHS` listesine girdi. Daha önce kodu sürüm kontrolü
dışındaydı ve yalnız Aşama 2 raporunda duruyordu; ölçümü etkileyen bir bileşenin
sürüm kontrolü dışında olması kendi başına bir boşluktu.

Yeniden ölçüldü (`scripts/setup/measure_app_proxy.py`, 147 görev, train + dev):
tam eşleşme %75,5, ortalama Jaccard 0,857. Kaçaklar `phone` 30, `venmo` 6,
`file_system` 3; fazlalar `simple_note` 6. Eşleşmeyen 36 görevin hepsinde en az
bir kaçak var, yani kalkanın bugünkü **yanlış pozitif üst sınırı %24,5**.

**Kaçakların büyük kısmı gerçek bir sınır, vekilin kusuru değil.** Otuz `phone`
kaçağının hepsinde yönerge "roommates", "siblings", "coworkers" diyor; ilişki
`phone` uygulamasında duruyor ama metin uygulamayı hiç adlandırmıyor. Hiçbir
metin tabanlı vekil bunu kurtaramaz.

Bu, deneysel bir artefakt değil **gerçek bir dağıtım özelliği**: gerçek bir
kullanımda da elde yalnız kullanıcının cümlesi olur. Ayrıntı
`docs/reports/izinli-uygulama-vekili.md` içinde.

## S-04 — Doğrulayıcı hükmünün iki bileşeni ayrı ayrı çıkarılamayabilir

> **İddiayı sınırlıyor.** 05-experiment-design — epizot düzeyi “beklenmeyen yan etki” etiketi

> **Kapanma sınıfı.** Sonraki tur — `requirement` metinlerinden çıkarım denenmedi; denendiğinde kapanır ya da kesinleşir

AppWorld'ün `TestTracker` sınıfı `passes` ve `failures` listeleri veriyor.
Makaledeki iki ayrımı, yani beklenen değişikliklerin tamam olup olmadığını ve
beklenmeyen değişiklik bulunup bulunmadığını, iki ayrı boole olarak veriyor
olmayabilir.

**Etki.** Düşük. **Azaltma.** `verifier_results` tablosunda ilgili iki sütun
duruyor. Çıkarılamıyorsa `NULL` kalacak.

**Bakılan yer.** Değerlendirme JSON'u test başına `requirement` metni ve
`label` taşıyor. Sekiz değerlendirmede yalnız iki etiket geçti, `no_op_pass` ve
`no_op_fail`; ama o örneklemde ajan hiçbir şey yapmadığından etiket kümesi
temsilî değil. İki bileşen `requirement` metinlerinde ayrışıyor — "assert model
changes match ..." beklenen değişikliği, "assert no new ... was added"
beklenmeyeni sınıyor. Çıkarım denenecekse başlangıç noktası bu; şimdilik iki
sütun `NULL` yazılıyor (`src/zihin/verification.py`).

## S-05 — Eylem düzeyinde yanıt gövdesi yok, durum kodu da yok

> **İddiayı sınırlıyor.** 07-failure-taxonomy — eylem düzeyi hata sınıfları

> **Kapanma sınıfı.** Dış olgu — `api_calls.jsonl`ın üç alanı AppWorld'ün günlük biçimi; ölçüldü ve doğrulandı

**Aşama 3'te ölçüldü ve doğrulandı, hatta beklenenden dar çıktı.**
`logs/api_calls.jsonl` her kayıtta yalnız üç alan taşıyor: `method`, `url` ve
`data`. Yanıt gövdesi yok, durum kodu da yok.

**Etki.** Orta. `actions.result_status` ve `actions.error_class` sütunları bu
kaynaktan doldurulamıyor ve şu an `NULL` kalıyor. Adımın başarılı olup olmadığı
yalnız gözlem metninden okunabiliyor, tek tek çağrı düzeyinde değil.

**Azaltma.** Sütunlar duruyor. Doldurulmaları için kendi ölçüm katmanımızın
çağrıyı sarmalaması gerekir; şu an kapsamda değil.

## S-16 — Eylem düzeyi yanıt verisi enstrümantasyonu henüz yok

> **İddiayı sınırlıyor.** 07-failure-taxonomy — eylem düzeyi hata sınıfları (üç kapılı suç atfı da aynı yanıt verisine dayanıyor)

> **Kapanma sınıfı.** Sonraki tur — API istemcisi sarmalanıp yanıt ve durum kodu kaydedilecek; taşıma katmanı K-19'un dışında

`api_calls.jsonl` yanıt gövdesi de durum kodu da taşımıyor (S-05). Üç şey bu
veriye dayanıyor: eylem düzeyi hata taksonomisi, hata indeksi madenciliği ve
üç kapılı suç atfı.

**Etki.** Yüksek ve zamanlaması var. Biriktirme tek seferlik ve geriye dönük
eklenemiyor. Enstrümantasyon biriktirme başlamadan kurulmazsa, eksik fark
edildiğinde bütün korpusun yeniden koşulması gerekir.

**Tercih sırası.** Önce API istemcisi sarmalanıp yanıt ve durum kodu
kaydedilecek; bu taşıma katmanı, iskele kısıtının kapsamı dışında (K-19).
Olmazsa adım çıktısını ayrıştırmaya düşülecek, ama kırılganlığı ve hangi
durumlarda kaçırdığı ölçülecek. Üçüncü seçenek yok: eylem düzeyi durumsuz
devam edilirse hata indeksi mekanizmasının yarısı ölür.

**Kapandı.** `src/zihin/api_capture.py` `Requester._get`, `_post`, `_patch`,
`_delete` ve `_put` metotlarını sarmalıyor; yanıt gövdesi ve durum kodu
yakalanıyor, 401 dahil. Kaydedici artık eylemleri buradan yazıyor ve
`actions.result_status` ile `error_class` sütunları doluyor.

Kayıt noktası `raise_if_failure` çağrısından önce ve bunu
`tests/test_api_capture.py` içinde ayrı bir test sabitliyor. Sıra bozulursa tam
olarak ilgilendiğimiz vakalar kaçıyor ve ölçüm yeşil görünüyor: ilk sondada
yedi çağrının yedisi de 200 raporlandı, oysa ikisi başarısızdı.

İki kaynak birlikte tutuluyor. Yakalayıcının saydığı çağrı ile
`api_calls.jsonl` deltasının saydığı çağrı adım başına karşılaştırılıyor;
ayrışma kaydediliyor ve rapora giriyor.

## S-18 — Soğuk rejim 7B'de tekdüze değil

> **İddiayı sınırlıyor.** K-51 — artık varyansın model başına ölçüldüğü

> **Kapanma sınıfı.** Ölçüldü — on soğuk epizot koşuldu ve 7B tekdüze çıkmadı; cevabın kendisi kısıt

Model başına on soğuk epizot koşuldu. 1.5B ve 3B onda on aynı yörüngeyi verdi.
7B'nin dokuz koşusu bir yörünge, biri başka bir yörünge verdi; ayrışan koşu 12
adım yerine 6 adımda bitti. Boşaltma her epizotta doğrulandı, yani sebep rejim
karışması değil.

**Etki.** Yüksek. K-21 soğuk rejimi tekdüzeliği ölçülmüş tek seçenek olduğu
için seçmişti; 7B'de o gerekçe geçerli değil.

**Azaltma.** K-48 devreye giriyor: determinizm hedefinden vazgeçilip yükleme
durumu kaydedilen ortak değişkene indiriliyor. Kuralın model başına mı yoksa
üç nokta için birden mi uygulanacağı K-48'de yazmıyor ve karara bağlanması
gerekiyor.

## S-19 — 3B'nin sıfır çağrısı yetenek tabanı değil, sistematik bir hata

> **İddiayı sınırlıyor.** K-58 — ön koşul kapısının “model yetersiz” diye okunması

> **Kapanma sınıfı.** Sonraki tur — sistematik hatanın kaynağı düzeltilip 3B yeniden koşulursa taban okuması değişir

S-14 ölçek ekseninin en küçük noktası için açılmıştı. 3B ile koşulan on
epizodun onunda da sıfır API çağrısı çıktı ve hepsi yirmi adım tavanına
dayandı. İlk okumada bu ikinci bir taban etkisi gibi göründü.

**Sınıflandırma başka söylüyor.** On epizodun 200 adımının 200'ü de K-36'nın
dördüncü kategorisinde: kod üretildi, ayrıştırıldı, ama hiç eylem üretmeden
yürütme hatası verdi. Hepsi de aynı hata:

```
NameError: name 'playlists' is not defined
```

**Mekanizma prompt'ta.** Referans yönergenin örnek çözümü `playlists = []`
tanımlayıp sayfa sayfa dolduruyor. Modeller örneğin sonraki kısmını
(`for playlist in playlists:`) kopyalıyor ama tanımı taşımıyor. Aynı hata
Aşama 2'de 1.5B'nin "boş başarı" epizodunda da çıkmıştı.

**Etki ve yön.** Teşhis "model zayıf" değil, "model bu iskelede belirli bir
hatayı sistematik yapıyor". Yetenek tabanı olsaydı 3B'nin 1.5B'den kötü olması
beklenmezdi; oysa 1.5B aynı görevde 19 çağrı yapıyor.

**Bunun ikili bir sonucu var ve ikincisi bir geçerlilik riski.** Bir yandan
ölçülecek bant var, çünkü hata düzeltilebilir bir hata. Öte yandan mekanizma bu
hatayı düzeltirse ölçtüğümüz etki "biriken deneyimin katkısı" değil "tek bir
prompt kopyalama hatasının kapanması" olabilir. Etki büyük çıkarsa ayrıştırmak
gerekecek.

**Yapılmayacak olan.** Prompt düzeltilmiyor. Referans iskele değiştirilmeden
alınıyor (K-23, K-26) ve bu hata iskelenin kendi davranışı. Düzeltme mekanizmanın
işi olacak, bizim değil.

**Üç model, üç farklı arıza biçimi.** Aynı görevde adım kategorileri:

| Model | Eylem üreten adım | Baskın arıza | Çağrıların durumu |
|---|---|---|---|
| 1.5B | 190/200 | Yanlış parolayla giriş döngüsü | 19/19 çağrı 401 |
| 3B | 0/200 | `NameError`, tanımsız değişken | çağrı yok |
| 7B | 40/120 | Sessiz boş başarı (60/120) | 5/5 çağrı 200 |

Hiçbiri görevi çözmüyor ama sebepleri farklı, yani üçü aynı taban etkisi
başlığı altında toplanamaz. 1.5B'nin döngüsü K-20'nin öngördüğü davranış:
sabit sıcaklık ve seed altında ajan başarısız çağrıyı tekrarlıyor.

**Sınırı.** Tek görev. Deseni genelleştirmek için pilot gerekiyor.

## S-17 — Adım tavanı ile çapa farklı birimde

> **İddiayı sınırlıyor.** 05-experiment-design — tavana çarpma oranının %10 altında tutulduğu

> **Kapanma sınıfı.** Sonraki tur — dönüşüm katsayısı pilotta ölçülecek, varsayılmayacak (K-43)

Tavan model çağrısı biriminde, çapa (`metadata.num_api_calls`) API çağrısı
biriminde. Aradaki dönüşüm bilinmiyor.

**Etki.** Yüksek. Yanlış dönüşüm katsayısı bütün tavanları kaydırır ve sansür
oranını doğrudan etkiler. **Azaltma.** Dönüşüm pilotta ölçülecek, varsayılmayacak
(K-43). Aşama 3'te bir epizotta yirmi adıma on dokuz eylem düştü ama tek
görevden oran çıkarılmaz.

## S-15 — Yazma yapan GET uçlarının listesi alt sınır

> **İddiayı sınırlıyor.** 04-threat-model — kalkanın yazma kümesinin tam olduğu

> **Kapanma sınıfı.** Sonraki tur — liste çalışma zamanı ölçümüyle genişletilecek; alt sınır olmaktan çıkabilir

Kalkanın okuma/yazma yüklemi `method` alanına dayanacak. Statik tarama on beş
GET ucunun yazma çağrısı içerdiğini gösterdi (K-41). Ama tarama yalnız işleyici
gövdesindeki doğrudan çağrıları görüyor: GET dışı 302 ucun 211'inde yazma
bulundu, kalan 91'i işi yardımcı fonksiyona devrediyor.

**Etki.** Yüksek. Kaçırılan bir yazma ucu, kalkanın tam olarak durdurması
gereken vakadır. **Azaltma.** Liste Aşama 4 öncesinde çalışma zamanı ölçümüyle
genişletilecek: GET uçları çağrılıp veritabanı özeti değişiyor mu bakılacak.

## S-06 — Bir sunucu süreci aynı anda tek bir dünya tutuyor

> **Kapsam.** AppWorld motorunun süreç başına tek dünya tuttuğunu kaydediyor; işletme kısıtı

> **Kapanma sınıfı.** Dış olgu — süreç başına tek dünya AppWorld motorunun tasarımı

AppWorld motoru ayrı süreçte koşabiliyor, ama bir süreç içinde ikinci bir dünya
başlatmak HTTP 400 döndürüyor. Sebebi freezegun'ın zamanı süreç geneli taklit
etmesi ve veritabanı bağlantı sızıntısından kaçınma.

**Etki.** Yüksek. Paralel epizot, port başına ayrı sunucu süreci gerektiriyor.
Bu doğrudan bir bellek ve çekirdek bütçesi sorunudur.

## S-07 — İskelenin kendi bağlam kesme mantığı var

> **Kapsam.** iskelenin kendi kesme mantığını kaydediyor; montajcı yazılmadığı için bugün bir iddiaya değmiyor

> **Kapanma sınıfı.** Dış olgu — kesme mantığı referans iskelenin içinde ve iskele K-19 ile dondurulmuş

Referans iskele eski gözlemleri `[NOT SHOWN FOR BREVITY]` ile değiştiriyor.
Bizim bağlam montajcımız geldiğinde iki mekanizma çakışacak.

**Etki.** Sonraki görevde yüksek, şimdi sıfır. **Şu anki durum.** Dokunulmuyor.

## S-08 — 8 GB VRAM'e üç model aynı anda sığmıyor

> **Kapsam.** 8 GB VRAM'e üç modelin sığmadığını kaydediyor; donanım kısıtı

> **Kapanma sınıfı.** Dış olgu — donanım kısıtı; 8 GB VRAM ölçüm tasarımının dışında

Kabaca 1.1, 2.0 ve 4.7 GB, üstüne 32k bağlamın KV cache'i. Model değiştirmek
açık boşaltma gerektiriyor, o da epizotlar arasına yeniden yükleme gecikmesi
sokuyor.

**Etki.** Orta. **Ölçüm.** Aşama 4'te gerçek sayılar girecek.

## S-09 — WSL bellek sınırı host geneli

> **Kapsam.** WSL bellek sınırının host geneli olduğunu kaydediyor; işletme kısıtı

> **Kapanma sınıfı.** Dış olgu — `.wslconfig` host geneli; işletme ortamının kısıtı

`.wslconfig` her dağıtıma uygulanıyor, docker-desktop dahil. 8 GB'lık sınır
yalnız bizim dağıtımımızı değil hepsini bağlıyor.

**Etki.** Düşük.

## ~~S-10 — WSL içinden Windows host'taki Ollama'ya erişim henüz çözülmedi~~

~~Ağ kipi varsayılan NAT bırakıldı. WSL'den host'a erişim ya mirrored kipe
geçmeyi ya da host IP'sini dinamik bulup güvenlik duvarı kuralı açmayı
gerektiriyor.~~

**Kapandı, Aşama 1.** `networkingMode=mirrored` çözdü. Sunucu `127.0.0.1`'e
bağlı kalıyor ve WSL erişiyor. Güvenlik duvarı kuralı gerekmedi (K-34).

## ~~S-11 — Ajan davranışı aynı seed'de bile oynak~~

~~Aynı görev, aynı model, aynı seed ve aynı sıcaklıkla koşulan üç epizot
sırasıyla 19, 1 ve 19 API çağrısı yaptı.~~

**Kapandı, Aşama 2.** Oynaklığın kaynağı rastgelelik değil, modelin bellekte
yüklü olup olmamasıymış. litellm seed'i doğru geçiriyor. Soğuk yüklemeden
sonraki ilk çıkarım ısınmış hâldekinden farklı ama kendi içinde kararlı.
Epizot düzeyinde iki soğuk koşu birebir aynı yörüngeyi (19 çağrı), iki ısınmış
koşu da birebir aynı yörüngeyi (1 çağrı) verdi. Ölçümün tamamı
`docs/appworld-facts.tr.md` içinde. Devamı S-13'te.

## S-13 — Sunucu tarafında görmediğimiz bir durum daha var

> **İddiayı sınırlıyor.** K-21 — soğuk rejimin tekdüze olduğu

> **Kapanma sınıfı.** Sonraki tur — epizot öncesi boşaltma protokolü ölçülüp K-21 altında karara bağlanacak

S-11 kapanırken bir belirsizlik kaldı. "Isınmış" tek bir durum değil. Aynı görev
ısınmış modelle bir koşuda 1 API çağrısı verdi, on iki epizotluk ölçüm batch'inde
yine ısınmış modelle 0 verdi. Aradaki fark modelin daha önce hangi istekleri
gördüğü. Bu durumu istemciden görmüyoruz.

**Etki.** Orta. Tekrarlanabilirlik yalnız sunucunun durumu kontrol edilirse
sağlanıyor. **Azaltma.** Ölçülen tek güvenilir protokol her epizottan önce
modeli boşaltmak. Kararı Aşama 4 verecek, K-21 altında.

## S-14 — Ölçek ekseninin en küçük noktası taban etkisine yapışmış

> **İddiayı sınırlıyor.** 02-research-question ikinci soru — ölçek ekseninin üç noktası

> **Kapanma sınıfı.** Sonraki tur — ön koşul kapısı kalkarsa ölçek ekseninin en küçük noktası yeniden ölçülecek

`qwen2.5-coder:1.5b-instruct-q4_K_M` ile koşulan on iki epizodun on birinde ajan
hiç API çağırmadan yirmi adımlık tavana dayandı. 223 model turunda toplam 1 API
çağrısı çıktı, tur başına 0,0045.

**Etki.** Yüksek. Bu noktada ölçülecek bant yok, dolayısıyla ölçek ekseninin en
küçük ucu mekanizmanın katkısını gösteremez.

**Aşama 4 uyarısı.** Aynı görev 3B ve 7B ile de koşuldu ve üçü de yirmi adımlık
tavana dayandı, hiçbiri görevi bitirmedi. Bu, taban etkisi endişesinin yalnız
1.5B'yi değil ekseni kapsayabileceğini düşündürüyor. Ama ölçüm tek görev ve
model başına tek tohum; seed'ler de `run_id` üzerinden türediği için modeller
arası karşılaştırılabilir değil. Kapsam bu yüzden genişletilmedi, yalnız uyarı
eklendi.

**Azaltma.** Karar pilotun. Kural pilottan önce ilan edildi: 1,5B taban
koşulunda çözüm üretmiyorsa eksen 3B ve 7B'ye iner, iki nokta kalır ve ölçek
sorusu keşifsel olarak daha da daraltılır. 14B 8 GB'a sığmadığı için yukarı
doğru telafi yok.

**Ek, 20 Ağustos 2026.** Son cümle artık geçerli değil ve silinmiyor: engel
donanımdı, ve o donanım değişti. 14B Colab'ın GPU'sunda koşabiliyor, eksene
dördüncü nokta olarak girdi (K-133) ve ön kayıt A.11'e tarihli ek düşüldü.
Yukarı doğru telafi **var**; "yerel makinede yok"tu.

## ~~S-12 — Sıfırlama testi CI koruması altında değil~~ — KAPANDI: K-100 veriyi CI'a kurdu

**Kapandı, 18 Ağustos 2026.** Ölçüt uygulandı, iddia edilmedi.

**Kapanma ölçütü: tasarım boşluğuydu ve dolduruldu.** K-100 CI'a `appworld
install` ve `appworld download data` adımlarını ekledi, ve `pytest` filtresi
`-m "not model_server and not sandbox"` oldu — yani `appworld` işareti artık
elenmiyor.

**Kanıt, iki parça.** Test `tests/test_appworld_reset.py` içinde ve
`pytestmark = pytest.mark.appworld` taşıyor. CI'ın kullandığı filtreyle toplama
koşuldu: `pytest -m "not model_server and not sandbox" --collect-only` çıktısında
`test_appworld_reset` **bir kez** görünüyor, yani test CI'da gerçekten
toplanıyor.

**Neyin kapanmadığı.** Testin CI'da koştuğu gösterildi; testin doğru şeyi
ölçtüğü ayrı bir soru ve bu kayıt onu hiç sormamıştı.

Epizot başına veritabanı sıfırlaması projenin en önemli değişmezlerinden biri.
Ama testi `appworld` işaretli, yani indirilmiş 198 MB veri istiyor ve CI'da
koşmuyor.

**Etki.** Orta. **Azaltma.** Yerel-yalnız kontroller listelendi ve her aşama
birleşmesinden önce koşuluyor. Sonucu aşama raporuna tarihiyle yazılıyor (K-35).

## S-20 — Küçük modellerin baskın hatasını iyi biçimli tek bir örnek kapatabilir

> **Kapsam.** denenmemiş bir düzeltmenin işe yarayabileceğini kaydediyor; yapılmamış iş

> **Kapanma sınıfı.** Sonraki tur — denenmemiş bir düzeltme; denendiğinde kapanır ya da çürütülür

3B'nin epizotlarında en sık görülen sonlanma, tanımsız değişkene başvuran kod.
Ajan `apis` üzerinden çağrı yazmak yerine daha önce hiç atanmamış bir ada
başvuruyor ve adım hiç API çağrısı üretmeden bitiyor.

Sınır 3B'ye özgü değil. Beş göreve yayılan bir taramada 1.5B'nin 144 adımının
90'ı aynı kategoride çıktı (%62,5) ve beş görevin üçünde epizottaki her adım bu
kategorideydi. Ölçüm durma kuralı açıkken yapıldı, yani oran eşiğe koşullu; yine
de kategorinin baskınlığı iki modelde de aynı yöne işaret ediyor.

Bu hata, yönergenin kendisiyle ilgili. İskeledeki yönergede doğru kullanımı
gösteren bir örnek var, ama modelin onu taklit etmesi için yeterli değil.
Yönergeye eklenecek iyi biçimli tek bir örnek bu hatayı büyük ölçüde
kapatabilir.

**Ölçüm sınırı daha da sertleştirdi: örneğin kendisi çalışmıyor.**
`prompts/react_code_agent/instructions.reference.txt` 153. satırı şu:

```text
spotify_password = [account_password["account_name"] == "spotify" for account_password in passwords][0]["password"]
```

Satır alıntı olduğu için biçimlendirilmeden bırakıldı; yönergedeki hâli bu.
Liste kavraması boole üretiyor, `[0]` bir boole veriyor, `["password"]` ise
`TypeError: 'bool' object is not subscriptable` fırlatıyor. Yönerge bu satırın
ardından başarılı bir giriş çıktısı gösteriyor, yani çalışmayan bir satırı
çalışmış gibi sunuyor. İkinci eksik: `print(login_result)` sözlüğü basıyor ama
`login_result["access_token"]` çıkarımı hiç gösterilmiyor, ve ölçümde model
sözlüğün tamamını `access_token` parametresine geçirip 401 alıyor.

45 epizotta bozuk kalıp 34 kez yazıldı (13 epizotta) ve 11 kez o `TypeError`
üretti. Aynı epizotlarda doğru filtre yazımı 488 kez geçiyor, yani model
çoğunlukla düzeltiyor: kusur gerçek ama tek başına baskın sebep değil.

Yönerge yine değiştirilmiyor (K-19, K-23). Değişseydi AppWorld'ün yayımlanmış
taban sayılarıyla karşılaştırma kaybedilirdi, ve o tabanlar da aynı kusurlu
yönergeyle koşmuş durumda.

**Kusur karıştırıcı değil, ama etkinin bir kısmını açıklıyor olabilir.** Bozuk
örnek altı koşulun altısında da aynı; taban ile mekanizma koşulları arasındaki
farka karışmıyor. Yani teknik anlamda karıştırıcı değil, tabanı aşağı çeken bir
kapsam maddesi.

Riskli taraf yorumda. Bu kusur, mekanizmanın **en görünür hedefi**: derlenmiş
bir beceri kartı ya da hata indeksi girdisi, doğru parola seçimini ve
`login_result["access_token"]` çıkarımını gösteren iyi biçimli bir örnek
taşıyacak. Ölçtüğümüz kazancın bir kısmı bu durumda "mekanizma biriken deneyimi
kullanıyor" değil, **"kartlarımız kıyaslamanın bozuk örneğini onarıyor"**
anlamına gelir.

İkisi aynı sayıya bakarak ayrılamıyor. Ayıran şey K-59'un kontrastı: onarım
yapısal olduğu için alakasız kart da aynı işi görür. Alakasız getirme koşulu da
kazanırsa yorum birinci şıkka, yani "değer yapısal şablonda" hükmüne gider.

**Etki.** Yüksek, ve sonuca değil yoruma. **Azaltma.** K-56'nın zorunlu koşulu,
K-59'un önceden yazılmış yorumu, ve bu maddenin makalede kapsam olarak
yazılması.

**Etki.** Yüksek, ama sonuca değil yoruma. Mekanizma 3B'de kazanç gösterirse o
kazancın ne kadarının beceri bilgisinden, ne kadarının yalnız iyi biçimli bir
örnek görmekten geldiği ayırt edilemez.

**Azaltma.** Yönerge değiştirilmiyor. Değiştirilseydi K-19 kırılırdı ve
AppWorld'ün yayımlanmış taban sayılarıyla karşılaştırma kaybedilirdi. Yerine
iki şey yapılıyor: bu sınır burada yazılı duruyor, ve ayrım
`irrelevant_retrieval` koşuluna bırakılıyor — o koşul kartın biçimini koruyup
içeriğini bozduğu için "örnek görmenin" katkısını içerikten ayırıyor (K-56).

## S-21 — Artık varyansa nokta kestirim değil üst sınır yazılıyor

> **İddiayı sınırlıyor.** K-51 — artık varyansa yazılan üst sınır

> **Kapanma sınıfı.** Ölçüldü — otuz epizotta sıfır ayrışma; daha çok epizot sınırı daraltır, sıfıra indirmez

İlk ölçüm tek görevle ve durma kuralı kapalıyken yapılmıştı: 7B'de yirmi
epizottan biri farklı yörünge verdi, 1.5B ve 3B'de onar epizot tekdüze çıktı.

Ölçüm beş senaryodan birer göreve yayıldı, model başına görev başına altı soğuk
epizot, durma kuralı açık. 1.5B ve 7B'de otuzar epizodun tamamı görev içinde
birebir aynı çıktı; tavana dayanan yirmi adımlık epizotlarda da sapma yok.

**Sıfır ayrışma, sıfır oran demek değil.** Otuz epizotta hiç ayrışma görmemek
oranın küçük olduğunu gösteriyor, sıfır olduğunu değil. Ön kayda giren sayı bu
yüzden üst sınır. Clopper-Pearson tek yanlı %95 üst sınırları:

| Ölçüm | Rejim | Ayrışma | Üst sınır |
|---|---|---|---|
| 1.5B, beş görev | kural açık | 0/30 | %9,5 |
| 7B, beş görev | kural açık | 0/30 | %9,5 |
| İkisi havuzlanmış | kural açık | 0/60 | %4,9 |
| 1.5B, tek görev | kural kapalı | 0/10 | %25,9 |
| 3B, tek görev | kural kapalı | 0/10 | %25,9 |
| 7B, tek görev | kural kapalı | 1/20 | %21,6 |

Gürültü tabanına giren sayı model başına **%9,5**, ve hangi rejimde ölçüldüğü
yanında yazılı: durma kuralı açık, yani deneyin koşacağı rejim. Havuzlanmış
%4,9 yalnız iki modelin oranının aynı olduğu varsayımı altında geçerli; K-51
oranı model başına istediği için taban model başına alınıyor.

**Ölçümün görmediği bir eksen kazara sınandı.** Tarama tek bir Ollama süreci
içinde koşmuştu. Sunucu sonradan öldü ve betikten yeniden başlatıldı; sansür
ölçümü o yeni süreçte ve farklı bir koşucu betikle koşuldu. İki modelin beşer
görevi, yani on yapılandırma, adım ve çağrı sayılarında taramadakini birebir
tekrarladı — 7B'nin tavana dayanan iki epizodu (20 adım, 19 ve 20 çağrı) dahil.
Eşleşme adım ve çağrı düzeyinde, yörünge özeti düzeyinde değil: kayıt betiği o
özeti hesaplamıyor. Sunucu yeniden başlatması yine de artık varyansın sınanmış
kaynakları arasına ancak bu kadarıyla giriyor.

**Kalan sınır.** Üst sınırı %2'ye indirmek sıfır ayrışmayla 149 epizot
istiyor; elimizde model başına otuz var. Daralması pilotun tekrar koşularına
bağlı. İki rejim havuzlanamaz: kural açıkken epizotlar kısalıyor ve sapma
fırsatı azalıyor, dolayısıyla iki ölçüm aynı niceliği ölçmüyor. İlk ölçümdeki
1/20 çürütülmüş değil, farklı bir rejime ait.

**Etki.** Düşük. Gürültü tabanı artık tek göreve dayanmıyor ve ön kayda
girebilecek durumda. 3B'nin artık varyansı kural açık rejimde taranmadı; ölçek
ekseninde kalıp kalmayacağı K-53'e bağlı olduğu için taraması o karardan
sonraya bırakıldı.

## S-22 — Sansür oranı beş göreve ve model başına tek epizoda dayanıyor

> **İddiayı sınırlıyor.** K-53 — sansür oranının bir sonuç olduğu

> **Kapanma sınıfı.** Sonraki tur — beş görev ve model başına tek epizot; tekrar sayısı artınca sınır daralır

K-53'ün ölçütü üç modelde de reddedildi: on beş epizodun on beşi de
doğrulayıcıdan kaldı, model başına %95 alt sınır %54,9. Sonucun kendisi güçlü
ama dayandığı örneklem dar.

Beş görev rastgele seçilmedi. Artık varyans taramasından geldiler ve o tarama
onları başka bir amaç için, senaryo başına birer görev olsun diye seçmişti.
Train bölmesinin zorluk dağılımını temsil ettiklerine dair bir kanıt yok. Model
başına da tek epizot var; oran bir modelin genel davranışını değil, o beş
görevdeki davranışını ölçüyor.

**Etki.** Orta, ve yönü tek taraflı değil. Beş görev ortalamadan zorsa gerçek
sansür oranı daha düşüktür; kolaysa daha da yüksektir. İkinci ihtimal ölçek
ekseninin tümünü tehdit ediyor, çünkü 7B de ölçütü karşılamıyor.

**İkinci sınır: tavan sabitti.** Ölçüm on beş epizodun on beşinde de sabit 20
adımlık tavanla koşuldu, oysa K-43 tavanı `k × num_api_calls` diye bağlıyor.
Beş görevin çapaları 10, 29, 71, 145 ve 195. Yani `6104387_1`'de referans çözüm
195 çağrı isterken ajana 20 model çağrısı verildi; o epizodun geçmemesi modelin
değil tavanın sonucu olabilir. Yalnız `29caf6f_1` (çapa 10) çapasıyla uyumlu
bir tavanla koştu. "Ölçüt karşılanmıyor" sonucu ayakta, ama sebebin ne kadarının
modelden geldiği bu ölçümden çıkmıyor.

**Azaltma.** Ön kayda giren kural, sayı değil. Ama kuralın ilk yazımı da
yanlıştı: "sansür oranı %10'un altında olmalı" diyordu ve K-53'ün ayırdığı iki
niceliği birleştiriyordu. Doğru hâli şu — yüzde on kuralı **tavana çarpma
oranına** ait, sansür oranı ise bir sonuç ve o kurala bağlı değil. Eksende kalma
ölçütünün eşiği eşleştirilmiş tasarımın gereksinimlerinden geliyor, kesin sayısı
pilottan.

Oran pilotun kendi örnekleminde ve görev başına tavanla yeniden ölçülecek.
Buradaki on beş epizodun işlevi, "7B sorun değil" varsayımını dayanaksız
bırakmak.

## S-27 — Bant taraması eski durma kuralıyla koşuldu, ön koşul kapısı ona dayanıyor

> **İddiayı sınırlıyor.** K-58 — ön koşul kapısının dayandığı bant taraması

> **Kapanma sınıfı.** Sonraki tur — bant taraması bugünkü durma kuralıyla yeniden koşulursa dayanak değişir

Bant taramasının otuz epizodu, "başarılı çağrı ilerlemedir" diyen eski kuralla
ve dört adımlık eşikle koşuldu. O kuralın yanlış olduğu sonradan ölçüldü (S-25)
ve düzeltildi.

**Ölçülen kirlilik:**

| Sonlanma | Epizot |
|---|---|
| `no_progress` | 16/30 (%53) |
| `step_ceiling` | 9/30 |
| `agent_finished` | 5/30 |

`no_progress` ile kapanan on altı epizodun **on beşi düzeltilmiş kuralla
kesilmezdi**: uç nokta temelli durgunlukları 2 ile 6 arasında, yeni eşik 15.
Altısı dört adımda kapanmış.

**Etki.** Yüksek. Otuz epizodun yarısı başarma şansını hiç bulmamış olabilir ve
**0/30 sonucu temiz bir ölçüm değil.** Ön koşul kapısı 11 Ağustos 2026'da o
sonuca dayanarak ateşledi; model ailesinin yeniden açılması da ona bağlı.

**Karşı kanıt, zayıflatıyor ama kapatmıyor.** Eski kural her epizodu dörtte
kesmiyordu: teşhislerde 45 epizotta 958 adım koştu, ortalama 21, ve iki epizot
150 ile 92 adım gitti. Arıza asimetrikti — çağrı üreten epizotları sonsuza
koşturuyor, hiç çağrı üretmeyenleri dörtte kesiyordu. Kapının ateşlemesi için
kritik olan taraf tam olarak ikincisi.

**Azaltma.** Tarama düzeltilmiş kuralla tekrarlanıyor (`bant2` öneki). Sonucu
sıfır çıkarsa kapının ateşlemesi temiz veriye dayanmış olacak ve aşağı akıştaki
her şey ayakta kalacak. Sıfırdan farklı çıkarsa kapı kirli veriyle ateşlemiş
demektir ve aile kararı yeniden açılacak.

## ~~S-28 — Künye alanı yanlış çağrı yerine yazıldı, otuz epizot düştü, nöbetçi ateşlemedi~~ — KAPANDI: K-100 öncesi bir arıza; ön kontrol nöbetçisi kuruldu

**Kapandı, 18 Ağustos 2026.** Ölçüt uygulandı.

**Kapanma ölçütü: tasarım boşluğuydu ve dolduruldu.** Kayıt "hatırlanmaya bağlı
nöbetçi nöbetçi değil" diyordu; eksik olan, taramanın kendi ön kontrolüydü.

**Kanıt.** `scripts/setup/measure_band.py` ve
`scripts/setup/measure_boundary_control.py` içinde birer `def preflight`
tanımı var, ve ikisi de otuz epizot başlamadan tek epizotla yazma yolunu
koşturuyor: künye satırı ve epizot satırı aranıyor, model çağrısı sıfırsa koşu
başlatılmıyor.

**Neyin kapanmadığı.** Ön kontrol yazma yolunun koştuğunu gösteriyor; yazılan
değerlerin doğru olduğunu göstermiyor. Künye alanlarının içeriği ayrı bir
sözleşmenin konusu (S-29).

`max_output_tokens` K-60 gereği künyeye eklenirken (637c825) `insert_run_manifest`
yerine `RecordingAgent` kurucusuna yazıldı. İskele bu anahtar sözcüğü tanımıyor;
`bant2` taramasının otuz epizodu da ajan kurulurken
`TypeError: Agent.__init__() got an unexpected keyword argument 'max_output_tokens'`
ile düştü ve tarama hiç veri üretmedi.

**Neden fark edilmedi.** O commit "152 test geçti, atlanan yok" diyor ve doğru
söylüyor. `tests/test_recorded_run.py` adına rağmen `scripts/record_run.py`'yi
koşmuyor, veritabanındaki **eski** satırları okuyor. Koşucu ne kadar bozulursa
bozulsun, geçmiş bir koşudan iyi satırlar durdukça o test geçiyor.

**Birim testiyle kapatılamayan kısım.** Ajan kurucusu sunucusuz çağrılabiliyor
(`Agent.__init__` yalnız yapılandırmayı saklıyor), ama `record_run.py` kurucuya
gelmeden önce etkin bağlam penceresini sunucudan okuyor (K-37 kapısı), yani
sunucusuz bir alt süreç testi kurucuya hiç ulaşamıyor. Kurucuya giden anahtar
sözcükler `main()` içinde satır içi yazıldığı için ayrı bir testin onları
kopyalaması da işe yaramazdı: kopyalanan çağrı yeri tam olarak kayabilen şey.

**Azaltma.** Duman testi ölçüm betiğinin ön kontrolü oldu ve otomatik koşuyor
(`scripts/setup/measure_band.py`, `preflight`). Elle koşulacak bir araç olarak
bırakmak yetmezdi: araç o gün de vardı ve koşulmadı. Hatırlanmaya bağlı bir
nöbetçi nöbetçi değil.

**Etki.** Ölçüm üstünde yok: düşen koşu veri yazmadı ve epizot atomikliği
korundu. Etki zamanda, bir tarama boşa gitti.

## ~~S-29 — Künye sözleşmesinin makine tarafı yalnız sıfırdan kurulan veritabanında geçerli~~ — KAPANDI: koşucular künye kısıtlarını başlamadan denetliyor

**Kapandı, 18 Ağustos 2026.** Ölçüt uygulandı.

**Kapanma ölçütü: tasarım boşluğuydu ve dolduruldu.** `ALTER TABLE`'ın kısıt
taşımaması SQLite'ın değişmeyen bir olgusu; kapanma o olguyu değil, olgunun
sessiz kalmasını kapatıyor.

**Kanıt.** `missing_manifest_constraints` üç koşucunun üçünde de çağrılıyor —
`measure_band.py`, `measure_boundary_control.py`, `measure_rule_off.py` — ve
kısıt eksikse koşu **başlatılmıyor**, epizot harcanmadan çıkılıyor.

**Neyin kapanmadığı.** Var olan bir veritabanı hâlâ kısıtsız sütunlar taşıyor.
Kapanan şey, o veritabanının üstüne yeni ölçüm koşulması.

Şema yalnız yeni dosyada uygulanıyor; var olan dosyaya eksik sütunlar
`ALTER TABLE ADD COLUMN` ile ekleniyor. SQLite'ın ALTER TABLE'ı kısıt taşımıyor ve
bu ölçüldü:

| Denenen | Sonuç |
|---|---|
| `ADD COLUMN ... NOT NULL DEFAULT CURRENT_TIMESTAMP` | reddedildi, sabit olmayan varsayılan |
| `ADD COLUMN ... NOT NULL` (varsayılansız) | reddedildi, NOT NULL sütun NULL varsayılanla eklenemiyor |
| `ADD COLUMN ... NOT NULL DEFAULT '' CHECK (...)` | reddedildi, CHECK mevcut satırlarda düşüyor |
| `ADD CONSTRAINT` | yok, sözdizimi hatası |
| `ADD COLUMN ... NOT NULL DEFAULT <sabit>` | geçti |

Sonuç: `serving_mode` sütunu `results/zihin.sqlite`'a eklendi, onunla gelen iki
CHECK eklenemedi. Canlı dosyanın şeması okundu ve üç eski CHECK'ten fazlasını
taşımıyor. Ayrıca `num_ctx_requested` orada hâlâ `NOT NULL`, yani barındırılan
kipin bıraktığı boşluk şema düzeyinde reddediliyor: **PR #18'in sözleşmesi canlı
veritabanında hiç işlemiyor.**

Bunun neden fark edilmediği de görünür: künyedeki altmış iki satırın hepsi `local`
ve model etiketleri yalnız üç `qwen2.5-coder` boyutu. Sınır kontrolünün otuz
epizodu bu depoya hiç yazılmadı — `scripts/setup/measure_boundary_control.py`
yalnız JSON üretiyor, kayıt katmanını kullanmıyor. Barındırılan kip hiç
denenmediği için kısıt da hiç sınanmadı.

**Etki.** Yazılmış veri üstünde yok: fark kısıtlarda, değerlerde değil, ve Python
katmanı bütün koşularda devredeydi. Etki ileriye dönük — "sözleşme yorumla değil
makineyle tutuluyor" iddiası yalnız sıfırdan kurulan dosyalar için doğru.

## ~~S-30 — Çıktı bütçesi ortamdan okunuyordu ve sessiz varsayılanı yanlış koşu başlattı~~ — KAPANDI: çıktı bütçesi yapılandırmaya taşındı

**Kapandı, 18 Ağustos 2026.** Ölçüt uygulandı.

**Kapanma ölçütü: tasarım boşluğuydu ve dolduruldu.** Kural yazılıydı — ölçümü
etkileyen her şey yapılandırmada — ve bu parametreye uygulanmamıştı.

**Kanıt, iki parça.** `max_output_tokens` artık `config/recording.yaml` içinde
tanımlı, ve `scripts/record_run.py` içinde `ZIHIN_MAX_TOKENS` ortam değişkeni
**hiç geçmiyor** (arandı, sıfır eşleşme). Değer künyeye de yazılıyor.

**Neyin kapanmadığı.** Aynı bütçenin farklı model ailelerinde aynı koşul
olmadığı ayrı bir sınırlama ve açık duruyor (S-26).

`max_output_tokens` ölçümü doğrudan etkiliyor: aynı model ve aynı otuz görevde
400'de 6/30, 4000'de 20/30 (S-26). Yani tesisat parametresi değil, ölçümün
tanımının parçası.

Buna rağmen ortam değişkeninden okunuyordu ve sessiz varsayılanı 400'dü. Bu, kendi
kuralımızın ihlaliydi — ölçümü etkileyen her şey yapılandırmada, ortam yalnız
gizli değerler ve sunucudan geri okunanlar için. Kural yazılıydı ve bu parametreye
uygulanmamıştı.

Sonucu somut: sınır kontrolü 13 Ağustos'ta yanlışlıkla 400 bütçeyle başlatıldı ve
iki epizot yazıldıktan sonra durduruldu. Karşılaştırılabilir olmadıkları için o
önek bırakıldı.

**Düzeltme.** Değer `config/recording.yaml` içinde ve sessiz varsayılanı yok;
belirtilmezse koşu düşüyor.

## ~~S-31 — Devam mantığı iki farklı ölçüm koşulunu sessizce birleştirebiliyordu~~ — KAPANDI: devam koruması yazılmışların koşulunu karşılaştırıyor

**Kapandı, 18 Ağustos 2026.** Ölçüt uygulandı.

**Kapanma ölçütü: tasarım boşluğuydu ve dolduruldu.** Atlama vardı, koşul
karşılaştırması yoktu.

**Kanıt.** `resume_check` `src/zihin/records.py` içinde tanımlı ve iki koşucuda
çağrılıyor (`measure_rule_off.py`, `measure_boundary_control.py`). Yazılmış
epizotların koşulu şimdikiyle uyuşmazsa koşu duruyor ve mesaj yeni bir önek
istiyor.

**Neyin kapanmadığı.** Koruma karşılaştırdığı alanlarla sınırlı. Künyede
taşınmayan bir koşul farkı hâlâ görünmez.

Yarıda kesilen bir koşuya devam ederken tamamlanmış epizotlar atlanıyor. Atlama
tek başına yetmiyordu: yazılmış epizotların **koşulu** ile yeni koşununki
karşılaştırılmıyordu.

S-30'un açığa çıkardığı senaryo somut. Bütçesi 400 olan iki epizodun üstüne 4000
ile devam edilseydi, otuz epizotluk küme ikisi 400 yirmi sekizi 4000 olan bir
karışım olurdu. Künye bunu kaydeder ama tek başına engellemez.

Ana koşuda aynı arıza kırk saatlik bir kümeyi çöpe atardı ve fark ancak sonradan
edilirdi.

**Düzeltme.** Devam denetimi koşul alanlarını karşılaştırıyor ve uyuşmazsa koşuyu
reddediyor: model, sunum kipi, sıcaklık, taban tohum, çıktı bütçesi, durma eşiği,
bağlam penceresi, KV cache tipi, flash attention, AppWorld commit'i, yönerge
özeti, kütüphane kimliği, çalışma ağacı, koşul, bölme ve adım tavanı.

Üç alan ayrı sınıfta.

`code_commit` reddedilmiyor: farklı bir commit altında devam etmek meşru olabilir
ve 13 Ağustos'ta kasten öyle yapıldı. Ama iki commit arasındaki fark
listeleniyor, ve **epizot içinde ne olduğunu belirleyen** yollardan biri farkta
görünürse uyarı redde yükseliyor. Böylece "farklı commit" ile "ölçümü değiştiren
farklı commit" ayrılıyor ve karar makinede oluyor.

`working_tree` reddediliyor. Farklı bir commit tanımlanabilir, kirli ağaç
tanımlanamaz: ilk yarı temiz ikinci yarı geçersiz kılmayla kirli koşarsa ikinci
yarının hangi kodda koştuğu belirsiz kalır.

`model_server_env` reddedilmiyor, farklılaşan anahtarlar listeleniyor.
Bileşenlerinin çoğu zaten ayrı ayrı reddediliyor; kalanı, sağlayıcının eklediği ve
bizim adlandırılmış alanımız olmayan bir ayar için görünürlük veriyor.

**Kalan kabalık.** Ölçümü belirleyen yollar listesi dosya düzeyinde ve
`src/zihin/records.py` listede yok. Dosya hem kaydedicinin yazma yolunu hem koşu
düzenleme yardımcılarını taşıyor; 13 Ağustos'un meşru devam değişikliği
ikincisindeydi. Yazma yolunu da korumak modülün bölünmesini gerektirir.

**Listedeki iki eksik, kirli ağaç kapısı listeye daraltılırken bulundu (K-76).**
`src/zihin/retriever.py` ve `src/zihin/cards.py` listede değildi: birincisi hangi
kartın hangi göreve gittiğini seçiyor, ikincisi modelin ne okuduğunu belirliyor.
Kapı bütün ağaca bakarken eksiklik yalnız devam denetimini zayıflatıyordu; kapı
listeye daraltıldığında **kapanmayan bir kapıya** dönüştü, çünkü kirli bir
getiriciyle koşu başlatılabilir hâle geldi. İkisi eklendi ve iki test çiviliyor.
Daraltmanın bulduğu şey daraltmanın kendi riskiydi: liste artık tek savunma
hattı, ve eksik bir girdinin bedeli arttı.

**Kayıttaki iki boşluk kapatıldı.** Adım tavanı hiçbir yere yazılmıyordu —
`termination_reason` tavana çarpıldığını söylüyor ama tavanın kaç olduğunu
söylemiyordu; `episodes.step_ceiling` eklendi. `library_id` künyeye eklendi ve
beceri kütüphanesi gelene kadar NULL.

## S-56 — Gürültü tabanı sıfır değil: tek epizottan çıkarılabilecek her iddianın üst sınırı

> **İddiayı sınırlıyor.** PILOT_REPORT.md ve uçtan uca demo — tek epizottan okunan her kol karşılaştırması

> **Kapanma sınıfı.** Ölçüldü — on beş hücrenin on biri üç tekrarda ayrıştı; gürültü tabanı bulgunun kendisi

Sabit tohum, sıcaklık 0,2, aynı prompt, aynı soğuk rejim — ve **on beş hücrenin
on biri üç tekrarda ayrışıyor.** Ölçüm üç kollu kart koşusu: 3 kol × 5 görev × 3
tekrar, hepsi tek commit'te (`docs/reports/uc-kollu-kart-kosusu.md`,
`results/card-arms.json`).

Bu bir kusur değil, bir büyüklük. K-51 determinizmi bir varsayım olmaktan
çıkarıp ölçülen bir niceliğe çevirmişti; bu, o niceliğin 7B'de bu görev
kümesindeki değeri.

**Kapsamı.** Gürültü tabanı, iki kolu tek epizotla karşılaştıran her ölçümü
geçersiz kılıyor. Bu düzenekte tek zarar gören uçtan uca demo oldu, çünkü tek
epizotla iki kol karşılaştıran tek ölçüm oydu (aşağıda).

**Neyi kapsamıyor.** Sıfırlar etkilenmiyor. `bant2`, `bant3` ve `bant3-kapali`
üç bağımsız koşu ve üçü de sıfır verdi; gürültü bir sıfırı imal edemez. Ön koşul
bulgusu (K-58) yerinde duruyor.

**Ek, 26 Ağustos 2026 — geriye dönük tavan denetimi.** Bu üç koşunun tavana
çarpma oranı sonradan kayıttan ölçüldü ve üçü aynı yerde durmuyor: `bant3` %0,0,
`bant3-kapali` **%96,2**, `bant2` ise kayıtta yok. Gürültü argümanı değişmiyor —
gürültü bir sıfırı imal edemez — ama iki sıfırın **alt sınır** olduğu burada
yazılı değildi. S-63'te.

**Uygulaması.** Bundan sonra iki kolu karşılaştıran hiçbir sonuç tek epizottan
okunmuyor. Hücre başına tekrar sayısı ölçümün tanımının parçası ve raporda
yazılı olacak.

---

## S-57 — Kimlik doğrulama bariyerini aşmak gerekli ama yeterli değil

> **İddiayı sınırlıyor.** PILOT_REPORT.md ayna bulgusu — iki mekanizmanın aynı darboğaza yakınsaması

> **Kapanma sınıfı.** Sonraki tur — bariyerden sonra ne gerektiği bir sonraki ölçüm turunun sorusu

Üç kollu koşuda **üç kolun her birinde** giriş etkisine (`POST
<uygulama>.auth/token`, 2xx) on beş hücrenin üçü ile yedisi arasında ulaşıldı.
Tamamlama ise **0/45**.

Yani jetonu almak bu örneklemde tek bir görevi bile çözdürmedi. Ölçülen darboğaz
jeton değil; jeton, arkasındaki darboğaza açılan kapı.

**Ayna bulgusuna sonucu.** Kütüphane jetonu almayı öğretiyor, indeks jetonu
taşımamayı yasaklıyor — iki bağımsız korpus aynı mekanik darboğaza yakınsadı ve
bu yakınsama gerçek. Ama o darboğazı aşmak görevi çözmeye yetmiyor. Ayna
bulgusunun anlatı gücü bu ölçümle sınırlanıyor ve ikisi birlikte yazılmak
zorunda: mekanizmalar aynı yere yakınsadı, **ve** o yer görevin çözüldüğü yer
değil.

---

## S-54 — Durum sondasının kör noktası kapandı, ama **ileriye dönük**

> **İddiayı sınırlıyor.** K-93 — durum sondasının değişiklikleri gördüğü

> **Kapanma sınıfı.** Sonraki tur — eski epizotların yeniden koşulması ya da ileriye dönüklüğün kabulü kapatır

Sunulan kipteki özet tabanlı sonda, satır sayısını değiştirmeyen bir `PATCH`i
görüyor (K-93, `set_volume` ile ölçüldü). Eski sondanın kendi belgesinde yazılı
olan kör nokta bu eksende kapanıyor.

**Kapanma yalnız bundan sonraki koşular için geçerli.** Mevcut beceri kütüphanesi
ve hata indeksi **eski sondayla** madenlendi: `state_change` satır sayısı farkı
taşıyor ve güncelleme yalnızca yazan çağrıları görmüyor. Bunun üç yerde sonucu
var ve üçü de kapanmadı:

- **Ampirik yazma kümesi** (K-41) satır sayısına dayanıyor. Satır sayısını
  değiştirmeyen bir yazma o kümede yok.
- **Hata kartlarının ayırt edici koşulları** bu kümeden türetilen sinyallerle
  arandı; korpus yeniden madenlenirse koşullar değişebilir.
- **Durma kuralının kalibrasyonu** eski sonda altında yapıldı. Kayıttaki
  ağırlığı sıfır olduğu için (4102 adımda 0) kalibrasyonun değişmesi
  beklenmiyor, ama sınanmadı.

**Silinmiyor, ayrımla duruyor:** kör nokta yeni koşularda yok, eski türetilmiş
projeksiyonlarda var. Yeniden madenleme yapılırsa ikisinin farkı ölçülüp
raporlanmalı; yapılmazsa kütüphane eski sondanın gördüğü dünyanın ürünü olarak
okunmalı.

## S-53 — Kaydedicinin montaj noktası uzak kipte ateşlemiyordu, ve sessizdi — DÜZELTİLDİ

> **Sınıflandırılmadı.** aynı sınıf

İlk sandbox epizodu koştu, 32 KB'lık bir yörünge üretti ve kayda **sıfır adım**
yazdı. Epizot satırı yine yazıldı, doğrulayıcı yine sonuç verdi; hiçbir yerde
alarm çıkmadı.

**Sebep.** Referans ajan `world.batch_execute` çağırıyor, `world.execute` değil.
Süreç içi kipte `batch_execute` her kod için `self.execute` çağırdığı için
`execute`i sarmalamak yetiyordu — kayıt bugüne kadar bu tesadüfle çalıştı. Uzak
ortam kipinde `batch_execute` doğrudan HTTP çağrısına sapıyor ve `self.execute`
hiç çağrılmıyor.

**İkinci kat.** Montaj düzeltildikten sonra adımlar geldi ama **eylemler sıfır
kaldı**. `_action_rows` iki kaynağın uzunluğunu karşılaştırıyor ve ikinci kaynak
(`api_calls.jsonl`) sandbox kipinde host tarafında yok. Yokluğu "sıfır çağrı"
diye okunuyordu. Kaynağın varlığı artık açık bir bayrak; yokluğu sayım
karşılaştırmasını da devre dışı bırakıyor, çünkü karşılaştıracak ikinci sayı yok.

**Kalan koruma.** Vekil uygulama çağrısı gördüğü hâlde sıfır adım kaydedilmişse
koşu epizot satırını yazmadan düşüyor (K-98). Bu iki arızanın ikisini de
yakalardı.

## S-52 — Vekil `error_class` alanını dolduramıyor, çünkü telde istisna yok

> **İddiayı sınırlıyor.** DATA_MODEL.md — `actions.error_class` alanının her epizotta dolu olduğu

> **Kapanma sınıfı.** Sonraki tur — yakalama noktası ya da veri modeli değişirse alan yeniden dolar

Bugünkü kayıt `actions.error_class` alanında `Requester`ın fırlattığı istisnanın
sınıf adını taşıyor. Vekil o istisnayı hiç görmüyor: istisna konteynerin içinde,
çağrı döndükten sonra oluşuyor. Sandbox'lı epizotlarda alan `NULL` kalıyor.

**Kaybedilen bilgi yok, ama kolonun anlamı kip başına değişiyor.** Ölçüldü: alan
5261 eylemin 4489'unda boş ve 772'sinde `"Exception"`, ve o 772 tam olarak
200 dışındaki durum kodlarının toplamı (401 503 + 422 235 + 409 34 = 772). Yani
alan durum kodundan bire bir türetilebiliyor ve hiçbir eylemde ek bir şey
söylemiyor.

Vekilin görmediği bir değeri uydurması mümkündü — durum 200 değilse
`"Exception"` yazmak — ve yapılmadı. Uydurulan bir değer, ölçülmüş bir değerden
ayırt edilemez hâle gelir.

## S-51 — Konteynerin ortam sunucusu ajanın koduyla aynı süreçte

> **İddiayı sınırlıyor.** 04-threat-model — konteynerin ajanın kodunu yalıttığı

> **Kapanma sınıfı.** Dış olgu — gömülü IPython kabuğu AppWorld'ün mimarisi; yalıtım konteyner sınırında aranıyor

Ortam sunucusu ajanın kodunu gömülü bir IPython kabuğunda yürütüyor, yani ajanın
kodu o sürecin yapabildiği her şeyi yapabiliyor: dünyanın yerel saatini
değiştirebilir, sunucunun bellek içi durumunu bozabilir, `execute`in döndürdüğü
metni etkileyebilir.

**Bu K-B'nin doğrudan sonucu ve kaçınılmaz.** Konteynerde tam `appworld` paketi
olacaksa, kodu yürüten şey de o pakettir. İnce bir RPC istemcisi bu yüzeyi
kapatırdı ama ajanın gördüğü arayüzü değiştirirdi (K-19).

**Korunan şey konteynerin içi değil, host.** Üçü de dışarıda: kayıt veritabanı,
doğrulayıcı, ve API sunucusunun yönetim yüzeyi. Ajanın dünyaya yaptığı her
değişiklik API sunucusundan geçmek zorunda ve o yol vekilden geçiyor, yani
kaydediliyor. Verdict de host tarafında, host'un yazdığı veritabanlarından
üretiliyor.

**Kapanmayan tek yer `DELETE /date_time`.** Vekilin alan ölçütü orada
"boş olmayan metin" ile yetiniyor, çünkü değer konteynerin içinde üretilen bir
UUID ve host onu önceden bilemiyor. Ajan kendi ürettiği bir kimlikle o rotayı
çağırabilir; yaptığı şey konteynerin kendi saat dondurmasını kaldırmak olur.
Dünyanın saati API sunucusunda ve `POST /date_time` tam eşleşmeye bağlı, yani
dünyanın saati bu yolla değişmiyor.

## S-50 — Yönetim rotalarının hepsi kesilemiyor: on biri dünyayı kurmak için gerekli

> **İddiayı sınırlıyor.** K-95 — yirmi bir yönetim rotasının vekilde kesildiği

> **Kapanma sınıfı.** Ölçüldü — K-95'in yirmi bir rotasından on biri dünyayı kurmak için gerekli çıktı

Kapsam belgesinin K-95 kararı "yirmi bir yönetim rotası vekilde yapısal olarak
kesilsin" diyordu. Ölçüm bunun harfiyen uygulanamayacağını gösterdi: ortam
sunucusunun **kendisi** dünyayı kurmak için on bir yönetim çağrısı yapıyor —
kurulumda sekiz, her adımdan sonra bir `POST /dbs/save`, kapanışta iki. Ortam
sunucusu konteynere girdiğinde o çağrılar da konteynerden geliyor.

Adım başına gelen `POST /dbs/save` ayrıca **ajanın kodundan sonra** geliyor, yani
"kurulum bitti, artık yönetim kapalı" biçiminde bir faz kapısı da işe yaramıyor:
çağrı `execute`in içinde, ajanın kodunun ardından.

**Uygulanan hâl: rota adı yerine gövdenin alanları.** İzin verilen on bir çağrının
her alanı ya tam değerine ya da ölçülmüş bir kalıba bağlı. Kaçış yolunun durduğu
yer `to_db_home_path`: tam eşleşme şartı olduğu için ajan host'un yazdığı yeri
değiştiremiyor. Ölçüldü — gerçek trafiğin 11'i geçiyor, kurcalanmış 12 denemenin
12'si kesiliyor, ve testin korumasız kolunda dosya gerçekten host'a yazılıyor.

**Kalan sınır ölçüldü ve büyük ölçüde kapandı.** Üç ayrı ölçüm:

1. **Ajan tetikli bir `/dbs/save`, sondanın göreceği değişiklikleri tüketmiyor.**
   Satır sayısını değiştirmeyen bir değişiklik yapıldı, sonda gördü
   (`{"spotify": {"MusicPlayer": 1}}`), izinli `/dbs/save` gönderildi, sonda
   tekrar koşuldu ve değişiklik hâlâ oradaydı. Sonrasında yapılan yeni bir
   değişiklik de göründü (`MusicPlayer: 2`), yani sonda canlı kalıyor. Çağrı
   yinelenen bir yazma, kayıt körleşmiyor.
2. **`SO_PEERCRED` ile ayırmak mümkün değil, ve sebebi iki katlı.** Konteynerde
   ajanın kodu **pid 1**, yani ortam sunucusuyla aynı süreç; ayrıca vekile
   bağlanan şey köprü ve köprü aynı sürecin bir iş parçacığı. Unix soket bu
   bilgiyi taşıyor ama ayıracak iki taraf yok. Aynı bilgi başka bir işe yaradı:
   konteynerin kimliğini teyit etmek (K-98).
3. **Ajanın kodundan çalışan bir yol bulunamadı.** AppWorld'ün kendi
   SafetyGuard'ı `requests`, `socket`, `subprocess` ve
   `urllib.request.urlopen`'ı kesiyor; istekçi nesnesi `apis` üzerinden
   erişilebilir değil. Beş yol denendi, beşi de kapalı.

Üçüncüsü **yolun olmadığının kanıtı değil**, beş denemenin sonucu. Vekilin alan
ölçütü bu güvence üzerine kurulmuyor: referansın kendi koruması bir gün
gevşerse filtre yerinde kalıyor.

## S-49 — Kırk beş test CI'da hiç koşmamıştı, ve iki ortam farkı yerelde görünmüyordu — DÜZELTİLDİ, VE KAPSAMA SONRADAN KAPATILDI

> **Sınıflandırılmadı.** aynı sınıf

**Sonradan eklenen not.** Aşağıdaki düzeltme testleri işaretleyip CI'da eledi:
gereksinim görünür oldu ama testler hâlâ koşmuyordu. Kapsama K-100 ile kapandı —
CI artık `appworld install` ve veriyi kuruyor. Ölçülen fark: koşan test 365'ten
446'ya, atlanan 47'den 7'ye; bedeli duvar saatinde 26 saniye
(`results/ci-kapsam.json`). Kalan yedi atlama yapısal: `results/` altındaki
üretilmiş artefaktlara bağlılar ve o dizin bilerek gitignore'da.



PR akışı #19'dan sonra durdu ve yol haritasının yedi maddesi tek dalda, 52 commit
olarak birikti. Dal itilmediği için **dört CI kontrolü o commit'lerin hiçbirini
görmedi**. İtildiğinde iki ayrı arıza çıktı ve ikisi de yerel koşuda görünmüyordu.

**Birinci fark: uygulama modülleri.** `route_table()` uç nokta çözümlemesini
AppWorld'ün uygulama modüllerinden kuruyor (`appworld.apps.venmo` ve kardeşleri).
O modüller `appworld install` ile geliyor, paketle değil — pakette yalnız
`appworld.apps.lib` var. CI paketi kuruyor, `appworld install` koşmuyor (K-32).
İlgili testler `appworld` işaretini taşımadığı için `-m "not appworld"` onları
elemiyordu. Ölçüldü: dört modülde **45 test** — `test_api_routes` 16,
`test_stopping_rule` 16, `test_shield_mount` 10, `test_compiler` 3.

**İkinci fark: çağırma biçimi.** `tests/test_shield_mount.py` sahte istekçiyi
`tests.test_api_capture` üzerinden alıyor. Depo kökü sys.path'te olmadığında
import düşüyor, ve kökün orada olması çağırma biçimine bağlı: `python -m pytest`
çalışma dizinini ekliyor, `pytest` betiği eklemiyor. Yerel koşu birincisini, CI
ikincisini kullanıyordu.

**İkisi de yerel bir ön kontrolle yakalanmadı, çünkü ön kontrol aynı gizleyen
biçimi kullanıyordu.** Birinci farkı taklit etmek için `appworld.apps.<uygulama>`
import'unu reddeden bir kanca, ikincisi için betik biçiminde çağırma gerekti;
ikisi kurulduktan sonra sekiz PR'ın hepsi yerelde önceden yeşil doğrulandı.

**Düzeltmeler.** Uygulama modülleri yoksa çözümlemeye ihtiyaç duyan test artık
**atlanıyor**: yama AppWorld'ün kendi `import_apis_module`'una konuyor, çünkü
testler `route_table`'ı doğrudan import ediyor ve modül özniteliğini yamalamak
çağıranın elindeki adı değiştirmiyor. Elle tutulan bir işaret listesi
kullanılmadı; hangi modülün çözümlemeye dokunduğu zamanla değişiyor ve liste
sessizce eskir. İkinci fark için `pyproject.toml` içinde `pythonpath = ["."]`:
aynı takımın iki çağırma biçiminde farklı sonuç vermesi testin değil
yapılandırmanın kusuru.

**Kalan sınır.** O 45 test CI'da hâlâ koşmuyor, artık atlanıyor. Yani uç nokta
çözümlemesinin doğruluğu yalnız yerelde sınanıyor; CI'ın gördüğü şey "bu test bu
ortamda koşamaz" bilgisi. Kapanma yolu CI'da `appworld install` koşturmak, ve
bedeli 198 MB veri indirmek.

## S-48 — İndeksin en sık kalıbı hiçbir görev tarafından getirilemiyor

> **İddiayı sınırlıyor.** PILOT_REPORT.md — getiricinin kapsama oranı

> **Kapanma sınıfı.** Ölçüldü — en sık kalıp hiçbir göreve düşmüyor; sebep sembol uzayının yapısı

`GET api_docs.api_descriptions` (422, **150 hata**) indeksteki en yüksek sayılı
kalıp. Getirici onu hiçbir göreve vermiyor: sembol uygulama ve `api_docs` altyapı
listesinde, altyapı da getiricide düşüyor (K-86). Ölçüldü: 315 görevin
hiçbirinde getirilmiyor, 15 kalıbın 14'ü getirilebiliyor
(`results/card-tokens.json`, `unreachable_rows`).

**Bu kalıp özelinde iyi haber.** S-45'in tesadüfi koşula dayanan kartı tam olarak
bu kart: ayıran tek koşulu başka bir uygulamaya ait ve gerçek sebebi
söylemiyor. Yani şüpheli kart yapısal olarak modele ulaşamıyor.

**Ama kural olarak bir kayıp.** Altyapı uygulamalarında gerçekten öğrenilebilir
bir arıza bilgisi varsa o da ulaşamıyor, ve indeksin boyutu bu yüzden getiricinin
ulaşabildiği boyuttan büyük görünüyor. Terk kriteri "indeks ilan edilen asgari
boyutta" diyor (`05-experiment-design.tr.md`); doğru okuma **getirilebilir** kalıp
sayısı, indeks satır sayısı değil.

**Kapanma yolu iki tane ve ikisi de karar gerektiriyor**: altyapı kartlarının
koşulsuz olarak her göreve verilmesi (o zaman ayırt edicilik ölçümü bozulur), ya
da `api_docs` 422'lerinin gerçek sebebini ifade edebilen bir koşul biçimi
(S-40'a bağlı, yanıt gövdesi gerekiyor).

## S-47 — Bağlayıcı bağlam sınırı jeton penceresi değil, iskelenin karakter tavanı

> **İddiayı sınırlıyor.** 03-architecture — bağlam bütçesinin 32K jeton olduğu

> **Kapanma sınıfı.** Dış olgu — 50000 karakterlik tavan referans iskelenin içinde ve K-19 onu dondurdu

Bağlam bütçesi 32K jeton olarak konuşuluyor ama referans iskele bağlamı
**karakterle** kesiyor: `max_prompt_length` 50000 ve kesme iskelenin kendi
içinde (S-07). İki sınır farklı birimde ve hangisinin bağladığı hiç
ölçülmemişti.

**Ölçüldü** (`results/context-cost.json`): gerçek kayıt içeriğinde 50000 karakter
**12799 jeton**, yani 3,91 karakter/jeton ve 32K pencerenin **%39'u**. Sabit blok
kartlarla birlikte ~3400 jeton, yani %10. Aradaki fark geçmişe kalıyor ama
geçmişin kendisi karakter tavanına çarpıyor: pencere hiçbir zaman dolmuyor.

**Sonucu iki tane.** Bağlam taşması (K-36'nın üçüncü kategorisi) bu
yapılandırmada jeton penceresinden gelemez; kayıtta sıfır bağlam taşması
görülmesi bununla tutarlı. Ve bağlam montajcısı devreye girdiğinde bütçesini
jetonla değil karakterle yazmak zorunda kalacak, ya da iskelenin kesme mantığını
devre dışı bırakmak zorunda kalacak — K-26'nın açık bıraktığı çakışma tam
burada.

**Tavan bağladı, ve bu ölçüldü.** Kayıtlı 105 epizodun **31'i** 50000 karakteri
geçti; en erken 9. adımda, kesilen epizotlarda medyan 19. adımda. Kesme geçmişin
**başını** atıyor (yönerge bloğu korunuyor, kuyruk korunuyor), yani korpusun üçte
birinde ajan kendi erken adımlarını bir noktadan sonra görmedi. Ölçüm bir alt
sınır: mesaj çerçeveleri (rol satırları, kod bloğu işaretleri) sayılmadı, yani
gerçek prompt bundan biraz uzun ve kesme biraz daha erken başladı.

**Kütüphane ve indeks bundan etkilenmiyor**, çünkü ikisi de kayıttan
madencilendi, prompt'tan değil. Etkilenen şey yörüngelerin kendisi.

**Değer bizim, referansın değil.** Tavan ajanın kurucu parametresi ve referansın
bu ajan için verdiği değer `null`, yani kesme yok: yayımlanan 108
`simplified_react_code_agent` yapılandırmasının 108'i öyle. 50000 legacy
`plan_execute` ailesinden geliyor ve 10 Ağustos'ta yürütücüye karar kaydı olmadan
girdi. Artık `config/recording.yaml` içinde, künyede ve devam denetiminin reddet
listesinde (K-90).

**Ölçümün kendi sınırı.** 3,91 karakter/jeton oranı kayıttaki kod ve gözlem
metninden geliyor. Başka bir içerik dağılımı — daha çok JSON, daha çok İngilizce
düzyazı — başka bir oran verir; sayı bu korpusa özgü.

## S-46 — Mimari belgesindeki sabit blok payı ölçülmemişti ve yanlıştı — DÜZELTİLDİ

> **Sınıflandırılmadı.** aynı sınıf

`03-architecture.tr.md` şunu yazıyordu: "Adım başına yaklaşık 5958 girdi tokenı.
Sabit blok 32K bütçenin kabaca beşte biri, kartlarla birlikte dörtte biri."

**İkinci cümle yanlıştı.** Ölçüldü: sabit blok medyan **3172–3185 jeton**, yani
pencerenin **%9,7'si**; kartlarla birlikte %10,1–10,5. Beşte bir yerine onda bir,
dörtte bir yerine yine onda bir.

**Yanlışın kaynağı bir birim karışması, kötü bir tahmin değil.** 5958 sayısı
Aşama 2'de ölçüldü ve **adım başına girdi jetonu**, yani birikmiş konuşma
geçmişini de içeriyor. Sabit blok ondan bağımsız bir büyüklük ve hiç ayrı
ölçülmemişti; iki sayının farkı geçmişin kendisi.

**Nasıl yakalandı.** Kartların üstüne bineceği taban ölçülmek istendi ve taban
ölçüldüğünde iddiayla uyuşmadı. Yani yakalayan şey, kartların maliyetini
sormanın kendisi oldu — belgeyi yeniden okumak değil.

**Düzeltildi.** Belgedeki cümle ölçülmüş sayılarla değiştirildi ve ölçümün
kaynağı yazıldı. Karar kaydı K-88.

## S-45 — İndeks kartlarının koşulu tesadüfen ayırabiliyor, ve kart bunu kendi üstünde taşıyor

> **İddiayı sınırlıyor.** K-85 — indeks kartlarının koşulunun ayırt edici olduğu

> **Kapanma sınıfı.** Ölçüldü — ayırt ediciliğin tesadüfi olabildiği bu korpusta gösterildi; kart bunu üstünde taşıyor

Koşul, her başarısızlıkta tutan ve hiçbir başarıda tutmayan bir yüklem olarak
seçiliyor. Aday uzayı alfabedeki her çağrının varlığı ve yokluğu — bu korpusta
**92 aday**. Başarısızlık grubu küçükse bir yüklem **tesadüfen** ayırabiliyor.

**Ölçüldü.** Koşul taşıyan 13 kartın 12'sinde ayıran koşul çağrının kendi
uygulamasına ait, yani nedensel olarak okunabiliyor ("önce giriş yap"). Birinde
(`GET api_docs.api_descriptions`, 422, 150 hata) ayıran tek koşul **başka bir
uygulamaya** ait: "önce `simple_note.profile` çağrılmış olması". Bu bir
korelasyon, sebep değil. O 422'lerin gerçek sebebi `app_name` argümanının
**değeri**, ve K-83 gereği değerler kalıba girmiyor.

**Sayı düzeltmesi.** Bu paragraf ilk yazıldığında "15 kartın 14'ünde" diyordu ve
o hâliyle K-85'ten önceki duruma aitti: aynı commit'te karşıt başarısı olmayan
iki kalıbın koşulu kaldırıldı, yani koşullu kart sayısı 15 değil 13. Bölen
değişti, pay değişmedi. Doğrusu yukarıda ve kaynağı
`results/pilot-dataset.json` → `failure_patterns`.

**İkinci tuzak: karşıt başarısı olmayan kalıplarda ayırt etmek boş bir iddia.**
Karşılaştırılacak başarı yoksa her uygun koşul trivial olarak ayırır.
`POST splitwise.auth/logout` kartında **59** koşul ayırıyor; seçim tamamen
keyfî.

**Çözüm silmek değil, işaretlemek.** Kart iki tanı alanı taşıyor:
`discriminating_count` (kaç koşul ayırdı) ve `own_app_condition` (seçilen koşul
çağrının kendi uygulamasına mı ait). İkisi de `body_write` ile aynı desen: fazla
dahil etme raporun içinde değil ürünün içinde görünüyor ve sorgulanabiliyor.

**Neden bir "aynı uygulama" kuralı konmadı.** Konabilirdi ve iki şüpheli kartı
düşürürdü. Ama nedensellik kısıtı koşul dilinin bir parçası değil, ve dile
sessizce eklenmiş bir kısıt K-83'ün kapalılık gerekçesini zayıflatır. Karar
verilmedi, ölçüm ve işaret kayda geçti.

## S-44 — `actions.error_class` tek değerli, sinyal durum kodunda

> **İddiayı sınırlıyor.** 07-failure-taxonomy — `error_class` alanının eylem düzeyi sinyal taşıdığı

> **Kapanma sınıfı.** Ölçüldü — 767 başarısız eylemin 767'sinde aynı değer; alan eylem düzeyi sinyal taşımıyor

767 başarısız eylemin **767'sinde** `error_class` değeri `Exception`. AppWorld
her başarısız yanıtta istisna fırlatıyor ve HTTP kodu istisna metninden
ayrıştırılıp `result_status` sütununa yazılıyor.

Yani sütun ayırt edici değil. Taksonominin eylem düzeyi etiketleri
(`07-failure-taxonomy.tr.md`) **`result_status`'tan** okunuyor: 401 → yetki reddi,
422 → geçersiz parametre, 409 → uygun olmayan durum.

`error_class` sütunu kaldırılmadı, çünkü sıfır olmayan bir bilgi taşıyor: bir
çağrının istisnayla mı yoksa hatalı kodla mı döndüğü ayrımı ileride başka bir
taşıma katmanında anlam kazanabilir. Ama bugün üzerine hiçbir ayrım kurulamaz ve
kuranlar sessizce hiçbir şey ayırmaz.

## S-43 — 409 sınıfı v0 indeksinin kapsamı dışında

> **İddiayı sınırlıyor.** 07-failure-taxonomy — koşul dilinin hata sınıflarını ifade edebildiği

> **Kapanma sınıfı.** Ölçüldü — 34 `409`ın hepsi tek uçta ve sebep nesne durumu; koşul dili bunu ifade edemiyor

Kayıtlı 34 `409` hatasının hepsi tek uçta: `POST venmo.transactions`. Sebebi
nesne durumu — bakiye yetersizliği gibi bir çakışma — ve koşul dilinin bunu
ifade eden biçimleri (nesne varlığı, nesne alan değeri) **gözlenemiyor**, çünkü
çağrı yanıt gövdesi kayda yazılmıyor (S-40).

v0 indeksi `401` ve `422` sınıflarını kapsıyor. 409 için üretilen kart, kendi
uygulamasına ait bir koşul bulsa bile gerçek sebebi söylemiyor; S-45'in
işaretleri onu görünür kılıyor.

Kapanma yolu S-40 ile aynı: yanıt gövdesini kalıcı hâle getirip yeniden koşmak.
Bu korpusa uygulanamıyor (S-16).

## S-42 — Bağlılık epizot boyunca aranıyordu, gövde içinde değil — DÜZELTİLDİ

> **Sınıflandırılmadı.** aynı sınıf

`06-skill-language.tr.md` bağlı argümanı "değeri **dizinin içinde** daha önceki bir
çağrının çıktısında geçiyor" diye tanımlıyor, ve dizi becerinin kendi gövdesi.
İlk uygulama epizodun tamamındaki önceki gözlemlerde arıyordu.

**Sonucu ölçüldü ve ciddi.** Boşluk 2 / destek 3'te en yüksek destekli beceri
şuydu:

    GET api_docs.api_doc
    POST venmo.auth/token

Gövdede `supervisor.account_passwords` **yok**. Buna rağmen `password`,
`username`, `app_name` ve `api_name` dördü de bağlı sayılıyordu, çünkü değerler
epizodun daha önceki bir adımında yazdırılmıştı. Derlenmiş beceri parametresiz
çıkardı ve çalışma anında o değerlerin hiçbirini elde edemezdi: gövde atomik
koşuyor, boşluğun atladığı çağrılar hiç çalışmıyor.

**Bu, atlanan çağrı sorusunun ikinci yüzü.** Aynı ölçüm ikisini birden çıkardı:
bir beceri, atladığı çağrıların ürettiği hiçbir şeye bağlı olamaz.

**Düzeltildi.** Bağlılık yalnız **oluşumun kendi adımlarının** çıktısında
aranıyor. Sayılar: bağlı argüman 22'den 13'e, serbest parametre 5'ten 14'e.
Beceriler artık ihtiyaç duydukları şeyi imzalarında ilan ediyor. Venmo giriş
becerisi kimlik bilgilerini parametre olarak istiyor; spotify becerisi
`account_passwords` çağrısını gövdesinde taşıdığı için parolası bağlı kalıyor,
yalnız kullanıcı adı serbest.

**Kalan bulaşma.** Bir adım hem gövde çağrısı hem başka çağrı taşıyorsa,
gözlemi ikisinin çıktısını da içeriyor. Bu, son koşul atfındaki bulaşmanın
(K-79) aynı sınıfı ve aynı yerde kapanacak.

## S-41 — Son koşulların çoğu v0'da boş, çünkü atıf yalıtım gerektiriyor

> **İddiayı sınırlıyor.** SKILL_SPEC.md — becerilerin son koşul taşıdığı

> **Kapanma sınıfı.** Ölçüldü — K-79 atfı tek çağrılı adımlarla sınırlıyor; boş son koşullar o kararın bilinen bedeli

Son koşul, destekleyen epizotlarda gözlenen durum farklarının şekil kesişimi
(`SKILL_SPEC.md`). Atıf yalnız **tek çağrı yapmış adımlardan** okunuyor (K-79):
çok çağrılı bir adımda farkın hangi çağrıdan geldiği bilinemez.

**Ölçülmüş taban.** Kayıtlı 22 geçen epizotta 454 adım var; 16'sı durum farkı
taşıyor ve **8'i tek çağrılı**. Yani atfedilebilir gözlem sayısı sekiz adımla
sınırlı.

**Ölçülmüş sonuç.** Boşluk 2 / destek 3 yapılandırmasında madencilenen 40
becerinin **39'unun son koşulu boş**, biri dolu
(`{venmo.PaymentRequest: +, venmo.Notification: +}`).

**Boşluğun iki farklı sebebi var ve karıştırılmamalı.**

1. **Giriş ailesi gerçekten durum değiştirmiyor.** `auth/token` çağrısı 213 tek
   çağrılı adımda sıfır fark üretti. Bu bir ölçüm eksikliği değil, olgu: giriş
   jeton üretiyor, satır üretmiyor. Etki soneki dolu, son koşul boş, ve şartname
   buna izin veriyor.
2. **Satır sayımı güncellemeyi görmüyor.** Yalnız alan düzeyinde yazan bir
   beceri boş son koşul üretecek. Bu yazma kümesini sınırlayan kör noktanın
   aynısı ve ikisi `model_hashes.json` katmanıyla birlikte kapanıyor.

**Etkisi.** Boş son koşullu becerilerde yürütme sonrası doğrulama dalı
çalışmıyor, getirmede alaka katkısı yok, ve düşürme kuralının ikinci sayacı
(`postcondition_misses`) hiç artmıyor. Yani bu becerilerde son koşul
mekanizmasının üç kullanımı da ölü.

**Neyin değişmesi gerekir.** Adım başına çağrı sayısı iskelenin davranışı ve biz
onu değiştirmiyoruz (K-19). Kapanış yolu ampirik yazma kümesiyle aynı:
epizot kapanışında model karması. Korpus büyürse tek çağrılı adım sayısı da
büyür, ama oran değişmez.

## S-40 — Bağlı argüman tespiti ajanın yazdırdığı kadarıyla sınırlı

> **İddiayı sınırlıyor.** 06-skill-language — bağlı argüman tespitinin yapısal yol eşleşmesiyle yapıldığı

> **Kapanma sınıfı.** Sonraki tur — S-16'nın yanıt enstrümantasyonu inerse tespit yüzeyi genişler

Şartname bağlı argümanı "değeri dizinin içinde daha önceki bir çağrının
çıktısında geçiyor, yapısal yol eşleşmesiyle tespit ediliyor" diye tanımlıyor
(`06-skill-language.tr.md`). **Çağrı yanıt gövdesi veritabanına yazılmıyor.**
`ApiCapture` onu çalışma anında yakalıyor ama `write_steps` yalnız durum kodunu
ve hata sınıfını saklıyor; S-05 durum kodunu düzeltti, gövdeyi değil.

**v0 gözlem metnini kullanıyor.** İskelenin deseni `print(apis.<app>.<api>(...))`
olduğu için ajanın sonra kullandığı değerler gözlemde görünüyor. Tespit metin
içermesiyle yapılıyor, yapısal yol eşleşmesiyle değil.

**Hata tek yönlü.** Yazdırılmadan kullanılan bir değer **serbest görünüyor**.
Yani sınıflandırma eksik tespit ediyor, fazla tespit etmiyor. Yön önemli: fazla
tespit bağlı olmayan bir argümanı gövdeye gömer ve beceriyi bozar; eksik tespit
yalnız imzayı gereksiz uzatır.

Kısa değerler için bir alt sınır var (üç karakter), çünkü `1` ve `on` her
gözlemde geçiyor. Bu da eksik tespit yönünde çalışıyor.

**Ölçüldü.** Boşluk 2 / destek 3'te 40 becerinin argümanlarından 270'i bağlı,
50'si serbest parametre olarak sınıflandırıldı. Giriş becerilerinde `password`,
`username`, `app_name` ve `api_name` bağlı çıkıyor — beklenen sonuç, çünkü
üçü de daha önceki bir `api_docs` ya da `supervisor` çağrısının çıktısından
geliyor.

**v1 yolu.** Yanıt gövdesini kalıcı hâle getirmek ve yeniden koşmak. Bu korpusa
uygulanamıyor: toplama tek seferlik (S-16) ve yeniden koşmak korpusu
değiştirir. Karar, bağlılığı hiç aramamanın seçenek olmamasıyla verildi —
şartname tam da bunun için uyarıyor: bağlı argümanlar parametre sanılırsa
çağıranın işin yarısını zaten bilmesi gerekir ve beceri değersizleşir.

## S-38 — Yazma kümesi türetmesi `@app.delete` süslemesini yazma çağrısı sanıyordu — ÇÖZÜLDÜ, ve bilinen bir fazla dahil etme bıraktı

> **Sınıflandırılmadı.** aynı sınıf

**Defekt.** Türetme her uç noktanın gövdesini `ast.walk` ile geziyor ve `.delete(...)`
biçiminde bir çağrı arıyor. `ast.walk` bir `FunctionDef`'in **süsleme listesini
de** geziyor, ve bütün DELETE uçları `@app.delete("/yol")` ile süsleniyor. Yani
her DELETE ucu, gövdesinde ne olursa olsun, yazar sayılıyor.

**Ölçüldü: dokuz uç yalnızca bu kaza sayesinde kümede.**

    amazon.delete_account        gmail.delete_account       splitwise.delete_account
    phone.delete_account         simple_note.delete_account spotify.delete_account
    file_system.delete_account   todoist.delete_account     venmo.delete_account

Gövdeleri yazma fiili içermiyor, çünkü hepsi `_delete_account(...)` adlı
paylaşılan bir yardımcıya devrediyor ve o yardımcı `apis.py` içinde değil.

**Cevap doğru, gerekçe yanlış.** Bir hesabı silmek elbette yazma. Ama kümede
oluşlarının sebebi gövdelerindeki kanıt değil, rota süslemesi. Süsleme sızıntısı
tek başına düzeltilirse bu dokuz uç kümeden **düşer** ve kalkan bütün yüzeydeki
en yıkıcı işlemi koşulsuz geçirir.

**Modül-içi yardımcı izlemek kurtarmıyor, ölçüldü.** Bir ve üç seviye izleme de
denendi; dokuzu da düşmeye devam ediyor, çünkü `_delete_account` modülde değil.
Buna karşılık izleme yedi uç **ekliyor** (`file_system.move_file`,
`move_directory`, `gmail.reply_to_email`, `splitwise.settle_up`, ve üç
`todoist.show_*`), ve son üçü ayrıca incelenmeli.

**Neden açık bırakıldı.** Düzeltmenin doğru biçimi türetmenin yöntemini
değiştiriyor: paylaşılan kütüphaneyi de taramak mı, süsleme sızıntısını düzeltip
DELETE yöntemini ayrı bir kural olarak eklemek mi, yoksa dokuzunu elle mi
sabitlemek. Üçü farklı kümeler üretiyor. Karar verilmeden dokunulmadı.

**Bugünkü durum güvenli tarafta.** Küme dokuz yıkıcı ucu içeriyor. Risk
düzeltmeyi yarım yapmakta.

### Önerilen dördüncü yol ölçüldü: olduğu gibi konamaz

Öneri şuydu: sızıntı kapatılsın, ve HTTP yöntem semantiği açık kural olsun —
POST, PUT, PATCH, DELETE yazar sayılır, gövde taraması yalnız GET için koşar.

Kuralın gerekçesi sağlam: bir DELETE ucunun durum değiştirmesi kaza değil,
protokolün anlamı, ve bugün o doğru cevabı süsleme sızıntısı üzerinden almak
doğru sonuca yanlış yoldan varmak. Ama iki ölçüm kuralı olduğu gibi sabitlemeye
karşı çıkıyor.

**Birinci ölçüm.** Sızıntı kapatıldıktan sonra gövdesinde hiç yazma bulunmayan
GET dışı uç sayısı 302'de **82**. Küçük değil. İçinde POST ile *okuyan* uçlar
da var: `admin.show_card_balance` ve `admin.validate_card` gövdelerinde
`find_one` yapıp değer döndürüyor.

**İkinci ölçüm, aritmetik.** Bugünkü 242 sayısı "GET dışı artı 12 GET yazarı"
**değil**:

| | |
|---|---|
| Adlandırılmış API | 478 |
| Yalnız GET | 176 |
| GET dışı | 302 |
| Bugün yazar | 242 = 230 GET dışı + 12 GET |
| Kural üretecek | 314 = 302 + 12 |

Yani kural 72 uç ekliyor, düşen sıfır. Etkisiz bir gerekçe düzeltmesi değil,
kümeyi %30 büyüten bir değişiklik.

**Ve bloker: yanlış pozitif %4,1'den %24,5'e çıkıyor.**

| Küme | Yazan anahtar | Yanlış pozitif |
|---|---|---|
| Bugün | 242 | 6/147 = %4,1 |
| Dördüncü yol | 314 | 36/147 = **%24,5** |
| Dördüncü yol eksi `login`/`logout` | 296 | 6/147 = %4,1 |

Sebep tek bir uç. `phone` 0 kaçaktan 30'a çıkıyor ve otuzunun otuzu da aynı
çağrı: `POST auth/token`, yani **giriş**. Ajan bir uygulamadan *okumak için*
önce giriş yapmak zorunda ve giriş bir POST. Kural olduğu gibi konursa giriş
yazma sayılır, kaçırılan uygulamaya giriş engellenir, ve okuma dolaylı yoldan
kesilir. K-69 — "okuma koşulsuz serbest" — pratikte yanlış olur: okuma bir
giriş kapısının arkasında koşulluya döner. Ölçüm tam olarak %24,5'e, yani
K-72'nin ayırdığı uygulama kümesi hata oranına geri dönüyor.

`login` ve `logout` dışarıda bırakılırsa kural çalışıyor ve yanlış pozitif
%4,1'de sabit kalıyor.

### Uygulanan kural

**GET dışı yöntemler yazar, oturum uçları hariç, gövde taraması yalnız GET
için.** Sınır geçen yardımcı taraması yöntemden bağımsız olarak her uçta koşuyor.

**İstisnanın gerekçesi K-69'dan türüyor, ölçümden değil.** K-69 okumayı
koşulsuz serbest bırakıyor. Giriş, okumanın ön koşulu: ajan kimlik doğrulaması
yapmadığı bir uygulamadan okuyamıyor. Dolayısıyla giriş yazma sayılırsa,
çıkarımın kaçırdığı uygulamaya giriş engellenir, arkasındaki okuma da onunla
birlikte ölür, ve K-69 uygulanamaz hâle gelir. İstisna bu türetmeden geliyor.
Sayı türetmeyi **doğruluyor**, üretmiyor. `logout` girişin çifti: bir oturum
jetonunu düşürüyor, kullanıcı verisine dokunmuyor, ve engellenmesi hiçbir şeyi
korumadan oturumları açık bırakırdı.

**Kabul gerekçesi hata yönü.** Bir güvenlik mekanizmasında iki hata yönü simetrik
değil. Okuyucuyu yazar saymak meşru bir okumayı engelliyor ve bunun marjinal
maliyeti **ölçüldü: sıfır** — yanlış pozitif %4,1'de kaldı. Yazarı okuyucu
saymak gerçek bir yazmayı denetimsiz geçiriyor. Fazla dahil etmek güvenli yön.

### Bilinen fazla dahil etme

GET dışı 284 ucun **64'ünün** gövdesinde hiçbir yazma çağrısı yok ve hepsi
kümede. İkisi doğrulanmış okuyucu:

| Uç | Yöntem | Gövdesi |
|---|---|---|
| `admin.show_card_balance` | POST | `_validate_card`, `PaymentCard.find_one`, bakiye döndürüyor |
| `admin.validate_card` | POST | `_validate_card`, boolean döndürüyor |

İkisi de kümede duruyor ve `body_write: false` alanı bunu uç bazında kayda
geçiriyor, yani fazla dahil etme raporun içinde değil ürünün içinde görünür.

Kalan 62 çoğunlukla hesap yaşam döngüsü (`signup`, `verify_account`,
`reset_password`, `send_verification_code`, `update_account_name`) ve
paylaşılan bir yardımcıya devreden uçlar; onlar gerçekten yazıyor, statik tarama
yalnız göremiyor.

### Kazanç

Dokuz `delete_account` artık kazayla değil, ilan edilmiş kuralla kümede.
Kümeye ayrıca `file_system.move_file`, `file_system.move_directory`,
`gmail.reply_to_email`, `splitwise.settle_up` ve bütün hesap POST'ları girdi:
242 → **296** yazar.

**Sınır geçen yazar 16'dan 19'a çıktı, ve üç yeni üye bu fazla dahil etmenin
sonucu.** Yeniler `amazon.add_payment_card`, `spotify.add_payment_card`,
`venmo.add_payment_card`; üçü de `admin`'e yazar sayılıyor. Sebep zincirin
başındaki iki okuyucu: kart yardımcıları `request_payment_card_balance` ve
`request_payment_card_validation`, `admin.show_card_balance` ve
`admin.validate_card` uçlarını çağırıyor, o ikisi POST olduğu için yöntem
kuralıyla yazar sayılıyor, ve hedef yazar sayılınca yardımcı de sınır geçen
yazma sayılıyor.

Yani bu üç üye yeni bir yazma kanıtı değil, bilinen fazla dahil etmenin bir
adım ötesi. **Pratik etkisi sıfır**: `admin` bir altyapı uygulaması
(`INFRASTRUCTURE_APPS`) ve izinli kümede her zaman var, dolayısıyla bu üç uç
hiçbir görevde engellenmiyor.

Ve türetmenin kırılgan yarısı — fiil adı eşleştirme ile delegasyon körlüğü, bu
oturumda iki kez ısıran şeyler — artık yalnız 176 GET ucuna uygulanıyor.

## ~~S-37 — `update` bir model fiili değil, ve iki saf okumayı yazar yaptı~~ — KAPANDI: `update` yazma fiili kümesinden çıkarıldı

**Kapandı, 18 Ağustos 2026.** Ölçüt uygulandı.

**Kapanma ölçütü: ölçüldü ve cevap geldi.** Kayıt zaten ölçümü taşıyordu:
`update` bütün yüzeyde iki kez geçiyor, ikisi de saf okuma, hiçbir model sınıfı
onu tanımlamıyor.

**Kanıt.** `scripts/setup/derive_write_set.py` içindeki `WRITE_METHODS`
kümesinde `update` **yok** (arandı, sıfır eşleşme).

**Neyin kapanmadığı.** Kalan sekiz fiilin her birinin gerçek kullanımı ayrı ayrı
doğrulanmadı; bu kayıt yalnız birini ölçtü.

`WRITE_METHODS` kümesinde `update` vardı. Türetme alıcının türünü bilmiyor,
yalnız öznitelik adına bakıyor, ve `update` hem Python `set`/`dict` metodu hem de
akla yatkın bir model fiili.

**Ölçüm kesin.** `update` bütün yüzeyde iki kez geçiyor:

    phone.show_contact_relationships   relationships.update(...)   -> bir set
    todoist.show_projects              project_dict.update(...)    -> bir dict

Hiçbir model sınıfı `update` tanımlamıyor ve `callers.py` onu hiç çağırmıyor.
Yani dokuz fiilden biri **sıfır** gerçek kullanıma sahipti ve iki yanlış pozitif
üretiyordu. Kalan sekiz adda böyle bir çakışma yok: Python kaplarında `save`,
`create`, `delete_all`, `create_save` diye bir şey yok.

**Etkisi gölge modunda görüldü.** İkisi de saf okuma, ve
`phone.show_contact_relationships` gölge koşusunun sekiz engellemesinden ikisini
üretiyordu — kalkanın tam da yapmaması gereken şey, bir okumayı kesmek.

**Nasıl bulundu.** Gölge modu koştuktan sonra engellenen çağrılara tek tek
bakıldı. Sayıya bakmakla görünmezdi: %0,09 engelleme oranı zaten küçüktü ve
"küçük demek doğru demek" değil.

**Düzeltme, 15 Kasım 2026.** Sekiz engellemeden biri bir testin kendi açtığı nottu
(S-83). Onsuz ilk koşu 9145 çağrıda 7 engelleme, %0,08. İki saf okuma bulgusu
değişmiyor.

**Düzeltildi.** `update` kümeden çıkarıldı, yazar uç sayısı 244'ten 242'ye,
GET yazarları 14'ten 12'ye indi. `download_*` sayısı dokuzda kaldı — K-41'in
taşıyıcı yarısı kıpırdamadı.

## ~~S-36 — İki rota şablonu aynı yolu eşliyor, çözümleyici yanlış cevap veriyordu~~ — KAPANDI: rota çözümlemesi yöntem duyarlı

**Kapandı, 18 Ağustos 2026.** Ölçüt uygulandı.

**Kapanma ölçütü: ölçüldü ve cevap geldi.** Çözümleyici yalnız yola bakıyordu;
artık HTTP yöntemini de alıyor.

**Kanıt.** `src/zihin/api_routes.py` yöntem alanını çözümlemenin içinde taşıyor,
ve `scripts/setup/verify_wire_identity.py` kayıttaki her eylemi telden geçirip
geri kuruyor — imzalı kolun eşleşmesi bu çözümlemenin doğruluğunu ölçüyor,
imzasız kontrol kolu da ölçümün boş olmadığını gösteriyor.

**Neyin kapanmadığı.** Ölçüm kayıttaki eylemler üzerinde. Kayıtta hiç görülmemiş
bir yol/yöntem çifti sınanmadı.

`phone` uygulaması iki çift şablon taşıyor ve her çiftin regexleri **aynı
dizeyi** eşliyor:

    GET, DELETE  /messages/text/{text_message_id}
    POST         /messages/text/{phone_number}

ve sesli mesajda aynısı. `route_template()` yalnız yola bakıyordu ve ilk
eşleşeni döndürüyordu, yani `POST /phone/messages/text/3155673041` — bir telefon
numarası — `{text_message_id}` şablonuna çözülüyordu.

**Nasıl bulundu.** Kalkanın fail-open dalı ölçülürken. Yazma kümesi 478
adlandırılmış API'nin 478'ini kapsıyordu, yani hiçbir çağrının bilinmeyen uca
düşmemesi gerekiyordu; ama 5213 kayıtlı çağrının 26'sı düşüyordu. Çelişki
çözümleyiciyi işaret etti.

**Etkisi ölçüldü ve bu korpusta latent.** Düzeltmeden sonra 26 çağrının 26'sı
`write_within_allowed_apps` sınıfına geçti, yani **kalkanın kararı değişmiyor**:
iki hâlde de izin. Defekt bu korpusta aktif bir yanlış karar üretmedi.

Önemi genel vakada. O uç `phone`'a yazıyor; `phone`'un izinli olmadığı bir
görevde doğru karar **ret** olurdu ve bilinmeyen uç dalı çağrıyı geçirirdi. Bu
korpusta o kombinasyon oluşmadı, ama kalkanın kapsamındaki delik gerçek.

**Düzeltme.** Çözümleme yöntemi de alıyor. Çiftlerin yöntemleri ayrık olduğu
için ayrım kesin. Yol eşleşip hiçbir rota o yöntemi kabul etmiyorsa cevap None:
bu bir 405, "bulamadığımız uç" değil.

Düzeltmeden sonra bilinmeyen uç 26'dan **sıfıra** indi ve 26 çağrı doğru sınıfa
(`write_within_allowed_apps`) geçti; okuma ve sınır geçen yazma sayıları
değişmedi.

**Etki alanı tarandı.** Çözümleyiciyi yalnız `endpoint_identity` kullanıyor ve
onu da yalnız `episodes.distinct_endpoints` tanı sütunu besliyor. Durma
kuralının PATH+PARAM kimliği ve `distinct_resources` çözümleyiciden **geçmiyor**,
ikisi de `split_endpoint`'ten gelen somut yolu kullanıyor. Kayıtlı hiçbir sayı
etkilenmedi: sütun eklendikten sonra henüz epizot koşulmamış.

**Sınıfı S-32'nin akrabası.** Çözümleyici sessizce yanlış cevap veriyordu ve
hiçbir şey itiraz etmiyordu. Yakalayan şey iki bağımsız sayının çelişmesiydi.

## S-35 — Yazma kümesinin iki kaynağı bir uçta anlaşmıyordu — KAPANDI: K-41 fazladan saydı

Yazma kümesinin statik yarısı yeniden türetildi
(`scripts/setup/derive_write_set.py`, çıktı `inputs/write-set-static.json`) ve
K-41'in kayıtlı bulgusuyla **bir uç** farkla uyuştu.

| Ölçüt | K-41 | Yeniden türetme |
|---|---|---|
| Yazan GET ucu | 15 | 14 → **12** |
| Bunlardan `download_*` | 9 | **9** |
| Türetilmiş alan grubu | 2 | **2** → 0 |
| Tembel ilklendirme grubu | 4 | 3 |

Uyuşmayan uç: `splitwise.show_group_balance`.

**Ok işaretli iki satır sonradan düzeldi ve fark açıklandı.** S-37 `update`
fiilini kümeden çıkardı; düşen iki uç `phone.show_contact_relationships` ve
`todoist.show_projects` idi, yani "türetilmiş alan" grubunun tamamı. İkisi de
saf okuma. Böylece K-41'in 15'i ile bugünkü 12 arasındaki üç ucun **ikisi
açıklandı**: onlar hiç yazmıyordu. Geriye tek belirsiz uç kalıyor, aşağıdaki
`splitwise.show_group_balance`.

**Yeniden türetme iki hatamı da buldurdu ve düzeltildi.** Birincisi yolu anahtar
almak: `splitwise` makbuz indirme ucu yolunu bir DELETE ile paylaşıyor, yani
"yalnız GET" filtresi bir GET yazıcısını eliyordu. AppWorld'ün birimi
adlandırılmış API, kalkanınki de o. İkincisi uygulama sınırını geçen her çağrıyı
yazma saymak: `does_file_exist` ve `enlist_files` de sınırı geçiyor ama okuyorlar.

**Statik bakış.** `show_group_balance` gövdesinde hiçbir yazma çağrısı yok;
çağırdığı tek yerel fonksiyon `check_authorization_to_group` ve o da yazmıyor.
Bütün çağrıları okuma: `find_all`, `by_ids`, `by_id_or_raise`.

**Canlı sonda.** Uç üç kez çağrıldı — gruplu iki kez, gruplanmamış bir kez —
ve üçünde de model başına satır sayısı değişmedi. Çağrıların gerçekten koştuğu
ayrıca doğrulandı; ilk denemede giriş sessizce düşmüştü ve sonda "değişmedi"
diyordu, yani sıfır fark tek başına kanıt değil.

**Belirsizlik bir adım daraltılabiliyor ve daraltıldı.** K-41 bu ucu "tembel
ilklendirme" grubuna koymuş. Tembel ilklendirme **satır yaratmak** demek ve
sonda satır yaratımını görüyor. Görmediğine göre geriye iki ihtimal kalıyor: uç
hiç yazmıyor, ya da güncelleme yapıyor.

**İkisinde de K-41'in sınıflandırması yanlış.** Yani belirsiz olan tek şey "hiç
yazmıyor mu, güncelleme mi"; "tembel ilklendirme mi" sorusu kapandı.

Sonuç: tembel ilklendirme grubu dörtten **üçe artı bir belirsize** düşüyor.
Kesin olan üç uç `spotify.show_current_song`, `show_song_queue` ve `show_volume`;
belirsiz olan `splitwise.show_group_balance`.

**Kalkan açısından etkisi düşük.** O uç yazsa bile `splitwise`'a yazıyor, yani
uygulama sınırını geçmiyor; kalkanın birinci aşama yüklemi sınır geçen yazmalara
bakıyor. Dokuz `download_*` ucunun dokuzu da birebir tuttu ve kalkanın var oluş
sebebi olan grup odur.

### Hüküm: K-41 fazladan saydı. Madde kapandı.

Üç kanıt aynı yöne bakıyor ve hiçbiri diğerine dayanmıyor:

1. **Canlı sonda satır değişimi görmedi.** Uç üç kez çağrıldı, üçünde de model
   başına satır sayısı aynı kaldı, ve çağrıların gerçekten koştuğu ayrıca
   doğrulandı.
2. **Gövdenin 149 satırında hiçbir yazma fiili yok.** Tam metin okundu.
   `defaultdict` biriktirmesi, `find_all`, `by_ids`, `by_id_or_raise`, sözlük
   öğe ataması. `.update` bile yok, yani S-37'nin düzelttiği çakışma buraya hiç
   değmiyor.
3. **K-41'in sınıflandırması her hâlükârda yanlıştı.** Ucu "tembel ilklendirme"
   grubuna koymuş; tembel ilklendirme satır yaratmak demek ve sonda satır
   yaratımını görüyor. Görmediğine göre o etiket zaten düşüyordu.

Üçünün ortak açıklaması tek: uç yazmıyor ve K-41 fazladan saydı.

**Kalan belirsizlik ve nerede kapanacağı.** Geriye tek bir ihtimal kalıyor: hem
gövde okumasına hem satır sayımına birden görünmeyen bir ORM güncellemesi —
satır sayısını değiştirmeyen, alan düzeyinde bir yazma. Statik tarama ve satır
sondası tam da bu noktada kör, ve ikisi de kör oldukları için kanıt üretemiyor.
Ampirik yarı (K-41) bunu yakalar, çünkü ölçtüğü şey satır sayısı değil.

Madde süresiz bekletilmiyor. Hüküm verildi, kalan belirsizlik yazıldı, ve
kapanacağı yer belli.

**Kalkan açısından etkisi zaten sıfırdı.** Uç yazsa bile `splitwise`'a yazıyor,
yani uygulama sınırını geçmiyor, ve kalkanın birinci aşama yüklemi sınır geçen
yazmalara bakıyor.

## S-34 — Sınır kontrolü ilan edilen koşulda koşmadı: düşünme açıktı

> **İddiayı sınırlıyor.** sınır kontrolü — “düşünme kapalı” ilanı

> **Kapanma sınıfı.** Sonraki tur — sınır kontrolü ilan edilen koşulda yeniden koşulursa kapanır

Tasarım `docs/05-experiment-design.tr.md` ve K-58'de sınır kontrolünü şöyle ilan
ediyor: "DeepSeek V4 Flash 0731, API üzerinden, **düşünme kapalı**." Koşu
düşünme açıkken yapıldı.

**Mekanizma.** İstek parametrelerinde düşünmeyi kapatan hiçbir şey yok.
Gönderilen alanlar: `name`, `temperature`, `seed`, `max_tokens`, `stop`,
`use_cache`, `retry_after_n_seconds`, `max_retries`, `cost_per_token`,
`api_key`. `reasoning` yok, `thinking` yok. İskele yanıttan `reasoning_content`
**okuyor** ama hiçbir yerde kapatmıyor, dolayısıyla sağlayıcı varsayılanı
geçerli oldu. Canlı ölçüldü: varsayılan çağrıda 146 akıl yürütme jetonu, 466
karakterlik alan.

**S-26 ile bağlantısı sonradan kuruldu.** S-26 dört yüz jetonun bağlayıcı
olmasını ölçmüştü ve sebebini "akıl yürütme aynı bütçeden yiyor" diye yazmıştı.
O cümle ilan edilen koşulun ihlal edildiğinin kanıtıydı ama o zaman
bağlanmadı. Yani bütçenin bağlayıcı olma sebebi de aslında bu ihlal.

**Ne ayakta kalıyor.** Düzenek doğrulaması ayakta: sorusu "herhangi bir model
bu hatta başarabiliyor mu" ve cevap evet, 20/30. Ayakta kalmasının sebebi
sorunun koşuldan bağımsız olması.

**Ne kurulamaz.** "DeepSeek V4 Flash 0731, düşünme kapalı, 20/30" cümlesi
kurulamaz. Sayı düşünen bir modele ait.

**Düzeltme ve maliyeti.** Model şartı sağlıyor: `reasoning={"enabled": False}`
sıfır akıl yürütme jetonu ve boş alan veriyor, üç ayrı soruda tutarlı. Parametre
iskelenin çağrı yolundan geçiyor — `non_cached_lm_call` `reasoning`'i birinci
sınıf parametre olarak taşıyor — ve iskelede tek satır değişmesi gerekmiyor;
`generation_kwargs` sözlüğüne değer koymak yetiyor.

**Doğrulama ölçütü, ölçülerek belirlendi: jeton sıfır VE alan boş, ikisi
birden.** Tek başına sıfır jeton raporu yetmiyor; varsayılan kipte bir çağrıda
`reasoning_tokens=0` dönerken alan 280 karakterdi.

Sınır kontrolünün düşünme kapalı tekrarı aile taramasından sonraya bırakıldı:
tarama yerel `serving_mode` ile koşuyor, barındırılan dalı hiç kullanmıyor.

## S-33 — Makine okunur karar kaydı düzyazı ayrıştırılarak üretiliyor

> **İddiayı sınırlıyor.** experiments/decisions.csv — karar kaydının makine okunur projeksiyonu

> **Kapanma sınıfı.** Sonraki tur — kaynağın yapılandırılmış hâle gelmesi ayrıştırma kırılganlığını kapatır

`experiments/decisions.csv` bir projeksiyon ve kaynağı `docs/08-decisions.tr.md`.
Üretimi düzyazı kalıplarına dayanıyor: bölüm başlıkları (`### K-63 — ...`),
devir ifadeleri (`Cevaplandı, K-28`, `karar K-34'e taşındı`) ve gerekçe
ayırıcısı (`**Gerekçe.**`).

**Yapısal kırılganlık.** Sıradan bir düzyazı düzenlemesi ayrıştırmayı bozabilir.
Başlık düzeyini değiştirmek, ifadeyi yeniden yazmak ya da ayırıcıyı kaldırmak
kayıt kaybına yol açar. Kalıplar ayrıca **Türkçeye bağlı**; belgelerin İngilizce
sürümü çıktığında ayrıştırıcı Türkçe kaynakta kalmak zorunda, aksi hâlde CSV
sessizce boşalır.

Arıza bir kez gerçekleşti: CSV başlık satırına düşmüş, 68 karar satırı
kaybolmuştu ve fark edilmesi bir tura mal oldu.

**Bu aşamada yeniden yapılandırılmıyor.** Kararları yapılandırılmış bir kaynaktan
(YAML ön madde ya da ayrı kayıtlar) üretmek doğru çözüm ama şimdi yapılacak iş
değil.

**Azaltma: tamlık denetimi.** Kaynaktaki her `[KA]-\d+` kimliği CSV'de bulunmak
zorunda; bulunmuyorsa betik CSV'yi **yazmadan** düşüyor. Alt sınırdan güçlü,
çünkü toplam arızayı değil kısmi kaybı da yakalıyor: başlıkların yarısı
bozulduğunda 35 eksik kimlik raporlandı. Kendi kendini de bakımlı, karar sayısı
arttıkça eşik güncellemek gerekmiyor.

Denetimin kalıbı (`\b[KA]-\d+\b`) bilerek Türkçe sözcüklerden bağımsız, yani
**koruma koruduğu şeyden daha az kırılgan.** Alt sınırda bu ayrım yoktu.

## S-32 — Durma kuralının uç nokta ölçütü hiç yürürlükte olmamıştı

> **İddiayı sınırlıyor.** 05-experiment-design — durma kuralının iki ölçütle koştuğu

> **Kapanma sınıfı.** Sonraki tur — kural düzeltildi; kapanma etkilenen ölçümlerin yeniden koşulmasına bağlı

Kural iki ölçütten kuruluydu: adım ya doğrulanabilir durumu değiştirir ya daha
önce dokunulmamış bir API uç noktasına ulaşır, ikisi de yoksa ilerlemesizdir.
İkinci ölçüt hiç çalışmadı.

**Mekanizma.** Kural adımın eylemlerinden `app` ve `api` anahtarlarını okuyordu.
Eylemler `logs/api_calls.jsonl` deltasından geliyor ve o satırların anahtarları
`method`, `url`, `data` — `app` ya da `api` diye alan yok. `.get()` ikisi için de
None döndürdü, her çağrı tek bir sabit kimliğe (`None.None`) eşlendi. İlk çağrılı
adımdan sonra o kimlik "görülmüş" kümesine giriyor, dolayısıyla **sonraki her
adım durgun** sayılıyordu. Kural pratikte "N adım üst üste durum değişmedi"
hâline inmişti.

Bu, `api_capture.py`'nin kendi giriş açıklamasında yazılı olan olguya rağmen oldu:
"`logs/api_calls.jsonl` yalnız `method`, `url` ve `data` taşıyor" (S-05). Bilgi
belgede duruyordu, kod başka bir şey varsayıyordu.

**Kanıt kesim noktalarında.** Sınır kontrolünün kesilen on altı epizodunun on
beşi tam on altıncı adımda kesildi: bir ilerlemeli adım, ardından on beş durgun,
eşik on beş.

**Ölçülmüş sonuç.** `sinir3` koşusu 13/30 verdi; aynı model ve aynı otuz görev
kural olmadan 20/30 veriyordu. Bozuk kural `agent_finished` ile geçen sekiz
epizodu kesti: `024c982_3`, `2d9f728_1`, `3b8fb7a_1`, `b6d1104_3`, `3d9a636_3`,
`0de03ea_3`, `8ce6779_1`, `8ce6779_2`. Dereceli skor 95/152'den 40/152'ye düştü.

**Ne ayakta kaldı, neden.** Bant taramasının 0/30'u ayakta. Sebebi usul: kesilen
yirmi altı epizot kural kapalı olarak tekrar koşulmuştu ve o kontrol uçları
**veritabanından** okuyor, günlükten değil. Veritabanındaki `app`/`api` yakalayıcı
üzerinden yazılıyor ve doğru. Kesim sonrası 1603 adımda sıfır yeni uç, sıfır durum
değişikliği çıkmıştı — üstelik somut yol düzeyinde, yani en cömert tanımla. Kural
kapalı kontrol bir usul gereği olarak konmuştu; bir ölçümü kurtardı.

**Ne düştü.** `sinir3` geçersiz. Eşik kalibrasyonu da geçersiz: hesap günlükten
regex ile kurulmuştu ve **amaçlanan** kuralı ölçüyordu, uygulananı değil. Anlamsız
değildi, yanlış kurala uygulanmıştı.

**Ölçütün taşıyıcı olduğu bu arızayla ölçüldü.** Bozuk kural, uç nokta ölçütü
devre dışıyken geçen epizotların yüzde kırkını kesti. Yani ölçüt olmadan durum
ölçütü tek başına başarıyı taşıyamıyor. S-25'in özgün gerekçesi zayıftı — o
epizodu yakalayan aslında durum ölçütüydü — ama ölçütün kendisi artık kendi
bağımsız gerekçesine sahip.

**Düzeltme.** Uç kimliği AppWorld'ün kendi rota tablosundan geliyor: URL derlenmiş
rota kalıplarıyla eşleniyor ve şablon uç kimliği oluyor (`notes/{note_id}`).
Kimlik türünden bağımsız — `friends/{user_email}` bir e-posta taşıyor ve sayısal
parçaları atan bir buluşsal onu yakalamazdı. Liste ile detay ayrı uçlar olarak
kalıyor. Kayıtlı 239 epizottaki 7138 çağrının 7138'i çözülüyor.

**Düzeltme, 15 Kasım 2026: 239 epizot, 7138 çağrı.** Bu sayının girdi listesi yok ve
sonradan kurulamıyor. Bir testin iki çıktısının bu ölçüme girip girmediği bu yüzden
bilinemiyor (S-83). Bütün çağrıların çözüldüğü iddiası iki durumda da geçerli.

Yöntem kimliğin parçası değil: `GET /transactions` ile `POST /transactions` aynı
uca eşleniyor. Yazan çağrı durumu değiştirdiği için birinci ölçütten geçiyor;
başarısız yazma ise gerçekten durgunluk.

**Sınıfı ve nöbetçileri** `experiments/setup-protocol.tr.md` bölüm 6'da.

## S-23 — Bu model sınıfı için yayımlanmış taban oranlarına tasarımdan önce bakılmadı

> **İddiayı sınırlıyor.** K-58 — ön koşul kapısının tasarım öncesi öngörülebilir olduğu

> **Kapanma sınıfı.** Kalıcı kayıt — tasarımdan önce bakılmamış olmak geri alınamaz; yeni ölçüm bunu değiştirmez

Ölçek ekseni üç yerel kuantalanmış modele kurulurken AppWorld'ün yayımlanmış
taban başarı oranlarına bu model sınıfı için hiç bakılmadı. Kuantalanmış yerel
bir 7B'nin ölçülebilir bir bantta olacağı varsayıldı ve doğrulanmadı. Tasarımın
en başında sorulması gereken soruydu.

Sayılara sonradan bakıldı. `test_normal`, pass@1:

| Model | Görev tamamlama |
|---|---|
| Mistral 7B | %0,0 |
| Qwen3-8B, AWQ 4-bit, 32K bağlam | %3,0 |
| Qwen3-8B, FP16, 12K bağlam | %5,4 |
| DeepSeek-Coder 33B Instruct | %7,1 |
| LLaMA-3-70B-Instruct | %20,8 |
| GPT-4o | %48,8 |

Kaynaklar: <https://arxiv.org/abs/2407.18901> ve
<https://arxiv.org/html/2604.11465v2>.

Bizim birincil modelimiz `qwen2.5-coder:7b-instruct-q4_K_M`, yani 7B ve dört
bit kuantalanmış. En yakın iki yayımlanmış nokta %0,0 ve %3,0. Beklenen taban
oranı sıfır ile birkaç yüzde arasında, ve tasarım bunun üzerine kurulmuştu.

**Etki.** Yüksek, ve tasarımın gövdesine dokunuyor. Taban oranı %2 civarındaysa
ikili başarı üzerinden mekanizma etkisi ölçmek çok büyük örneklem istiyor; bu,
K-55'in çıkarılan nicelik üzerinden güç hesabı kararını gerekçelendiriyor ama
tek başına yetmeyebilir.

**Azaltma.** Bant taraması ve K-57'nin üç yolu. Sınır ön kayda bu hâliyle
giriyor: yayımlanmış tabanlar tasarımdan sonra bakıldı, tasarım kararlarını
etkilemedi, ve örneklem kuralı buna göre yeniden yazıldıysa o da burada yazılı.

## S-24 — Dış inceleme ön koşul sorusunu sormadı

> **İddiayı sınırlıyor.** 10-external-review — dış incelemenin tasarımı denetlediği

> **Kapanma sınıfı.** Kalıcı kayıt — inceleme yapıldı ve o soruyu sormadı; sonraki bir inceleme bunu geri almaz

Tasarım iki tur simüle hakem incelemesinden geçti: beş model, dört jüri rolü.
Hiçbiri "bu modeller bu kıyaslamada bir şey çözebiliyor mu" diye sormadı.
Kaçırılan soru tasarımın en alttaki varsayımıydı ve yanlış çıktı.

Sınır incelemenin kendisinde. Hakem simülasyonu tasarımın iç tutarlılığını
denetliyor: estimand tanımlı mı, sansür kuralı karıştırıcı üretiyor mu, güç
hesabı doğru nicelik üzerinde mi. Bunların hepsi tasarımın içindeki sorular.
Tasarımın dışındaki ön koşul — düzeneğin ölçmeye çalıştığı şeyin var olup
olmadığı — inceleme biçiminin kör noktasında kaldı.

**Etki.** Yüksek, ve geriye dönük değil ileriye dönük. Bu çalışmada ön koşul
artık ölçüldü. Sınırın kalıcı tarafı şu: iç tutarlılık incelemesi geçen bir
tasarım, ölçtüğü şey yoksa yine de boş çıkar.

**Azaltma.** K-58'in ön koşul kapısı. Kapı, aynı hatanın bir sonraki tasarımda
tekrarlanmasını incelemeye bırakmıyor, koşu sırasına yazıyor.

## S-26 — Aynı çıktı bütçesi model ailesine göre aynı koşul demek değil

> **İddiayı sınırlıyor.** sınır kontrolü — aynı bütçenin aynı koşul olduğu

> **Kapanma sınıfı.** Ölçüldü — sınır kontrolünde aynı sayı farklı koşul verdi; olgu model ailelerinin özelliği

`max_tokens` yerel modelde 400. Sınır kontrolünde aynı sayı verildi ve sonuç
yanıltıcı çıktı: DeepSeek V4 Flash akıl yürütme üretiyor, `reasoning_content`
ile `content` aynı bütçeden yiyor, ve bağlam uzadıkça akıl yürütme bütçenin
tamamını alıp içeriği boş bırakıyor.

Ölçülen fark:

| | 400 jeton | 4000 jeton |
|---|---|---|
| Geçen görev | 6/30 | 20/30 |
| Kodsuz adım | 125/501 = %25,0 | 62/902 = %6,9 |
| `no_progress` ile kapanan | 21 | 4 |

Aynı model, aynı görevler, aynı iskele; değişen tek şey çıktı bütçesi. Sayının
kendisi eşitken koşullar eşit değildi.

**Yerel ölçümler etkilenmiyor.** qwen2.5-coder akıl yürütme üretmiyor ve bant
taramasının 958 adımında kodsuz adım sayısı sıfır, yani 400 orada hiç
bağlayıcı olmadı. 7B'nin 0/30'u ayakta.

**Etki.** Yüksek, ve yalnız bu koşuya değil yönteme. Model aileleri arasında
karşılaştırma yapan her ölçüm aynı tuzağı taşıyor.

**Azaltma ve kural.** Eşitlenecek olan sayı değil, bütçenin bağlayıcı
olmaması. Denetim göstergesi kodsuz adım oranı; sıfıra yakın değilse bütçe
bağlayıcıdır ve sonuç bir alt sınırdır. 4000 jetonda oran %6,9 olduğu için
%66,7 de bir alt sınır olarak yazılıyor.

**Bir de yöntem dersi.** Bu tuzağı koşmadan önce fark ettim ve tek görevle
"ölçtüm": on altı adımın on dördü eylem üretti, bütçe yetiyor diye yazdım.
Yetersiz kontroldü, çünkü sorun ilk adımlarda değil bağlam uzadıkça çıkıyor.
Doğru kontrol tek epizodun ilk adımlarına değil, bütün koşudaki kodsuz adım
oranına bakmaktı.

## ~~S-25 — Durma kuralı başarılı okumayı ilerleme sayıyor~~

**Kapandı.** Kural uç nokta kümesi üzerinden yeniden kuruldu: bir adım,
doğrulanabilir durumu değiştirmediyse ve daha önce dokunulmamış bir API uç
noktasına ulaşmadıysa ilerlemesiz. Başarılı çağrı tek başına ilerleme
sayılmıyor.

Kural yazılmadan önce kendi motive edici vakalarında ölçüldü. `09b0ee6_2`'de uç
nokta kümesi dördüncü adımda üç uçta doyuyor ve ardından 146 durgun adım
geliyor; `c77c005_3`'te beşinci adımda dört uçta doyuyor, ardından 87 durgun
adım. İkisinde de kural ateşliyor.

Eşik 4'ten **15**'e çıkarıldı ve iki taraflı kalibre edildi.

Yanlış negatif tarafı yerel taramanın 62 epizodunda ölçüldü; hepsi başarısız ve
patolojik olanların en kısa durgunluğu 13. Ama o küme yalnız başarısızlıkları
ayırdığını gösteriyordu, **başarıyı esirgediğini göstermiyordu.**

Yanlış pozitif tarafı sınır kontrolünün 20 geçen epizodunda ölçüldü. En uzun
durgunluk 12 (`b6d1104_3`): yetenekli bir model ne yapacağını düşünürken aynı
uçları on iki adım boyunca okuyabiliyor. **İlk konan 10 değeri geçen epizotların
ikisini keserdi.**

15 ise geçen epizodun hiçbirini kesmiyor, kalan epizotların 7/10'unu kesiyor, ve
gözlenen en yüksek başarılı durgunluğun üç adım üstünde. 13 ile 17 arasında aynı
sonucu veren bir plato var.

**Ölçümün kendi sınırı.** Sınır kontrolü epizotları JSON'a yazıldığı için adım
düzeyi uç noktalar epizot günlüğünden yeniden kuruldu. Yöntem veritabanıyla
karşılaştırıldı: adım sayıları 30 epizotta birebir aynı, durgunlukta en büyük
fark 4. Sapmanın yönü belli — çağrı yoğun epizotlarda günlük yöntemi durum
değişimini göremediği için durgunluğu fazla gösteriyor, yani 12 bir üst sınır.

**Yanlış negatif tarafındaki maliyet, kayda geçsin diye.** Yerel 62 epizotta
N=13 on sekiz epizot yakalıyordu, N=15 on yedi yakalıyor. Kaçan tek epizot
`13547f5_2`: 20 adım, durgunluk 13.

İkinci ve daha büyük maliyet: eski eşik 4'tü ve 62 epizodun 44'ünün durgunluğu
15'in altında, çoğu tam 4. Bunlar eski kuralla dörtte kesiliyordu, yeni kuralla
tavanlarına kadar koşacaklar. Tarama belirgin biçimde yavaşlayacak.

Öncelik sırası bilerek böyle: **önce geçeni kesme, sonra patolojiyi yakala.**
Kesilen bir başarı geri gelmiyor ve sebebi de bilinmiyor; boşa koşan bir epizot
yalnız zamana mal oluyor.

Değer hâlâ geçici, kesin sayı eşik taramasından çıkacak.

Aşağıdaki özgün metin kayıtta kalması için duruyor.

## S-25 (özgün metin) — Durma kuralı başarılı okumayı ilerleme sayıyor

`_made_no_progress` bir adımı iki koşuldan biri sağlanırsa ilerlemiş sayıyor:
durum farkı boş değilse, ya da çağrılarından en az biri başarılıysa. İkinci
koşul bir kör nokta taşıyor.

Ölçülmüş örnek `09b0ee6_2`: 150 adım, 736 API çağrısı, 736'sının 736'sı 200, ve
150 adımın 150'sinde de `state_change` boş. Ajan her adımda baştan giriş yapıp
aynı çalma listesi kütüphanesini yeniden sayfalıyor. Kural bir kez bile
ateşlemedi, çünkü her adımda başarılı okuma vardı.

Kör nokta "amaçsız durum değişimi" değil, amaçsız **başarılı okuma**. Ayrım
düzeltmeyi belirliyor.

**Etki.** Orta. Bu epizot tavana kadar koştu ve on beş dakika harcadı. Deney
ölçeğinde aynı desen hem bütçe hem de adım tavanı kalibrasyonunu bozar.

**Azaltma denenmedi, çünkü kolay düzeltme yanlış.** Kuralı "durum değişmeli"
diye sıkılaştırmak, salt okuma yapan araştırma evrelerini ve doğrulayıcısı
"assert no model changes" olan cevap görevlerini yanlış keser. Doğru düzeltme
tekrarı yakalamaktan geçiyor: aynı çağrı dizisinin aynı yanıtla tekrarlanması.
Eşik taraması bunu da ölçmeli.

**Tekrar etiketinin merkeziliği ölçüldü.** İki bağımsız yerde aynı desen çıktı:
`09b0ee6_2` her adımda aynı giriş ve sayfalama dizisini yeniden koşturuyor
(150 adım, 736 çağrı, sıfır durum değişimi), ve `c77c005_3` aynı yanlış venmo
girişini 88 kez tekrarlıyor. Birincisinde çağrılar başarılı, ikincisinde
başarısız; ortak olan tek şey tekrar. Adım taksonomisi (K-36) bu ekseni hiç
taşımıyor, yani tekrar şu an ne durma kuralında ne de taksonomide görünüyor.
