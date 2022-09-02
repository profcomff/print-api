run:
	source ./venv/bin/activate && uvicorn --reload --log-level debug print_service.fastapi:app

migrate:
	source ./venv/bin/activate && alembic upgrade head

prod-up:
	docker-compose up --detach --remove-orphans --force-recreate --build
	docker-compose run --rm api bash -c 'alembic upgrade head'

prod-down:
	docker-compose down
