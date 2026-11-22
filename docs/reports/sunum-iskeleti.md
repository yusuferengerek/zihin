# Final sunumu — iskelet

**Bu belge bir sunum değil, bir kapsama testi.** Sunum iddia iddia kuruluyor ve
her iddianın yanında bir **atıf yuvası** var. Yuva doluysa iddia söylenebilir.
Yuva boşsa iddia söylenemez — ve boş yuvalar bulgunun kendisi.

Yöntemin sebebi: bir sunum yazarken en kolay hata, elde sayısı olmayan bir
cümleyi doğal göründüğü için söylemek. İskeleti önce kurmak o cümleleri ölçümden
önce görünür kılıyor.

Sayılar burada kopyalanmıyor, dosya ve içindeki yol gösteriliyor (protokol §6).

---

## Kapsama özeti — önce bu

<!-- KAPSAMA BASLANGIC: uretilmis, elle duzenlenmiyor -->

| Katman | İddia sayısı | Atfı olan | Boş |
|---|---|---|---|
| Problem ve tasarım | 4 | 4 | 0 |
| Kurulan mekanizmalar | 8 | 8 | 0 |
| Ölçüm altyapısı ve dürüstlük kontrolleri | 6 | 6 | 0 |
| **Nedensel iddialar** | **7** | 0 | **7** |
| Neden boş | 5 | 5 | 0 |
| Sınırlamalar | 5 | 5 | 0 |
| **Toplam** | **35** | **28** | **7** |

Bu tablo üretiliyor; elle düzenlenen bir kopyası yok (`scripts/build_skeleton_coverage.py`). Sayılar aşağıdaki iddia satırlarından sayılıyor, ayrıca yazılmıyor.

<!-- KAPSAMA BITIS -->

**Boş yuvaların hepsi tek bir yerde toplanıyor ve bu tesadüf değil.** Nedensel
katmanın tamamı boş, çünkü ön koşul kapısı ateşledi ve hipotez hiç test
edilmedi. Sunumun omurgası bu olmak zorunda: *mekanizmalar kuruldu ve
çalıştıkları gösterildi; hipotez test edilmedi ve sebebi ölçüldü.*

---

## 1. Problem ve tasarım

| # | İddia | Atıf yuvası | Durum |
|---|---|---|---|
| 1.1 | Ajanlar aynı çağrı dizilerini görevden göreve yeniden keşfediyor | `results/pilot-dataset.json` → `mining_grid`, `skills` | **dolu** |
| 1.2 | Ölçülecek şey başarı değil, çözüme giden yolun uzunluğu | `docs/02-research-question.tr.md` | **dolu** (tasarım kararı, sayı gerektirmiyor) |
| 1.3 | Altı koşul her birini tek bir şeyi izole edecek biçimde ayırıyor | `docs/05-experiment-design.tr.md` → "Koşullar" | **dolu** |
| 1.4 | Bağlam hacmi ile içerik ayrılmadan kazanç yorumlanamaz | `docs/05-experiment-design.tr.md` → "İki kritik kontrast" | **dolu** |

## 2. Kurulan mekanizmalar

| # | İddia | Atıf yuvası | Durum |
|---|---|---|---|
| 2.1 | Beceri derleyicisi kayıttan kütüphane üretiyor | `results/pilot-dataset.json` → `skills` | **dolu** |
| 2.2 | Hata indeksi kayıttan kalıp çıkarıyor | `results/pilot-dataset.json` → `failure_patterns` | **dolu** |
| 2.3 | Sembolik getirici göreve kart eşliyor | `results/pilot-dataset.json` → `coverage.per_split` | **dolu** |
| 2.4 | Kalkan her koşulda açık ve maliyeti ölçüldü | `results/pilot-dataset.json` → `shield.false_positive_rate` | **dolu** |
| 2.5 | Kart biçimi ilan edilen jeton bütçesine sığıyor | `results/pilot-dataset.json` → `card_tokens` | **dolu** |
| 2.6 | Birleştirilmiş bağlam 32K pencereye sığıyor | `results/pilot-dataset.json` → `context_cost` | **dolu** |
| 2.7 | Ajanın kodu yalıtılmış bir konteynerde koşuyor | `results/sandbox-olcum.json` | **dolu** |
| 2.8 | Kartlar prompt'a bayt bayına giriyor; fark yalnız kart bloğu | `results/card-demo.json` → `tasks[].entry`, üç görevde 3/3 | **dolu** |

