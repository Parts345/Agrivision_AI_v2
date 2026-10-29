# AgriVision

Rice leaf disease screening for farmers and agronomists.

- **Web app** (`frontend/`): React + Vite. Check a leaf, view your scan history, and see the public dashboard. Available in English, Marathi, and Hindi.
- **API** (`backend/`): FastAPI + TensorFlow. Runs the model, stores scan history per device in SQLite, and serves dashboard statistics.
- **Streamlit app** (`app.py`, `utils/`): a separate single-page version that uses the same model and disease data.

## Privacy

- No accounts. The browser creates a random device id and sends it with each scan.
- Scan history and thumbnails are only returned to the device that created them.
- The dashboard shows totals and class counts across all users. It never shows device ids.
- Photos are resized in the browser before upload. The server stores a small JPEG thumbnail, not the original photo.
- Clearing browser data removes the device id, so that device's history can no longer be opened.

## Model

The backend looks for the model in this order:

1. `model/model.h5` (or the path in `MODEL_PATH`), if it exists.
2. `model/.cache/model_keras3_compatible.h5`, the bundled copy (Keras 3 compatible).

It has 6 classes: Bacterial Blight, Blast, Brown Spot, Healthy, Sheath Rot, Tungro. The input size is read from the model.

Disease names and English guidance are in `backend/app/disease_info.py`. Marathi and Hindi versions are in `frontend/src/i18n/diseases.js`. If you change a class name or add a class, update both.

## Run the API

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:

| Method | Path | Notes |
|---|---|---|
| GET | `/health` | Status and whether the model is loaded |
| POST | `/predict` | Form field `file`. Send `X-Device-ID` to save the scan |
| GET | `/scans` | Your scans (needs `X-Device-ID`). `limit` and `offset` |
| GET | `/scans/{id}` | One scan with full guidance (needs `X-Device-ID`) |
| GET | `/scans/{id}/thumbnail` | JPEG thumbnail (needs `X-Device-ID`) |
| DELETE | `/scans/{id}` | Delete your scan (needs `X-Device-ID`) |
| GET | `/stats` | Public totals, class counts, daily counts |

Environment variables:

```text
MODEL_PATH=../model/model.h5                       # optional; relative to backend/
DATABASE_PATH=data/agrivision.db                   # optional; relative to backend/
ALLOWED_ORIGINS=http://localhost:5173              # comma-separated frontend origins
MAX_UPLOAD_BYTES=10485760                          # optional
```

## Run the web app

```bash
cd frontend
npm install
cp .env.example .env              # set VITE_API_BASE_URL if the API is elsewhere
npm run dev
```

Open `http://localhost:5173`.

Weather uses [Open-Meteo](https://open-meteo.com/), which needs no API key. The dashboard uses the browser's location when permission is granted and falls back to Kalyan, Maharashtra.

## Run the Streamlit app

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

**Frontend (Vercel):** root directory `frontend`, build `npm run build`, output `dist`, with `VITE_API_BASE_URL=https://your-api.onrender.com`.

**Backend (Render):** `backend/render.yaml` is preconfigured. Set `ALLOWED_ORIGINS` to your frontend URL.

Scan history is stored in SQLite. On Render, attach a **persistent disk** and point `DATABASE_PATH` at it (for example `/var/data/agrivision.db`). Without a persistent disk, history is lost on every redeploy.
