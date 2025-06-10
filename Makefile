app_name = vmeste

celery_services = rabbit celery
loc_services := db backend $(celery_services) elasticsearch redis
docker_compose := docker compose -f docker-compose.yml

build:
	$(docker_compose) build $(c)

rebuild:
	$(docker_compose) up -d --build --force-recreate $(loc_services)
	docker image prune -f

up:
	$(docker_compose) up -d $(loc_services)

start:
	$(docker_compose) start $(c)

down:
	$(docker_compose) down $(c)

destroy:
	$(docker_compose) down --rmi all -v $(c)

stop:
	$(docker_compose) stop $(c)

restart:
	$(docker_compose) restart $(loc_services)

restart-celery:
	$(docker_compose) restart $(celery_services)

reup:
	$(docker_compose) down $(c)
	$(docker_compose) up -d $(loc_services)

logs:
	$(docker_compose) logs --tail=1000 -f $(c)

app-logs:
	$(docker_compose) logs --tail=1000 -f backend $(c)

celery-logs:
	$(docker_compose) logs --tail=1000 -f celery $(c)

app-bash:
	docker exec -it $(app_name)_backend /bin/sh $(c)

db-bash:
	docker exec -it $(app_name)_db bash $(c)

migrations:
	docker exec -it $(app_name)_backend python manage.py makemigrations

migrate:
	docker exec -it $(app_name)_backend python manage.py migrate

es-rebuild:
	docker exec -it $(app_name)_backend python manage.py search_index --rebuild -f

psql:
	docker exec -it $(app_name)_db psql -U postgres
