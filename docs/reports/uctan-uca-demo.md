# Uçtan uca demo — kart bağlama girdi mi, model onu kullandı mı

> **GERİ ÇEKİLDİ — davranış iddiası, 18 Ağustos 2026.** Bu rapordaki
> "kartlı kol başarılı etkiye ulaştı, kartsız kol ulaşmadı" karşılaştırması
> tekrar altında ayakta kalmadı. Üç kol × beş görev × üç tekrar koşuldu
> (`docs/reports/uc-kollu-kart-kosusu.md`): on beş hücrenin **on biri** üç
> tekrarda ayrışıyor, ve kartsız kol on beş hücrenin altısında başarılı etkiye
> ulaşıyor. Tek epizot kolları ayırmıyordu; ayırdığı sanılan şey gürültüydü
> (S-56).
>
> **Geri çekilmeyen kısım:** giriş ölçümü. Kart bloğunun prompt'a bayt bayına
> girdiği, farkın yalnız blok olduğu ve taban prompt'unun referansla özdeş
> olduğu modele hiç bakmadan doğrulandı ve o ölçüm etkilenmiyor.
>
> Epizotlar kayıttan silinmedi; eski commit ölçümü olarak yerinde duruyor.


**Sayılar `results/card-demo.json` içinde.** Bu rapor onları yorumluyor,
kopyalamıyor; manşetler dışındaki her şey o dosyada.

Ön kayıt koşudan önce yazıldı ve dört sonucun yorumu orada
(`experiments/preregistration.md`, madde 7). Bu rapor o yorumları uyguluyor.

---

## Ne koşuldu

Yerel eksenin en büyük modeli, `qwen2.5-coder:7b-instruct-q4_K_M`. Her görev
**iki kez**: kartlı ve kartsız, aynı seed, aynı soğuk rejim, aynı yirmi adımlık
tavan. Koşu üretimin kendi yürütücüsünden geçti (`scripts/record_run.py
--cards`), yani künye, kalkan, durma kuralı ve kayıt yolu deneyin koşacağı
hâliyle aynı.

Seçim ölçütleri koşudan önce yazılı: kütüphanenin madencilendiği görevlerden
olmayacak, en az bir beceri kartı alacak, tek uygulama adlandıracak, ve her görev
farklı senaryodan. **Dördüncü ölçüt koşu sırasında eklendi** ve sebebi bir kusur;
kaydı ön kayıtta.

On epizot koştu: seçilen üç görevin altı epizodu, ve seçim düzeltilmeden önce
koşan iki varyantın dört epizodu.

## Birinci ölçüm: kart bağlama girdi mi

**Üç görevin üçünde de girdi**, ve ölçüm modele hiç bakmıyor:

| Denetim | Sonuç |
|---|---|
| Kart bloğu prompt dosyasının içinde, bayt bayına | 3/3 |
| İki prompt yalnız blok kadar farklı | 3/3 |
| Kartsız kolun prompt'u referansla bayt bayına aynı (K-25) | 3/3 |
| Künyedeki `instruction_file_digest` iki kolda farklı | 3/3 |

Blok boyutu 125 jeton (spotify kartı + bir hata kartı) ve 166 jeton (simple_note
kartı + bir hata kartı). Kart bütçesi ≤180+≤120, yani blok bütçenin yarısından
küçük (K-87).

**Bu ölçümün tamamı mekanik.** Kartın modele ulaştığını gösteriyor, okunduğunu
değil.

## İkinci ölçüm: model kullandı mı

On epizot, beş çift (`card-demo.json` → `tasks` ve `within_scenario_repetition`):

| Görev | Uygulama | Çağrı taban → kartlı | Yörünge aynı | Kartlı başarılı etki | Gövde eşleşmesi kartlı/taban |
|---|---|---|---|---|---|
| `0de03ea_1` | spotify | 20 → 11 | hayır | **adım 4** | **3/3** vs 1/3 |
| `1150ed6_2` | spotify | 2 → 2 | evet | yok | 1/3 vs 1/3 |
| `0a9d82a_1` | simple_note | 0 → 0 | (iki kol da boş) | yok | 0/7 vs 0/7 |
| `0a9d82a_2` * | simple_note | 7 → 2 | hayır | **adım 5** | — |
| `0a9d82a_3` * | simple_note | 4 → 0 | hayır | yok | — |

\* senaryo içi tekrar: seçim düzeltilmeden önce koşan çiftler, düzeltilmiş
demonun parçası değil.

**Hiçbir epizot doğrulayıcıyı geçmedi.** Beş çiftin onunda da `passed = 0`. Yerel
eksen sıfırda kalıyor ve bu ön koşul kapısıyla tutarlı.

### Kartın işini yaptığı hâl: `0de03ea_1`

