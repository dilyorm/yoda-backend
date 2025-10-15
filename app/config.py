import os
from functools import lru_cache
from typing import List


class Settings:
    genie_api_key: str | None
    valid_client_tokens: List[str]
    allowed_origins: List[str]

    def __init__(self) -> None:
        self.genie_api_key = os.getenv('GENIE_API_KEY')
        self.valid_client_tokens = [t.strip() for t in os.getenv('VALID_CLIENT_TOKENS', '').split(',') if t.strip()]
        self.allowed_origins = [o.strip().lower() for o in os.getenv('ALLOWED_ORIGINS', '').split(',') if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


