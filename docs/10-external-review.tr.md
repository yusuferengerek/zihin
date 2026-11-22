# Dış İnceleme Kaydı

Bu belge, tasarımın kod yazılmadan önce dış modellere sınatıldığı iki turun
kaydıdır. Amaç kör noktaları bulmaktı. Turlardan çıkan kararlar
`08-decisions.tr.md` içinde numaralarıyla duruyor; burada o kararların nereden
geldiği yazılı.

## 1. Protokol

Değerlendiren taraflara verilen rol bir hakem heyetiydi: dört üye, sırasıyla
ajan mimarileri, deneysel yöntem, güvenlik ve alan editörü. Sunan taraf
savunmaya girmiş bir doktora öğrencisi olarak konumlandırıldı, yani
tasarımın zayıf yerlerini kendisi savunmak zorunda kaldı.

Akış şöyleydi. Tasarım tek bir metne indirildi, bütün modellere aynı metin
verildi, çıktılar toplandı, ve ikinci tur için ilk turun düzeltmelerini
içeren yeni bir metin hazırlandı.

Değerlendirme kuralı baştan yazıldı: aynı itirazı birden çok model
yapıyorsa gerçek bir sorun sayılır, tek model yapıyorsa muhtemelen
gürültüdür. Bu kural, tek bir modelin ısrarlı ama yanlış bir itirazının
tasarımı sürüklemesini engelledi. Kuralın istisnası da uygulandı: tek
modelin yakaladığı ama doğrulanabilir olan bulgular ayrıca listelendi.

Üçüncü tur açılmadı. Sebebi iki ölçüm: bulgu oranı ikinci turda belirgin
biçimde düştü, ve kalan itirazlar birbiriyle çelişen tercihlere dönüştü
(bir model daha katı bir eşik isterken bir diğeri aynı eşiği gevşetmeyi
öneriyordu). Çelişen tercihler bir tasarım kararına dönüştürülemez.

## 2. Birinci tur

Beş model: Gemini 3.6 Flash, MiniMax M3, GLM 5.2, Kimi K3 (düşünme açık),
DeepSeek V4 Flash 0731 (düşünme açık).

Kararlar: Gemini "katkı yok" dedi, diğer üçü "koşullu evet" dedi.

### Yakınsayan itirazlar

| Uzlaşma | İtiraz |
|---|---|
| 5/5 | Altıncı koşul (ham yörünge makro) hileli. Parametresiz sabit bir makro görülmemiş görevde tanım gereği çalışamaz. |
| 4/5 | Birincil metrik, atomik beceri tanımıyla örtüşüyor. |
| 4/5 | "İki koşulun da çözdüğü görevler" kısıtı sonuca koşullanmış bir seçim. |
| 4/5 | Kalkan beceriyi açmıyor; beceri gövdesindeki yazmalar denetimsiz geçiyor. |
| 4/5 | Adım tavanı taban dağılımından türetilirse döngüsel; ön kayıt pilottan sonra yazılırsa p-hacking. |
| 3/5 | Yorum kapısı nitel, sayısal bir ölçüte bağlı değil. |
| 3/5 | Kısmi yürütmede ajanın elindeki BAĞLAM taban koşuluyla eşit değil. |
| 3/5 | Dış taban yok; yalnız kendi ablasyonlarıyla karşılaştırma yapılıyor. |
| 3/5 | Ezberleme kapısının 0,5 eşiği gerekçesiz, ve oran kestirimi payda sıfıra yaklaşınca kararsız. |
| 2/5 | Model ekseni model ile kütüphaneyi birlikte değiştiriyor. (İki model de bunu öldürücü saydı.) |

### Tek modelin yakaladığı ama doğru çıkan bulgular

Birincil hücrenin görülmüş ve görülmemiş görevleri havuzlaması. "Ağ kapalı"
iddiasının kıyaslamanın gerçeğiyle çelişmesi. Disk kotasının hiç
tanımlanmamış olması. "Ömür boyu" teriminin veriyle desteklenmemesi. Sabit
bir k değerinin ölçek sorusunun cevabını önceden belirlemesi. Duvar
saatinin ölçülmemesi. Bağlı argüman tespitinin dize eşleşmesiyle sahte bağ
üretebilmesi. Ön koşul indirgeme prosedürünün hiç tanımlı olmaması.
Kuantalamanın model boyutuyla karışması. Zehirli beceri riski.

### Reddedilen itirazlar

Anlamsal getirme talebi reddedildi: gömme çalışma zamanına yeni bir kiralık
bileşen ve yeni bir karıştırıcı ekliyor, ve sembolik getirme bilinçli bir
kısıt. Bu bir sınırlama olarak yazıldı.

Okuma tarafı sızıntısı ilk turda reddedildi, ikinci turda kabul edildi.

Gemini'nin "katkı yok" kararı reddedildi: beş modelin tek aykırısıydı ve
gerekçesi diğer dördünün ayrıntılı itirazlarıyla çelişiyordu.

## 3. İkinci tur

