import logging

from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    api_key: str
    base_url: str | None = None
    content_type: str | None = None
    log_level: int = logging.WARNING
    logger: logging.Logger | None = None
    timeout_ms: int = 60_000
