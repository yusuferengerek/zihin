# Kurulum sonrası 2 — Artık varyans ve adım taksonomisi

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

## Önce bir cevap: 7B temiz sayaçla mı koştu

Evet. Yakalayıcı düzeltmesi 3B ve 7B koşularından **önce** yapıldı; ilk 1.5B
koşusu düzeltmeden önceydi ve tek ayrışma gösteren o oldu.

Kanıt kayıtta duruyor. Kirli sayaç her adımda çerçevenin iç çağrısını fazladan
sayıyordu, yani eylem üreten her epizot ayrışma gösterirdi. Kayıtlarda 3B ve
7B'nin sayım ayrışması yok; ilk 1.5B koşusunda on koşunun onunda da var.

Yine de 7B ölçümü tekrarlandı, çünkü artık varyans ölçümü ikinci bir bağımsız
örneklem istiyor. Sonuçlar aşağıda.

## Artık varyans

Aynı görev (`82e2fac_1`), aynı seed (2773802488), aynı koşul, model başına on
soğuk epizot. Her epizottan önce model boşaltıldı ve boşaldığı doğrulandı.

| Model | Koşu | Farklı yörünge | Dağılım |
|---|---|---|---|
| 1.5B | 10 | 1 | `d2b4954cc6fc05e3` ×10 |
| 3B | 10 | 1 | `e85fb237a7fcf621` ×10 |
| 7B, birinci parti | 10 | 2 | `6fb9c5fc4d8d62b2` ×9, `a224f9753ae5c0e7` ×1 |
| 7B, ikinci parti | 10 | 1 | `6fb9c5fc4d8d62b2` ×10 |

**7B'nin ayrışma oranı 1/10 değil, yirmi epizotta bir.** İkinci parti tamamen
tekdüze çıktı. İki parti arasında modeli etkileyen hiçbir şey değişmedi; ilk
parti de düzeltilmiş sayaçla koşmuştu.

Bu, K-51'in istediği şeyin ta kendisi: ikili bir varsayım değil, ölçülmüş bir
büyüklük. 1.5B ve 3B'de artık varyans sıfır, yani gürültü tabanına katkıları da
sıfır. 7B'de yirmide bir ve ayrışan koşu 12 adım yerine 6 adımda bitiyor,
API çağrısı sayısı ikisinde de aynı.

Boşaltma kırk epizodun kırkında da doğrulandı, yani ayrışmanın sebebi rejim
karışması değil. Tohum ekseni de üç modelde de canlı: ikinci tohum her seferinde
farklı yörünge verdi.

**Ölçümün sınırı.** Tek görev ve iki parti. Yirmide bir oranı bir nokta
kestirimi; pilotun tekrar koşuları bunu daraltacak.

## Sıfır çağrılı epizotların sınıflandırması

S-19'u taban ilan etmeden önce adımları K-36'nın kategorilerine dağıttım.
Sonuç teşhisi değiştiriyor.

### 3B: 200 adımın 200'ü de aynı hata

On epizot, epizot başına yirmi adım, hepsi `execution_error_no_action`. Yani
kod üretildi, ayrıştırıldı, ama hiç eylem üretmeden yürütme düştü. Ve hepsinde
aynı satır:

```
NameError: name 'playlists' is not defined
```

**Mekanizma prompt'un içinde.** Referans yönergenin örnek çözümü `playlists = []`
tanımlayıp sayfa sayfa dolduruyor, sonra `for playlist in playlists:` ile
geziyor. Model örneğin ikinci kısmını kopyalıyor ama tanımı taşımıyor. Aynı
hata Aşama 2'de 1.5B'nin boş başarı epizodunda da çıkmıştı, yani desen modele
değil iskeleye ait.

**Teşhis "model zayıf" değil.** Yetenek tabanı olsaydı 3B'nin 1.5B'den kötü
olması beklenmezdi; oysa 1.5B aynı görevde on dokuz çağrı yapıyor.

### 7B: üç kategori bir arada

