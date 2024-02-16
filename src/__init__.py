import os

from logging import getLogger, Logger
from typing import TYPE_CHECKING

from src.lib.constants import ORIGINS

if TYPE_CHECKING:
    from src.config import Config

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


class Application:
    def __init__(self, config: "Config"):
        self.logger: Logger = config.LOGGER if config.LOGGER else getLogger()
        self.logger.setLevel(config.LOG_LEVEL)
        self._app = FastAPI(title="Ticket Transcriber API")

        # Add CORS headers
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Connect routers to the application
        self._connect_routers()

        # Fallback to the UI
        if os.path.exists("/tmp/static"):
            self._app.mount(
                "/",
                StaticFiles(directory="/tmp/static", html=True),
                name="static"
            )

    @property
    def app(self) -> FastAPI:
        return self._app

    def _connect_routers(self) -> None:
        import src.controllers as controllers

        routers = [
            controllers.file_management.router,
            controllers.ticket.router,
            controllers.user_metadata.router
        ]

        for router in routers:
            self._app.include_router(router, prefix="/api")
