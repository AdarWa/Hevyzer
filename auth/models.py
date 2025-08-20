from __future__ import annotations
from typing import List
from pydantic import BaseModel
from pathlib import Path
import json
from os import getenv

CONFIG_PATH = str(getenv("CONFIG_PATH"))

class StravaAccess(BaseModel):
    access_token: str = ""
    refresh_token: str = ""
    token_expires: int = 0

    def is_expired(self, current_time: int) -> bool:
        """Check if the access token has expired given the current timestamp."""
        return current_time >= self.token_expires
    
    def validate_access(self) -> bool:
        """Check if the credentials are valid"""
        return self.access_token != "" and self.refresh_token != "" and self.token_expires > 0


class Config(BaseModel):
    strava_access: StravaAccess = StravaAccess()
    emails: List[str] = []
    poll_time_minutes: int = 5


    def save(self, filepath: str | Path = CONFIG_PATH) -> None:
        """Save configuration to a JSON file."""
        path = Path(filepath)
        path.write_text(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, filepath: str | Path = CONFIG_PATH) -> Config:
        """Load configuration from a JSON file."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        data = json.loads(path.read_text())
        return cls(**data)

    @classmethod
    def get_default_config(cls):
        return cls()

    def update_strava_tokens(self, access_token: str, refresh_token: str, token_expires: int) -> None:
        """Update Strava tokens in place."""
        self.strava_access.access_token = access_token
        self.strava_access.refresh_token = refresh_token
        self.strava_access.token_expires = token_expires

config = Config()