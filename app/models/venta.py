from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from app.core.database import Base


class Venta(Base):
    __tablename__ = "venta"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=False)

    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=True)

    total = Column(Numeric(14, 2), nullable=False)

    cliente = relationship("Cliente")
    usuario = relationship("Usuario")
    detalles = relationship(
        "DetalleVenta",
        back_populates="venta",
        cascade="all, delete-orphan"
    )


class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("venta.id"), nullable=False)
    medicamento_id = Column(Integer, ForeignKey("medicamento.id"), nullable=False)

    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(14, 2), nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    medicamento = relationship("Medicamento")