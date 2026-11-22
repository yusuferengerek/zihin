# `inputs/` — koşunun okuduğu, koşunun üretmediği dosyalar

Buradaki her dosya bir **girdi**. Hiçbiri bir koşunun çıktısı değil ve hiçbiri
bir koşu tarafından yazılmıyor.

## Dizin neden var

`results/` bir rol ilan ediyor: *"bu üretilmiş bir sonuç"*. `write-set-static.json`
orada duruyordu ama rolü tam tersiydi — kalkanın neyi engelleyip neyi geçireceğini
o belirliyor, yani **ölçümü tanımlayan** bir eser. Yanlış ilan yerel makinede
görünmüyordu, çünkü dosya oradaydı; taze bir klonda görünür oldu ve koşu
`FileNotFoundError` ile düştü.

Dizinin adı, dosyanın ne olduğunu söyleyen ilk şey. Bir girdi çıktı dizininde
durursa, `.gitignore` onu eler ve kimse fark etmez.

## Neden yeniden üretmiyoruz

Yeniden üretmek ortamlar arası **sessiz** fark bırakır. Kurulu `appworld`
paketi biraz farklıysa yazma kümesi farklı çıkar, kalkan başka davranır, ve
hiçbir şey uyarı vermez. AppWorld yansısıyla aynı mantık (`vendor/appworld/README.md`):
dosya depoda durur,
her ortam **aynı baytları** alır, ve doğruluğu bir özet karşılaştırmasıyla
sınanır.

## Doğrulama

```bash
uv run python scripts/setup/derive_write_set.py --check
```

Kurulu `appworld` paketinin rota tablosundan yeniden türetir ve buradaki
dosyayla **bayt bayına** karşılaştırır. Tutmazsa çıkış kodu 1 ve sebebi yazılı.
Bu denetim ön koşul denetiminin (`check_prerequisites.py`) içinden de koşuyor,
yani koşudan önce.

## İçindekiler

| Dosya | Kim okuyor | Nereden geliyor |
|---|---|---|
| `write-set-static.json` | Kalkan (`shield.load_write_set`), derleyici, madenci | `derive_write_set.py`, kurulu appworld paketinden türetildi |

296 yazar uç ve sınır geçen 19 sayısı bu dosyadan geliyor ve raporlarda
alıntılanıyor. Sayıların her ortamda aynı olması, dosyanın her ortamda aynı
olmasına bağlı.
