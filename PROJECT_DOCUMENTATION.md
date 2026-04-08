# PROJECT DOCUMENTATION

## 1. Project Title

**Ionic SL: Dual-Phase Lithium Electrolyte Conductivity Prediction Platform**

---

## 2. Project Summary

Ionic SL is a dual-mode web application designed to predict ionic conductivity for lithium battery electrolytes. The project supports two different electrolyte classes:

- **Solid Electrolytes**
- **Liquid Electrolytes**

The application provides a modern cyber-lab styled frontend and a FastAPI backend. Users select a phase, enter a chemistry-based input, and receive a conductivity prediction, graph statistics, and the closest matched dataset record.

At its current stage, the project is a strong working prototype. It uses curated datasets and phase-aware matching logic rather than final trained `.pth` model inference.

---

## 3. Objectives

The main objectives of the project are:

- to build a dual-phase electrolyte prediction interface
- to separate solid-state and liquid-state chemistry workflows
- to provide a clean and engaging user experience
- to use curated electrolyte datasets to support prediction
- to prepare a structure that can later be extended to real machine learning model inference

---

## 4. Project Folder Structure

Main project folder:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL`

Important contents:

```text
new_ionic_SL/
  backend/
    app/
      routers/
      schemas/
      services/
      utils/
      main.py
    requirements.txt
    run.py
  frontend/
    src/
      components/
      lib/
      App.jsx
      main.jsx
      styles.css
    index.html
    package.json
    tailwind.config.js
    vite.config.js
  data/
    solid_electrolyte_500.csv
    liquid_electrolyte_500.csv
    processed/
  models/
  README.md
  PROJECT_DOCUMENTATION.md
  .gitignore
  .python-version
```

---

## 5. Technology Stack

### Frontend

- React 18
- Vite
- Tailwind CSS
- Framer Motion
- Lucide React Icons

### Backend

- FastAPI
- Uvicorn
- Pydantic
- Pandas
- NumPy

### Planned Future ML Stack

- PyTorch
- DGL
- Pymatgen
- RDKit

These advanced chemistry and graph libraries are part of the long-term design, but they are not required for the cleaned running prototype version.

---

## 6. Datasets Used

The project currently uses two cleaned datasets with 500 rows each.

### Solid Electrolyte Dataset

File:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\data\solid_electrolyte_500.csv`

Main columns:

- `phase`
- `formula`
- `temperature_c`
- `ionic_conductivity_s_cm`
- `log10_ionic_conductivity`
- `family`
- `chemical_family`
- `source_doi`

Purpose:

- used for solid electrolyte matching and conductivity prediction fallback

### Liquid Electrolyte Dataset

File:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\data\liquid_electrolyte_500.csv`

Main columns:

- `phase`
- `experiment_id`
- `formulation`
- `temperature_c`
- `pc_g`
- `ec_g`
- `emc_g`
- `lipf6_g`
- `ionic_conductivity_s_cm`
- `ln_ionic_conductivity`

Purpose:

- used for liquid electrolyte formulation matching and conductivity prediction fallback

---

## 7. Functional Workflow

The project flow is divided into four main stages.

### Stage 1: Portal

The home screen displays two portal cards:

- `Solid Electrolyte`
- `Liquid Electrolyte`

The user first selects one phase.

### Stage 2: Lab Input

The input screen changes depending on the selected phase.

Solid mode expects:

- a solid electrolyte chemical formula
- example: `Li7La3Zr2O12`

Liquid mode expects:

- a liquid electrolyte formulation string
- example: `LiPF6 in EC/EMC`

### Stage 3: Scanner

When the user submits the input:

- the frontend shows a full-screen scanner overlay
- the request is sent to the backend
- the backend performs validation and matching

### Stage 4: Reveal

The result screen displays:

- predicted conductivity value
- graph statistics
- matched dataset record
- a narrative explanation of the result

---

## 8. Backend Architecture

Backend root:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\backend`

