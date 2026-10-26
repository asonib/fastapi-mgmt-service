from fastapi import FastAPI
from app.config.settings import settings
from app.controller import actuator_controller, joke_controller, summary_controller, weather_controller
from app.exception.handlers import register_exception_handlers
from app.utils.logger import logger

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register Error Handlers
register_exception_handlers(app)

# Include Controllers
app.include_router(actuator_controller.router)
app.include_router(joke_controller.router)
app.include_router(summary_controller.router)
app.include_router(weather_controller.router)


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting up {settings.APP_NAME}...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down microservice...")
