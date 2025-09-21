import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import cv2
import random
import time
import tensorflow as tf
import os

# --- Uygulama Ayarları ve Sabitler ---
st.set_page_config(page_title="Pixi ile Çiz ve Öğren", page_icon="🤖", layout="wide")

# Görsel iyileştirmeler için CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(to bottom right, #f0f8ff, #add8e6); color: #333; }
    .main-header { font-size: 2.5rem; color: #2c3e50; text-align: center; margin-bottom: 1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
    .sub-header { font-size: 1.2rem; color: #34495e; text-align: center; margin-bottom: 2rem; }
    .pixi-message { background-color: #ffffff; border-radius: 15px; padding: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1rem; color: #2c3e50; }
    .success-message { background-color: #d4edda; border-left: 5px solid #28a745; color: #155724; }
    .error-message { background-color: #f8d7da; border-left: 5px solid #dc3545; color: #721c24; }
    .warning-message { background-color: #fff3cd; border-left: 5px solid #ffc107; color: #856404; }
    .hint-button { background-color: #ffd700; color: #333; font-weight: bold; }
    .next-button { background-color: #4a90e2; color: white; font-weight: bold; width: 100%; }
    .stButton > button { border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .canvas-container { border: 2px solid #4a90e2; border-radius: 15px; background-color: white; padding: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .sidebar .stSlider { margin-bottom: 1rem; }
    .metric-container { text-align: center; font-size: 1.2rem; color: #2c3e50; }
</style>
""", unsafe_allow_html=True)

# Kelime Veri Tabanı
@st.cache_data
def load_word_data():
    try:
        with open('model/labels.txt', 'r') as f:
            labels = [line.strip() for line in f.readlines() if line.strip()]
        if not labels:
            st.error("labels.txt dosyası boş veya geçersiz!")
            return []
        word_data = [{'de': en, 'en': en, 'hint1': f'Bu bir {en.lower()} olabilir, çizimi dene!', 'hint2': f'Türkçe karşılığı bilinmiyor, çizimiyle öğren!'} for en in labels]
        return word_data
    except FileNotFoundError:
        st.error("labels.txt dosyası bulunamadı! Lütfen 'model' klasörünü kontrol edin.")
        return []
    except Exception as e:
        st.error(f"labels.txt yüklenirken hata: {e}")
        return []

WORD_DATA = load_word_data()

# --- Pixi'nin Cümleleri ---
PIXI_SUCCESS_PHRASES = [
    "Yaşasın! Buldum! Bu harika bir **{}**! Çok güzel çizdin!",
    "İşte bu! Seninle harika bir takımız! Mükemmel bir **{}** çizimi.",
    "Vay canına! Sen bir sanatçısın! Tabii ki bu bir **{}**!",
    "Harikasın! Bu **{}** çizimini hemen tanıdım!"
]
PIXI_FAIL_PHRASES = [
    "Ah, bu biraz zordu galiba! Doğru cevap **{}** olacaktı. Bir sonrakinde başarırız!",
    "Neredeyse buluyordum! Çizimin çok güzeldi ama süremiz bitti. Cevap: **{}**.",
    "Hmm, bunu tam çıkaramadım. Doğrusu **{}** imiş. Üzülme, devam edelim!"
]
PIXI_GUESSING_PHRASES = [
    "Hmm, bu bir... **{}** mı?",
    "Dur bir saniye, şekillenmeye başladı! Sanırım bir **{}**!",
    "Çizgilerin bana bir şeyler anlatıyor... Bu bir **{}** olabilir mi?"
]

# --- MODEL YÜKLEME VE İŞLEME FONKSİYONLARI ---
@st.cache_resource
def load_model_and_labels():
    try:
        model = tf.keras.models.load_model('model/quickdraw_model.h5')
        with open('model/labels.txt', 'r') as f:
            labels = [line.strip() for line in f.readlines() if line.strip()]
        if model and labels:
            st.success("Model ve etiketler başarıyla yüklendi!")
            return model, labels
        else:
            st.warning("Model veya etiketler eksik, rastgele tahmin moduna geçiliyor.")
            return None, labels
    except Exception as e:
        st.error(f"Model yüklenemedi! Hata: {e}. Rastgele tahmin moduna geçiliyor.")
        try:
            with open('model/labels.txt', 'r') as f:
                labels = [line.strip() for line in f.readlines() if line.strip()]
        except:
            labels = []
        return None, labels if labels else []

def preprocess_image(image_data):
    if image_data is not None and image_data.sum() > 0:
        gray = cv2.cvtColor(image_data, cv2.COLOR_RGBA2GRAY)
        resized = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)
        inverted = cv2.bitwise_not(resized)   # QuickDraw formatı için ters çevirme
        normalized = inverted.astype('float32') / 255.0
        processed = np.expand_dims(normalized, axis=(0, -1))
        st.write("Görüntü işlendi - Şekil:", processed.shape if processed is not None else "Boş")
        return processed
    st.warning("Çizim verisi alınamadı veya boş!")
    return None

# --- Oyun Başlatma ve Durum Yönetimi ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'current_round' not in st.session_state: st.session_state.current_round = 1
if 'total_rounds' not in st.session_state: st.session_state.total_rounds = 5
if 'current_word_data' not in st.session_state: st.session_state.current_word_data = random.choice(WORD_DATA) if WORD_DATA else None
if 'round_active' not in st.session_state: st.session_state.round_active = False
if 'game_started' not in st.session_state: st.session_state.game_started = False
if 'stroke_color' not in st.session_state: st.session_state.stroke_color = "#000000"
if 'background_color' not in st.session_state: st.session_state.background_color = "#FFFFFF"
if 'stroke_width' not in st.session_state: st.session_state.stroke_width = 15
if 'hint_level' not in st.session_state: st.session_state.hint_level = 0
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'guess_made' not in st.session_state: st.session_state.guess_made = False

def initialize_game():
    st.session_state.score = 0
    st.session_state.current_round = 1
    st.session_state.total_rounds = 5
    start_new_round()
    st.session_state.game_started = True

def start_new_round():
    if WORD_DATA:
        st.session_state.current_word_data = random.choice(WORD_DATA)
    st.session_state.round_active = True
    st.session_state.start_time = time.time()
    st.session_state.round_won = False
    st.session_state.hint_level = 0
    st.session_state.guess_made = False

# --- MODEL YÜKLEME ---
model, labels = load_model_and_labels()

if not labels:
    st.error("Etiketler yüklenemedi! Oyun oynanamaz.")
    st.stop()

if model is None:
    st.warning("Model yüklenemedi, rastgele tahmin modunda çalışacak.")
    def predict(image_data):
        return random.choice(labels) if labels else "Bilinmeyen"
else:
    st.success("Model yüklendi, tahminler gerçek verilere dayalı olacak.")
    def predict(image_data):
        processed = preprocess_image(image_data)
        if processed is not None:
            try:
                predictions = model.predict(processed, verbose=0)
                st.write("Tahmin çıktısı - Şekil:", predictions.shape if predictions is not None else "Boş")
                top_index = np.argmax(predictions[0])
                if 0 <= top_index < len(labels):
                    return labels[top_index]
                else:
                    st.warning(f"Tahmin indeksi ({top_index}) etiket sayısını ({len(labels)}) aştı!")
                    return random.choice(labels) if labels else "Bilinmeyen"
            except Exception as e:
                st.error(f"Tahmin hatası: {e}")
                return random.choice(labels) if labels else "Bilinmeyen"
        return random.choice(labels) if labels else "Bilinmeyen"

# --- Görsel Oyun Ekranı ---
st.markdown("<h1 class='main-header'>🎨 Pixi ile Çiz ve Öğren! 🇩🇪</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Almanca kelimeleri çizerek öğren! Haydi başlayalım!</p>", unsafe_allow_html=True)

if not st.session_state.game_started:
    st.markdown("### Çizim Ayarlarını Seç!")
    st.session_state.stroke_color = st.color_picker("Çizgi Rengi", "#000000")
    st.session_state.background_color = st.color_picker("Arka Plan Rengi", "#FFFFFF")
    st.session_state.stroke_width = st.slider("Çizgi Kalınlığı", 1, 50, 15)
    if st.button("Oyunu Başlat", type="primary"):
        initialize_game()
        st.experimental_rerun()
elif not st.session_state.current_word_data:
    st.error("Kelime verisi yüklenemedi! Lütfen labels.txt dosyasını kontrol edin.")
    st.stop()
else:
    # Oyun bitti mi kontrol et
    if st.session_state.current_round > st.session_state.total_rounds:
        st.markdown("<h2 class='main-header'>Oyun Bitti!</h2>", unsafe_allow_html=True)
        st.subheader(f"Skorun: {st.session_state.total_rounds} kelimeden {st.session_state.score} puanı kazandın!")
        st.balloons()
        if st.button("Tekrar Oyna", type="primary"):
            st.session_state.game_started = False
            st.experimental_rerun()
        st.stop()

    # Mevcut Tur
    word_data = st.session_state.current_word_data
    target_word_de = word_data['de']
    target_word_en = word_data['en']

    st.header(f"Tur: {st.session_state.current_round}/{st.session_state.total_rounds} - Haydi çiz: **{target_word_de}**")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<div class='canvas-container'>", unsafe_allow_html=True)
        canvas_result = st_canvas(
            stroke_width=st.session_state.stroke_width,
            stroke_color=st.session_state.stroke_color,
            background_color=st.session_state.background_color,
            width=400, height=400, drawing_mode="freedraw",
            key=f"canvas_{st.session_state.current_round}",
            update_streamlit=st.session_state.round_active and not st.session_state.guess_made,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if st.session_state.round_active:
            if st.session_state.start_time is not None:
                elapsed_time = time.time() - st.session_state.start_time
                time_left = max(0, 20 - int(elapsed_time))
                st.markdown(f"<div class='metric-container'>Kalan Süre: <b>{time_left}</b> saniye</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='metric-container'>Kalan Süre: 20 saniye</div>", unsafe_allow_html=True)

            st.write("---")
            st.subheader("🤖 Pixi Düşünüyor...")
            guess_placeholder = st.empty()
            if not st.session_state.guess_made and canvas_result.image_data is not None and canvas_result.image_data.sum() > 0:
                guess_placeholder.info("Çizimi tamamla ve 'Tahmin Et' butonuna bas!")
            elif st.session_state.guess_made:
                st.write("Tahmin yapılıyor...")  # Debug için
                current_guess_en = predict(canvas_result.image_data)
                st.write(f"Tahmin edilen kelime (EN): {current_guess_en}")  # Debug için
                current_guess_de_list = [d['de'] for d in WORD_DATA if d['en'] == current_guess_en]
                if current_guess_de_list:
                    current_guess_de = current_guess_de_list[0]
                    guess_placeholder.markdown(f"<div class='pixi-message'>{random.choice(PIXI_GUESSING_PHRASES).format(f'**{current_guess_de}**')}</div>", unsafe_allow_html=True)
                    if current_guess_en == target_word_en:
                        st.session_state.round_won = True
                        st.session_state.round_active = False
                        time_left = max(0, 20 - int(time.time() - st.session_state.start_time))
                        st.session_state.score += time_left
                        st.balloons()
                else:
                    st.error(f"Tahmin edilen kelime ({current_guess_en}) veri tabanında bulunamadı!")
                st.session_state.guess_made = False  # Tahmin sonrası sıfırla

            st.write("---")
            if st.button("Bu kelimeyi bilmiyorum", key="hint_button", help="İpucu al!"):
                if st.session_state.hint_level < 2:
                    st.session_state.hint_level += 1

            if st.session_state.hint_level >= 1:
                st.markdown("<div class='warning-message'>**1. İpucu:** {}</div>".format(word_data['hint1']), unsafe_allow_html=True)
            if st.session_state.hint_level >= 2:
                st.markdown("<div class='success-message'>**2. İpucu:** Türkçesi **{}</div>".format(word_data['hint2']), unsafe_allow_html=True)

            if st.button("Tahmin Et", type="primary"):
                if canvas_result.image_data is not None and canvas_result.image_data.sum() > 0:
                    st.session_state.guess_made = True
                else:
                    st.warning("Lütfen önce bir çizim yapın!")

        if not st.session_state.round_active:
            time_left = max(0, 20 - int(time.time() - st.session_state.start_time))
            st.markdown(f"<div class='metric-container'>Kalan Süre: <b>{time_left if time_left > 0 else 'Süre Doldu!'}</b></div>", unsafe_allow_html=True)
            if st.session_state.round_won:
                st.markdown("<div class='success-message'>"+random.choice(PIXI_SUCCESS_PHRASES).format(target_word_de)+"</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='error-message'>"+random.choice(PIXI_FAIL_PHRASES).format(target_word_de)+"</div>", unsafe_allow_html=True)

            if st.button("Sonraki Kelime →", type="primary"):
                st.session_state.current_round += 1
                if st.session_state.current_round <= st.session_state.total_rounds:
                    start_new_round()
                st.experimental_rerun()
