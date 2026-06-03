import os


class Config:
    APP_NAME = "AutoServiceSystem"
    SECRET_KEY = "your-secret-key"


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"


class DebugConfig(Config):
    DEBUG = True
    ENV = "debug"


class TestConfig(Config):
    DEBUG = False
    ENV = "test"
    TESTING = True


def get_config():
    env = os.getenv("APP_ENV", "production")
    if env == "production":
        return ProductionConfig()
    elif env == "debug":
        return DebugConfig()
    elif env == "test":
        return TestConfig()
    return ProductionConfig()


config = get_config()
