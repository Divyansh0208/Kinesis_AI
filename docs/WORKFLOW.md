# Kinesis AI — User Journey & System Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Athlete as Athlete
    participant UI as Web Browser (UI & Canvas)
    participant MP as MediaPipe (Webcam Stream)
    participant Flask as Flask Backend
    participant Kinematics as Kinematic Engine
    participant AI as AI Engine (Ollama / Gemini)
    participant DB as SQLite / PostgreSQL

    Athlete->>UI: Selects Activity (e.g. Football Shooting / Push-Ups)
    UI->>MP: Request Camera & Init Pose Detector
    MP-->>UI: 33 Landmark Points
    UI->>UI: 10s Calibration Check (Full body visible & centered)
    
    loop Live Repetition Analysis (30 FPS)
        MP->>UI: Stream 33 Normalized Coordinates
        UI->>Flask: POST /api/{sport}/analyze
        Flask->>Kinematics: Compute Joint Angles, Symmetry, Stability
        Kinematics-->>Flask: Form Score /100, Rep Validation, Risk Indicators
        Flask-->>UI: Live HUD Metrics, Posture Corrections & Tones
        UI-->>Athlete: Instant Visual Skeleton + Audio Feedback
    end

    Athlete->>UI: Finishes Workout / Drill Session
    UI->>Flask: POST /api/sports/save (Session Data)
    Flask->>DB: Save Session, XP & Badge Record
    Flask->>AI: Generate Post-Session Deep Tactical Advice
    AI-->>Flask: Structured Tactical Recommendations
    Flask-->>UI: Return Summary Modal with XP & Level-Up
    UI-->>Athlete: Display Dashboard & Radar Trends
```

---

## The 5-Stage Intelligence Cycle in Detail

### 1. SENSE
The browser requests standard camera access (640x480 resolution). MediaPipe extracts 33 body keypoints with `x, y, z` normalized coordinates and visibility probabilities.

### 2. PREDICT
The client sends coordinate vectors to the Flask backend, where deterministic mathematical calculations measure:
* Joint Angles (vectors around vertices)
* Segment Symmetry (Left vs Right differential)
* Spatial Stability (variance across sliding frames)
* Movement-Risk Index (deviation from safe athletic corridors)

### 3. OPTIMIZE
When an athlete generates a training plan or asks for nutrition coaching, the backend invokes the local Ollama LLM (e.g. `gemma3:4b`) to structure a progressive 4-week periodized program. If Ollama is offline, the system seamlessly uses the Google Gemini 2.0 Flash API.

### 4. ASSIST
During live practice, the athlete receives instant multi-sensory feedback:
* **Visual:** Cyber-glow skeleton lines, real-time score badges, and guidance text.
* **Audio:** High/low confirmation audio tones for quality repetitions and spoken bilingual coaching cues.

### 5. MONITOR
All session metrics, quality rep ratios, and movement-risk histories are consolidated on the athlete dashboard with Chart.js radar and time-series charts.
