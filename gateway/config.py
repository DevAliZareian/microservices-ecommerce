from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "API Gateway"
    debug: bool = False
    allowed_hosts: str = "localhost,127.0.0.1"

    user_service_url: str = "http://user_service:8000"
    product_service_url: str = "http://product_service:8000"
    order_service_url: str = "http://order_service:8000"
    payment_service_url: str = "http://payment_service:8000"
    notification_service_url: str = "http://notification_service:8000"

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_lifetime_minutes: int = 15

    cors_allow_origins: str = "*"

    model_config = {"extra": "ignore", "env_prefix": "GATEWAY_"}


settings = Settings()
