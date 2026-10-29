from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str
    classes: list[str]


class PredictionResponse(BaseModel):
<<<<<<< HEAD
    scan_id: str | None = None
=======
>>>>>>> origin/main
    predicted_class: str
    predicted_label: str
    confidence: float
    probabilities: dict[str, float]
    description: str
    symptoms: list[str]
    causes: list[str]
    prevention: list[str]
    treatment: list[str]
    risk_level: str
<<<<<<< HEAD


class ScanSummary(BaseModel):
    id: str
    created_at: str
    predicted_class: str
    confidence: float
    has_thumbnail: bool


class ScanList(BaseModel):
    items: list[ScanSummary]
    total: int


class ScanDetail(PredictionResponse):
    id: str
    created_at: str


class DailyCount(BaseModel):
    day: str
    count: int


class RecentScan(BaseModel):
    created_at: str
    predicted_class: str
    confidence: float


class StatsResponse(BaseModel):
    total_scans: int
    scans_last_7_days: int
    by_class: dict[str, int]
    daily: list[DailyCount]
    recent: list[RecentScan]
=======
>>>>>>> origin/main
