from fastapi import FastAPI

from .models import init_db
from .routers import init_routers


def create_app():
    app = FastAPI()

    init_routers(app)
    init_db()

    return app
