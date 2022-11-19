FROM python:3.10
WORKDIR /app
RUN mkdir -p static/cache && mkdir -p static/photo/lecturer

COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

ADD gunicorn_conf.py alembic.ini /app/
ADD migrations /app/migrations
ADD print_service /app/print_service

VOLUME ["/app/static"]

CMD [ "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/app/gunicorn_conf.py", "print_service.fastapi:app" ]
