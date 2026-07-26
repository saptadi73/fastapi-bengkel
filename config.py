import os
from urllib.parse import quote_plus

from dotenv import load_dotenv


load_dotenv()


def _get_env(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is None:
        return default
    return value


def get_database_url() -> str:
    database_url = _get_env("DATABASE_URL")
    if database_url:
        return database_url

    db_driver = _get_env("DB_DRIVER", "postgresql+psycopg2")
    db_host = _get_env("DB_HOST", "localhost")
    db_port = _get_env("DB_PORT", "5432")
    db_user = _get_env("DB_USER", "openpg")
    db_password = _get_env("DB_PASSWORD", "openpgpwd")
    db_name = _get_env("DB_NAME", "bengkel")

    user = quote_plus(db_user)
    password = quote_plus(db_password)
    return f"{db_driver}://{user}:{password}@{db_host}:{db_port}/{db_name}"


def get_starsender_api_key() -> str:
    return _get_env("STARSENDER_API_KEY", "")
