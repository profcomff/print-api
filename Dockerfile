FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}
ENV APP_NAME=print_service
ENV APP_MODULE=${APP_NAME}.routes.base:app

COPY ./requirements.txt /app/
RUN apt-get update && apt-get -y install cron && pip install -U -r /app/requirements.txt

COPY ./static /app/static/

COPY ./alembic.ini /alembic.ini
COPY ./logging_prod.conf /app/
COPY ./logging_test.conf /app/
COPY ./migrations /migrations/

COPY ./${APP_NAME} /app/${APP_NAME}

COPY ./prestart.sh /app/prestart.sh
RUN (crontab -l 2>/dev/null; echo \
    "* * * * *  find /app/static -type f -name $(date -d '-7' days --iso)'*' -print -delete>> /var/log/cron.log 2>&1"\
    ) | crontab -
