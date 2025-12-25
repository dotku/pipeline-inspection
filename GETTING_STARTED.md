# Getting Started - Pipeline Inspection System

Choose your path based on what you need right now.

## 🎯 What Do You Want to Do?

### "I want to demo this to a client TODAY"
👉 **Use MacBook Pro** (10 minutes setup)

```bash
cd /Users/wlin/dev/pipeline-inspection
./start_macos.sh
```

Open http://localhost:3000 and you're live!

**See:** [macOS Demo Guide](deployment/macos/README_MACOS.md)

---

### "I need to test the concept"
👉 **Use Intel/PC or MacBook** (15 minutes setup)

**MacBook:**
```bash
./start_macos.sh
```

**PC/Linux:**
```bash
./start.sh
```

**See:** [Main README](README.md#installation-intelpc---development)

---

### "I'm ready to deploy to production"
👉 **Use ARM + NPU device** (2-3 weeks for full optimization)

**Quick test (10 min):**
```bash
# On ARM device
cd deployment/arm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_arm.txt
python test_tflite_inference.py --camera 0
```

**Full deployment:**
See [ARM Deployment Guide](deployment/arm/README_ARM.md)

---

## 📊 Quick Comparison

| What You Need | Use This | Setup Time | Performance |
|---------------|----------|------------|-------------|
| **Client demo today** | MacBook Pro | 10 min | 15-30 FPS ⭐ |
| **Test the concept** | MacBook/PC | 15 min | 8-18 FPS |
| **Develop custom model** | PC/Cloud GPU | 1 day | N/A |
| **Deploy to production** | ARM + NPU | 2-3 weeks | 30-60 FPS ⭐ |

---

## 🚀 Typical Project Timeline

### Week 1: Demo & Validation
- ✅ Setup on MacBook Pro (10 min)
- ✅ Demo to stakeholders
- ✅ Collect initial feedback
- ✅ Start collecting pipeline images

**Platform:** MacBook Pro
**Output:** Validated concept, stakeholder buy-in

---

### Week 2-3: Data Collection & Labeling
- 📸 Collect 500-1000 pipeline images
- 🏷️ Label defects using Roboflow/LabelImg
- 📊 Review data quality
- ✅ Prepare dataset for training

**Platform:** Any
**Output:** Labeled dataset ready for training

---

### Week 4-5: Model Training
- 🧠 Train custom YOLO model
- 📈 Validate accuracy (target: >90%)
- 🔄 Iterate on hyperparameters
- ✅ Export final model

**Platform:** PC/Cloud with GPU
**Output:** Custom trained YOLO model

---

### Week 6: ARM Testing
- 🔄 Convert model to TFLite
- 📱 Deploy to ARM device (FP32)
- 🧪 Test functionality
- 📊 Baseline performance (5-8 FPS)

**Platform:** ARM device
**Output:** System validated on ARM

---

### Week 7-8: NPU Optimization
- 🎯 INT8 quantization
- ⚡ NPU delegate integration
- 📊 Performance tuning (30-60 FPS)
- 🔒 Stability testing (24h run)

**Platform:** ARM + NPU
**Output:** Production-ready deployment

---

### Week 9+: Production Deployment
- 🚀 Deploy to field
- 📊 Monitor performance
- 🔧 Maintenance & updates
- 📈 Scale to more units

**Platform:** ARM + NPU
**Output:** System in production

---

## 💡 Pro Tips

### For Demos
1. **Pre-download the model** before client arrives
2. **Test camera** 5 minutes before demo
3. **Prepare sample objects** to detect
4. **Have a PDF report** ready to show
5. **Use MacBook M1/M2/M3** for best demo experience

### For Development
1. **Use version control** (git) from day 1
2. **Document your custom classes** in README
3. **Save example images** of each defect type
4. **Keep a changelog** of model versions

### For Production
1. **Always test on ARM device** before full deployment
2. **Use INT8 quantization** for NPU
3. **Validate accuracy** doesn't drop >2% after quantization
4. **Run 24h stability test** before field deployment
5. **Have rollback plan** (keep previous model version)

---

## 🆘 Common Questions

### Q: Which MacBook is best for demos?
**A:** Apple Silicon (M1/M2/M3) gives 15-30 FPS. Intel Mac gives 8-18 FPS. Both work, but M-series is noticeably smoother.

### Q: Do I need the same hardware for demo and production?
**A:** No! Demo on MacBook (convenient), deploy on ARM (efficient).

### Q: Can I skip the ARM testing phase?
**A:** Not recommended. Always validate on target hardware before production.

### Q: How long does model training take?
**A:**
- Small dataset (500 images): 2-4 hours
- Medium dataset (1000 images): 4-8 hours
- Large dataset (5000 images): 1-2 days
- Depends on GPU power

### Q: What if I don't have pipeline images yet?
**A:** Start with MacBook demo using generic object detection. Collect images during initial testing phase.

---

## 📂 Key Files & Folders

```
pipeline-inspection/
├── start_macos.sh          # ⭐ Quick start for MacBook
├── start.sh                # Quick start for PC/Linux
│
├── deployment/
│   ├── macos/              # 🍎 MacBook demo setup
│   │   └── README_MACOS.md # Full macOS guide
│   ├── arm/                # ⚡ Production deployment
│   │   ├── QUICKSTART_ARM.md
│   │   └── README_ARM.md
│   └── intel/              # PC deployment
│
├── scripts/
│   ├── convert_yolo_to_tflite.py  # Model conversion
│   └── benchmark.py               # Performance testing
│
├── backend/                # Python backend
├── frontend/              # Next.js frontend
├── models/                # YOLO models
└── reports/               # Generated reports
```

---

## 🎬 Your First Demo (Step by Step)

### 1. Setup (10 min)
```bash
cd /Users/wlin/dev/pipeline-inspection
./start_macos.sh
```

Wait for:
```
✅ System Started Successfully!
Frontend:  http://localhost:3000
```

### 2. Test Camera (1 min)
- Open http://localhost:3000
- Allow camera access if prompted
- Verify video feed appears

### 3. Test Detection (2 min)
- Point camera at objects (phone, cup, laptop, etc.)
- Watch detection boxes appear in real-time
- Check detection log on right side

### 4. Generate Report (2 min)
- Click "Generate Report"
- Fill in:
  - Location: "Demo Office"
  - Inspector: "Your Name"
  - Notes: "Client demonstration"
- Click "PDF + JSON"
- Download and open PDF

### 5. Present (10 min)
- Show live detection
- Explain confidence scores
- Display detection log
- Present professional PDF report
- Discuss production deployment (ARM + NPU)

**Total demo time: ~15 minutes**

---

## 🎯 Next Steps

Choose based on your stage:

### Just Starting?
👉 [Run MacBook Demo](deployment/macos/README_MACOS.md)

### Ready to Customize?
👉 [Train Custom Model](README.md#training-custom-model)

### Going to Production?
👉 [ARM Deployment Guide](deployment/arm/README_ARM.md)

### Need Help Deciding?
👉 [Deployment Decision Guide](DEPLOYMENT_GUIDE.md)

---

## 📞 Quick Links

- **MacBook Demo**: [deployment/macos/README_MACOS.md](deployment/macos/README_MACOS.md)
- **ARM Production**: [deployment/arm/README_ARM.md](deployment/arm/README_ARM.md)
- **ARM Quick Start**: [deployment/arm/QUICKSTART_ARM.md](deployment/arm/QUICKSTART_ARM.md)
- **Full Documentation**: [README.md](README.md)
- **Decision Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

**Most common path:**
1. Demo on MacBook → 2. Collect data → 3. Train model → 4. Deploy on ARM 🚀

**Fastest demo:**
```bash
./start_macos.sh
# Open http://localhost:3000
```

**Let's get started! 🎉**
