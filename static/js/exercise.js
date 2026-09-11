/**
 * Kinesis AI — Fitness Exercise Live Analysis Controller
 * Real-time loop for Push-ups, Squats, Lunges, Planks, and Jumping Jacks.
 */

class FitnessExerciseController {
    constructor(config) {
        this.exerciseType = config.exerciseType;
        this.sessionId = 'fit_' + Math.random().toString(36).substring(2, 9);
        this.pipeline = null;
        this.calibration = null;
        this.isActive = false;
        this.startTime = null;

        this.lastRepCount = 0;
        this.qualityReps = 0;
        this.currentScore = 0;
        this.sessionScores = [];

        // DOM elements
        this.videoEl = document.getElementById('webcamVideo');
        this.canvasEl = document.getElementById('skeletonCanvas');
        this.calibrationEl = document.getElementById('calibrationOverlay');
        this.repCounterEl = document.getElementById('repCounter');
        this.qualityRepCounterEl = document.getElementById('qualityRepCounter');
        this.formScoreEl = document.getElementById('formScoreValue');
        this.formGaugeEl = document.getElementById('formScoreBar');
        this.fatigueBadgeEl = document.getElementById('fatigueBadge');
        this.correctionsContainer = document.getElementById('liveCorrections');
        this.positivesContainer = document.getElementById('livePositives');
        this.timerEl = document.getElementById('sessionTimer');
        this.riskAlertBanner = document.getElementById('riskAlertBanner');

        this.timerInterval = null;
    }

    async init() {
        this.pipeline = new KinesisPosePipeline(this.videoEl, this.canvasEl, {
            onResults: (landmarks) => this.onFrame(landmarks)
        });

        this.calibration = new KinesisCalibration(this.calibrationEl, {
            onCalibrationSuccess: () => this.startSession()
        });

        await this.pipeline.init();
        await this.pipeline.start();
        this.calibration.start();
    }

    onFrame(landmarks) {
        if (!this.calibration.isCalibrated) {
            this.calibration.processFrame(landmarks);
            return;
        }

        if (!this.isActive) return;

        // Extract raw landmarks array
        const rawPoints = landmarks.map(lm => ({
            x: lm.x,
            y: lm.y,
            z: lm.z,
            visibility: lm.visibility || 1.0
        }));

        // Send to backend deterministic analyzer
        fetch('/api/fitness/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                exercise: this.exerciseType,
                session_id: this.sessionId,
                landmarks: rawPoints
            })
        })
        .then(res => res.json())
        .then(data => this.handleAnalysisData(data))
        .catch(err => console.debug('Fitness frame analyze error:', err));
    }

    handleAnalysisData(data) {
        if (!data) return;

        this.currentScore = data.form_score || 0;
        this.sessionScores.push(this.currentScore);

        // Update Reps
        if (data.current_reps > this.lastRepCount) {
            this.lastRepCount = data.current_reps;
            if (this.repCounterEl) this.repCounterEl.textContent = data.current_reps;

            if (data.quality_rep) {
                this.qualityReps = data.quality_reps;
                if (this.qualityRepCounterEl) this.qualityRepCounterEl.textContent = data.quality_reps;
                KinesisAudio.playRepTone();
            } else {
                KinesisAudio.playAlertTone();
            }
        }

        // Update Score & Gauge
        if (this.formScoreEl) this.formScoreEl.textContent = Math.round(this.currentScore);
        if (this.formGaugeEl) {
            this.formGaugeEl.style.width = `${Math.min(100, this.currentScore)}%`;
            if (this.currentScore >= 80) {
                this.formGaugeEl.className = 'progress-bar bg-success';
            } else if (this.currentScore >= 60) {
                this.formGaugeEl.className = 'progress-bar bg-warning';
            } else {
                this.formGaugeEl.className = 'progress-bar bg-danger';
            }
        }

        // Update Fatigue
        if (this.fatigueBadgeEl && data.fatigue_level) {
            this.fatigueBadgeEl.textContent = `Fatigue: ${data.fatigue_level.toUpperCase()}`;
            this.fatigueBadgeEl.className = `badge rounded-pill ${data.fatigue_level === 'high' ? 'bg-danger' : (data.fatigue_level === 'moderate' ? 'bg-warning text-dark' : 'bg-success')}`;
        }

        // Update Feedback Lists
        if (this.correctionsContainer && data.corrections) {
            this.correctionsContainer.innerHTML = data.corrections.map(c => `<div class="text-warning small mb-1"><i class="bi bi-exclamation-triangle-fill me-1"></i> ${c}</div>`).join('');
        }
        if (this.positivesContainer && data.positives) {
            this.positivesContainer.innerHTML = data.positives.map(p => `<div class="text-neon-green small mb-1"><i class="bi bi-check-circle-fill me-1"></i> ${p}</div>`).join('');
        }

        // Risk Banner
        if (this.riskAlertBanner && data.risk) {
            if (data.risk.risk_level === 'high') {
                this.riskAlertBanner.classList.remove('d-none');
                this.riskAlertBanner.innerHTML = `<i class="bi bi-shield-exclamation me-1"></i> <strong>Movement Risk Alert:</strong> Form drift detected. Reset your posture to avoid strain.`;
            } else {
                this.riskAlertBanner.classList.add('d-none');
            }
        }
    }

    startSession() {
        this.isActive = true;
        this.startTime = Date.now();
        this.timerInterval = setInterval(() => this.updateTimer(), 1000);
        showKinesisToast('Session Active', `Tracking ${this.exerciseType}. Maintain good form!`, 'success');
    }

    updateTimer() {
        if (!this.startTime || !this.timerEl) return;
        const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
        const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
        const secs = String(elapsed % 60).padStart(2, '0');
        this.timerEl.textContent = `${mins}:${secs}`;
    }

    async finishSession() {
        this.isActive = false;
        clearInterval(this.timerInterval);
        this.pipeline.stop();

        const durationSec = (Date.now() - (this.startTime || Date.now())) / 1000;
        const avgScore = this.sessionScores.length > 0 ? (this.sessionScores.reduce((a, b) => a + b, 0) / this.sessionScores.length) : 0;

        // Save session
        const payload = {
            exercise_type: this.exerciseType,
            reps: this.lastRepCount,
            quality_reps: this.qualityReps,
            duration: durationSec,
            form_score: avgScore,
            fatigue_level: avgScore < 60 ? 'high' : 'low'
        };

        const res = await fetch('/api/fitness/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        // Show finish modal
        showSummaryModal(payload, data);
    }
}

function showSummaryModal(sessionData, serverResponse) {
    const modalEl = document.getElementById('summaryModal');
    if (!modalEl) return;

    document.getElementById('summaryReps').textContent = sessionData.reps;
    document.getElementById('summaryQualityReps').textContent = sessionData.quality_reps;
    document.getElementById('summaryScore').textContent = Math.round(sessionData.form_score) + '/100';
    document.getElementById('summaryCalories').textContent = serverResponse.calories_estimated || '0';
    document.getElementById('summaryXP').textContent = '+' + (serverResponse.xp_earned || 0) + ' XP';

    const bsModal = new bootstrap.Modal(modalEl);
    bsModal.show();
}
