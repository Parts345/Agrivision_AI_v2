# AgriVision

Rice leaf disease screening for farmers and agronomists. Upload or photograph a rice leaf and get the most likely disease, the confidence for each class, and guidance on symptoms, causes, prevention, and treatment.

## Features

- Check a leaf from a photo or the phone camera
- Results in English, Marathi, and Hindi
- Scan history per device (no accounts)
- Public dashboard with scan totals and class counts
- Light and dark themes

## Project structure

```text
frontend/   React + Vite web app
backend/    FastAPI API with TensorFlow inference and SQLite scan history
model/      Trained model file (model/model.h5)
app.py      Streamlit version of the app
utils/      Helpers for the Streamlit version
```

## Model

Place the trained model at:

```text
model/model.h5
```

The backend uses `model/model.h5` by default, or another path supplied through
`MODEL_PATH`. If the default file is absent, it falls back to the bundled
Keras 3-compatible copy at `model/.cache/model_keras3_compatible.h5`. Model
files are not excluded by `.gitignore`, so `model/model.h5` can be tracked and
uploaded to GitHub.

The model has 6 classes, in this order:

```text
Bacterialblight, Blast, Brownspot, Healthy, Sheathrot, Tungro
```

Class names and English disease guidance are in `backend/app/disease_info.py`. Marathi and Hindi text is in `frontend/src/i18n/diseases.js`. If you change a class, update both files.

## Backend setup

Requires Python 3.11 (TensorFlow does not support Python 3.13 or newer yet).

Windows (PowerShell):

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

macOS / Linux:

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check that the server is running by opening `http://localhost:8000/health`.

### API endpoints

| Method | Path | Notes |
|---|---|---|
| GET | `/health` | Server status and whether the model is loaded |
| POST | `/predict` | Form field `file`. Send `X-Device-ID` to save the scan to history |
| GET | `/scans` | Scans for this device. Supports `limit` and `offset` |
| GET | `/scans/{id}` | One scan with full guidance (needs `X-Device-ID`) |
| GET | `/scans/{id}/thumbnail` | JPEG thumbnail (needs `X-Device-ID`) |
| DELETE | `/scans/{id}` | Delete one of this device's scans (needs `X-Device-ID`) |
| GET | `/stats` | Public totals, class counts, and daily counts |

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `MODEL_PATH` | `model/model.h5` | Path to the model file. Relative paths start from `backend/` |
| `DATABASE_PATH` | `backend/data/agrivision.db` | SQLite file for scan history |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | Comma-separated frontend URLs allowed by CORS |
| `MAX_UPLOAD_BYTES` | `10485760` (10 MB) | Largest image the API accepts |

## Frontend setup

Requires Node.js 20 or 22 (LTS).

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

To point the frontend at a different API, create `frontend/.env`:

```text
VITE_API_BASE_URL=http://localhost:8000
```

Weather on the dashboard uses [Open-Meteo](https://open-meteo.com/), which needs no API key. It uses the browser's location when permitted and otherwise falls back to Kalyan, Maharashtra.

## Streamlit version

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Privacy

- No accounts. The browser creates a random device ID and sends it with each scan.
- Scan history and thumbnails are returned only to the device that created them.
- The dashboard shows totals and class counts across all users, never device IDs.
- Photos are resized in the browser before upload. The server stores a small thumbnail, not the original photo.
- Clearing browser data removes the device ID, so that history can no longer be opened.

## Deployment

**Frontend (Vercel):** set the root directory to `frontend`, the build command to `npm run build`, and the output directory to `dist`. Add the environment variable:

```text
VITE_API_BASE_URL=https://your-backend-url
```

**Backend (Render):** `backend/render.yaml` is preconfigured. Set `ALLOWED_ORIGINS` to your frontend URL, and upload `model.h5` to the service (or set `MODEL_PATH` to its location).

Scan history is stored in SQLite. On Render, attach a persistent disk and set `DATABASE_PATH` to a path on it (for example `/var/data/agrivision.db`). Without a persistent disk, history is lost on every redeploy.

## Limitations

This is a screening tool, not a diagnosis. Results depend on photo quality and the stage of the disease. For severe or spreading disease, confirm with a local agriculture officer or Krishi Vigyan Kendra.