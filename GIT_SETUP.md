# Git Monorepo Setup Guide

## Fix Nested Repository Issue

The frontend has its own git repository (created by `create-next-app`). Let's fix this:

### Quick Fix (30 seconds)

```bash
cd /Users/wlin/dev/pipeline-inspection

# Remove frontend's separate git repository
rm -rf frontend/.git

# Add frontend to main repository
git add frontend/

# Commit the integration
git commit -m "Integrate frontend into monorepo

Backend and frontend are tightly coupled and should version together."

# Verify clean state
git status  # Should show: working tree clean
```

✅ **Done!** Now you have a clean monorepo.

---

## Git Workflow (Monorepo)

### Initial Setup

```bash
# Clone (one command)
git clone <repo-url>
cd pipeline-inspection

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install

# Ready to develop!
```

### Daily Development

```bash
# Make changes to both backend and frontend
# ...

# Commit related changes together
git add backend/app.py frontend/components/VideoStream.tsx
git commit -m "Update video streaming protocol

- Backend: Add FPS metadata to WebSocket
- Frontend: Display FPS in UI"

# Or commit everything
git add .
git commit -m "Add new defect type: sediment"
```

### Branching Strategy

```bash
# Feature branch
git checkout -b feature/add-sediment-detection

# Make changes to backend and/or frontend
# ...

# Commit
git commit -am "Add sediment detection"

# Push
git push origin feature/add-sediment-detection

# Create PR
gh pr create --title "Add sediment detection"
```

---


## Current Repository Structure (Monorepo)

```
pipeline-inspection/                    # Git root
├── .git/                              # Single git repository
├── .gitignore                         # Shared ignore rules
│
├── backend/                           # Python backend
│   ├── app.py
│   ├── camera.py
│   ├── yolo_detector.py
│   └── ...
│
├── frontend/                          # Next.js frontend
│   ├── app/
│   ├── components/
│   └── ...
│
├── deployment/                        # Deployment configs
│   ├── arm/
│   ├── macos/
│   └── intel/
│
├── scripts/                           # Shared scripts
├── docs/                              # Documentation
└── README.md
```

---

## .gitignore Strategy

Already configured correctly in root `.gitignore`:

```gitignore
# Backend (Python)
backend/venv/
backend/__pycache__/
backend/*.pyc
backend/.env

# Frontend (Node.js)
frontend/node_modules/
frontend/.next/
frontend/out/
frontend/.env*.local

# Generated files
models/*.pt
models/*.tflite
reports/*.pdf
reports/*.json

# System
.DS_Store
*.log
.vscode/
.idea/
```

---

## Commit Message Convention

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Examples

**Backend change:**
```
feat(backend): Add INT8 quantization support

- Add quantization script
- Update model loading to support TFLite
- Add NPU delegate configuration
```

**Frontend change:**
```
fix(frontend): Fix WebSocket reconnection logic

- Retry connection every 3 seconds
- Show connection status in UI
- Clear video on disconnect
```

**Full-stack change:**
```
feat: Add sediment detection class

Backend:
- Add 'sediment' to defect classes
- Update YOLO model config
- Add sediment color to annotation

Frontend:
- Add sediment icon to detection log
- Update type definitions
- Add sediment to report template
```

---

## Release Workflow

```bash
# 1. Update version
# Edit package.json, pyproject.toml, etc.

# 2. Commit version bump
git add .
git commit -m "chore: Bump version to v1.1.0"

# 3. Tag release
git tag -a v1.1.0 -m "Release v1.1.0

Features:
- Add ARM+NPU deployment support
- Add macOS optimization
- Add INT8 quantization

Improvements:
- 30-60 FPS on ARM+NPU
- Better error handling
- Updated documentation"

# 4. Push with tags
git push origin main --tags

# 5. Create GitHub release
gh release create v1.1.0 --title "v1.1.0" --notes "See CHANGELOG.md"
```

---

## CI/CD with Monorepo

Example GitHub Actions (`.github/workflows/ci.yml`):

```yaml
name: CI

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Build
        run: |
          cd frontend
          npm run build
      - name: Run tests
        run: |
          cd frontend
          npm test
```

---

## Monorepo Benefits

This project uses a monorepo because:

✅ **Atomic commits** - Change backend API + frontend UI together
✅ **Version sync** - One version number, always compatible
✅ **Simplified deployment** - One tag = one release
✅ **Easier development** - One `git clone`, no submodules

---

## Next Steps

After fixing the nested repo:

1. ✅ Continue normal development
2. ✅ Commit related changes together
3. ✅ Tag releases as a single unit
