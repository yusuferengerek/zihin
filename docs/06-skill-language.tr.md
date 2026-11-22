# Beceri dili

Beceri, geçmiş epizotlardan madencilenmiş, doğrulanmış bir çağrı dizisi.
Derleyici onu üretiyor; derleyici çevrimdışı, belirlenimci ve model kullanmıyor
(`03-architecture.tr.md`).

## Madencilik

Sıralı örüntü madenciliği, **kapalı örüntü**, **boşluk kısıtı**.

Destek farklı epizot değil **farklı görev** sayısı üzerinden. Aynı görevin on
epizodu bir görev sayılıyor; yoksa tek bir görevin tekrarları bir örüntüyü
kütüphaneye sokabilir.

Uzunluk alt sınırı **iki**. Asıl filtre bir **değer eşiği**.

Değer, **model çağrısı** cinsinden: `(gözlenen adım sayısı − 1) × görev desteği
× başarı oranı`. Burada eskiden "uzunluk eksi bir" yazıyordu ve yanlış birimi
sayıyordu; bir adım bir model çağrısı ve ajan bir adımda birkaç API çağrısı
yapabiliyor, yani çağrı uzunluğu tasarrufu abartıyor. Ölçüldü ve dört
beceriden birinde iki kat fark çıktı (K-82).

Başarı oranı v0'da yapı gereği bir: beceriler yalnız geçen epizotlardan
madencileniyor. Çarpan, çağrılma sicili biriktikten sonra anlam kazanacak.

**Beceriler yalnız başarılı epizotlardan madencileniyor.**

## Argümanlar

Üç sınıf var.

**Bağlı argüman.** Değeri dizinin içinde daha önceki bir çağrının çıktısında
geçiyor. Yapısal yol eşleşmesiyle tespit ediliyor. Gövdede kalıyor.

**Serbest parametre.** Değişiyor ve dizide hiç üretilmiyor. İmzaya çıkıyor.

**Sabit.** Bütün örneklerde aynı ve dizide üretilmiyor. Gömülüyor.

### Sıra kritik

**Önce bağlılık, sonra değişkenlik.**

Tersi yapılırsa bağlı argümanlar parametre sanılır ve beceri değersizleşir,
çünkü çağıranın zaten işin yarısını bilmesi gerekir.

### Sabit ilan etme eşiği

Sabit ilan etmek için belirli sayıda farklı görevde aynı değer görülmeli.

Gerekçe **maliyet asimetrisi**: yanlış dondurulmuş bir sabit beceriyi sessizce
bozar, gereksiz bir serbest parametre yalnız çağrıyı uzatır.

**Dinamik tip kara listesi** var: zaman damgaları, kimlik kalıpları ve gizli
etiketli değerler sabit ilan edilemiyor.

## Birleştirme

Beceri **arama öneki** ve **etki soneki** olarak ikiye ayrılıyor. Etki soneki
aynıysa aynı beceri.

Etki kısmı da farklı olan ama aynı hedefe varan diziler v1'de ayrı kalıyor.

### Reddedilen iki yol

**Gömme benzerliğiyle kümeleme.** Getiricide reddedilen gerekçenin aynısı:
çalışma zamanına yeni bir karıştırıcı ekliyor.

**Bir modele "bunlar aynı iş mi" diye sormak.** Bu, derleyicinin içine model
koyuyor ve derleyicinin belirlenimci olma şartını kırıyor.

## Yürütme

Beceri **atomik** çağrılıyor. Yarıda kırılırsa **geri alma yok**, ilk hatada
duruyor.

Kırılan beceri **yapılandırılmış dönüş** veriyor: hangi çağrılar koştu,
çıktıları, nerede durdu, hata ne, durduğu andaki gözlem.

Sebebi ölçüm adaleti: böylece ajanın elindeki bilgi taban koşuluyla eşitleniyor.
Kırılan beceri ajanı taban koşulundan daha kör bırakırsa, ölçülen fark
mekanizmanın değil bilgi kaybının sonucu olur.

Atomiklik yalnız model çağrısı düzeyinde bir özellik; kalkan denetimi beceri
içindeki her çağrı için ayrı işliyor (`04-threat-model.tr.md`).

## Suç atfı

Üç kapı, sırayla.

1. **Çağrı beceriye hiç ulaşmadıysa** modelin hatası. Becerinin istatistiğine
   yazılmıyor.
2. **İmza doğru ama ön koşul sağlanmıyorsa** modelin hatası. Ayrı sayaçta.
3. **İmza doğru, ön koşul sağlanmış, içindeki API hata döndürdüyse** becerinin
   hatası.

**Düşürme kuralını besleyen tek sayı üçüncüsü.** İlk iki kapı olmasaydı model
hataları beceriye yazılır ve iyi beceriler kütüphaneden düşerdi.

## Henüz yazılmamış olanlar

Değer eşiğinin sayısı, sabit ilan etme eşiğinin sayısı ve boşluk kısıtının
büyüklüğü burada yok. Üçü de kurulum aşamasının dolduracağı değerler; karar
kuralları ön kayda, sayıları kurulum sonrasına ait (`08-decisions.tr.md` K-50).
