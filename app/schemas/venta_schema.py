from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class VentaLineaRequest(BaseModel):
    medicamento_id: int = Field(..., gt=0, examples=[1])
    cantidad: int = Field(..., ge=1, examples=[2])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "medicamento_id": 1,
                "cantidad": 2
            }
        }
    )


class VentaCreate(BaseModel):
    cliente_id: int | None = Field(default=None, gt=0, examples=[1])
    cliente_documento: str | None = Field(default=None, min_length=1, max_length=20, examples=["0102030405"])
    items: list[VentaLineaRequest] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validar_cliente(self):
        if self.cliente_id is None and not self.cliente_documento:
            raise ValueError("Debe indicar cliente_id o cliente_documento")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "cliente_id": 1,
                    "items": [
                        {
                            "medicamento_id": 1,
                            "cantidad": 2
                        }
                    ]
                },
                {
                    "cliente_documento": "0102030405",
                    "items": [
                        {
                            "medicamento_id": 1,
                            "cantidad": 1
                        },
                        {
                            "medicamento_id": 2,
                            "cantidad": 3
                        }
                    ]
                }
            ]
        }
    )


class DetalleVentaResponse(BaseModel):
    id: int = Field(..., examples=[1])
    medicamento_id: int = Field(..., examples=[1])
    nombre_medicamento: str = Field(..., examples=["Amoxicilina 500mg"])
    cantidad: int = Field(..., examples=[2])
    precio_unitario: Decimal = Field(..., examples=[4.75])
    subtotal: Decimal = Field(..., examples=[9.50])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "medicamento_id": 1,
                "nombre_medicamento": "Amoxicilina 500mg",
                "cantidad": 2,
                "precio_unitario": 4.75,
                "subtotal": 9.50
            }
        }
    )


class VentaResponse(BaseModel):
    id: int = Field(..., examples=[1])
    fecha: datetime = Field(..., examples=["2026-04-19T10:30:00"])
    cliente_id: int = Field(..., examples=[1])
    cliente_documento: str = Field(..., examples=["0102030405"])
    cliente_nombre: str = Field(..., examples=["María López"])
    vendedor_username: str | None = Field(default=None, examples=["admin"])
    total: Decimal = Field(..., examples=[9.50])
    detalles: list[DetalleVentaResponse]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "fecha": "2026-04-19T10:30:00",
                "cliente_id": 1,
                "cliente_documento": "0102030405",
                "cliente_nombre": "María López",
                "vendedor_username": "admin",
                "total": 9.50,
                "detalles": [
                    {
                        "id": 1,
                        "medicamento_id": 1,
                        "nombre_medicamento": "Amoxicilina 500mg",
                        "cantidad": 2,
                        "precio_unitario": 4.75,
                        "subtotal": 9.50
                    }
                ]
            }
        }
    )