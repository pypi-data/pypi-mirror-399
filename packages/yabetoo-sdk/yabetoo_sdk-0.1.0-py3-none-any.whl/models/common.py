from typing import Dict
from pydantic import BaseModel
from enum import Enum





class HttpClientOptions(BaseModel):
    """HTTP client configuration options"""
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    verify_ssl: bool = True
    follow_redirects: bool = True
    custom_headers: Dict[str, str] = {}

class EnvironmentType(str, Enum):
    SANDBOX = 'sandbox'
    PRODUCTION = 'production'
