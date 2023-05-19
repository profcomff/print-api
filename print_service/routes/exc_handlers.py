import starlette.requests
from starlette.responses import JSONResponse

from print_service.base import StatusResponseModel
from print_service.exceptions import (
    AlreadyUpload,
    FileIsNotReceived,
    FileNotFound,
    InvalidPageRequest,
    InvalidType,
    IsCorrupt,
    IsNotUpload,
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


@app.exception_handler(TooLargeSize)
async def too_large_size(req: starlette.requests.Request, exc: TooLargeSize):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=413
    )


@app.exception_handler(TooManyPages)
async def too_many_pages(req: starlette.requests.Request, exc: TooManyPages):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=413
    )


@app.exception_handler(InvalidPageRequest)
async def invalid_format(req: starlette.requests.Request, exc: TooManyPages):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=416
    )


@app.exception_handler(TerminalQRNotFound)
async def terminal_not_found(req: starlette.requests.Request, exc: TerminalQRNotFound):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"Terminal not found by QR").dict(),
        status_code=400,
    )


@app.exception_handler(TerminalTokenNotFound)
async def terminal_not_found(req: starlette.requests.Request, exc: TerminalTokenNotFound):
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
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=403
    )


@app.exception_handler(PINGenerateError)
async def generate_error(req: starlette.requests.Request, exc: PINGenerateError):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=500
    )


@app.exception_handler(FileIsNotReceived)
async def file_not_received(req: starlette.requests.Request, exc: FileIsNotReceived):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=400
    )


@app.exception_handler(PINNotFound)
async def pin_not_found(req: starlette.requests.Request, exc: PINNotFound):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"Pin {exc.pin} not found").dict(),
        status_code=404,
    )


@app.exception_handler(InvalidType)
async def invalid_type(req: starlette.requests.Request, exc: InvalidType):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=415
    )


@app.exception_handler(AlreadyUpload)
async def already_upload(req: starlette.requests.Request, exc: AlreadyUpload):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=415
    )


@app.exception_handler(IsCorrupt)
async def is_corrupt(req: starlette.requests.Request, exc: IsCorrupt):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=415
    )


@app.exception_handler(UnprocessableFileInstance)
async def unprocessable_file(req: starlette.requests.Request, exc: UnprocessableFileInstance):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=422
    )


@app.exception_handler(FileNotFound)
async def unprocessable_file(req: starlette.requests.Request, exc: FileNotFound):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc.count} file(s) not found").dict(),
        status_code=404,
    )


@app.exception_handler(IsNotUpload)
async def not_upload(req: starlette.requests.Request, exc: IsNotUpload):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=415
    )
