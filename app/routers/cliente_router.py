from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.schemas.cliente_schema import (
    ClienteCreate,
    ClienteResponse,
    ClienteUpdate
)
from app.schemas.error_schema import ErrorResponse

router = APIRouter(
    prefix="/api/cliente",
    tags=["Clientes"]
)


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cliente",
    description="""
Crea un nuevo cliente en el sistema.

### Reglas:
- El documento debe ser único.
- El correo y teléfono son opcionales.
- Requiere autenticación JWT.
""",
    response_description="Cliente creado correctamente.",
    responses={
        201: {"description": "Cliente creado correctamente"},
        400: {
            "model": ErrorResponse,
            "description": "Datos inválidos o documento duplicado"
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
def guardar_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    existente = db.query(Cliente).filter(Cliente.documento == cliente.documento).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El documento ya está registrado"
        )

    nuevo_cliente = Cliente(
        nombre=cliente.nombre,
        documento=cliente.documento,
        telefono=cliente.telefono,
        correo=cliente.correo
    )

    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return nuevo_cliente


@router.get(
    "",
    response_model=list[ClienteResponse],
    summary="Listar clientes",
    description="Obtiene el listado completo de clientes registrados en el sistema.",
    response_description="Listado de clientes obtenido correctamente.",
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
def listar_clientes(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    return db.query(Cliente).all()


@router.get(
    "/{id}",
    response_model=ClienteResponse,
    summary="Obtener cliente por ID",
    description="Retorna la información de un cliente específico según su identificador.",
    response_description="Cliente encontrado correctamente.",
    responses={
        200: {"description": "Cliente encontrado"},
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Cliente no encontrado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def obtener_cliente_por_id(
    id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    return cliente


@router.put(
    "/{id}",
    response_model=ClienteResponse,
    summary="Actualizar cliente",
    description="""
Actualiza la información de un cliente existente.

### Reglas:
- El cliente debe existir.
- No puede existir otro cliente con el mismo documento.
- Requiere autenticación JWT.
""",
    response_description="Cliente actualizado correctamente.",
    responses={
        200: {"description": "Cliente actualizado correctamente"},
        400: {
            "model": ErrorResponse,
            "description": "Documento duplicado o datos inválidos"
        },
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Cliente no encontrado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def actualizar_cliente(
    id: int,
    datos: ClienteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    repetido = db.query(Cliente).filter(
        Cliente.documento == datos.documento,
        Cliente.id != id
    ).first()

    if repetido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe otro cliente con ese documento"
        )

    cliente.nombre = datos.nombre
    cliente.documento = datos.documento
    cliente.telefono = datos.telefono
    cliente.correo = datos.correo

    db.commit()
    db.refresh(cliente)

    return cliente


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar cliente",
    description="Elimina un cliente existente por su ID.",
    responses={
        204: {"description": "Cliente eliminado correctamente"},
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Cliente no encontrado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def eliminar_cliente(
    id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    db.delete(cliente)
    db.commit()