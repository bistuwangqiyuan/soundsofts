"""腐蚀与应力在线监测平台 V2.0 - FastAPI Backend."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import (
    auth,
    coupling,
    data_cards,
    data_visualization,
    defect_analysis,
    inference,
    preprocessing,
    training,
)
from core.config import get_settings

settings = get_settings()
from core.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown."""
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="腐蚀与应力在线监测平台 V2.0 API",
    description="聚乙烯补口粘接检测 - 声力耦合分析、缺陷检测与报告生成",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "healthy", "version": "2.0.0"}


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(data_visualization.router, prefix="/data", tags=["Data Visualization"])
app.include_router(data_cards.router, prefix="/data", tags=["Data Cards"])
app.include_router(preprocessing.router, prefix="/preprocess", tags=["Preprocessing"])
app.include_router(training.router, prefix="/training", tags=["Training"])
app.include_router(inference.router, prefix="/inference", tags=["Inference"])
app.include_router(defect_analysis.router, prefix="/defects", tags=["Defect Analysis"])
app.include_router(coupling.router, prefix="/coupling", tags=["Coupling"])
