
from pydantic import BaseModel, Field
from typing import Dict


class AQIPredictionRequest(BaseModel):
    """Input schema for AQI prediction endpoint."""

    pm25: float = Field(
        ...,
        ge=0,
        le=500,
        description="Fine particulate matter concentration in µg/m³ (0–500)",
        example=35.5
    )
    pm10: float = Field(
        ...,
        ge=0,
        le=600,
        description="Coarse particulate matter concentration in µg/m³ (0–600)",
        example=60.0
    )
    co2: float = Field(
        ...,
        ge=300,
        le=5000,
        description="Carbon dioxide concentration in ppm (300–5000)",
        example=420.0
    )
    no2: float = Field(
        ...,
        ge=0,
        le=400,
        description="Nitrogen dioxide concentration in µg/m³ (0–400)",
        example=25.0
    )
    temperature: float = Field(
        ...,
        ge=-10,
        le=50,
        description="Ambient temperature in Celsius (-10 to 50)",
        example=22.5
    )
    humidity: float = Field(
        ...,
        ge=10,
        le=100,
        description="Relative humidity percentage (10–100)",
        example=65.0
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pm25": 35.5,
                "pm10": 60.0,
                "co2": 420.0,
                "no2": 25.0,
                "temperature": 22.5,
                "humidity": 65.0
            }
        }


class AQIPredictionResponse(BaseModel):
    """Output schema for AQI prediction endpoint."""

    status: str
    category_id: int
    category: str
    confidence: float
    all_probabilities: Dict[str, float]
    message: str


class HealthResponse(BaseModel):
    """Output schema for health check endpoint."""
    model_config = {"protected_namespaces": ()}
    status: str
    model_loaded: bool
    version: str
    service: str