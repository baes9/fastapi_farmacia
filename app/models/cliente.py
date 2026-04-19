from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    documento = Column(String(20), nullable=False, unique=True, index=True)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(120), nullable=True)