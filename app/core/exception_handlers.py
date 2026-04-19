from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errores = []

        for error in exc.errors():
            loc = error.get("loc", [])
            campo = ".".join(str(x) for x in loc if x != "body")
            errores.append({
                "campo": campo or None,
                "mensaje": error.get("msg"),
                "valor": error.get("input")
            })

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "timestamp": datetime.now().isoformat(),
                "status": 400,
                "error": "Bad Request",
                "message": "Error de validación",
                "path": str(request.url.path),
                "details": errores
            }
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "timestamp": datetime.now().isoformat(),
                "status": exc.status_code,
                "error": "HTTP Exception",
                "message": exc.detail,
                "path": str(request.url.path),
                "details": None
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "timestamp": datetime.now().isoformat(),
                "status": 500,
                "error": "Internal Server Error",
                "message": "Ocurrió un error interno en el servidor",
                "path": str(request.url.path),
                "details": None
            }
        )