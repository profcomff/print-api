import uvicorn


if __name__ == '__main__':
    uvicorn.run("print_service.routes.base:app", reload=True)
