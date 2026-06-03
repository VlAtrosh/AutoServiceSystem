from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles

from .modules.cars.api import router as cars_router
from .modules.integration.api import router as integration_router
from .modules.order.api import router as order_router
from .modules.reference.api import router as reference_router
from .modules.report.api import router as report_router
from .modules.user.api import router as user_router

app = FastAPI(
    title="AutoServiceSystem",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

# Это добавит кнопку Authorize в Swagger
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(order_router)
app.include_router(reference_router)
app.include_router(report_router)
app.include_router(integration_router)
app.include_router(cars_router)
# Путь к фронтенду (относительно корня проекта)
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend" / "web"

if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

    @app.get("/")
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "index.html not found"}


@app.get("/test-token")
async def test_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"token": credentials.credentials}


@app.get("/health")
def health():
    return {"status": "ok"}
