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
