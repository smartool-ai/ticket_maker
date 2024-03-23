import uvicorn
from logging import getLogger

from mangum import Mangum

from src.config import config
from src import Application

config.LOGGER = getLogger("base_logger")
logger = config.LOGGER
logger.info("Starting server...")

fast_app = Application(config).app
logger.info("Starting FastAPI server...")

handler = Mangum(fast_app)
logger.info("Attached Mangum handler...")

if __name__ == "__main__":
    uvicorn.run(fast_app, port=8000)
