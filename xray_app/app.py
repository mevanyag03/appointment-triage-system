import streamlit as st
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import torch.nn.functional as F

# Page config
st.set_page_config(page_title="Chest X-Ray Analyzer", layout="wide")
st.title("🫁 Chest X-Ray Pneumonia Detector")
st.markdown("Upload a chest X-ray image to detect pneumonia using AI")

# Load model
@st.cache_resource
def load_model():
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 2)
    model.load_state_dict(torch.load('xray_model.pth', map_location='cpu'))
    model.eval()
    return model

model = load_model()

# Transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Upload
uploaded = st.file_uploader("Upload chest X-ray", type=["jpg", "jpeg", "png"])

if uploaded:
    img = Image.open(uploaded).convert('RGB')
    st.image(img, caption="Uploaded X-ray", width=300)

    tensor = transform(img).unsqueeze(0)

    with torch.no_grad():
        output = model(tensor)
        probs = F.softmax(output, dim=1)[0]
        pred = output.argmax().item()

    label = "PNEUMONIA" if pred == 1 else "NORMAL"
    confidence = probs[pred].item()

    st.subheader("Result")
    if pred == 1:
        st.error(f"🚨 {label} detected — Confidence: {confidence:.2%}")
    else:
        st.success(f"✅ {label} — Confidence: {confidence:.2%}")

    st.info("⚠️ This tool is for educational purposes only. Not a substitute for clinical diagnosis.")