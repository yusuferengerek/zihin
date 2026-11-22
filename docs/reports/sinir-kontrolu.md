# Sınır kontrolü — düzenek çalışıyor mu

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

Üç tabakalama denendi ve üçü de bant açmadı: referans uzunluk, gpt-4o'nun
çözdüğü alt küme, uygulama kümesi. Bütün alt kümelerde ikili başarı sıfır kaldı.
Bu noktada iki açıklama ayrılamıyordu: ya model bandı yetersiz, ya da düzenekte
bir hata var ve hiçbir model geçemez.

**Bu koşu bir bant araması değil, düzenek doğrulaması.** Yayımlanmış tabanlar bu
kıyaslamada sıfır değil. Güçlü bir model bizim düzeneğimizde de sıfır alırsa
hata bizdedir.

## Ne sabit tutuldu

Bant taramasının aynı otuz görevi, görev başına aynı tavan (`2 × çapa`, en az
20, en çok 150), aynı durma kuralı, aynı yakalayıcı, aynı durum sondası, aynı
doğrulayıcı, aynı yönerge dosyası, aynı sıcaklık, aynı `max_tokens`.

Değişen tek şey model ve onu sunan katman:
`openrouter/deepseek/deepseek-v4-flash-0731`.

**Koşu künyeye yazmıyor.** Künye sözleşmesi (K-46) `num_ctx_effective`,
`kv_cache_type`, `keep_alive` ve `context_verified` alanlarını zorunlu tutuyor;
hepsi yerel Ollama kavramı. Barındırılan bir modelde etkin bağlam penceresi
doğrulanamıyor, dolayısıyla `context_verified=1` yazmak yalan olurdu. Koşu
deneyin parçası olmadığı için kendi JSON çıktısına yazıyor — K-52'nin önyükleme
için kurduğu ayrımın aynısı.

## Çıktı bütçesi: yakalanan, yanlış doğrulanan, sonra ölçülen tuzak

Model akıl yürütme üretiyor: yanıtta `content` yanında `reasoning_content` var
ve ikisi aynı çıktı bütçesinden yiyor. On altı jetonluk bir sonda çağrısında
bütçenin tamamı akıl yürütmeye gitti ve `content` boş döndü.

Yerel yapılandırmada `max_tokens` 400. Bütçe yetmezse her adım kodsuz döner ve
sınır kontrolü modelden değil taşımadan sıfır verir — doğrulamayı tam da
kurulduğu amaçtan koparacak bir arıza.

**Yaptığım kontrol yetersizdi.** Tek görevi hiçbir ayar değiştirmeden koşturdum;
on altı adımın on dördü eylem üretti, ikisi kodsuz. "Bütçe yetiyor" diye
yazdım. Yanlıştı. O görev kısa bir görevdi ve sorun bağlam uzadıkça çıkıyor:
konuşma büyüdükçe akıl yürütme uzuyor ve dört yüz jetonu tümden yiyor.

Doğru kontrol tek epizodun ilk adımlarına değil, bütün koşudaki kodsuz adım
oranına bakmaktı. İlk koşuda o oran yüksekti ve `no_progress` ile kapanan 21
epizodun büyük kısmı buradan geliyordu.

**Ölçüm.** Erken kesilen üç epizot, yalnız `max_tokens` değiştirilerek tekrar
koşuldu:

| Görev | 400 jeton | 2000 jeton |
|---|---|---|
| `1150ed6_1` | 6 adım, 1 eylem, 5 kodsuz, kesildi, kaldı | 12 adım, 14 eylem, 0 kodsuz, **geçti** 6/6 |
| `09b0ee6_3` | 6 adım, 2 eylem, 4 kodsuz, kesildi, kaldı | 8 adım, 14 eylem, 0 kodsuz, **geçti** 1/1 |
| `652485c_2` | 5 adım, 1 eylem, 4 kodsuz, kesildi, kaldı | 55 adım, 124 eylem, 18 kodsuz, kesildi, kaldı |

