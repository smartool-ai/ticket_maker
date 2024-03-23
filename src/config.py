"""
config.py:  Maintains the configuration settings for the application
            Should be one of the first modules imported and should not
            have any application dependencies in its import.
"""

import os
import json
from logging import getLogger, Logger


class Config:
    """
    Common Configuration
    """

    CONFIGURATION_NAME = ""
    LOGGER: Logger = getLogger()
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

    def __repr__(self) -> str:
        """
        Returns a string representation of the Config object
        """
        rep = {
            "LOGGER": self.LOGGER.level,
        }
        return json.dumps(rep)


class DevelopmentConfig(Config):
    """
    Development Configuration
    """

    CONFIGURATION_NAME = "development"
    DEBUG = True


class TestingConfig(Config):
    """
    Testing Configuration
    """

    CONFIGURATION_NAME = "testing"
    DEBUG = True
    TESTING = True


class DeployedConfig(Config):
    """
    Deployed Configuration
    """

    CONFIGURATION_NAME = "deployed"
    DEBUG = True


class ProductionConfig(DeployedConfig):
    """
    Production Configuration
    """

    CONFIGURATION_NAME = "production"
    DEBUG = True


app_config = {
    "deployed": DeployedConfig,
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


CONFIGURATION_NAME = os.getenv("TRANSCRIBER_CONFIGURATION", "testing")

if CONFIGURATION_NAME not in app_config:
    raise RuntimeError(f"Invalid configuration string {CONFIGURATION_NAME}")

# Instantiate the configuration object
config: Config = app_config[CONFIGURATION_NAME]()