## 3. Ölçüm altyapısı ve dürüstlük kontrolleri

Bu bölüm sunumun ayırt edici tarafı: ölçümün kendisinin ne kadar sınandığı.

| # | İddia | Atıf yuvası | Durum |
|---|---|---|---|
| 3.1 | Kayıt yalnız ekleme; projeksiyon silinip yeniden üretilebiliyor | `DATA_MODEL.md`, `tests/test_record_schema.py` | **dolu** |
| 3.2 | Sandbox katmanı ajanın gördüğü metni değiştirmiyor | `results/transparency.json` → üç kolun özeti | **dolu** |
| 3.3 | Altı güvenlik korumasının her biri ateşlerken görüldü | `tests/test_sandbox_security.py`, CI "Sandbox" kontrolü | **dolu** |
| 3.4 | Vekilin ürettiği kimlik kayıtlı kimlikle aynı | `results/wire-identity.json` → imzalı ve imzasız kol | **dolu** |
| 3.5 | Model yörüngeleri tekdüze; artık varyansa üst sınır yazıldı | `results/determinizm/`, S-21 | **dolu** |
| 3.6 | CI temiz makinede kurulumla koşuyor | `results/ci-kapsam.json` | **dolu** |

## 4. Nedensel iddialar — **hepsi boş**

Sunumun asıl iddia edeceği katman bu ve tamamı atıfsız.

| # | İddia | Atıf yuvası | Durum |
|---|---|---|---|
| 4.1 | Mekanizmalar model çağrısı sayısını düşürüyor | — | **BOŞ** — birincil hücre hiç koşulmadı |
| 4.2 | Kazanç bağlam hacminden değil içerikten geliyor | — | **BOŞ** — alakasız kol koşuldu (`results/card-arms.json`) ama kütüphane içerik atfı için fazla homojen: dört becerinin dördü de giriş (protokol §12.2). Kol ayrımı ayrıca gürültü tabanının altında kaldı (S-56) |
| 4.3 | Kazanç ezberlemeden gelmiyor | — | **BOŞ** — ezberleme kapısı ölçülmedi |
| 4.4 | Etki model boyutuyla değişiyor / değişmiyor | — | **BOŞ** — ölçek ekseni koşulmadı |
| 4.5 | Bizim derleyicimiz naif bir derleyiciden iyi | — | **BOŞ** — naif derleyici yazılmadı |
| 4.6 | Beceriler ile hata indeksinin etkisi toplanabilir | — | **BOŞ** — ve ayna bulgusu (K-84) toplanabilir olmayacağını **önceden** söylüyor |
| 4.7 | Kartlar modelin davranışını değiştiriyor | — | **BOŞ** — demonun bu iddiası tekrar altında geri çekildi (S-56); giriş iddiası (2.8) etkilenmedi |

**Bu tablo sunumda gösterilecek.** Boş yuvaları gizleyip yalnız dolu olanları
anlatmak, kurulum çalışmasını sonuç gibi sunmak olurdu.

## 5. Neden boş — ölçülmüş cevap

| # | İddia | Atıf yuvası | Durum |
|---|---|---|---|
| 5.1 | Ön koşul kapısı 11 Ağustos 2026'da ateşledi | `results/pilot-dataset.json` → `precondition_gate.fired_on` | **dolu** |
| 5.2 | Üç yerel model otuz görevde sıfır çözdü | `precondition_gate.local_axis` | **dolu** |
| 5.3 | Sıfır, durma kuralının artefaktı değil | `precondition_gate.local_axis_stopping_rule_off` (kural kapalı, 26 epizot, 0) | **dolu** |
| 5.4 | Sıfır, düzeneğin değil modelin sonucu | `precondition_gate.boundary_control` | **dolu, ama koşullu** — aşağı bak |
| 5.5 | Üç tabakalama denendi, hiçbiri bant açmadı | `docs/reports/teshis.md` | **dolu** |

**5.4 için sabitlenmiş yazı kısıtı.** Söylenebilecek hâli şu:

> DeepSeek V4 Flash 0731 aynı otuz görevde bizim hattımızda 20/30 aldı: on üçü
> durma kuralı **açıkken**, yedisi kuralın kestiği on altı görev kural
> **kapalıyken** tekrar koşulduğunda. O koşularda düşünme açıktı ve bu ilan
> edilen koşul değildi.

