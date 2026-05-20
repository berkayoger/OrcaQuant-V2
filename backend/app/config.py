import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///orcaquant.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "15"))
    JWT_REFRESH_TOKEN_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_DAYS", "7"))
    ENABLE_BILLING = os.getenv("ENABLE_BILLING", "false").lower() == "true"
    ENABLE_REALTIME = os.getenv("ENABLE_REALTIME", "false").lower() == "true"
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(1024 * 1024)))  # 1MB default
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    MARKET_DATA_PROVIDER = os.getenv("MARKET_DATA_PROVIDER", "sample").strip().lower()
    MARKET_DATA_TIMEOUT_SECONDS = int(os.getenv("MARKET_DATA_TIMEOUT_SECONDS", "10"))
    MARKET_DATA_CACHE_TTL_SECONDS = int(os.getenv("MARKET_DATA_CACHE_TTL_SECONDS", "300"))


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///orcaquant-dev.db")


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    DEBUG = False
