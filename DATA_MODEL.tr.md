# Veri modeli

Şemanın kendisi `src/zihin/schema.sql` içinde; burada neden öyle olduğu var.

## Tablolar

Dokuz tablo, iki sınıf. Sınıf ayrımı bu belgenin en önemli kuralı ve makine
tarafından zorlanıyor (§"Projeksiyon kuralı").

| Tablo | Sınıf | Ne tutuyor |
|---|---|---|
| `run_manifests` | kayıt | Koşunun kendisi: model, sunucu ayarları, sınırlar, commit'ler, kalkan ve sandbox kimliği |
| `episodes` | kayıt | Bir görev denemesi: koşul, tohum, sonlanma sebebi, toplamlar |
| `steps` | kayıt | Bir model çağrısı ve onu izleyen bir `execute()` |
| `actions` | kayıt | O adımda yapılan API çağrıları |
| `observations` | kayıt | O adımın çıktısı, adım başına tek |
| `shield_violations` | kayıt | Kalkanın reddettiği eylemler |
| `verifier_results` | kayıt | Epizot başına tek hüküm |
| `skills` | **projeksiyon** | Derleyicinin ürettiği beceri kütüphanesi |
| `failure_patterns` | **projeksiyon** | Madencilikle çıkarılan hata indeksi |

**Düzeltme, 13 Ekim 2026: on iki tablo.** Bu bölüm dokuz tablo sayıyor; şemada bugün
on iki tablo var. Sonradan giren üçü:

| Tablo | Ne tutuyor | Nasıl girdi |
|---|---|---|
| `run_ledger` | Biriktirme koşusunun defteri, blok sınırı başına bir satır (K-162) | `579d4f1`, 10 Eylül 2026; PR'sız, doğrudan `main`'e |
| `experiment_slices` | Deneyin dilimleri: her dilimin görev listesi, ilk epizodundan önce yazılıyor | #70 (`4a04e50`) |
| `experiment_episodes` | Deney epizodu başına bir satır, epizodun kendi işleminde yazılıyor | #70 (`4a04e50`) |

Şema üçünü de kayıt olarak tanımlıyor; `PROJECTION_TABLES` hâlâ yalnız `skills` ve
`failure_patterns`'ı sayıyor. Ama hiçbiri yalnız ekleme tetikleyicisi taşımıyor: eksik
bir tabloyu var olan bir dosyaya ekleyen göç şemayı `;` ile bölüyor ve bir
tetikleyicinin gövdesi `;` taşıyor, yani burada yazılan bir tetikleyici taze dosyada
olurdu, deneyin yazdığı seride olmazdı. Bu üç tabloda yalnız ekleme yazıcılara
dayanıyor (K-182). Tetikleyici taşıyan kayıt tabloları yine yukarıdaki yedi tablo.

## Silme testi

Bir tablonun hangi sınıfa girdiğini belirleyen soru tek:

> **Bu tabloyu silsem, kayıttan geri hesaplayabilir miyim?**

Cevap "evet" ise projeksiyondur ve silinip yeniden üretilebilir olmak zorunda.
Cevap "hayır" ise kayıttır ve yalnız ekleme kuralı altındadır: bir kez yazıldı
mı ne güncellenir ne silinir.

Test retorik değil, koşuluyor: `tests/test_compiler.py` ve
`tests/test_failure_index.py` projeksiyonu silip kayıttan yeniden üretiyor ve
aynı satırların çıktığını sınıyor.

**Testin bugün geçmeyen bir tarafı var ve yazılıyor.** Projeksiyon **aynı
kimlikle** yeniden üretilemiyor: kimlik derleyici commit'ini taşıyor
(`v0-gap2-sup3-142662f`), yani bugün yeniden üretmek yeni bir kimlik yazar.
İçerik yeniden üretilebilir, kimlik üretilemez. Bu bilinçli — kimliğin commit
taşıması, hangi kuralın ürettiğini söylemek için var — ama "silip aynısını geri
koyabilirim" cümlesi bu yüzden tam doğru değil.

## Projeksiyon kuralı

