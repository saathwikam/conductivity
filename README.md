# Ionic SL

Ionic SL is a dual-phase lithium battery electrolyte conductivity project with:

- a FastAPI backend that routes solid and liquid chemistry inputs through separate preprocessing paths
- a React frontend with a cyber-lab UX, portal selection, scanner loading state, and 3D reveal panel
- dataset-backed prediction fallback logic while model weights are still being prepared

## Project Structure

```text
new_ionic_SL/
  backend/
    app/
    requirements.txt
    run.py
  frontend/
    src/
    package.json
  data/
    solid_electrolyte_500.csv
    liquid_electrolyte_500.csv
  models/
    alignn_solid.pth
    alignn_liquid.pth
```

## Backend

The backend exposes:

- `GET /health`
- `POST /predict`

Example request:

```json
{
  "phase": "liquid",
  "formula": "LiPF6 in EC/EMC"
}
```

Example response fields:

- `prediction`
- `graph_stats`
- `matched_record`
- `phase`
- `narrative`

The current implementation:

- uses the trained solid ALIGNN checkpoint for solid inference when `models/alignn_solid.pth`, `alignn310`, and `MP_API_KEY` are available
- uses the cleaned datasets as a fallback when trained runtime dependencies are not available
- builds lightweight graph statistics for solids and liquids
- includes a liquid preprocessing pipeline that maps formulations to component structure metadata and graph-ready records
- is ready to switch to `models/alignn_solid.pth` and `models/alignn_liquid.pth` later

## Frontend

The frontend provides:

- stage 1 portal cards for solid and liquid
- stage 2 glowing chemistry input
- stage 3 molecular scanner overlay
- stage 4 result reveal with NGL viewer and conductivity gauge

## Run Locally

Backend:

```powershell
cd backend
pip install -r requirements.txt
python run.py
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Deployment

Recommended split deployment:

- frontend: Vercel or Render Static Site
- backend: Render Web Service

Important notes:

- set `VITE_API_BASE_URL` in the frontend deployment to your backend URL
- the hosted backend can run the trained liquid model from `models/liquid_model_training/best_liquid_model.pt`
- the solid ALIGNN path still depends on the heavier ALIGNN runtime and Materials Project access; without that runtime, hosted solid predictions fall back to the dataset path

This repo includes:

- [render.yaml](./render.yaml) for Render deployment
- [frontend/.env.example](./frontend/.env.example) showing the frontend API variable
