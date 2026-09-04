export UV_ENV_FILE := ".env"

compose := "docker compose"
manage := "uv run manage.py"

up:
	@{{compose}} up -d

down:
	@{{compose}} down --rmi local

manage *args:
	@{{manage}} {{args}}
	
migrate *args:
	@{{manage}} migrate {{args}}

createsuperuser *args:
	@{{manage}} createsuperuser {{args}}

celery:
	uv run celery -A lulzcasz_dev worker --loglevel=INFO --concurrency=2
