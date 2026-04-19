from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Medicamento(Base):
    __tablename__ = "medicamento"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(String(255), nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categoria.id"), nullable=False)

    categoria = relationship("Categoria")