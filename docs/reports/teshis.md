# Teşhis — duvar nerede

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

Bant taraması otuz görevde sıfır geçiş buldu. Yol seçmeden önce üç soru: duvar
kimlik doğrulamada mı, başarısızlıkların ne kadarı kategori 4, ve güçlü bir
modelin çözdüğü görevlerde 7B daha ileri gidiyor mu.

Teşhis 1 ve 2 yeni koşu istemedi; bant taramasının otuz epizodu zaten kayıtta.

## Sonradan eklenen uyarı: bu raporun tabanı kirli çıktı

**Bu rapordaki her sayı seri 1'den** (`results/zihin.sqlite`) ve seri 1 eski durma
kuralıyla koşuldu. Bant taramasının otuz epizodunun on altısı `no_progress` ile
kapandı, on beşi düzeltilmiş kuralla kesilmezdi (S-27). Yani bu raporun tabanı,
epizotların yarısının erken kesildiği bir koşu.

Kirlilik her ölçümü aynı şekilde etkilemiyor. Aşağıdakiler tek tek karara
bağlandı; iki tanesi ayakta, üç tanesi tekrar koşuluyor.

### Ayakta kalan: Teşhis 1

**Gerekçe: bu bir oran ölçümü, kesilme oranı kabaca koruyor.** Bulgu çağrı
sayılarının mutlak büyüklüğünde değil, uygulama içindeki desende: `venmo`da jeton
hiç alınamıyor (92 denemenin 89'u 401), `simple_note` ile `file_system`de jeton
alınıyor ama sonraki çağrıya taşınamıyor. Bu desen tek bir epizodun değil,
onlarca epizodun tekrarladığı bir şey. Erken kesilme hangi epizotların katkı
verdiğini değiştirir, uygulama içindeki 200/401 oranını sistematik olarak
çevirmez.

**Ayakta kalmayan kısım:** yüzdelerin kesin değerleri. %84,2 ve %15,3 tekrar
koşulduğunda oynayabilir. Bulgunun kendisi — duvarın kimlik doğrulamada olduğu ve
iki farklı biçimde tıkandığı — oynamaz.

### Ayakta kalan: Teşhis 2

**Gerekçe: a fortiori.** Kesilme kategori 4'ü **şişiriyor**. Dörtte kapanan altı
epizodun dört adımının dördü de kategori 4'tü; düzeltilmiş kuralla o epizotlar
devam etseydi paydaya kategori 4 olmayan adımlar eklenirdi. Yani gerçek oran
ölçülen %16,9'un **altında**.

Teşhisin hükmü "kategori 4 baskın değil"di. Gerçek oran daha düşükse hüküm
zayıflamıyor, güçleniyor. İskeleye uyarlama bu veriyle gerekçelendirilemez
sonucu ayakta ve daha sağlam.

### Tekrar koşulacak: Teşhis 3

gpt-4o'nun çözdüğü ve çözemediği alt kümelerin karşılaştırması (%4,8 ve %5,4)
dereceli skora dayanıyor, dereceli skor da epizodun ne kadar ilerlediğine. Erken
kesilen bir epizot daha az anlamlı test geçirir. İki alt küme farklı oranlarda
kesilmişse fark yapay olarak silinmiş ya da yaratılmış olabilir.

Yan bulgu — referans uzunluğun gpt-4o için de zorluk sinyali olmaması — ayakta:
o tablo yalnız yayımlanmış gpt-4o koşusundan geliyor, bizim epizotlarımıza hiç
dokunmuyor.

### Tekrar koşulacak: uygulama kümesine göre tabakalama

%13,7 ve %2,4 aynı sebeple dereceli skora dayanıyor ve tabakalamanın kendisi bir
ayrım iddiası. Kesilme uygulama kümesine göre dengesizse ayrım artefakt olabilir.

### Tekrar koşulacak: artık varyans ve tekdüzelik

Ön kayda giren gürültü tabanını besliyor (S-21). Gürültü tabanı yanlışlama
kapısının eşiğini belirliyor, yani kirli bir tabandan hesaplanması en pahalı
hata olur.

## Teşhis 1: duvar kimlik doğrulamada değil, ama orada bir duvar var

Otuz epizotta 1717 API çağrısı:

| Durum | Çağrı | Oran |
|---|---|---|
| 200 | 1445 | %84,2 |
| 401 | 263 | %15,3 |
| 422 | 5 | %0,3 |
| 409 | 4 | %0,2 |

Supervisor dışı uygulamalardan 1106 çağrı 200 döndü ve otuz epizodun 23'ü en az
bir tane aldı. Yani ajan gerçek uygulamalara erişebiliyor; 1,5B'de gördüğümüz
"on dokuz çağrının on dokuzu 401" tablosu 7B'de yok.

Ama 401'ler rastgele dağılmıyor, uygulamaya göre keskin ayrılıyor:

| Uygulama | Çağrı | 200 | 401 |
|---|---|---|---|
| `spotify` | 758 | 757 | 1 |
| `simple_note` | 245 | 127 | 118 |
| `venmo` | 159 | 47 | 108 |
| `api_docs` | 131 | 127 | 0 |
| `file_system` | 58 | 29 | 29 |
| `todoist` | 20 | 18 | 2 |
| `phone` | 5 | 1 | 4 |

**İki ayrı arıza biçimi var ve jeton uçlarına bakınca ayrışıyorlar.**

Birincisi jeton alamama. `venmo.auth/token` 92 denemenin 89'unda 401 dönüyor,
yalnız 3'ünde 200. Ajan venmo'ya hiç giremiyor.

İkincisi jetonu kullanamama. `simple_note.auth/token` 119 denemenin 118'inde
200 dönüyor, yani jeton alınıyor; ama `simple_note.notes` 117 kez 401 dönüyor.
`file_system` aynı desende: `auth/token` 29 kez 200, `file_system.file` 29 kez
401. Jeton elde ediliyor ve sonraki çağrıya doğru geçirilemiyor.

`supervisor.account_passwords` 334 kez çağrıldı ve 334'ü de 200 döndü. Yani
parolayı arama adımı çalışıyor; arıza sonrasında.

**Sonuç.** Duvar tek bir kapı değil. Çağrıların altıda beşi başarılı ve
`spotify` uçtan uca çalışıyor. Ama üç uygulamada kimlik doğrulama tıkanıyor ve
tıkanma iki farklı yerde: venmo'da parola, simple_note ile file_system'de
jetonun taşınması. Bu, görev karmaşıklığından bağımsız ve düzeltilebilir
görünen bir kayıp.

## Teşhis 2: kategori 4 baskın değil

Otuz epizottaki 958 adım:

| Kategori | Adım | Oran |
|---|---|---|
| Eylem üretti | 785 | %81,9 |
| `execution_error_no_action` (kategori 4) | 162 | %16,9 |
| `execution_ok_no_action` | 11 | %1,1 |
| `no_code` | 0 | %0 |

7B adımların beşte dördünde çalıştırılabilir kod üretip API çağırıyor. Kod
üretilmeyen adım hiç yok.

**Bunun karar sonucu.** İskeleye asgari uyarlama, kategori 4 baskın çıkarsa
meşru olacaktı. Baskın çıkmadı. Teşhis "model karmaşık bir iskelede yönerge
takip edemiyor" demiyor; model yönergeyi takip ediyor, kod yazıyor, API
çağırıyor. Uyarlama bu veriyle gerekçelendirilemez.

**Ama dağılım epizotlar arasında iki tepeli.** Otuz epizodun altısı hiç API
çağrısı üretmeden dörtte kapandı (dört adımın dördü de kategori 4). Diğer uçta
`09b0ee6_2` 150 adımda 736 çağrı yaptı ve hepsi 200 döndü, yine de görevi
bitiremedi. Ortalama %16,9 bu iki davranışın karışımı; tek bir arıza biçimini
tarif etmiyor.

## Teşhis 3: güçlü modelin çözdüğü görevlerde daha ileri gidiliyor mu

Yayımlanmış taban koşuları indirildi (`appworld download experiment-outputs`).
`legacy_react_code_agent/openai/gpt-4o-2024-05-13/test_normal` bizimkiyle aynı
iskele ailesi ve aynı bölme. Toplamlar yayımlanmış sayılarla birebir tuttu:
gpt-4o %48,8, gpt-4-turbo %26,8, LLaMA-3-70B %20,8, DeepSeek-Coder-33B %7,1.

**Önce bir yan bulgu: referans uzunluk gpt-4o için de zorluk sinyali değil.**

| Bant | gpt-4o'nun çözme oranı |
|---|---|
| 1-10 | 10/17 = %59 |
| 11-20 | 19/37 = %51 |
| 21-40 | 31/74 = %42 |
| 41-89 | 19/32 = %59 |
| 90+ | 3/8 = %38 |

Neredeyse düz. 41-89 bandı 1-10 kadar kolay. Bant taramamızın sıfır çıkması
uzunluk ekseninin yanlış eksen olmasıyla da açıklanabilirdi; bu tablo o
ihtimali kapatıyor, çünkü eksen güçlü model için de bilgi taşımıyor.

**Asıl karşılaştırma.** gpt-4o'nun çözdüğü 82 görevden bizim koştuğumuz
30 tanesi var: bant taramasındaki 15 örtüşme, artı bu tur koşulan 15 yeni görev.

| Alt küme | Görev | 7B geçen | Anlamlı test |
|---|---|---|---|
| gpt-4o çözdü | 30 | 0 | 6/126 = %4,8 |
| gpt-4o çözemedi | 15 | 0 | 5/93 = %5,4 |

**Fark yok.** Güçlü bir modelin çözdüğü görevlerde 7B daha ileri gitmiyor;
nokta kestirim ufak bir farkla ters yönde. İkili başarı iki tarafta da sıfır.

Bu, üçüncü teşhisin umut ettiği şeyi vermedi: çözülebilirliğin doğrudan
kanıtlandığı alt küme de bant açmıyor.

## Uygulama kümesine göre tabakalama

Referans uzunluk işe yaramadı. Uygulama kümesi yarıyor.

Görev başına uygulama listesi test bölmelerinde yok (S-03), ama yayımlanmış
gpt-4o koşusunun `api_calls.jsonl` dosyalarından çıkarılabiliyor. Kaynak
yayımlanmış bir koşu, bizim ölçümümüz değil.

`test_normal`'ın 168 görevinin 99'u tek uygulamalı: 37 venmo, 30 spotify,
16 simple_note, 7 phone, 6 file_system, 3 todoist.

Bizim 45 epizodumuz uygulama kümesine göre ayrıldığında:

| Alt küme | Görev | 7B geçen | Anlamlı test |
|---|---|---|---|
| Yalnız auth çalışan uygulamalar (`spotify`, `todoist`) | 11 | 0 | 7/51 = %13,7 |
| Diğerleri | 34 | 0 | 4/168 = %2,4 |

Dereceli skorda beş buçuk kat fark. Referans uzunluk tabakalamasının veremediği
sinyali bu veriyor. İkili başarı yine iki tarafta da sıfır.

**Ama bir karıştırıcı var ve büyük.** `spotify` tam olarak referans yönergenin
örnek çözümünde gösterilen uygulama. "Auth'un çalıştığı uygulama" ile
"yönergenin gösterdiği uygulama" aynı şey. %13,7'nin ne kadarının auth'tan, ne
kadarının örnek görmekten geldiği bu veriden ayrılamaz.

Bunun ön kayda etkisi doğrudan: örneklemi `spotify` görevleriyle sınırlamak,
taban koşulunu yönergenin zaten çözdüğü göreve daraltmak demek. Kapsam kısıtı
olarak ilan edilebilir ama S-19'un riskini azaltmıyor, büyütüyor.

## 736 çağrılık epizot

`09b0ee6_2`: 150 adım, 736 API çağrısı, **736'sının 736'sı 200**, ve 150 adımın
150'sinde de `state_change` boş. Veritabanı bir kez bile değişmedi.

Çağrı dağılımı: `spotify.library/playlists` 441, `supervisor.account_passwords`
148, `spotify.auth/token` 147. Yani ajan her adımda baştan giriş yapıp bütün
çalma listesi kütüphanesini yeniden sayfalıyor.

Epizot şu hatayla açılıyor:

```
NameError: name 'playlists' is not defined
```

Bu S-20'nin ta kendisi: yönergedeki örnek `playlists = []` tanımlayıp sayfa
sayfa dolduruyor, model örneğin ikinci yarısını kopyalıyor ve tanımı
taşımıyor. Sonraki adımda tanımı yazıyor, ama sonra aynı ön hazırlığı her
adımda tekrar yapıyor ve göreve hiç varmıyor.

**İyimserliği frenleyen taraf.** Model API'leri doğru çalıştırdığında bile
görev bitmiyor. Auth düzelse bant açılmayabilir; bu epizotta auth zaten
çalışıyordu.

**Durma kuralında kör nokta.** Kural 150 adım boyunca hiç ateşlemedi. Sebebi
kayıtta görünüyor: `_made_no_progress` bir adımı, çağrılarından biri başarılıysa
ilerlemiş sayıyor. Bu epizotta her adımda başarılı okuma var, dolayısıyla
pencere hiç dolmuyor. Durum farkı ise 150 adımın 150'sinde de boş.

Kör nokta "amaçsız durum değişimi" değil, **amaçsız başarılı okuma**. Ayrım
düzeltmeyi değiştiriyor: kuralı "durum değişmeli" diye sıkılaştırmak salt okuma
evrelerini ve hiçbir şey değiştirmemesi gereken cevap görevlerini yanlış
keserdi. S-25 olarak yazıldı.

## Yönergenin kendi kusuru

Teşhis 1'in izini sürerken referans yönergede çalışmayan bir satır bulundu.
`prompts/react_code_agent/instructions.reference.txt`, 153. satır:

```text
spotify_password = [account_password["account_name"] == "spotify" for account_password in passwords][0]["password"]
```

Satır alıntı olduğu için biçimlendirilmeden bırakıldı; yönergedeki hâli bu.
Liste kavraması boole üretiyor, `[0]` bir boole veriyor, `["password"]` ise
`TypeError: 'bool' object is not subscriptable` fırlatıyor. Yönerge bu satırın
ardından başarılı bir giriş çıktısı gösteriyor, yani çalışmayan bir satırı
çalışmış gibi sunuyor.

İkinci kusur eksiklik: yönerge `print(login_result)` ile sözlüğü basıyor ama
`login_result["access_token"]` çıkarımını hiç göstermiyor.

Ölçtüğümüz iki arıza bu ikisine oturuyor. 45 epizotta bozuk kalıp 34 kez
yazıldı (13 epizotta) ve 11 kez `'bool' object is not subscriptable` üretti.
Aynı epizotlarda doğru filtre yazımı 488 kez geçiyor, yani model çoğunlukla
düzeltiyor. Kusur gerçek ama baskın sebep değil.

Yönerge değiştirilmiyor (K-19, K-23). Bulgu S-20'ye işlendi.

## Yerel-yalnız kontroller

11 Ağustos 2026: `ruff check` temiz, `ruff format --check` temiz, 133 test
geçti ve atlanan yok, import ve build tamam.

Teşhis 1 ve 2 yeni koşu istemedi. Teşhis 3 için 15 yeni epizot koşuldu ve
hükmüyle birlikte şemaya yazıldı; ham çıktı `results/gpt4o-alt-kume.json`.
Yayımlanmış taban koşuları `appworld download experiment-outputs` ile indirildi
ve toplamları yayımlanmış sayılarla karşılaştırılıp doğrulandı.

## Sırada ne var

Üç teşhis de yol seçimini daraltmadan bırakmadı:

- Kategori 4 baskın değil, yani iskele uyarlaması için önceden yazılan koşul
  sağlanmıyor.
- gpt-4o'nun çözdüğü alt küme bant açmıyor.
- Uygulama kümesi tabakalaması dereceli skorda beş buçuk kat fark veriyor ama
  ikili başarı orada da sıfır, ve `spotify` yönergenin gösterdiği uygulama
  olduğu için kısıt S-19'un riskini büyütüyor.

Karar sizin. Yeni bilgi olarak eklenen tek şey, arızanın büyük kısmının mekanik
ve tekrar eden bir dizi olması — mekanizmanın hedefiyle örtüşüyor, ama aynı
sebeple `irrelevant_retrieval` koşulunun da kazanması bekleniyor. Üç sonucun
yorumu K-59'da sonuç görülmeden yazıldı.
