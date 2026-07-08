import os


def _csv_env(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///orcaquant.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "15"))
    JWT_REFRESH_TOKEN_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_DAYS", "7"))
    ENABLE_BILLING = os.getenv("ENABLE_BILLING", "false").lower() == "true"
    ENABLE_REALTIME = os.getenv("ENABLE_REALTIME", "false").lower() == "true"
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(1024 * 1024)))  # 1MB default
    CORS_ALLOWED_ORIGINS = _csv_env("CORS_ALLOWED_ORIGINS", "http://localhost:5173")
    MARKET_DATA_PROVIDER = os.getenv("MARKET_DATA_PROVIDER", "sample").strip().lower()
    MARKET_DATA_TIMEOUT_SECONDS = int(os.getenv("MARKET_DATA_TIMEOUT_SECONDS", "10"))
    MARKET_DATA_CACHE_TTL_SECONDS = int(os.getenv("MARKET_DATA_CACHE_TTL_SECONDS", "300"))

    ACCOUNT_VERIFICATION_CODE_TTL_MINUTES = int(os.getenv("ACCOUNT_VERIFICATION_CODE_TTL_MINUTES", "10"))
    ACCOUNT_VERIFICATION_MAX_ATTEMPTS = int(os.getenv("ACCOUNT_VERIFICATION_MAX_ATTEMPTS", "5"))
    ACCOUNT_CODE_DEBUG_RESPONSE = os.getenv("ACCOUNT_CODE_DEBUG_RESPONSE", "false").lower() == "true"
    ACCOUNT_CODE_CHANNEL = os.getenv("ACCOUNT_CODE_CHANNEL", "email").strip().lower()

    # External billing provider boundary. Provider adapters must read through
    # these settings instead of reaching into os.environ directly.
    BILLING_PROVIDER = os.getenv("BILLING_PROVIDER", "fake").strip().lower()
    BILLING_ALLOWED_CURRENCIES = _csv_env("BILLING_ALLOWED_CURRENCIES", "TRY,USD,EUR")
    BILLING_CHECKOUT_SUCCESS_URL = os.getenv("BILLING_CHECKOUT_SUCCESS_URL", "http://localhost:5173/billing/success")
    BILLING_CHECKOUT_FAILURE_URL = os.getenv("BILLING_CHECKOUT_FAILURE_URL", "http://localhost:5173/billing/failure")
    BILLING_CALLBACK_URL = os.getenv("BILLING_CALLBACK_URL", "http://localhost:5000/api/v1/billing/callback/iyzico")
    PAYMENT_PROVIDER_TIMEOUT_SECONDS = int(os.getenv("PAYMENT_PROVIDER_TIMEOUT_SECONDS", "15"))

    IYZICO_API_KEY = os.getenv("IYZICO_API_KEY", "")
    IYZICO_SECRET = os.getenv("IYZICO_SECRET", "")
    IYZICO_BASE_URL = os.getenv("IYZICO_BASE_URL", "https://sandbox-api.iyzipay.com")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///orcaquant-dev.db")


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ACCOUNT_CODE_DEBUG_RESPONSE = True


class ProductionConfig(BaseConfig):
    DEBUG = False
