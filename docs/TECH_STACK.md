# Kinesis AI — Technology Stack

## 1. Frontend Technologies
* **HTML5 & CSS3:** Semantic modern structure with cyber-glow sports styling and glassmorphism.
* **Bootstrap 5.3.3:** Responsive mobile-first layout and navigation components.
* **Bootstrap Icons 1.11.3:** Vector sports, fitness, and navigation iconography.
* **Chart.js 4.4.7:** Interactive canvas charts for form trends and 6-axis sports biomechanics radars.
* **MediaPipe Pose (JS Client):** Real-time client-side pose detection running at 30 FPS.
* **Web Speech API & Web Audio API:** In-browser SpeechRecognition (Hindi + English) and synthesized audio tones.

---

## 2. Backend & Core Application
* **Python 3.10 – 3.12:** High-performance, type-hinted backend logic.
* **Flask 3.1.1:** Lightweight WSGI web application framework.
* **Flask-SQLAlchemy 3.1.1 & SQLAlchemy 2.0:** High-level ORM supporting SQLite and PostgreSQL.
* **Flask-Login 0.6.3:** Session-based user authentication and access control.
* **NumPy 1.26.4:** Vector calculations, joint angle trigonometry, and spatial stability analysis.
* **Python-Dotenv:** Environment configuration management.

---

## 3. Artificial Intelligence & Vision
* **Local Primary Engine:** Ollama (`gemma3:4b`, `mistral`, or any local model via REST API).
* **Cloud Fallback Engine:** Google Generative AI Python SDK (`gemini-2.0-flash`).
* **Computer Vision:** MediaPipe 33-point Pose Landmark Topology.
* **Biomechanical Engine:** Custom Python kinematic solvers (`FitnessAnalyzer`, `FootballAnalyzer`, `CricketAnalyzer`, `DrillAnalyzer`, `InjuryRiskEngine`).

---

## 4. Hardware Requirements & Optimization
* **Client Device:** Standard laptop or mobile phone with webcam (No external GPU required).
* **Client RAM:** 4GB+ RAM.
* **Bandwidth:** Zero video stream upload; sends only small coordinate JSON vectors.
