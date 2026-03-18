from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.email_routes import router as email_router
from app.config import settings

app = FastAPI(
    title="Email Classifier API",
    description="API para classificação inteligente de emails usando IA",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email_router)
