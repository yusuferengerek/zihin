# Model ailesi taraması

> **Bu tarama iptal edilen bir karara aitti (K-101).** Aile kilidi sınır
> kontrolünden sonra yeniden açılmış, sonra kullanıcı aileyi değiştirmeme kararı
> vermişti. Eksen Qwen2.5-Coder olarak kalıyor ve aşağıdaki adaylar taranmadı.
> Rapor, yapılmış çalışmanın kaydı olarak duruyor: bir ölçüm, ait olduğu karar
> iptal edildi diye geçersizleşmiyor.

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

Sınır kontrolü düzeneğin çalıştığını gösterdi: aynı otuz görevde güçlü bir
model 20/30 alıyor, yerel 7B 0/30. Sıfır düzenekten değil model kapasitesinden
geliyor. Bu, aile kilidini yeniden açıyor.

**Kilit hiçbir zaman "Qwen2.5-Coder olmalı" değildi.** Şart şuydu: tek aile,
birden çok yoğun boyut, akıl yürütme modu olmayan, sekiz gigabayta sığan.
Qwen2.5-Coder 2024 sonundan bir aile; aynı şartları tutan daha yeni bir aile
aynı boyutta daha yetenekli olabilir.

## Aday listesi nasıl çıkarıldı

Ollama kayıt sunucusunun manifest ucu doğrudan sorgulandı
(`registry.ollama.ai/v2/library/<aile>/manifests/<etiket>`). Yöntem bilinen bir
modelle doğrulandı: `qwen2.5-coder:7b-instruct-q4_K_M` için 4,68 GB döndü, yani
yüklü dosyayla uyuşuyor.

Otuz üç aile × on iki boyut tarandı. Eşik 6,5 GB: sekiz gigabayt VRAM'den 32K
bağlamın q8_0 KV cache'i için pay ayrıldı (K-45'te 7B için ölçülen 0,9 GiB).

| Aile | 6,5 GB altına sığan boyutlar | Not |
|---|---|---|
| `qwen3.5` | 0.8b, 2b, 4b (9b=6,6 GB sınırda) | Kendi sayfası mimarisini "sparse Mixture-of-Experts" diye tanımlıyor |
| `qwen2.5-coder` | 0.5b, 1.5b, 3b, 7b | Şu anki aile |
| `qwen2.5` | 0.5b, 1.5b, 3b, 7b | Kod uzmanı değil |
| `qwen3` | 4b, 8b | Hibrit düşünme modu var |
| `falcon3` | 1b, 3b, 7b | Yoğun |
| `granite3.3` | 2b, 8b | Yoğun |
| `granite4` | 1b, 3b | Bazı boyutları hibrit mimari |
| `gemma3` | 1b, 4b | 12b=8,1 GB sığmıyor |
| `gemma2` | 2b, 9b | 2024 |
| `cogito` | 3b, 8b | Hibrit akıl yürütme modu var |
| `codegemma` | 2b, 7b | 2024 |
| `starcoder2` | 3b, 7b | 2024 |
| `yi-coder` | 1.5b, 9b | 2024 |
| `llama3.2` | 1b, 3b | 3b'nin üstü sığmıyor |

Tek boyutu sığanlar (eksen kurulamaz): `gemma4` yalnız 12b=7,4 GB, `glm4`
yalnız 9b, `mistral` yalnız 7b, `llama3.1` yalnız 8b, `olmo2` yalnız 7b.
`phi4` 14b=9,1 GB ile sığmıyor.

**Güncel kod uzmanı aile yok.** `qwen3-coder` 30b ve 480b sunuyor, ikisi de
sınırın çok üstünde.

## Şarta takılan iki aday

`qwen3.5` en yeni ve en çok boyut sunan aile, ama kendi model sayfası
mimarisini "Gated Delta Networks combined with sparse Mixture-of-Experts"
diye tanımlıyor. Şart yoğun boyut istiyor. Kütüphane listesi onu yoğun diye
gösteriyor, model sayfası seyrek diyor; çelişki bu veriden çözülemedi.

`qwen3` ve `cogito` hibrit düşünme modu taşıyor. `qwen3` için mod
kapatılabiliyor (`/no_think`), ama şart "akıl yürütme modu olmayan" diyor ve
modun varlığı kapatılabilir olmasından bağımsız.

İkisi de ölçüme alındı, çünkü yetenek eşiği geçilmezse mimari tartışması
gereksiz kalıyor. Şarta uygunluk kararı sizin.

## Eleme tasarımı

Her adayın sekiz gigabayta sığan en büyük boyutu, bant taramasının **on iki**
görevinde: 1-10 bandının altısı ve 11-20 bandının altısı.

Neden bu on iki: sınır kontrolünde DeepSeek 1-10'da 4/6, 11-20'de 6/6 aldı; 7B
ikisinde de 0/6. Ayrımın en keskin olduğu yer burası. Bir aday burada sıfır
alıyorsa otuz görevde %25 eşiğini geçemez ve tam koşu israf olur.

Çıktı bütçesi K-60 gereği raporlanıyor: kodsuz adım oranı sıfıra yakın değilse
sonuç alt sınır olarak yazılıyor.

## Sonuç

SONUC-BURAYA
