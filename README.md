# AI Emergency Healthcare Command Centre

An educational demonstration of an emergency healthcare command centre. It combines a Streamlit dashboard with a FastAPI service for emergency intake, AI-assisted priority classification, ambulance dispatch, hospital recommendations, and simulated patient-vitals telemetry.

> **Disclaimer:** This is a software demonstration, not a medical device or clinical decision-support system. Its classifications, recommendations, routes, and simulated data must not be used to make real-world medical or emergency-response decisions.

## Features

- Emergency case intake and priority classification
- Hospital recommendations based on emergency details and hospital resources
- Ambulance dispatch with estimated travel times
- Hospital resource display and updates
- Patient vitals history and simulated telemetry
- SQLite database initialized and seeded by the backend
- FastAPI interactive API documentation

## Technology

- Python
- FastAPI and Uvicorn
- Streamlit
- SQLAlchemy and SQLite
- scikit-learn, pandas, NumPy, Plotly, and PyDeck

## Run locally

Use Python 3.10 or newer. From the project root, create and activate a virtual environment, then install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start both the FastAPI backend and Streamlit dashboard:

```powershell
python run.py
```

Open the dashboard at <http://localhost:8501>. The API and interactive API docs are available at <http://127.0.0.1:8000> and <http://127.0.0.1:8000/docs>.

The dashboard can be started separately with:

```powershell
streamlit run frontend/app.py
```

When running the dashboard separately, start the backend in another terminal:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Set `API_BASE_URL` if the backend is not available at the local default (`http://127.0.0.1:8000/api`).

## API overview

The API endpoints are grouped under `/api`:

| Group | Example endpoints |
| --- | --- |
| Emergencies | `GET /api/emergencies/`, `POST /api/emergencies/`, `GET /api/emergencies/{emergency_id}` |
| Dispatch | `GET /api/dispatch/recommend_hospital/{emergency_id}`, `POST /api/dispatch/auto_dispatch/{emergency_id}` |
| Hospitals | `GET /api/hospitals/`, `PUT /api/hospitals/{hospital_id}/resources` |
| Vitals | `POST /api/vitals/`, `GET /api/vitals/emergency/{emergency_id}`, `POST /api/vitals/simulate_next/{emergency_id}` |

See <http://127.0.0.1:8000/docs> for request schemas and complete interactive documentation while running locally.

## Deploy to Render

The repository includes a [Render Blueprint](./render.yaml) that defines separate web services for the API and Streamlit dashboard.

1. Push this repository to GitHub.
2. In Render, choose **New → Blueprint** and connect this repository.
3. Review the two services and deploy the Blueprint.
4. Confirm that the frontend service's `API_BASE_URL` environment variable points to the deployed API URL followed by `/api`. Update it if Render assigns a different service URL.

The included setup uses SQLite. Render's local filesystem is not durable across deploys or instance replacement, so this configuration is suitable for a demonstration rather than persistent production data. Use a managed persistent database and configure its connection securely for any production deployment.

## Project layout

```text
backend/
  app/
    ai_engines/     # Priority classification, recommendations, and routing
    db/             # SQLAlchemy models, database setup, and seed data
    iot/            # Simulated patient-vitals generation
    routers/        # FastAPI endpoints
    main.py         # FastAPI application
frontend/
  app.py            # Streamlit dashboard
  logo.png
render.yaml         # Render Blueprint
run.py              # Local launcher for backend and frontend
requirements.txt
```
