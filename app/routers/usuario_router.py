from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import obtener_password_hash
from app.dependencies.auth import get_current_user
from app.models.usuario import Usuario
from app.schemas.error_schema import ErrorResponse
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse


router = APIRouter(
    prefix="/api/usuario",
    tags=["Usuarios"]
)


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="""
Crea un nuevo usuario en el sistema.

### Reglas:
- El correo debe ser único.
- El username debe ser único.
- La contraseña debe contener mayúscula, minúscula y número.
- Requiere autenticación JWT.
""",
    response_description="Usuario creado correctamente.",
    responses={
        201: {"description": "Usuario creado correctamente"},
        400: {
            "model": ErrorResponse,
            "description": "Datos inválidos o usuario duplicado"
        },
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def guardar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    existe_correo = db.query(Usuario).filter(Usuario.correo == usuario.correo).first()
    if existe_correo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )

    existe_username = db.query(Usuario).filter(Usuario.username == usuario.username).first()
    if existe_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username ya está registrado"
        )

    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        direccion=usuario.direccion,
        username=usuario.username,
        password=obtener_password_hash(usuario.password)
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


@router.get(
    "/{id}",
    response_model=UsuarioResponse,
    summary="Obtener usuario por ID",
    description="Retorna la información de un usuario específico según su identificador.",
    response_description="Usuario encontrado correctamente.",
    responses={
        200: {"description": "Usuario encontrado"},
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Usuario no encontrado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def obtener_usuario_por_id(
    id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return usuario


@router.get(
    "",
    response_model=list[UsuarioResponse],
    summary="Listar usuarios",
    description="Obtiene el listado completo de usuarios registrados en el sistema.",
    response_description="Listado de usuarios obtenido correctamente.",
    responses={
        200: {"description": "Listado obtenido correctamente"},
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def listar_usuarios(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    return db.query(Usuario).all()


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario existente por su ID.",
    responses={
        204: {"description": "Usuario eliminado correctamente"},
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Usuario no encontrado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def eliminar_usuario(
    id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    db.delete(usuario)
    db.commit()