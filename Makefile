run:
	source ./venv/bin/activate && uvicorn --reload --log-level debug print_service.fastapi:app

db:
	docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust --name db-print_service postgres:15
	sleep 3

redis:
	docker run -d -p 6379:6379 --name redis-print_service redis
	sleep 3

migrate:
	alembic upgrade head
