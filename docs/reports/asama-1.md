# Aşama 1 raporu — AppWorld kurulumu ve tek görev

Bu rapor kodun ne yaptığını değil, neyi doğruladığımı anlatıyor.

## Kabul ölçütü ne diyordu

> Bir görev başlıyor, ajan API çağrıları yapıyor, doğrulayıcı bir hüküm
> döndürüyor, ve bu hüküm okunabilir bir yerde duruyor. Aynı görevi ikinci kez
> koştuğunda veritabanının başlangıç durumuna dönmüş olduğunu doğrula.

Aşama 0'ın gözden geçirmesinde bir madde daha eklendi: temiz makinede kurulum
AppWorld dahil yeniden doğrulanacak, Git LFS önkoşulu REPRODUCE.md'ye yazılacak
(K-32).

## Kurulumu belgeden takip ettim

Resmî sıra şu: `pip install appworld`, sonra `appworld install`, sonra
`appworld download data`. Bizde ilk adım `uv sync --all-groups --frozen`, çünkü
paket PyPI'dan değil GitHub `main` dalından tek bir commit'e sabitlenerek
geliyor (K-10). Kalan iki adım olduğu gibi koşuldu.

Sabitlenen commit `a072b7a`. Kurulan sürüm `0.2.0.dev0`, toplam 114 paket. Veri
198 MB ve `data/` altına açılıyor, dizin izlenmiyor.

Bölme başına görev sayısı: train 90, dev 57, test_normal 168, test_challenge
417.

## Neyi doğruladım

### Görev uçtan uca koşuyor

`scripts/run_single_task.py` referans iskeleyi değiştirmeden kuruyor, tek görevi
koşturuyor ve ardından değerlendirmeyi çağırıyor. Kullanılan sınıf
`SimplifiedReActCodeAgent`, görev `82e2fac_1`, model
`qwen2.5-coder:1.5b-instruct-q4_K_M`.

Ajan API çağırıyor. `logs/api_calls.jsonl` dolu ve çağrılar gerçek uç noktalara
gidiyor: `/spotify/library/playlists`, `/supervisor/account_passwords` gibi.

Doğrulayıcı hüküm üretiyor ve hüküm iki yerde okunabiliyor. Birincisi
`tasks/82e2fac_1/evaluation/report.md`, içinde bir geçen ve bir düşen sınama
var. Geçen sınama `assert no model changes`. Düşen sınama `assert answers
match`, ayrıntısıyla birlikte: `'<<not_given>>' == 'a love that never was'`.
İkincisi `evaluations/on_only_82e2fac_1.txt` ve `.json`, toplu metrikleri
taşıyor ve `task_goal_completion` değerini 0.0 veriyor.

Görev çözülmedi. Kabul ölçütü bunu istemiyor, 1.5B bir modelden AppWorld'ü
çözmesini de beklemiyoruz.

### Veritabanı epizot başına sıfırlanıyor

Testi `tests/test_appworld_reset.py`. Koşu 1 not yaratıp aynı koşuda okuyor,
koşu 2 aynı görevi yeniden açıp o kimliği istiyor ve `409 The note with id 3084
does not exist` alıyor.

Buraya iki yanlış çapadan geçtim. İkisini de yazıyorum, çünkü ikisi de geçen ama
hiçbir şey kanıtlamayan sınamalardı.

İlki `dbs/model_hashes.json` karşılaştırmasıydı. Boş koşularda o dosya `{}`
geliyor. Yani tam durumu değil, yalnız değişen modelleri tutuyor. İki boş
koşunun eşit çıkması, sıfırlama hiç çalışmasa bile olacak bir şeydi.

İkincisi not sayısıydı. `search_notes` sayfalı ve beşte sabit kalıyor.
`create_note` başarıyla dönüp `note_id` verdiği hâlde sayaç kıpırdamadı, yani
sınama değişimi göremiyordu.

Testin gövdesindeki yaratma adımı bu yüzden var. Onsuz sınama, sıfırlama hiç
çalışmasa bile geçerdi.

### Temiz makine kurulumu AppWorld dahil sınanıyor

CI'a `git lfs install` adımı girdi ve `uv sync` artık AppWorld ile birlikte
koşuyor. K-32'nin istediği doğrulama her PR'da tekrarlanıyor.

## Karşılaştığım sürprizler

### Git LFS önkoşulu teoride değil pratikte ısırdı

`uv`, `[tool.uv.sources]` içinde `lfs = true` yazılmadıkça bundle dosyalarını
131 baytlık işaretçi olarak kuruyor. `appworld install` de şu satırla düşüyor:
`File .../apps.bundle is a Git LFS pointer and not a bundle file`. Bayrakla
gelen dosyalar 193950 ve 204426 bayt, elle klonlananla birebir aynı.

Makinede `git lfs` paketi kuruluydu ama `git lfs install` çalıştırılmamıştı,
yani filtre `~/.gitconfig` içinde yoktu. Paketin varlığı yetmiyor.

### Referans iskele `appworld` paketinde değil

`appworld run` komutu `appworld_agents` modülünü istiyor. O modül PyPI'da yok ve
deposu diye tahmin ettiğim adres 404 veriyor. Depodaki
`experiments/code/simplified/` dosyaları da kendi kendine yetmiyor, hepsi
`appworld_agents.*` import ediyor.

