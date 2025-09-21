# app_v2_child.py
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import cv2
import random
import time
import tensorflow as tf
import os

# -----------------------
# App meta & style
# -----------------------
st.set_page_config(page_title="Pixi ile Çiz ve Öğren!", page_icon="🖍️", layout="wide")

# Kid-friendly CSS
st.markdown("""
<style>
:root{
  --primary:#FF6F61;
  --accent:#FFD166;
  --bg:#FFF9F2;
  --card:#FFFFFF;
}
body { background: linear-gradient(180deg, #FFFDF9 0%, #F7F5FF 100%); }
.header {
  font-family: "Trebuchet MS", Helvetica, sans-serif;
  color: #2C2C54;
  text-align: center;
  padding: 1rem;
}
.sub {
  text-align:center;
  color: #444;
  margin-top:-12px;
  margin-bottom:18px;
}
.topbar {
  background: linear-gradient(90deg, var(--primary), #FF9A8B);
  color: white;
  padding: 12px 18px;
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}
.canvas-card {
  background: var(--card);
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}
.pixibox {
  background: linear-gradient(180deg, #fff6f6, #fff9f2);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 10px;
  text-align:center;
  font-weight:600;
}
.pred-item { padding:8px 6px; border-radius:10px; margin-bottom:6px; }
.correct { background: linear-gradient(90deg,#D4F8E8,#E8FFF2); }
.wrong { background:linear-gradient(90deg,#FFF4F4,#FFF9F9); }
.small-muted { color:#666; font-size:0.9rem; }
.footer-note { color:#777; font-size:0.9rem; margin-top:8px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h1>🎨 Pixi ile Çiz & Öğren</h1></div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Verilen Almanca kelimeyi çiz, Pixi tahmin etsin, puan kazan! (Çocuk dostu arayüz)</div>", unsafe_allow_html=True)

# -----------------------
# Load model & labels
# -----------------------
@st.cache_resource
def load_model_and_labels():
    model_path = 'model/quickdraw_model.h5'
    labels_path = 'model/labels.txt'
    model = None
    labels = []
    # Load labels
    try:
        with open(labels_path, 'r', encoding='utf-8') as f:
            labels = [line.strip() for line in f if line.strip()]
    except Exception as e:
        st.error(f"labels.txt yüklenirken hata: {e}")
        labels = []
    # Load model
    try:
        if os.path.exists(model_path):
            model = tf.keras.models.load_model(model_path)
        else:
            st.warning("Model dosyası bulunamadı; rastgele tahmin moduna döner.")
            model = None
    except Exception as e:
        st.error(f"Model yüklenemedi: {e}")
        model = None
    return model, labels

model, labels = load_model_and_labels()

if not labels:
    st.error("Etiketler (labels.txt) bulunamadı veya boş. Oyun başlatılamıyor.")
    st.stop()

# -----------------------
# Helpers
# -----------------------
def preprocess_image(image_data, target_size=(28,28)):
    """
    image_data: RGBA numpy array from streamlit canvas
    returns: (1, h, w, 1) float32 normalized image or None
    """
    if image_data is None:
        return None
    try:
        # Convert to uint8 if needed
        img = (image_data * 255).astype(np.uint8) if image_data.max() <= 1.0 else image_data.astype(np.uint8)
        # If has alpha channel, composite onto white background using alpha
        if img.shape[2] == 4:
            alpha = img[:,:,3] / 255.0
            # create white background
            bg = np.ones_like(img[:,:,:3], dtype=np.uint8) * 255
            img_rgb = (img[:,:,:3].astype(np.float32) * alpha[...,None] + bg.astype(np.float32) * (1-alpha[...,None])).astype(np.uint8)
        else:
            img_rgb = img[:,:,:3]
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        # Crop to bounding box of drawing to reduce whitespace (improves recognition)
        coords = cv2.findNonZero(255 - gray)  # find where lines exist (assuming lines darker)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            crop = gray[y:y+h, x:x+w]
        else:
            crop = gray
        # Resize with aspect ratio preserved, pad to square
        h0, w0 = crop.shape[:2]
        if h0 == 0 or w0 == 0:
            resized = cv2.resize(gray, target_size, interpolation=cv2.INTER_AREA)
        else:
            # scale
            scale = max(h0, w0)
            # create square canvas
            square = 255 * np.ones((scale, scale), dtype=np.uint8)
            # center crop on square
            y_off = (scale - h0)//2
            x_off = (scale - w0)//2
            square[y_off:y_off+h0, x_off:x_off+w0] = crop
            resized = cv2.resize(square, target_size, interpolation=cv2.INTER_AREA)
        # invert (QuickDraw expects dark background? we ensure white background -> black strokes)
        inverted = cv2.bitwise_not(resized)
        normalized = inverted.astype('float32') / 255.0
        processed = normalized.reshape(1, target_size[0], target_size[1], 1)
        return processed
    except Exception as e:
        st.error(f"Ön işlem hatası: {e}")
        return None

def model_predict_topk(processed, k=3):
    """Return list of (label, prob) sorted by prob desc."""
    if model is None:
        # fallback random
        picks = random.sample(labels, min(k, len(labels)))
        return [(p, round(1.0/len(picks), 2)) for p in picks]
    try:
        preds = model.predict(processed, verbose=0)
        probs = preds[0]
        top_idx = np.argsort(probs)[::-1][:k]
        return [(labels[i], float(probs[i])) for i in top_idx]
    except Exception as e:
        st.error(f"Tahmin sırasında hata: {e}")
        # fallback
        picks = random.sample(labels, min(k, len(labels)))
        return [(p, round(1.0/len(picks), 2)) for p in picks]

# -----------------------
# Game state init
# -----------------------
if 'score' not in st.session_state: st.session_state.score = 0
if 'round' not in st.session_state: st.session_state.round = 1
if 'total_rounds' not in st.session_state: st.session_state.total_rounds = 7
if 'current_word' not in st.session_state:
    st.session_state.current_word = random.choice(labels)
if 'round_active' not in st.session_state: st.session_state.round_active = False
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'last_guess' not in st.session_state: st.session_state.last_guess = None
if 'top_preds' not in st.session_state: st.session_state.top_preds = []

# -----------------------
# Sidebar controls
# -----------------------
with st.sidebar:
    st.header("Ayarlar 🎨")
    stroke_color = st.color_picker("Çizgi rengi", value="#000000")
    stroke_width = st.slider("Kalınlık", 4, 60, 20)
    bg_color = st.color_picker("Arka plan rengi", value="#FFFFFF")
    rounds = st.number_input("Tur sayısı", min_value=1, max_value=20, value=st.session_state.total_rounds, step=1)
    st.session_state.total_rounds = int(rounds)
    st.markdown("---")
    st.markdown("**Puanlama:**\n- Hızlı ve doğru -> daha çok puan\n- Her tur zaman: 25s")
    st.markdown("---")
    if st.button("Yeni Oyun Başlat"):
        st.session_state.score = 0
        st.session_state.round = 1
        st.session_state.current_word = random.choice(labels)
        st.session_state.round_active = True
        st.session_state.start_time = time.time()
        st.session_state.last_guess = None
        st.experimental_rerun()

# -----------------------
# Main layout
# -----------------------
col1, col2 = st.columns([2,1])

with col1:
    st.markdown("<div class='canvas-card'>", unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center;'><div style='font-weight:700; font-size:1.1rem;'>Tur {st.session_state.round}/{st.session_state.total_rounds}</div><div class='small-muted'>Skor: <strong>{st.session_state.score}</strong></div></div>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)

    target_word = st.session_state.current_word
    # Show the german word to draw (use big friendly font)
    st.markdown(f"<div style='background: linear-gradient(90deg,#fff,#fff); border-radius:12px; padding:12px; margin-bottom:8px; text-align:center;'><h2 style='margin:0; font-size:2.2rem; color:#2C2C54;'>{target_word}</h2><div class='small-muted'>Şimdi bunu çiz!</div></div>", unsafe_allow_html=True)

    # Canvas
    canvas_result = st_canvas(
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        width=520,
        height=520,
        drawing_mode="freedraw",
        key=f"canvas_{st.session_state.round}",
        update_streamlit=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Action buttons under canvas
    col_a, col_b, col_c = st.columns([1,1,1])
    with col_a:
        if st.button("Tahmin Et 🎯"):
            if canvas_result and canvas_result.image_data is not None and canvas_result.image_data.sum() > 0:
                processed = preprocess_image(canvas_result.image_data)
                if processed is not None:
                    with st.spinner("Pixi bakıyor..."):
                        preds = model_predict_topk(processed, k=3)
                        st.session_state.top_preds = preds
                        st.session_state.last_guess = preds[0][0] if preds else None
                        # check correctness
                        elapsed = int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0
                        time_left = max(0, 25 - elapsed)
                        correct = (st.session_state.last_guess == target_word)
                        if correct:
                            pts = max(1, time_left)
                            st.session_state.score += pts
                            st.success(f"Pixi: Doğru! Bu bir **{target_word}** 🥳 (+{pts} puan)")
                            st.balloons()
                        else:
                            st.error(f"Pixi: Hmm... Bu sefer {st.session_state.last_guess} gibi görünüyor.")
                        st.session_state.round_active = False
                else:
                    st.warning("Çiziminizi okuyamadım, lütfen daha belirgin çizin.")
            else:
                st.warning("Lütfen önce çizim yapın!")
    with col_b:
        if st.button("İpucu 💡"):
            # show simple hint (first letter)
            hint = f"Kelimenin ilk harfi: **{target_word[0].upper()}**"
            st.info(hint)
    with col_c:
        if st.button("Pes et ve göster"):
            st.warning(f"Doğru cevap: **{target_word}**")
            st.session_state.round_active = False

with col2:
    st.markdown("<div class='pixibox'><div style='font-size:1.1rem;'>🤖 Pixi</div><div class='small-muted'>Senin çizimini tahmin edecek dost robot!</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='padding:12px; border-radius:12px; background:linear-gradient(180deg,#fff,#fff); box-shadow:0 6px 16px rgba(0,0,0,0.04)'>", unsafe_allow_html=True)

    st.subheader("Pixi'nin Tahminleri")
    if st.session_state.top_preds:
        # show top3 nicely
        for i, (lab, prob) in enumerate(st.session_state.top_preds, start=1):
            cls = "correct" if lab == target_word and not st.session_state.round_active else "wrong"
            prob_pct = round(prob * 100, 1) if isinstance(prob, float) else round(prob*100,1)
            st.markdown(f"<div class='pred-item {cls}'><strong>{i}. {lab}</strong> — <span class='small-muted'>{prob_pct}%</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='small-muted'>Henüz tahmin yapılmadı. Çizimini tamamla, sonra 'Tahmin Et' tuşuna bas.</div>", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(f"<div class='small-muted'>Kalan süre (tur):</div>", unsafe_allow_html=True)
    # show timer
    if st.session_state.round_active:
        elapsed = int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0
        time_left = max(0, 25 - elapsed)
        st.progress(int((time_left/25) * 100))
        st.markdown(f"<div style='font-size:1.4rem; font-weight:700;'>{time_left} s</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='small-muted'>Tur tamamlandı. Sonuçlara bak veya 'Sonraki'ye geç.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# End of round / Next
# -----------------------
st.markdown("<hr/>", unsafe_allow_html=True)
coln1, coln2, coln3 = st.columns([1,1,2])
with coln1:
    if st.button("Sonraki ➜"):
        # increment round and reset
        st.session_state.round += 1
        if st.session_state.round > st.session_state.total_rounds:
            # game over
            st.success(f"Oyun bitti! Toplam skorun: {st.session_state.score}")
            st.balloons()
            # reset game session to allow restart
            st.session_state.round = 1
            st.session_state.current_word = random.choice(labels)
            st.session_state.round_active = False
            st.session_state.start_time = None
            st.experimental_rerun()
        else:
            st.session_state.current_word = random.choice(labels)
            st.session_state.round_active = True
            st.session_state.start_time = time.time()
            st.session_state.top_preds = []
            st.session_state.last_guess = None
            # clear canvas key by re-running with new key (handled by key name using round number)
            st.experimental_rerun()

with coln2:
    if st.button("Oyunu Bitir"):
        st.success(f"Oyun sonlandı. Toplam skorun: {st.session_state.score}")
        st.session_state.round = 1
        st.session_state.current_word = random.choice(labels)
        st.session_state.round_active = False
        st.session_state.start_time = None

with coln3:
    st.markdown("<div class='footer-note'>İpucu: Çizimi daha belirgin yapmak için kalın fırça kullan ve arka plan açık beyaz bırakmayı dene.</div>", unsafe_allow_html=True)

# -----------------------
# Initialize first run
# -----------------------
if st.session_state.start_time is None and st.session_state.round_active:
    st.session_state.start_time = time.time()
elif not st.session_state.round_active and st.session_state.start_time is None:
    # if game hasn't started, show a friendly start hint
    st.info("Yeni oyuna başlamak için soldan 'Yeni Oyun Başlat' butonuna bas veya 'Tahmin Et' ile devam et.")
