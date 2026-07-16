import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Secure PIN-based file and text sharing API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Apply CORS configurations
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include api_router (includes health checks and future API endpoints)
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
def startup_event():
    # Ensure tables exist in database
    from app.core.database import Base, engine
    from app.models.share import Share
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized.")

    # Verify local uploads directory exists
    if not os.path.exists(settings.UPLOAD_DIR):
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        print(f"Created local uploads directory at {settings.UPLOAD_DIR}")

@app.get("/", tags=["Root"])
def root_endpoint():
    return {
        "message": f"Welcome to the {settings.APP_NAME} API",
        "documentation": "/docs"
    }
