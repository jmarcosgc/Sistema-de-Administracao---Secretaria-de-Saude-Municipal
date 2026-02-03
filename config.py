import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://admin:1234@localhost:5432/dbsistemasaude"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JSON_SORT_KEYS = False

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')