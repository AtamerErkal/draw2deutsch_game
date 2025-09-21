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
# Kid-friendly CSS
# -----------------------
st.markdown("""
<style>
:root{ --card:#fff; --accent:#FF6F61; --accent2:#FFD166; --bg1:#FFFDF9; --muted:#666;}
body { background: linear-gradient(180deg, #FFFDF9 0%, #F7F5FF 100%); }
.header { text-align:center; padding:12px; }
.title { font-size:2.2rem; color:#2C2C54; margin-bottom:6px; font-weight:800; }
.subtitle { color:#4b4b6b; margin-top:0; margin-bottom:14px; }
.container { display:flex; gap:18px; }
.canvas-card { background: var(--card); border-radius:14px; padding:14px; box-shadow: 0 10px 30px rgba(0,0,0,0.06); }
.side-card { background: linear-gradient(180deg,#fff,#fff); border-radius:12px; padding:12px; box-shadow:0 8px 20px rgba(0,0,0,0.04); }
.pixibubble { background: linear-gradient(90deg,#fff,#fff); border-radius:12px; padding:10px; margin-bottom:8px; text-align:center; font-weight:700; }
.green { background: linear-gradient(90deg,#D4F8E8,#E8FFF2); }
.red { background: linear-gradient(90deg,#FFF4F4,#FFF9F9); }
.pred { padding:8px; border-radius:10px; margin-bottom:6px; }
.badge { display:inline-block; padding:8px 12px; border-radius:999px; background:linear-gradient(90deg,#FFDEB5,#FFD166); font-weight:700; }
.small { color:var(--muted); font-size:0.9rem; }
.center { text-align:center; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><div class='title'>Pixi'nin Macerası — Almanca Öğren</div><div class='subtitle'>Her bölüm bir macera! Kelimeyi gör, çiz, Pixi tahmin etsin — yıldız kazan!</div></div>", unsafe_allow_html=True)

# -----------------------
# WORD DATA (100 items) with article and topic
# -----------------------
# Note: English words should match or be close to your model's labels (lowercased).
WORD_DATA = [
    # Hayvanlar (Animals)
    {"de":"der Hund","en":"dog","topic":"Hayvanlar"},
    {"de":"die Katze","en":"cat","topic":"Hayvanlar"},
    {"de":"der Vogel","en":"bird","topic":"Hayvanlar"},
    {"de":"der Fisch","en":"fish","topic":"Hayvanlar"},
    {"de":"das Pferd","en":"horse","topic":"Hayvanlar"},
    {"de":"die Kuh","en":"cow","topic":"Hayvanlar"},
    {"de":"das Schaf","en":"sheep","topic":"Hayvanlar"},
    {"de":"das Huhn","en":"chicken","topic":"Hayvanlar"},
    {"de":"die Ente","en":"duck","topic":"Hayvanlar"},
    {"de":"das Schwein","en":"pig","topic":"Hayvanlar"},

    # Meyveler (Fruits)
    {"de":"der Apfel","en":"apple","topic":"Meyveler"},
    {"de":"die Banane","en":"banana","topic":"Meyveler"},
    {"de":"die Birne","en":"pear","topic":"Meyveler"},
    {"de":"die Traube","en":"grapes","topic":"Meyveler"},
    {"de":"die Erdbeere","en":"strawberry","topic":"Meyveler"},
    {"de":"die Kirsche","en":"cherry","topic":"Meyveler"},
    {"de":"die Orange","en":"orange","topic":"Meyveler"},
    {"de":"die Zitrone","en":"lemon","topic":"Meyveler"},
    {"de":"die Melone","en":"melon","topic":"Meyveler"},
    {"de":"die Wassermelone","en":"watermelon","topic":"Meyveler"},

    # Ev & Eşyalar (Home)
    {"de":"das Haus","en":"house","topic":"Ev eşyaları"},
    {"de":"die Tür","en":"door","topic":"Ev eşyaları"},
    {"de":"das Fenster","en":"window","topic":"Ev eşyaları"},
    {"de":"der Stuhl","en":"chair","topic":"Ev eşyaları"},
    {"de":"der Tisch","en":"table","topic":"Ev eşyaları"},
    {"de":"das Bett","en":"bed","topic":"Ev eşyaları"},
    {"de":"die Lampe","en":"lamp","topic":"Ev eşyaları"},
    {"de":"die Uhr","en":"clock","topic":"Ev eşyaları"},
    {"de":"das Buch","en":"book","topic":"Ev eşyaları"},
    {"de":"der Stift","en":"pen","topic":"Ev eşyaları"},

    # Taşıtlar (Transport)
    {"de":"das Auto","en":"car","topic":"Ulaşım"},
    {"de":"der Bus","en":"bus","topic":"Ulaşım"},
    {"de":"das Fahrrad","en":"bicycle","topic":"Ulaşım"},
    {"de":"der Zug","en":"train","topic":"Ulaşım"},
    {"de":"das Flugzeug","en":"airplane","topic":"Ulaşım"},
    {"de":"das Schiff","en":"ship","topic":"Ulaşım"},
    {"de":"die Straße","en":"street","topic":"Ulaşım"},
    {"de":"die Brücke","en":"bridge","topic":"Ulaşım"},
    {"de":"die Ampel","en":"traffic light","topic":"Ulaşım"},
    {"de":"die Schule","en":"school","topic":"Ulaşım"},

    # Doğa (Nature)
    {"de":"die Sonne","en":"sun","topic":"Doğa"},
    {"de":"der Mond","en":"moon","topic":"Doğa"},
    {"de":"der Stern","en":"star","topic":"Doğa"},
    {"de":"der Baum","en":"tree","topic":"Doğa"},
    {"de":"die Blume","en":"flower","topic":"Doğa"},
    {"de":"der Berg","en":"mountain","topic":"Doğa"},
    {"de":"die Wolke","en":"cloud","topic":"Doğa"},
    {"de":"der Regen","en":"rain","topic":"Doğa"},
    {"de":"der Schnee","en":"snow","topic":"Doğa"},
    {"de":"das Gras","en":"grass","topic":"Doğa"},

    # Vücut (Body)
    {"de":"die Hand","en":"hand","topic":"Vücut"},
    {"de":"der Fuß","en":"foot","topic":"Vücut"},
    {"de":"der Kopf","en":"head","topic":"Vücut"},
    {"de":"das Auge","en":"eye","topic":"Vücut"},
    {"de":"der Mund","en":"mouth","topic":"Vücut"},
    {"de":"die Nase","en":"nose","topic":"Vücut"},
    {"de":"das Ohr","en":"ear","topic":"Vücut"},
    {"de":"das Herz","en":"heart","topic":"Vücut"},
    {"de":"der Mann","en":"man","topic":"Vücut"},
    {"de":"die Frau","en":"woman","topic":"Vücut"},

    # Oyun & Elektronik
    {"de":"der Ball","en":"ball","topic":"Oyuncaklar"},
    {"de":"die Puppe","en":"doll","topic":"Oyuncaklar"},
    {"de":"der Teddy","en":"teddy-bear","topic":"Oyuncaklar"},
    {"de":"der Computer","en":"computer","topic":"Oyuncaklar"},
    {"de":"das Handy","en":"phone","topic":"Oyuncaklar"},
    {"de":"der Fernseher","en":"television","topic":"Oyuncaklar"},
    {"de":"das Radio","en":"radio","topic":"Oyuncaklar"},
    {"de":"das Spiel","en":"game","topic":"Oyuncaklar"},
    {"de":"die Musik","en":"music","topic":"Oyuncaklar"},
    {"de":"das Buch","en":"book","topic":"Oyuncaklar"},

    # Yiyecekler
    {"de":"das Brot","en":"bread","topic":"Yiyecekler"},
    {"de":"die Milch","en":"milk","topic":"Yiyecekler"},
    {"de":"der Käse","en":"cheese","topic":"Yiyecekler"},
    {"de":"das Ei","en":"egg","topic":"Yiyecekler"},
    {"de":"das Fleisch","en":"meat","topic":"Yiyecekler"},
    {"de":"der Reis","en":"rice","topic":"Yiyecekler"},
    {"de":"die Suppe","en":"soup","topic":"Yiyecekler"},
    {"de":"die Pizza","en":"pizza","topic":"Yiyecekler"},
    {"de":"der Kuchen","en":"cake","topic":"Yiyecekler"},
    {"de":"der Apfel","en":"apple","topic":"Yiyecekler"},

    # Giysi (Clothes)
    {"de":"die Jacke","en":"jacket","topic":"Giysi"},
    {"de":"die Hose","en":"pants","topic":"Giysi"},
    {"de":"das Hemd","en":"shirt","topic":"Giysi"},
    {"de":"der Schuh","en":"shoe","topic":"Giysi"},
    {"de":"das Kleid","en":"dress","topic":"Giysi"},
    {"de":"der Hut","en":"hat","topic":"Giysi"},
    {"de":"der Mantel","en":"coat","topic":"Giysi"},
    {"de":"der Rock","en":"skirt","topic":"Giysi"},
    {"de":"die Socke","en":"sock","topic":"Giysi"},
    {"de":"der Handschuh","en":"glove","topic":"Giysi"}
]

# -----------------------
# Load model & labels
# -----------------------
@st.cache_resource
def load_model_and_labels():
    model_path = "model/quickdraw_model.h5"
    labels_path = "model/labels.txt"
    model = None
    labels = []
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
        model = None
    return model, labels

model, labels = load_model_and_labels()

if not labels:
    st.stop()

# -----------------------
# Utility: choose topics and words
# -----------------------
TOPICS = sorted(list({w["topic"] for w in WORD_DATA}))

def get_words_by_topic(topic):
    return [w for w in WORD_DATA if w["topic"] == topic]

# -----------------------
# Image preprocessing
# -----------------------
def preprocess_image(image_data, target_size=(28,28), dilate_iter=1):
    """
    Convert RGBA canvas image -> model-ready (1,h,w,1)
    Steps:
      - convert to uint8
      - composite alpha on white background
      - grayscale
      - threshold & dilate to thicken strokes
      - crop bounding box
      - pad to square, resize to target_size
      - invert (white bg -> black bg expectation), normalize
    """
    if image_data is None:
        return None
    try:
        img = (image_data * 255).astype(np.uint8) if image_data.max() <= 1.0 else image_data.astype(np.uint8)
        # compose alpha if present
        if img.shape[2] == 4:
            alpha = img[:,:,3] / 255.0
            rgb = img[:,:,:3].astype(np.float32)
            bg = np.ones_like(rgb, dtype=np.uint8) * 255
            comp = (rgb * alpha[...,None] + bg.astype(np.float32) * (1-alpha[...,None])).astype(np.uint8)
        else:
            comp = img[:,:,:3]
        gray = cv2.cvtColor(comp, cv2.COLOR_BGR2GRAY)
        # Threshold to get strokes (lines darker)
        _, th = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        # Invert temporarily to get foreground as white for findNonZero
        inv = cv2.bitwise_not(th)
        coords = cv2.findNonZero(inv)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            crop = gray[y:y+h, x:x+w]
        else:
            crop = gray
        # Make square canvas with white background
        h0, w0 = crop.shape[:2]
        if h0 == 0 or w0 == 0:
            square = 255 * np.ones((max(gray.shape), max(gray.shape)), dtype=np.uint8)
        else:
            side = max(h0, w0)
            square = 255 * np.ones((side, side), dtype=np.uint8)
            y_off = (side - h0)//2
            x_off = (side - w0)//2
            square[y_off:y_off+h0, x_off:x_off+w0] = crop
        resized = cv2.resize(square, target_size, interpolation=cv2.INTER_AREA)
        # Thicken strokes a bit
        kernel = np.ones((2,2), np.uint8)
        dilated = cv2.dilate(resized, kernel, iterations=dilate_iter)
        # Invert so strokes are white on black (or vice versa depending on model). QuickDraw often expects white stroke on black bg? We'll invert to white stroke on black:
        inverted = cv2.bitwise_not(dilated)
        normalized = inverted.astype('float32') / 255.0
        processed = normalized.reshape(1, target_size[0], target_size[1], 1)
        return processed
    except Exception as e:
        st.error(f"Ön işlem hatası: {e}")
        return None

# -----------------------
# Prediction helper
# -----------------------
def predict_topk(processed, k=5):
    if processed is None:
        return []
    if model is None:
        # fallback random
        picks = random.sample(labels, min(k, len(labels)))
        return [(p, 1.0/len(picks)) for p in picks]
    preds = model.predict(processed, verbose=0)[0]
    idx = np.argsort(preds)[::-1][:k]
    return [(labels[i], float(preds[i])) for i in idx]

# -----------------------
# Game state
# -----------------------
if 'topic' not in st.session_state: st.session_state.topic = TOPICS[0]
if 'round_idx' not in st.session_state: st.session_state.round_idx = 0
if 'words' not in st.session_state: st.session_state.words = get_words_by_topic(st.session_state.topic)
if 'score' not in st.session_state: st.session_state.score = 0
if 'stars' not in st.session_state: st.session_state.stars = 0
if 'start' not in st.session_state: st.session_state.start = False
if 'last_preds' not in st.session_state: st.session_state.last_preds = []
if 'dilate' not in st.session_state: st.session_state.dilate = 1

# -----------------------
# Sidebar: choose topic / settings
# -----------------------
with st.sidebar:
    st.header("Bölüm Seçimi & Ayarlar")
    choice = st.selectbox("Bölüm (Tema)", TOPICS, index=TOPICS.index(st.session_state.topic))
    if choice != st.session_state.topic:
        st.session_state.topic = choice
        st.session_state.words = get_words_by_topic(choice)
        st.session_state.round_idx = 0
        st.session_state.start = False
        st.session_state.last_preds = []
    rounds = st.number_input("Tur sayısı (bir bölüm için)", min_value=3, max_value=20, value=8, step=1)
    st.session_state.rounds = int(rounds)
    st.session_state.dilate = st.slider("Çizgileri hafif kalınlaştır (dilate)", 0, 3, 1)
    st.markdown("---")
    if st.button("Yeni Bölüm Başlat"):
        st.session_state.score = 0
        st.session_state.stars = 0
        st.session_state.round_idx = 0
        # shuffle chosen words and trim to rounds
        pool = st.session_state.words.copy()
        random.shuffle(pool)
        st.session_state.play_words = pool[:st.session_state.rounds]
        st.session_state.start = True
        st.session_state.last_preds = []
        st.experimental_rerun()

# -----------------------
# Main UI
# -----------------------
col_main, col_side = st.columns([3,1])

with col_main:
    st.markdown("<div class='canvas-card'>", unsafe_allow_html=True)
    if not st.session_state.start:
        st.markdown("<div class='center'><h2>Pixi ile maceraya hazır mısın?</h2><p class='small'>Soldan bir bölüm seç ve 'Yeni Bölüm Başlat' tuşuna bas. Pixi sana çizilecek Almanca kelimeyi söyleyecek.</p></div>", unsafe_allow_html=True)
    else:
        idx = st.session_state.round_idx
        # ensure play_words exists
        if 'play_words' not in st.session_state:
            pool = st.session_state.words.copy()
            random.shuffle(pool)
            st.session_state.play_words = pool[:st.session_state.rounds]
        if idx >= len(st.session_state.play_words):
            # section complete
            st.markdown(f"<div class='center'><h2>Tebrikler! Bölümü tamamladın 🎉</h2><p class='small'>Skor: <strong>{st.session_state.score}</strong> — Yıldızlar: {'⭐'*st.session_state.stars}</p></div>", unsafe_allow_html=True)
            if st.button("Başka Bir Bölüm Seç"):
                st.session_state.start = False
                st.session_state.round_idx = 0
                st.experimental_rerun()
        else:
            current = st.session_state.play_words[idx]
            # display german with artikel
            st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center;'><div><h2 style='margin:0'>{current['de']}</h2><div class='small'>Şimdi bunu çiz — Pixi tahmin edecek!</div></div><div class='badge'>Tur {idx+1}/{st.session_state.rounds}</div></div>", unsafe_allow_html=True)
            st.markdown("<hr/>", unsafe_allow_html=True)
            # Canvas
            canvas_result = st_canvas(
                stroke_width=st.slider("Fırça kalınlığı", 4, 60, 18, key=f"brush_{idx}"),
                stroke_color=st.color_picker("Çizgi rengi", "#000000", key=f"col_{idx}"),
                background_color=st.color_picker("Arka plan rengi", "#FFFFFF", key=f"bg_{idx}"),
                width=520,
                height=520,
                drawing_mode="freedraw",
                key=f"canvas_{idx}",
                update_streamlit=True,
            )
            st.markdown("<div style='margin-top:10px; display:flex; gap:10px;'>", unsafe_allow_html=True)
            if st.button("Tahmin Et 🎯", key=f"guess_{idx}"):
                if canvas_result and canvas_result.image_data is not None and canvas_result.image_data.sum() > 0:
                    proc = preprocess_image(canvas_result.image_data, dilate_iter=st.session_state.dilate)
                    # run prediction
                    topk = predict_topk(proc, k=5)
                    st.session_state.last_preds = topk
                    # check if target in topk
                    target_en = current['en'].strip().lower()
                    # labels are lowercase
                    top_labels = [t[0].lower() for t in topk]
                    matched_at = None
                    for i,lab in enumerate(top_labels):
                        # normalize variants: replace underscores/hyphens with space
                        norm_lab = lab.replace("_"," ").replace("-"," ").strip()
                        norm_target = target_en.replace("_"," ").replace("-"," ").strip()
                        if norm_lab == norm_target:
                            matched_at = i
                            break
                    # scoring
                    if matched_at == 0:
                        # top1
                        pts = 5
                        st.success(f"Pixi: Harika! Top-1 — {current['de']} doğru 🎉 (+{pts} puan)")
                        st.balloons()
                        st.session_state.score += pts
                        st.session_state.stars += 3 if st.session_state.stars < 30 else 0
                    elif matched_at is not None:
                        pts = 3
                        st.success(f"Pixi: Süper! {matched_at+1}. tahminde buldum — {current['de']} (+{pts} puan)")
                        st.session_state.score += pts
                        st.session_state.stars += 2 if st.session_state.stars < 30 else 0
                    else:
                        # not in top5
                        pts = 1
                        st.warning(f"Pixi: Hmm... Bu sefer bulamadım ama cesaretin için +{pts} puan veriyorum. Doğrusu: **{current['de']}**")
                        st.session_state.score += pts
                    # advance round (small delay so child sees result)
                    time.sleep(0.6)
                    st.session_state.round_idx += 1
                    st.experimental_rerun()
                else:
                    st.warning("Lütfen önce bir çizim yap!")
            if st.button("Pes et (Doğruyu göster)", key=f"giveup_{idx}"):
                st.info(f"Doğru cevap: **{current['de']}**")
                st.session_state.round_idx += 1
                st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            # show last preds if available
            if st.session_state.last_preds:
                st.markdown("<hr/>", unsafe_allow_html=True)
                st.markdown("<div class='small'>Pixi'nin son tahminleri (Top-5):</div>", unsafe_allow_html=True)
                for i,(lab,prob) in enumerate(st.session_state.last_preds, start=1):
                    pct = round(prob*100,2) if isinstance(prob,float) else prob
                    cls = "green" if lab.lower().replace("_"," ").replace("-"," ").strip() == current['en'].lower().replace("_"," ").replace("-"," ").strip() else "red"
                    st.markdown(f"<div class='pred {cls}'><strong>{i}. {lab}</strong> — <span class='small'>{pct}%</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_side:
    st.markdown("<div class='side-card center'>", unsafe_allow_html=True)
    st.markdown("<div class='pixibubble'>🤖 Pixi</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-weight:700; font-size:1.1rem; text-align:center;'>Skor</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1.6rem; font-weight:800; text-align:center; padding:6px;'>{st.session_state.score} puan</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='small' style='text-align:center'>Yıldızlar: {'⭐'*min(10, st.session_state.stars//2)}</div>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center'><button onclick=\"window.scrollTo(0,0)\" style='padding:8px 12px; border-radius:10px; background:linear-gradient(90deg,#FF9A8B,#FF6F61); color:white; border:none;'>Pixi'ye Merhaba De!</button></div>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<div class='small'>İpuçları:</div>", unsafe_allow_html=True)
    st.markdown("<ul class='small'><li>Kalın fırça ile çizmek modelin görmesini kolaylaştırır.</li><li>Arka planı düz beyaz bırak.</li><li>Çizimi büyük tut, küçük detaylardan kaçın.</li></ul>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# Helpers used inline: define predict_topk now (kept after UI to avoid repetition)
# -----------------------
def predict_topk(proc, k=5):
    try:
        if proc is None:
            return []
        if model is None:
            # fallback random
            picks = random.sample(labels, min(k, len(labels)))
            return [(p, 1.0/len(picks)) for p in picks]
        preds = model.predict(proc, verbose=0)[0]
        idx = np.argsort(preds)[::-1][:k]
        return [(labels[i], float(preds[i])) for i in idx]
    except Exception as e:
        st.error(f"Tahmin hatası: {e}")
        return []

# -----------------------
# End of file
# -----------------------
