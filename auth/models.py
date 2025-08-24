from __future__ import annotations
from typing import List
from pydantic import BaseModel
from pathlib import Path
import json
from os import getenv

CONFIG_PATH = str(getenv("CONFIG_PATH"))
REPORTS_PATH = str(getenv("REPORTS_PATH"))

class StravaAccess(BaseModel):
    access_token: str = ""
    refresh_token: str = ""
    token_expires: int = 0
    strava_id: int = 0

    def is_expired(self, current_time: int) -> bool:
        """Check if the access token has expired given the current timestamp."""
        return current_time >= self.token_expires
    
    def validate_access(self) -> bool:
        """Check if the credentials are valid"""
        return self.access_token != "" and self.refresh_token != "" and self.token_expires > 0

class Exercise(BaseModel):
    name: str
    sets: List[Set] = []

class Set(BaseModel):
    reps: int
    weight: float
    volume: float
    set_type: str
    progressive_overload: ProgressiveOverload

class ProgressiveOverload(BaseModel):
    last_volume: float = 0
    current_volume: float = 0
    last_reps: int = 0
    current_reps: int = 0
    last_weight: float = 0
    current_weight: float = 0

    # Keep history of last 20 workouts
    history: list[dict] = []

    def add_to_history(self):
        self.history.append({
            "weight": self.current_weight,
            "reps": self.current_reps,
            "volume": self.current_volume
        })
        # Truncate to last 20
        self.history = self.history[-20:]

    
class Report(BaseModel):
    activity_id: int
    notes: str
    name: str
    exercises: List[Exercise] = []
    
class Measures(BaseModel):
    age: int = 16
    bodyweight: int = 47 # kg

class Config(BaseModel):
    strava_access: StravaAccess = StravaAccess()
    emails: List[str] = []
    poll_time_minutes: int = 5
    hevy_identification: str = "Logged with Hevy"
    progressive_overload_truncation: int = 20
    model: str = "mistral:7b-instruct-q4_K_M"
    measures: Measures = Measures()

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
        
class Reports(BaseModel):
    reports: List[Report] = []
    
    def save(self, filepath: str | Path = REPORTS_PATH) -> None:
        """Save reports to a JSON file."""
        path = Path(filepath)
        path.write_text(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, filepath: str | Path = REPORTS_PATH) -> Reports:
        """Load reports from a JSON file."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Reports file not found: {filepath}")
        data = json.loads(path.read_text())
        return cls(**data)

    @classmethod
    def get_default_reports(cls):
        return cls()

config = Config()
reports = Reports()