Her iki nitelik de cümlenin parçası. Kısaltılmış hâli — "20/30" ya da "kuralla
20/30" — savunmada eksik kalır, çünkü sayı tek bir koşunun tek bir koşuldaki
sonucu değil.

**"Düşünme kapalı, 20/30" cümlesi kurulamaz** (S-34). Slaytta da, konuşmada da.

## 6. Sınırlamalar — sunumda açıkça

| # | İddia | Atıf yuvası | Durum |
|---|---|---|---|
| 6.1 | Kapsama yüksek ama tek boyutlu | `coverage.per_split`, S-48 | **dolu** |
| 6.2 | Kütüphanenin dördü de giriş; korpus çeşitliliği bulgusu | `corpus_diversity` | **dolu** |
| 6.3 | Sıfır engelleme kalkanın ucuz olduğunun kanıtı değil | `shield.block_rate`, PILOT_REPORT | **dolu** |
| 6.4 | Tasarruf kestirimleri zayıf modeller için alt sınır | `skills[].expected_saving`, PILOT_REPORT | **dolu** |
| 6.5 | Konteynerin içi güvenli değil ve olması amaçlanmıyor | S-51 | **dolu** |

---

## Çapraz kontrol — iddialar ile sınırlama haritası

**Soru.** Bir iddianın sıfır sınırlaması olması iki farklı şey olabilir: iddia
iyi desteklendiği için sınırlaması yoktur, ya da sınırlamasını yazmayı unuttuk.
İkisi aynı görünüyor ve ayrılmaları gerekiyor.

**Yöntem ve sınırı.** İki liste farklı anahtarlıyor: iskelet **kanıt eserlerine**
(`results/*.json`, belge bölümleri), sınırlama haritası **belge ve kararlara**
(`07-failure-taxonomy`, `K-58`). Aradaki bağ türetilmiyor, **elle kuruluyor**, ve
ölçütü şu: kayıt okunduğunda iddianın söylediğini kısıtlıyor mu. Bu bir yargı,
ölçüm değil — haritanın kendi ölçütünün (K-107) tersi yönde uygulanmış hâli ve
o yönde ad verme disiplini yok.

**Sayılar.** 35 iddia, 33 açık sınırlama, 23 iddia anahtarı. On dokuz iddianın
en az bir sınırlaması var; on altısının hiç yok. On altı üç gruba ayrılıyor.

### A. İddia yok — boş nedensel yuva (3)

`4.1`, `4.3`, `4.5`. Sınırlaması olmaması bilgi taşımıyor: kısıtlanacak bir
cümle yok.

**Beklenenden az.** Yedi boş yuvanın yalnız üçü burada; `4.2`, `4.4`, `4.6` ve
`4.7` zaten sınırlama taşıyor (`S-56`, `S-14`, `S-57`, `S-56`). Boş bir yuvanın
sınırlaması olabiliyor, çünkü sınırlama iddianın neden kurulamadığını da
kaydediyor.

### B. Kendisi sınırlama (3)

`6.2`, `6.3`, `6.4`. Bölüm 6'nın iddiaları zaten sınırlama; üstlerine bir
sınırlama aramak sınırlamanın sınırlamasını aramak olurdu. `6.1` ve `6.5`
buraya düşmüyor çünkü kimlik adlandırıyorlar.

### C. Gerçek soru (10)

Kalanlar. Her birinin yanında **bir okuma** var, ölçüm değil.

