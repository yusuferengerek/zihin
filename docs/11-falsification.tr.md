# Yanlışlama

Danışmanın asgari listesinin üstüne eklendi (K-33). Kapılar yazıldı; her kaydın
"Sonuç" satırı ölçümden sonra doluyor.

Buraya, tasarımın hangi gözlemle yanlışlanmış sayılacağı yazılıyor. Ölçümden
sonra değil, ölçümden önce.

Bir iddianın yanlışlanma koşulu ölçümden sonra yazılırsa iddia yanlışlanamaz
hâle gelir, çünkü her sonuç kendine bir açıklama bulur. Bu dosyanın işi o kapıyı
önceden kapatmaktır.

Her kayıt şunları taşıyor:

- **İddia.** Tasarımın hangi cümlesi sınanıyor.
- **Yanlışlayan gözlem.** Hangi ölçüm, hangi eşikte, hangi yönde çıkarsa iddia
  düşer.
- **Ne zaman ölçülüyor.**
- **Sonuç.** Ölçümden sonra doldurulur, öncesinde boş kalır.

Sayılar burada kopyalanmıyor; ön kayıt (`experiments/preregistration.md` Bölüm A)
bağlayıcı metin, bu dosya kapıların tek yerde toplanmış hâli.

---

## Y-1 — Hipotez desteklenmemiştir

**İddia.** Derlenmiş beceriler ve açık bir başarısızlık indeksi, ayrılmış
görevlerde model çağrısı sayısını düşürür.

**Yanlışlayan gözlem.** Birincil hücrede — mekanizmalar açık ile taban, model
çağrısı metriğinde, ana eksenin en büyük yerel noktasında, görülmemiş alt
kümede, iki taraflı — eşleştirilmiş fark sıfırdan ayırt edilemiyorsa ya da ters
yöndeyse.

**Ek, 25 Eylül 2026.** "Ana eksenin en büyük yerel noktası" ifadesi ön kayıt
A.2'nin 25 Eylül 2026 ekiyle güncellendi: birincil hücrenin modeli
`qwen2.5-coder:32b-instruct-q4_K_M`, ve "yerel" şartı artık karşılanmıyor. Seçim
keşifsel, `Y-1`'in hükmü onaylayıcı (`K-169`).

**Ne zaman.** Ana koşu bittiğinde, tek seferde. Ara bakış yok: birincil hücreye
koşu ortasında bakmak, durma anını sonuca göre seçmeyi mümkün kılar.

**Sonuç.** Boş.

---

## Y-2 — Ezberleme doğrulanmıştır

**İddia.** Kazanç, biriktirmede görülmüş görevlerin ezberlenmesinden gelmiyor.

**Yanlışlayan gözlem.** Görülmemiş görevlerdeki kazancın görülmüş görevlerdeki
kazanca oranı **yarımın altındaysa**.

Bölme ölçütü biriktirme kaydındaki **normalize eylem dizisiyle birebir eşleşme**;
ölçüt ölçümden önce sabit ve sonuca bakılarak değiştirilmiyor.

**Ne zaman.** Y-1 ile aynı anda, aynı koşudan.

**Ek, 28 Ağustos 2026 — bu kapı onaylayıcı kümeden çıktı, koşudan önce.**
Yukarıdaki ilan değişmedi ve silinmiyor. Değişen şey hükmü: bu kapı bu örneklem
boyutunda hüküm **üretemiyor**, çünkü örneklemin yarısını okuyor ve o yarının
aralığı ölçülen geçiş oranında hiçbir beklenen etkide gereken kadar dar değil
(`S-67`). Kazanç görülmüş ve görülmemiş görevlerde **ayrı ayrı raporlanıyor**;
oranın yarımın altında olup olmadığına hüküm verilmiyor. Karar `K-148`.

**Sonuç.** Boş.

---

## Y-3 — Sembolik getirici bu ortamda ilgili deneyim bulamıyor

**İddia.** Getirici, kapsanan görevlerin çoğuna ilgili kart bulabiliyor.

**Yanlışlayan gözlem.** Kapsama oranı **%25'in altındaysa**.

**Bu bir "test edemedik" değil, bir bulgudur** ve öyle raporlanıyor. Mekanizma
sınanamadığı için değil, mekanizmanın girdisi bu ortamda yok olduğu için.

**Ne zaman.** Getirme koşusunda, ana koşudan önce; kapsama ana koşunun girdisi.

**Sonuç.** Kurulum fazında ölçüldü ve kapı **açılmadı**: `test_normal`
bölmesinde kapsama 168/168. Ama ölçüm tek boyutlu — kapsama uygulama eşleşmesine
dayanıyor ve kartın göreve gerçekten uyduğunu söylemiyor. Ana koşudaki değer
yeniden ölçülecek.

---

## Y-4 — Hata indeksi mekanizma olarak terk edilir

**İddia.** Hata indeksi, modelin davranışını değiştiren bir mekanizmadır.

**Yanlışlayan gözlem.** Kapsama yeterliyken **ve** indeks ilan edilen asgari
boyuttayken `failures` koşulu tabana göre etki göstermiyorsa.

**"Asgari boyut" getirilebilir kalıp sayısıdır, indeks satırı değil** (S-48).
Getirilemeyen satırlarla dolu bir indeks yeterli görünür ve mekanizmayı haksız
yere aklar: "indeks yeterince büyüktü, demek ki mekanizma denendi" denir, oysa
modele hiç ulaşmayan bir kalıp denenmemiştir. Ölçüldü: 15 satırlık indeksin
getirilebilir boyutu 14.

