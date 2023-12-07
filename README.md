# Сервис печати
Серверная часть сервиса для работы с документами, отправляемыми на печать

## Функционал 
1. Управление файлами, отправляемыми пользователями на печать
    - Создание/удаление файлов
    - Редактирование параметров печати

2. Получение файлов со стороны клиента-терминала печати 

3. Управление пользователями, которым разрешена печать на принтере

4. Прямое подключение клиентом-терминалом печати 
    - Генерация QR кодов для быстрой печати
    - Отправка команд на мгновенное обновление/перезагрузку терминала 


## Запуск

1. Перейдите в папку проекта

2. Создайте виртуальное окружение командой и активируйте его:
    ```console
    foo@bar:~$ python3 -m venv venv
    foo@bar:~$ source ./venv/bin/activate  # На MacOS и Linux
    foo@bar:~$ venv\Scripts\activate  # На Windows
    ```

3. Установите библиотеки
    ```console
    (venv) foo@bar:~$ pip install -r requirements.txt
    (venv) foo@bar:~$ pip install -r requirements.dev.txt
    ```

4. Поднимите базу данных
    ```console
    (venv) foo@bar:~$ docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust --name db-print_service postgres:15
    (venv) foo@bar:~$ alembic upgrade head  # Произвести миграции БД
    ```

5. Запускайте приложение!
    ```console
    (venv) foo@bar:~$ python -m print_service
    ```


## ENV-variables description

- `DB_DSN=postgresql://postgres@localhost:5432/postgres` – Данные для подключения к БД
- `STATIC_PATH` - путь до папки, в которой лежит статика.
