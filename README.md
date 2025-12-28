# StepBlocker 🚶‍♂️🛡️

A website blocker for Mac that requires you to walk 2,000 steps before you can unblock sites.

**Blocking = easy.** Click a button.  
**Unblocking = hard.** Walk 2,000 steps first.

## Quick Start

### 1. Download

```bash
git clone https://github.com/DavidZeff1/stepblocker.git
cd stepblocker
```

Or click the green "Code" button above → "Download ZIP"

### 2. Run

```bash
python3 stepblocker.py
```

That's it. No installation needed.

## How It Works

1. **Block sites** - Type a domain or click a preset (Social, YouTube, etc.), enter your Mac password
2. **Try to unblock** - App asks for a 6-digit code
3. **Walk 2,000 steps** - Open `step-tracker/index.html` on your phone
4. **Get the code** - Enter it in the app
5. **Site unblocked** - After entering your Mac password

## Requirements

- macOS (any recent version)
- Python 3 (comes pre-installed on Mac)

## Files

```
stepblocker/
├── stepblocker.py      ← Run this on your Mac
├── step-tracker/
│   └── index.html      ← Open this on your phone
└── README.md
```

## Step Tracker Options

The step tracker works in 3 ways:

1. **Motion tracking** - Walk with phone in pocket (needs HTTPS)
2. **Manual entry** - Check your phone's Health app, type the number
3. **Host online** - Put it on GitHub Pages for easy phone access

### Hosting on GitHub Pages (optional)

1. Fork this repo
2. Go to Settings → Pages → Enable from main branch
3. Access at `https://YOURUSERNAME.github.io/stepblocker/step-tracker/`

## FAQ

**Q: Can I cheat?**  
A: Yes. This is friction, not security. The goal is to make unblocking annoying enough that you don't do it impulsively.

**Q: Does it need internet?**  
A: No. Everything runs locally.

**Q: How does blocking work?**  
A: It adds entries to `/etc/hosts` that redirect blocked domains to `127.0.0.1`.

**Q: Why do I need my Mac password?**  
A: Editing `/etc/hosts` requires admin privileges.

## License

MIT - Do whatever you want with it.