**Sonucu: yeniden ayarlanmaz.** Terk kriteri karşılandığında eşik oynatılmıyor,
mekanizma bırakılıyor.

**Ne zaman.** Ana koşudan sonra, `failures` ile `baseline` karşılaştırmasından.

**Sonuç.** Boş.

---

## Y-5 — Beceri derleyicisi mekanizma olarak terk edilir

**İddia.** Derlenmiş beceriler, modelin davranışını değiştiren bir mekanizmadır.

**Yanlışlayan gözlem.** Y-4'ün aynısı, `skills` koşulu için. Kütüphane boyutu da
**getirilebilir beceri sayısı** ile ölçülüyor.

**Ne zaman.** Ana koşudan sonra.

**Sonuç.** Boş.

---

## Y-6 — İki kritik kontrast bozulursa analiz planı çöker

**İddia (K-31).** Taban ile alakasız getirme arasındaki fark **saf bağlam
hacmi**; sadece beceriler ile alakasız getirme arasındaki fark **saf içerik**.

**Yanlışlayan gözlem.** İki durumdan biri:

1. Alakasız getirme koşulu tabandan **ayırt edilemiyorsa** — o zaman bağlam
   hacminin etkisi ölçülemiyor ve çıkarıcı kontrol boş bir işlem oluyor.
2. Alakasız getirme koşulu tabandan **mekanizma koşulu kadar** iyileşiyorsa —
   o zaman ölçülen şey içerik değil hacim.

**Toplanabilirlik varsayımı ayrıca sınanıyor ve şüphe önceden yazılı.** Ayna
bulgusu (K-84) bu korpusta hacim ve içerik etkilerinin toplanabilir
olmayabileceğini söylüyor: kütüphanenin dördü de giriş, indeksin en sık kalıpları
da giriş hatası. İkisi aynı arızayı hedefliyorsa birinin kapattığını diğeri
ikinci kez kapatamaz. Toplanabilirlik tutmazsa çıkarıcı kontrolün sayısı
yorumlanamaz ve bu **sonuçtan önce** yazılıyor.

**Ne zaman.** Ana koşudan sonra, koşullar arası karşılaştırmadan.

**Ek, 28 Ağustos 2026 — birinci dal onaylayıcı kümeden çıktı, koşudan önce.**
"Alakasız getirme koşulu tabandan ayırt edilemiyorsa" dalı hüküm vermiyor;
alakasız kolun tabana göre farkı **yönsel olarak** raporlanıyor. Sebep ölçülmüş:
o dalın hacim etkisini sıfırdan ayırması için gereken aralık, ölçülen geçiş
oranında elde edilemiyor. **İkinci dal onaylayıcı kalıyor** — içerik ile hacmi
ayıran karşılaştırma çıkarıcı kontrolün kendisi ve o menzilde. Karar `K-148`.

**Ek, 26 Eylül 2026 — ikinci dalın mekanizma koşulu adlandırıldı, sonuç görülmeden.**
Faz 1'de mekanizma koşulu `skills_failures`: ikinci dal `skills_failures` –
`irrelevant_retrieval` karşılaştırmasıyla, 101 görevde okunuyor. Yukarıdaki iddia
cümlesinin kontrastı (`skills` – `irrelevant_retrieval`) faz 2'nin ikinci okuması olarak
kalıyor. İlan ön kayıt A.7'nin 26 Eylül ekinde, karar `K-188`.

**Sonuç.** Boş.

---

## Ön koşul kapısı — ateşledi

Yukarıdaki altı kapı hipotezle ilgili. Ön koşul kapısı onlardan önce geliyor ve
hipoteze hiç sıra gelip gelmeyeceğini belirliyor.

**İddia.** Taban koşulu ayrılmış kümede ilan edilen asgari başarı oranını
tutturur, yani ölçülebilir bir bant vardır.

**Yanlışlayan gözlem.** Tutturamazsa **deney hipotezi test edememiştir ve
mekanizma sonuçları raporlanmaz.**

**Sonuç: ateşledi, 11 Ağustos 2026.** Qwen2.5-Coder 1,5B, 3B ve 7B AppWorld'ün
otuz görevlik tabakalanmış örnekleminde hiçbir görevi çözmedi. Üç tabakalama
denendi ve hiçbiri ölçülebilir bant açmadı: referans uzunluk, güçlü modelin
çözdüğü alt küme, uygulama kümesi.

**Sıfırlar düzenekten gelmiyor, 12 Ağustos 2026.** Aynı otuz görevde DeepSeek V4
Flash 0731 bizim hattımızda 20/30, yayımlanmış gpt-4o koşusu 15/30. O koşuda
düşünme açıktı ve bu ilan edilen koşul değildi (S-34); "düşünme kapalı, 20/30"
cümlesi kurulamaz.

**Kapının dayandığı ölçümün temizliği sınandı.** İlk tarama eski durma kuralıyla
koşulmuştu (S-27); üç tekrar yapıldı ve üçü de sıfır verdi — `bant2` 0/30,
`bant3` 0/30, `bant3-kapalı` **durma kuralı tamamen kapalıyken** 26 epizotta 0.

**Ateşlemenin sonucu:** model ailesi yeniden seçiliyor. Mekanizmalar kuruldu ve
çalıştıkları gösterildi, ama hipotez henüz test edilmedi.
