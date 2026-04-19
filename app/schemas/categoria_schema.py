from pydantic import BaseModel, ConfigDict, Field


class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, examples=["Analgésicos"])


class CategoriaCreate(CategoriaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Analgésicos"
            }
        }
    )


class CategoriaUpdate(CategoriaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Antibióticos"
            }
        }
    )


class CategoriaResponse(CategoriaBase):
    id: int = Field(..., examples=[1])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Analgésicos"
            }
        }
    )