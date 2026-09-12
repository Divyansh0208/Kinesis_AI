# Kinesis AI — System Architecture

## 1. Architecture Style

Monolithic Flask app (hackathon-appropriate) with clearly separated service modules — structured so each service (CV, injury engine, diet, yoga, voice, gamification) could later be split into microservices if scaling demands it.

## 2. High-Level Component Diagram

```
                         ┌─────────────────────────┐
                         │        Client            │
                         │ Browser / PWA (Bootstrap,│
                         │ Vanilla JS, Chart.js)     │
                         └────────────┬─────────────┘
                                      │ HTTP / WebSocket (webcam frames)
                                      ▼
                         ┌─────────────────────────┐
                         │      Flask App Layer      │
                         │  app.py / routes.py       │
                         │  Flask-Login/Session       │
                         └───────┬───────┬───────────┘
                                 │       │
             ┌───────────────────┘       └───────────────────┐
             ▼                                                ▼
   ┌───────────────────────┐                       ┌───────────────────────┐
   │   CV & Scoring Layer    │                       │     AI Services Layer   │
   │ pose_detection.py       │                       │ gemini.py                │
   │ injury_risk_engine.py   │                       │ diet_service.py           │
   │ sports_tracker.py       │                       │ yoga_service.py           │
   └───────────┬─────────────┘                       │ voice_service.py          │
               │                                      └──────┬──────────┬────────┘
               │                                             │          │
               │                                     ┌───────▼───┐  ┌───▼──────────┐
               │                                     │  Ollama    │  │ Google Gemini │
               │                                     │ (local LLM)│  │ API (cloud)   │
               │                                     └────────────┘  └───────────────┘
               ▼
   ┌───────────────────────┐
   │   Persistence Layer     │
   │ models.py (SQLAlchemy)  │
   │ SQLite (dev) /           │
   │ PostgreSQL (prod)        │
   └───────────┬─────────────┘
               │
               ▼
   ┌───────────────────────┐        ┌────────────────────────┐
   │  Gamification Engine    │        │  Coach Dashboard         │
   │ gamification.py          │◄──────┤ coach_dashboard.py        │
   │ (XP, streaks, badges)    │        │ (batch/institutional view)│
   └───────────────────────┘        └────────────────────────┘

   ┌───────────────────────┐
   │  External Integrations  │
   │ google_fit_service.py    │ ── Google Fit REST API / wearables
   └───────────────────────┘
```

## 3. Layer Responsibilities

| Layer | Responsibility | Key files |
|---|---|---|
| **Client** | Webcam capture, UI rendering, PWA shell, voice UI | `templates/`, `static/` |
| **App layer** | Routing, auth, session mgmt | `app.py`, `routes.py`, `start_app.py` |
| **CV & Scoring** | Pose extraction → form scoring → injury-risk detection → sports drill metrics | `pose_detection.py`, `injury_risk_engine.py`, `sports_tracker.py` |
| **AI Services** | Adaptive plans, diet, yoga, voice — local-first, cloud-fallback | `gemini.py`, `diet_service.py`, `yoga_service.py`, `voice_service.py` |
| **Persistence** | Session/user/score data | `models.py` + SQLite/PostgreSQL |
| **Gamification** | XP, streaks, badges, leaderboards | `gamification.py` |
| **Institutional** | Aggregate batch-level views | `coach_dashboard.py` |
| **Integrations** | Wearable / Google Fit sync | `google_fit_service.py` |

## 4. Key Architectural Decisions

1. **Local-first AI routing:** every AI-service call attempts Ollama first; Gemini is invoked only as a fallback when no local model is available. This is enforced at the service layer (`diet_service.py`, `yoga_service.py`, `voice_service.py`), not the UI — keeping the privacy guarantee structural, not incidental.
2. **CV processing stays client-adjacent:** pose detection runs against the live webcam feed with minimal round-tripping, to keep correction feedback near real-time.
3. **Single injury-risk engine, multiple consumers:** `injury_risk_engine.py` is shared by both workout and yoga flows — one scoring core, not duplicated logic.
4. **Institutional view is read-only aggregate:** `coach_dashboard.py` reads from the same persistence layer as individual users — no separate data pipeline, avoids sync drift between personal and institutional views.
5. **Modular-by-file, monolith-by-deployment:** each concern lives in its own file/service, but ships as one Flask app for the hackathon timeline — a pragmatic step toward future microservice extraction, not a full split now.

## 5. Data Flow Summary

```
Webcam → Landmarks → Scoring → DB → Gamification → Dashboard
                 ↘
                  Injury-risk note → Corrective drill (surfaced to user)

User request (diet/yoga/voice) → Ollama (local) → [fallback] → Gemini (cloud) → Response
```

## 6. Scalability Path

- **Now:** single Flask instance, SQLite, single-tenant.
- **Next:** PostgreSQL, multi-tenant coach dashboard, modular deployment per institution.
- **Later:** split CV/AI services into independently scalable services if load requires; IoT/wearable telemetry as an additional ingestion path into the same persistence layer.
