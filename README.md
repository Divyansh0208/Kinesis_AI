<p align="center">
  <h1 align="center">🏋️ Kinesis AI</h1>
  <p align="center">
    <strong>AI-Powered Movement Intelligence for Safer, Smarter Fitness</strong>
  </p>
  <p align="center">
    Webcam in → 33-point 3D pose estimation → real-time form scoring → injury-risk prediction → adaptive coaching (voice, diet, yoga) → gamified dashboard
  </p>
  <p align="center">
    <em>Built for Smart India Hackathon 2026 · PS #26196 · Theme: Fitness & Sports · Org: AICTE/MIC · Team INOVE8</em>
  </p>
</p>

---

## ✨ Features

### 🎯 Real-Time Pose Detection & Exercise Analysis
- **33-point 3D pose estimation** via MediaPipe Pose in the browser
- Real-time **rep counting** with state-machine logic (pushups, squats, jumping jacks)
- **Form scoring** (0–100) based on joint angles, body alignment, and range of motion
- Instant corrective **feedback overlays** on the webcam feed.

### ⚠️ Injury Risk Prediction Engine
- **Session-level fatigue drift** — compares form score of the first third vs. last third of a session's reps to catch technique breakdown as it happens
- **Cross-session trend** — rolling 30-day average form score per exercise, flags compounding decline before it becomes an injury
- Returns a `risk_level` (low/moderate/high), a 0–100 `risk_score`, a plain-language note, and a corrective drill per exercise type
- Every assessment is logged (`InjuryRiskLog`) for history and trend tracking

### 🏆 Gamification Engine
- **XP = effort (reps + duration) × form-quality multiplier** — sloppy volume earns less than clean technique
- 10-level XP curve with day-based streak tracking (breaks on a >1 day gap)
- 7 badges: first workout, streak milestones, form perfectionist, level 5, century club, and more
- Global **leaderboard**, sorted by XP

### 🔐 Firebase Authentication
- Email/password **and** Google sign-in, handled client-side by the Firebase JS SDK
- Server verifies the Firebase **ID token** on every login/register call (`firebase_admin`) — no passwords ever touch the Flask backend
- Auto-provisions a local `User` row on first sign-in (unique username generated from the Firebase display name/email), and auto-links a pre-Firebase account by matching email
- Session management via Flask-Login after token verification

### 🧘 AI Yoga Planner
- Personalized yoga sessions based on mood, goal, duration, and mobility level
- **25+ pose database** with images, Sanskrit names, difficulty ratings, and step-by-step cues
- Plans generated via **Ollama** (local LLM) with Gemini cloud fallback
- Pose-ID normalization so LLM output always maps to the correct image

### 🥗 AI Diet Planner
- Personalized meal plans considering age, weight, goals, dietary preferences, and allergies
- Structured JSON output with macros, meal breakdowns, and grocery lists
- Supports reasoning models (DeepSeek-R1, QwQ) with automatic `<think>` tag stripping and a diet-preference-aware fallback plan

### 🗣️ Bilingual Voice Assistant
- **Hindi / English / Hinglish** voice chatbot powered by **Sarvam AI**
- Speech-to-Text → LLM chat → Text-to-Speech pipeline (streaming & legacy modes)
- TTS-optimized output (no markdown, natural pauses, Devanagari script for Hindi)
- Text-only fallback when microphone is unavailable
- Scoped to fitness-coaching only — the assistant identifies itself as the Kinesis fitness coach and stays in-domain (form, injury-risk, diet, yoga, sports, app navigation) rather than answering general-purpose questions

### 💪 AI Workout Planner
- Custom 4-week progressive workout plans adapted to fitness level, equipment, and physical limitations
- Powered by **Google Gemini** (cloud) with **Ollama** local fallback
- Accessibility-aware — respects constraints like "seated-only" or injury accommodations

### 📊 Gamified Dashboard
- Workout streaks, total calories burned, average duration stats
- 30-day workout history charts (Chart.js)
- Data export / import / backup / restore via JSON

### 🏃 Google Fit Integration
- OAuth 2.0 flow to connect Google Fit
- Reads activity, body, and heart-rate data from Google Fitness APIs
- Domain-mismatch auto-correction for seamless local OAuth

---

## 🏗️ Architecture