| # | İddia | Okuma |
|---|---|---|
| 1.1 | Ajanlar aynı çağrı dizilerini yeniden keşfediyor | **yazılmamış** — kanıt, madenciliğin dördü de giriş çıkan bir korpus (`6.2`); yeniden keşif iddiası tek kalıp ailesine dayanıyor |
| 1.2 | Ölçülecek şey yolun uzunluğu | **anahtarlama boşluğu** — `S-17` yolun birimini tartışıyor ve yalnız sansür oranına anahtarlanmış |
| 1.3 | Altı koşul her birini tek şeyi izole ediyor | **yazılmamış** — izolasyonun koşulan tek örneği (alakasız kol) kütüphane homojenliğiyle karıştı ve ayrım gürültü tabanının altında kaldı |
| 1.4 | Hacim ile içerik ayrılmadan kazanç yorumlanamaz | **yazılmamış** — ayrımın aracı `1.3` ile aynı ve aynı sebeple çalışmadı |
| 2.5 | Kart biçimi ilan edilen jeton bütçesine sığıyor | **anahtarlama boşluğu** — `S-47` bağlayıcı sınırın jeton değil karakter olduğunu söylüyor, ve `03-architecture`'a anahtarlanmış |
| 2.8 | Kartlar prompt'a bayt bayına giriyor | **yazılmamış** — üç görev, tek model, tek commit; giriş mekanizması geri çekilmeden kurtuldu ama örneklemi üç |
| 3.2 | Sandbox katmanı ajanın gördüğü metni değiştirmiyor | **yazılmamış** — ölçüm sabit bir CODE dizisiyle koşuyor ve demo epizotlarını dışlıyor (K-96); keyfî ajan davranışı için gösterilmedi |
| 3.3 | Altı güvenlik koruması ateşlerken görüldü | **muhtemelen yeterli** — `6.5` konteynerin içinin güvenli olmadığını zaten söylüyor; en zayıf aday |
| 3.4 | Vekilin ürettiği kimlik kayıtlı kimlikle aynı | **yazılmamış, ve izi var** — `S-36`'nın kapanış notu "kayıtta hiç görülmemiş bir yol/yöntem çifti sınanmadı" diyor; bu artığı taşıyan açık kayıt yok |
| 5.5 | Üç tabakalama denendi, hiçbiri bant açmadı | **yazılmamış** — üç tabakalama, dördüncüsünün olmadığının kanıtı değil |

**`3.4` yöntem olarak dikkate değer.** Kapanış notlarındaki "neyin kapanmadığı"
paragrafı bir artığı adıyla yazmıştı, ve o artık hiçbir açık kayda geçmedi. Aşırı
kapatmama disiplini artığı görünür kıldı; onu bir kayda taşımak ayrı bir adım ve
atlandı.

### Ters yön — sınırlaması olup iddiası olmayanlar (5)

`S-04` (doğrulayıcı hükmünün bileşenleri), `S-22` (sansür oranı), `S-24` (dış
inceleme ön koşul sorusunu sormadı), `S-33` (karar kaydının projeksiyonu),
`S-50` (yönetim rotaları). Bunlar bir iddiayı sınırlıyor ama sunum o iddiayı
kurmuyor. `S-33` iç araç, sorun değil; `S-04`, `S-22` ve `S-50` sunumun
kurmadığı ama ölçümün dayandığı cümleleri kısıtlıyor.

### İki bayat atıf düzeltildi

`6.1` `S-31`'e atıf veriyordu; `S-31` devam mantığıyla ilgili ve bu turda
kapandı, kapsamayla ilgisi yok. Kapsamadan söz eden tek açık kayıt `S-48` ve
içeriği tam olarak "kapsama tek boyutlu"; atıf ona çevrildi. Slayt sırasındaki
`2.1–2.7` ve `4.1–4.6` aralıkları da satırlarla uyuşmuyordu.

**Bu bölüm sınırlama belgesine kayıt eklemiyor.** On aday orada değil, burada;
yazılmaları ayrı bir karar ve çeviri borcunu büyütüyor.

---

## Slayt sırası önerisi

İskeletin iddia sırası ile anlatım sırası aynı olmak zorunda değil. Önerilen
sıra, boş yuvayı saklamak yerine ona doğru yürüyen bir sıra:

1. Soru ve neden ölçmesi zor (1.2, 1.4)
2. Ne kuruldu (2.1–2.8), her biri tek slayt değil tek tabloda
3. **Ön koşul kapısı ve ateşlemesi** (5.1–5.5) — burada anlatı kırılıyor
4. Buna rağmen ne gösterildi: mekanizmalar çalışıyor (3.1–3.6)
5. Ne gösterilemedi ve neden (4.1–4.7 tablosu, olduğu gibi)
6. Sınırlamalar (6.1–6.5)
7. Bundan sonra ne gerekiyor: aile yeniden seçimi, sonra ön kayıt Bölüm A'nın
   bağladığı koşu

**Üçüncü adımın yeri önemli.** Kapı ateşlemesini sona bırakmak, dinleyiciye
sonucu olan bir çalışma izlenimi verip sonunda geri almak olur.

---

## Bu iskeletin kendi sınırı

İskelet, iddiaların **atfı olup olmadığını** gösteriyor; atfın **doğru** olup
olmadığını göstermiyor. Dolu bir yuva yanlış bir sayıya da işaret edebilir. Bu
belge o denetimi yapmıyor ve yapmadığını söylüyor.
