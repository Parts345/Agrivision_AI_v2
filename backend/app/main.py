from __future__ import annotations

import io
import logging
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Header, HTTPException, Query, Response, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps, UnidentifiedImageError

from app import db
from app.config import settings
from app.disease_info import CLASS_NAMES, DISPLAY_NAMES, get_disease_details
from app.schemas import (
    HealthResponse,
    PredictionResponse,
    ScanDetail,
    ScanList,
    StatsResponse,
)
from app.services.model_service import load_model, model_is_loaded, predict

logger = logging.getLogger("agrivision")
DEVICE_ID_PATTERN = re.compile(r"^[A-Za-z0-9-]{8,64}$")
THUMBNAIL_SIZE = (320, 320)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    try:
        load_model()
    except Exception as exc:
        print(f"Model warmup skipped: {exc}")
    yield


app = FastAPI(title=settings.app_name, version=settings.api_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


def _device_id(value: str | None) -> str:
    if not value or not DEVICE_ID_PATTERN.match(value):
        raise HTTPException(status_code=400, detail="A valid device id is required.")
    return value


def analyze(image_bytes: bytes) -> tuple[dict, bytes]:
    """Run the model and build a small JPEG thumbnail from one decode."""
    result = predict(image_bytes)
    image = Image.open(io.BytesIO(image_bytes))
    image = ImageOps.exif_transpose(image).convert("RGB")
    image.thumbnail(THUMBNAIL_SIZE)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=82)
    return result, buffer.getvalue()


def _label_for(class_name: str) -> str:
    return DISPLAY_NAMES.get(class_name, class_name)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=model_is_loaded(),
        model_path=str(settings.model_path),
        classes=[_label_for(name) for name in CLASS_NAMES],
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_endpoint(
    file: UploadFile = File(...),
    x_device_id: str | None = Header(default=None),
) -> PredictionResponse:
    device_id = _device_id(x_device_id) if x_device_id else None

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file.")

    image_bytes = await file.read(settings.max_upload_bytes + 1)
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")
    if len(image_bytes) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Image is too large. Maximum size is {settings.max_upload_bytes // (1024 * 1024)} MB.",
        )

    try:
        result, thumbnail = await run_in_threadpool(analyze, image_bytes)
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="The uploaded file is not a readable image.") from exc
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

    scan_id = None
    if device_id:
        try:
            scan_id = await run_in_threadpool(
                db.insert_scan,
                device_id,
                result["predicted_class"],
                result["confidence"],
                result["probabilities"],
                thumbnail,
            )
        except Exception:
            logger.exception("Could not save scan history")

    return PredictionResponse(scan_id=scan_id, **result)


@app.get("/scans", response_model=ScanList)
async def list_scans(
    x_device_id: str | None = Header(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ScanList:
    device_id = _device_id(x_device_id)
    items, total = await run_in_threadpool(db.list_scans, device_id, limit, offset)
    return ScanList(items=items, total=total)


@app.get("/scans/{scan_id}", response_model=ScanDetail)
async def get_scan(scan_id: str, x_device_id: str | None = Header(default=None)) -> ScanDetail:
    device_id = _device_id(x_device_id)
    row = await run_in_threadpool(db.get_scan, device_id, scan_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    details = get_disease_details(row["predicted_class"])
    return ScanDetail(
        id=row["id"],
        created_at=row["created_at"],
        scan_id=row["id"],
        predicted_class=row["predicted_class"],
        predicted_label=details["label"],
        confidence=row["confidence"],
        probabilities=row["probabilities"],
        description=details["description"],
        symptoms=details["symptoms"],
        causes=details["causes"],
        prevention=details["prevention"],
        treatment=details["treatment"],
        risk_level=details["risk_level"],
    )


@app.get("/scans/{scan_id}/thumbnail")
async def scan_thumbnail(scan_id: str, x_device_id: str | None = Header(default=None)) -> Response:
    device_id = _device_id(x_device_id)
    data = await run_in_threadpool(db.get_thumbnail, device_id, scan_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Thumbnail not found.")
    return Response(content=data, media_type="image/jpeg", headers={"Cache-Control": "private, max-age=86400"})


@app.delete("/scans/{scan_id}", status_code=204)
async def delete_scan(scan_id: str, x_device_id: str | None = Header(default=None)) -> Response:
    device_id = _device_id(x_device_id)
    deleted = await run_in_threadpool(db.delete_scan, device_id, scan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return Response(status_code=204)


@app.get("/stats", response_model=StatsResponse)
async def stats() -> StatsResponse:
    data = await run_in_threadpool(db.get_stats)
    return StatsResponse(**data)
