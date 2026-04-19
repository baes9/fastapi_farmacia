from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.schemas.error_schema import ErrorResponse
from app.core.security import crear_token_access, verificar_password


router = APIRouter(
    prefix="/api/login",
    tags=["Autenticación"]
)


@router.post(
    "",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="""
Valida las credenciales del usuario y retorna un token JWT.

### Flujo:
1. Se valida username y password.
2. Si las credenciales son correctas, se genera un token JWT.
3. El token se usa luego en endpoints protegidos.
""",
    response_description="Token JWT generado correctamente.",
    responses={
        200: {
            "description": "Autenticación exitosa"
        },
        400: {
            "model": ErrorResponse,
            "description": "Error de validación en la solicitud"
        },
        401: {
            "model": ErrorResponse,
            "description": "Credenciales inválidas"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.username == request.username).first()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    if not verificar_password(request.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    token = crear_token_access({"sub": usuario.username})
    return {"token": token}