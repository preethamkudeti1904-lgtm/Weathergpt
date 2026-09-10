# WeatherGPT
> **Conversational AI for Weather Forecasting, Alerts & Climate Information**  
> *Built for India Meteorological Department (IMD) / Ministry of Earth Sciences (MoES) - Smart India Hackathon (SIH)*

---

## 🌟 Overview

**WeatherGPT** is a production-style, scientific meteorological intelligence platform. It combines verified real-time weather observations, predictive hourly and 7-day numerical forecasts, standardized IMD early warnings, geospatial satellite imagery, and a **conversational AI agent grounded strictly in live atmospheric observations**.

Designed to serve 8 specialized user personas—from **Farmers** needing crop-specific agro-met advisories to **Disaster Management Authorities** tracking convective squall and flood risks, **Aviation**, **Marine**, and **Researchers**.

---

## 🚀 Key Features

1. **Strictly Grounded WeatherGPT AI**: Natural language meteorological reasoning that validates questions against live weather API data before answering, preventing hallucinations and attributing sources transparently.
2. **Multilingual Architecture**: Native support for 8 Indian languages (English, Hindi, Telugu, Tamil, Kannada, Malayalam, Marathi, Bengali) with centralized translation dictionaries.
3. **Voice Interaction**: Browser SpeechRecognition for query input and SpeechSynthesis for spoken responses.
4. **Interactive Satellite Maps**: Esri World Imagery (High-Resolution Satellite), OpenStreetMap (Road), and CartoDB (Hybrid), paired with temperature isotherm and radar overlays.
5. **Role-Based Personalization**:
   - **🌾 Farmer**: Crop weather advisory, 7-day cumulative rainfall, soil moisture index, spraying windows.
   - **🚨 Disaster Management**: Emergency command post, IMD color-coded stages (Green, Yellow, Orange, Red), flood inundation threat, and SOP checklists.
   - **✈ Aviation**: Flight categories (VFR, MVFR, IFR), surface visibility, crosswinds, and altimeter settings.
   - **🌊 Marine**: Sea state (Beaufort scale), coastal winds, and fishermen warnings.
   - **🔬 Researcher**: Historical climate records, temperature & rainfall trends, CSV and JSON exports.
   - **🌤 General User**: Daily outlook, feels-like temperature, and clothing advice.
6. **IMD Standard Early Warning Grid**: Threshold-driven severe weather alert detection for heavy downpours, thunderstorms, heat waves, strong winds, and dense fog.
7. **Modular NWP Architecture**: Clean abstraction layer prepared for GFS (Global Forecast System) and high-resolution WRF India numerical weather prediction models.
8. **Clean Database Abstraction**: SQLAlchemy 2.0 supporting PostgreSQL for production with automatic SQLite fallback for zero-friction local execution.

---

## 🏗 System Architecture

```
User Query / Voice
        │
        ▼
[ Query Parser & Intent Extractor ]
        │  (Extracts: Intent, Location, Time Window, Persona)
        ▼
[ WeatherService Layer ] ──────────────► [ Real Providers: Open-Meteo / WMO / OpenWeather / IMD ]
        │
        ▼
[ Data Validation & Grounding ]
        │
        ▼
[ Grounded AI Engine (Gemini / OpenAI / Heuristic) ]
        │
        ▼
Natural Language Response (Fact Grounded + Source Attribution + Advisory)
```

---

## 💻 Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Lucide Icons, Leaflet GIS.
- **Backend**: Python 3, FastAPI, Uvicorn, Pydantic v2, HTTPX.
- **Database**: PostgreSQL / SQLite (via SQLAlchemy 2.0 ORM).
- **Meteorology**: Open-Meteo REST & WMO Standards (Real Data), OpenWeatherMap API, IMD hooks.
- **Artificial Intelligence**: Google Gemini (`google-genai`), OpenAI API, Grounded Meteorological Semantic Engine.

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python run.py
```
The FastAPI backend will start at `http://127.0.0.1:8080` (Interactive API docs at `http://127.0.0.1:8080/api/docs`).

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The Vite development server will start at `http://localhost:5173`.

---

## 🔑 Environment Variables (`.env`)

Copy `.env.example` to `.env` in the root directory:

```env
# Application
APP_NAME=WeatherGPT
API_V1_STR=/api
SECRET_KEY=your-secure-secret-key

# Database (PostgreSQL in production; SQLite fallback default)
DATABASE_URL=sqlite:///./weathergpt.db

# Weather Provider ("open-meteo" works out-of-the-box without keys)
WEATHER_PROVIDER=open-meteo
OPENWEATHER_API_KEY=

# AI Provider (Optional: Gemini or OpenAI API keys)
GEMINI_API_KEY=
OPENAI_API_KEY=

# Development Controlled Demo Mode (False = Real Live APIs)
DEMO_MODE=False
```

---

## 🛰 Numerical Weather Prediction (NWP) / GFS / WRF Architecture

The backend includes a dedicated `NWPService` (`backend/app/weather/nwp_service.py`):
- Exposes `/api/nwp/status`, `/api/nwp/gfs`, and `/api/nwp/wrf`.
- Designed for ingesting Gridded Binary (GRIB2) and NetCDF atmospheric files from IMD's high-resolution WRF (3 km) model runs and NOAA GFS (0.25° grid).

---

## 🔒 Security & Quality Standards

- No API keys or secrets are exposed in the frontend client.
- Password hashing powered by `bcrypt` / `passlib`.
- Stateless token authentication with JSON Web Tokens (JWT).
- Input sanitization and CORS security policies enabled.
- Transparent attribution: all weather responses display the data provider and update timestamp.

---

## 📄 License
Developed for the **India Meteorological Department (IMD) / Ministry of Earth Sciences (MoES)**.
