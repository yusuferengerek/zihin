# Mekanizma yol haritası — kapanış notları

Her madde kapanırken buraya kısa bir not düşüyor: ne kuruldu, ne ölçüldü, bitmiş
sayılma şartlarının yedisinden hangileri sağlandı.

**Neden tek dosya.** Pilot raporu yazılırken her sayının yeniden türetilmesi
gerekmesin. Ölçümler raporlara dağılırsa hangi sayının hangi yapılandırmada
alındığı kaybolur; bu depoda yazma kümesi tek günde iki kez değişti ve aynı
ölçüm iki farklı sayı verdi.

## "İncelendi" bu belgede ne demek

Her maddenin bitmiş sayılma tablosunda geçtiği için bir kez tanımlanıyor; dış
okuyucu için önemli.

**Yazan ile inceleyen aynı değil.** Kodu ajan yazıyor, incelemeyi proje sahibi
yapıyor. İnceleme etkili: bu belgedeki maddelerde kaydedilen kusurların önemli
bir kısmı incelemede yakalandı, ve birkaçında inceleme ajanın vardığı sonucu
çürüttü.

**Ama inceleyen diff'i değil raporu okuyor.** Yani inceleme, ajanın ne yaptığını
anlattığı metin üzerinden yürüyor; satır satır kod okuması değil. Bu gerçek bir
fark ve iki sonucu var. Anlatılmayan bir değişiklik incelemeye hiç girmiyor. Ve
rapordaki bir sayı yanlışsa, inceleme onu ancak başka bir sayıyla çeliştiği için
yakalayabiliyor — nitekim bu depoda birkaç kez öyle oldu.

Bunu telafi eden şey testlerin ve kapıların kendisi: incelemenin göremediği yeri
ağaç durumu görüyor. Ama telafi tam değil, ve "incelendi" satırı bu anlamda
okunmalı.

Yol haritası: 1. kalkan → 2. beceri şartnamesi → 3. derleyici v0 →
4. hata indeksi → 5. getirici v0 → 6. mekanizma pilotu → 7. uçtan uca demo →
**8. sandbox**.

Yedi madde kapandı; sırada sandbox.

## Madde başına PR

