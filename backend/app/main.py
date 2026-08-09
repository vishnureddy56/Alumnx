import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db
from app.schemas.task import InvalidEnumValueException
from app.utils.exception_handlers import (
    invalid_enum_value_handler,
    validation_exception_handler
)
from app.routers.task_router import router as task_router
from app.routers.extended_router import router as extended_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RouteIQ")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RouteIQ database...")
    init_db()
    logger.info("RouteIQ database initialized.")
    yield


app = FastAPI(
    title="RouteIQ",
    description="AI-Powered Sales Inbox & Task Routing Backend Service",
    version="1.0.0",
    lifespan=lifespan
)

# Exception handlers for exact 400 format for enum failures
app.add_exception_handler(InvalidEnumValueException, invalid_enum_value_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# CORS configuration
origins = [
    "*",
    "http://localhost:5173",
    "http://localhost:3000",
    settings.FRONTEND_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(task_router)
app.include_router(extended_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
