# Colab'da koşturma

Defter: `zihin-colab.ipynb`. Şartlar ve önceden ilan edilmiş yorum:
`experiments/setup-protocol.tr.md` §15.

> ## Defter her oturumda **depodan** açılıyor
>
> Drive'a kaydedilmiş bir kopya **kullanılmıyor**. Tek kaynak deponun içindeki
> `experiments/colab/zihin-colab.ipynb` dosyası.
>
> **Sebebi ölçüldü.** Drive'a kaydedilen bir kopya kaydedildiği anda donuyor.
> Bir kopya birleşmiş bir dalı çekmeye devam etti; o daldan sonra eklenen
> dosyalar temiz kurulumda yoktu, ve arıza kendini `FileNotFoundError` diye
> adlandırdı — yani "bu dosya hiç yazılmadı" gibi okundu. Depodaki defter
> düzeltildi ve **düzeltme koşan esere ulaşmadı**.
>
> **Kaydedilmiş bir kopya kullanılırsa hiçbir düzeltme ulaşmaz.** Depodaki
> defterin doğruluğunu denetleyen test (`tests/test_colab_ref.py`) deponun
> dosyasını okuyor; Drive'daki kopya o denetimin öznesi değil (`S-69`).
>
> **Nasıl açılır:** aşağıdaki doğrudan bağlantı, ya da Colab'da **Dosya → Not
> defteri aç → GitHub**. Colab "Drive'a bir kopya kaydet" önerirse, o kopya
> okumak içindir, koşturmak için değil.

---

## Bir kez yapılacak: GitHub jetonu

**Colab'ın GitHub yetkilendirmesi bu iş için yetmiyor.** O yetkilendirme defteri
*açmaya* yarıyor; depoyu klonlamak ve sonuçları geri itmek ayrı bir jeton
istiyor. İkisi farklı şey, ve ilk denemede bu karıştırıldı.

1. <https://github.com/settings/personal-access-tokens/new> adresini açın —
   **fine-grained** jeton.
2. **Repository access:** Only select repositories → `zihin`.
3. **Permissions → Repository permissions → Contents:** `Read and write`.
   Başka izin gerekmiyor.
4. Jetonu oluşturun ve **kopyalayın** (bir daha gösterilmiyor).
5. Colab'da soldaki **anahtar simgesi** (Secrets) → **Add new secret**:
   - Name: `GITHUB_TOKEN`
   - Value: kopyaladığınız jeton
   - **Notebook access** anahtarını açın.

Jeton hiçbir dosyaya yazılmıyor, ekrana basılmıyor ve commit'lenmiyor. Klon
sırasında `origin` adresinin içinde duruyor; oturum sanal makinesi tek
kullanıcılı ve oturum bitince yok oluyor.

---

## Defteri açma — iki ayrı yetki, iki ayrı adım

Bu iş **iki** yetkiye dayanıyor ve ilk denemenin çoğunu ikisinin karıştırılması
yedi:

| Yetki | Neye yarıyor | Nerede duruyor |
|---|---|---|
| Colab'ın GitHub yetkilendirmesi | Defteri **açmaya** | Colab ↔ GitHub, bir kez |
| `GITHUB_TOKEN` (yukarıdaki jeton) | Depoyu **klonlamaya**, sonuçları **itmeye** | Colab Secrets |

Biri diğerinin yerine geçmiyor: yetkilendirme olmadan defter açılmıyor, jeton
olmadan ikinci bölümdeki klon ve beşinci bölümdeki itme düşüyor.

**Doğrudan bağlantı** — yetkilendirme tamamlandıktan sonra çalışıyor:

<https://colab.research.google.com/github/yusuferengerek/zihin/blob/main/experiments/colab/zihin-colab.ipynb>

Adresin içinde dal adı var; dal değişirse bu bağlantı da değişiyor. Dal adı **tek yerde** yaşıyor — defterdeki `ZIHIN_REF` varsayılanı — ve bu belgenin onunla aynı adı söylediğini `tests/test_colab_ref.py` çiviliyor. Bir kez ayrıştı: defter birleşmiş bir özellik dalını çekmeye devam etti ve temiz bir Colab kurulumu `main`'de olan dosyaları eksik gördü.

**404 görürseniz adres yanlış değil, yetkilendirme tamamlanmamış.** GitHub, özel
bir depoyu göremeyen bir isteğe 403 değil **404** döndürüyor. Bu kasıtlı: 403
"burada bir depo var ama giremezsin" demek olurdu ve deponun varlığını açık
ederdi. Yani buradaki "bulunamadı" çoğu zaman "henüz yetkin yok" demek. *(403
yerine 404 GitHub'ın belgelenmiş davranışı; bu depoda ölçülmedi. Gözlenen kısım
şu: yetkilendirme tamamlanmadan 404 geldi, tamamlandıktan sonra aynı adres
açıldı.)*

Yetkilendirmeyi tamamlama yolu, ki aynı zamanda ikinci açma yolu:

