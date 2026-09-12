# Kinesis AI — Project Context

_Reference doc for anyone (or any AI assistant) picking up work on this repo._

## What this is

Kinesis AI — AI-powered movement intelligence for safer, smarter fitness. Built for **Smart India Hackathon 2026**, PS #26196 ("Student Innovation — Ideas that can boost fitness activities and assist in keeping fit"), Theme: Fitness & Sports, Org: AICTE / MIC-Student Innovation.

**Team:** INOVE8

## Origin note (important)

This project was inspired by an existing open-source fitness-app README (Flask/OpenCV/MediaPipe/SQLite/Gemini/Ollama/Chart.js/Google Fit) found during research. **That original project is someone else's work and is not the base being shipped.** Kinesis AI is an original, independently-built platform for the same problem space, under its own name and its own architecture. Treat the original only as inspiration/prior-art, never as a source to name or copy from directly.

## One-line pitch

Turns a standard webcam into a proactive fitness companion that senses movement, predicts injury risk before it happens, and coaches correction in real time — bilingually, affordably, and privacy-first.

## The 5-stage loop (core mental model)

**SENSE → PREDICT → OPTIMIZE → ASSIST → MONITOR**

Every feature maps back to one of these five stages. When in doubt about where a new feature belongs, place it in this loop first.

## Signature differentiator

**Injury-risk prediction engine.** Everything else (rep counting, workout plans, diet, yoga) exists in fitness apps somewhere. Proactive injury-risk prediction from joint-angle drift + fatigue tracking — flagging risk *before* it becomes damage — does not. This is the feature to protect and prioritize if scope needs to shrink.

## Non-negotiable design principles

1. **Privacy-first, structurally.** Local Ollama inference is the default path for anything diet/yoga/voice/health-adjacent. Gemini is a fallback for when no local model exists — never the default.
2. **Affordable by design.** No proprietary sensors or wearables required — a webcam and a laptop must be sufficient for the full core loop.
3. **Accessibility is core, not a bolt-on.** Chair/bed-bound variants, high-contrast UI, full voice navigation must be first-class, not "coming later."
4. **Sports, not just gym.** The theme is "Fitness & Sports" — drills, agility, reaction time must stay in scope, not get cut for time.
5. **Institutional angle matters for this PS.** The coach/school dashboard is what makes this a fit for AICTE's student-innovation mandate — don't treat it as a stretch feature.

## Known current limitations (be upfront about these, don't hide them)

- Vision accuracy depends on lighting + full-body webcam framing.
- Local LLM inference speed is hardware-dependent on the user's device.

## Roadmap beyond hackathon scope (don't build now, but keep architecture open for)

- IoT/smartwatch sync for live heart-rate + physical-load telemetry.
- Multi-person pose tracking for team sports / dynamic agility drills.

## Companion docs in this repo

- `PRD.md` — full product requirements, features, metrics, non-goals.
- `TECH_STACK.md` — technologies, module-to-file map, rationale.
- `WORKFLOW.md` — system flow, session/user/coach/voice workflows, build order.
- `ARCHITECTURE.md` — component diagram, layer responsibilities, key architectural decisions.

## Quick facts cheat-sheet

| | |
|---|---|
| PS ID | 26196 |
| Theme | Fitness & Sports |
| Org | AICTE, MIC-Student Innovation |
| Team | INOVE8 |
| Backend | Flask + SQLAlchemy |
| CV | OpenCV + MediaPipe (33 landmarks) |
| Cloud AI | Google Gemini |
| Local AI | Ollama (Llama 3 / Mistral / Gemma) |
| DB | SQLite (dev) → PostgreSQL (prod) |
| Frontend | Bootstrap 5, Vanilla JS, Chart.js, PWA |

---

## Build Log (living section — update every phase)

### Phase 1 — Scaffold & rebrand (done)
- Took a prior-art open-source fitness app (Flask/OpenCV/MediaPipe/SQLite/Gemini/Ollama/Chart.js/Google Fit) as a structural starting point per CONTEXT rules above — used as inspiration/base code only, not copied as-is long-term.
- Renamed all product-name strings across code, templates, JS, CSS, README, DB filename (`kinesis.db`) to Kinesis AI branding. Verified zero leftover old-name references (checked case-insensitive across repo).
- Old README replaced with a Kinesis-branded one pointing to `docs/`.
- Planning docs (`PRD.md`, `ARCHITECTURE.md`, `TECH_STACK.md`, `WORKFLOW.md`, this `CONTEXT.md`) placed under `docs/`.
- Existing modules inherited as-is (not yet audited line-by-line against PRD): `app.py`, `routes.py`, `models.py`, `extensions.py`, `pose_detection.py`, `gemini.py`, `diet_service.py`, `yoga_service.py`, `voice_service.py`, `google_fit_service.py`, `start_app.py`, `run.py`, templates/, static/.
- NOT yet present / not yet built: `injury_risk_engine.py` (signature feature — priority), `sports_tracker.py`, `gamification.py`, `coach_dashboard.py`. These are referenced in ARCHITECTURE/TECH_STACK but don't exist in the inherited codebase yet.

