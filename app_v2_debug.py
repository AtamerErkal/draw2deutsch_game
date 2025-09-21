import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import cv2
import tensorflow as tf
import random
import os

st.set_page_config(page_title="Pixi Debug", page_icon="🐞", layout="wide")

# -----------------------
# Load model & labels
# -----------------------
@st.cache_resource
def load_model_and_labels():
    model_path = 'model/quickdraw_model.h5'
    labels_path = 'model/labels.txt'
    model, labels = None, []
    try:
        with open(labels_path, 'r', encoding='utf-8') as f:
            labels = [line.strip() for line in f if line.strip()]
    except Exception as e:
        st.error(f"labels.txt yüklenemedi: {e}")
    try:
        if os.path.exists(model_path):
            model = tf.keras.models.load_model(model_path)
        else:
            st.error("quickdraw_model.h5 bulunamadı!")
    except Exception as e:
        st.error(f"Model yüklenemedi: {e}")
    return model, labels

model, labels = load_model_and_labels()

if not labels:
    st.stop()

# -----------------------
# Preprocess
# -----------------------
def preprocess_image(image_data, target_size=(28,28)):
    if image_data is None:
        return None
    img = (image_data * 255).astype(np.uint8) if image_data.max() <= 1 else image_data.astype(np.uint8)
    gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
    resized = cv2.resize(gray, target_size, interpolation=cv2.INTER_AREA)
    inverted = cv2.bitwise_not(resized)   # ters çevir
    norm = inverted.astype("float32") / 255.0
    return norm.reshape(1, target_size[0], target_size[1], 1)

# -----------------------
# UI
# -----------------------
st.title("🐞 Pixi Debug Mode")
st.write("Burada çizimini yap, ardından **top-5 tahminleri** göreceğiz.")

canvas = st_canvas(
    stroke_width=15,
    stroke_color="#000000",
    background_color="#FFFFFF",
    width=280,
    height=280,
    drawing_mode="freedraw",
    key="canvas_debug"
)

if st.button("Tahmin Et"):
    if canvas.image_data is not None and canvas.image_data.sum() > 0:
        proc = preprocess_image(canvas.image_data)
        if model:
            preds = model.predict(proc, verbose=0)[0]
            top5_idx = np.argsort(preds)[::-1][:5]
            debug_rows = []
            for i in top5_idx:
                debug_rows.append({
                    "Index": i,
                    "Label": labels[i] if i < len(labels) else "???",
                    "Prob (%)": round(preds[i]*100, 2)
                })
            st.subheader("Top-5 Tahminler")
            st.table(debug_rows)
        else:
            st.warning("Model yüklenemedi.")
    else:
        st.warning("Önce bir şeyler çiz!")