```
┌──────────────┐     ┌────────────────────────────────────────────┐
│   Browser    │     │                Flask Server                 │
│              │     │                                              │
│  MediaPipe   │────▶│  routes.py  (all page + API routes)         │
│  Pose (JS)   │     │     ├── pose_detection.py                   │
│              │     │     ├── injury_risk_engine.py                │
│  Firebase    │────▶│     ├── firebase_init.py (token verify)     │
│  Auth (JS)   │     │     ├── gamification.py                     │
│              │     │     ├── gemini.py                           │
│  Bootstrap 5 │     │     ├── yoga_service.py                     │
│  Chart.js    │     │     ├── diet_service.py                     │
│              │     │     ├── voice_service.py                    │
│              │     │     └── google_fit_service.py               │
└──────────────┘     │                                              │
                      │  models.py  (User, Workout, UserStats,      │
                      │              InjuryRiskLog)                 │
                      │  extensions.py  (db, login_manager)         │
                      └──────────┬───────────────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┬───────────────┐
              ▼                  ▼                  ▼               ▼
        SQLite /           Ollama (local)     Google Gemini    Firebase Auth
        PostgreSQL         LLM Server         (cloud API)      (Admin SDK)
                                               Sarvam AI
                                               Google Fit API
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask, SQLAlchemy, Flask-Login, Flask-Session, Gunicorn |
| **Auth** | Firebase Authentication (email/password + Google), `firebase-admin` server-side token verification |
| **Database** | SQLite (dev) → PostgreSQL (prod) |
| **Computer Vision** | OpenCV, MediaPipe Pose (browser-side), NumPy |
| **AI / LLM** | Ollama (local, default) + Google Gemini (cloud fallback) |
| **Voice** | Sarvam AI (STT: saaras:v3, Chat: sarvam-105b, TTS: bulbul:v3) |
| **Fitness Data** | Google Fit API (OAuth 2.0) |
| **Frontend** | Bootstrap 5, Chart.js, Jinja2 Templates, PWA-ready |
| **Deployment** | Procfile (Railway / Heroku), runtime.txt (Python 3.x) |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Ollama** installed and running ([ollama.com](https://ollama.com)) — the app auto-starts it if found in PATH
- A **Firebase project** with Email/Password and Google sign-in enabled (Firebase Console)
- *(Optional)* Google Gemini API key for cloud LLM fallback
- *(Optional)* Sarvam AI API key for voice assistant
- *(Optional)* Google Cloud OAuth credentials for Google Fit

### Installation

```bash
# Clone the repository
git clone https://github.com/Divyansh0208/Kinesis_AI.git
cd Kinesis_AI

# Create a virtual environment
python -m venv env
source env/bin/activate        # Linux/macOS
env\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Pull a local LLM model (recommended)
ollama pull llama3.2
```

### Firebase Setup

1. Create a project at [console.firebase.google.com](https://console.firebase.google.com), enable **Authentication → Email/Password** and **Google** providers.
2. Generate a service-account key: **Project Settings → Service Accounts → Generate new private key**. Save the JSON somewhere local (not in the repo) and point `FIREBASE_CREDENTIALS_PATH` at it.
3. From **Project Settings → General → Your apps**, grab the web app config values for `FIREBASE_API_KEY`, `FIREBASE_AUTH_DOMAIN`, `FIREBASE_PROJECT_ID`, `FIREBASE_APP_ID`.

### Configuration

```bash
# Copy the example env file and fill in your keys
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `SESSION_SECRET` | Yes | Flask session secret key |
| `FIREBASE_CREDENTIALS_PATH` | Yes | Path to the Firebase service-account JSON (server-side token verification) |
| `FIREBASE_API_KEY` | Yes | Firebase web app config (public, safe to expose to browser) |
| `FIREBASE_AUTH_DOMAIN` | Yes | Firebase web app config |
| `FIREBASE_PROJECT_ID` | Yes | Firebase web app config |
| `FIREBASE_APP_ID` | Yes | Firebase web app config |
| `DATABASE_URL` | No | Defaults to `sqlite:///kinesis.db` |
| `GOOGLE_API_KEY` | No | Google Gemini API key (cloud fallback) |
| `SARVAM_API_KEY` | No | Sarvam AI key for voice assistant |
| `GOOGLE_CLIENT_ID` | No | OAuth client ID for Google Fit |
| `GOOGLE_CLIENT_SECRET` | No | OAuth client secret for Google Fit |
| `GOOGLE_REDIRECT_URI` | No | Defaults to `http://localhost:5000/oauth2callback` |
| `GEMINI_MODEL` | No | Override default Gemini model (e.g. `models/gemini-3.6-flash`) |
| `PORT` | No | Server port, defaults to `5000` |

### Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🔐 Authentication Flow

