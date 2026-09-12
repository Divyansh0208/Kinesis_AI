# Kinesis AI — Workflow & System Flow

## 1. High-Level Loop (Product Methodology)

```
SENSE → PREDICT → OPTIMIZE → ASSIST → MONITOR
```

| Stage | What happens |
|---|---|
| **Sense** | Webcam captures video → MediaPipe extracts 33 live 3D body landmarks |
| **Predict** | Joint-angle drift + fatigue analyzed → injury-risk flagged early (before damage) |
| **Optimize** | Gemini + Ollama generate adaptive 4-week workout, diet & recovery plans |
| **Assist** | Real-time bilingual voice coach corrects form mid-rep (incl. chair/bed-bound yoga) |
| **Monitor** | Dashboard tracks personal streaks/XP + institutional batch-level metrics |

## 2. Technical Data Flow

```
Webcam feed
   → MediaPipe pose landmarks (33 points)
   → Form-quality + injury-risk scoring (injury_risk_engine.py)
   → SQLite/PostgreSQL logging (models.py)
   → Gamification engine (XP, streaks, badges)
   → Chart.js dashboard (visual trends)

Diet / Yoga / Voice requests
   → Ollama (local model) attempted first
   → Falls back to Gemini only if no local model available
   → Personal health data stays on-device by default
```

## 3. Session Workflow (User Perspective)

1. User opens a workout/yoga session (webcam permission required).
2. Live pose overlay renders; system counts reps only on correct form.
3. Instant visual + spoken correction cues fire on form deviation.
4. Session data (joint angles, fatigue drift, reps, timing) logged continuously.
5. Post-session: injury-risk note generated (plain language) + corrective drill suggested.
6. XP/streak/badges updated; dashboard refreshed with new trend data.
7. Weekly: adaptive workout plan re-generated based on logged performance (Gemini).
8. On-demand: diet plan, recovery guidance, or yoga flow generated (Ollama-first).

## 4. Institutional Workflow (Coach/School Mode)

1. Coach/admin logs into `coach_dashboard.py` view.
2. Aggregate view of batch: activity levels, form-quality trends, injury-risk flags across students.
3. Used for AICTE institutional fitness compliance tracking.

## 5. Voice Coaching Flow

1. User speaks (Hindi or English) — auto language detection.
2. `voice_service.py` handles STT → intent → routes to relevant service (workout correction, yoga cue, general query).
3. Response generated via local LLM (Ollama) or Gemini (fallback) → TTS → spoken back.
4. Fully voice-navigable — no typing required mid-workout.

## 6. Accessibility Flow

- High-contrast UI + large touch targets active by default in Accessibility Mode.
- Chair/bed-bound exercise & yoga variants auto-offered based on user profile/mobility level.
- Voice-first navigation available as a full alternative input path throughout the app.

## 7. Deployment / Scaling Path

```
Individual (webcam + laptop)
   → College batch (multi-tenant dashboard, shared institutional views)
   → Regional gym chain (modular deployment, incremental rollout)
```

## 8. Development Workflow (Build Order Recommendation)

1. Core CV pipeline: `pose_detection.py` (landmark extraction) — validate accuracy first.
2. `injury_risk_engine.py` — build scoring logic on top of validated landmarks.
3. `models.py` + DB — persist sessions/scores.
4. `sports_tracker.py` + `gamification.py` — extend beyond gym exercises, add engagement layer.
5. `gemini.py` + `diet_service.py` + `yoga_service.py` — AI planning layer (local-first).
6. `voice_service.py` — bilingual voice on top of stable core.
7. `coach_dashboard.py` + `google_fit_service.py` — institutional + wearable integrations last.
8. `templates/` + `static/` — polish UI/UX + PWA/accessibility features throughout, not just at the end.
