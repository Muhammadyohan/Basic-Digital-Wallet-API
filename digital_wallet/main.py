from gevent import monkey

monkey.patch_all()

from fastapi import FastAPI

from contextlib import asynccontextmanager

from . import models
from . import routers

from . import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if models.engine is not None:
        # Close the DB connection
        await models.close_session()


def create_app(settings=None):
    settings = config.get_settings()
    app = FastAPI(lifespan=lifespan)

    models.init_db(settings)

    routers.init_routers(app)

    # @app.on_event("startup")
    # async def on_startup():
    #     await models.recreate_table()

    return app
