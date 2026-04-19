import re
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, examples=["Juan Pérez"])
    correo: EmailStr = Field(..., examples=["juan@email.com"])
    direccion: str = Field(..., min_length=5, max_length=150, examples=["Cuenca"])
    username: str = Field(
        ...,
        min_length=4,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
        examples=["juanp"]
    )


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8, max_length=100, examples=["Juanp123"])

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not re.search(r"[a-z]", value):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        if not re.search(r"\d", value):
            raise ValueError("La contraseña debe tener al menos un número")
        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Juan Pérez",
                "correo": "juan@email.com",
                "direccion": "Cuenca",
                "username": "juanp",
                "password": "Juanp123"
            }
        }
    )


class UsuarioResponse(UsuarioBase):
    id: int = Field(..., examples=[1])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Juan Pérez",
                "correo": "juan@email.com",
                "direccion": "Cuenca",
                "username": "juanp"
            }
        }
    )