# Kinesis AI — Product Requirements Document

**Team:** INOVE8 | **Event:** Smart India Hackathon 2026
**PS ID:** 26196 — "Student Innovation: Ideas that boost fitness activities and assist in keeping fit"
**Theme:** Fitness & Sports | **Org:** AICTE, MIC-Student Innovation

## 1. Problem

Millions of people — from beginners to the elderly — exercise without professional guidance. Unnoticed movement faults (knee valgus, lower-back rounding, etc.) accumulate silently and cause injury over time. People abandon fitness because of preventable pain, and professional biomechanical coaching is a financial luxury most can't access.

**The gap:** existing tools measure activity (steps, reps, calories) but don't understand movement *quality*, and don't intervene before poor form becomes an injury.

## 2. Existing Solutions & Limitations

| Category | How it works | Gap |
|---|---|---|
| Standard fitness apps | Track steps/reps/calories | Blind to form — a biomechanically risky squat still logs as a "successful" rep |
| Premium wearables / CV systems | Sensors + continuous cloud processing | Cost-prohibitive for students; sensitive health data processed on public cloud |

**Missing layer:** affordable, privacy-first, real-time biomechanical coaching.

## 3. Solution Overview

Kinesis AI turns a standard webcam into a proactive fitness companion, via a 5-stage loop:

**SENSE → PREDICT → OPTIMIZE → ASSIST → MONITOR**

1. **Sense** — Webcam → 33 live 3D body landmarks (MediaPipe).
2. **Predict** — Analyze joint-angle drift + fatigue to flag injury risk *before* it happens.
3. **Optimize** — Gemini + Ollama generate adaptive 4-week workout, diet & recovery plans.
4. **Assist** — Real-time bilingual (Hindi/English) voice coach corrects form mid-rep, incl. chair/bed-bound yoga variants.
5. **Monitor** — Dashboard tracks streaks/XP individually and batch-level metrics institutionally.

## 4. Target Users

- Individual users (beginner → intermediate) exercising without a trainer.
- Elderly / differently-abled users needing accessible, low-impact guidance.
- Colleges / schools (AICTE institutions) wanting batch-level fitness tracking (coach dashboard).
- Budget-conscious users who can't afford wearables or personal trainers.

## 5. Core Features (Functional Requirements)

1. **Real-Time 3D Pose & Form Analysis** — 33-landmark tracking; pushups, squats, jumping jacks, lunges, planks; per-rep depth/angle/alignment scoring; reps only count on correct form; instant visual + spoken correction.
2. **Injury-Risk Prediction Engine (signature feature)** — tracks joint-angle deviation + fatigue-linked form drift across a session and over weeks; flags compounding risk patterns proactively; plain-language risk note + corrective drill.
3. **Sports Drill & Performance Tracker** — shuttle runs, jump-rope cadence, plank-hold timing, agility ladder; reaction time + movement speed via pose velocity.
4. **Gamified Progress & Community Challenges** — XP, streaks, badges tied to form quality (not just attendance); leaderboards; friend challenges; school/college coach dashboard.
5. **Adaptive AI Workout Planner** — Gemini-generated 4-week programs from fitness level, equipment, goals, limitations; adjusts weekly based on logged performance.
6. **AI Diet & Recovery Planner** — local Ollama LLMs generate macro-targeted meal plans (Vegan/Keto/Paleo/etc.) + recovery guidance tied to session intensity; on-device inference by default.
7. **AI Yoga & Mobility Instructor** — flows by mood/goal/mobility, incl. seated/bed-bound variants; SVG pose guides + live pose-matching via same CV pipeline.
8. **Bilingual Voice Coach** — real-time Hindi/English conversational coaching (Gemini + local LLM), auto language detection, fully voice-navigable.
9. **Accessibility-First Mode** — high-contrast UI, large touch targets, full voice-first navigation, chair/bed-based variants.
10. **Unified Dashboard & Wearable/Fit Sync** — Chart.js visualizations (streaks, calories, form-quality, injury-risk history); Google Fit + wearable sync.

## 6. Non-Functional Requirements

- **Privacy-first:** health-sensitive inference (diet, yoga, voice) runs on-device via Ollama by default; Gemini only as fallback when no local model available.
- **Affordability:** runs on a standard webcam + consumer laptop — no special sensors/wearables required.
- **Real-time:** pose feedback and form correction must feel live (target: near-frame-rate latency).
- **Accessibility:** must support elderly/differently-abled users end-to-end, not as an afterthought.
- **Scalability:** individual → college batch → regional gym chain, via multi-tenant dashboard and modular deployment.
- **Offline resilience:** PWA, offline-capable core flows where feasible.

## 7. Differentiators

- **Injury-risk prediction is proactive, not reactive** — competitors count reps; Kinesis predicts damage before it happens.
- **Privacy-first architecture** — on-device AI by default vs. cloud-dependent premium systems.
- **Genuinely covers "Sports"**, not just gym exercises (drills, agility, reaction time).
- **Institutional angle** — coach/school dashboard is a direct fit for AICTE's student-innovation mandate.
- **Accessibility as core, not bolt-on** — chair/bed-bound modes, voice-first, high-contrast.

## 8. Success / Impact Metrics

- Posture accuracy score (form-quality trend over time)
- Injury-risk reduction rate
- Institutional fitness compliance (batch-level engagement)
- Engagement / streak performance

## 9. Current Limitations

- **Lighting & hardware:** vision accuracy depends on adequate lighting + unobstructed full-body webcam angle.
- **Edge computing:** local LLM inference speed depends on user's device hardware.

## 10. Future Scope

- **IoT integration:** direct smartwatch sync for live heart-rate telemetry and internal physical-load tracking.
- **Advanced sports tech:** multi-person tracking for team sports and dynamic agility drills.

> **Vision:** from today's webcam → tomorrow's smart fitness ecosystem. From personal fitness → institutional wellness.

## 11. Non-Goals (v1 scope guard)

- Not a medical diagnostic tool — injury-risk flags are advisory, not clinical.
- No multi-person pose tracking in v1 (single-user sessions only).
- No hardware/wearable manufacturing — integration only, via Google Fit / existing wearable APIs.
