FROM mwader/static-ffmpeg:8.1.1@sha256:735f84b905e00d5c618b667f0b053f83b1096f5fc404c607e6134bf2275a0e0a AS ffmpeg

FROM ghcr.io/astral-sh/uv:0.11.11-debian@sha256:844e7975a1d54305c09ffcffabedab251807ef1473ef92e9538d016a15c6fdcd AS base 

COPY --from=ffmpeg /ffmpeg /usr/local/bin/
COPY --from=ffmpeg /ffprobe /usr/local/bin/

WORKDIR /app

ADD https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css /app/static/css/bootstrap.min.css
ADD https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js /app/static/js/bootstrap.bundle.min.js

ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/prism.min.js /app/static/js/prism.min.js
ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/autoloader/prism-autoloader.min.js /app/static/js/prism-autoloader.min.js
ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/toolbar/prism-toolbar.min.js /app/static/js/prism-toolbar.min.js
ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/toolbar/prism-toolbar.min.css /app/static/css/prism-toolbar.min.css
ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/treeview/prism-treeview.min.css /app/static/css/prism-treeview.min.css
ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/treeview/prism-treeview.min.js /app/static/js/prism-treeview.min.js
ADD https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/copy-to-clipboard/prism-copy-to-clipboard.min.js /app/static/js/prism-copy-to-clipboard.min.js

ADD https://cdn.jsdelivr.net/npm/prism-themes@1.9.0/themes/prism-coy-without-shadows.min.css /app/static/css/prism-coy-without-shadows.min.css

ADD https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7.2.0/css/all.min.css /app/static/css/all.min.css
ADD https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7.2.0/webfonts/fa-solid-900.woff2 /app/static/webfonts/fa-solid-900.woff2
ADD https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7.2.0/webfonts/fa-regular-400.woff2 /app/static/webfonts/fa-regular-400.woff2
ADD https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7.2.0/webfonts/fa-brands-400.woff2 /app/static/webfonts/fa-brands-400.woff2

COPY pyproject.toml uv.lock ./

FROM base AS development

RUN uv sync --frozen --no-install-project

COPY . .

RUN uv sync --frozen

FROM base AS prod_dependencies

RUN uv sync --frozen --no-dev --no-install-project

FROM prod_dependencies AS web_production

COPY . .

RUN uv sync --frozen --no-dev

RUN STATIC_URL="static/" CSRF_TRUSTED_ORIGINS="*" DJANGO_SETTINGS_MODULE="lulzcasz_dev.settings.production" SECRET_KEY="build-dummy-key" ALLOWED_HOSTS="*" DATABASE_URL="sqlite:///" uv run --no-dev python manage.py collectstatic --noinput

CMD ["uv", "run", "--no-dev", "gunicorn", "lulzcasz_dev.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "5"]

FROM prod_dependencies AS worker_production

COPY . .

RUN uv sync --frozen --no-dev

CMD ["uv", "run", "--no-dev", "celery", "-A", "lulzcasz_dev", "worker", "-c", "2", "--loglevel", "INFO"]
