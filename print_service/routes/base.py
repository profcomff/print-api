from logging import getLogger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_sqlalchemy import DBSessionMiddleware

from print_service import __version__
from print_service.routes.file import router as file_router
from print_service.routes.user import router as user_router
from print_service.routes.qrprint import router as qrprint_router
from print_service.routes.admin import router as admin_router
from print_service.settings import Settings, get_settings


settings: Settings = get_settings()
logger = getLogger(__name__)

app = FastAPI(
    title='Сервис отправки заданий печати',
    description=(
        'Серверная часть сервиса отправки заданий на печать и получения файлов для печати с терминала'
    ),
    version=__version__,
)
app.add_middleware(DBSessionMiddleware, db_url=settings.DB_DSN, engine_args=dict(pool_pre_ping=True))

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


app.include_router(user_router, prefix='', tags=['User'])
app.include_router(file_router, prefix='/file', tags=['File'])
app.include_router(qrprint_router, prefix='/qr', tags=['File'])
app.include_router(admin_router, prefix='/admin', tags=['Admin'])
app.mount('/static', StaticFiles(directory='static'), 'static')
