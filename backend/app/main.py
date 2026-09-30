from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.data.seed.load_seed_data import seed_if_empty
from app.database import Base, SessionLocal, engine
from app.routers import animals, commentary, environments, matchups, stats, tournaments

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    logger.info("Animal Arena API started")
    yield
    logger.info("Animal Arena API shutting down")


app = FastAPI(
    title="Animal Arena API",
    description=(
        "A deterministic/probabilistic animal matchup simulation engine. "
        "Entertainment only -- not a scientifically validated prediction of "
        "real animal combat outcomes."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("validation error on %s: %s", request.url.path, exc.errors())
    return JSONResponse(status_code=422, content=jsonable_encoder({"detail": exc.errors()}))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "internal server error"})


app.include_router(animals.router)
app.include_router(environments.router)
app.include_router(matchups.router)
app.include_router(tournaments.router)
app.include_router(commentary.router)
app.include_router(stats.router)


@app.get("/api/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}
