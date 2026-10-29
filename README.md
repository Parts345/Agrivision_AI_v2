<<<<<<< HEAD
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
=======
# AgriVision AI Smart Farming Platform

Startup-style rice disease detection platform with a React/Vite frontend and FastAPI TensorFlow backend.

## What Is Included

- `frontend/` React + Vite + Tailwind CSS + Framer Motion + Recharts
- `backend/` FastAPI REST API with CORS and `POST /predict`
- Real Keras/TensorFlow model loading from `model/model.h5`
- Keras 3 compatibility patch for legacy CBAM Lambda layers
- Drag/drop image upload, camera upload, preview, toast states, animated results
- Dashboard, weather UI, disease analytics, recommendations, chatbot placeholder
- Deployment files for Vercel and Render

## Model

The backend defaults to:

```text
model/model.h5
```

To use another file, set:

```text
MODEL_PATH=C:\Users\Ushank Rajeshirke\Downloads\rice_disease_cbam_transformer_model2.h5
```

Class labels are centralized in:

```text
backend/app/disease_info.py
```

The current model in this workspace appears to use 6 outputs:

```text
Bacterial Blight, Blast, Brown Spot, Healthy, Sheath Rot, Tungro
```

If your trained model has 5 classes, remove or adjust the extra class in `CLASS_NAMES`.

## Run Backend

```bash
cd backend
python -m venv .venv  or py -3.11 -m venv .venv
.venv\Scripts\activate
>>>>>>> origin/main
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

<<<<<<< HEAD
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
=======
Health check:

```text
http://localhost:8000/health
```

Prediction endpoint:

```text
POST http://localhost:8000/predict
form-data key: file
```

## Run Frontend
>>>>>>> origin/main

```bash
cd frontend
npm install
<<<<<<< HEAD
cp .env.example .env              # set VITE_API_BASE_URL if the API is elsewhere
npm run dev
```

Open `http://localhost:5173`.

Weather uses [Open-Meteo](https://open-meteo.com/), which needs no API key. The dashboard uses the browser's location when permission is granted and falls back to Kalyan, Maharashtra.

## Run the Streamlit app

```bash
pip install -r requirements.txt
streamlit run app.py
=======
npm run dev
```

Open:

```text
http://localhost:5173
```

Create `frontend/.env` when deploying or changing backend URL:

```text
VITE_API_BASE_URL=http://localhost:8000
>>>>>>> origin/main
```

## Deployment

<<<<<<< HEAD
**Frontend (Vercel):** root directory `frontend`, build `npm run build`, output `dist`, with `VITE_API_BASE_URL=https://your-api.onrender.com`.

**Backend (Render):** `backend/render.yaml` is preconfigured. Set `ALLOWED_ORIGINS` to your frontend URL.

Scan history is stored in SQLite. On Render, attach a **persistent disk** and point `DATABASE_PATH` at it (for example `/var/data/agrivision.db`). Without a persistent disk, history is lost on every redeploy.
=======
### Frontend on Vercel

Set project root to `frontend`, build command `npm run build`, output directory `dist`.

Environment variable:

```text
VITE_API_BASE_URL=https://your-backend.onrender.com
```

### Backend on Render or Railway

Use `backend/requirements.txt`.

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Environment variables:

```text
MODEL_PATH=../model/model.h5
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

For production, upload the model file with the backend or store it in a persistent/private artifact location and set `MODEL_PATH`.
>>>>>>> origin/main
