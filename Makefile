run:
	source ./venv/bin/activate && uvicorn --reload --log-config logging_dev.conf print_service.routes:app

configure: venv
	source ./venv/bin/activate && pip install -r requirements.dev.txt -r requirements.txt

venv:
	python3.11 -m venv venv

format:
	autoflake -r --in-place --remove-all-unused-imports ./print_service
	isort ./print_service
	black ./print_service

db:
	docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust --name db-print_service postgres:15
	sleep 3

redis:
	docker run -d -p 6379:6379 --name redis-print_service redis
	sleep 3

migrate:
	alembic upgrade head
