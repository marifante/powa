FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y git curl pipx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pipx install poetry && pipx ensurepath

RUN mkdir -p /home/powa && \
    useradd -m embeddev && \
    groupadd -r powa && \
    usermod -aG powa root && \
    usermod -aG powa embeddev && \
    chown -R embeddev:powa /home/powa

WORKDIR /home/powa

COPY . .

ENTRYPOINT ["/bin/bash", "--login"]

FROM base AS dev

RUN pipx install poetry && pipx ensurepath && \
    /root/.local/bin/poetry install --no-interaction && \
    /root/.local/bin/poetry install --only dev --no-interaction

FROM base AS prod

USER embeddev

RUN pipx install poetry && pipx ensurepath && \
    /home/embeddev/.local/bin/poetry install --no-interaction
