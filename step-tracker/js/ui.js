function updateUI() {
    const percent = Math.min(100, (steps / CONFIG.TARGET_STEPS) * 100);
    const remaining = Math.max(0, CONFIG.TARGET_STEPS - steps);
    
    document.getElementById('stepCount').textContent = steps.toLocaleString();
    document.getElementById('remaining').textContent = remaining.toLocaleString();
    document.getElementById('progress').textContent = Math.round(percent) + '%';
    document.getElementById('progressCircle').style.strokeDashoffset = 553 - (percent / 100) * 553;
    
    if (steps >= CONFIG.TARGET_STEPS) {
        document.getElementById('unlockSection').classList.remove('hidden');
        generateUnlockCode();
    } else {
        document.getElementById('unlockSection').classList.add('hidden');
    }
}

function showStatus(message, type) {
    const box = document.getElementById('statusBox');
    box.textContent = message;
    box.className = `status ${type}`;
    box.classList.remove('hidden');
    if (type !== 'tracking') {
        setTimeout(() => box.classList.add('hidden'), 3000);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadState();
    updateUI();
    
    // Refresh code every minute
    setInterval(() => {
        if (steps >= CONFIG.TARGET_STEPS) {
            generateUnlockCode();
        }
    }, 60000);
});
