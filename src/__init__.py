from logging import Logger
from typing import TYPE_CHECKING

from src.lib.constants import ORIGINS
from src.lib.loggers import get_module_logger

if TYPE_CHECKING:
    from src.config import Config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class Application:
    def __init__(self, config: "Config"):
        self.logger: Logger = config.LOGGER if config.LOGGER else get_module_logger()
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

    @property
    def app(self) -> FastAPI:
        return self._app

    def _connect_routers(self) -> None:
        import src.controllers as controllers

        routers = [
            controllers.file_management.router,
            controllers.health.router,
            controllers.ticket.router,
            controllers.user_metadata.router,
        ]

        for router in routers:
            self._app.include_router(router, prefix="/api")