Üçün ikisi kalmaktan geçmeye döndü ve kodsuz adımlar tümden kayboldu.
Üçüncüsünde 18 kodsuz adım kaldı, yani 2000 de bağlayıcıydı.

**Eşitlenen şey sayı değil, bütçenin bağlayıcı olmaması.** Yerel modelde 400
bağlayıcı değil: qwen2.5-coder akıl yürütme üretmiyor ve bant taramasının 958
adımında kodsuz adım sayısı sıfır. API modelinde aynı rejime ulaşmak için bütçe
büyütüldü. İki modele aynı sayıyı vermek, ikisini aynı koşula koymuyor.

Nihai koşu `max_tokens=4000` ile yapıldı. Bağlayıcılık göstergesi kodsuz adım
oranı: 400 jetonda %25,0 (125/501), 4000 jetonda %6,9 (62/902). Hâlâ sıfır
değil, yani bütçe uzun bağlamlarda kısmen bağlayıcı kalıyor ve **%66,7 bir alt
sınır.**

## Sonuç: düzenek çalışıyor

Otuz görev, `openrouter/deepseek/deepseek-v4-flash-0731`, `max_tokens=4000`:

| Ölçüt | Değer |
|---|---|
| Geçen görev | 20/30 = %66,7 |
| %95 alt sınır | %50,1 |
| Anlamlı test (no-op düzeltilmiş) | 95/152 = %62,5 |
| Kodsuz adım | 62/902 = %6,9 |
| Maliyet | 0,62 dolar |

**Sıfır değil, ve az da değil.** Bant taramasındaki sıfırların sebebi düzenek
değil, model kapasitesi.

### Sonradan eklenen not: 20/30 bir alt sınır, iki ayrı sebeple

Tablodaki %50,1 istatistiksel alt sınır, yani örneklem büyüklüğünden gelen. Ondan
bağımsız iki sebeple daha alt sınır, ve ikisi de K-60'ın bağlayıcılık
göstergelerinden:

**Adım tavanı.** Beş epizot `step_ceiling` ile kapandı. Tavana çarpan epizot
devam etseydi görevi bitirebilirdi.

**Durma kuralı.** Dört epizot `no_progress` ile kapandı ve **bu koşu eski durma
kuralıyla yapıldı** — eşik dört, ve ölçüt "başarılı çağrı ilerlemedir". O kuralın
yanlış olduğu sonradan ölçüldü (S-25, S-27): amaçsız başarılı okumaları ilerleme
sayıyor, dolayısıyla erken kesiyor. Bu dördün düzeltilmiş kuralla kesilip
kesilmeyeceği bilinmiyor.

Yani gerçek oran 20/30'un üstünde olabilir; altında olamaz. **Düzeneğin
çalıştığı sonucu bundan etkilenmiyor** — alt sınırın kendisi zaten yayımlanmış
gpt-4o oranının (15/30) üstünde.

Koşu düzeltilmiş kuralla ve seri 2 şemasıyla tekrarlanıyor. Üç kazanç: temiz
sayı, künye satırı (bu otuz epizot veritabanına hiç yazılmamıştı, S-29), ve
düzeltilmiş kuralın düzenek doğrulamasını değiştirip değiştirmediğinin cevabı.

Bu bölümdeki bütün sayılar seri 1'den; sınır kontrolünün epizotları ise hiçbir
seride değil, yalnız `results/sinir-kontrolu.json` içinde.

### Aynı otuz görevde üç nokta

| Model | Hat | Geçen |
|---|---|---|
| DeepSeek V4 Flash 0731 | bizim hattımız | 20/30 = %66,7 |
| gpt-4o-2024-05-13 | yayımlanmış koşu, durma kuralı yok | 15/30 = %50,0 |
| qwen2.5-coder 7B q4_K_M | bizim hattımız | 0/30 = %0 |

