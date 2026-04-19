from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.categoria import Categoria
from app.models.usuario import Usuario
from app.schemas.categoria_schema import (
    CategoriaCreate,
    CategoriaResponse,
    CategoriaUpdate
)
from app.schemas.error_schema import ErrorResponse

router = APIRouter(
    prefix="/api/categoria",
    tags=["Categorías"]
)


@router.post(
    "",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear categoría",
    description="""
Crea una nueva categoría de medicamentos.

### Reglas:
- El nombre de la categoría no debe repetirse.
- Requiere autenticación JWT.
""",
    response_description="Categoría creada correctamente.",
    responses={
        201: {"description": "Categoría creada correctamente"},
        400: {
            "model": ErrorResponse,
            "description": "Datos inválidos o categoría duplicada"
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
def guardar_categoria(
    categoria: CategoriaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    existente = db.query(Categoria).filter(Categoria.nombre == categoria.nombre).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La categoría ya existe"
        )

    nueva_categoria = Categoria(nombre=categoria.nombre)
    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)

    return nueva_categoria


@router.get(
    "/{id}",
    response_model=CategoriaResponse,
    summary="Obtener categoría por ID",
    description="Retorna una categoría específica según su identificador.",
    response_description="Categoría encontrada correctamente.",
    responses={
        200: {"description": "Categoría encontrada"},
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Categoría no encontrada"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def obtener_categoria_por_id(
    id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    categoria = db.query(Categoria).filter(Categoria.id == id).first()

    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    return categoria


@router.get(
    "",
    response_model=list[CategoriaResponse],
    summary="Listar categorías",
    description="Obtiene el listado completo de categorías registradas.",
    response_description="Listado de categorías obtenido correctamente.",
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
def listar_categorias(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    return db.query(Categoria).all()


@router.put(
    "/{id}",
    response_model=CategoriaResponse,
    summary="Actualizar categoría",
    description="""
Actualiza el nombre de una categoría existente.

### Reglas:
- La categoría debe existir.
- No puede existir otra categoría con el mismo nombre.
- Requiere autenticación JWT.
""",
    response_description="Categoría actualizada correctamente.",
    responses={
        200: {"description": "Categoría actualizada correctamente"},
        400: {
            "model": ErrorResponse,
            "description": "Nombre duplicado o datos inválidos"
        },
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Categoría no encontrada"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def actualizar_categoria(
    id: int,
    datos: CategoriaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    categoria = db.query(Categoria).filter(Categoria.id == id).first()

    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    repetida = db.query(Categoria).filter(
        Categoria.nombre == datos.nombre,
        Categoria.id != id
    ).first()

    if repetida:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe otra categoría con ese nombre"
        )

    categoria.nombre = datos.nombre
    db.commit()
    db.refresh(categoria)

    return categoria


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar categoría",
    description="Elimina una categoría existente por su ID.",
    responses={
        204: {"description": "Categoría eliminada correctamente"},
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Categoría no encontrada"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def eliminar_categoria(
    id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    categoria = db.query(Categoria).filter(Categoria.id == id).first()

    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    db.delete(categoria)
    db.commit()