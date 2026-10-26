from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class WeatherResponse(BaseModel):
    city: str
    temperature: float
    condition: str
    humidity: int


class JokeResponse(BaseModel):
    joke_text: str
    category: str


class SummaryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class SummaryResponse(BaseModel):
    summary: str


class ActuatorLink(BaseModel):
    href: str
    templated: bool = False

class ActuatorIndexResponse(BaseModel):
    links: Dict[str, ActuatorLink]

class HealthComponent(BaseModel):
    status: str
    details: Optional[Dict[str, Any]] = None

class ActuatorHealthResponse(BaseModel):
    status: str
    components: Optional[Dict[str, HealthComponent]] = None

class ActuatorInfoResponse(BaseModel):
    app: Dict[str, Any]
