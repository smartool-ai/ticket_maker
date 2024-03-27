import uvicorn
from mangum import Mangum
from pixelum_core.loggers.loggers import get_module_logger

from src.config import config
from src import Application

config.LOGGER = get_module_logger()
logger = config.LOGGER
logger.info("Starting server...")

fast_app = Application(config).app
logger.info("Starting FastAPI server...")

handler = Mangum(fast_app, lifespan="off")
logger.info("Attached Mangum handler...")

if __name__ == "__main__":
    uvicorn.run(fast_app, port=8000)
