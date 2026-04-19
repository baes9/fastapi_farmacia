from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClienteBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120, examples=["María López"])
    documento: str = Field(..., min_length=5, max_length=20, examples=["0102030405"])
    telefono: str | None = Field(default=None, max_length=20, examples=["0991234567"])
    correo: EmailStr | None = Field(default=None, examples=["maria@email.com"])


class ClienteCreate(ClienteBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "María López",
                "documento": "0102030405",
                "telefono": "0991234567",
                "correo": "maria@email.com"
            }
        }
    )


class ClienteUpdate(ClienteBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Pedro Ruiz",
                "documento": "1102233445",
                "telefono": "0987654321",
                "correo": "pedro@email.com"
            }
        }
    )


class ClienteResponse(ClienteBase):
    id: int = Field(..., examples=[1])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "María López",
                "documento": "0102030405",
                "telefono": "0991234567",
                "correo": "maria@email.com"
            }
        }
    )