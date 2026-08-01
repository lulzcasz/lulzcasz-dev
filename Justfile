export UV_ENV_FILE := ".env"

compose := "docker compose"
manage := "uv run manage.py"

up:
	@{{compose}} up -w

down:
	@{{compose}} down --rmi local

manage *args:
	@{{manage}} {{args}}
	
migrate *args:
	@{{manage}} migrate {{args}}

createsuperuser *args:
	@{{manage}} createsuperuser {{args}}
