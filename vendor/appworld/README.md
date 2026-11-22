# AppWorld yansısı — geri düşüş, birincil yol değil

Bu depo iki tekerleği taşımıyor. Yansı, bu deponun kurulduğu özel arşivde duruyor ve
hakemlere istek üzerine veriliyor. **Birincil kurulum yolu değiller.** Önyükleme her
zaman önce yukarı akışa gidiyor.

| | |
|---|---|
| Yukarı akış kaynağı | `https://github.com/StonyBrookNLP/appworld.git` |
| Sabitlenen commit | `a072b7a86e7c1d5b1d7175659d750ebb9b79f10a` |
| `appworld-0.2.0.dev0-py3-none-any.whl` | sha256 `13965100b4e6191e5503c06a24f9b9140b0f04a95a56c8394c29bc6f094c67e3` |
| `appworld_agents-0.1.0.dev0-py3-none-any.whl` | sha256 `32fcd23f68b86c08fdf357fe409a8823fdc7ae64582d784dcf046374cd739e73` |

## Neden var

20 Ağustos 2026'da Colab önyüklemesi `uv sync` sırasında durdu: sabitlenen
commit'in `.bundle` nesneleri Git LFS'ten çekilirken GitHub

> `This repository exceeded its LFS budget.`

diyerek **403** döndürdü. Aynı yanıt geliştirme makinesinden de alındı, yani bu
Colab'ın ağıyla ilgili değil — yukarı akış deposunun durumu. Bütçe bizim değil,
depo bizim değil, ve ne zaman açılacağı bizim elimizde değil.

## PyPI neden yeterli olmadı

Ölçüldü, tahmin edilmedi:

| | |
|---|---|
| PyPI'daki en yüksek sürüm | `0.1.3.post1` |
| Etiketin gerçek tarihi | 2024-10-14 (`v0.1.3`) |
| Bizim sabitimiz | `a072b7a86`, 2026-02-17, `0.2.0.dev0` |
| Aradaki commit sayısı | **196** |
| `appworld-agents` PyPI'da | **yok** (HTTP 404) |

İkinci satır kararı tek başına veriyor: referans iskele (K-19) `appworld-agents`
dağıtımının içinde ve o dağıtım PyPI'da hiç yayımlanmamış — depoya `#174`
commit'iyle, `v0.1.3`'ten *sonra* girmiş. PyPI'ya geçmek 196 commit geri gitmek
ve iskeleyi kaybetmek demekti. Sessizce yapılabilecek bir şey değil; yapılmadı.

## Ne olduğu ve aynılığının nasıl bilindiği

Tekerlekler, yukarı akış nesneleri hâlâ sunulurken çekilmiş yerel bir
checkout'tan üretildi. `PROVENANCE.json` kaynak commit'i, alınma tarihini ve
özet değerlerini taşıyor.

Aynılık iddiası **ölçülüyor**: bir bundle'ın sha256'sı onun Git LFS nesne
kimliğidir. Kurulumdan sonra `record_appworld_source.py` kurulu bundle'ları
özetleyip `PROVENANCE.json`'daki kimliklerle karşılaştırıyor. Tutmazsa önyükleme
duruyor — o noktada neyin kurulu olduğu bilinmiyor demektir.

## Künyeye ne yazılıyor

Yansı kullanıldığında künyenin `os_environment` alanı şunu taşıyor:

```
Linux <sürüm> / <python> / appworld: mirror a072b7a86 (2026-08-20)
```

Yukarı akıştan kurulduğunda `appworld: upstream`. Sessiz bir geri düşüş ölçümün
kaynağını gizler; bu yüzden geri düşüş sessiz değil.

## Yukarı akış düzeldi mi

```
uv run python scripts/check_upstream_lfs.py
```

`download action present` çıkarsa bütçe geri gelmiş demektir. O andan sonra
önyükleme kendiliğinden yukarı akışı kullanır — burada geri alınacak bir şey
yok, çünkü yansı hiçbir zaman birincil yol olmadı.

## Yeniden üretmek

```
CO=$(mktemp -d)
git clone https://github.com/StonyBrookNLP/appworld.git "$CO"
git -C "$CO" checkout a072b7a86e7c1d5b1d7175659d750ebb9b79f10a
git -C "$CO" lfs pull            # yukarı akış bütçesi açıkken
uv build --wheel --out-dir vendor/appworld "$CO"
uv build --wheel --out-dir vendor/appworld "$CO/experiments"
```

Üretilen tekerleklerin özet değerleri `PROVENANCE.json`'dakilerle tutmalı.
