import os
import uvicorn
from logging import getLogger

from fastapi import Request, Response
from starlette.background import BackgroundTask
from starlette.types import Message
from mangum import Mangum

from src.config import config
from src.bootstrap import bootstrap
from src import Application
from dotenv import load_dotenv


load_dotenv()
bootstrap()

config.LOGGER = getLogger("base_logger")
logger = config.LOGGER
logger.info("Starting server...")

fast_app = Application(config).app
logger.info("Starting FastAPI server...")

handler = Mangum(fast_app)
logger.info("Attached Mangum handler...")

if __name__ == "__main__":
    uvicorn.run(fast_app, port=8000)