Kaynağı aynı depo. `experiments/pyproject.toml`, `appworld-agents` adıyla ikinci
bir dağıtım tanımlıyor ve `appworld_agents = "."` satırıyla `experiments/`
dizinini paket köküne bağlıyor. İkisini de aynı commit'e sabitledim, ikincisi
`subdirectory = "experiments"` ile geliyor.

Yönerge dosyası kurulu paketin içinde geliyor, boyutu 11350 bayt. Aşama 5'in
kopyalama kararı (K-23) bu dosyadan yapılacak.

### İskele `num_ctx` geçirmiyor

K-19 litellm yolunu birinci sıraya koymuştu. Bağlantı o yoldan kuruluyor ama
bağlam penceresi geçmiyor. Sebebi şu: iskelenin `LanguageModel` sınıfı hangi
anahtarların kabul edileceğini `litellm.completion` imzasından çıkarıp beyaz
liste uyguluyor. Listede 41 ad var, `num_ctx` yok. `api_base` de yok, onun
yerine `base_url` var.

Bunun ölçülen sonucu ağır. Ollama bağlam penceresini VRAM'e bakarak 4096
seçiyor. Yönerge dosyası tek başına 11350 bayt ve ajan adım başına yaklaşık 3800
girdi tokenı harcıyor. 4096'lık pencerede koşulan iki epizottan biri 18 API
çağrısı yaptı, diğeri sıfır. İkincisinde model `from apis import api_docs,
supervisor` yazdı, sandbox `Usage of the following module is not allowed: apis`
diyerek reddetti ve hiçbir çağrı sunucuya ulaşmadı.

Sunucu tarafında `OLLAMA_CONTEXT_LENGTH=32768` ile pencereyi açtım. Sıfır
ortadan kalktı ama davranış oynak kaldı, üç epizot 19, 1 ve 19 çağrı yaptı. Bu
yol K-19'un saydığı dördünden hiçbiri değil, beşinci bir yol. Kalıcı karar Aşama
4'ün ve A-05 olarak açık duruyor.

### Aynı seed aynı davranışı vermiyor

Yukarıdaki 19, 1, 19 dizisi aynı seed ve aynı sıcaklıkla alındı. Seed 123,
sıcaklık 0.2. Seed'in Ollama'ya ulaşıp ulaşmadığını doğrulamadım. S-11 olarak
kaydedildi, Aşama 4 ayrıca sınayacak.

### İskele anahtarsız açılmıyor

`LanguageModel`, istemci litellm olsa bile kurucusunda bir `OpenAI()` nesnesi
üretiyor ve o nesne `OPENAI_API_KEY` olmadan açılmıyor. Yerel modelde anahtar
kullanılmadığı için betik yer tutucu bir değer koyuyor. Gerçek bir sağlayıcıya
çağrı gitmiyor.

### Ağ köprüsü beklediğimden ucuza çözüldü

NAT kipinde WSL'den Windows'taki Ollama'ya erişimin üç adresten de kesildiğini
ölçtüm. Sebebi Hyper-V güvenlik duvarının `DefaultInboundAction` değerinin
`Block` olması. `networkingMode=mirrored` bunu güvenlik duvarı kuralı olmadan
çözdü ve sunucunun `0.0.0.0`'a bağlanmasını da gereksiz kıldı. Ollama şimdi
yalnız `127.0.0.1` dinliyor.

K-03'ün DNS kaygısını sınadım, çıkmadı. `pypi.org`, `github.com` ve
`registry.ollama.ai` çözüldü, HTTPS istekleri döndü, `uv lock --check` geçti.
S-10 kapandı.

## Ölçemediklerim

`num_ctx`'in isteğe gerçekten 32768 olarak yansıyıp yansımadığını istek
düzeyinde doğrulamadım. Yalnız sunucunun yapılandırma dökümünde
`OLLAMA_CONTEXT_LENGTH = 32768` yazdığını ve davranışın değiştiğini gördüm.
İstek düzeyinde doğrulama Aşama 4'ün kabul ölçütünde zaten var.

Seed'in Ollama'ya geçip geçmediğini ölçmedim.

Aşama 1'de hiçbir performans ölçümü yok. Sunucu şu an `OLLAMA_KV_CACHE_TYPE`
boş ve `OLLAMA_FLASH_ATTENTION` false ile koşuyor. Aşama 4 onu kendi betiğinden
yeniden başlatacak.

## Yerel-yalnız kontroller

`appworld` işaretli testler CI'da koşmuyor. Listesi REPRODUCE.md içinde,
koşucusu `scripts/local_checks.sh` (K-35).

Son koşu: `2026-08-10T20:57:13+03:00`, commit `68c69c8`. Bir test geçti, yirmi
test elendi.

## Bitmiş sayılma şartları

| Şart | Durum |
|---|---|
| Kodlandı | Evet |
| Testi yazıldı | Evet, 21 test. Biri `appworld` işaretli |
| Loglandı | CHANGELOG girdisi yazıldı |
| Belgesi yazıldı | REPRODUCE, 08-decisions, 09-limitations, PROJECT_STATUS |
| Hata durumu düşünüldü | `MODEL_SERVER_URL` yoksa betik açıklamayla duruyor, rapor dosyası yoksa çıktı bunu söylüyor |
| PR üzerinden gözden geçirildi | PR açıldı |
| Temiz kurulumda baştan çalıştırıldı | CI AppWorld dahil kuruyor. Adımlar REPRODUCE.md'de ve hepsi koşuldu |
