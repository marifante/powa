FROM python:3.11-slim AS prod

RUN apt-get update && apt-get install -y git curl pipx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m embeddev

USER embeddev

RUN pipx install poetry && pipx ensurepath

WORKDIR /home/embeddev/powa

COPY . .

RUN /home/embeddev/.local/bin/poetry install --no-interaction

ENTRYPOINT ["/bin/bash", "--login"]

FROM prod AS dev

RUN /home/embeddev/.local/bin/poetry install --only dev --no-interaction
