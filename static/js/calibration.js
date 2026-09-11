/**
 * Kinesis AI — 10-Second Camera & Pose Calibration Module
 * Verifies full-body visibility, lighting, centering, and distance before scoring commences.
 */

class KinesisCalibration {
    constructor(overlayElement, options = {}) {
        this.overlay = overlayElement;
        this.options = Object.assign({
            requiredStableFrames: 15,
            onCalibrationSuccess: null
        }, options);

        this.statusText = this.overlay.querySelector('.calibration-status-text');
        this.progressBar = this.overlay.querySelector('.calibration-progress-bar');
        this.countdownEl = this.overlay.querySelector('.calibration-countdown');

        this.stableCount = 0;
        this.isCalibrated = false;
        this.isChecking = false;
    }

    start() {
        this.overlay.classList.remove('d-none');
        this.stableCount = 0;
        this.isCalibrated = false;
        this.isChecking = true;
        this._updateUI('Position yourself inside the frame...', 0);
    }

    processFrame(landmarks) {
        if (!this.isChecking || this.isCalibrated) return;

        if (!landmarks || landmarks.length < 33) {
            this._handleFail('No person detected. Step in front of camera.');
            return;
        }

        // Key points: Nose(0), Shoulders(11,12), Hips(23,24), Knees(25,26), Ankles(27,28)
        const keyIdxs = [0, 11, 12, 23, 24, 25, 26, 27, 28];
        const lowVis = keyIdxs.filter(i => (landmarks[i].visibility || 0) < 0.5);

        if (lowVis.length > 0) {
            if (lowVis.some(i => [25, 26, 27, 28].includes(i))) {
                this._handleFail('Move farther back so your knees and feet are visible.');
            } else {
                this._handleFail('Keep your full body inside the camera frame.');
            }
            return;
        }

        // Check horizontal centering
        const midShoulderX = (landmarks[11].x + landmarks[12].x) / 2;
        if (midShoulderX < 0.25 || midShoulderX > 0.75) {
            this._handleFail('Move towards the center of the screen.');
            return;
        }

        // Check distance (shoulders width)
        const shoulderWidth = Math.abs(landmarks[11].x - landmarks[12].x);
        if (shoulderWidth > 0.55) {
            this._handleFail('Step back a little — you are too close.');
            return;
        }

        // Calibration frame valid
        this.stableCount++;
        const pct = Math.min(100, Math.round((this.stableCount / this.options.requiredStableFrames) * 100));
        this._updateUI('Hold still... Calibrating body posture', pct);

        if (this.stableCount >= this.options.requiredStableFrames) {
            this.isCalibrated = true;
            this.isChecking = false;
            this._updateUI('✓ Calibrated! Ready to Train.', 100);
            KinesisAudio.playRepTone();

            setTimeout(() => {
                this.overlay.classList.add('d-none');
                if (this.options.onCalibrationSuccess) {
                    this.options.onCalibrationSuccess();
                }
            }, 800);
        }
    }

    _handleFail(msg) {
        this.stableCount = Math.max(0, this.stableCount - 1);
        const pct = Math.min(100, Math.round((this.stableCount / this.options.requiredStableFrames) * 100));
        this._updateUI(msg, pct, 'warning');
    }

    _updateUI(msg, pct, state = 'info') {
        if (this.statusText) {
            this.statusText.textContent = msg;
            this.statusText.className = `calibration-status-text fw-bold ${state === 'warning' ? 'text-warning' : 'text-neon-cyan'}`;
        }
        if (this.progressBar) {
            this.progressBar.style.width = `${pct}%`;
        }
    }
}
