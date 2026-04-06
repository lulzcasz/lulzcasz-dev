export UV_ENV_FILE := ".env"

compose := "docker compose"
manage := "uv run manage.py"
garage := "docker compose exec storage /garage"

bucket_name := "lulzcasz-dev"
key_name := "test-key"
domain_alias := "media.localhost"

access_key := "GK06482d2e182023a5782e72e6"
secret_key := "da5f822da7f6919ab3113b3e8dd53e1333a9895beb7599b7393dc05e47fcb826"

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

s3-init:
    @NODE_ID=$({{garage}} node id | grep -oE '[a-f0-9]{64}' | head -n 1); \
    {{garage}} layout assign -z dc1 -c 10G ${NODE_ID}; \
    {{garage}} layout apply --version 1

s3-setup:
    @{{garage}} bucket create {{bucket_name}}
    
    @{{garage}} key import -n {{key_name}} --yes {{access_key}} {{secret_key}}
    
    @{{garage}} bucket allow --read --write --owner {{bucket_name}} --key {{key_name}}
    @{{garage}} bucket alias {{bucket_name}} {{domain_alias}}
    @{{garage}} bucket website --allow {{bucket_name}}
