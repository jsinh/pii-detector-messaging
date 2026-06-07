from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables / .env.

    Every value has a safe default so the app boots with zero config in dev.
    Override any field by setting an env var with the PII_ prefix, e.g.
    PII_FN_FP_COST_RATIO=20.
    """

    model_config = SettingsConfigDict(
        env_prefix="PII_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- service metadata ---
    app_name: str = "pii-detector-messaging"
    environment: str = "development"  # development | production
    log_level: str = "INFO"
    host: str = "0.0.0.0"  # bind all interfaces (required for Docker); override locally if desired
    port: int = 8000


    # --- detection / eval knobs ---
    # Compliance weighting: how many false positives one false negative is
    # "worth". README default is 10:1 in favour of recall.
    fn_fp_cost_ratio: float = 10.0


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (built once per process)."""
    return Settings()