`PROJECTION_TABLES` sabiti (`src/zihin/records.py`) iki tabloyu adıyla sayıyor:
`skills` ve `failure_patterns`.

Kuralın iki sonucu var ve ikisi de kodda:

1. **Projeksiyon tablolarında yalnız ekleme tetikleyicisi yok.** Kayıt
   tablolarının yedisinde `UPDATE` ve `DELETE` `RAISE(ABORT)` ile engelli;
   projeksiyonlarda engellenmiyor, çünkü silinip yeniden üretilmeleri gereken
   şey tam olarak onlar.
2. **Şema göçü projeksiyonları yeniden kurabiliyor.** Göç yolu, projeksiyon
   tablolarının tanımı değiştiğinde onları düşürüp yeniden yaratıyor; kayıt
   tablolarında bunu yapmıyor ve yapamaz.

Bir tablo listeye eklenirse yalnız ekleme koruması ondan kalkar. Liste bu yüzden
tek yerde ve testle çivili.

## Tek gerçek kaynağı kayıt defteri

Kayıt defteri tek gerçek veri kaynağı. Beceri kütüphanesi ve hata indeksi
türetilmiş projeksiyon, yani silinip kayıttan yeniden hesaplanabilirler. Bu
yüzden `skills` ve `failure_patterns` tabloları burada yok ve olmayacak.

**Düzeltme, 18 Ekim 2026: iki projeksiyon tablosu bu şemada.** Bu paragraf, şemada
yalnız kayıt tabloları varken yazıldı (`09ed3fb`, 10 Ağustos 2026). `skills` 16
Ağustos'ta (`142662f`), `failure_patterns` 17 Ağustos'ta (`771b94f`) aynı şemaya
girdi; ikisi `PROJECTION_TABLES`'ta sayılı ve yukarıdaki tabloda **projeksiyon**
olarak duruyor. Değişmeyen şu: kayıt tek gerçek kaynağı; iki tablo kayıttan
türetiliyor, silinip yeniden üretilebiliyor ve yalnız ekleme kuralı onlara
uygulanmıyor.

Gerekçesi zamanla ilgili. Türetme kuralları çalışma boyunca birkaç kez
değişecek. Projeksiyon gerçek kabul edilirse, kural değiştiği anda eski veri
kullanılamaz hâle gelir. Kayıt gerçek kabul edilirse, kural değiştiğinde
yapılacak tek şey yeniden hesaplamaktır.

Aynı ilke `actions.raw_parameters` sütununda da geçerli. Ham parametreler özet
değeriyle değil tam hâliyle duruyor (K-15), çünkü normalizasyon kuralı
değişecek ve projeksiyonun kayıttan yeniden hesaplanabilmesi gerekiyor.

## Dört düzey

```
run_manifests
  └── episodes            bir görev denemesi
        └── steps         bir model çağrısı ve onu izleyen bir execute()
              ├── actions       o adımda yapılan API çağrıları
              ├── observations  o adımın çıktısı, adım başına tek
              └── shield_violations  kalkanın reddettiği eylemler
        └── verifier_results   epizot başına tek hüküm
```

### Gözlem neden adıma bağlı

Şartname gözlemi eyleme bağlıyordu. Ölçüm başka söyledi: AppWorld'ün
`execute()` metodu adım başına tek bir çıktı dizesi döndürüyor, tek tek API
çağrıları için ayrı çıktı vermiyor. Eylem düzeyinde "tam çıktı" diye bir kavram
ortamda yok. Karar K-13'te, gözlem adıma bağlı.

Bunun bir sonucu var: `observations.step_id` üzerinde `UNIQUE` kısıt duruyor,
yani adım başına tam olarak bir gözlem.

### Eylem üretmeyen adım da tabloda duruyor

K-36'nın dördüncü ve beşinci kategorileri hiç eylem üretmiyor. O adımlar
kayıttan düşerse sıfır eylemli epizot, ajanın çağırmamayı seçtiği epizotla
aynı görünür. `steps.outcome_category` bu ayrımı taşıyor ve
`episode_timeline` görünümü eylem satırı olmayan adımları da veriyor.

## Kalkan ihlalleri neden ayrı tabloda

