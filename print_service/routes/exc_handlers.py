import starlette.requests
from starlette.responses import JSONResponse

from print_service.base import StatusResponseModel
from print_service.exceptions import (
    AlreadyUpload,
    FileIsNotReceived,
    InvalidPageRequest,
    InvalidType,
    IsCorrupt,
    NotInUnion,
    PINGenerateError,
    PINNotFound,
    TerminalNotFound,
    TooLargeSize,
    TooManyPages,
    UnionStudentDuplicate,
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


@app.exception_handler(TerminalNotFound)
async def invalid_format(req: starlette.requests.Request, exc: TerminalNotFound):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=400
    )


@app.exception_handler(UserNotFound)
async def invalid_format(req: starlette.requests.Request, exc: UserNotFound):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=404
    )


@app.exception_handler(UnionStudentDuplicate)
async def invalid_format(req: starlette.requests.Request, exc: UnionStudentDuplicate):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=400
    )


@app.exception_handler(NotInUnion)
async def invalid_format(req: starlette.requests.Request, exc: NotInUnion):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=403
    )


@app.exception_handler(PINGenerateError)
async def invalid_format(req: starlette.requests.Request, exc: PINGenerateError):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=500
    )


@app.exception_handler(FileIsNotReceived)
async def invalid_format(req: starlette.requests.Request, exc: FileIsNotReceived):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=400
    )


@app.exception_handler(PINNotFound)
async def invalid_format(req: starlette.requests.Request, exc: PINNotFound):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=404
    )


@app.exception_handler(InvalidType)
async def invalid_format(req: starlette.requests.Request, exc: InvalidType):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=415
    )


@app.exception_handler(AlreadyUpload)
async def invalid_format(req: starlette.requests.Request, exc: AlreadyUpload):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=415
    )


@app.exception_handler(IsCorrupt)
async def invalid_format(req: starlette.requests.Request, exc: IsCorrupt):
    return JSONResponse(
        content=StatusResponseModel(status="Error", message=f"{exc}").dict(), status_code=415
    )
