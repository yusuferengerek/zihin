# Üç kollu kart koşusu — 45 epizot, tek commit

**Gösterimsel, istatistiksel değil.** Beş görev ve üç tekrar ayırt edici güç
vermiyor. Bu koşu bir kazanç iddiası taşımıyor; taşıdığı tek şey, demonun
iddiasının tekrar altında ayakta kalıp kalmadığı.

Sayılar `results/card-arms.json` içinde. Koşu öneki `uckol`, commit `9a42ac4`,
model `qwen2.5-coder:7b-instruct-q4_K_M`, hepsi aynı commit'te. Yorum
`experiments/setup-protocol.tr.md` §12'de **koşudan önce** ilan edildi.

## 1. Görev başına, kol başına, tekrar başına

`geçti/adım/sonlanma`. Kırk beş epizodun **hiçbiri görevi geçmedi.**

| görev | kol | r0 | r1 | r2 |
|---|---|---|---|---|
| `0de03ea_1` | cards | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| | baseline | fail/20/ceiling | fail/4/finished | fail/11/finished |
| | irrelevant | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| `1150ed6_2` | cards | fail/9/finished | fail/20/ceiling | fail/20/ceiling |
| | baseline | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| | irrelevant | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| `0a9d82a_1` | cards | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| | baseline | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| | irrelevant | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| `0a9d82a_2` | cards | fail/11/finished | fail/20/ceiling | fail/20/ceiling |
| | baseline | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| | irrelevant | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| `0a9d82a_3` | cards | fail/20/ceiling | fail/8/finished | fail/20/ceiling |
| | baseline | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |
| | irrelevant | fail/20/ceiling | fail/20/ceiling | fail/20/ceiling |

Kolların birbirinden gerçekten farklı olduğu künyeden okunuyor: aynı görevde üç
kolun `instruction_file_digest` değeri üç ayrı değer (`a4c24f4b…` / `c41f7852…` /
`dc4cf77a…`).

## 2. Demonun kendi ölçütü: etkiye ulaşma

Görev geçme ölçütü sıfır olduğu için asıl karşılaştırma demonun kullandığı ölçüt:
kartın etki soneki (`POST <uygulama>.auth/token`) epizotta geçti mi, ve **2xx ile
mi** geçti.

Üç tekrarın kaçında başarılı etkiye ulaşıldı:

| görev | cards | baseline | irrelevant |
|---|---|---|---|
| `0de03ea_1` | 2/3 | 2/3 | 2/3 |
| `1150ed6_2` | 2/3 | 0/3 | 0/3 |
| `0a9d82a_1` | 1/3 | 1/3 | 1/3 |
| `0a9d82a_2` | 1/3 | 2/3 | 0/3 |
| `0a9d82a_3` | 1/3 | 1/3 | 0/3 |
| **toplam** | **7/15** | **6/15** | **3/15** |

## 3. Kararlılık — önceden ilan edilen kurala göre

Bir hücre, üç tekrarı da aynı cevabı veriyorsa kararlı. Demonun ölçütünde:

**Üç tekrarın uyuştuğu hücre: 4/15. Ayrıştığı: 11/15.**

Protokol §12.3 şunu yazıyordu: *"Çoğunda ayrışıyorsa demonun 'kartlı 2 çift,
kartsız 0' iddiası desteklenmiyor ve geri çekilir."*

**On beş hücrenin on biri ayrışıyor. İddia geri çekiliyor.**

Geri çekilen tam olarak şu: demonun tek epizotluk kollarında kartlı kol iki
çiftte başarılı etkiye ulaşmış, kartsız kol hiçbirinde ulaşmamıştı. Üç tekrarda
kartsız kol 15 hücrenin 6'sında başarılı etkiye ulaşıyor. Tek epizot, kolları
ayırmıyordu; ayırdığını sandığımız şey gürültüydü.

**Düzeltme, 16 Kasım 2026: kartsız kolun 15'i.** Bir önceki paragraftaki "kartsız kol 15
hücrenin 6'sında" cümlesi hücre değil epizot sayıyor. §2'nin tablosu kartsız kolu görev
başına üç tekrar üzerinden sayıyor, yani bu 15 epizot (beş görev, üçer tekrar) ve 6/15 o
tablonun toplamı. "On beş hücrenin on biri ayrışıyor" cümlesindeki 15 ise hücre (beş görev,
üç kol). Hiçbir sayı değişmiyor.

## 4. Kol karşılaştırması

Önceden ilan edilen tablo üç sonuç öngörüyordu: alakasız kol kartlıya yakınsa
etki hacim ve biçimden, kartsıza yakınsa içerikten, arada kalırsa n=5'te
yorumlanamaz.

Çıkan desen üçüne de uymuyor: **alakasız kol her ikisinin de altında**
(3/15 karşı 7/15 ve 6/15). Kartlı ile kartsız arasında ise fark yok denecek
kadar az (7 karşı 6).

On beş hücrenin on biri kararsızken bu farkların hiçbiri yorumlanamaz. Doğru
ifade şu: **bu düzenekte üç kol birbirinden ayrılmıyor, ve ayrılmama sebebi
gürültü tabanının kolların arasındaki farktan büyük olması.**

Alakasız kolun düşük çıkması bir "kart zararlı" bulgusu **değil**; 3/15 ile 6/15
arasındaki fark, aynı hücrede üç tekrarın kendi arasında ayrıştığı bir düzenekte
gürültünün içinde kalıyor.

## 5. Alakasız kolun sınırı — koşmadan önce yazılmıştı

`experiments/setup-protocol.tr.md` §12.2'de ölçülerek yazıldı: kütüphanedeki dört
becerinin dördünün de etki soneki bir `auth/token` POST'u, ve gövdeler aynı
iskeleti taşıyor. Başka uygulamadan gelen kart da aynı dersi veriyor.

Dolayısıyla bu kütüphanede alakasız kontrol **içerik ile şablonu ayıramaz**;
ayırdığı tek şey kart biçimli metin ile kart biçimli olmayan metin. Bu koşu o
sınırı değiştirmiyor, ve zaten değiştiremezdi.

Ek bir homojenlik koşarken ölçüldü: beş görev yalnız iki uygulamaya değiyor
(`spotify` ×2, `simple_note` ×3), yani beş görev beş bağımsız deneme değil.

## 6. Ne öğrenildi

1. **Tek epizotluk kol karşılaştırması bu modelde bilgi taşımıyor.** Gürültü
   tabanı sıfır değil ve kolların arasındaki farktan büyük.
2. **Demonun kartlı/kartsız iddiası geri çekildi.** Kayıt silinmiyor; epizotlar
   eski commit ölçümü olarak yerinde duruyor.
3. **Kütüphane içerik atfı için fazla homojen.** Bu, koşudan önce yazılmış
   beklentinin gerçekleşmesi; bir başarısızlık değil, ölçülmüş bir sonuç.
4. Bir sonraki turda kart mekanizması hakkında bir şey söylenecekse, önce
   yapısal olarak farklı beceriler taşıyan bir korpus, sonra hücre başına üçten
   fazla tekrar gerekiyor.
