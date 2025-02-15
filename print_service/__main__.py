import uvicorn

from print_service.routes.base import app


if __name__ == '__main__':
    uvicorn.run(app)
