# Hata taksonomisi

Hata indeksi, hangi eylemin hangi bağlamda düştüğünü taşıyan kayıt. Üç
gözlemlenen düzey ve bir ayrı eksen var.

## Eylem düzeyi

Kalkan engeli, yetki reddi, nesne bulunamadı, geçersiz parametre, uygun olmayan
durum, imza veya API yok, istisna, süre aşımı, kaynak sınırı, hatasız.

**Öncelik sırası sabit:** önce kalkan, sonra çalışma zamanı istisnası, sonra API
hata kodu. Sıra sabit olmasaydı aynı olay iki farklı etiketle sayılabilirdi.

## Adım düzeyi

Beş kategori:

1. **Kod üretilmedi.**
2. **Ayrıştırılamadı.**
3. **Bağlam taştı.**
4. **Kod üretildi ama hiç eylem üretmeden yürütme hatası verdi.** Kısa adı
   *kategori 4*.
5. **Ajan hatayı işlemi etkisizleştirerek düzeltti ve dışarıdan temiz
   görünüyor.** Kısa adı *sessiz boş başarı*.

Beşinci kategori doğrulayıcıya kadar hiçbir yerde alarm üretmiyor; ölçülen
epizotlarda en yetenekli modelin baskın arıza biçimi oydu. Gerekçesi ve ölçümü
`08-decisions.tr.md` K-36'da.

## Epizot düzeyi

Çözüldü, doğrulayıcı geçirmedi, beklenmeyen yan etki, bütçe bitti, kesildi.

## Tekrar: ayrı eksen

**Tekrar, sonuç ve ilerleme etiketlerinden bağımsız bir eksen.**

Ölçüldü ve merkezî çıktı: bir epizot 150 adımda 736 başarılı çağrı yapıp
veritabanını hiç değiştirmedi; bir başkası aynı yanlış girişi 88 kez tekrarladı.
Birincide çağrılar başarılı, ikincide başarısız; ortak olan tek şey tekrar.

### Ölçülen nicelik: uç nokta kümesinin büyümesi

Tekrar, **API uç noktası kümesi** üzerinden ölçülüyor. Uç nokta parametreyi
soyutluyor: `spotify.library/playlists`, sayfa numarasından bağımsız tek bir uç.

Soyutlama şart. Farklı kimliklerle dönen bir döngü her adımda yeni bir normalize
eylem üretir; eylem kümesine bakan bir ölçüt böyle bir döngüyü hiç yakalayamaz.
Uç nokta kümesi ise doyuma ulaşır ve orada kalır.

**Adım etiketi.** Bir adım, doğrulanabilir durumu değiştirmediyse ve daha önce
dokunulmamış bir uca ulaşmadıysa *durgun*. Ardışık durgun adım sayısı epizodun
tekrar ekseni üzerindeki konumu.

**Ölçülmüş dayanak.** Kayıtlı 62 epizot:

| Epizot | Adım | Uç nokta | En uzun durgunluk |
|---|---|---|---|
| `09b0ee6_2` | 150 | 3 | 146 |
| `c77c005_3` | 92 | 4 | 87 |
| `59fae45_2` | 11 | 65 | 3 |
| `1150ed6_1` | 8 | 7 | 1 |

İki patolojik epizotta uç nokta kümesi dördüncü ve beşinci adımda doyuyor.
Gerçek keşif yapan epizotlarda durgunluk 6 adımı geçmiyor; patolojik olanların
en kısası 13. Sekiz ile on iki arasında hiçbir epizot yok.

Durma kuralı bu eksene dayanıyor (`05-experiment-design.tr.md`).

## Türetilmiş etiketler

**Kullanılanlar, referans gerektirmeyenler:** tekrar eden eylem, ilerlemesiz
aralık.

**Kullanılmayanlar, referans gerektirenler:** gereksiz çağrı, çıkmaz sokak.

Sebep: ikinciler ancak doğru çözümü bilerek etiketlenebilir ve **mekanizma bir
görüşten öğrenmemeli.** Öğrenirse ölçtüğümüz şey mekanizmanın değil referans
çözümün katkısı olur.

## Bağlam koşulu zorunlu

**Hata indeksindeki her kayıt bağlam koşulu taşımak zorunda.**

Koşulsuz bir yasak kaydı ajanı kötüleştirir: "bu çağrıyı yapma" diyen ama ne
zaman yapmaması gerektiğini söylemeyen bir kart, çağrının gerekli olduğu
durumlarda da onu engeller.

### Koşul dili kapalı ve sayılabilir

Üç şey söyleyebiliyor:

- nesnenin var olup olmadığı,
- nesnenin belirli alanlarının değeri,
- dizide daha önce belirli bir çağrının yapılmış olup olmadığı.

Dilin kapalı olması şart, çünkü açık bir koşul dili indeksin içine ikinci bir
programlama dili koyar ve o dilin ifade gücü ölçülmemiş bir mekanizma olur.

### İndirgeme karşıtsal

Aynı çağrı dizisinin başarılı ve başarısız geçtiği epizotlar karşılaştırılıp
ayrışan yüklem aranıyor.

**Karşıtsal eşi olmayan kalıplar silinmiyor.** "Bilinen başarı yok" işaretiyle
indekse giriyor ve getirmede ayrı sayılıyor. Silinseydi yalnız bir kez görülen
ama gerçek olan hatalar kaybolurdu.

## Kalkan ihlalleri doğrudan girmiyor

İndekse girmesi için aynı kalıbın **kalkanın engellemediği bir durumda da**
başarısızlıkla sonuçlanmış olması gerekiyor.

Kalkan sinyali tek başına kayıt üretmiyor, sadece güçlendiriyor. Üretseydi
indeks kalkanın kendi yüklemini öğrenirdi ve mekanizma kalkanın kopyası hâline
gelirdi.

## Reddedilen: ceza ile öğretme

Gerekçe `04-threat-model.tr.md` içinde: tespit edebilen sistem engelleyebilir, ve
ceza ödül sinyaline karışırsa ajan tespitten kaçınmayı öğrenir.

## Henüz yazılmamış olanlar

İndeksin ilan edilen asgari boyutu — terk kriterinin dayandığı sayı
(`05-experiment-design.tr.md`) — burada yok. Kurulum aşamasının dolduracağı değer.
