from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoriaSimpleResponse(BaseModel):
    id: int = Field(..., examples=[1])
    nombre: str = Field(..., examples=["Antibióticos"])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Antibióticos"
            }
        }
    )


class MedicamentoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120, examples=["Amoxicilina 500mg"])
    descripcion: str = Field(..., min_length=3, max_length=255, examples=["Antibiótico de amplio espectro"])
    precio: Decimal = Field(..., gt=0, examples=[4.75])
    stock: int = Field(..., ge=0, examples=[50])
    categoria_id: int = Field(..., gt=0, examples=[1])


class MedicamentoCreate(MedicamentoBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Amoxicilina 500mg",
                "descripcion": "Antibiótico de amplio espectro",
                "precio": 4.75,
                "stock": 50,
                "categoria_id": 1
            }
        }
    )


class MedicamentoUpdate(MedicamentoBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Ibuprofeno 400mg",
                "descripcion": "Antiinflamatorio y analgésico",
                "precio": 3.20,
                "stock": 100,
                "categoria_id": 1
            }
        }
    )


class MedicamentoResponse(BaseModel):
    id: int = Field(..., examples=[1])
    nombre: str = Field(..., examples=["Amoxicilina 500mg"])
    descripcion: str = Field(..., examples=["Antibiótico de amplio espectro"])
    precio: Decimal = Field(..., examples=[4.75])
    stock: int = Field(..., examples=[50])
    categoria: CategoriaSimpleResponse

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Amoxicilina 500mg",
                "descripcion": "Antibiótico de amplio espectro",
                "precio": 4.75,
                "stock": 50,
                "categoria": {
                    "id": 1,
                    "nombre": "Antibióticos"
                }
            }
        }
    )