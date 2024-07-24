## Что нужно для запуска 

1. python3.11. Установка описана [тут](https://www.python.org/downloads/)

2. Docker. Как установить docker описано [тут](https://docs.docker.com/engine/install/)

3. PostgreSQL. Запустить команду
    ```bash
    docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust --name db-print_service postgres:15
    ```

4. Опционально Redis (если хотите дергать ручку `/qr` или подключаться по вебсокету)
    ```bash
    docker run -d -p 6379:6379 --name redis-print_service redis
    ```

## Какие переменные нужны для запуска
- `DB_DSN=postgresql://postgres@localhost:5432/postgres`

### Опционально, если хотите дергать ручку `/qr` или подключаться по вебсокету
- `REDIS_DSN=redis://localhost:6379/0`


## Codestyle

- Black. Как пользоваться описано [тут](https://black.readthedocs.io/en/stable/)

- Также применяем [isort](https://pycqa.github.io/isort/)