Kalkanın reddettiği eylem yürütülmüyor, dolayısıyla `actions` tablosuna
girmiyor. Ama kaybolmaması gerekiyor: reddedilen her eylem, hasar oluşmadan
önce elde edilmiş etiketli bir olumsuz örnek ve doğrudan hata indeksine
yazılacak.

`shield_violations` adıma bağlı, çünkü ihlal bir adımın ürettiği kod içinde
oluyor. `mode` sütunu `enforce` ve `shadow` değerlerini alıyor; gölge kipte
eylem geçiyor ama ihlal yine kaydediliyor.

## Epizot satırındaki iki alan neden var

`sequence_in_run` ve `model_load_state` Aşama 2 ölçümü yüzünden eklendi.

Ölçülen olgu şu: aynı görev, aynı seed, aynı sıcaklık. Model soğukken epizot 19
API çağrısı üretiyor, ısınmışken 1. İki koşu da kendi rejiminde birebir
tekrarlanıyor. Yani yükleme durumu gizli bir değişken ve kaydedilmezse
epizotlar arası fark koşul farkı sanılır.

`sequence_in_run` ise koşu içindeki kaymayı sonradan sınamak için. Sunucu
durumunda zamanla bir sürüklenme varsa, sıra numarası ortak değişken olarak
modele girebilir. `UNIQUE (run_id, sequence_in_run)` kısıtı numaranın
tekrarlanmasını engelliyor, yoksa sınama anlamsızlaşır.

## Künye

`run_manifests` koşu sırasında toplanmazsa sonradan toplanamayacak alanları
taşıyor. Model etiketi boyut ve kuantalama dahil tam hâliyle yazılıyor.

### Künye sözleşmesi: zorunlu-dolu alanlar

Bu alanlardan biri boşsa künye **yazılmıyor**, koşu düşüyor (K-46). Sebebi
zamanla ilgili: bu bilgiler koşu sırasında toplanmazsa sonradan toplanamıyor,
yani eksik künye koşuyu değersiz kılıyor. Liste `ZORUNLU_KUNYE_ALANLARI`
sabitinde, tek yerde.

**Düzeltme, 13 Ekim 2026: sabitin adı.** Sabit, tanımlayıcıların İngilizceye
çevrildiği commit'te (`acef1d8`, 18 Ağustos 2026) `REQUIRED_MANIFEST_FIELDS` adını
aldı; `src/zihin/records.py` içinde.

| Alan | Neden zorunlu |
|---|---|
| `run_id` | Koşunun kimliği |
| `model_tag` | Hangi model; boyut ve kuantalama dahil |
| `temperature`, `base_seed` | Yörüngeyi belirleyen iki sayı |
| `no_progress_limit` | Epizodu sonlandırabilen parametre; 0 "kural kapalı" demek ve o da yazılıyor |
| `max_output_tokens` | Ölçüldü: yalnız bu değer değişince geçen görev 6/30'dan 20/30'a çıktı (S-26) |
| `max_prompt_characters` | Etkin bağlamı belirleyen sayı (S-47); -1 "tavan yok", NULL "kaydedilmedi" |
| `model_server_env` | Sunucu ayarları depo dışında yaşıyor |
| `appworld_commit`, `code_commit` | Hangi kodun ürettiği |
| `instruction_file_digest` | Modele giden metnin özeti |
| `os_environment` | Platform |
| `shield_mode` | `shield_violations` satırlarının hangi rejimde üretildiği |

Yerel sunumda ayrıca sunucuya özgü alanlar zorunlu; barındırılan modelde
karşılıkları olmadığı için o kipte aranmıyor.

**Nullable olmak ile boş bırakılabilir olmak aynı şey değil.** Sütun `NULL`
kabul ediyor olabilir; sözleşme yine de dolu olmasını isteyebilir. Şema tarafı
eski satırların göç edebilmesi için gevşek, Python tarafı yeni satırlar için
sıkı. Bu ayrım S-29'un dersi: `CHECK` kısıtları göç yoluyla eklenen sütunlara
taşınamıyor.

