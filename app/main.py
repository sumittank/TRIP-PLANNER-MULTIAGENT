"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config.settings import get_settings
from app.database.connection import init_db
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import health, history, preferences, travel
from app.utils.exceptions import AppError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    init_db()
    Path(settings.travel_plans_dir).mkdir(parents=True, exist_ok=True)
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(health.router)
app.include_router(travel.router)
app.include_router(history.router)
app.include_router(preferences.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# @app.get("/")
# async def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


# @app.get("/planner")
# async def planner(request: Request):
#     return templates.TemplateResponse("planner.html", {"request": request})


# @app.get("/history-page")
# async def history_page(request: Request):
#     return templates.TemplateResponse("history.html", {"request": request})


# @app.get("/saved-page")
# async def saved_page(request: Request):
#     return templates.TemplateResponse("saved.html", {"request": request})


# @app.get("/settings-page")
# async def settings_page(request: Request):
#     return templates.TemplateResponse("settings.html", {"request": request})


# # @app.get("/about")
# # async def about_page(request: Request):
# #     return templates.TemplateResponse("about.html", {"request": request})

# @app.get("/about")
# async def about_page(request: Request):
#     return templates.TemplateResponse(
#     request=request,
#     name="about.html",
#     context={}
# )


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/planner")
async def planner(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="planner.html",
        context={}
    )


@app.get("/history-page")
async def history_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={}
    )


@app.get("/saved-page")
async def saved_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="saved.html",
        context={}
    )


@app.get("/settings-page")
async def settings_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={}
    )


@app.get("/about")
async def about_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={}
    )