1. Colab'da **Dosya → Not defteri aç**.
2. **GitHub** sekmesi, ve istenirse GitHub'a yetki verin.
3. **"Özel depoları dahil et"** kutusunu işaretleyin.
4. Depo: `yusuferengerek/zihin`, dal: `main`.
5. `experiments/colab/zihin-colab.ipynb`.

Yetkilendirmeden sonra **iki yol da** çalışıyor.

Sonra **Çalışma zamanı → Çalışma zamanı türünü değiştir → A100 GPU**.
Şartlar tablosu (`runtime`, §19.6) A100 diyor; ilan edilen modelin ölçülen
dosyası 19,851 GB ve T4'ün 15360 MiB'ine sığmıyor.

---

## Seri 3 Drive'da: bir kez kopyalanacak, her oturumda doğrulanacak

Drive'daki `MyDrive/zihin/results/zihin-3.sqlite` **yarım** bir dosyaydı: yerel
yarı (`b3l`, `b7l`, `b15l`, `b32`) yok, `run_ledger` tablosu yok (`S-74`,
`K-171`). Birleşik kayıt yerelde duruyor ve tablo kurulu; her önekin kaç epizot
taşıdığı `results/series-3-merge.json`'da.

1. Drive'daki eski dosyanın adını değiştirin — silmeyin — örneğin
   `zihin-3-colab-269.sqlite`.
2. Yerel dosyayı Drive'a aynı yere, aynı adla kopyalayın: WSL'de
   `/home/yusuf/zihin/results/zihin-3.sqlite`, Windows'tan
   `\wsl$\zihin\home\yusuf\zihin\results\zihin-3.sqlite`.

**Önyükleme bunu kendisi doğruluyor** (E adımı, `K-173`): dosya yoksa ya da
birleşmenin bıraktığı öneklerden biri eksik ya da küçükse ya da `run_ledger` yoksa
**duruyor** ve problemleri tek tek yazıyor. Geçerse şunu söylüyor:

```
episodes: 389 (the merge left 389); prefixes: {...}
the series holds everything the merge left, and the ledger table
series 3: verified on Drive and linked; resume will skip what is already written
```

Drive'da dosya bulamayan bir oturum artık yeni, boş bir seri **kurmuyor**; seriyi
ikinci kez bölen tam olarak buydu.

---

## Çalıştırma sırası — "tümünü çalıştır" DEĞİL

Defterde kasıtlı bir **kontrol noktası** var: dilim başlamadan önce ortam
ölçümüne bakılıyor.

| Sıra | Hücreler | Ne yapıyor |
|---|---|---|
| 1 | 1 → 3 | Drive, jeton kontrolü, klon, önyükleme, **ortam ölçümü** |
| — | **durun ve okuyun** | GPU, VRAM, tam yerleşiklik, yükleme süresi |
| 2 | 4 | Deney, faz 1: bildirilen sıranın sıradaki `--tasks` görevi, her görevde üç tohum ve üç koşul |
| 3 | 5 | Sonuçları `colab-sonuclari` dalına itme |

Dördüncü hücre kendini de koruyor: ortam ölçümü koşmamışsa ya da model tamamen
VRAM'de değilse **başlamıyor**. Kontrol noktası insana bırakılmıyor, ama
insanın bakması da bekleniyor.

**Oturum kesilirse** dördüncü bölümü yeniden çalıştırmak yeterli: yarım dilim önce
tamamlanıyor, yazılmış epizotlar atlanıyor ve bu sınanmış
(`tests/test_run_experiment.py`). Dilimin boyutunu Pro+ tahsisine göre siz
seçiyorsunuz; ilk dilimin maliyeti önyükleme ölçümüyle birlikte hesaplanacak.

---

## Klon adımı düşerse

İkinci bölüm, git'i çağırmadan önce üç şeyi ayrı ayrı kontrol ediyor ve düşerse
**hangisinin** düştüğünü yazıyor. Sebebi ölçülmüş: `git clone` en az dört ayrı
arızayı aynı `128` çıkış koduyla bildiriyor ve kod hiçbirini ayırmıyor.

| Gördüğünüz satır | Anlamı | Yapılacak |
|---|---|---|
| `/user -> 401` | Jeton geçersiz ya da süresi dolmuş | Yeni jeton, `GITHUB_TOKEN` güncelle |
| `/repos/... -> 404` | Jeton geçerli, bu depoyu göremiyor | Jetonda `zihin` seçili mi, `Contents` verilmiş mi |
| `... dalı -> 404` | Dal adı yanlış ya da dal itilmemiş | Dal adını kontrol edin |
| `... var ama checkout değil` | Dizin dolu, klon yazamıyor | Hücrenin yazdığı `rm -rf` komutunu koşturun |

Bunların dışında bir şey düşerse git'in kendi cümlesi ekrana geliyor; çıkış kodu
tek başına gösterilmiyor.

**Jeton hiçbir hata metninde görünmüyor.** Komut satırına girmiyor: git onu
`GIT_ASKPASS` ile ortamdan okuyor. Bu bir ölçüm sonucu — önceki biçim jetonu
klon adresinde taşıyordu ve klon düşünce Python'un hata izi jetonu tam metin
hâlinde bastı.
