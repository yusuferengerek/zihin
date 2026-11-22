# Sandbox imajı: ajanın ürettiği kodun koştuğu yer.
#
# **İçinde tam `appworld` paketi var** (K-B). İnce bir RPC istemcisi imajı
# küçültürdü ama ajanın gördüğü arayüzü sessizce değiştirirdi; K-19'un şartı aynı
# mesajların gitmesi ve aynı metnin dönmesi.
#
# **Bağımlılıklar kilit dosyasından kuruluyor.** `uv sync --frozen`, yani
# konteynerdeki sürümler host'takilerle aynı kilitten geliyor. İki taraf ayrı
# çözülürse ajan başka bir AppWorld sürümüyle konuşur ve fark sessiz kalır.
#
# **`data/` imaja girmiyor.** Salt okunur bağlanıyor (K-96): gömmek damganın
# veriyi de kapsamasını sağlardı ama 198 MiB'ı ikinci bir yerde çoğaltırdı.
#
# **Git LFS şart.** AppWorld'ün `apps.bundle` ve `tests.bundle` dosyaları depoda
# LFS ile duruyor; filtre kurulmadan `uv` onları 131 baytlık pointer olarak
# indiriyor ve `appworld install` "is a Git LFS pointer" diye düşüyor.
#
# Kök salt okunur koşuyor ve yazılabilir tek alan tmpfs; ikisi de `podman run`
# bayrağı, imajın kendisi onları bilmiyor.

FROM docker.io/library/python:3.11-slim-bookworm

# git ve git-lfs: AppWorld GitHub'dan sabit bir commit'ten kuruluyor.
# curl: uv kurulumu için.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git git-lfs curl ca-certificates \
    && git lfs install --system \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11.28 /uv /uvx /usr/local/bin/

WORKDIR /zihin

# Önce yalnız kilit ve tanım: bağımlılık katmanı kaynak değişince yeniden
# kurulmasın.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-group dev

COPY src ./src
RUN uv sync --frozen --no-group dev

# AppWorld'ün uygulama modülleri paketin içinden açılıyor. Veri indirilmiyor:
# `data/` salt okunur bağlanıyor.
RUN uv run appworld install

# Ortam sunucusunun ve köprünün beklediği yerler. Soket dizini salt okunur
# bağlanıyor; oluşturuluyor ki bağlama noktası imajda hazır olsun.
RUN mkdir -p /bridge /zihin/data /zihin/experiments/outputs

# `HOME` yazılabilir alana bakıyor: kök salt okunur koşuyor ve ev dizinine yazmak
# isteyen bir kütüphane koşuyu düşürürdü. Ölçüldü — `uv run` çalışma anında
# `/root/.cache/uv` altına geçici dosya açmaya çalışıp "Read-only file system"
# ile düştü.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APPWORLD_ROOT=/zihin \
    HOME=/tmp \
    PATH=/zihin/.venv/bin:$PATH

# Giriş noktası doğrudan sanal ortamın Python'u, `uv run` değil. Sebebi ölçüldü:
# `uv run` çalışma anında yazılabilir bir önbellek istiyor ve salt okunur kökte
# düşüyor. Kurulum aşamasında uv gerekiyor, koşu aşamasında gerekmiyor.
ENTRYPOINT ["/zihin/.venv/bin/python", "-m", "zihin.container_entry"]
CMD ["/bridge/apis.sock", "8123"]
