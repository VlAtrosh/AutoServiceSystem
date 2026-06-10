from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.v1.endpoints import posts
from app.api.v1.endpoints import works_router, parts_router
from app.api.v1.endpoints.cars import router as cars_router
from app.api.v1.endpoints.mechanics import router as mechanics_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.appointments import router as appointments_router

from app.core.config import settings
from app.api.v1.endpoints import auth_router, clients_router, orders_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    swagger_ui_parameters={"persistAuthorization": True},
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== РОУТЕРЫ ==========
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(clients_router, prefix=settings.API_V1_STR)
app.include_router(orders_router, prefix=settings.API_V1_STR)
app.include_router(posts.router, prefix=settings.API_V1_STR)
app.include_router(works_router, prefix=settings.API_V1_STR)
app.include_router(parts_router, prefix=settings.API_V1_STR)
app.include_router(cars_router, prefix=settings.API_V1_STR)
app.include_router(mechanics_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(appointments_router, prefix=settings.API_V1_STR, tags=["Запись на ремонт"])

# ========== ФРОНТЕНД ==========
FRONTEND_WEB = Path("/app/frontend/web")

if FRONTEND_WEB.exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_WEB / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_WEB / "js")), name="js")
    
    @app.get("/")
    async def serve_index():
        index_file = FRONTEND_WEB / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "index.html not found"}
else:
    @app.get("/")
    async def root():
        return {
            "message": "AutoServiceSystem API",
            "version": settings.VERSION,
            "docs": f"{settings.API_V1_STR}/docs"
        }

# ========== HEALTH CHECK ==========
@app.get("/health")
async def health_check():
    return {"status": "ok", "env": settings.APP_ENV}