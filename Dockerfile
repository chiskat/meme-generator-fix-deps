FROM python:3.10 AS tmp

WORKDIR /tmp

RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH="${PATH}:/root/.local/bin"

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry self add poetry-plugin-export \
  && poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10-slim AS app

WORKDIR /app

EXPOSE 2233

VOLUME /data

ENV TZ=Asia/Shanghai \
  LOAD_BUILTIN_MEMES=true \
  MEME_DIRS="[\"/data/memes\"]" \
  MEME_DISABLED_LIST="[]" \
  GIF_MAX_SIZE=10.0 \
  GIF_MAX_FRAMES=100 \
  BAIDU_TRANS_APPID="" \
  BAIDU_TRANS_APIKEY="" \
  LOG_LEVEL="INFO"

COPY --from=tmp /tmp/requirements.txt /app/requirements.txt

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    fontconfig \
    fonts-noto-color-emoji \
    libgl1 \
    libgl1-mesa-dri \
    libegl1 \
    gettext \
  && rm -rf /var/lib/apt/lists/*

COPY --chown=root:root ./resources/fonts/ /usr/local/share/fonts/meme-generator/

RUN fc-cache -fv \
  && fc-list | grep -q "NotoColorEmoji" \
  && test "$(find /usr/local/share/fonts/meme-generator -type f | wc -l)" -gt 0

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./meme_generator /app/meme_generator

COPY ./docker/config.toml.template /app/config.toml.template
COPY ./docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh
RUN python -m meme_generator.cli

CMD ["/app/start.sh"]