gpt-4o satırı bizim koşumuz değil; indirilen yayımlanmış çıktıdan aynı otuz
göreve süzüldü. **Bizim hattımız güçlü bir modele, yayımlanmış bir koşunun aynı
görevlerdeki oranından daha yüksek oran veriyor.** Düzenek yalnız "bozuk değil",
tam olarak çalışıyor.

### Bant başına

| Bant | n | DeepSeek geçen | DeepSeek test | 7B geçen | 7B test |
|---|---|---|---|---|---|
| 1-10 | 6 | 4/6 | 22/25 | 0/6 | 0/25 |
| 11-20 | 6 | 6/6 | 36/36 | 0/6 | 4/36 |
| 21-40 | 6 | 2/6 | 8/31 | 0/6 | 0/31 |
| 41-89 | 6 | 4/6 | 13/30 | 0/6 | 1/30 |
| 90+ | 6 | 4/6 | 16/30 | 0/6 | 1/30 |

Referans uzunluk burada da zorluğu tahmin etmiyor: en kötü bant 21-40, en iyisi
11-20. Bu, gpt-4o'nun yayımlanmış koşusundaki düz profille (%59, %51, %42, %59,
%38) aynı yöne işaret ediyor.

Bant taramasından çıkardığım "kısa görevler daha kolay değil" sonucu, 7B
verisiyle sınırlı olduğu için bilgi taşımıyordu: taban her bantta sıfırdı ve
sıfırlar arasında fark görünmez.

## Durma kuralı hakkında yazdığımın düzeltmesi

400 jetonluk koşuda otuz epizodun 21'i `no_progress` ile kapanmıştı ve bunu
"kural yetenekli modeli de kesiyor" diye yazmıştım. Yanlıştı.

Bütçe bağlayıcı olmaktan çıkınca:

| Sonlanma | 400 jeton | 4000 jeton |
|---|---|---|
| `agent_finished` | 7 | 21 |
| `no_progress` | 21 | 4 |
| `step_ceiling` | 2 | 5 |

`no_progress` 21'den 4'e düştü ve o dördün yalnız biri gpt-4o'nun çözdüğü
görev. Yani kesilmelerin büyük kısmı kuralın katılığı değil, bizim çıktı
bütçemizdi. Kural, bütçe düzeldiğinde iyi davranıyor.

Kuralın kendisi zaten doğru sebeple ateşliyordu: `b9c5c9a_3` epizodunda son dört
etkileşimin dördü de boş kod bloğuydu ("No code available to execute"). Kural
boşluğu doğru okuyordu; boşluğun sebebi başkaydı.

## Karar ağacına söylediği

Düzenek sağlam çıktı, yani eşiğin nerede olduğunu arama yolu açık. Buradan
çıkan üç somut şey:

1. **7B'nin sıfırı model kapasitesi.** Aynı hatta güçlü bir model 20/30
   alıyor. Bant taramasının ve teşhislerin sonuçları ayakta.
2. **Ölçek ekseni için sıfırın üstünde nokta var, ama yerel değil.** A-06'nın
   sorduğu şey buydu; bu koşu ekseni yerel donanımın dışına taşımanın
   ölçülebilir bir sonuç verdiğini gösteriyor, hangi noktanın seçileceğini
   değil.
3. **Ölçüm hattı ön kayda girebilir durumda.** Yakalayıcı, durum sondası, durma
   kuralı, doğrulayıcı ve dereceli skor, geçen epizot üreten bir modelde uçtan
   uca çalıştı.

## Yerel-yalnız kontroller

12 Ağustos 2026: `ruff check` temiz, `ruff format --check` temiz, 133 test
geçti ve atlanan yok, import ve build tamam.

Ham çıktılar: `results/sinir-kontrolu.json` (400 jeton),
`results/sinir-kontrolu-4000.json` (4000 jeton),
`results/sinir-jeton-2000.json` (üç görevlik bütçe denemesi).