Yüz yirmi adımın dağılımı: 40 adım eylem üretti, 60 adım
`execution_ok_no_action`, 20 adım `no_code`.

Epizot başına dörde bölünürse: dört adım eylem üretiyor, altı adım yürütmeyi
başarıyla bitirip hiç eylem üretmiyor, iki adım hiç kod üretmiyor.

Altı adımlık `execution_ok_no_action` payı dikkat çekici. Bu K-36'nın beşinci
kategorisi, yani Aşama 2'de "sessiz boş başarı" diye tanımladığımız durum. 7B
epizot başına altı kez o durumu üretiyor.

### 1.5B: adımlar eylem üretiyor ama eylemlerin hepsi düşüyor

İki yüz adımın 190'ı eylem üretti, 10'u `execution_error_no_action`, yani epizot
başına yalnız ilk adım hata veriyor.

Ama eylemlerin kendisi başarısız. On dokuz çağrının on dokuzu da
`POST /spotify/auth/token` ve hepsi 401 dönüyor. Model yanlış parolayla giriş
denemesini yirmi adım boyunca tekrarlıyor.

Bu, K-20'nin öngördüğü davranışın ta kendisi: sabit sıcaklık ve sabit seed
altında ajan başarısız bir çağrıyı tekrarlıyor, çünkü dağılım değişmiyor.

### Üç model, üç farklı arıza biçimi

| Model | Eylem üreten adım | Baskın arıza | Çağrıların durumu |
|---|---|---|---|
| 1.5B | 190/200 | Yanlış parolayla giriş döngüsü | 19/19 çağrı 401 |
| 3B | 0/200 | `NameError`, tanımsız değişken | çağrı yok |
| 7B | 40/120 | Sessiz boş başarı (60/120) | 5/5 çağrı 200 |

Hiçbiri görevi çözmüyor ama sebepleri birbirinden tamamen farklı. Üçü de aynı
"taban etkisi" başlığı altında toplanamaz.

7B'nin baskın arızası K-36'nın beşinci kategorisi, yani dışarıdan temiz görünen
ve doğrulayıcıya kadar alarm üretmeyen tür. En yetenekli noktamızın en çok
ürettiği hata biçimi bu; K-40'ın tavanda sansür kuralı tam olarak bunun için
konmuştu.

### Bunun ikili sonucu

Bir yandan ölçülecek bant var, çünkü baştaki hata düzeltilebilir bir hata.

Öte yandan bir geçerlilik riski doğuyor: mekanizma bu hatayı düzeltirse
ölçtüğümüz etki "biriken deneyimin katkısı" değil "tek bir prompt kopyalama
hatasının kapanması" olabilir. Etki büyük çıkarsa ikisini ayrıştırmak gerekecek.
S-19'a yazıldı.

**Yapılmayacak olan.** Prompt düzeltilmiyor. Referans iskele değiştirilmeden
alınıyor (K-23, K-26) ve bu hata iskelenin kendi davranışı. Düzeltmek
mekanizmanın işi.

## Karara bağlananlar

- **K-51.** Determinizm bir analiz varsayımı olarak alınmıyor. Artık varyans
  model başına ölçülüp gürültü tabanına ekleniyor. K-48'in ikili seçimi
  yerine geçti.
- **K-42, nihai hâli.** Zorluk bölmesi bütün ve dokunulmamış kalıyor.
  Biriktirme train, dev ve kullanılmayan normal test görevlerinden.
  Değerlendirme normal testten, örneklem biriktirmede temsil edilen
  uygulamalarla sınırlı. Uygulamalar arası aktarım erişilebilir 37 görevle
  koşacak ve küçük n'iyle raporlanacak.

## Sırada

Önyükleme biriktirmesi (K-50'nin üçüncü maddesi). Havuz tanımı artık kapalı, yani
neyin biriktirileceği belli.

## Yerel-yalnız kontroller

Son koşu: `2026-08-11T13:05:57+03:00`, commit `935a603`. On dört test geçti,
99 test elendi.
