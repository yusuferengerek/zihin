# Projenin teknik olguları

Bu dosya projenin **atıf verilebilir teknik olgularını** çıkarıyor: ne kuruldu,
ne ölçüldü, hangi sayı söylenebilir ve hangi cümle kurulamaz. Sunumu besliyor.

Sayılar tek yerde duruyor; burada manşet değerler ve kaynak dosyaları var.

---

## Bir cümlede

AppWorld üzerinde, derlenmiş becerilerin ve açık bir başarısızlık indeksinin
görev çözmek için gereken model çağrısı sayısını düşürüp düşürmediğini ölçen bir
araştırma koşum aracı. Mekanizmalar kuruldu ve çalıştıkları gösterildi; hipotez
ön koşul kapısı ateşlediği için henüz test edilmedi.

## Ne kuruldu

| Bileşen | Ne yapıyor |
|---|---|
| Kayıt defteri | Yalnız ekleme SQLite şeması, dört düzey, yedi kayıt tablosu artı iki türetilmiş projeksiyon; `UPDATE`/`DELETE` tetikleyiciyle engelli |
| Beceri derleyicisi | Kayıttan kapalı örüntü madenciliği; boşluk kısıtlı dizi eşleme, serbest parametre çıkarımı |
| Hata indeksi | Başarısız çağrılardan kalıp çıkarımı, ayırt edici koşul araması |
| Sembolik getirici | Görev metninden uygulama çıkarımı, kart eşleme; gömme yok (bilerek) |
| Kart biçimi | Yedi alanlı beceri kartı, beş alanlı hata kartı, jeton bütçeli |
| Kalkan | Eylem öncesi yüklem; saf fonksiyon karar, ayrı montaj noktası |
| Sandbox | Kök yetkisiz konteyner, ağsız, salt okunur kök; kayıt konteyner dışında bir loopback vekilinde |
| Koşum aracı | Referans iskeleye dokunmadan kayıt; künye sözleşmesi, devam denetimi, kirli ağaç kapısı |

**Ölçek:** kütüphane `src/zihin/` altında 5825 satır Python; betikler ve testler
15191 satır. 460 test, beş CI kontrolü.

## Atıf verilebilir ölçümler

Hepsi makine okunur bir dosyada; parantez içinde kaynak.

**Mekanizma ölçümleri**

- Kart jeton bütçeleri sınandı: beceri kartı ≤180, hata kartı ≤120; üç tokenizer
  aynı sayıyı verdi (`results/card-tokens.json`)
- Birleştirilmiş bağlam k=5+5 ile 32K pencereye sığıyor; sabit blok pencerenin
  **%9,7**'si (train medyanı 0,0968) (`results/context-cost.json`)
- Etkin bağlamı belirleyen şey jeton penceresi değil, iskelenin karakter tavanı:
  50000 karakter = **12799 jeton** (S-47)
- Getirme kapsaması `test_normal`'da 168/168; ölçüm tek boyutlu
  (`results/retrieval-coverage.json`)
- Kalkanın yanlış pozitif oranı **%4,1**; uygulama kümesi hata oranı %24,5 —
  ikisi ayrı sayı (`results/pilot-dataset.json`)

**Ölçümün kendisine dair ölçümler**

- Sandbox katmanı ajanın gördüğü metni değiştirmiyor: üç kol, aynı özet
  (`results/transparency.json`)
- Vekilin telden kurduğu kimlik kayıtlı kimlikle **5261/5261** eşleşiyor;
  imzasız kontrol kolunda 1090 eşleşmiyor (`results/wire-identity.json`)
- Konteynerin ağ yalıtımı iki platformda ölçüldü; dört kipten biri sıfır erişim
  veriyor (`results/container-network.json`)
- Yörünge tekdüzeliği: iki modelde 0/30 ayrışma, Clopper-Pearson tek yanlı %95
  üst sınır **%4,9** (S-21)
- CI kapsaması: koşan test 365 → 446, bedeli duvar saatinde 26 saniye
  (`results/ci-kapsam.json`)

**Ön koşul kapısı**

- 11 Ağustos 2026'da ateşledi: üç yerel model, otuz görev, **0/30**
- Durma kuralı tamamen kapalıyken tekrarlandı: yine **0**
- Üç tabakalama denendi, hiçbiri ölçülebilir bant açmadı

## Kurulamayan cümleler

Sunum bu cümleleri **kuramaz**; hepsi ölçülmüş bir sebeple.

| Kurulamayan | Sebep |
|---|---|
| "Mekanizmalar model çağrısı sayısını %X düşürdü" | Birincil hücre hiç koşulmadı |
| "Kazanç içerikten geliyor, hacimden değil" | `irrelevant_retrieval` koşulu koşulmadı |
| "Etki model boyutuyla azalıyor" | Ölçek ekseni koşulmadı |
| "DeepSeek V4 Flash 0731, düşünme kapalı, 20/30" | O koşuda düşünme açıktı ve ilan edilen koşul değildi (S-34) |
| "Kütüphane aynı kimlikle yeniden üretilebiliyor" | İçerik üretilebiliyor, kimlik derleyici commit'i taşıdığı için üretilemiyor |

## Yöntemsel taraf — projenin ayırt edici yanı

Teknik beceriden çok yöntem tarafı ayırt edici; olgular şunlar:

- **Ön kayıt, ölçümden önce.** Hipotez, birincil hücre, estimand, altı kapı ve
  yorum tablosu koşudan önce yazıldı (`experiments/preregistration.md`).
- **Yanlışlama kapıları ve terk kriterleri.** Bir mekanizmanın hangi gözlemle
  **bırakılacağı**, yeniden ayarlanmayacağı önceden yazılı
  (`docs/11-falsification.tr.md`).
- **Kapı ateşlediğinde tasarım korundu.** Ön koşul kapısı ateşleyince mekanizma
  sonuçları raporlanmadı ve model ailesi yeniden seçildi; eşik oynatılmadı.
- **Sınırlamalar numaralandırılıp takip ediliyor.** 51 kayıt
  (`docs/09-limitations.tr.md`), her biri ölçülmüş bir arızadan.
- **Korumaların ateşlediği gösteriliyor.** Bir kontrol, yakalaması gereken şeyi
  yakaladığı gösterilmeden kabul edilmiyor; güvenlik testlerinin her biri
  korumasız kolda başarılı olduğu gösterilerek yazıldı.
- **Ölçüm aletinin kendisi sınandı.** Kaydedicinin montaj noktası mutasyonla
  çivili; CI ortamı yerelde yeniden üretiliyor ve o kancanın kendisi de
  ateşlediği gösterilerek kabul edildi.

## Kullanılan teknolojiler

Python 3.11, SQLite, FastAPI/uvicorn (AppWorld'ün sunulan kipi), podman (kök
yetkisiz konteyner), Ollama (yerel model sunumu), pytest, ruff, uv, GitHub
Actions.
