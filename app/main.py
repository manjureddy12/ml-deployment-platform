
# app/main.py

import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import (
    AQIPredictionRequest,
    AQIPredictionResponse,
    HealthResponse
)
from app.model import load_model, predict_aqi

# ─────────────────────────────────────────────
# App Startup: Pre-load the model
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML model on startup so first request isn't slow."""
    print("🚀 Starting AQI Prediction Service...")
    load_model()
    print("✅ Service ready!")
    yield
    print("🛑 Shutting down service...")


# ─────────────────────────────────────────────
# FastAPI App Configuration
# ─────────────────────────────────────────────
app = FastAPI(
    title="AQI Prediction API",
    description=(
        "A production-ready Air Quality Index prediction service. "
        "Submit pollutant readings and get instant AQI category predictions "
        "powered by a RandomForest ML model."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Allow cross-origin requests (needed for web frontends)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Track service start time for uptime reporting
START_TIME = time.time()


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Service health check"
)
async def health_check():
    """
    Returns the health status of the API service.
    Used by Kubernetes liveness and readiness probes.
    """
    try:
        model = load_model()
        model_loaded = model is not None
    except Exception:
        model_loaded = False

    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        version="1.0.0",
        service="AQI Prediction Service"
    )


@app.post(
    "/predict",
    response_model=AQIPredictionResponse,
    tags=["Prediction"],
    summary="Predict Air Quality Index category"
)
async def predict(request: AQIPredictionRequest):
    """
    Predicts the AQI category based on pollutant readings.

    **Categories:**
    - 0: Good
    - 1: Moderate
    - 2: Unhealthy for Sensitive Groups
    - 3: Unhealthy
    - 4: Hazardous
    """
    try:
        result = predict_aqi(
            pm25=request.pm25,
            pm10=request.pm10,
            co2=request.co2,
            no2=request.no2,
            temperature=request.temperature,
            humidity=request.humidity
        )

        return AQIPredictionResponse(
            status="success",
            category_id=result["category_id"],
            category=result["category"],
            confidence=result["confidence"],
            all_probabilities=result["all_probabilities"],
            message=f"Air quality is predicted to be: {result['category']}"
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.get("/", tags=["Root"])
async def root():
    """API root — redirects users to documentation."""
    return JSONResponse({
        "message": "Welcome to the AQI Prediction API 🌍",
        "docs": "/docs",
        "health": "/health",
        "predict": "POST /predict"
    })