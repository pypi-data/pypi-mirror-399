"""MizbanCloud SDK Configuration."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class MizbanCloudConfig:
    """Configuration for MizbanCloud client."""

    base_url: str = "https://auth.mizbancloud.com"
    timeout: int = 30
    language: str = "en"
    headers: Dict[str, str] = field(default_factory=dict)
    token: Optional[str] = None
