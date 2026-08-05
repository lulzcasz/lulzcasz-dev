FROM mwader/static-ffmpeg:8.1.2@sha256:33f770f812cbfc3de96c547157fc9faf8bd95a36481753439ffa761045167585 AS ffmpeg

FROM ghcr.io/astral-sh/uv:0.12.2-trixie-slim@sha256:829cfaa2f7e8dc7d92911ecc804ea2e2f7492980eea8140ea93d9fad3b51ded3 AS base 

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

FROM node:24.19.0-alpine3.23@sha256:244cc2b53f46f9e876304391d17682b0ddae9ac33491f4857e25e35a36ba7995 AS frontend_builder
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
    DATABASE_URL="sqlite:///" \
    uv run --no-dev python manage.py collectstatic --noinput

CMD ["uv", "run", "--no-dev", "gunicorn", "lulzcasz_dev.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

FROM prod_dependencies AS worker_production

COPY . .
RUN uv sync --frozen --no-dev

CMD ["uv", "run", "--no-dev", "celery", "-A", "lulzcasz_dev", "worker", "-c", "1", "--loglevel", "INFO"]
