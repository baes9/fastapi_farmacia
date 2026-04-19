from pydantic import BaseModel, Field, ConfigDict


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, examples=["admin"])
    password: str = Field(..., min_length=1, examples=["Admin123"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin",
                "password": "Admin123"
            }
        }
    )


class TokenResponse(BaseModel):
    token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIs..."])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIs..."
            }
        }
    )