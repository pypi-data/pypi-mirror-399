from .base import BaseConfig


class CommerceConfig(BaseConfig):
    auto_logout: bool = False
    content_type: str = "application/xml"
    partner_id: str | None = None
    password: str | None = None
    sandbox: bool = True
    username: str | None = None
