# Araştırma sorusu

İki soru var. İkincisi birinciye bağlı ve daha zayıf.

## Birinci soru — onaylayıcı

**Derlenmiş beceriler ve açık bir başarısızlık indeksi, ayrılmış görevlerde
çözüm için gereken model çağrısı sayısını düşürüyor mu?**

Bu soru **tek bir hücrede onaylayıcı olarak** test ediliyor. Hücrenin tanımı:
mekanizmalar açık koşulu ile taban koşulu, model çağrısı metriğinde, ana eksenin
en büyük yerel noktasında, görülmemiş alt kümede, iki taraflı.

En büyük nokta seçiliyor çünkü hipotez için en zor durum: model büyüdükçe
biriken deneyimin katkısı azalması beklenen yön.

**Ek, 25 Eylül 2026.** "Ana eksenin en büyük yerel noktası" ifadesi ön kayıt
A.2'nin 25 Eylül 2026 ekiyle güncellendi: birincil hücrenin modeli
`qwen2.5-coder:32b-instruct-q4_K_M`, ve "yerel" şartı artık karşılanmıyor. Seçim
keşifsel, `Y-1`'in hükmü onaylayıcı (`K-169`).

## İkinci soru — keşifsel

**İncelenen model boyutları içinde bu etki sistematik olarak ortadan kalkıyor
mu?**

Keşifsel, çünkü ölçek ekseni üç noktadan oluşuyor ve üç nokta bir eğrinin
şeklini onaylayıcı olarak belirlemeye yetmiyor. Ekseni yorumlama tablosu ön
kayda giriyor: düz, düşen, yükselen ve ters U için ne söyleneceği ölçümden önce
yazılıyor.

**Ek, 20 Ağustos 2026.** Eksene dördüncü nokta girdi (14B, K-133). Cümlenin
sayısı değişti, gerekçesi değişmedi: dört nokta da bir eğrinin şeklini
onaylayıcı olarak belirlemeye yetmiyor, ve dördüncü nokta sıfırlar görüldükten
sonra seçildiği için ayrıca keşifsel. Özgün ilan ve tarihli ek ön kayıt
A.11'de.

İkinci soru birinciye bağlı. Birinci soru için ölçek ekseninin en az iki
noktasının ön koşul kapısını geçmesi gerekiyor; tek nokta geçerse ikinci soru
ölçülemez hâle geliyor.

## Neyi sormuyoruz

Başarı oranının artıp artmadığını sormuyoruz. Birincil metrik başarı değil,
çözüme giden yolun uzunluğu. Başarı oranı ikincil metrik olarak raporlanıyor.

Mekanizmaların modeli daha "akıllı" yapıp yapmadığını sormuyoruz. Model
sabit; değişen bağlama giren bilgi.

## Yanlışlama

Her iddianın hangi gözlemle düşeceği `11-falsification.tr.md` içinde, ölçümden
önce yazılıyor. Üç kapı `05-experiment-design.tr.md` bölüm "Kapılar" altında
tanımlı.
