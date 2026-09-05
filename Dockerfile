FROM mwader/static-ffmpeg:8.1.2@sha256:33f770f812cbfc3de96c547157fc9faf8bd95a36481753439ffa761045167585 AS ffmpeg

FROM ghcr.io/astral-sh/uv:0.12.10-trixie-slim@sha256:260222c52f44bbf971682a1f84b333a6110ad03b41602cea2a3350e126e004ec AS base 

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ffmpeg /ffmpeg /usr/local/bin/
COPY --from=ffmpeg /ffprobe /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

FROM base AS development

RUN uv sync --frozen --no-install-project
COPY . .
RUN uv sync --frozen

FROM base AS prod_dependencies

RUN uv sync --frozen --no-dev --no-install-project

FROM node:24.20.0-alpine3.23@sha256:0388af2af070cd4736a1567cfed02469ba117848845b4165d87a333edb53d2ca AS frontend_builder
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

RUN npm run build

FROM prod_dependencies AS web_production

COPY . .
RUN uv sync --frozen --no-dev

COPY --from=frontend_builder /app/static/dist ./static/dist

RUN STATIC_URL="static/" \
    CSRF_TRUSTED_ORIGINS="http://localhost" \
    DJANGO_SETTINGS_MODULE="lulzcasz_dev.settings.production" \
    SECRET_KEY="build-dummy-key" \
    ALLOWED_HOSTS="*" \
    DATABASE_NAME="dummy" \
    CELERY_BROKER_URL="redis://localhost:6379" \
    uv run --no-dev python manage.py collectstatic --noinput

CMD ["uv", "run", "--no-dev", "gunicorn", "lulzcasz_dev.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

FROM prod_dependencies AS worker_production

COPY . .
RUN uv sync --frozen --no-dev

CMD ["uv", "run", "--no-dev", "celery", "-A", "lulzcasz_dev", "worker", "-c", "1", "--loglevel", "INFO"]
