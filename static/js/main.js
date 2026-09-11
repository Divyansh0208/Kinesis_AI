/**
 * Kinesis AI — Global JavaScript Utilities
 * SIH 2026 Edition
 */

document.addEventListener('DOMContentLoaded', () => {
    initAIStatusPoller();
});

/**
 * Polls backend AI status and updates header badge (Ollama / Gemini / None)
 */
function initAIStatusPoller() {
    const aiBadge = document.getElementById('aiEngineBadge');
    const aiText = document.getElementById('aiEngineText');
    if (!aiBadge || !aiText) return;

    fetch('/api/status')
        .then(res => res.json())
        .then(data => {
            if (data && data.ai) {
                const ai = data.ai;
                if (ai.ollama_available) {
                    aiText.textContent = `AI: Ollama (${ai.ollama_model || 'Local'})`;
                    aiBadge.className = 'd-none d-md-flex align-items-center gap-2 px-3 py-1 rounded-pill bg-dark border border-success text-success fs-8';
                } else if (ai.gemini_available) {
                    aiText.textContent = 'AI: Gemini (Cloud Fallback)';
                    aiBadge.className = 'd-none d-md-flex align-items-center gap-2 px-3 py-1 rounded-pill bg-dark border border-info text-info fs-8';
                } else {
                    aiText.textContent = 'AI: Rule Engine (Offline)';
                    aiBadge.className = 'd-none d-md-flex align-items-center gap-2 px-3 py-1 rounded-pill bg-dark border border-secondary text-secondary fs-8';
                }
            }
        })
        .catch(err => console.debug('AI Status poll silent failure:', err));
}

/**
 * Synthesizes short audio tone / voice feedback for quality reps & warnings
 */
class KinesisAudio {
    static playRepTone() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
            osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15); // A5
            gain.gain.setValueAtTime(0.2, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.2);
        } catch (e) {
            // AudioContext not permitted or disabled
        }
    }

    static playAlertTone() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(300, ctx.currentTime);
            osc.frequency.setValueAtTime(200, ctx.currentTime + 0.1);
            gain.gain.setValueAtTime(0.25, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.25);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.25);
        } catch (e) {}
    }

    static speak(text, lang = 'en-US') {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.05;
        utterance.pitch = 1.0;
        utterance.lang = lang;
        window.speechSynthesis.speak(utterance);
    }
}

/**
 * Shows transient toast notification
 */
function showKinesisToast(title, message, type = 'info') {
    const toastContainer = document.getElementById('kinesisToastContainer') || createToastContainer();
    const toastEl = document.createElement('div');
    toastEl.className = `alert alert-${type} shadow-lg border-0 d-flex align-items-center gap-2 mb-2`;
    toastEl.style.minWidth = '280px';
    toastEl.innerHTML = `
        <i class="bi bi-bell-fill fs-5"></i>
        <div>
            <strong>${title}</strong>
            <div class="small">${message}</div>
        </div>
    `;
    toastContainer.appendChild(toastEl);
    setTimeout(() => {
        toastEl.style.opacity = '0';
        toastEl.style.transition = 'opacity 0.4s ease';
        setTimeout(() => toastEl.remove(), 400);
    }, 3500);
}

function createToastContainer() {
    const div = document.createElement('div');
    div.id = 'kinesisToastContainer';
    div.className = 'position-fixed bottom-0 end-0 p-3';
    div.style.zIndex = '9999';
    document.body.appendChild(div);
    return div;
}
