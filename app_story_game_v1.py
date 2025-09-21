# app_story_game.py
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import cv2
import random
import time
import tensorflow as tf
import os

st.set_page_config(page_title="Pixi'nin Macerası — Almanca Öğren", page_icon="🤖🖍️", layout="wide")

# -----------------------
# Load model & labels
# -----------------------
@st.cache_resource
def load_model_and_labels():
    model_path = "model/quickdraw_model.h5"
    labels_path = "model/labels.txt"
    model, labels = None, []
    try:
        with open(labels_path, "r", encoding="utf-8") as f:
            labels = [line.strip().lower() for line in f if line.strip()]
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

# -----------------------
# Word list (örnek kısaltılmış, sen 100 kelimelik listenle devam edebilirsin)
# -----------------------
WORD_DATA = [
    {"de": "der Hund", "en": "dog", "topic": "Hayvanlar"},
    {"de": "die Katze", "en": "cat", "topic": "Hayvanlar"},
    {"de": "der Vogel", "en": "bird", "topic": "Hayvanlar"},
    {"de": "der Fisch", "en": "fish", "topic": "Hayvanlar"},
    {"de": "der Apfel", "en": "apple", "topic": "Meyveler"},
    {"de": "die Banane", "en": "banana", "topic": "Meyveler"},
    {"de": "das Haus", "en": "house", "topic": "Ev"},
    {"de": "der Stuhl", "en": "chair", "topic": "Ev"},
    {"de": "das Auto", "en": "car", "topic": "Ulaşım"},
    {"de": "der Zug", "en": "train", "topic": "Ulaşım"},
]

# -----------------------
# Image preprocessing
# -----------------------
def preprocess_image(image_data, target_size=(28,28), dilate_iter=1):
    if image_data is None:
        return None
    try:
        img = (image_data*255).astype(np.uint8) if image_data.max()<=1.0 else image_data.astype(np.uint8)
        if img.shape[2]==4:
            alpha = img[:,:,3]/255.0
            rgb = img[:,:,:3].astype(np.float32)
            bg = np.ones_like(rgb)*255
            comp = (rgb*alpha[...,None]+bg*(1-alpha[...,None])).astype(np.uint8)
        else:
            comp = img[:,:,:3]
        gray = cv2.cvtColor(comp, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray,240,255,cv2.THRESH_BINARY)
        inv = cv2.bitwise_not(th)
        coords = cv2.findNonZero(inv)
        if coords is not None:
            x,y,w,h = cv2.boundingRect(coords)
            crop = gray[y:y+h,x:x+w]
        else:
            crop = gray
        h0,w0 = crop.shape[:2]
        side = max(h0,w0) if h0>0 and w0>0 else 28
        square = 255*np.ones((side,side),dtype=np.uint8)
        yoff=(side-h0)//2 if h0>0 else 0
        xoff=(side-w0)//2 if w0>0 else 0
        square[yoff:yoff+h0,xoff:xoff+w0]=crop
        resized = cv2.resize(square,target_size,interpolation=cv2.INTER_AREA)
        kernel=np.ones((2,2),np.uint8)
        dilated=cv2.dilate(resized,kernel,iterations=dilate_iter)
        inverted=cv2.bitwise_not(dilated)
        normalized=inverted.astype("float32")/255.0
        return normalized.reshape(1,target_size[0],target_size[1],1)
    except:
        return None

# -----------------------
# Prediction helper
# -----------------------
def predict_topk(processed, k=3):
    if processed is None: return []
    if model is None: return []
    preds = model.predict(processed,verbose=0)[0]
    idx=np.argsort(preds)[::-1][:k]
    return [(labels[i],float(preds[i])) for i in idx]

# -----------------------
# Session state
# -----------------------
if "round_idx" not in st.session_state: st.session_state.round_idx=0
if "play_words" not in st.session_state: st.session_state.play_words=[]
if "score" not in st.session_state: st.session_state.score=0
if "start" not in st.session_state: st.session_state.start=False
if "start_time" not in st.session_state: st.session_state.start_time=0

# -----------------------
# Sidebar settings
# -----------------------
with st.sidebar:
    st.header("Ayarlar")
    duration = st.slider("Süre (saniye)",10,30,20)
    rounds = st.slider("Tur sayısı",3,10,5)
    if st.button("Yeni Oyun"):
        pool=WORD_DATA.copy()
        random.shuffle(pool)
        st.session_state.play_words=pool[:rounds]
        st.session_state.round_idx=0
        st.session_state.score=0
        st.session_state.start=True
        st.session_state.start_time=time.time()
        st.experimental_rerun()

# -----------------------
# Main UI
# -----------------------
if not st.session_state.start:
    st.write("🎮 Oyuna başlamak için soldan 'Yeni Oyun' başlat!")
else:
    idx=st.session_state.round_idx
    if idx>=len(st.session_state.play_words):
        st.success(f"Oyun bitti! Skorun: {st.session_state.score}")
    else:
        current=st.session_state.play_words[idx]
        st.subheader(f"Çiz: **{current['de']}**  ({current['en']})")
        remaining=duration-int(time.time()-st.session_state.start_time)
        if remaining<0: remaining=0
        st.progress(remaining/duration)
        st.write(f"⏰ Kalan süre: {remaining} sn")
        canvas_result=st_canvas(
            stroke_width=8,stroke_color="#000",background_color="#FFF",
            width=400,height=400,drawing_mode="freedraw",key=f"canvas_{idx}",update_streamlit=True
        )
        preds=[]
        if canvas_result.image_data is not None and canvas_result.image_data.sum()>0:
            proc=preprocess_image(canvas_result.image_data)
            preds=predict_topk(proc)
            if preds:
                st.write("🤖 Pixi'nin tahminleri:")
                for p,prob in preds:
                    st.write(f"- {p} ({prob*100:.1f}%)")
        # kontrol: doğru bulundu mu?
        target=current["en"].lower()
        top_labels=[p[0].lower().replace("_"," ").replace("-"," ") for p,_ in preds]
        if target in top_labels:
            st.success("✅ Doğru! Pixi bildi 🎉")
            st.session_state.score+=5
            st.session_state.round_idx+=1
            st.session_state.start_time=time.time()
            st.experimental_rerun()
        elif remaining==0:
            st.error(f"❌ Süre bitti! Doğru cevap: {current['de']}")
            st.session_state.round_idx+=1
            st.session_state.start_time=time.time()
            st.experimental_rerun()
