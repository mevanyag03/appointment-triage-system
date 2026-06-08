# MediAI — AI Based Healthcare Assistant

A proof-of-concept platform demonstrating how AI can assist in clinical healthcare workflows. Built as AI in Healthcare project - AIESEC Global Volunteering Project SkillUp at the Department of Computer Science and Engineering, MM(DU), Ambala,Haryana.

---

## Modules

### 🏥 Module 1 — Patient Triage & Appointment System

Symptom-based patient intake system that evaluates severity and assigns priority levels to manage doctor queues efficiently.

**Features**

- Patient symptom input form
- Rule-based priority classification: Emergency / Urgent / Normal / Routine
- Live appointment queue management

**Run**

```bash
cd appointment-triage-system
pip install -r requirements.txt
streamlit run app.py
```

---

### 🫁 Module 2 — Chest X-Ray Pneumonia Detector

Deep learning model trained on 5,216 chest X-ray images to assist in pneumonia detection with visual explainability.

**Features**

- ResNet-50 transfer learning model
- Binary classification: Normal vs Pneumonia
- 84.78% test accuracy, 96% pneumonia recall
- Grad-CAM heatmaps showing model focus regions

**Run**

```bash
cd xray_app
pip install -r requirements.txt
streamlit run app.py
```

---

## Homepage

Open `index.html` directly in any browser — no setup needed. Links to both modules.

---

## Project Structure

```
appointment-triage-system/
│
├── index.html              # Homepage
├── README.md               # This file
│
├── Appointment/           # Triage & appointment app
├── app.py
├── triage_logic.py        # Priority assignment logic
├── patient_dataset.csv
├── patients.csv           # Patient queue data
│
└── xray_app/
    ├── app.py              # X-ray analyser app
    └── xray_model.pth      # Trained ResNet-50 model
    └── requirements.txt
```

---

## Tech Stack

- Python, Streamlit
- PyTorch, torchvision
- ResNet-50 (transfer learning)
- OpenCV, PIL, Matplotlib

---

## Dataset

Chest X-Ray Images (Pneumonia) — Kaggle  
5,216 training images · 624 test images · Binary classification

---

## Disclaimer

This platform is built for educational and demonstration purposes only. It is not intended for clinical use or medical decision making.
