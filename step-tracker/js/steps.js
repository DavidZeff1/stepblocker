let steps = 0;
let isTracking = false;
let lastAccel = { x: 0, y: 0, z: 0 };
let stepThreshold = 12;
let lastStepTime = 0;
let challengeStartTime = null;

function loadState() {
    const saved = localStorage.getItem('stepChallenge');
    if (saved) {
        const state = JSON.parse(saved);
        if (Date.now() - state.startTime > 24 * 60 * 60 * 1000) {
            localStorage.removeItem('stepChallenge');
            return;
        }
        steps = state.steps || 0;
        challengeStartTime = state.startTime;
    }
}

function saveState() {
    localStorage.setItem('stepChallenge', JSON.stringify({
        steps: steps,
        startTime: challengeStartTime || Date.now()
    }));
}

function startTracking() {
    if (!window.DeviceMotionEvent) {
        showStatus('Motion not supported. Enter steps manually.', 'error');
        return;
    }
    
    if (typeof DeviceMotionEvent.requestPermission === 'function') {
        DeviceMotionEvent.requestPermission()
            .then(r => {
                if (r === 'granted') enableTracking();
                else showStatus('Permission denied. Enter steps manually.', 'error');
            })
            .catch(() => showStatus('Could not request permission.', 'error'));
    } else {
        enableTracking();
    }
}

function enableTracking() {
    isTracking = true;
    challengeStartTime = challengeStartTime || Date.now();
    window.addEventListener('devicemotion', handleMotion);
    document.getElementById('startBtn').classList.add('hidden');
    document.getElementById('stopBtn').classList.remove('hidden');
    showStatus('📍 Tracking... Walk with your phone!', 'tracking');
}

function stopTracking() {
    isTracking = false;
    window.removeEventListener('devicemotion', handleMotion);
    document.getElementById('startBtn').classList.remove('hidden');
    document.getElementById('stopBtn').classList.add('hidden');
    document.getElementById('statusBox').classList.add('hidden');
    saveState();
}

function handleMotion(e) {
    const a = e.accelerationIncludingGravity;
    if (!a || a.x === null) return;
    
    const now = Date.now();
    const mag = Math.sqrt(
        Math.pow(Math.abs(a.x - lastAccel.x), 2) +
        Math.pow(Math.abs(a.y - lastAccel.y), 2) +
        Math.pow(Math.abs(a.z - lastAccel.z), 2)
    );
    
    if (mag > stepThreshold && (now - lastStepTime) > 300) {
        steps++;
        lastStepTime = now;
        updateUI();
        saveState();
    }
    
    lastAccel = { x: a.x, y: a.y, z: a.z };
}

function setManualSteps() {
    const v = parseInt(document.getElementById('manualSteps').value, 10);
    if (isNaN(v) || v < 0) {
        showStatus('Enter a valid number', 'error');
        return;
    }
    steps = v;
    challengeStartTime = challengeStartTime || Date.now();
    updateUI();
    saveState();
    document.getElementById('manualSteps').value = '';
    showStatus('Steps updated!', 'success');
}