| Madde | PR | Dal | Commit |
|---|---|---|---|
| — (kurulum sonrası, madde değil) | [#20](https://github.com/yusuferengerek/zihin-archive/pull/20) | `kurulum-sonrasi-hizalama` | `de32822`..`ba88f44` |
| 1 kalkan | [#21](https://github.com/yusuferengerek/zihin-archive/pull/21) | `madde-1-kalkan` | `4d6a0ac`..`cfdc1e1` |
| 2 beceri şartnamesi | [#22](https://github.com/yusuferengerek/zihin-archive/pull/22) | `madde-2-skill-spec` | `51f3e0d`..`c30ff34` |
| 3 derleyici | [#23](https://github.com/yusuferengerek/zihin-archive/pull/23) | `madde-3-derleyici` | `1d76cd4`..`30233e4` |
| 4 hata indeksi | [#24](https://github.com/yusuferengerek/zihin-archive/pull/24) | `madde-4-hata-indeksi` | `ecc70d9`..`4bb340a` |
| 5 getirici | [#25](https://github.com/yusuferengerek/zihin-archive/pull/25) | `madde-5-getirici` | `4136d71` |
| 6 mekanizma pilotu | [#26](https://github.com/yusuferengerek/zihin-archive/pull/26) | `madde-6-mekanizma-pilotu` | `b0f9051` |
| 7 uçtan uca demo | [#27](https://github.com/yusuferengerek/zihin-archive/pull/27) | `madde-7-demo` | `5a21312`..`63fa7ba` |

**Sekiz PR, sırayla açıldı ve birleştirildi**, her birinin açıklaması ilgili
kapanış notu, her birinde dört CI kontrolü yeşil. Akış PR #19'dan sonra durmuştu
ve bu bölme geriye dönük yapıldı; bedeli S-49'da sayıldı. Kural artık protokolde:
her madde kendi PR'ıyla kapanıyor, PR açılmadan sonraki maddeye geçilmiyor.

**İki sınır geriye dönük bölmenin kendisinden geliyor.** `4d6a0ac` boşluk
raporunu ve yazma kümesi türetmesini birlikte taşıyor, `5a21312` karakter tavanını
(madde 6) ve demo koşucusunu (madde 7) birlikte taşıyor. İkisi de bölünemedi,
çünkü bölmek commit'i ikiye ayırmak — tarihi yeniden yazmak — olurdu.

---

## Madde 1 — Kalkan ve birim test takımı

**Durum: kapandı.** Commit'ler `4d6a0ac`..`c2ce910`, on commit: `4d6a0ac`,
`27f356a`, `8fb86ec`, `04c488a`, `2b3a7ec`, `a8369ae`, `10e11a2`, `26103da`,
`916ccaf`, `c2ce910`.

**Liste düzeltildi.** İlk hâlinde altı commit yazıyordu ve birincisi `9e055f9`
idi; o özet artık dalda değil, aynı içeriğin amend edilmiş öncesi. Ayrıca yazma
kümesi türetmesini ve yüklemi getiren üç commit listede yoktu. Doğrusu yukarıda,
ve PR açıklamasındaki commit listesi bu aralıktan üretiliyor.

`4d6a0ac` iki maddeye dokunuyor: boşluk raporu kurulum sonrası işin parçası, ama
`scripts/setup/derive_write_set.py` ilk kez o commit'te doğuyor ve yazma kümesi
kalkanın artefaktı. Doğrusal tarihte ayrılamıyor, o yüzden madde 1'in başına
konuldu.

### Ne kuruldu

| Parça | Yer |
|---|---|
| Saf yüklem | `src/zihin/shield.py` — beş dal, kapalı ret sözlüğü |
| İzinli uygulama çıkarıcısı | `src/zihin/allowed_apps.py` — görev metninden, ground truth'tan değil (K-70) |
| Montaj noktası | `src/zihin/shield_mount.py` + `api_capture._wrap` — çözümleme, kayıt, adım sınırında boşaltma |
| Yazma kümesi türetmesi | `scripts/setup/derive_write_set.py` — yöntem kuralı + GET için gövde taraması |
| Kayıt | `shield_violations` tablosu; künyede `shield_mode`, `shield_config_digest` |

Yüklem montaj noktasından ayrı. Sandbox'a geçişte (K-65) montaj yeniden
yazılacak, yüklem kıpırdamayacak.

### Ne ölçüldü

| Ölçüm | Değer | Nerede |
|---|---|---|
| Yanlış pozitif oranı | **6/147 = %4,1** | `results/shield-cost.json`, train+dev |
| Engelleme oranı, çağrı | **6/9154 = %0,07** | `results/shadow-mode.json`, 258 epizot |
| Engelleme oranı, epizot | 6/258 = %2,33 | aynı |
| Engelleme oranı, görev | 1/58 = %1,72 | aynı |
| Yüklem dağılımı | okuma %94,29, izinli yazma %5,65 | aynı |
| Fail-open dalı | 5213 kayıtlı çağrının **0'ı** | `results/shield-cost.json` |
| Yazma kümesi kapsaması | 478 API, 478 anahtar, yöntemsiz uç 0 | aynı |
| Yazar uç | 296 (sınır geçen 19, GET yazarı 12, `download_*` 9) | `inputs/write-set-static.json` |
| Uygulama kümesi çıkarımı | tam eşleşme %75,5, Jaccard 0,857 | `docs/reports/izinli-uygulama-vekili.md` |

**Düzeltme, 15 Kasım 2026: engelleme satırları.** Gölge korpusuna bir testin iki çıktısı
girmişti (S-83). Onlarsız çağrıda 5/9145 = %0,05, epizotta 5/256 = %1,95, görevde
1/58 = %1,72 (değişmedi). Yüklem dağılımı iki ondalıkta aynı: okuma %94,29, izinli
yazma %5,65. Aşağıdaki kurallar tablosundaki %0,09'un karşılığı %0,08: ilk koşu 9145
çağrıda 7 engelleme.

**İki oran birbirinin yerine geçmiyor (K-72).** Yanlış pozitif yalnız yer
gerçeği olan train + dev'de ölçülebiliyor; engelleme oranı bütün korpusta
ölçülüyor ama orada bir engellemenin doğru olup olmadığı bilinemiyor.

**Engelleme oranı kalkanın ucuzluğunu göstermiyor.** Altı engellemenin altısı da
düzeneğin kendi yazma sondalarından (`durum-sondasi-*`, `notlar`,
`reset-check-1`, `sifirlama*`), tek görevde ve tek uçta. Model yörüngelerinde
engelleme oranı **sıfır**, ve bu korpusun kalkanı sınamadığının kanıtı: 58
görevin çoğu tek uygulamaya dokunuyor, sınır geçen yazma fırsatı hiç doğmuyor.

### Ölçüm sırasında bulunan ve düzeltilen kusurlar

| | Kusur | Etki |
|---|---|---|
| S-36 | Çözümleyici yöntemi almıyordu, iki `phone` şablonu aynı yolu eşliyor | 26 çağrı bilinmeyen uca düşüyordu; bu korpusta latent |
| S-37 | `update` model fiili değil, Python kap metodu | İki saf okuma yazar sayılıyordu, ikisi gölge modunda engellendi |
| S-38 | `ast.walk` süsleme listesini geziyordu | Dokuz `delete_account` kümede yalnız kaza sonucu duruyordu |
| S-35 | K-41 ile bir uç anlaşmazlığı | **Kapandı**: K-41 fazladan saydı |

### Bilerek açık bırakılanlar

- **Zorlama kipi kurulmadı (K-71).** İkame yanıtın biçimi bir koşul değişkeni
  ve karar verilmedi. `enforce` ile kurulmaya çalışılırsa montaj kurulum anında
  düşüyor.
- **Bilinen fazla dahil etme (S-38).** 64 GET dışı ucun gövdesinde yazma yok ve
  hepsi kümede; ikisi doğrulanmış okuyucu. Uç bazında `body_write` alanıyla
  kayıtlı. Bir adım öteye de yayıldı: üç `add_payment_card` ucu bu iki okuyucu
  üzerinden sınır geçen yazar oldu. Pratik etkisi sıfır, çünkü `admin` altyapı
  uygulaması ve koşulsuz izinli — ve bu artık varsayım değil, `allowed_apps.py`
  içinde kural ve `test_allowed_apps.py` içinde çivili. Üç uçtan biri doğrudan
  yüklem üzerinden sınanıyor.
- **Ampirik yarı boş (S-35, K-41).** Küme `statik ∪ ampirik` olarak tanımlı,
  ampirik yarı henüz toplanmadı.

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Yüklem, çıkarıcı, montaj, türetme, künye alanları |
| Testi yazıldı | Evet. `test_shield.py` 15, `test_shield_mount.py` 13, `test_allowed_apps.py` 16, künye sözleşmesi 6, devam koruması 2 |
| Loglandı | Commit gövdelerinde; ölçüm çıktıları `results/` altında |
| Belgesi yazıldı | K-69..K-74, S-35..S-38, bu not |
| Hata durumu düşünüldü | Bilinmeyen uç adlandırılmış dal; zorlama kipi kurulumda düşüyor; kalkanlı koşu özetsiz künye yazamıyor; türetme kapısı dört değişmezi sınıyor |
| PR üzerinden gözden geçirildi | **Evet, PR #21.** Açıklaması bu kapanış notunun kendisi, dört CI kontrolü yeşil. İnceleme yine diff üzerinden değil rapor üzerinden — yukarıdaki tanım geçerli |
| Temiz kurulumda baştan çalıştırıldı | Test takımı tam geçiyor; türetme sıfırdan koşup kapıyı geçiyor; künye göçü gerçek seri 2 kopyasında sınandı. CI artık `appworld install` ve veriyi kuruyor, yani bu maddenin testleri temiz makinede gerçekten koşuyor (K-100). |

**Yedi şartın yedisi sağlandı.** PR satırı uzun süre "dal henüz açılmadı" diyordu;
madde PR #21 ile kapandı ve satır güncellendi.

**İki düzeltme, ikisi de bu satırda.** İlk hâlinde "bu depoda PR akışı yok"
yazıyordu ve yanlıştı: o an 19 PR vardı, 18'i birleştirilmiş. Sonra "dal henüz
açılmadı" oldu ve o da bir süre sonra eskidi. Doğrusu yukarıda ve PR numarasıyla
birlikte.

### Bu maddede kayda geçen genel kurallar

Kalkan işi dört protokol kuralı doğurdu; hepsi
`experiments/setup-protocol.tr.md` içinde ve hepsi ölçülmüş bir arızadan geliyor.

| Kural | Doğuran arıza |
|---|---|
| Bir fonksiyonun davranışı değişince çağıranın düzeltilmiş yolu koştuğu ayrıca doğrulanır | Çözümleyici düzeltildi, ölçüm betiği eski yolda kaldı |
| Küçük olmak doğru olmak değil | %0,09 engelleme oranının içindeki iki saf okuma |
| Bir ölçüm, ölçtüğü şeyin üretim uygulamasını çağırır | Yeniden yazılan `writes_of` sıfır verdi, üretim yolu altı |
| Doğrulayıcıya karşı ölçülmüş olmak dal testlerinin yerine geçmez | `allowed_apps.py` %75,5 ile ölçüldü, sıfır testi vardı |

---

## Madde 2 — Beceri şartnamesi

**Durum: kapandı.** Commit'ler `51f3e0d`, `3cbd9eb`, `78134d1`, `c30ff34`.

### Ne kuruldu

Bu madde belge üretti, kod üretmedi; kodu madde 3.

| Parça | Yer |
|---|---|
| Yedi bölümlü şartname | `SKILL_SPEC.md` — kimlik, gövde, destek, ön koşul, son koşul, beklenen tasarruf, sicil |
| Son koşulun tanımı | Destekleyen epizotlardaki durum farklarının **şekil** kesişimi (kullanıcı tanımı) |
| Dokuz değişmez | Derleyicinin çıktısının sağlaması gerekenler; madde 3'ün doğrulama kapısı bunları sınıyor |
| Kütüphaneye girme şartı | Etki soneki boş olamaz (K-75); boş olanlar **keşif öneki** olarak ayrı raporlanıyor |

Son koşulun okuma düzeyi karara bağlandı — şekil, büyüklük değil — ve gerekçesi
ölçüm değil dilin kendi tasarımı: serbest parametresi olan bir beceride fark
büyüklüğü tanımı gereği değişiyor, dolayısıyla sıkı okuma hiçbir destekleyen
epizotta tutmazdı.

### Ne ölçüldü

Kayıtlı 3909 adımda (`results/pilot-dataset.json` → `record`):

| Ölçüm | Değer |
|---|---|
| Durum değişimi gösteren adım | 28 (%0,7) |
| Değişen farklı model | 18 |
| Aynı modelde birden fazla büyüklük görülen | 9 (18'in yarısı) |
| `supervisor`'ın durum farklarında görünmesi | hiç |

Son ölçüm bir kaygıyı kapattı: `state_probe` ile `allowed_apps` içindeki altyapı
listeleri farklı, ve bu fark son koşulu kirletiyor olabilirdi. Kirletmiyor.

**Üç yorum sonuç görülmeden yazıldı** (şartnamenin içinde): büyüklük sabitse sıkı
okuma geri gelir; parametreyi izliyorsa şekil okuması doğrudur; hiçbir şeyi
izlemiyorsa sonda gürültülüdür ve mekanizma askıya alınır. Madde 3'te
gerçekleşen ikincisi oldu.

### Bilerek açık bırakılanlar

- **Değer eşiği, sabit ilan etme eşiği, boşluk kısıtı** sayı olarak yazılmadı
  (K-50). Karar kuralları ön kayıtta, sayıları kurulum sonrasında.
- **Bilinen sınır yazıldı:** durum farkı satır sayımına dayanıyor, güncelleme
  görünmüyor (S-35). Son koşul aynı yerde kör.

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | **Bu madde kod üretmiyor.** Şartname belge; kodu madde 3'te ve orada sayılıyor |
| Testi yazıldı | Kısmen. Şekil okuması `3cbd9eb` ile çivilendi; dokuz değişmezin testi madde 3'te |
| Loglandı | Commit gövdelerinde |
| Belgesi yazıldı | Şartnamenin kendisi belge; K-75, S-35 |
| Hata durumu düşünüldü | Boş son koşul ile NULL ayrı; boş etki soneki kütüphaneden çıkıyor; üç yorum önceden yazıldı |
| PR üzerinden gözden geçirildi | **Evet, PR #22.** Açıklaması bu kapanış notunun kendisi, dört CI kontrolü yeşil. İnceleme yine diff üzerinden değil rapor üzerinden — yukarıdaki tanım geçerli |
| Temiz kurulumda baştan çalıştırıldı | Uygulanmaz, koşulacak bir şey yok |

---

## Madde 3 — Derleyici v0 ve `skills` tablosu

**Durum: kapandı.** Commit'ler `1d76cd4`, `7266048`, `f4d7471`, `e22b103`,
`afbef92`, `142662f`, `30233e4`.

### Ne kuruldu

| Parça | Yer |
|---|---|
| Madencilik çekirdeği | `src/zihin/compiler.py` — kapalı sıralı örüntü, boşluk kısıtı, destek görev üzerinden |
| Etki ayrımı | Yazma kümesine göre etki soneki; boş olan keşif öneki (K-75) |
| Birleştirme | Aynı etki soneki aynı beceri; arama öneki farkı beceriyi çoğaltmıyor |
| Argüman sınıflandırması | Bağlı / serbest / sabit; sıra bağlılık→değişkenlik |
| Son koşul | Destekleyen epizotların durum farklarının şekil kesişimi |
| Kontrol kanalı ayrımı | `supervisor.message` ve `complete_task` gövdeden de çıkıyor (K-80) |
| Tablo ve yazma yolu | `schema.sql` `skills`, `records.insert_skill`, `replace_library` |
| Ölçüm ve inşa betikleri | `scripts/setup/mine_skills.py` (3×7 ızgara), `build_skill_library.py` |

### Ne ölçüldü

Korpus: 22 geçen epizot, 20 görev, 854 çağrı, 46 elemanlı alfabe
(`pilot-dataset.json` → `mining_grid`).

Kurşun yapılandırma boşluk 2 / destek 3:

| Ölçüm | Değer |
|---|---|
| Kapalı örüntü | 100 |
| Etki soneki dolu | 38 |
| Birleştirme sonrası beceri | **4** |
| Keşif öneki | 62 |
| Bağlı argüman / serbest parametre | 13 / 14 |
| Son koşul | 4'ünde de boş |

Eşik duyarlılığı 21 hücrede süpürüldü: destek 2'ye inince beceri sayısı boşluk
2'de 11, boşluk 5'te 35; destek 8'de 1, destek 10'da 0.

Beklenen tasarruf iki birimde: adım tabanlı 8, 7, 20, 30; çağrı tabanlı 8, 14,
20, 30. Dört beceriden üçünde iki sayı aynı, `spotify` becerisinde iki kat fark
var — çünkü üç çağrıyı iki adımda yapıyor.

### Ölçüm sırasında bulunan ve düzeltilen kusurlar

| | Kusur | Etki |
|---|---|---|
| S-42 | Bağlılık epizot boyunca aranıyordu, gövde içinde değil | En yüksek destekli beceri parametresiz çıkıyordu ve çalışma anında parolayı elde edemezdi. Bağlı 22→13, serbest 5→14 |
| K-82 | Şartname "uzunluk eksi bir" diyordu, yani API çağrısı sayıyordu | Birincil metrik model çağrısı; tasarruf adım tabanlı oldu, çağrı tabanlı tanı olarak yanında duruyor |
| K-79 | İlk atıf uygulaması "herhangi bir adım yalıtılmışsa ölçülebilir" sayıyordu | Bir kirli epizot dört oluşumun anlaştığı kesişimi boşaltıyordu. Artık etki sonekindeki her çağrının yalıtılmış olması gerekiyor |
| — | İlk madenci sonlanmıyordu: her düzeyde bütün alfabeyi deniyor ve her oluşumu tutuyordu | Aday güdümlü genişletme, yalnız bitiş konumları |
| — | İki test yanlıştı, kod doğruydu | Kapanış filtresinin doğru davranışı boşluk hatası sanılmıştı |

### Bilerek açık bırakılanlar

- **Son koşullar boş** ve iki sebebi var (S-41): giriş çağrısı satır üretmiyor, ve
  atıf yalıtılmış adım gerektiriyor.
- **Değer eşiği uygulanmadı**, saklandı; eşik pilottan önce seçilmeyecek (K-50).
- **Destek 2 hücrelerinin beceri kimlikleri kaydedilmedi**, yalnız sayıları.

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Madenci, birleştirme, argüman sınıflandırması, son koşul, tablo, iki betik |
| Testi yazıldı | Evet. `test_compiler.py` 36, `test_skill_library.py` 15 |
| Loglandı | Commit gövdelerinde; `results/mined-skills.json` ızgarayla birlikte |
| Belgesi yazıldı | K-75, K-79…K-82, S-41, S-42; `SKILL_SPEC.md` güncellendi |
| Hata durumu düşünüldü | Dokuz değişmez doğrulama kapısında; NULL ile boş ayrı; projeksiyon silinip yeniden üretilebiliyor |
| PR üzerinden gözden geçirildi | **Evet, PR #23.** Açıklaması bu kapanış notunun kendisi, dört CI kontrolü yeşil. İnceleme yine diff üzerinden değil rapor üzerinden — yukarıdaki tanım geçerli |
| Temiz kurulumda baştan çalıştırıldı | Kısmen, ve sınırı yazılıyor. Kütüphane kayıttan üretiliyor, projeksiyonun silinip yeniden üretilebilmesi testte çivili. **Aynı kimlikle** yeniden üretme sınanmadı: kimlik derleyici commit'ini taşıyor (`v0-gap2-sup3-142662f`), yani bugün yeniden üretmek yeni bir kütüphane kimliği yazar ve ölçülmüş artefaktı yerinden oynatır. CI artık `appworld install` ve veriyi kuruyor, yani bu maddenin testleri temiz makinede gerçekten koşuyor (K-100). |

---

## Madde 4 — Hata indeksi ve `failure_patterns` tablosu

**Durum: kapandı.** Commit'ler `ecc70d9`, `771b94f`, `4bb340a`.

### Ne kuruldu

| Parça | Yer |
|---|---|
| Alt tabaka ölçümü | `scripts/setup/measure_failure_substrate.py` — **inşadan önce** koşuldu |
| Madenci | `src/zihin/failure_index.py` — gruplama, karşıtsal küme, koşul arama |
| Koşul dili | Kapalı, üç biçim; kayıtta yalnız üçüncüsü gözlenebiliyor (K-83) |
| Tablo ve yazma yolu | `schema.sql` `failure_patterns`, `records.insert_failure_pattern`, `replace_index` |
| İnşa betiği | `scripts/setup/build_failure_index.py` |

### Ne ölçüldü

Alt tabaka (`pilot-dataset.json` → `failure_substrate`): 5213 eylem, 767
başarısızlık; 401 → 498, 422 → 235, 409 → 34; 20 farklı başarısız uç, 18'inin
karşıtsal eşi var, 5'i iki ya da daha fazla görevde başarısız.

İndeks (`pilot-dataset.json` → `failure_patterns`): 15 kalıp; 11 `401`, 3 `422`,
1 `409`; 13'ünün karşıtsal eşi var, 2'sinin yok ve o ikisi koşul taşımıyor;
koşullu 13 kalıbın 12'sinde koşul çağrının kendi uygulamasına ait.

**Alt tabakanın inşadan önce ölçülmesi bir kararı önceden verdirdi:** `error_class`
tek değerli çıktı (S-44), yani sinyal durum kodunda ve indeks onun üzerine
kuruldu.

### Ölçüm sırasında bulunan ve karara bağlanan şeyler

| | Ne | Sonuç |
|---|---|---|
| K-84 | Ayna bulgusu: kütüphane jetonu almayı öğretiyor, indeks jetonu taşımamayı yasaklıyor | İki mekanizma bağımsız değil; toplanabilirlik bu korpusta muhtemelen tutmayacak |
| K-83 | Koşul dilinin dördüncü biçimi eklenmedi | Argüman bileşeni **normalize şekil**, değer değil; `access_token` şekilde kalıyor |
| K-85 | Karşıt başarısı sıfır olan kalıpta ayırt etme boş bir iddia | O kalıplar koşul taşımıyor; dört CHECK zorluyor. `splitwise.auth/logout`'un 59 koşulu böyle düştü |
| S-45 | Koşul tesadüfen ayırabiliyor | Ad hoc kısıt konmadı; kart iki tanı alanı taşıyor ve getirici okuma anında filtreliyor |
| S-43 | 409'un gerçek sebebi nesne durumu | Sınıf v0 kapsamı dışında; kapanma yolu yanıt gövdesinin kalıcılaştırılması |

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Madenci, tablo, yazma yolu, iki betik |
| Testi yazıldı | Evet. `test_failure_index.py` 14; projeksiyon testi tabloyu tanıyor (`4bb340a`) |
| Loglandı | Commit gövdelerinde; `results/failure-substrate.json` |
| Belgesi yazıldı | K-83…K-85, S-43…S-45; `07-failure-taxonomy.tr.md` ile tutarlılık denetlendi |
| Hata durumu düşünüldü | Dört CHECK koşul/işaret tutarlılığını zorluyor; kalkan ihlali tek başına kayıt üretmiyor; indeks silinip yeniden üretilebiliyor |
| PR üzerinden gözden geçirildi | **Evet, PR #24.** Açıklaması bu kapanış notunun kendisi, dört CI kontrolü yeşil. İnceleme yine diff üzerinden değil rapor üzerinden — yukarıdaki tanım geçerli |
| Temiz kurulumda baştan çalıştırıldı | Kısmen, kütüphaneyle aynı sebeple: indeks kayıttan üretiliyor ama kimliği (`v0-sup1-4bb340a`) derleyici commit'ini taşıdığı için aynı kimlikle yeniden üretme sınanmadı. CI artık `appworld install` ve veriyi kuruyor, yani bu maddenin testleri temiz makinede gerçekten koşuyor (K-100). |

---

## Madde 5 — Getirici v0

**Durum: kapandı.** Commit `4136d71`.

### Ne kuruldu

| Parça | Yer |
|---|---|
| Getirici | `src/zihin/retriever.py` — sembolik eşleşme, sembol uygulama |
| Eşleşme ölçütü | Becerinin **etki soneki**, gövdesi değil |
| Altyapı ayrımı | Getiricide düşüyor, kalkanda düşmüyor; tek çıkarım iki kullanım (K-86) |
| Filtreler | Üçü de varsayılansız argüman: değer eşiği, ayıran koşul üst sınırı, doğrulanmamış kart anahtarı |
| Ölçüm betiği | `scripts/setup/measure_retrieval.py` — 50 hücreli duyarlılık ızgarası, bölme başına |

### Ne ölçüldü

Kapsama, filtresiz tavan (`pilot-dataset.json` → `coverage`): train %96,7 /
%90,0 / %96,7; dev %94,7 / %89,5 / %94,7; test_normal %100 / %94,6 / %100
(herhangi / yalnız beceri / yalnız hata). Yanlışlama kapısı %25; dokuz ölçümün
(üç bölme × üç okuma) dokuzu üstünde.

Madencilenmemiş görevlerde kapsama düşmüyor: test_normal'ın 150 görülmemiş
görevinde %100.

**Ayırt edicilik ayrıca ölçüldü**, çünkü yüksek kapsama tek başına onu
göstermiyor (`results/retriever-discrimination.json` → `distinct_card_sets`, `most_common_set_share`).
Getirici ayırıyor — ama ayırdığı şey hangi uygulamanın girişi.

Duyarlılık: değer eşiği 10'da beceri kapsaması %94,6→%50,6, 30'da %35,7; ayıran
koşul üst sınırı 1'de hata kapsaması %100→%38,1.

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Getirici, üç filtre, ölçüm betiği |
| Testi yazıldı | Evet. `test_retriever.py` 14; ikisi mutasyon testi (gövdeye eşleşme, altyapı) |
| Loglandı | Commit gövdesinde; `results/retrieval-coverage.json` |
| Belgesi yazıldı | K-86; kapsama kapısı `05-experiment-design.tr.md` ile bağlandı |
| Hata durumu düşünüldü | Filtre verilmezse `TypeError`; NULL tasarruf küçük sayılmıyor; iki kütüphane birbirine karışmıyor |
| PR üzerinden gözden geçirildi | **Evet, PR #25.** Açıklaması bu kapanış notunun kendisi, dört CI kontrolü yeşil. İnceleme yine diff üzerinden değil rapor üzerinden — yukarıdaki tanım geçerli |
| Temiz kurulumda baştan çalıştırıldı | Evet. Ölçüm salt okunur bağlantıyla, sıfırdan koşuyor. CI artık `appworld install` ve veriyi kuruyor, yani bu maddenin testleri temiz makinede gerçekten koşuyor (K-100). |

### Bu maddede kayda geçen genel kural

| Kural | Doğuran arıza |
|---|---|
| Bir kapıya zincirlenen her komutun çıkış durumu kapıya bağlanır, ve bağ komut kasten düşürülerek sınanır | Doğrulama aleti alt süreç çıkışını denetlemiyordu; pytest çıkışı commit kapısına bağlı değildi ve takım düşerken commit geçti |

---

## Madde 6 — Mekanizma pilotu

**Durum: kapandı.** Raporu `PILOT_REPORT.md`, verisi
`results/pilot-dataset.json`.

### Ne kuruldu

| Parça | Yer |
|---|---|
| Kart biçimi | `src/zihin/cards.py` — beceri kartı yedi alan, hata kartı beş alan (K-87) |
| Jeton sayacı | `model_server.count_tokens`, `count_chat_tokens` — sunucunun kendi tokenizer'ı |
| Kart jeton ölçümü | `scripts/setup/measure_card_tokens.py` |
| Bağlam maliyeti ölçümü | `scripts/setup/measure_context_cost.py` — üretim yolu dünya açılarak doğrulanıyor |
| Pilot veri seti | `scripts/setup/build_pilot_dataset.py` → tek dosya, kaynak özetleri, tutarlılık kapısı (K-89) |
| Kirli ağaç kapısının daraltılması | `records.working_tree` + `defines_measurement` (K-76) |
| Pilot raporu | `PILOT_REPORT.md` |

### Ne ölçüldü

Şartnamede duran ama hiç sınanmamış iki ölçüm:

| Ölçüm | Sonuç |
|---|---|
| Beceri kartı | 4 kart, 78–122 jeton (medyan 88), bütçe ≤180, **aşan 0** |
| Hata kartı | 14 kart, 36–48 jeton (medyan 42), bütçe ≤120, **aşan 0** |
| Alan sayısı | Beceride 7, hatada 5; hepsinde |
| Üç modelin uyumu | Her kart için aynı sayı |
| k=5+5 blok | En çok 523 jeton; bütçe tavanı 1500 |
| Sabit blok | Medyan 3172–3185 jeton, pencerenin %9,7'si |
| Kartlarla toplam | Medyan 3296–3447 (%10,1–10,5), en çok 3645 (%11,1) |
| Tur maliyeti | Medyan 182, ortalama 419, p90 1066 jeton |
| İskelenin karakter tavanı | 50000 karakter = **12799 jeton**, pencerenin %39'u |

Korpus çeşitliliği doğrudan ölçüldü (ızgaradan çıkarım yerine): 20 geçen görev, 6
uygulama, 8 farklı uygulama kümesi; 3+ görevde tekrarlayan 14 çağrının 4'ü
altyapı, 4'ü oturum, 5'i sıradan okuma, **1'i sıradan yazma**.

### Ölçüm sırasında bulunan kusurlar

| | Kusur | Etki |
|---|---|---|
| S-46 | Mimari belgesindeki sabit blok payı ölçülmemişti ve yanlıştı | Beşte bir değil onda bir; belge düzeltildi |
| S-47 | Bağlayıcı sınırın hangi birimde olduğu bilinmiyordu | Karakter tavanı bağlıyor; pencere hiç dolmuyor |
| S-48 | İndeksin en sık kalıbı hiçbir görev tarafından getirilemiyor | Terk kriteri getirilebilir kalıp sayısına bakacak |
| K-76 | Kapı listeye daraltılırken listenin kendisi eksik çıktı | `retriever.py` ve `cards.py` eklendi; eksik girdinin bedeli daraltmayla arttı |
| — | `num_predict: 0` "üretme" demiyor | Sayaç `num_predict: 1` kullanıyor; ölçüm takıldığı için fark edildi |
| — | S-45'in kendi uygulama sayısı K-85'ten sonra eskimişti | 15 kartın 14'ü değil, koşullu 13 kartın 12'si; bölen değişmiş |

### Bilerek açık bırakılanlar

- **Pilot koşusu koşulmadı** ve koşulamaz: ön koşul kapısı ateşledi, taban sıfır
  çözüyor, adım farkı tanımsız. Raporun ilk bölümü bunu kanıtıyla söylüyor.
- **Eşikler seçilmedi** (K-50): değer eşiği, ayıran koşul üst sınırı,
  doğrulanmamış kart anahtarı. Üçü de duyarlılık ızgarasında.
- **Kart biçimi modele hiç gösterilmedi.** Bütçeye sığdığı ölçüldü; bir modelin
  onu okuyup kullanabildiği gösterilmedi. O madde 7, uçtan uca demo.
- **Zorlama kipi kurulmadı** (K-71).

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. Kart biçimi, jeton sayacı, iki ölçüm betiği, veri seti kurucusu, daraltılmış kapı |
| Testi yazıldı | Evet. `test_cards.py` 14, `test_manifest_contract.py` 68'e çıktı (kapı kapsamı için 9 yeni) |
| Loglandı | `results/card-tokens.json`, `results/context-cost.json`, `results/pilot-dataset.json` |
| Belgesi yazıldı | K-76 uygulama notu, K-87…K-89, S-46…S-48; `03-architecture.tr.md` düzeltildi; protokole bir kural |
| Hata durumu düşünüldü | Veri seti eksik girdiyle kurulmuyor; kütüphane kimliği ayrışırsa duruyor; iki AppWorld commit'i varsa duruyor; kart bütçeyi aşarsa betik düşüyor; sayaç sıfır dönerse hata fırlatıyor |
| PR üzerinden gözden geçirildi | **Evet, PR #26.** Açıklaması bu kapanış notunun kendisi, dört CI kontrolü yeşil. İnceleme yine diff üzerinden değil rapor üzerinden — yukarıdaki tanım geçerli |
| Temiz kurulumda baştan çalıştırıldı | Evet. Üç ölçüm de sıfırdan koştu; bağlam ölçümü kendi üretim yolunu dünya açarak doğruladı. CI artık `appworld install` ve veriyi kuruyor, yani bu maddenin testleri temiz makinede gerçekten koşuyor (K-100). |

### Bu maddede kayda geçen genel kural

| Kural | Doğuran ihtiyaç |
|---|---|
| Rapor sayıyı kopyalamaz, veri setine atıf verir | Sekiz ölçüm çıktısı, sekiz ayrı gün; yazma kümesi tek günde iki kez değişti ve aynı ölçüm iki farklı sayı verdi |

---

## Madde 7 — Uçtan uca demo

**Durum: kapandı.** Raporu `docs/reports/uctan-uca-demo.md`, verisi
`results/card-demo.json`.

### Ne kuruldu

| Parça | Yer |
|---|---|
| Kartlı koşu | `scripts/record_run.py --cards` — getiricinin kartlarını slota koyuyor, koşul adını kart yapılandırmasından alıyor, `library_id`'yi künyeye yazıyor |
| Demo ölçümü | `scripts/setup/measure_card_demo.py` — giriş ve kullanım ayrı, kartlı/kartsız eşleştirilmiş |
| Eşleşme araması | Derleyicinin kendi `occurrences_of`'u, boşluk 2 (K-81) |
| Devam edebilirlik | Kayıtlı epizot yeniden koşulmuyor; `UNIQUE (run_id, task_id, condition, seed)` zaten reddediyor ve yerel 7B'de bir epizot on beş dakikayı aşıyor |
| Karakter tavanı | Aynı maddede künyeye girdi (K-90); demo epizotlarının hepsi 50000 ile koştu ve künyede yazılı |

**Kart bulunamayan görevde kartlı koşu başlamıyor.** Boş slotla koşan bir epizot
künyede `library_id` taşır ve kartlı görünürdü.

### Ne ölçüldü

On epizot, beş çift, tek model (`qwen2.5-coder:7b-instruct-q4_K_M`).

**Giriş, modele bakmadan, 3/3:** blok prompt'un içinde bayt bayına; iki prompt
yalnız blok kadar farklı; kartsız kolun prompt'u referansla bayt bayına aynı
(K-25); künye özetleri farklı. Blok 125 ve 166 jeton, yani kart bütçesinin
(≤180+≤120) yarısından küçük.

**Kullanım:**

| Ölçüm | Sonuç |
|---|---|
| Soru sorulabilir görev | 2/3 (birinde iki kol da hiç çağrı üretmedi) |
| Yörünge kartsızdan farklı | 1/2 sorulabilir görevde; beş çiftin üçünde |
| Gövde eşleşmesi, kartlı | 1/3 (`0de03ea_1`: 3/3 eleman; kartsız 1/3) |
| Başarılı etkiye ulaşma | ~~kartlı 2 çift, kartsız **0** çift~~ **GERİ ÇEKİLDİ**: üç tekrarda kartsız kol 15 hücrenin 6'sında ulaşıyor (`uc-kollu-kart-kosusu.md`, S-56) |
| Doğrulayıcıyı geçen epizot | **0/10** |

En açık hâl `0de03ea_1`: kartlı kol adım 4'te başarılı giriş yaptı, adım 13'te
kendi kendine durdu; kartsız kol yirmi adımın yirmisinde aynı `api_docs` çağrısını
yaptı ve tavana çarptı. Çağrı 20 → 11.

### Ölçüm sırasında bulunan kusurlar

| | Kusur | Etki |
|---|---|---|
| Görev seçimi | İlk üç eşleşme aynı senaryonun üç varyantıydı | "Üç görev" tek kartın üç kez sınanmasıydı; ölçüte farklı senaryo şartı eklendi, koşmuş epizotlar senaryo içi tekrar olarak ayrı etiketli |
| Ön kayıt | Dört yorum "iki kol da hiç çağrı üretmedi" hâlini öngörmüyordu | Beşinci yorum eklendi: o görevde soru **sorulamaz**; iki boş dizinin eşitliği kimlik iddiası değil (K-79'un ayrımı) |
| Kullanım ölçümü | "Etkiye ulaştı" ile "başarıyla ulaştı" ayrılmamıştı | Taban kolunda iki `401` giriş denemesi etkiye ulaşma sayılıyordu ve kartın kazandığı yer beraberlik görünüyordu |
| S-45 | Kartın koşulu canlı olarak yanlış çıktı | `simple_note.notes` gerçekten `401` döndü ama kartın koşulu (`profile` çağrılmış olması) korelasyon; etiket doğru, koşul yanlış |

### Bilerek açık bırakılanlar

- **Atomik yürütme yok.** Kart diziyi yazıyor, modeli kendisi yapıyor; kırılan
  becerinin yapılandırılmış dönüşü ve üç kapılı suç atfı çalışmadı.
- **Hacim ile içerik ayrılmıyor.** Yörünge değişikliği kartın içeriğinden mi 125
  jeton fazladan metinden mi geldiği ayrılamıyor; ayrımı `irrelevant_retrieval`
  koşulu verir ve o koşul koşmadı.
- **Tek model, üç görev, kazanç iddiası yok.** Hiçbir epizot geçmedi ve geçmesi
  beklenmiyordu; ön koşul kapısı bu eksende ateşledi.
- **Kartın zarar verdiği bir çift var** (`0a9d82a_3`: kartsız 4 çağrı, kartlı 0) ve
  n=1 ile sebebi söylenemez.

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. `--cards` yolu, demo ölçümü, devam edebilirlik |
| Testi yazıldı | Evet. `tests/test_card_demo.py` 13 test; başarılı etki ayrımı, boşluk kısıtı, kısmi eşleşme, sıfır çağrılı epizot |
| Loglandı | `results/card-demo.json`; on epizot kayıtta, künyeleriyle |
| Belgesi yazıldı | K-91, ön kayıt madde 7 (dört yorum + beşinci), `docs/reports/uctan-uca-demo.md` |
| Hata durumu düşünüldü | Kart bulunamazsa koşu başlamıyor; blok girmezse betik düşüyor; kayıtlı epizot yeniden koşulmuyor; sorulamayan hâl ayrı sayılıyor |
| PR üzerinden gözden geçirildi | **Evet, PR #27.** Açıklaması bu kapanış notunun kendisi, dört CI kontrolü yeşil. İnceleme yine diff üzerinden değil rapor üzerinden — yukarıdaki tanım geçerli |
| Temiz kurulumda baştan çalıştırıldı | Evet. Ölçüm kayıttan yeniden koşuluyor ve aynı sayıları veriyor; epizotlar üretim yürütücüsünden geçti. CI artık `appworld install` ve veriyi kuruyor, yani bu maddenin testleri temiz makinede gerçekten koşuyor (K-100). |

### Kirli ağaç kapısının daraltılması burada işe yaradı

Demo saatler sürdü ve o sürede belgeler, ön kayıt ve demo betiği düzenlendi.
Kapı bütün ağaca bakıyor olsaydı her düzenleme koşan epizodu durduracaktı; liste
dışı olduğu için `working_tree()` "clean" kaldı ve koşu kesilmedi (K-76). Kararın
gerekçesi tam olarak buydu ve ilk kez burada denendi.

---

## Madde 8 — Sandbox

**Durum: kapandı.** Kapsamı `docs/12-sandbox-scope.tr.md`, ölçümleri
`results/sandbox-olcum.json`, `results/transparency.json`,
`results/container-network.json`, `results/wire-identity.json`.

Ajanın ürettiği kod artık kök yetkisiz, ağsız, salt okunur kökte bir konteynerde
koşuyor; kayıt konteynerin dışındaki bir vekilden geliyor.

### Ne kuruldu

| Parça | Yer |
|---|---|
| İmaj | `Containerfile` — tam `appworld` paketi (K-B), kilit dosyasından, 643 MB; `data/` içeride değil, salt okunur bağlanıyor |
| Konteyner yaşam döngüsü | `src/zihin/sandbox.py` — epizot başına doğ, sınırları uygula, günlükleri `podman cp` ile al, yık |
| Kayıt vekili | `src/zihin/kayit_vekili.py` — iki yönü kaydeder, tipi rota imzasından türetir, kalkanı çağırır, yönetim rotalarını alan ölçütüyle süzer |
| Köprü | `src/zihin/soket_koprusu.py` — konteyner içindeki TCP portunu bağlanan unix sokete bağlıyor; stdlib, yeni bağımlılık yok |
| Konteyner girişi | `src/zihin/konteyner_girisi.py` — köprü + AppWorld'ün kendi ortam sunucusu, miras alınan tanımlayıcı üzerinde |
| Yapılandırma | `config/sandbox.yaml` — sınırlar, imaj damgası, ağ kipi, soket yolları |
| Kayıt şeması | Künyede dokuz sandbox alanı; `steps.state_hashes` (K-93) |
| Koşucu | `scripts/record_run.py --sandbox` |

**Topoloji: iki unix soket, iki yönde, ve konteynerin hiç ağı yok.** Konteyner →
host yönü salt okunur bağlanan soketle; host → konteyner yönü host'un bağlayıp
tanımlayıcısını `--preserve-fds` ile geçirdiği soketle. İkincisi konteynerin
dizine yazmasını gerektirmiyor, yani "yazılabilir bağlama yok" kuralı (K-94) ile
"host içeri ulaşabilsin" şartı çakışmıyor.

### Ne ölçüldü

**Şeffaflık testi — K-A'nın birinci şartı.** Üç kol, aynı görev, aynı yedi kod
bloğu; ölçüt ajanın gördüğü metnin tamamı:

| Kol | `sha256(environment_io.md)` |
|---|---|
| Süreç içi | `5e4812502f278f0b` |
| Sunulan, vekilsiz | `5e4812502f278f0b` |
| Sunulan + vekil | `5e4812502f278f0b` |

Üç kol, çünkü kip değişimi ile vekil aynı testte karışırsa çıkan fark
atfedilemez.

**Kimlik doğrulaması — K-92.** Kayıttaki 5261 eylemin **5261'i** imzadan
türetilen tiple eşleşiyor; imzaya bakmayan kontrol kolunda **1090'ı**
eşleşmiyor, ve o sayı bağımsız ölçülen "metin olmayan değer taşıyan GET"
sayısıyla birebir aynı.

**Ağ politikası — iki platformda.** `--network=none` sıfır erişim veriyor;
varsayılan netavark, `pasta` ve `slirp4netns` üçü de dış ağa çıkıyor (1.1.1.1
403 dönüyor, yani istek internete ulaşıyor). Salt okunur bağlanan sokete
`connect` çalışıyor — bu bir riskti, ölçüldü.

**Kaynak sınırları — K-C.** `6104387_1` konteynerde üç kez koşuldu, kullanım iki
saniyede bir örneklendi:

| | Ölçülen tepe | Sınır | Pay | Kullanım |
|---|---|---|---|---|
| Bellek | 158,0 MiB | 512 MiB | 3,2 kat | %29,4 |
| Süreç | 4 | 128 | 32 kat | %3 |
| tmpfs | ~32 KiB | 64 MiB | 2000 kat | %0,05 |
| CPU | %62,5 | 1 çekirdek | — | %62,5 |

**Hiçbiri bağlamadı** ve K-D'nin göstergesi bu: sınıra çarparak biten epizot
0/3. Ölçümün sınırı yazılı: tek görev, tek model, 20 adım, ve örnekleme aralığı
bir tepeyi kaçırabilir.

**Yönetim trafiği.** Ortam sunucusunun kendisi on bir yönetim çağrısı yapıyor.
Politika gerçek trafiğin 11'ini geçiriyor, kurcalanmış 12 denemenin 12'sini
kesiyor.

**S-50'nin kalan sınırı.** Ajan tetikli bir `/dbs/save` sondanın göreceği
değişiklikleri **tüketmiyor** (ölçüldü); `SO_PEERCRED` ayıramıyor çünkü ajanın
kodu konteynerde pid 1, yani ortam sunucusuyla aynı süreç; ve ajanın kodundan
çalışan bir yol bulunamadı (beş deneme, AppWorld'ün kendi guard'ı dördünü
kesiyor).

### Ölçüm sırasında bulunan kusurlar

Yedisi de "çalışıyor gibi görünüp yanlış sebeple çalışan" sınıfından ve altısı
bizim kendi kodumuzda.

| | Kusur | Etki |
|---|---|---|
| Kaydedici | Referans ajan `batch_execute` çağırıyor, `execute` değil; uzak kipte sarmalayıcı hiç ateşlemiyordu | Epizot koştu, 32 KB yörünge üretti, kayda **sıfır adım** yazdı ve sessiz kaldı (S-53) |
| Eylem kaynağı | `api_calls.jsonl` sandbox kipinde konteynerin içinde; yokluğu "sıfır çağrı" diye okunuyordu | Adımlar geldi, eylemler sıfır kaldı |
| Tanımlayıcı | `dup2(fd, 3)` ebeveynde yapılıyordu ve vekil önce başladığında onun soketini eziyordu | Hata vermeyen ama çalışmayan bir köprü |
| Kabuk | dash tek haneli olmayan tanımlayıcıyı `Bad fd number` ile reddediyor | Taşıma belirlenimci bir Python fırlatıcısına taşındı |
| Hazırlık denetimi | Yalnız "200 döndü mü" diye soruyordu | Yanlış portta host'un API sunucusu cevap verdi ve "ortam hazır" sanıldı |
| Köprü portu | Bir iş parçacığında bağlanıyordu, "port meşgul" yutuluyordu | Koşu artakalan bir sunucuya gitti |
| `podman cp` | Var olan dizine kopyalarken içine yerleştiriyor | Günlükler `logs/logs/` altına düştü |

Bir de birinci turdaki güvenlik ölçümünde üç adım yeşil yanıp hiçbir şey
kanıtlamıyordu (bellek `/dev/shm` varsayılanına çarpmış, tmpfs çıkış kodu
`tail`den gelmiş, loopback testinde host'ta dinleyici yok).

### Bilerek açık bırakılanlar

- **Konteynerin içi güvenli değil ve olması amaçlanmıyor** (S-51). Ortam sunucusu
  ajanın koduyla aynı süreç; bu K-B'nin doğrudan sonucu. Korunan şey host.
- **`error_class` sandbox kipinde NULL** (S-52). Telde istisna yok. Alan zaten
  durum kodundan bire bir türetilebiliyordu; uydurulmadı.
- **Durum sondasının kör noktası ileriye dönük kapandı** (S-54). Mevcut kütüphane
  ve indeks eski sondayla madenlendi.
- **Kalkanın uygulama kipi hâlâ yok** (K-71). Vekilin rota filtresi ondan ayrı
  bir katman.

### Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet. İmaj, konteyner yaşam döngüsü, vekil, köprü, giriş noktası, yapılandırma, şema alanları, koşucu bayrağı |
| Testi yazıldı | Evet. 55 yeni test: `test_sandbox_security.py` 11 (hepsi iki kollu), `test_kayit_vekili.py` 33, `test_sandbox_config.py` 11 |
| Loglandı | `results/sandbox-olcum.json`, `transparency.json`, `container-network.json`, `wire-identity.json`; epizot 118 kayıtta, künyesinde sandbox alanları dolu |
| Belgesi yazıldı | K-92…K-98, `docs/12-sandbox-scope.tr.md` (+ İngilizce eşi), tehdit modeli güncellemesi, S-50…S-54 |
| Hata durumu düşünüldü | Kimlik teyidi (K-98); port meşgulse koşu düşüyor; imaj yoksa düşüyor; kaydedici takılmamışsa epizot satırı yazılmıyor; reddedilen istek sesli |
| PR üzerinden gözden geçirildi | **Evet, PR #29.** Açıklaması bu kapanış notu; beş CI kontrolü yeşil |
| Temiz kurulumda baştan çalıştırıldı | Büyük ölçüde. Güvenlik testlerinin on biri de CI'da temiz makinede koşuyor — `appworld install` ve veri CI'a girdikten sonra görev verisi isteyen ikisi de dahil (K-100). Kalan boşluk uçtan uca epizot: model sunucusu CI'da yok ve olması da beklenmiyor |

### Bu maddede kayda geçen genel kural

**Bir koşu, başlattığı şeyle konuştuğunu doğrulamadan sayılmaz** (K-98).
Artakalan bir durum bu depoda üç kez yanlış yeşil üretti: mutasyon betiği kirli
zeminde koştu, doğrulama aleti bayat dosya okudu, ve burada konteyner hiç
başlamadığı hâlde epizot artakalan bir sunucuya koşup temiz göründü.
