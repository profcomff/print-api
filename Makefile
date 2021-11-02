prod-up:
	docker-compose up --detach --remove-orphans --force-recreate --build
	docker-compose run --rm api bash -c 'alembic upgrade head'

prod-down:
	docker-compose down
