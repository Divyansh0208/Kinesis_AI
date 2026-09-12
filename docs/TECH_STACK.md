# Kinesis AI — Tech Stack

## Backend
- **Framework:** Flask (Python 3.8+)
- **Auth/Session:** Flask-Login, Flask-Session
- **ORM:** SQLAlchemy
- **Database:** SQLite (dev) → PostgreSQL (prod)

## Frontend
- **Base:** HTML5, Bootstrap 5, Vanilla JS
- **Charts:** Chart.js (streaks, calories, form-quality, injury-risk trends)
- **Delivery:** PWA (offline-capable core flows)

## Computer Vision
- **Pose detection:** MediaPipe (33-landmark body tracking)
- **Video pipeline:** OpenCV
- **Image utils:** Pillow, NumPy

## AI Layer (dual-path: local-first, cloud fallback)
- **Cloud AI:** Google Gemini API — adaptive workout planning, complex reasoning, fallback for diet/yoga/voice
- **Local AI:** Ollama (Llama 3, Mistral, Gemma) — diet plans, yoga flows, voice coaching; on-device by default for privacy
- **Routing rule:** local Ollama tried first → falls back to Gemini only if no local model is available

## Integrations
- **Auth:** Google OAuthlib (Google Sign-In)
- **Wearables:** Google Fit REST API + wearable sync adapters

## Infra / Deployment considerations
- Modular deployment (single-user → college batch → multi-tenant institutional)
- Webcam as the only required hardware — no proprietary sensors

## Module-to-File Map

| Module | File | Responsibility |
|---|---|---|
| App bootstrap | `app.py` | Application factory + Ollama auto-starter |
| Routing | `routes.py` | Controllers & Blueprints |
| Data models | `models.py` | SQLAlchemy schemas |
| CV pipeline | `pose_detection.py` | OpenCV + MediaPipe landmark extraction |
| Injury engine | `injury_risk_engine.py` | Joint-deviation & fatigue risk scoring |
| Sports tracking | `sports_tracker.py` | Drill & agility tracking |
| Gamification | `gamification.py` | XP, streaks, badges, leaderboards |
| Gemini wrapper | `gemini.py` | Google Gemini API calls |
| Diet logic | `diet_service.py` | Ollama-driven diet + recovery plans |
| Yoga logic | `yoga_service.py` | Ollama-driven yoga/mobility flows |
| Coach view | `coach_dashboard.py` | School/coach aggregate dashboard |
| Wearable sync | `google_fit_service.py` | OAuth + wearable data sync |
| Voice | `voice_service.py` | Bilingual TTS/STT |
| Boot orchestration | `start_app.py` | Cross-platform launcher |
| Views | `templates/` | Jinja2 templates |
| Static assets | `static/` | CSS/JS/PWA manifest |

## Why this stack (rationale)

- **Flask over heavier frameworks:** fast to build for a hackathon timeline, huge Python ML/CV ecosystem compatibility.
- **MediaPipe over building custom pose models:** production-grade, real-time, runs on commodity webcams — no GPU/cloud inference needed for the core CV loop.
- **Ollama local-first:** keeps sensitive health data (body metrics, diet, medical-adjacent info) on-device — core to the privacy-first differentiator, and reduces cloud cost/dependency.
- **Gemini as the "smart fallback":** handles heavier reasoning (adaptive multi-week planning) where local models may underperform, without making it a hard dependency.
- **SQLite → PostgreSQL path:** zero-friction local dev, straightforward prod scaling.
