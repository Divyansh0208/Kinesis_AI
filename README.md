# ⚡ Kinesis AI — Webcam Movement Intelligence Platform

[![SIH 2026](https://img.shields.io/badge/Smart%20India%20Hackathon-2026-blue.svg)](https://sih.gov.in)
[![PS ID](https://img.shields.io/badge/PS%20ID-26196-orange.svg)](https://sih.gov.in)
[![Theme](https://img.shields.io/badge/Theme-Fitness%20%26%20Sports-green.svg)](https://sih.gov.in)
[![Team](https://img.shields.io/badge/Team-INOVE8-purple.svg)](https://github.com)
[![Privacy](https://img.shields.io/badge/AI-Ollama%20Local%20(Primary)-brightgreen.svg)](https://ollama.com)

> **"Your Webcam. Your Movement. Your AI Coach."**

Kinesis AI transforms any ordinary smartphone or laptop camera into an elite, real-time biomechanics coach and movement intelligence platform. Built for **Smart India Hackathon 2026 (PS ID: 26196, Fitness & Sports Theme)** by **Team INOVE8**.

---

## 🌟 Core Product Concept: The 5-Stage Movement Intelligence Loop

```
SENSE ──► PREDICT ──► OPTIMIZE ──► ASSIST ──► MONITOR
  │          │            │           │          │
Webcam   Kinematics   Ollama AI    Real-time   Dashboard
33 Pose  Form & Risk  4-Wk Plan   Audio/HUD   XP & Radar
```

1. **🎥 SENSE**: Webcam stream → MediaPipe Pose → 33 body landmark 3D coordinates at 30 FPS.
2. **🧠 PREDICT**: Deterministic biomechanical engine calculates joint angles, movement symmetry, center-of-mass stability, fatigue form drift, and proactive movement-risk indicators.
3. **⚡ OPTIMIZE**: Local privacy-first **Ollama AI** (with **Gemini Cloud fallback**) synthesizes 4-week position-specific athletic regimens and Indian nutritional plans.
4. **🗣️ ASSIST**: Real-time visual HUD overlays with glowing skeleton rendering + bilingual (Hindi + English) Voice Coach feedback.
5. **📊 MONITOR**: Unified athlete dashboard with Chart.js kinematic radars, quality-rep XP gamification, and injury risk trends.

---

## 🏆 Key Features & Innovations

### 1. 🏋️ Core Fitness Tracking
* **Push-ups**: 90° elbow depth check, straight-line body alignment (shoulder-hip-ankle), and symmetry.
* **Squats**: Thigh parallel depth (80°–100°), knee-over-toe alignment, and torso lean penalty.
* **Lunges**: 90° front knee flexion, back-knee clearance, and upright spine stability.
* **Planks**: Hold duration timer, core sag/arch detection, and micro-wobble stability score.
* **Jumping Jacks**: Overhead arm reach (>150°) and leg spread cadence validation.
* **Quality Rep Gating**: Only repetitions satisfying strict biomechanical criteria increment the quality counter.

### 2. ⚽ Football Intelligence Center
* **Shooting Biomechanics**: Plant foot placement, knee flexion, hip power rotation, torso backward lean check, and kicking follow-through arc. Score: `/100`.
* **Pose-Based Dribbling & Agility**: Center of mass shifts, rapid directional pivots, and low-center-of-gravity index (clearly labeled as *Pose-Based Analysis*).
* **Player-Style Inspired Coaching**: Select technical philosophies like *Lionel Messi-inspired close-control principles* or *Explosive Winger mechanics*.

### 3. 🏏 Cricket Biomechanics Center
* **Pull Shot Analysis**: Back-foot weight transfer, hip axis rotation, shoulder line, head stillness, and high follow-through.
* **Cover Drive (with Kohli Mode)**: Front-foot stride commitment, head-over-ball alignment, front knee flexion, and balanced follow-through.
* **Straight Drive**: Vertical bat presentation and balanced high front-elbow drive.
* **Batting Stance Readiness**: Base width, relaxed knee flexion, side-on shoulder alignment.
* **Bowling Biomechanics & Safety**: Run-up posture, front-arm pull, front-leg brace stability (>160°), and lower-back lumbar safety monitoring.

### 4. 🛡️ Signature Movement-Risk Engine
* Proactively identifies movement-risk indicators (joint-angle deviation, left/right asymmetry, excessive range of motion, fatigue-related form deterioration).
* Outputs: `Low Risk`, `Moderate Risk`, `High Risk`.
* **Honest Safety Philosophy**: Always displays athletic guidance with disclaimer: *"This is a movement-risk indicator, not a medical diagnosis."*

### 5. 🎙️ Bilingual Voice Coach (Hindi + English)
* Spoken voice interaction in natural Hindi, Hinglish, or English (e.g., *"Mera pull shot kaisa tha?"*).
* Instant audio response with SpeechSynthesis and actionable tactical advice.

### 6. 🔒 Privacy-First AI Architecture
* **Primary Engine**: Local [Ollama](https://ollama.com) (`gemma3:4b` or any installed local LLM).
* **Cloud Fallback**: Google Gemini 2.0 Flash API (used only when Ollama is unavailable).
* **Zero Frame Uploads to Cloud**: Video frames are processed strictly locally via MediaPipe and deterministic Python kinematics.

---

## 📂 Project Architecture

```
KinesisFX/
├── app.py                      # Flask application factory
├── run.py                      # Server entry point
├── routes.py                   # Core auth, fitness & dashboard routes
├── sports_routes.py            # Football & cricket training routes
├── api_routes.py               # Real-time pose analysis & REST endpoints
├── models.py                   # SQLAlchemy database schema (PostgreSQL ready)
├── pose_detection.py           # MediaPipe Pose & biomechanical calculations
├── injury_risk_engine.py       # Proactive movement-risk detection
├── sports_tracker.py           # Live sports session management
├── football_analyzer.py        # Football technique kinematic engine
├── cricket_analyzer.py         # Cricket shot & bowling kinematic engine
├── sports_drills.py            # Athletic agility & reaction drills
├── sports_scoring.py           # Unified /100 scoring engine
├── gamification.py             # XP calculation, levels & badge unlocks
├── ai_provider.py              # Ollama-first, Gemini-fallback abstraction
├── ollama_service.py           # Local Ollama client
├── gemini.py                   # Google Gemini fallback client
├── diet_service.py             # BMR/TDEE & Indian nutrition planner
├── yoga_service.py             # Asana posture alignment analyzer
├── voice_service.py            # Bilingual Hindi/English voice coach
├── google_fit_service.py       # Health & wearable sync service
├── requirements.txt            # Python dependencies
├── templates/                  # Modern responsive Jinja2 templates
└── static/                     # Cyber-glow CSS & MediaPipe JS pipelines
```

---

## 🚀 Quickstart Guide

### Prerequisites
* Python 3.10 – 3.12
* Webcam (built-in or USB)
* *(Optional)* [Ollama](https://ollama.com) installed with `gemma3:4b` or `mistral`

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/INOVE8/Kinesis-AI.git
cd Kinesis-AI
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` (or copy `.env.example`):
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
GOOGLE_API_KEY=your_gemini_api_key_here
SESSION_SECRET=kinesis-secret-key-change-me
DATABASE_URL=sqlite:///kinesis.db
```

### 3. Launch Application
```bash
python run.py
```
Open **`http://localhost:5000`** in Google Chrome or Microsoft Edge.

---

## 📊 SIH 2026 Team Credentials

* **Theme**: Fitness & Sports
* **Problem Statement ID**: 26196
* **Organization**: Ministry of Education's Innovation Cell (MIC) / AICTE
* **Team**: INOVE8
* **Lead AI & Full-Stack Engineer**: INOVE8 Core Team
