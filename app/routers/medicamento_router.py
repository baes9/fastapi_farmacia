from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.categoria import Categoria
from app.models.medicamento import Medicamento
from app.models.usuario import Usuario
from app.schemas.error_schema import ErrorResponse
from app.schemas.medicamento_schema import (
    MedicamentoCreate,
    MedicamentoResponse,
    MedicamentoUpdate
)

router = APIRouter(
    prefix="/api/medicamento",
    tags=["Medicamentos"]
)


@router.post(
    "",
    response_model=MedicamentoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear medicamento",
    description="""
Crea un nuevo medicamento y lo asocia a una categoría existente.

### Reglas:
- La categoría indicada debe existir.
- El precio debe ser mayor que cero.
- El stock no puede ser negativo.
- Requiere autenticación JWT.
""",
    response_description="Medicamento creado correctamente.",
    responses={
        201: {"description": "Medicamento creado correctamente"},
        400: {
            "model": ErrorResponse,
            "description": "Datos inválidos o categoría inexistente"
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
def guardar_medicamento(
    medicamento: MedicamentoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    categoria = db.query(Categoria).filter(Categoria.id == medicamento.categoria_id).first()
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La categoría no existe"
        )

    nuevo_medicamento = Medicamento(
        nombre=medicamento.nombre,
        descripcion=medicamento.descripcion,
        precio=medicamento.precio,
        stock=medicamento.stock,
        categoria_id=medicamento.categoria_id
    )

    db.add(nuevo_medicamento)
    db.commit()
    db.refresh(nuevo_medicamento)

    medicamento_guardado = (
        db.query(Medicamento)
        .options(joinedload(Medicamento.categoria))
        .filter(Medicamento.id == nuevo_medicamento.id)
        .first()
    )

    return medicamento_guardado


@router.get(
    "",
    response_model=list[MedicamentoResponse],
    summary="Listar medicamentos",
    description="Obtiene el listado completo de medicamentos con su categoría asociada.",
    response_description="Listado de medicamentos obtenido correctamente.",
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
def listar_medicamentos(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    return db.query(Medicamento).options(joinedload(Medicamento.categoria)).all()


@router.get(
    "/{id}",
    response_model=MedicamentoResponse,
    summary="Obtener medicamento por ID",
    description="Retorna un medicamento específico junto con su categoría.",
    response_description="Medicamento encontrado correctamente.",
    responses={
        200: {"description": "Medicamento encontrado"},
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Medicamento no encontrado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def obtener_medicamento_por_id(
    id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    medicamento = (
        db.query(Medicamento)
        .options(joinedload(Medicamento.categoria))
        .filter(Medicamento.id == id)
        .first()
    )

    if medicamento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicamento no encontrado"
        )

    return medicamento


@router.put(
    "/{id}",
    response_model=MedicamentoResponse,
    summary="Actualizar medicamento",
    description="""
Actualiza la información de un medicamento existente.

### Reglas:
- El medicamento debe existir.
- La categoría indicada debe existir.
- El precio debe ser mayor que cero.
- El stock no puede ser negativo.
- Requiere autenticación JWT.
""",
    response_description="Medicamento actualizado correctamente.",
    responses={
        200: {"description": "Medicamento actualizado correctamente"},
        400: {
            "model": ErrorResponse,
            "description": "Datos inválidos o categoría inexistente"
        },
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Medicamento no encontrado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def actualizar_medicamento(
    id: int,
    datos: MedicamentoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    medicamento = db.query(Medicamento).filter(Medicamento.id == id).first()

    if medicamento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicamento no encontrado"
        )

    categoria = db.query(Categoria).filter(Categoria.id == datos.categoria_id).first()
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La categoría no existe"
        )

    medicamento.nombre = datos.nombre
    medicamento.descripcion = datos.descripcion
    medicamento.precio = datos.precio
    medicamento.stock = datos.stock
    medicamento.categoria_id = datos.categoria_id

    db.commit()
    db.refresh(medicamento)

    medicamento_actualizado = (
        db.query(Medicamento)
        .options(joinedload(Medicamento.categoria))
        .filter(Medicamento.id == id)
        .first()
    )

    return medicamento_actualizado


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar medicamento",
    description="Elimina un medicamento existente por su ID.",
    responses={
        204: {"description": "Medicamento eliminado correctamente"},
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Medicamento no encontrado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def eliminar_medicamento(
    id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    medicamento = db.query(Medicamento).filter(Medicamento.id == id).first()

    if medicamento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicamento no encontrado"
        )

    db.delete(medicamento)
    db.commit()