**Bağlam iki farklı birimde sınırlı ve künye ikisini de taşıyor.**
`num_ctx_requested` / `num_ctx_effective` jeton penceresi;
`max_prompt_characters` iskelenin kendi prompt tavanı, karakter cinsinden.
Bağlayıcı olan ikincisi: ölçüldü, 50000 karakter gerçek kayıt içeriğinde 12799
jeton, yani 32K pencerenin %39'u (S-47). Değer `config/recording.yaml`'dan
okunuyor, ajana geçen sayı ile künyeye giren sayı aynı kaynaktan, ve alan devam
denetiminin reddet listesinde. NULL "kaydedilmedi" demek — künye yalnız ekleme
kabul ediyor, yani sütun eklendikten sonra eski satırlara sayı yazılamıyor; -1
"tavan yok" demek.

İki alan K-37'nin şartı: `num_ctx_effective` ve `context_verified`. Bağlam
penceresi sunucu tarafındaki ortam değişkeninden geliyor, yani depo dışında
yaşıyor. Sunucu bir kez o değişken olmadan yeniden başlarsa pencere sessizce
4096'ya döner ve ölçüm bozulur ama hiçbir yerde hata görünmez. Koşucu bu
yüzden koşudan önce sunucuya soruyor ve tutmuyorsa duruyor.

Doğrulamanın kendi maliyeti var ve ölçüldü: `/api/ps` yalnız o an yüklü modeli
bildiriyor, yani pencereyi okumak için modeli yüklemek gerekiyor. Doğrulama
modeli ısıtıyor. `scripts/record_run.py` bu yüzden doğrulamadan sonra modeli
tekrar boşaltıp epizodu soğuk rejimde başlatıyor.

## Yalnız ekleme

Bütün kayıt tablolarında `UPDATE` ve `DELETE`, `RAISE(ABORT)` eden
tetikleyicilerle engelli (K-16). Bu bir sözleşme değil mimari kural, o yüzden
makine tarafından korunuyor. `tests/test_record_schema.py` yedi tablonun her
biri için ayrı ayrı sınıyor.

**Düzeltme, 13 Ekim 2026.** Bu paragraf yazıldığında kayıt tablosu yediydi. Bugün on
kayıt tablosu var ve tetikleyiciler yalnız o yedisinde; sonradan giren üçü,
`run_ledger`, `experiment_slices` ve `experiment_episodes`, yalnız eklemeyi
yazıcılarına bırakıyor (yukarıda, "Tablolar"; K-182).

Bunun bir sonucu var: epizodun bitiş zamanı ve toplamları ancak epizot bitince
biliniyor, güncelleme de yasak. Bu yüzden `scripts/record_run.py` epizodun
tamamını bellekte biriktirip sonunda tek işlemde yazıyor. Koşu ortasında çökme
olursa AppWorld'ün kendi kayıtları diskte duruyor, yani veri kaybolmuyor,
yalnız veritabanına girmemiş oluyor.

## Yazma nerede yapılıyor

Kayda yazma işi host tarafında, yürütücü sürecinde (K-14). Ajanın çalıştırdığı
kodun içinden kayda yazılmıyor. Sebebi basit: kendi ortamını bozan bir ajan,
içeriden yazılan kaydı da bozar.

Eylemler AppWorld'ün `logs/api_calls.jsonl` dosyasından geliyor. O dosya düz
bir liste ve hangi çağrının hangi adıma ait olduğunu söylemiyor, yani koşu
bittikten sonra bakıldığında eylemler adımlara bağlanamıyor. Kayıt bu yüzden
canlı alınıyor: dosyanın o adımda uzadığı kadarı o adımın eylemleridir.

Bunu yapmak için iskeleye dokunulmuyor. `SimplifiedReActCodeAgent` olduğu gibi
kullanılıyor, yalnız ortamın yürütme metodu dışarıdan sarmalanıyor. Ajanın
prompt'u, ayrıştırıcısı ve döngüsü aynı kalıyor.

