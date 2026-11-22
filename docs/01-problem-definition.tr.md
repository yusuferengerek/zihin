# Problem tanımı

## Gözlenen durum

Dil modeli tabanlı ajanlar her görevi sıfırdan çözüyor. Bir hafta önce
çözdükleri problemi bugün yeniden keşfediyor, geçen sefer yaptıkları hatayı
tekrar ediyorlar.

Bunun maliyeti doğrudan ölçülebilir. Her adım bir model çağrısı, her çağrı zaman
ve para. Sistem çalıştıkça hızlanmıyor: yüzüncü görev birinci görev kadar
pahalı.

## Bilinen çözüm ve bedeli

Bilinen çözüm daha büyük model. Bu iki şey demek: daha pahalı donanım, ve dışa
bağımlılık. İkisi de bu projenin kabul etmediği bedeller, çünkü ölçmek istediğimiz
şey modelin büyümesinden bağımsız bir kazanç.

## Sınadığımız alternatif

Modeli büyütmeden, biriken deneyimi kullanarak maliyeti düşürmek.

İki mekanizma var. **Derlenmiş beceriler**: geçmiş epizotlardan madencilenen,
doğrulanmış çağrı dizileri. **Açık bir başarısızlık indeksi**: hangi eylemin
hangi bağlamda düştüğünü taşıyan kayıt.

İkisi de ajanın kendisini değiştirmiyor. Modele dokunulmuyor, eğitim yok, ince
ayar yok. Değişen tek şey ajanın bağlamına giren bilgi.

## Bu belgenin kapsamı dışındakiler

Bu proje modeli iyileştirmiyor, kıyaslamayı iyileştirmiyor ve genel bir bellek
mimarisi önermiyor. Tek bir soruyu ölçüyor: biriken deneyim, model çağrısı
sayısını düşürüyor mu.

Araştırma sorularının tam hâli `02-research-question.tr.md` içinde.
