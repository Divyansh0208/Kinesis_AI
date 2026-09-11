# Kinesis AI — Technical Architecture

```mermaid
graph TD
    subgraph Client ["Client Tier (Browser)"]
        Webcam["🎥 Webcam Video Stream"]
        MP["⚡ MediaPipe Pose (JS)"]
        Canvas["🎨 Canvas HUD & Skeleton Layer"]
        VoiceIn["🎙️ Web Speech Recognition"]
        VoiceOut["🔊 Web Audio / SpeechSynthesis"]
    end

    subgraph Backend ["Application Tier (Flask 3.x)"]
        App["Flask Core App Factory"]
        Auth["Flask-Login & User Mgmt"]
        RoutesMain["Core Routes (Fitness, Yoga, Diet)"]
        RoutesSports["Sports Routes (Football, Cricket)"]
        RoutesAPI["REST API Endpoints"]

        subgraph Kinematics ["Biomechanical & Movement Engine"]
            PoseMath["Vector Angle & Kinematics Math"]
            FitAnalyzer["Fitness Analyzer (Quality Reps)"]
            FBAnalyzer["Football Kinematics (Shooting/Agility)"]
            CricAnalyzer["Cricket Biomechanics (Pull/Cover/Bowling)"]
            RiskEngine["Injury Risk Engine (Non-medical indicators)"]
            GameEngine["Gamification & XP Engine"]
        end

        subgraph AI ["AI Provider Abstraction"]
            AIProvider["AIProvider Base"]
            Ollama["Local Ollama (PRIMARY)"]
            Gemini["Gemini 2.0 Flash (FALLBACK)"]
        end
    end

    subgraph Data ["Data & Sync Tier"]
        DB[(SQLite / PostgreSQL DB)]
        GoogleFit["Google Fit / Health Sync"]
    end

    Webcam --> MP
    MP --> Canvas
    MP --> RoutesAPI
    VoiceIn --> RoutesAPI
    RoutesAPI --> Kinematics
    RoutesAPI --> AI
    AIProvider --> Ollama
    Ollama -.->|Unavailable| Gemini
    Kinematics --> RoutesAPI
    RoutesAPI --> VoiceOut
    Backend --> DB
    Backend --> GoogleFit
```

---

## 1. Biomechanical Kinematics Engine
* Built with pure NumPy and deterministic trigonometric formulas (`calculate_angle`, `calculate_symmetry`, `calculate_stability`).
* Zero LLM invocation during real-time 30 FPS video tracking ensures sub-15ms response latency on basic laptops without GPU requirements.

---

## 2. Privacy-First AI Layer
* Primary: Local Ollama instance listening at `http://localhost:11434`.
* Transparent Fallback: If Ollama returns a connection error, `AIProvider` automatically falls back to the Gemini Cloud API using the server-side `GOOGLE_API_KEY`.
* Security: API keys and server credentials are never sent to the client browser.

---

## 3. Data Storage & PostgreSQL Readiness
* Relational database using SQLAlchemy models:
  * `User`: Profiles, XP, levels, login streaks.
  * `Workout`: Fitness repetitions, quality reps, duration, form score, estimated calories.
  * `SportsSession`: Football & cricket scores, component breakdowns, style inspiration.
  * `InjuryRiskRecord`: Movement-risk indicators and non-medical athletic guidance.
  * `Achievement`: Gamification badges unlocked by form excellence.
  * `TrainingPlan`: AI-generated position-specific 4-week training schedules.