Kartlı kol adım 4'te `GET supervisor.account_passwords` ve `POST
spotify.auth/token` yaptı, ikisi de `200`. Sonra indirilen şarkıları ve albümleri
okudu, adım 12'de `POST spotify.music_player/play`, adım 13'te
`POST supervisor.message` — ve **kendi kendine durdu**, tavana çarpmadan (13 adım).

Kartsız kol yirmi adımın yirmisinde `GET api_docs.api_descriptions` çağırdı. Aynı
çağrı, yirmi kez, hepsi `200`. Tavana çarparak bitti.

Kart gövdesi `GET api_docs.api_descriptions → GET supervisor.account_passwords →
POST spotify.auth/token`, ve kartlı kolda üçünün üçü sırayla tutuyor. Kartsız
kolda yalnız birincisi.

Doğrulayıcı: kartlı 3/5 test, kartsız 2/5. İkisi de geçmedi.

### Kartın hiçbir şey değiştirmediği hâl: `1150ed6_2`

Aynı kart, aynı uygulama, iki kolda da iki çağrı ve **birebir aynı yörünge**. Kart
bağlama girdi, davranış değişmedi. Ön kayıttaki ikinci yorum: bu bir başarısızlık
değil, sonuç.

### Sorunun sorulamadığı hâl: `0a9d82a_1`

İki kol da **hiç çağrı üretmedi**; yirmi adımın yirmisi yürütme hatası
(`apis.simple_note.notes`, `get_notes()`, var olmayan parametre adları). İki boş
dizinin eşitliği bir kimlik iddiası değil, ölçüm yokluğu.

**Ön kayıt bu hâli öngörmüyordu ve beşinci bir yorum gerekti:** iki kol da eylem
üretmediyse kullanım sorusu bu görevde **sorulamaz**. Ayrım K-79'un ayrımının
aynısı — "ölçüldü, değişmedi" ile "ölçülemedi" ayrı şeyler — ve veri dosyasında
`answerable` alanı olarak duruyor. Dördü seçilen görevlerde 2/3, beş çiftin
dördünde sorulabilir.

Yerel 7B'nin hiç çağrı üretmemesi bu demonun kusuru değil: kayıtlı 59 7B
epizodunun **14'ünde** (%24) sıfır çağrı var.

### Kartın zarar verdiği hâl: `0a9d82a_3`

Senaryo içi tekrarın ikinci çifti: kartsız kol dört çağrı yaptı, **kartlı kol hiç
çağrı yapmadı**. Tek yönlü bir demo raporu bunu atlardı; atlanmıyor. Beş çiftin
birinde kart bloğu davranışı kötü yönde değiştirdi, ve n=1 ile sebebi
söylenemez.

### Ayrıştırma sinyali

Model hiçbir epizotta kartın on altı haneli kimliğini kendi kodunda tekrar
etmedi. Sinyal tek yönlü: tekrar etmemesi kartı okumadığını **söylemiyor** —
`0de03ea_1`'de gövdenin üçü sırayla tutuyor ve o kartın okunduğunun daha güçlü
kanıtı.

## Kartın kendi kusuru, canlı gözlendi

`simple_note` görevlerinin hata kartı şunu diyordu:

    FAILURE GET simple_note.notes
      fails with: authorization_denied
      when: GET simple_note.profile has succeeded earlier in this episode

Kartsız kolda `GET simple_note.notes` gerçekten `401` döndü — ve epizotta hiç
`profile` çağrısı yoktu. Yani **etiket doğru, koşul yanlış**: gerçek sebep jetonun
olmaması, kartın söylediği koşul bir korelasyon. S-45'in tesadüfi ayırt etmesi
artık bir modelin bağlamında gözlendi.

Bu kart `own_app_condition = 1` taşıyor, yani "kendi uygulamasına ait koşul"
işareti bu kartı kurtarmıyor: koşul aynı uygulamadan olabilir ve hâlâ nedensel
olmayabilir.

## Ne sınanmadı

**Atomik yürütme yok.** Kart çağrı dizisini yazıyor, modeli o diziyi kendisi
yapıyor. `06-skill-language.tr.md`'nin atomik çağrısı, kırılan becerinin
yapılandırılmış dönüşü ve üç kapılı suç atfı bu demoda hiç çalışmadı. Sınanan şey
kartın **içeriği**.

**Hacim ile içerik ayrılamıyor.** `0de03ea_1`'de yörüngenin değişmesi kartın
içeriğinden mi geldi, yoksa bağlama 125 jeton fazladan metin girmesinden mi —
demo bunu ayırmıyor. Ayrımı yalnız `irrelevant_retrieval` koşulu verebilir (K-29,
S-19) ve o koşul burada koşmadı.

**Tek model, üç görev.** Kazanç iddiası yok ve olamaz. Demo mekanizmanın davranışa
ulaşabildiğini gösteriyor; ne sıklıkla ulaştığını göstermiyor.

**Başarı ölçülmedi.** Hiçbir epizot geçmedi, ve geçmesi de beklenmiyordu: ön koşul
kapısı bu eksende ateşledi.

## Ek: sonradan yapılan üç ölçüm

Demo kapandığında üç soru açık kalmıştı. Sayılar `results/demo-eklenti.json`
içinde.

### `0a9d82a_3`'ün kartlı kolu kategori 4 müydü — evet, yirmi adımın yirmisi de

Kartlı kol yirmi adım boyunca **hiç sunucuya ulaşmadı** ve yirmi adımın hepsi
K-36'nın dördüncü kategorisi: kod üretildi, ayrıştırıldı, hiç eylem üretmeden
yürütme hatası verdi. Kartsız kol aynı görevde dört eylem üretti (16 adım
kategori 4, 4 adım eylem üretti).

Zararın nerede olmadığı da önemli: kartlı kolun kodu var olmayan API adlarını
çağırıyor (`apis.simple_note.notes`, `get_all_notes`), yani kartın gösterdiği
diziye hiç gelmemiş. Kart bloğu modeli yanlış bir çağrıya yönlendirmedi; model
hiçbir adımda ayakta kalamadı. n=1, sebep söylenemez.

### Görev başına teslim edilen kart — beceri slotu hiç dolmuyor

| Bölünme | Görev | Kapsanan | Eşleşen beceri | Eşleşen hata | Hata slotu bağlayan |
|---|---|---|---|---|---|
| train | 90 | 87 | 0:9, 1:69, 2:12 | 0:3, 1:51, 2:6, 3:6, 4:18, 5:3, 6:3 | 6 görev |
| dev | 57 | 54 | 0:6, 1:42, 2:9 | 0:3, 1:33, 2:3, 4:12, 7:6 | 6 görev |
| test_normal | 168 | 168 | 0:9, 1:116, 2:40, 3:3 | 1:54, 2:15, 3:15, 4:47, 5:21, 6:3, 7:10, 8:3 | 16 görev |

İki şey çıkıyor. **Beş beceri slotunun üçü hiçbir görevde dolmuyor**: en çok
eşleşen beceri sayısı 3. Yani k=5 beceri için bir tavan değil, boş bir söz. Hata
tarafında tavan bağlıyor ama az: 315 görevin 28'inde, ve kesilen kart sayısı en
fazla üç.

Bütün sayılar üçün katı. Tesadüf değil: AppWorld görevleri senaryo başına üç
varyant ve getirici uygulama üzerinden eşliyor, yani bir senaryonun üç varyantı
aynı kartları alıyor. Bu aynı zamanda §"kart bağlama girdi mi" ölçümünün senaryo
içi tekrarının neden aynı kartlarla koştuğunun açıklaması.

### `0de03ea_1`'de doğrulayıcı ne bekliyordu — ve ham fark yanıltıyor

Görev: internetsiz on beş dakikalık bir yolculuk için, yeterli sayıda indirilmiş
şarkısı olan bir albümü çalmak. Beş test:

| # | Ne istiyor | No-op etiketi | Kartlı | Taban |
|---|---|---|---|---|
| 1 | Cevap `null` olmalı, yani metinsel cevap beklenmiyor | `no_op_fail` | geçti | düştü (`'<<not_given>>' == 'null'`) |
| 2 | Yalnız `spotify.MusicPlayer` değişmeli | `no_op_fail` | geçti | düştü (`set() == {'spotify.MusicPlayer'}`) |
| 3 | Player satırı güncellenmeli, oluşturulmamalı ya da silinmemeli | `no_op_pass` | geçti | geçti |
| 4 | İndirilmiş her şarkı kuyrukta olmalı | `no_op_fail` | düştü (`23 in [8, 9, 10]`) | düştü |
| 5 | Koleksiyon dışından şarkı kuyruğa girmemeli | `no_op_pass` | **düştü** (`3 == 0`) | geçti |

Ham skor 3'e 2. No-op tabanına göre düzeltilince (`graded_detail`, K-53'ün
dayandığı etiketler) **2/3'e 0/3**: taban kolun iki geçişi de hiçbir şey yapmayan
bir ajanın geçeceği testler. Yani ham fark farkı küçük gösteriyor.

Ters yönde de bir şey var ve o daha rahatsız edici: **kartlı kol eyleme geçtiği
için bedava geçişlerden birini kaybetti.** Beşinci test kuyruğa koleksiyon
dışından şarkı girmemesini istiyor; boş kuyruk bunu bedava geçiyor, kuyruğa üç
yanlış şarkı koyan kol düşüyor. Bu görevde eylemsizlik ödüllendiriliyor, ve K-53
sansür tanımı tam bu yüzden var.
