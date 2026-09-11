# Kinesis AI — Product Requirements Document (PRD)

## 1. Product Vision
To provide every athlete and fitness enthusiast with an intelligent, privacy-first movement coach accessible through any web browser and camera.

---

## 2. Core Functional Requirements

### 2.1 Pose Detection & SENSE Pipeline
* Ingest 2D video at 640x480 / 30 FPS.
* Extract 33 standardized body landmarks using MediaPipe Pose.
* Require a mandatory 10-second calibration phase to ensure full-body visibility, lighting quality, and distance before scoring starts.

### 2.2 Biomechanical Analytics (PREDICT)
* Calculate joint angles (`calculate_angle`), Euclidean distances (`calculate_distance`), velocity (`calculate_velocity`), left/right symmetry (`calculate_symmetry`), and position stability (`calculate_stability`).
* Validate rep quality based on range of motion and core alignment before incrementing quality rep counters.
* Continuously compute 0-100 technique and form scores with component breakdowns.
* Track fatigue form degradation across rolling frame windows.

### 2.3 Sports Center Expansion
* **Football Modules:**
  * Shooting Technique (Plant Foot, Hip Rotation, Knee Position, Torso Position, Balance, Follow Through).
  * Pose-based Dribbling & Agility (Center of Mass shift, direction change cadence).
  * Player-style inspired coaching principles (Messi close control, explosive winger).
* **Cricket Modules:**
  * Pull Shot (Back-foot transfer, hip rotation, head stability, follow-through).
  * Cover Drive (Front-foot stride, head-over-ball alignment, Kohli-inspired focus mode).
  * Straight Drive (Vertical bat line, front-elbow elevation).
  * Batting Stance (Readiness, base width, shoulder line).
  * Bowling Action (Run-up posture, front-leg brace, lumbar spine safety).

### 2.4 Injury-Risk Engine
* Identify excessive joint angles, extreme asymmetries, sudden velocity jerks, and fatigue-related form collapse.
* Classify risk as Low, Moderate, or High.
* Mandate clear non-medical disclaimer on all risk views.

### 2.5 AI Optimization (OPTIMIZE)
* Generate 4-week position-specific sports training plans.
* Calculate BMR/TDEE and generate Indian athletic diet plans.
* Primary AI: Local Ollama. Fallback AI: Google Gemini API.

### 2.6 Voice Assistant (ASSIST)
* Bilingual voice coaching in Hindi, Hinglish, and English using Web Speech API and backend LLM reasoning.

### 2.7 Dashboard & Gamification (MONITOR)
* Track XP earned exclusively for **form quality**, not empty repetition counts.
* Milestone badges, daily streaks, level progression, and Chart.js radar/trend visualizations.
