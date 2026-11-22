# Alternatifler defteri — güç sorununun yolları

Bu defter **kapanmıyor**. Deneyin gücü yetmediğinde ne yapılabileceğinin
yollarını, her birinin durumunu ve fiyatını tutuyor. Çerçeve içindeki yollar
tükenirse buraya dönülüyor.

**Neden bir defter.** Bir yol denendiğinde ya da kapandığında, o anın gerekçesi
başka bir kaydın içinde kalıyor ve sonradan "başka seçenek var mıydı" sorusuna
cevap vermek için üç belge okumak gerekiyordu. Burada dört satır var ve her satır
kendi eserine bağlı.

**Sorun.** Ön kayıttan türetilen geçiş oranı eşiği 0,75-0,85 (`K-146`); birincil
tabakada ölçülen oran 0,280. Aradaki fark `S-68`.

---

## (a) Daha yüksek geçiş oranı veren bir model

**Durum: ölçümle kapalı.**

Eşiğin geçilmesi gereken yer eylem tabakası. Bu projenin ölçtüğü **en yüksek
nokta** DeepSeek V4 Flash ve orada 15/25 = **0,600** veriyor; ikinci referans
gpt-4o 10/25 = 0,400. Eşik 0,75. Ölçümler `results/stratum-rates.json`, karar
`K-147`.

**Kapalı olan ne, olmayan ne.** Kapanan şey "ölçtüğümüz modellerden biri yeter"
iddiası. Kapanmayan şey ilkesel imkân: 0,75'i eylem tabakasında geçen bir model
varsa bu yol açılır. Böyle bir model **ölçülmedi**, ve bu defterin bu satırı onu
ölçen bir koşuyla değişir.

**Nitelik.** DeepSeek'in 20/30'u iki koşunun birleşimi ve o koşularda düşünme
açıktı; ayrıntısı `S-34`.

---

## (b) Örneklemi büyütmek

**Durum: ertelendi, fiyatı yazılı.**

Ezberleme kapısını menzile sokmak **500 eylem görevi** istiyor (beklenen etki %20
ve üstü için; %10'da havuzun tamamı yetmiyor). Bugünkü 105'in üstüne
`test_challenge`'ın 408 eylem görevinden 395'i demek. Hesap tarafı 7500 epizot,
yaklaşık **225 oturum-saati**. Ölçüm `results/sample-size.json`, kayıt `K-149`.

**Bedeli yalnız para değil.** Eklenen görevlerin çapa dağılımı farklı, yani
büyüyen örneklem aynı sorunun daha kesin cevabını değil **başka bir görev
popülasyonu hakkında** bir cevap verirdi.

**Tetiği var.** Deney 105 görevde koşulduğunda `Y-1`'in aralığı sıfırı
dışlayamazsa bu yola geçiliyor. Tetik koşudan önce ilan edildi.

**Ek — 25 Eylül 2026: fiyat bir aralık.** Yukarıdaki 500 yedi tekrarın medyanı.
Tekrar başına (`K-168`): beklenen etki %20 ve üstüyse **400–557** eylem görevi,
üst uç havuzun tamamı; %30'da yedi tekrarın ikisinde, %50'de birinde havuz
yetmiyor; %10'da hiçbirinde. Hesap tarafı 6000–8355 epizot, yaklaşık **180–250
oturum-saati**. Tabaka artık 104 görev; tetik aynı ve 104'e uygulanıyor.

---

## (c) Onaylayıcı ayrımları daraltmak

**Durum: seçildi ve ilan edildi, koşudan önce.**

`Y-2` ve `Y-6`'nın birinci dalı onaylayıcı kümeden çıktı; ikisi de yönsel olarak
raporlanmaya devam ediyor. Kalan onaylayıcı ayrımlar `Y-1`, `Y-6`'nın ikinci
dalı, ve `Y-4`/`Y-5`. İlan `experiments/preregistration.md` A.7 altında, karar
`K-148`.

**Bedeli.** İki soru bu koşuda cevaplanmıyor. Ezberlemenin kazancı ne kadar
açıkladığı ve hacim etkisinin sıfırdan ayrılıp ayrılmadığı **yönsel** kalıyor.

---

## (d) Çerçeve dışı yollar

**Durum: çerçeve dışı. Son çare, ve yalnız açık ilanla.**

Yukarıdaki üçü ön kaydın çerçevesinin **içinde**: metriği, estimand'ı, bölme
tanımını ve onaylayıcı disiplini koruyorlar. Bu satır çerçevenin kendisini
değiştirecek yolları tutuyor.

**Bu defter şu an belirli bir (d) adaylandırmıyor**, çünkü adaylandırılmadı. Slot
boş ve boş olduğu yazılı; buraya bir şey yazılması ayrı bir karar.

**Girilirse şartı önceden yazılı.** Çerçeve dışına çıkan her adım, çıkmadan önce
tarihli bir ekle ilan edilecek, neyin değiştiği adıyla yazılacak, ve o adımdan
sonraki hiçbir sonuç önceki çerçevenin sonucu gibi sunulmayacak.

---

## Bütün satırların altındaki nitelik

`S-66`: eşiğin ve 500 sayısının dayandığı gürültü katsayısı iki tekrarlı hücreden
ölçüldü. İkisi de **alt sınır**; gerçek değişkenlik büyükse (a) daha da kapanır,
(b) daha da pahalılaşır, (c) daha da gerekli olur.
