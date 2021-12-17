from logging import getLogger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_sqlalchemy import DBSessionMiddleware

from print_service import __version__
from print_service.api_routes import file_router, user_router
from print_service.settings import Settings, get_settings


settings: Settings = get_settings()
logger = getLogger(__name__)

app = FastAPI(
    title='Сервис отправки заданий печати',
    description=(
        'Серверная часть сервиса отправки заданий на печать и получения файлов для печати с терминала'
    ),
    version=__version__,
    root_path=settings.ROOT,
)
app.add_middleware(DBSessionMiddleware, db_url=settings.DB_DSN, engine_args=dict(pool_pre_ping=True))

origins = [
    "https://app.profcomff.com",
    "http://app.profcomff.com",
    "https://www.profcomff.com",
    "http://www.profcomff.com",
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router, prefix='', tags=['User'])
app.include_router(file_router, prefix='/file', tags=['File'])
app.mount('/static', StaticFiles(directory='static'), 'static')
