import os

class Config:
    ENV = os.getenv("APP_ENV", "dev")
    if ENV == "prod":
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    elif ENV == "dev":
        SQLALCHEMY_DATABASE_URI = os.getenv('LOCAL_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   
        "pool_recycle": 300     
    }