### 8.1 Entry Point

File:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\backend\run.py`

Purpose:

- starts the FastAPI application using Uvicorn

### 8.2 FastAPI App Setup

File:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\backend\app\main.py`

Purpose:

- creates the FastAPI app
- enables CORS
- registers routes

Endpoints:

- `GET /health`
- `POST /predict`

---

## 9. Backend Request and Response

Schema file:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\backend\app\schemas\predict.py`

### Request Schema

```json
{
  "phase": "solid or liquid",
  "formula": "user input string"
}
```

### Response Schema

```json
{
  "prediction": 0.0,
  "graph_stats": {},
  "matched_record": {},
  "phase": "solid or liquid",
  "narrative": "text explanation"
}
```

---

## 10. Prediction Service Logic

Core file:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\backend\app\services\predictor.py`

The `PredictionService` is the main backend logic unit.

It performs:

- input cleaning
- phase routing
- input validation
- dataset loading
- exact or nearest match search
- graph statistics generation
- response building

### Solid Prediction Path

When phase is `solid`:

1. check that the input is not liquid-like
2. normalize the formula
3. load the solid dataset
4. search exact formula match
5. if no exact match, find nearest solid formula
6. compute graph statistics
7. return prediction and matched record

### Liquid Prediction Path

When phase is `liquid`:

1. check that the input is not a solid-only formula
2. load the liquid dataset
3. search exact formulation match
4. if no exact match, find nearest liquid formulation
5. compute graph statistics
6. return prediction and matched record

---

## 11. Chemistry Helper Logic

File:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\backend\app\services\chemistry.py`

This file contains chemistry parsing and validation helper functions.

### Main Responsibilities

- parsing solid formulas into elemental composition
- identifying liquid-like input strings
- identifying solid-like formulas
- creating lightweight graph statistics for both phases

### Important Functions

`parse_composition(raw_formula)`

- extracts elements and counts from formulas

`normalize_formula(raw_formula)`

- removes spaces
- optionally uses `pymatgen` if available
- safely falls back if not installed

`is_liquid_like_input(raw_value)`

- detects strings like:
  - `LiPF6 in EC/EMC`
  - `LiPF6 + EC + EMC`

`is_solid_like_formula(raw_value)`

- detects compact solid formulas like:
  - `Li7La3Zr2O12`

`build_solid_graph_stats(formula)`

- returns lightweight solid graph information

`build_liquid_graph_stats(formulation)`

- returns lightweight liquid graph information

---

## 12. Dataset Loading Logic

File:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\backend\app\services\dataset_store.py`

Purpose:

- loads the two cleaned CSV datasets
- uses `lru_cache` so repeated reads are avoided
- creates normalized keys for exact lookup

Main functions:

- `load_solid_dataset()`
- `load_liquid_dataset()`

---

## 13. Frontend Architecture

Frontend root:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\frontend`

### Entry Files

- `index.html`
- `src/main.jsx`
- `src/App.jsx`

### Supporting Files

- `src/styles.css`
- `src/lib/api.js`
- `src/components/ui/PhaseCard.jsx`
- `src/components/ui/ScannerOverlay.jsx`
- `src/components/ui/CountGauge.jsx`

---

## 14. Frontend Screen Behavior

Main app file:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\frontend\src\App.jsx`

### State Variables

- `phase`
- `formula`
- `result`
- `loading`
- `error`

### UI Behavior

#### Portal Screen

- shows the two phase cards
- user chooses solid or liquid mode

#### Input Screen

- displays selected phase heading
- displays chemistry input field
- provides example input button

#### Scanner Overlay

- appears during backend processing
- provides animated loading experience

#### Reveal Section

- shows prediction gauge
- shows graph stats
- shows matched record

The earlier structure viewer was intentionally removed to keep the prototype focused and clean.

---

## 15. Frontend Components

### PhaseCard Component

File:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\frontend\src\components\ui\PhaseCard.jsx`

Purpose:

- displays the selectable portal cards
- provides animation and visual style

### ScannerOverlay Component

File:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\frontend\src\components\ui\ScannerOverlay.jsx`

Purpose:

- creates the animated loading pop-up
- gives the cyber-lab scanner effect

### CountGauge Component

File:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\frontend\src\components\ui\CountGauge.jsx`

Purpose:

- animates the predicted conductivity value
- displays a progress-style gauge

### API Helper

File:

`C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\frontend\src\lib\api.js`

Purpose:

- sends the prediction request to the backend
- handles backend errors and converts them to readable frontend messages

---

## 16. Styling and UX

Main style files:

- `src/styles.css`
- `tailwind.config.js`

Design choices:

- dark mode interface
- cyber-lab feeling
- glassmorphism cards
- neon blue and green lighting accents
- Orbitron font for headings
- Rajdhani font for readable body text
- Framer Motion transitions for interaction

---

## 17. Input Validation Behavior

The project now includes phase mismatch validation.

### Valid Examples

Solid mode:

- `Li7La3Zr2O12`
- `Li2OHBr`

Liquid mode:

- `LiPF6 in EC/EMC`
- `LiPF6 + EC + EMC`

### Invalid Examples

If entered in solid mode:

- `LiPF6 in EC/EMC`

If entered in liquid mode:

- `Li7La3Zr2O12`

These invalid cases now produce readable backend errors instead of misleading predictions.

---

## 18. Current Strengths

- clean frontend and backend separation
- dual-phase prediction design
- curated datasets
- clear user workflow
- working validation logic
- attractive and modern demo-ready interface
- leaner, cleaner code after cleanup

---

## 19. Current Limitations

- prediction is still dataset-driven fallback logic
- real `.pth` model inference is not connected yet
- liquid chemistry parsing is practical but not universal
- graph statistics are simplified representations, not full graph neural network input graphs

---

## 20. Future Improvements

Possible future upgrades:

- integrate trained PyTorch model weights into `models/`
- add real solid crystal graph generation using Pymatgen
- add real molecular graph generation using RDKit
- improve liquid formulation parser for more chemistry formats
- add temperature-aware controls in the frontend
- add model confidence score
- add export/report features

---

## 21. How to Run the Project

### Backend

```powershell
cd "C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\backend"
& "C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt
python run.py
```

Open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

### Frontend

```powershell
cd "C:\Users\rishika akavaram\OneDrive\Documents\new_ionic_SL\frontend"
npm install
npm run dev
```

Open:

- `http://localhost:5173`

---

## 22. Example Test Inputs

### Solid Example

```text
Li7La3Zr2O12
```

### Liquid Example

```text
LiPF6 in EC/EMC
```

Expected output types:

- predicted conductivity value
- graph stats
- matched record

---

## 23. Final Project Status

The project is currently in a stable prototype state. It is suitable for demonstration, explanation, and further extension. The codebase is cleaner now, phase validation has been improved, and unnecessary parts have been removed. The next major milestone would be replacing dataset fallback logic with real trained model inference.

### Updated Solid Status

The solid module now includes a trained ALIGNN checkpoint:

- `models/alignn_solid.pth`

Backend behavior for solid mode is now:

- if the trained checkpoint, the `alignn310` environment, and `MP_API_KEY` are available, the backend runs true solid ALIGNN inference through the helper script:
  - `training/scripts/predict_solid_alignn.py`
- otherwise it falls back to the earlier dataset-based matching path

### Liquid Status

The liquid side now has a preprocessing foundation based on:

- `training/liquid_component_map.json`
- `training/scripts/prepare_liquid_graph_data.py`
- `backend/app/services/liquid_preprocessor.py`

This layer parses formulation strings, maps known components to molecular identities and SMILES, and creates graph-ready liquid records that include temperature as an explicit feature.
