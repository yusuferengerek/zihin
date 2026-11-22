# Değişiklik günlüğü

Biçim [Keep a Changelog](https://keepachangelog.com/tr/1.1.0/) esas alınarak
tutuluyor.

## [Yayımlanmamış]

### Hizalama Adım 0 — Tasarım katmanı yazıldı

**Eklendi**

Yedi tasarım belgesi boş yer tutucudan çıkarıldı ve tam bağlam belgesinden
dolduruldu:

- `01-problem-definition.tr.md` problem, bilinen çözümün bedeli, sınanan
  alternatif.
- `02-research-question.tr.md` iki soru, birincisi onaylayıcı tek hücrede,
  ikincisi keşifsel.
- `03-architecture.tr.md` iki güven bölgesi, yedi bileşen, kayıt/projeksiyon
  ayrımı ve silme testi, bağlam montajcısı.
- `04-threat-model.tr.md` üç somut tehdit, sandbox, kalkanın denetim zamanlaması,
  cezalandırmanın reddi.
- `05-experiment-design.tr.md` dört hata sınıfı, altı koşul, iki kritik kontrast,
  model ekseni ve iki kontrol, metrikler, analiz planı, kapılar.
- `06-skill-language.tr.md` madencilik, üç argüman sınıfı ve sıra kuralı,
  birleştirme, atomik yürütme, üç kapılı suç atfı.
- `07-failure-taxonomy.tr.md` üç düzey, tekrar ekseni, bağlam koşulu zorunluluğu,
  kapalı koşul dili, karşıtsal indirgeme.

Ayrıca `experiments/setup-protocol.tr.md` yazıldı ve donuyor: aile seçim ölçütü,
ayar bütçesi ve tükettiği dört revizyon, kurulumda dokunulan görev kimlikleri,
taranacak parametreler ve karar kuralları, tanı metriklerinin tanımı. Deney ön
kaydı ayrı kalıyor ve kurulum bitince donacak.

**Değişti**

- `PROJECT_STATUS.md` her tasarım öğesini uygulama durumuna eşliyor: tasarlandı,
  uygulandı, doğrulandı. Tasarım belgeleri hedef tasarımı anlatıyor, kod alt
  kümesini uyguluyor; tablo o boşluğu kapatıyor. Kapanmış S-11'e yapılan bayat
  atıf da düzeltildi.

**Karara bağlandı**

- K-62 yorumlanma kuralı önceden yazılmamış ölçüm sonuç değil, kurulum
  tanısıdır. Kurulum sonrası dört PR'da dağılan sonuçların ortak sebebi.
- K-61 hizalandı: aile kontrolü ana eksenin en büyük noktası bandında ve tek
  nokta; `granite` yalnız aday.
- K-43 düzeltildi. "Sansür oranı %10'un altında" diyordu; yüzde on kuralı
  yalnız **tavana çarpma oranına** ait. Aynı birleştirme S-22'de de vardı ve
  orada da düzeltildi.

**Belgelendi**

- `docs/reports/hizalama-denetimi.md` tasarım zemini ile deponun
  karşılaştırması. Merkezî bulgu: on beş PR, yedi boş tasarım belgesi ve boş bir
  ön kaydın üstüne birleştirildi. Dört sonuç geri alındı, biri yanlış ölçütle
  değerlendirildi, biri alt sınıra indi.
- Ön koşul kapısının ateşleme tarihi yazıldı: 11 Ağustos 2026.
- Kurulumda dokunulan görevler ölçüldü: `test_normal`'da 45/168, `train`'de
  13/90, `dev` ve `test_challenge` hiç dokunulmadı. Değerlendirmeye 123 görev
  kalıyor.

### Kurulum sonrası — Bağlayıcılık kuralı ve model ailesi taraması

**Karara bağlandı**

- K-60 sıfır yorumlanmadan önce bağlayıcı olmayan parametreler gösterilir.
  Kapsam: çıktı bütçesi, bağlam penceresi, adım tavanı, durma kuralı. Her
  birinin bağlayıcılık göstergesi tabloda; gösterge sıfıra yakın değilse sonuç
  alt sınır olarak yazılıyor.
- K-53 ikiye ayrıldı. Tavana çarpma oranı bir ölçüm artefaktı ve %10'un altında
  kalmalı; sansür oranı ise doğrulayıcı hükmüne dayanan bir sonuç ve %10 kuralı
  ona uygulanmıyor. Uygulansaydı tabana %90 başarı şartı konmuş olurdu.

**Ölçüldü**

- Ollama kayıt sunucusunda otuz üç aile × on iki boyut tarandı. 6,5 GB altına
  birden çok boyut sığdıran aileler: `qwen3.5` (0.8b, 2b, 4b), `qwen2.5-coder`,
  `qwen2.5`, `falcon3`, `granite3.3`, `granite4`, `gemma3`, `gemma2`,
  `codegemma`, `starcoder2`, `yi-coder`, `llama3.2`, `qwen3`, `cogito`.
  Güncel kod uzmanı aile yok: `qwen3-coder` 30b ve 480b sunuyor.
- 7B'nin sıfırı bütçe artefaktı değil: 958 adımın hepsi kod üretti, kodsuz ve
  ayrıştırılamayan adım sıfır (K-60'a işlendi).

### Kurulum sonrası — Sınır kontrolü: düzenek çalışıyor

**Ölçüldü**

- `deepseek/deepseek-v4-flash-0731`, bizim hattımızda, bant taramasının aynı
  otuz görevinde: **20/30 geçti** (%66,7), %95 alt sınır %50,1, dereceli skor
  95/152 = %62,5. Maliyet 0,62 dolar.
- Aynı otuz görevde üç nokta: DeepSeek 20/30, gpt-4o'nun yayımlanmış koşusu
  15/30, qwen2.5-coder 7B 0/30. Düzenek güçlü bir modele yayımlanmış koşudan
  daha yüksek oran veriyor.
- Bant taramasındaki sıfırlar model kapasitesinden; düzenekten değil.

**Sınır olarak yazıldı**

- S-26 aynı çıktı bütçesi model ailesine göre aynı koşul demek değil. Aynı
  model ve aynı görevlerde yalnız `max_tokens` değişince geçen görev 6/30'dan
  20/30'a çıktı; kodsuz adım oranı %25,0'ten %6,9'a düştü. Yerel model akıl
  yürütme üretmediği için etkilenmiyor (958 adımda kodsuz adım sıfır).
  Eşitlenecek olan sayı değil, bütçenin bağlayıcı olmaması.
- K-58'e ek: ön koşul kapısı bağlayıcı bütçe altında ölçülemez; kapı koşusunda
  kodsuz adım oranı raporlanıyor.

**Düzeltildi**

- "Durma kuralı yetenekli modeli de kesiyor" değerlendirmesi geri alındı.
  Bütçe bağlayıcı olmaktan çıkınca `no_progress` ile kapanan epizot 21'den
  4'e düştü ve o dördün yalnız biri gpt-4o'nun çözdüğü görev.
- Bant taramasından çıkarılan "kısa görevler daha kolay değil" sonucu 7B
  verisiyle sınırlıydı ve bilgi taşımıyordu: taban her bantta sıfırdı.

### Kurulum sonrası — Sınır kontrolü hazırlığı

**Eklendi**

- `scripts/measure_boundary_control.py`. Bant taramasının otuz görevini API
  üzerinden sunulan bir modelle koşturuyor: aynı iskele, aynı görev başına
  tavan, aynı durma kuralı, aynı yakalayıcı, aynı doğrulayıcı. Değişen tek şey
  model ve onu sunan katman.

  Künyeye yazmıyor. Künye sözleşmesi `num_ctx_effective`, `kv_cache_type`,
  `keep_alive` ve `context_verified` alanlarını zorunlu tutuyor ve bunların
  hepsi yerel Ollama kavramı; barındırılan bir modelde etkin bağlam penceresi
  doğrulanamadığı için `context_verified=1` yazmak yalan olurdu. Koşu deneyin
  parçası olmadığından kendi JSON çıktısına yazıyor.

**Açıldı**

- A-06 ölçek ekseni yerel donanımla sınırlı kalıyor mu. Kısıt 7B'nin
  çalışacağı varsayımına dayanıyordu; varsayım düştü. Karar sınır kontrolüne
  bağlandı.

**Sınır olarak yazıldı**

- S-20'ye kapsam maddesi: yönergedeki bozuk örnek bütün koşullarda ortak, yani
  karıştırıcı değil ama mekanizmanın en görünür hedefi. Ölçülen kazancın bir
  kısmı "kartlar kıyaslamanın bozuk örneğini onarıyor" anlamına gelebilir;
  ayıran şey K-59'un kontrastı.
- S-25'e tekrar etiketinin merkeziliği: iki bağımsız epizotta aynı desen, biri
  başarılı çağrılarla biri başarısız; ortak olan tek şey tekrar. Taksonomi bu
  ekseni taşımıyor.

### Kurulum sonrası — Teşhis: duvar nerede

**Eklendi**

- `scripts/measure_gpt4o_subset.py`. Yayımlanmış gpt-4o koşusunun çözdüğü
  görevlerde 7B'yi koşturuyor.
- `zihin.verification.graded_detail`. No-op tabanına göre düzeltilmiş dereceli
  skorun bileşenlerini değerlendirme dosyasından okuyor; iki ölçüm betiği de
  aynı işlevi kullanıyor.

**Karara bağlandı**

- K-58 ön koşul kapısı. Taban koşulu ayrılmış kümede ilan edilen asgari başarı
  oranını tutturamazsa hipotez test edilmemiştir ve mekanizma sonuçları
  raporlanmaz. Kural sonuç görülmeden donduruldu.
- K-59 `irrelevant_retrieval` kontrastının üç sonucunun yorumu, sonuç
  görülmeden yazıldı.

**Sınır olarak yazıldı**

- S-24 iki turluk dış inceleme ön koşul sorusunu sormadı.
- S-25 durma kuralı başarılı okumayı ilerleme sayıyor. Ölçülmüş örnek: 150
  adım, 736 çağrı, hepsi 200, durum farkı 150 adımda da boş, kural hiç
  ateşlemedi.
- S-20 sertleştirildi. Referans yönergenin 153. satırı çalışmıyor
  (`'bool' object is not subscriptable`) ve yönerge onu çalışmış gibi
  gösteriyor; ayrıca `login_result["access_token"]` çıkarımı hiç
  gösterilmiyor. 45 epizotta bozuk kalıp 34 kez kopyalandı.

**Ölçüldü**

- Duvar kimlik doğrulamada değil: 1717 çağrının 1445'i 200, 30 epizodun 23'ü
  supervisor dışı uygulamalardan 200 alıyor. Venmo'nun 401'i model hatası —
  spotify parolası venmo girişinde kullanılıyor, aynı blok 88 kez tekrarlanıyor.
- Kategori 4 baskın değil: 958 adımın %81,9'u eylem üretiyor, %16,9'u kategori
  4, kod üretilmeyen adım yok.
- gpt-4o'nun çözdüğü 30 görevde 7B dereceli skoru %4,8; çözemediği 15 görevde
  %5,4. İkili başarı ikisinde de sıfır.
- Uygulama kümesi tabakalaması: yalnız `spotify`/`todoist` görevlerinde dereceli
  skor %13,7, diğerlerinde %2,4. `spotify` yönergenin gösterdiği uygulama
  olduğu için kısıt karıştırıcı taşıyor.

### Kurulum sonrası — Önyükleme durduruldu, ölçülebilir bant taraması

**Eklendi**

- `scripts/measure_band.py`. Referans uzunluğa göre tabakalanmış başarı
  taraması. Tavan görev başına hesaplanıyor (`k × num_api_calls`), çünkü sabit
  tavan çapası 195 olan bir görevde görevi değil tavanı ölçer.
- `ZIHIN_MAX_STEPS` ve `ZIHIN_SPLIT` ortam değişkenleri `record_run.py` için.

**Karara bağlandı**

- K-57 önyükleme biriktirmesi durduruldu. Sebep analiz değil mekanizma:
  beceriler yalnız başarılı epizotlardan madenciliyor, başarı sıfırken
  madencilenecek korpus yok. Bant çıkmazsa üç yol yazılı, ikisi yaşayabilir.

**Sınır olarak yazıldı**

- S-23 bu model sınıfı için yayımlanmış taban oranlarına tasarımdan önce
  bakılmadı. `test_normal` pass@1: Mistral 7B %0,0, Qwen3-8B AWQ %3,0,
  Qwen3-8B FP16 %5,4, DeepSeek-Coder 33B %7,1, LLaMA-3-70B %20,8, GPT-4o %48,8.
  Bizim model 7B ve dört bit kuantalanmış.
- S-22 genişletildi. Sansür ölçümü sabit 20 adımlık tavanla koşuldu, oysa K-43
  tavanı çapaya bağlıyor; beş görevin çapaları 10 ile 195 arasında.

**Ölçüldü**

- Bant taraması: `test_normal`, 7B, otuz görev, beş bant, görev başına tavan
  `2 × num_api_calls`. Beş bantta da geçen görev sıfır; ikili başarı için %95
  üst sınır %9,5. Dereceli skor (no-op düzeltilmiş) 6/152 = %3,9, üç görevde
  toplanmış.
- En kısa bant sıfır çıktı ve tavandan değil: orada `k` 2,2 ile 3,3 arasında ve
  altı epizodun yalnız biri tavana dayandı.
- Otuz epizodun beşi `agent_finished` ile bitip doğrulayıcıdan kaldı.

### Kurulum sonrası — Sansür hükümden tanımlanıyor

**Eklendi**

- `src/zihin/verification.py`. Doğrulayıcıyı epizot bitiminde koşturup hükmü
  kayda çeviriyor. Sonraya bırakılamıyor: değerlendirme görev çıktı dizinindeki
  son veritabanı durumunu okuyor ve aynı görev başka bir modelle koşulduğunda o
  dizin üzerine yazılıyor.
- `tests/test_verifier_verdict.py`. Pinlenen asıl davranış `passed` alanının üç
  hâli; okunamayan hüküm `0` olarak yazılsaydı ölçüm arızası sansür sayısının
  içinde kaybolurdu.

**Değişti**

- `scripts/record_run.py` doğrulayıcı hükmünü gerçekten yazıyor. Önceki hâlinde
  satır açılıyordu ama `passed` her epizotta `NULL` kalıyordu.
- Deney dizini `ZIHIN_EXPERIMENT` ile ayrılabiliyor ve `run_id` önüne deney adı
  geliyor. Aynı görev ve model çifti ikinci bir ölçümde tekrar koşulduğunda
  künye birincil anahtarı çakışıyordu.

**Karara bağlandı**

- K-41 genişletildi. Yazma kümesi `statik ∪ ampirik`. Canlı sayım güncellemeyi
  göremiyor ve statik taramanın üçüncü grubu tam olarak o sınıf; statik tarama
  da devretmeyi göremiyor. İkisi birbirinin kör noktasını kapatıyor.
- K-53 yeniden yazıldı. Sansürü doğrulayıcının hükmü tanımlıyor, sonlanma
  sebebi değil. Sebep listesi ajanın bitirdiğini bildirip doğrulayıcıdan kaldığı
  hâli kaçırıyordu. `termination_reason` ayrı bir tanı alanı olarak kaldı.
- K-54 genişletildi. Kategori 4 oranı ana deneyde durma kuralı açıkken
  ölçülüyor; kural kapalı ölçüm yalnız eşik seçimine hizmet ediyor. Makalede
  hangi oranın hangi rejimden geldiği yazılıyor.
- S-21 yeniden yazıldı. Artık varyansa nokta kestirim değil üst sınır giriyor:
  model başına 0/30 için Clopper-Pearson %95 üst sınırı %9,5, ölçüldüğü rejim
  yanında.
- S-22 açıldı. Sansür oranı beş göreve ve model başına tek epizoda dayanıyor;
  beş görev rastgele örneklem değil.

**Ölçüldü**

- Sansür oranı üç modelde de %100, on beş epizotta. %95 alt sınır %54,9, ölçüt
  %10'un altını istiyor. 1.5B ve 3B için bekleniyordu, 7B için beklenmiyordu.
- Sunucu süreci yeniden başlatıldıktan sonra on yapılandırmanın onunda da adım
  ve çağrı sayıları taramadakiyle birebir aynı çıktı.

### Kurulum sonrası — Önyükleme öncesi üç koruma

**Eklendi**

- `src/zihin/state_probe.py`. Adım öncesi ve sonrası canlı veritabanı sayımını
  alıp farkı çıkarıyor. Okunamayan model `-1` yazılıyor, çünkü `0` "kayıt yok"
  demek ve iki ardışık `0` yanlışlıkla "değişmedi" diye okunur.
- `steps.state_change` sütunu. Üç hâl taşıyor: `NULL` ölçülmedi, `{}` ölçüldü
  ve değişmedi, dolu sözlük ölçüldü ve şu kadar değişti.
- `run_manifests.no_progress_limit`. Epizodun hangi eşikle koşulduğu kayıttan
  geri okunuyor. Alan zorunlu künye sözleşmesine de girdi (K-46).
- `tests/test_stopping_rule.py`. Durma kuralı ve durum ölçümü sahte adımlarla
  sınanıyor.

**Değişti**

- `RecordingAgent` ilerlemesiz aralık kuralını uyguluyor. Son
  `no_progress_limit` adımın hepsi ilerlemesizse epizot `no_progress` sebebiyle
  bitiyor. 1,5B'nin dört yüz bir alıp döndüğü epizot yirmi adım yerine dörtte
  kapandı.
- `scripts/record_run.py` kendi kaydedici kopyasını taşımıyor, paketteki
  `RecordingAgent`'ı kullanıyor. `run_id` artık modeli de içeriyor; aynı görevi
  ikinci bir modelle kaydetmek birincil anahtarı çakıştırıyordu.
- `check_cold_determinism.py` ölçümü durma kuralı açıkken yapıyor ve sonucu
  görev başına ayrı dosyaya yazıyor.

**Karara bağlandı**

- K-52 önyükleme biriktirmesi deneyin parçası değil. K-53 ölçek ekseninde
  işletme ölçütü sansür oranı. K-54 kategori 4 oranı koşul başına raporlanıyor.
  K-55 güç hesabı çıkarılan nicelik üzerinden. K-56 `irrelevant_retrieval`
  zorunlu koşul.

### Kurulum sonrası — S-16 bağlandı, yükleme protokolü kilitlendi

**Eklendi**

- `src/zihin/api_capture.py`. AppWorld'ün API istemcisini sarmalayıp yanıt
  gövdesini ve durum kodunu yakalıyor. Kayıt `raise`'den önce alınıyor ve sıra
  ayrı bir testle sabitlendi.
- `scripts/check_cold_determinism.py`. Model başına on soğuk epizot koşuyor,
  hepsinin aynı yörüngeyi verdiğini ve ikinci tohumun farklı yörünge verdiğini
  sınıyor.
- `zihin.scaffold.episode_prompt_path`, epizoda özgü prompt yolu.

**Değişti**

- `RecordingAgent` eylemleri yakalayıcıdan yazıyor; `actions.result_status` ve
  `error_class` artık doluyor. `api_calls.jsonl` deltası ikinci kaynak olarak
  tutuluyor ve sayımlar adım başına karşılaştırılıyor.
- `unload_model` boşaltmanın gerçekleştiğini sunucuya sorarak doğruluyor,
  doğrulanmazsa hata fırlatıyor (K-21'in ikinci şartı).
- `serve_models.ps1` sabit bekleme yerine yoklama yapıyor. GPU keşfi bu makinede
  23 saniye sürüyor ve sekiz saniyelik sabit bekleme, sunucu ayaktayken bile
  başarısız rapor veriyordu.

**Karara bağlandı**

- K-21 soğuk rejim, iki şartıyla. K-47 gereken determinizmin türü. K-48
  tekdüzelik tutmazsa ne yapılacağı, sonuç görülmeden. K-49 bir şeyin doğru
  sebeple mi çalıştığını ayrıca sorma kuralı. K-50 bağımlılık zinciri ve ön
  kaydın donma kuralı.

### Aşama 5 — İskele ve boş kart slotu

**Eklendi**

- `prompts/react_code_agent/` altında iki dosya: referans prompt'un
  değiştirilmemiş kopyası ve slot işaretçisi taşıyan sürüm.
- `src/zihin/scaffold.py`, slotu yerine koyan katman.
- `src/zihin/model_server.py`, sunucu introspection'ı tek yerde.
- `config/scaffold.yaml`, slot konumu.
- `scripts/verify_slot.py`, kabul ölçütünü koşturan doğrulama.
- `tests/test_scaffold_slot.py` ve `tests/test_manifest_contract.py`.

**Ölçüldü**

- Boş slotlu prompt referansla bayt bayına aynı, sha256 özetleri eşit.
- Aynı görev, aynı seed, aynı model: referans ve slotlu iskele birebir aynı
  yörüngeyi üretti, `d2b4954cc6fc05e3`, ikisi de 19 API çağrısı.
- Model başına yükleme süresi medyanı: 2,72 / 3,01 / 3,55 saniye. Üç bin
  epizotta soğuk protokolün toplam maliyeti 2,6 saat, toplam koşunun kabaca
  yüzde altısı.

**Değişti**

- Seed artık yalnız `task_id` ve `seed_index` ikilisinden türüyor. Model ve
  koşul girmiyor (K-20). İmza ayrı bir testle sabitlendi.
- Künye alanlarının zorunlu-dolu sözleşmesi kondu (K-46). Boş alan varsa künye
  yazılmıyor ve koşu düşüyor.

**Karara bağlandı**

- K-43 adım tavanı görev başına, K-44 normalizasyon tabanı
  `metadata.num_api_calls`, K-45 eşzamanlılık ölçülmüş hâliyle 7B'de tek epizot,
  K-46 künye sözleşmesi.
- S-17 açıldı: tavan model çağrısı biriminde, çapa API çağrısı biriminde.

### Aşama 4 — Ollama model sunum katmanı

**Eklendi**

- `config/models.yaml`. Üç model etiketi boyut ve kuantalama dahil tam hâliyle,
  bağlam penceresi, sıcaklık, seed tabanı, `keep_alive`, KV cache tipi ve flash
  attention.
- `scripts/serve_models.ps1`. Sunucuyu proje ayarlarıyla ve oturumdan bağımsız
  başlatıyor, uygulanan ayarları çıktıya basıyor.
- `scripts/measure_models.py`. Model başına bağlam penceresini doğruluyor,
  VRAM'i ölçüyor, tek görev koşturuyor ve künyeyi yazıyor.
- `src/zihin/recording_agent.py`. Kaydedici ajan betikten pakete taşındı, iki
  betik de onu kullanıyor.
- `tests/test_model_config.py` ve `tests/test_model_serving.py`, yeni
  `model_server` işaretiyle.

**Ölçüldü**

- Üç model de tamamen VRAM'de: 1,560, 2,602 ve 5,160 GiB. 7B yüklüyken kartta
  2,84 GiB pay kalıyor; sunucunun boş VRAM ölçümüne göre gerçek pay 1,74 GiB.
- Etkin bağlam penceresi üç modelde de 32768.
- Sunucu ayarları künyede: KV cache q8_0, flash attention true, keep_alive 30m.
  Kaynak sunucunun kendi yapılandırma dökümü.
- Adım tavanı kalibrasyonu tutmadı: doğrulayıcının aktif iş gereksinimi ile
  referans çözüm uzunluğu arasındaki korelasyon 0,088. Ama kalibrasyona gerek de
  yokmuş; `metadata.num_api_calls` 732 görevin hepsinde dolu.
- S-16 için birinci tercih çalışıyor: `Requester` sarmalanarak yanıt gövdesi ve
  durum kodu yakalanabiliyor, 401 dahil.

**Düzeltildi**

- Künyeye sunucu ayarları `None` yazılıyordu. Ayarlar Windows'taki sürecin
  ortamında, ölçüm betiği WSL içinde; `os.environ` onları görmüyor.
- Ölçüm betiği epizot yazıp adım yazmıyordu ve tutarsız kayıt üretiyordu.

### Aşama 3 — SQLite kayıt şeması

**Eklendi**

- `src/zihin/schema.sql`. Yedi tablo, dört düzeyli hiyerarşi, yalnız ekleme
  tetikleyicileri, yabancı anahtarlar, indeksler ve `episode_timeline` görünümü.
- `src/zihin/records.py`, şemayı uygulayan ve yazma yüzeyini veren ince katman.
- `scripts/record_run.py`, tek görevi koşturup canlı kaydeden yürütücü.
- `config/recording.yaml`, gözlem boyut sınırı ve koşu başına disk kotası.
- `DATA_MODEL.md`, şemanın neden öyle olduğu.
- `tests/test_record_schema.py` ve `tests/test_recorded_run.py`.

**Şemaya giren yeni alanlar**

- `episodes.model_load_state` ve `episodes.sequence_in_run` (K-39).
- `steps.outcome_category`, K-36'nın beş kategorisi.
- `shield_violations` tablosu.
- `run_manifests.num_ctx_effective` ve `context_verified`, K-37'nin şartı.

**Ölçüldü**

- `api_calls.jsonl` yalnız `method`, `url` ve `data` taşıyor. Yanıt gövdesi de
  durum kodu da yok, S-05 doğrulandı ve beklenenden dar çıktı.
- On beş GET ucu yazma çağrısı içeriyor ve dağılım rastgele değil, üç
  sistematik grup (K-41). Dokuzu `download_*`.
- Kaydedilen epizot: 20 adım, 19 eylem, 20 gözlem. Soğuk rejim ölçümüyle
  birebir aynı.

**Karara bağlandı**

- K-38 serpiştirilmiş atama, K-39 yükleme durumu ve sıra numarası, K-40 tavanda
  sansür, K-41 kalkan yüklemi ve istisna listesi, K-42 biriktirme havuzu ile
  değerlendirme örneklemi.
- K-11'e ikinci çapa eklendi: referans uzunluk ile doğrulayıcı çağrı sayısı
  arasındaki ilişki kalibre edilip test bölmelerine uygulanacak.

### Aşama 2 — AppWorld olgu raporu

**Eklendi**

- `docs/appworld-facts.tr.md`. Yedi soru ölçülerek cevaplandı, sekizinci madde
  kaynak koddan incelendi.
- `scripts/measure_episodes.py`, epizot koşturup ham sayıları JSON'a yazıyor.
- `scripts/check_determinism.py`, seed kontrolünü token ve epizot düzeyinde
  sınıyor.

**Ölçüldü**

- Bölmeler: train 90, dev 57, test_normal 168, test_challenge 417. Toplam 732
  görev, artı `_base_` adlı görev olmayan bir dizin.
- Referans çözümler 147 görevde var, train ve dev'in tamamında. Çözüm başına API
  çağrısı: ortalama 53,44, medyan 37, en yüksek 244.
- Görev başına API çağrısı 732 görevin hepsinde metadata'dan okunuyor.
  `test_challenge` medyanı en düşük bölme (25) ama kuyruğu en uzun olan da o,
  p95 değeri 178 ve en yüksek görev 649.
- Eğitim ve geliştirme bölmeleri on bir kullanıcı uygulamasının yalnız beşine
  dokunuyor. `test_challenge` içinde `amazon`, `gmail`, `splitwise` ve `todoist`
  geçiyor, dördü de eğitimde yok.
- 473 API'nin hepsinde `method` alanı var, okuma ve yazma ayrımı hazır geliyor.
  Aynı ayrım ad önekinden yüzde 99,4 doğrulukla da çıkıyor.
- Veritabanı sıfırlaması dünya açılışında otomatik, ayrı çağrı yok, medyan
  maliyeti 0,150 saniye.
- On iki epizotta 223 model turu ve toplam 1 API çağrısı. Ölçek ekseninin en
  küçük noktası taban etkisine yapışmış (S-14).

**Değişti**

- S-02 kısmen çürüdü, S-03 aşıldı, S-11 kapandı. Yerlerine S-13 ve S-14 açıldı.
- Adım düzeyi taksonomisi üçten beş kategoriye çıktı (K-36).
- A-05 karara bağlandı (K-37): bağlam penceresi sunucu tarafında veriliyor, ama
  koşu başına doğrulanıyor ve künyeye yazılıyor.
- K-22'ye oturum bağımsızlığı şartı eklendi.
- K-21 yeniden açıldı. Epizot yörüngesi modelin yüklü olup olmamasına göre
  değişiyor ve ölçülen tek güvenilir protokol `keep_alive` mantığının tersi.

### Aşama 1 — AppWorld kurulumu ve tek görev

**Eklendi**

- `appworld` ve `appworld-agents`, ikisi de `a072b7a` commit'ine sabit.
  İkincisi aynı deponun `experiments/` dizininden build ediliyor ve referans
  ajan iskelesini taşıyor.
- `scripts/run_single_task.py`, tek görevi referans iskeleyle koşturuyor ve
  ardından değerlendirmeyi çağırıyor.
- `scripts/local_checks.sh`, CI'da koşmayan kontrolleri tek komutta topluyor
  (K-35).
- `tests/test_appworld_reset.py`, epizot başına veritabanı sıfırlamasını
  sınıyor.
- `REPRODUCE.md` dolduruldu. İçinde Git LFS önkoşulu, mirrored ağ kipi,
  kurulum, model sunucusu, koşum ve yerel-yalnız kontroller var.

**Değişti**

- Ağ kipi mirrored oldu (K-34). Güvenlik duvarı kuralı gerekmedi ve Ollama
  `0.0.0.0` yerine `127.0.0.1` dinliyor. S-10 kapandı.
- CI her işte `git lfs install` koşuyor ve `appworld` işaretli testleri eliyor.

**Ölçüldü**

- Bölme başına görev sayısı: train 90, dev 57, test_normal 168,
  test_challenge 417.
- Ollama'nın VRAM'e dayalı varsayılan bağlam penceresi 4096. Yönerge dosyası
  11350 bayt ve ajan adım başına yaklaşık 3800 girdi tokenı harcıyor.
- Aynı seed ve sıcaklıkta koşulan üç epizot 19, 1 ve 19 API çağrısı yaptı
  (S-11).

### Aşama 0 ardılı — Koşul şeması kapandı, durum dosyaları eklendi

**Değişti**

- `retrieval.mode` artık getirme yöntemini taşıyor, içerik alakasını değil.
  Değerler `none` ve `symbolic` oldu, önceden `none` ve `standard` idi. İçerik
  alakası yalnız `skills.source` ve `failures.source` alanlarında kaldı (K-28).
- Saf içerik kontrastı düzeltildi. Doğrusu sadece beceriler ile alakasız
  getirme çiftidir. Önceden yanlışlıkla ikisi birden ile alakasız getirme
  yazılmıştı, oysa o çift iki alanda birden ayrışıyor ve tek eksenli değil
  (K-31).

**Eklendi**

- `PROJECT_STATUS.md`, `REPRODUCE.md`, `PILOT_REPORT.md`,
  `docs/10-external-review.tr.md`, `docs/11-falsification.tr.md` ve
  `experiments/decisions.csv`, hepsi taslak olarak (K-33).
- Git LFS önkoşulu `REPRODUCE.md`'ye yazıldı.
- İki kritik kontrastı ve `retrieval.mode` tablosunu denetleyen üç test.

### Aşama 0 — Depo iskeleti

İlk giriş. Zemin kuruldu, mekanizma yok.

**Eklendi**

- Depo ağacı: `docs/`, `experiments/`, `config/`, `src/`, `tests/`, `results/`,
  `pilot/`, `scripts/`.
- Python sürümü 3.11 olarak sabitlendi. `.python-version` dosyası ve
  `pyproject.toml` içindeki `requires-python = "==3.11.*"` satırı bunu tutuyor.
- Bağımlılıklar `uv` ile kilitlendi. Çalışma zamanı bağımlılığı tek, `pyyaml`.
  Geliştirme tarafında `pytest` ve `ruff` var.
- Altı koşul yapılandırması `config/` altında toplandı, hepsi aynı şemada:
  `baseline`, `skills`, `failures`, `skills_failures`, `irrelevant_retrieval`,
  `naive_compiler`.
- `src/zihin/config.py`, koşul yapılandırmalarını okuyup şemayı denetleyen
  asgari yükleyici.
- Şema denetimi testleri. Altı dosyanın anahtar yapısının birebir aynı olduğu,
  kalkanın istisnasız açık olduğu ve bozuk yapılandırmaların reddedildiği
  doğrulanıyor.
- Apache 2.0 lisansı, kanonik metin. sha256 değeri
  `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
- GitHub Actions üzerinde dört kontrol: bağımlılık kurulumu, lint, testler,
  import ve build.
- `docs/` altında dokuz tasarım belgesi başlıklarıyla açıldı. `08-decisions.tr.md`
  ve `09-limitations.tr.md` baştan doldurulmaya başlandı.
- `experiments/` altında ön kayıt, deney matrisi ve pilot planı başlıklarıyla
  açıldı.

**Kararlar**

Bu aşamada alınan kararların tamamı gerekçeleriyle
[`docs/08-decisions.tr.md`](docs/08-decisions.tr.md) içinde.
