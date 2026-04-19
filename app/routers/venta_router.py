from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.cliente import Cliente
from app.models.medicamento import Medicamento
from app.models.usuario import Usuario
from app.models.venta import DetalleVenta, Venta
from app.schemas.error_schema import ErrorResponse
from app.schemas.venta_schema import (
    DetalleVentaResponse,
    VentaCreate,
    VentaResponse
)

router = APIRouter(
    prefix="/api/venta",
    tags=["Ventas"]
)


def redondear(valor: Decimal) -> Decimal:
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def construir_venta_response(venta: Venta) -> VentaResponse:
    return VentaResponse(
        id=venta.id,
        fecha=venta.fecha,
        cliente_id=venta.cliente.id,
        cliente_documento=venta.cliente.documento,
        cliente_nombre=venta.cliente.nombre,
        vendedor_username=venta.usuario.username if venta.usuario else None,
        total=venta.total,
        detalles=[
            DetalleVentaResponse(
                id=detalle.id,
                medicamento_id=detalle.medicamento.id,
                nombre_medicamento=detalle.medicamento.nombre,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario,
                subtotal=detalle.subtotal
            )
            for detalle in venta.detalles
        ]
    )


def obtener_cliente_desde_request(datos: VentaCreate, db: Session) -> Cliente:
    if datos.cliente_id is not None:
        cliente = db.query(Cliente).filter(Cliente.id == datos.cliente_id).first()
        if cliente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado"
            )
        return cliente

    documento = (datos.cliente_documento or "").strip()
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe indicar cliente_id o cliente_documento"
        )

    cliente = db.query(Cliente).filter(Cliente.documento == documento).first()
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado para ese documento"
        )

    return cliente


@router.post(
    "",
    response_model=VentaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar venta",
    description="""
Registra una venta con uno o varios medicamentos.

### Reglas:
- Se debe enviar `cliente_id` o `cliente_documento`.
- Cada item debe tener `medicamento_id` y `cantidad`.
- El sistema calcula automáticamente precio unitario, subtotal y total.
- El stock del medicamento se descuenta automáticamente.
- El vendedor se obtiene desde el token JWT.
""",
    response_description="Venta registrada correctamente.",
    responses={
        201: {"description": "Venta registrada correctamente"},
        400: {
            "model": ErrorResponse,
            "description": "Datos inválidos o stock insuficiente"
        },
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Cliente o medicamento no encontrado"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def registrar_venta(
    datos: VentaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    cliente = obtener_cliente_desde_request(datos, db)

    venta = Venta(
        fecha=datetime.now(),
        cliente=cliente,
        usuario=usuario_actual,
        total=Decimal("0.00")
    )

    db.add(venta)

    total = Decimal("0.00")

    for item in datos.items:
        medicamento = db.query(Medicamento).filter(Medicamento.id == item.medicamento_id).first()

        if medicamento is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medicamento no encontrado: {item.medicamento_id}"
            )

        if medicamento.stock < item.cantidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Stock insuficiente para {medicamento.nombre} "
                    f"(disponible: {medicamento.stock}, solicitado: {item.cantidad})"
                )
            )

        precio = redondear(Decimal(medicamento.precio))
        subtotal = redondear(precio * item.cantidad)

        detalle = DetalleVenta(
            venta=venta,
            medicamento=medicamento,
            cantidad=item.cantidad,
            precio_unitario=precio,
            subtotal=subtotal
        )

        db.add(detalle)

        medicamento.stock = medicamento.stock - item.cantidad
        total += subtotal

    venta.total = redondear(total)

    db.commit()

    venta_guardada = (
        db.query(Venta)
        .options(
            joinedload(Venta.cliente),
            joinedload(Venta.usuario),
            joinedload(Venta.detalles).joinedload(DetalleVenta.medicamento)
        )
        .filter(Venta.id == venta.id)
        .first()
    )

    return construir_venta_response(venta_guardada)


@router.get(
    "",
    response_model=list[VentaResponse],
    summary="Listar ventas",
    description="Obtiene el listado completo de ventas registradas, ordenadas de la más reciente a la más antigua.",
    response_description="Listado de ventas obtenido correctamente.",
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
def listar_ventas(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    ventas = (
        db.query(Venta)
        .options(
            joinedload(Venta.cliente),
            joinedload(Venta.usuario),
            joinedload(Venta.detalles).joinedload(DetalleVenta.medicamento)
        )
        .order_by(Venta.fecha.desc())
        .all()
    )

    return [construir_venta_response(v) for v in ventas]


@router.get(
    "/{id}",
    response_model=VentaResponse,
    summary="Obtener venta por ID",
    description="Retorna una venta específica con sus detalles, cliente y vendedor.",
    response_description="Venta encontrada correctamente.",
    responses={
        200: {"description": "Venta encontrada"},
        401: {
            "model": ErrorResponse,
            "description": "No autorizado"
        },
        404: {
            "model": ErrorResponse,
            "description": "Venta no encontrada"
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor"
        }
    }
)
def obtener_venta_por_id(
    id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    venta = (
        db.query(Venta)
        .options(
            joinedload(Venta.cliente),
            joinedload(Venta.usuario),
            joinedload(Venta.detalles).joinedload(DetalleVenta.medicamento)
        )
        .filter(Venta.id == id)
        .first()
    )

    if venta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )

    return construir_venta_response(venta)