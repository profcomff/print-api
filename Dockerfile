FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim
ENV APP_NAME=print_service
ENV APP_MODULE=${APP_NAME}.fastapi:app

COPY ./requirements.txt /app/
RUN pip install -r /app/requirements.txt  && mkdir /app/static

COPY ./alembic.ini /app/alembic.ini
COPY ./migrations /app/migrations
COPY ./${APP_NAME} /app/${APP_NAME}
