from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.database.session import init_db
from app.rag.vector_store import vector_store_instance
from app.api.routes import router
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager to initialize database and seed resources on startup."""
    logger.info("Initializing FlowMind AI application startup...")
    init_db()
    vector_store_instance.seed_initial_knowledge()
    logger.info("Startup complete. FlowMind AI ready.")
    yield
    logger.info("FlowMind AI shutdown complete.")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="FlowMind AI – An Intelligent Student Workflow Intelligence Platform",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
