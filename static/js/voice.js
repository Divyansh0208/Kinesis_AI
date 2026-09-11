/**
 * Kinesis AI — Bilingual Hindi + English Voice Coach Controller
 * Uses Web Speech API for speech recognition and audio synthesis.
 */

class KinesisVoiceCoach {
    constructor(config = {}) {
        this.statusText = document.getElementById('voiceStatusText');
        this.waveContainer = document.getElementById('voiceWave');
        this.chatLog = document.getElementById('voiceChatLog');
        this.recordBtn = document.getElementById('voiceRecordBtn');
        this.micIcon = document.getElementById('voiceMicIcon');
        this.langSelect = document.getElementById('voiceLangSelect');

        this.recognition = null;
        this.isRecording = false;
        this.currentLang = 'en-IN';

        this.initSpeechRecognition();
    }

    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            if (this.statusText) {
                this.statusText.textContent = "Speech recognition not supported in this browser. You can type queries below.";
            }
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = this.langSelect ? this.langSelect.value : 'en-IN';

        this.recognition.onstart = () => {
            this.isRecording = true;
            if (this.waveContainer) this.waveContainer.classList.remove('d-none');
            if (this.statusText) this.statusText.textContent = "Listening... Speak now (Hindi or English)";
            if (this.recordBtn) this.recordBtn.classList.add('btn-danger');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.appendMessage('user', transcript);
            this.sendToAICoach(transcript);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            if (this.statusText) this.statusText.textContent = `Listening stopped (${event.error}). Click to speak again.`;
            this.resetRecordingUI();
        };

        this.recognition.onend = () => {
            this.resetRecordingUI();
        };

        if (this.langSelect) {
            this.langSelect.addEventListener('change', () => {
                this.currentLang = this.langSelect.value;
                if (this.recognition) this.recognition.lang = this.currentLang;
            });
        }
    }

    toggleRecording() {
        if (!this.recognition) {
            alert('Speech recognition is not supported in this browser.');
            return;
        }

        if (this.isRecording) {
            this.recognition.stop();
            this.resetRecordingUI();
        } else {
            this.recognition.lang = this.langSelect ? this.langSelect.value : 'en-IN';
            this.recognition.start();
        }
    }

    resetRecordingUI() {
        this.isRecording = false;
        if (this.waveContainer) this.waveContainer.classList.add('d-none');
        if (this.recordBtn) this.recordBtn.classList.remove('btn-danger');
        if (this.statusText) this.statusText.textContent = "Click the microphone to ask your Voice Coach";
    }

    async sendToAICoach(query) {
        if (this.statusText) this.statusText.textContent = "AI Coach thinking...";

        try {
            const res = await fetch('/api/voice/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            const data = await res.json();
            const reply = data.text || "Keep moving with confidence!";
            this.appendMessage('coach', reply, data.provider);

            // Audio Speech Synthesis
            const langCode = data.lang === 'hi' ? 'hi-IN' : 'en-US';
            KinesisAudio.speak(reply, langCode);

            if (this.statusText) this.statusText.textContent = "Ready. Click mic to speak again.";
        } catch (e) {
            console.error('Voice coach query error:', e);
            this.appendMessage('coach', "Aapka form badhiya tha! Focus on steady movement.");
        }
    }

    appendMessage(sender, text, provider = null) {
        if (!this.chatLog) return;

        const isUser = sender === 'user';
        const msgDiv = document.createElement('div');
        msgDiv.className = `d-flex mb-3 ${isUser ? 'justify-content-end' : 'justify-content-start'}`;

        msgDiv.innerHTML = `
            <div class="p-3 rounded-4 ${isUser ? 'bg-neon-cyan text-dark fw-semibold' : 'bg-dark border border-secondary text-light'}" style="max-width: 80%;">
                <div class="d-flex align-items-center gap-2 mb-1">
                    <i class="bi ${isUser ? 'bi-person-fill' : 'bi-activity text-neon-green'}"></i>
                    <strong class="fs-8">${isUser ? 'You' : 'Kinesis Voice Coach'}</strong>
                    ${provider ? `<span class="badge bg-secondary-subtle text-light border border-secondary fs-8">${provider}</span>` : ''}
                </div>
                <div>${text}</div>
            </div>
        `;
        this.chatLog.appendChild(msgDiv);
        this.chatLog.scrollTop = this.chatLog.scrollHeight;
    }
}
