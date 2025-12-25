# Git Repository Setup Guide

## Current Issue

The frontend has its own git repository (created by `create-next-app`), causing a nested repository situation.

## Recommended: Convert to Monorepo

### Quick Fix (5 minutes)

```bash
cd /Users/wlin/dev/pipeline-inspection

# 1. Remove frontend's separate git repository
rm -rf frontend/.git

# 2. Add frontend to main repository
git add frontend/

# 3. Check what will be committed
git status

# 4. Commit the integration
git commit -m "Integrate frontend into monorepo

- Add Next.js frontend application
- Real-time video streaming UI
- Detection log and system status
- Report generation interface
- Responsive design for desktop and mobile

Removed frontend's separate .git to consolidate into monorepo.
Backend and frontend are tightly coupled and should version together."

# 5. Verify clean state
git status
```

### Expected Output

After running the above:
```
On branch main
nothing to commit, working tree clean
```

---

## Why Monorepo?

### ✅ Advantages for This Project

1. **Tightly Coupled Components**
   - Backend API ↔ Frontend UI
   - WebSocket protocol
   - Shared data types

2. **Atomic Changes**
   ```bash
   # Single commit for API change + UI update
   git commit -m "Add new detection class

   - Backend: Add 'sediment' detection class
   - Frontend: Add sediment display in UI"
   ```

3. **Simplified Deployment**
   - One version number
   - One tag for release
   - Clear compatibility

4. **Easier Development**
   - One `git clone`
   - No submodule complexity
   - Shared scripts and configs

### ❌ When to Use Separate Repos

Only if:
- Frontend can work with multiple backends
- Different teams own different parts
- Independent release cycles
- Different deployment schedules

**For this project:** These don't apply. Monorepo is ideal.

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

## Alternative: Separate Repos (Not Recommended)

If you really want separate repos:

### Setup

```bash
# 1. Create separate frontend repo
cd /Users/wlin/dev
mkdir pipeline-inspection-frontend
mv pipeline-inspection/frontend/* pipeline-inspection-frontend/
cd pipeline-inspection-frontend
git init
git add .
git commit -m "Initial commit: Frontend"

# 2. Update main repo
cd ../pipeline-inspection
git rm -rf frontend
git commit -m "Remove frontend (moved to separate repo)"

# 3. Add frontend as submodule (optional)
git submodule add <frontend-repo-url> frontend
```

### Drawbacks

❌ More complex setup
❌ Versioning issues (which frontend works with which backend?)
❌ Two PRs for related changes
❌ Harder to keep in sync
❌ Git submodules are tricky

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

## Summary

### ✅ Do This (Monorepo)
```bash
cd /Users/wlin/dev/pipeline-inspection
rm -rf frontend/.git
git add frontend/
git commit -m "Integrate frontend into monorepo"
```

### ❌ Don't Do This (Separate Repos)
- Adds unnecessary complexity
- Versioning nightmare
- Not worth it for this project

---

## Quick Action

Run these commands now:

```bash
cd /Users/wlin/dev/pipeline-inspection

# Remove nested git repo
rm -rf frontend/.git

# Add frontend to main repo
git add frontend/

# Commit
git commit -m "Integrate frontend into monorepo

Backend and frontend are tightly coupled and should be versioned together.
This simplifies development, deployment, and version management."

# Verify
git status  # Should show: working tree clean
```

**Done!** You now have a clean monorepo. 🎉