Üç model: Gemini, MiniMax, GLM. Kararlar: Gemini yine tek aykırı ("daha da
kötüleşti"), MiniMax ve GLM "iyileşti".

### Yakınsayan itirazlar

| Uzlaşma | İtiraz |
|---|---|
| 3/3 | D7 mantıksal olarak çöküyor: bağlı argüman içeren bir beceride kalkan henüz yürütülmemiş bir çağrıyı denetleyemez. D7 ile D14 çelişiyor. |
| 3/3 | D4'ün toplanabilirlik varsayımı yazılmış ama test edilmemiş. Üçü de aynı düzeltmeyi önerdi. |
| 3/3 | D13 karşıtsal indirgeme, karşıtsal eşi olmayan hataları sessizce siliyor. |
| 2/3 | Kalibrasyon metriği totolojiye yakın: derleyicinin öz tutarlılığını ölçüyor. |
| 2/3 | R3'ün (okuma tarafı) reddi hatalıydı. |
| 2/3 | Loopback izni yeni bir saldırı yüzeyi. |
| 2/3 | D14'ün iki zıt kırılma biçimi var ve arada eşik yok. |

GLM tek başına dört şey yakaladı: birincil hücreyi görülmemiş alt kümeye
taşımak n'i 15-25'e düşürüyor ve gücü yarıya indiriyor; "yetersiz güçle
raporlanır" kuralı bir tasarım hatası; kart konumu ölçülmüyor; getirici
sıralaması tanımsız.

### İki metrik tartışması

Birinci turun "birincil metrik totolojik" itirazına iki metrikli bir düzen
önerilmişti. İkinci turda iki model bağımsız olarak aynı şeyi söyledi: token
sayısı model çağrısıyla mekanik olarak korele olduğu için iki metrikli düzen
totolojiyi kapatmıyor. İkisi de aynı çözümü önerdi: atomiklikten bağımsız
bir oran. Bu, model çağrısı bölü başarılı API çağrısı olarak zorunlu tanı
metriğine dönüştü.

### Estimand tartışması

"İki koşulun da çözdüğü görevler" kısıtı yerine tavanda sansürlenmiş bir
estimand önerildi. İtiraz şuydu: sansürlü estimand da yanlı. Cevap kabul
edildi ama karşılaştırmalı olarak: eski önyargı yapısal ve sınırsız, yeni
önyargı parametrik ve sınırlı.

## 4. Turlardan doğan kararlar

Aşağıdaki kararların hepsi bu iki turdan çıktı ve önceki tasarımın bir
kısmını geçersiz kıldı. Numaraları `08-decisions.tr.md` içinde.

Kalkanın denetim anı ön kontrol artı adım adım denetime çevrildi. Statik
argümanlı çağrılar beceri başlamadan, dinamik argümanlılar kendi
yürütülmelerinden hemen önce denetleniyor. Atomiklik yalnız model çağrısı
düzeyinde bir özellik.

Beceri ortasındaki kalkan reddi ayrı bir sonuç sınıfı oldu. "Kalkanın
reddettiği her eylem bedava negatif örnektir" iddiası yalnız yürütme öncesi
retlere daraltıldı.

Suç atfına dördüncü bir durum eklendi: reddedilen çağrının uygulaması kartta
listeliyse ikinci kapı, listeli değilse derleyici kusuru.

Getirici filtresi kondu: uygulama kümesi görevin izinli kümesinin alt kümesi
olmayan beceriler hiç getirilmiyor.

Altıncı koşul düşürüldü ve yerine naif derleyici koşulu kondu. Soru daraldı:
"derleme gerekli mi" değil, "bizim derleyicimiz naif bir derleyiciden iyi
mi".

Birincil metrik korundu, çünkü bu ortamda taban da tek turda birden çok API
çağırabiliyor; beceri paketleme imkânı vermiyor, doğrulanmış paketi önceden
veriyor. Yanına zorunlu tanı metriği kondu.

Sansür tavana kadar kısıtlanmış ortalamaya ve görev kümesiyle bootstrap'a
geçti; Wilcoxon sağlamlık kontrolüne indi.

D8 tam çapraz yerine ters kola çevrildi: ana eksen her modelin kendi
kütüphanesiyle, iki ek hücre keşifsel.

Toplanabilirlik testi ana deneyden kurulum aşamasına alındı.

Karşıtsal filtre iki yollu oldu: karşıtsal eşi olmayan kalıplar silinmiyor,
"bilinen başarı yok" işaretiyle indekse giriyor ve getirmede ayrı sayılıyor.

Kalibrasyon metriği düşürüldü.

Güç kuralı değişti: ön kayıt sabit bir n değil bir karar kuralı ilan ediyor.

R3 reddi geri alındı; kalkanın birinci aşama yüklemi okumayı da kapsayacak
şekilde genişletildi. (Bu karar sonradan ölçümle yeniden daraltıldı; gerekçe
`09-limitations.tr.md` içinde.)

Sandbox ağ politikası ağ ad alanı düzeyine taşındı.

D14'ün katılık eşiği kurulum aşamasında ölçümle seçilmek üzere bırakıldı.

Kart konumu sabitlendi ve ilan edildi; permütasyon kontrolü kurulum
aşamasına kondu.

## 5. Bu incelemenin kendi sınırı

İki tur, beş model, dört jüri rolü. Hiçbiri şunu sormadı: bu model sınıfı bu
kıyaslamada herhangi bir görevi çözebiliyor mu?

Bütün analiz planı "çözülmüş görev var" varsayımının üzerine kuruluydu ve o
varsayım hiç sınanmadı. Estimand tartışması, sansür kuralı, totoloji,
çıkarıcı kontrol, güç hesabı — hepsi bu ön koşulun altında duruyor.

Ön koşul 11 Ağustos 2026'da ölçüldü ve tutmadı. Yerel eksenin üç noktası da
otuz görevde sıfır çözdü. Ayrıntısı `09-limitations.tr.md` ve
`experiments/preregistration.md` içinde.

Bundan çıkarılan ders kayda geçirildi: bir tasarımın en üst katındaki
hipotez ne kadar dikkatle sınanırsa sınansın, altındaki ön koşullar ayrıca
ölçülmedikçe inceleme onları görmüyor. Hakem simülasyonu tasarımın iç
tutarlılığını denetliyor, dış geçerliliğini değil.
