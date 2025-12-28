function generateUnlockCode() {
    const now = new Date();
    const hourBlock = Math.floor(now.getTime() / 3600000);
    const dateStr = now.toISOString().split('T')[0];
    const input = `${CONFIG.SECRET}-${dateStr}-${hourBlock}`;
    
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
        hash = ((hash << 5) - hash) + input.charCodeAt(i);
        hash = hash & hash;
    }
    
    const code = Math.abs(hash % 1000000).toString().padStart(6, '0');
    document.getElementById('unlockCode').textContent = code;
    
    const minutesLeft = Math.ceil(((hourBlock + 1) * 3600000 - now.getTime()) / 60000);
    document.getElementById('expiresIn').textContent = `Valid for ${minutesLeft} minutes`;
}

function copyCode() {
    navigator.clipboard.writeText(document.getElementById('unlockCode').textContent)
        .then(() => showStatus('Code copied!', 'success'));
}