### Next up (per WORKFLOW.md build order)
1. Audit `pose_detection.py` against PRD's 33-landmark / exercise list (pushups, squats, jumping jacks, lunges, planks) — validate before building on top.
2. Build `injury_risk_engine.py` — joint-angle drift + fatigue scoring, feeds off validated landmarks. Top priority, this is the differentiator.
3. Check `models.py` schema covers: sessions, per-rep scores, injury-risk history, XP/streaks — extend as needed.
4. `sports_tracker.py` + `gamification.py` — not yet built.
5. Confirm `diet_service.py` / `yoga_service.py` / `voice_service.py` actually do local-first Ollama → Gemini-fallback routing (inherited code — needs verification against that rule, not assumed correct).
6. `coach_dashboard.py` — not yet built.
7. UI/PWA/accessibility polish — ongoing, not a final-phase-only task.

### Rules for whoever (human or AI) continues this
- Never write the old project's name anywhere (code, comments, commits, docs, chat). Refer to prior art only as "an existing open-source reference project" if it must come up at all.
- Update this Build Log section at the end of every phase: what changed, what's inherited-but-unverified, what's genuinely new, what's next.
- Keep the 5 non-negotiable design principles (top of this file) as the check before merging anything.

### Phase 1.1 — Actually verified working (done)
- Fixed a broken dependency pin found on install: `mediapipe==0.10.5` no longer exists on PyPI → bumped to `0.10.21`, bumped `opencv-python` to `4.10.0.84` and `numpy` to `1.26.4` for compatibility.
- Confirmed: fresh venv installs clean, `app.py` boots, SQLite tables create, `/`, `/login`, `/register` all return 200 via Flask test client. Ollama/Gemini warnings on boot are expected (no local keys in this sandbox), not bugs.
- Confirmed no leftover old-project name anywhere in served HTML or source (only false-positive match was the generic phrase "computer vision").

### Phase 1.2 — Pillow pin fix (done)
- `pillow==10.0.0` had no prebuilt wheel for the user's Python/Windows combo, so pip fell back to downloading and compiling the source tarball — extremely slow, and on Windows it hit `WinError 32` (temp file locked, usually antivirus or pip cache) mid-build. Bumped to `pillow==10.4.0`, which has prebuilt wheels, so pip just downloads a `.whl` and installs instantly, no compile step.

### Phase 1.3 — Removed dead mediapipe Python dependency (done)
- Found: the Python `mediapipe` package was never actually imported anywhere in the backend (`grep` across all `.py` files: zero hits). Real pose detection runs 100% client-side in-browser via MediaPipe's JS CDN scripts, loaded in `templates/exercise_analysis.html`.
- The pinned Python package was pure dead weight, and its build/wheel availability was the exact thing breaking installs (no matching version for some users' Python/OS combos, e.g. `WinError 32` / no wheel found errors).
- Removed `mediapipe` from `requirements.txt` entirely. Re-verified: fresh venv installs clean, `app.py` boots, `/`, `/login`, `/register` still 200.
- `opencv-python` stays (guarded with try/except in `routes.py` for one image-decode feature, already had a working wheel for the user).
- Lesson for later phases: if `injury_risk_engine.py` needs server-side pose math, it should consume the landmark JSON already produced by the browser-side MediaPipe JS, not re-run pose estimation in Python. Don't re-add the Python mediapipe package unless a genuinely new server-side need appears.

### Phase 1.4 — Relaxed compiled-package pins for cross-Python compatibility (done)
- User's local pip failed on `numpy==1.26.4`: no prebuilt wheel for their (newer) Python version, so pip tried compiling from source, which needs a C compiler / MSVC Build Tools they don't have (`meson.build ERROR: Unknown compiler(s)`).
- Root cause pattern: hard-pinning exact versions of compiled packages (numpy, opencv, pillow) breaks whenever the user's Python version is newer than what that exact pin shipped wheels for.
- Fix: changed `numpy==1.26.4` → `numpy>=1.26.4`, `opencv-python==4.10.0.84` → `opencv-python>=4.10.0.84`, `pillow==10.4.0` → `pillow>=10.4.0`. Pip now resolves to whatever version has a prebuilt wheel for the user's actual Python, instead of being locked to one that might not.
- Re-verified in a fresh venv: installs clean, app boots, `/`, `/login`, `/register` all 200.
- Pure-Python deps (flask, flask-login, flask-sqlalchemy, werkzeug, etc.) stay pinned exactly — they don't have this compiler problem.
