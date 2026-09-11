/**
 * Kinesis AI — Football Technique Live Analysis Controller
 * Real-time loop for Shooting, Dribbling, Agility Drills & Style-inspired coaching.
 */

class FootballController {
    constructor(config) {
        this.skill = config.skill || 'shooting';
        this.sessionId = 'fb_' + Math.random().toString(36).substring(2, 9);
        this.styleInspiration = config.styleInspiration || 'technical_dribbler';
        this.pipeline = null;
        this.calibration = null;
        this.isActive = false;
        this.startTime = null;

        this.scores = [];
        this.currentScore = 0;
        this.breakdown = {};
        this.corrections = [];
        this.positives = [];

        // DOM elements
        this.videoEl = document.getElementById('webcamVideo');
        this.canvasEl = document.getElementById('skeletonCanvas');
        this.calibrationEl = document.getElementById('calibrationOverlay');
        this.scoreValEl = document.getElementById('footballScoreVal');
        this.styleBadgeEl = document.getElementById('styleInspirationBadge');
        this.breakdownContainer = document.getElementById('metricBreakdown');
        this.correctionsEl = document.getElementById('footballCorrections');
        this.positivesEl = document.getElementById('footballPositives');
        this.styleTipsEl = document.getElementById('styleCoachingTips');
        this.timerEl = document.getElementById('sessionTimer');
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

        const rawPoints = landmarks.map(lm => ({
            x: lm.x,
            y: lm.y,
            z: lm.z,
            visibility: lm.visibility || 1.0
        }));

        fetch('/api/football/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                skill: this.skill,
                session_id: this.sessionId,
                style_inspiration: this.styleInspiration,
                landmarks: rawPoints
            })
        })
        .then(res => res.json())
        .then(data => this.handleData(data))
        .catch(err => console.debug('Football analysis frame error:', err));
    }

    handleData(data) {
        if (!data) return;

        this.currentScore = data.score || 0;
        this.scores.push(this.currentScore);

        if (this.scoreValEl) {
            this.scoreValEl.textContent = Math.round(this.currentScore);
        }

        // Render Breakdown
        if (this.breakdownContainer && data.metrics) {
            this.breakdown = data.metrics;
            this.breakdownContainer.innerHTML = Object.entries(data.metrics).map(([k, v]) => `
                <div class="d-flex justify-content-between align-items-center mb-1 small">
                    <span class="text-secondary text-capitalize">${k.replace(/_/g, ' ')}</span>
                    <span class="fw-bold text-neon-cyan">${typeof v === 'number' ? Math.round(v) : v}</span>
                </div>
            `).join('');
        }

        // Corrections & Positives
        if (this.correctionsEl && data.corrections) {
            this.corrections = data.corrections;
            this.correctionsEl.innerHTML = data.corrections.map(c => `
                <div class="text-warning small mb-1"><i class="bi bi-exclamation-triangle-fill me-1"></i> ${c}</div>
            `).join('');
        }

        if (this.positivesEl && data.positives) {
            this.positives = data.positives;
            this.positivesEl.innerHTML = data.positives.map(p => `
                <div class="text-neon-green small mb-1"><i class="bi bi-check-circle-fill me-1"></i> ${p}</div>
            `).join('');
        }

        // Style Inspiration Coaching Tips
        if (this.styleTipsEl && data.style_coaching) {
            const sc = data.style_coaching;
            this.styleTipsEl.innerHTML = `
                <div class="text-neon-cyan fw-bold mb-1"><i class="bi bi-stars me-1"></i> ${sc.style_name || 'Style Focus'}</div>
                <div class="text-light small mb-2">${sc.description || ''}</div>
                <ul class="list-unstyled mb-0 ps-1 small text-secondary">
                    ${(sc.coaching_tips || []).map(tip => `<li><i class="bi bi-arrow-right-short text-neon-green"></i> ${tip}</li>`).join('')}
                </ul>
            `;
        }
    }

    startSession() {
        this.isActive = true;
        this.startTime = Date.now();
        this.timerInterval = setInterval(() => this.updateTimer(), 1000);
        showKinesisToast('Drill Started', `Analyzing Football ${this.skill.toUpperCase()}. Give your best!`, 'success');
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
        const avgScore = this.scores.length > 0 ? (this.scores.reduce((a, b) => a + b, 0) / this.scores.length) : 0;

        const payload = {
            sport: 'football',
            sport_skill: this.skill,
            score: avgScore,
            duration: durationSec,
            reps: Math.max(1, Math.round(durationSec / 5)),
            risk_level: avgScore < 50 ? 'moderate' : 'low',
            style_inspiration: this.styleInspiration,
            breakdown: this.breakdown,
            feedback: this.corrections
        };

        const res = await fetch('/api/sports/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        // Show finish modal
        this.showSportsSummary(payload, data);
    }

    showSportsSummary(payload, serverResp) {
        const modalEl = document.getElementById('sportsSummaryModal');
        if (!modalEl) return;

        document.getElementById('summaryScore').textContent = Math.round(payload.score) + '/100';
        document.getElementById('summaryDuration').textContent = Math.round(payload.duration) + 's';
        document.getElementById('summaryXP').textContent = '+' + (serverResp.xp_earned || 0) + ' XP';

        const bsModal = new bootstrap.Modal(modalEl);
        bsModal.show();
    }
}
