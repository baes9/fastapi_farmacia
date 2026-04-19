from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, SessionLocal, engine
from app.core.exception_handlers import register_exception_handlers
from app.core.security import obtener_password_hash
from app.models.categoria import Categoria
from app.models.cliente import Cliente
from app.models.medicamento import Medicamento
from app.models.usuario import Usuario
from app.models.venta import DetalleVenta, Venta
from app.routers.categoria_router import router as categoria_router
from app.routers.cliente_router import router as cliente_router
from app.routers.login_router import router as login_router
from app.routers.medicamento_router import router as medicamento_router
from app.routers.usuario_router import router as usuario_router
from app.routers.venta_router import router as venta_router


tags_metadata = [
    {
        "name": "Inicio",
        "description": "Endpoints básicos de verificación del servicio."
    },
    {
        "name": "Autenticación",
        "description": "Endpoints para autenticación de usuarios y generación de token JWT."
    },
    {
        "name": "Usuarios",
        "description": "Gestión de usuarios del sistema."
    },
    {
        "name": "Categorías",
        "description": "Administración de categorías de medicamentos."
    },
    {
        "name": "Clientes",
        "description": "Administración de clientes de la farmacia."
    },
    {
        "name": "Medicamentos",
        "description": "Gestión de medicamentos, precios, stock y categorías."
    },
    {
        "name": "Ventas",
        "description": "Registro y consulta de ventas con detalle de ítems y descuento automático de stock."
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin = db.query(Usuario).filter(Usuario.username == "admin").first()

        if admin is None:
            admin = Usuario(
                nombre="Administrador",
                correo="admin@farmacia.com",
                direccion="Cuenca",
                username="admin",
                password=obtener_password_hash("Admin123")
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()

    yield


app = FastAPI(
    title="API FARMACIA",
    version="1.0",
    summary="API REST para gestión de farmacia :D",
    description="""
API desarrollada con **FastAPI** para la gestión de una farmacia.

Desarrollado por **Braddley Estrella, Alexander Arevalo, Jean Pierre Chica**.

## Funcionalidades principales
- Autenticación con JWT
- Gestión de usuarios
- Gestión de categorías
- Gestión de clientes
- Gestión de medicamentos
- Registro de ventas con detalle
- Descuento automático de stock

## Flujo recomendado de uso
1. Iniciar sesión en `/api/login`
2. Copiar el token devuelto
3. Presionar **Authorize** en Swagger
4. Probar los endpoints protegidos

## Usuario inicial por defecto
- **username:** `admin`
- **password:** `Admin123`
""",
    docs_url="/swagger-ui.html",
    openapi_url="/v3/api-docs",
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

register_exception_handlers(app)


@app.get(
    "/",
    tags=["Inicio"],
    summary="Verificar disponibilidad de la API",
    description="Endpoint básico para comprobar que la API está funcionando correctamente.",
    response_description="Mensaje de confirmación del servicio."
)
def home():
    return {"mensaje": "API Farmacia en FastAPI"}


app.include_router(login_router)
app.include_router(usuario_router)
app.include_router(categoria_router)
app.include_router(cliente_router)
app.include_router(medicamento_router)
app.include_router(venta_router)