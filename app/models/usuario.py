from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False, index=True)
    direccion = Column(String(150), nullable=False)
    username = Column(String(20), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)