**Sarmalanan metot kipe göre değişiyor ve bu ölçülerek öğrenildi.** Referans
ajan `world.batch_execute` çağırıyor, `world.execute` değil. Süreç içi kipte
`batch_execute` her kod için `self.execute` çağırdığı için `execute`i sarmalamak
yetiyordu — kayıt bugüne kadar bu tesadüfle çalıştı ve kimse fark etmedi. Uzak
ortam kipinde `batch_execute` doğrudan HTTP çağrısına sapıyor ve `self.execute`
hiç çağrılmıyor; ilk sandbox epizodu 32 KB yörünge üretip kayda sıfır adım yazdı
(S-53). Uzak kipte `batch_execute`, süreç içi kipte `execute` sarmalanıyor ve
ikisi `tests/test_recording_mount.py` içinde mutasyonla çivili.

**Sandbox kipinde eylemler `api_calls.jsonl`'den gelmiyor.** O dosya ortam
sunucusunun yazdığı bir dosya ve ortam sunucusu konteynerin içinde; host
tarafında ikinci kaynak yok. Eylemler kayıt vekilinden geliyor ve sayım
karşılaştırması yapılmıyor, çünkü karşılaştıracak ikinci sayı yok. Kaynağın
yokluğu bir süre "sıfır çağrı" diye okundu ve bu da S-53'ün ikinci katıydı.

## Doldurulamayan sütunlar

`verifier_results.expected_changes_complete` ve `unexpected_changes_present`:
AppWorld'ün `TestTracker` sınıfı `passes` ve `failures` listeleri veriyor,
makaledeki iki bileşeni ayrı boole olarak vermiyor olabilir (S-04). Sütunlar
duruyor ki çıkarılabildiği gün yer hazır olsun.

**`actions.result_status` artık doluyor ve bu bölüm o yüzden değişti.** S-05
`api_calls.jsonl`'in yanıt gövdesi de durum kodu da taşımadığını söylüyordu;
`ApiCapture` `Requester`ı sarmalayarak ikisini de aldı (S-16). Ölçülen: 5261
eylemin hepsinde durum kodu var — 200 (4489), 401 (503), 422 (235), 409 (34).

**`actions.error_class` kipe göre değişiyor.** Süreç içi kipte istisnanın sınıf
adını taşıyor; sandbox kipinde `NULL`, çünkü vekil istisnayı görmüyor — istisna
konteynerin içinde oluşuyor (S-52). Alan kayıtta durum kodundan bire bir
türetilebiliyor (772 = 503+235+34), yani bilgi kaybı yok; vekilin görmediği bir
değeri uydurması reddedildi.

**Durum ölçümü iki kolonda ve ikisi aynı adımda dolamıyor.** `steps.state_change`
satır sayısı farkını taşıyor ve süreç içi kipte doluyor; `steps.state_hashes`
hangi modelin değiştiğini taşıyor ve sunulan kipte doluyor (K-93). İkisi ayrı
kolon çünkü ayrı anlamlar: biri "kaç satır değişti", diğeri "hangi model
değişti". Aynı kolona konsaydı bir değerin anlamı onu üreten kipe bağlı olurdu.
`insert_step` ikisinin birlikte yazılmasını reddediyor.

## Gözlem boyutu ve disk kotası

`config/recording.yaml` iki sınır taşıyor. Bağlama giren kesilmiş metin için
üst sınır 8192 bayt. Aşama 2'de ölçülen adım başına 5958 girdi tokenının
yanında bu sınır, tek bir gözlemin bağlamın tamamını yutmasını engelliyor.

Koşu başına disk kotası 2 GiB. Kota dolduğunda koşu duruyor. Sessizce kayıt
düşürmek, sonradan fark edilmeyen bir veri kaybı üretir; durmak kaybetmekten
iyidir (K-17).

Kesme bağlama girerken uygulanıyor, taşma anında değil. Tam metin diskte
kalıyor ve veritabanı yalnız referansını taşıyor.

## Epizodu tek sorguyla okumak

`episode_timeline` görünümü kabul ölçütünün istediği sorgunun kendisi.

```sql
SELECT * FROM episode_timeline
WHERE episode_id = ?
ORDER BY step_index, action_index;
```

Sol dış birleşim kullanılıyor, böylece eylem üretmeyen adımlar da satır
veriyor.
