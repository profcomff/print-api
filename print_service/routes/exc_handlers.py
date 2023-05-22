import starlette.requests
from starlette.responses import JSONResponse

from print_service.base import StatusResponseModel
from print_service.exceptions import (
    AlreadyUploaded,
    FileIsNotReceived,
    FileNotFound,
    InvalidPageRequest,
    InvalidType,
    IsCorrupted,
    IsNotUploaded,
    NotInUnion,
    PINGenerateError,
    PINNotFound,
    TerminalQRNotFound,
    TerminalTokenNotFound,
    TooLargeSize,
    TooManyPages,
    UnionStudentDuplicate,
    UnprocessableFileInstance,
    UserNotFound,
)
from print_service.routes.base import app
from print_service.settings import get_settings


settings = get_settings()


@app.exception_handler(TooLargeSize)
async def too_large_size(req: starlette.requests.Request, exc: TooLargeSize):
    payload = StatusResponseModel(status="Error", message=f"{exc}").dict()
    payload['ru'] = f'Размер файла превышает максимально допустимый: {settings.MAX_SIZE}'
    return JSONResponse(content=payload, status_code=413)


@app.exception_handler(TooManyPages)
async def too_many_pages(req: starlette.requests.Request, exc: TooManyPages):
    payload = StatusResponseModel(status="Error", message=f"{exc}").dict()
    payload[
        'ru'
    ] = f'Количество запрошенных страниц превышает допустимое число: {settings.MAX_PAGE_COUNT}'
    return JSONResponse(content=payload, status_code=413)


@app.exception_handler(InvalidPageRequest)
async def invalid_format(req: starlette.requests.Request, exc: TooManyPages):
    payload = StatusResponseModel(status="Error", message=f"{exc}").dict()
    payload['ru'] = 'Количество запрошенных страниц превышает их количество в файле'
    return JSONResponse(content=payload, status_code=416)


@app.exception_handler(TerminalQRNotFound)
async def terminal_not_found_by_qr(req: starlette.requests.Request, exc: TerminalQRNotFound):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"Terminal not found by QR").dict(),
        status_code=400,
    )


@app.exception_handler(TerminalTokenNotFound)
async def terminal_not_found_by_token(req: starlette.requests.Request, exc: TerminalTokenNotFound):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"Terminal not found by token").dict(),
        status_code=400,
    )


@app.exception_handler(UserNotFound)
async def user_not_found(req: starlette.requests.Request, exc: UserNotFound):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"User not found").dict(), status_code=404
    )


@app.exception_handler(UnionStudentDuplicate)
async def student_duplicate(req: starlette.requests.Request, exc: UnionStudentDuplicate):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=400
    )


@app.exception_handler(NotInUnion)
async def not_in_union(req: starlette.requests.Request, exc: NotInUnion):
    payload = StatusResponseModel(status="Error", message=f"{exc}").dict()
    payload['ru'] = 'Отсутствует членство в профсоюзе'
    return JSONResponse(content=payload, status_code=403)


@app.exception_handler(PINGenerateError)
async def generate_error(req: starlette.requests.Request, exc: PINGenerateError):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=500
    )


@app.exception_handler(FileIsNotReceived)
async def file_not_received(req: starlette.requests.Request, exc: FileIsNotReceived):
    payload = StatusResponseModel(status="Error", message=f"{exc}").dict()
    payload['ru'] = 'Файл не получен'
    return JSONResponse(
        content=payload,
        status_code=400,
    )


@app.exception_handler(PINNotFound)
async def pin_not_found(req: starlette.requests.Request, exc: PINNotFound):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"Pin {exc.pin} not found").dict(),
        status_code=404,
    )


@app.exception_handler(InvalidType)
async def invalid_type(req: starlette.requests.Request, exc: InvalidType):
    payload = StatusResponseModel(status="Error", message=f"{exc}").dict()
    payload['ru'] = f'Неподдерживаемый формат файла. Допустимые: {settings.CONTENT_TYPES}'
    return JSONResponse(content=payload, status_code=415)


@app.exception_handler(AlreadyUploaded)
async def already_upload(req: starlette.requests.Request, exc: AlreadyUploaded):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=415
    )


@app.exception_handler(IsCorrupted)
async def is_corrupted(req: starlette.requests.Request, exc: IsCorrupted):
    payload = StatusResponseModel(status="Error", message=f"{exc}").dict()
    payload['ru'] = 'Файл повреждён'
    return JSONResponse(content=payload, status_code=415)


@app.exception_handler(UnprocessableFileInstance)
async def unprocessable_file_instance(req: starlette.requests.Request, exc: UnprocessableFileInstance):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=422
    )


@app.exception_handler(FileNotFound)
async def file_not_found(req: starlette.requests.Request, exc: FileNotFound):
    payload = StatusResponseModel(status="Error", message=f"{exc.count} file(s) not found").dict()
    payload['ru'] = 'Файл не найден'
    return JSONResponse(
        content=payload,
        status_code=404,
    )


@app.exception_handler(IsNotUploaded)
async def not_uploaded(req: starlette.requests.Request, exc: IsNotUploaded):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=415
    )
