/**
 * Kinesis AI — MediaPipe Pose & Camera Pipeline
 * Initializes webcam, tracks 33 body landmarks, draws high-contrast cyber-glow skeleton,
 * and streams normalized coordinates for deterministic biomechanical analysis.
 */

class KinesisPosePipeline {
    constructor(videoElement, canvasElement, options = {}) {
        this.video = videoElement;
        this.canvas = canvasElement;
        this.ctx = canvasElement.getContext('2d');
        this.options = Object.assign({
            modelComplexity: 1,
            smoothLandmarks: true,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5,
            onResults: null
        }, options);

        this.pose = null;
        this.camera = null;
        this.isRunning = false;
        this.lastLandmarks = null;
    }

    async init() {
        if (!window.Pose) {
            console.error('MediaPipe Pose library not loaded on page.');
            return false;
        }

        this.pose = new window.Pose({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
        });

        this.pose.setOptions({
            modelComplexity: this.options.modelComplexity,
            smoothLandmarks: this.options.smoothLandmarks,
            minDetectionConfidence: this.options.minDetectionConfidence,
            minTrackingConfidence: this.options.minTrackingConfidence
        });

        this.pose.onResults((results) => this._handlePoseResults(results));

        if (window.Camera) {
            this.camera = new window.Camera(this.video, {
                onFrame: async () => {
                    if (this.isRunning && this.video.readyState >= 2) {
                        await this.pose.send({ image: this.video });
                    }
                },
                width: 640,
                height: 480
            });
        }
        return true;
    }

    async start() {
        if (!this.pose) {
            await this.init();
        }
        this.isRunning = true;
        if (this.camera) {
            await this.camera.start();
        } else {
            // Fallback direct getUserMedia
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480, facingMode: 'user' },
                audio: false
            });
            this.video.srcObject = stream;
            await this.video.play();
            this._runManualFrameLoop();
        }
    }

    stop() {
        this.isRunning = false;
        if (this.camera) {
            this.camera.stop();
        }
        if (this.video && this.video.srcObject) {
            this.video.srcObject.getTracks().forEach(track => track.stop());
        }
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    async _runManualFrameLoop() {
        if (!this.isRunning) return;
        if (this.video.readyState >= 2) {
            await this.pose.send({ image: this.video });
        }
        requestAnimationFrame(() => this._runManualFrameLoop());
    }

    _handlePoseResults(results) {
        if (!this.canvas) return;

        // Match canvas dimensions to video
        if (this.canvas.width !== this.video.videoWidth && this.video.videoWidth > 0) {
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
        }

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        if (results.poseLandmarks) {
            this.lastLandmarks = results.poseLandmarks;
            this._drawCyberSkeleton(results.poseLandmarks);

            if (this.options.onResults) {
                this.options.onResults(results.poseLandmarks);
            }
        }
    }

    _drawCyberSkeleton(landmarks) {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        // MediaPipe Pose Connections
        const connections = [
            // Torso
            [11, 12], [12, 24], [24, 23], [23, 11],
            // Left Arm
            [11, 13], [13, 15],
            // Right Arm
            [12, 14], [14, 16],
            // Left Leg
            [23, 25], [25, 27], [27, 29], [29, 31],
            // Right Leg
            [24, 26], [26, 28], [28, 30], [30, 32],
            // Face & Head
            [0, 1], [1, 2], [2, 3], [0, 4], [4, 5], [5, 6]
        ];

        // 1. Draw glowing connection lines
        ctx.lineWidth = 4;
        ctx.strokeStyle = '#00f2fe';
        ctx.shadowColor = '#00f2fe';
        ctx.shadowBlur = 12;

        connections.forEach(([i, j]) => {
            const p1 = landmarks[i];
            const p2 = landmarks[j];
            if (p1 && p2 && (p1.visibility || 1) > 0.5 && (p2.visibility || 1) > 0.5) {
                ctx.beginPath();
                ctx.moveTo(p1.x * w, p1.y * h);
                ctx.lineTo(p2.x * w, p2.y * h);
                ctx.stroke();
            }
        });

        // 2. Draw glowing joint landmark nodes
        ctx.shadowBlur = 8;
        landmarks.forEach((p, idx) => {
            if ((p.visibility || 1) > 0.5) {
                const x = p.x * w;
                const y = p.y * h;

                // Major joint styling
                const isMajorJoint = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28].includes(idx);
                ctx.fillStyle = isMajorJoint ? '#00ff87' : '#ffffff';
                ctx.shadowColor = isMajorJoint ? '#00ff87' : '#00f2fe';

                ctx.beginPath();
                ctx.arc(x, y, isMajorJoint ? 5.5 : 3.5, 0, 2 * Math.PI);
                ctx.fill();
            }
        });

        // Reset shadow
        ctx.shadowBlur = 0;
    }
}
