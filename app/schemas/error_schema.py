from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    campo: str | None = Field(default=None, examples=["correo"])
    mensaje: str = Field(..., examples=["value is not a valid email address"])
    valor: Any | None = Field(default=None, examples=["correo-malo"])


class ErrorResponse(BaseModel):
    timestamp: datetime
    status: int = Field(..., examples=[400])
    error: str = Field(..., examples=["Bad Request"])
    message: str = Field(..., examples=["Error de validación"])
    path: str = Field(..., examples=["/api/usuario"])
    details: list[ErrorDetail] | None = None