1. Frontend (`login.html` / `register.html`) uses the **Firebase JS SDK** to sign the user in with email/password or Google, and gets back a Firebase **ID token**.
2. The token is POSTed to `/login` or `/register` as `{"idToken": "..."}`.
3. Flask verifies the token server-side via `firebase_admin.auth.verify_id_token` (`firebase_init.py`) — invalid/expired tokens are rejected with 401.
4. On first sign-in, a local `User` row is auto-created (`firebase_uid`, auto-generated unique `username`, `email`); a pre-Firebase account is auto-linked if its email matches.
5. `flask_login.login_user()` starts the session; all `/api/*` and page routes are gated with `@login_required` from there on.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/register` | Create/link account from a verified Firebase ID token |
| `POST` | `/login` | Sign in with a verified Firebase ID token |
| `GET`  | `/logout` | End session |
| `POST` | `/api/complete-session` | Save a finished workout session, run injury-risk assessment, award XP/streak/badges |
| `GET`  | `/api/leaderboard` | Top users by XP |
| `POST` | `/api/analyze-pose` | Real-time pose analysis from landmark data |
| `POST` | `/api/fitness-chat` | AI fitness Q&A chatbot |
| `POST` | `/api/generate-yoga-plan` | Generate personalized yoga session |
| `POST` | `/api/generate-diet-plan` | Generate personalized diet plan |
| `POST` | `/api/voice/process` | Streaming voice assistant (audio → text → LLM → TTS) |
| `POST` | `/api/voice/process_legacy` | Non-streaming voice assistant fallback |
| `POST` | `/api/voice/process_text` | Text-only voice assistant (no mic) |
| `POST` | `/api/voice/clear` | Clear voice chat history |
| `GET`  | `/api/dashboard-stats` | 30-day workout statistics for charts |
| `POST` | `/api/update-profile` | Update fitness level / goals |
| `GET`  | `/api/export-data` | Export user data as JSON |
| `POST` | `/api/import-data` | Import user data from JSON |
| `GET`  | `/api/backup-data` | Create data backup |
| `POST` | `/api/restore-data` | Restore from backup |
| `POST` | `/api/clear-data` | Clear user data |
| `GET`  | `/api/health-check` | Server health status |
| `GET`  | `/api/version` | App version info |
| `GET`  | `/api/docs` | API documentation |
| `GET`  | `/authorize/google-fit` | Start Google Fit OAuth flow |
| `GET`  | `/oauth2callback` | Google Fit OAuth callback |

---

## 📁 Project Structure

```
kinesis-ai/
├── app.py                    # Flask app factory, Ollama auto-start
├── routes.py                 # All page routes and API endpoints
├── models.py                 # SQLAlchemy models (User, Workout, UserStats, InjuryRiskLog)
├── extensions.py             # Shared db & login_manager instances
├── firebase_init.py          # Firebase Admin SDK init + ID token verification
├── injury_risk_engine.py     # Fatigue-drift + 30-day trend injury risk scoring
├── gamification.py           # XP, levels, streaks, badges, leaderboard
├── gemini.py                 # Gemini + Ollama LLM helpers (workout, chat)
├── pose_detection.py         # PoseAnalyzer: pushup, squat, jumping jack
├── yoga_service.py           # AI yoga plan generation + 25-pose database
├── diet_service.py           # AI diet plan generation
├── voice_service.py          # Sarvam AI bilingual voice pipeline
├── google_fit_service.py     # Google Fit OAuth + data fetching
├── templates/                # Jinja2 HTML templates
│   ├── base.html             # Base layout
│   ├── index.html            # Landing page
│   ├── dashboard.html        # Gamified stats dashboard
│   ├── exercise_analysis.html    # Real-time pose detection UI
│   ├── workout_planner.html      # AI workout plan generator
│   ├── yoga.html              # AI yoga session planner
│   ├── diet.html              # AI diet plan generator
│   ├── voice_assistant.html      # Bilingual voice chatbot
│   ├── login.html             # Firebase login page
│   └── register.html          # Firebase registration page
├── static/                   # CSS, JS, images, yoga pose images
├── requirements.txt           # Python dependencies
├── .env.example                # Environment variable template
├── Procfile                    # Deployment entrypoint
├── runtime.txt                 # Python version for deployment
└── docs/                        # Project documentation (PRD, architecture, workflow)
```

---

## 🤖 AI Model Fallback Strategy

Kinesis AI is designed to work **offline-first** with graceful cloud fallback:

1. **Ollama (Local)** — Default. Auto-detects available models (`llama3.2` → `llama3` → `mistral` → `gemma` → `tinyllama`). Auto-starts the Ollama server if installed. Now has a real timeout on the fallback path so a slow reasoning model can't hang a request indefinitely.
2. **Google Gemini (Cloud)** — Used when Ollama is unavailable or as explicit override. Requires `GOOGLE_API_KEY`.
3. **Mock/Template** — Hardcoded fallback responses when both LLM backends are offline.

Note: the bilingual voice assistant runs on **Sarvam AI** (cloud) rather than Ollama, since Sarvam's models are purpose-built for Hindi/English/Hinglish speech. This is a deliberate exception to the local-first default for this one feature.

---

## 🚧 Known Gaps

- `sports_tracker.py` (shuttle runs, jump-rope cadence, agility ladder) — not yet built.
- `coach_dashboard.py` (school/batch-level view) — not yet built.
- `/api/leaderboard` and badge data have working backend routes, but no dashboard UI consumes them yet (streak/XP stats do already show on the dashboard).
- Accessibility mode (chair/bed-bound variants, high-contrast UI, full voice-first navigation) is not yet implemented as a first-class mode.

---

## 👥 Team INOVE8

Built with ❤️ for **Smart India Hackathon 2026**

---

## 📄 License

This project is developed as part of Smart India Hackathon 2026 (PS #26196).
