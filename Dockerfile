FROM mwader/static-ffmpeg:8.1.2@sha256:33f770f812cbfc3de96c547157fc9faf8bd95a36481753439ffa761045167585 AS ffmpeg

FROM ghcr.io/astral-sh/uv:0.11.23-trixie-slim@sha256:e08a160f54f8c272f810f30f3099162199a529151ded0edb3018f6e9c8631846 AS base 

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ffmpeg /ffmpeg /usr/local/bin/
COPY --from=ffmpeg /ffprobe /usr/local/bin/

WORKDIR /app

ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/prism.min.js /app/static/js/
ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/autoloader/prism-autoloader.min.js /app/static/js/
ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/toolbar/prism-toolbar.min.js /app/static/js/
ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/treeview/prism-treeview.min.js /app/static/js/
ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/copy-to-clipboard/prism-copy-to-clipboard.min.js /app/static/js/

ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/toolbar/prism-toolbar.min.css /app/static/css/
ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/treeview/prism-treeview.min.css /app/static/css/
ADD https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7.2.0/css/all.min.css /app/static/css/

ADD https://cdn.jsdelivr.net/npm/prism-themes@1.9.0/themes/prism-coldark-dark.min.css /app/static/css/

ADD https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7.2.0/webfonts/fa-solid-900.woff2 /app/static/webfonts/
ADD https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7.2.0/webfonts/fa-regular-400.woff2 /app/static/webfonts/
ADD https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7.2.0/webfonts/fa-brands-400.woff2 /app/static/webfonts/

COPY pyproject.toml uv.lock ./

FROM base AS development

RUN uv sync --frozen --no-install-project
COPY . .
RUN uv sync --frozen

FROM base AS prod_dependencies

RUN uv sync --frozen --no-dev --no-install-project

FROM node:24.17.0-alpine3.23 AS frontend_builder
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

RUN npm run build

FROM prod_dependencies AS web_production

COPY . .
RUN uv sync --frozen --no-dev

COPY --from=frontend_builder /app/static/css ./static/css

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
