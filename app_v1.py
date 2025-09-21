import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import cv2
import random
import time
import tensorflow as tf
import os
import json

# --- Uygulama Ayarları ve Sabitler ---
st.set_page_config(page_title="Pixi ile Çiz ve Öğren", page_icon="🤖")

# Kelime Veri Tabanı (labels.txt'den dinamik olarak oluşturulacak)
@st.cache_data
def load_word_data():
    with open('model/labels.txt', 'r') as f:
        labels = [line.strip() for line in f.readlines()]
    word_data = []
    for en in labels:
        de = en  # Varsayılan olarak İngilizce ile aynı, manuel çeviri eklenebilir
        hint1 = f"Bu bir {en.lower()} olabilir, çizimi dene!"
        hint2 = f"Türkçe karşılığı bilinmiyor, çizimiyle öğren!"
        word_data.append({'de': de, 'en': en, 'hint1': hint1, 'hint2': hint2})
    return word_data

WORD_DATA = load_word_data()

# --- Pixi'nin Cümleleri (Değişiklik yok) ---
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
    """Modeli ve etiketleri yükler, doodleNet mimarisine göre manuel oluşturuldu."""
    try:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
        from tensorflow.keras.initializers import GlorotUniform

        model = Sequential([
            Conv2D(16, (3, 3), activation='relu', input_shape=(28, 28, 1), padding='same',
                   kernel_initializer=GlorotUniform(), bias_initializer='zeros'),
            Conv2D(16, (3, 3), activation='relu', padding='same',
                   kernel_initializer=GlorotUniform(), bias_initializer='zeros'),
            MaxPooling2D((2, 2)),
            Conv2D(32, (3, 3), activation='relu', padding='same',
                   kernel_initializer=GlorotUniform(), bias_initializer='zeros'),
            Conv2D(32, (3, 3), activation='relu', padding='same',
                   kernel_initializer=GlorotUniform(), bias_initializer='zeros'),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu', padding='same',
                   kernel_initializer=GlorotUniform(), bias_initializer='zeros'),
            Conv2D(64, (3, 3), activation='relu', padding='same',
                   kernel_initializer=GlorotUniform(), bias_initializer='zeros'),
            MaxPooling2D((2, 2)),
            Dropout(0.1),
            Flatten(),
            Dense(512, activation='tanh', kernel_initializer=GlorotUniform(), bias_initializer='zeros'),
            Dense(345, activation='softmax', kernel_initializer=GlorotUniform(), bias_initializer='zeros')
        ])
        try:
            model.load_weights('model/myDoodleNet.weights.bin')
        except Exception as e:
            st.warning(f"Ağırlıklar yüklenemedi (.bin formatı uyumsuz): {e}. Rastgele ağırlıklar kullanıldı.")
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

        with open('model/labels.txt', 'r') as f:
            labels = [line.strip() for line in f.readlines()]
        return model, labels
    except Exception as e:
        st.error(f"Model veya etiket dosyası yüklenemedi! 'model' klasörünü kontrol edin. Hata: {e}")
        return None, None

def preprocess_image(image_data):
    """Canvas'tan gelen çizimi modelin anlayacağı formata dönüştürür."""
    if image_data is not None:
        gray = cv2.cvtColor(image_data, cv2.COLOR_RGBA2GRAY)
        resized = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)
        normalized = resized.astype('float32') / 255.0
        processed = np.expand_dims(normalized, axis=(0, -1))  # (1, 28, 28, 1)
        return processed
    return None

# --- Oyun Başlatma ve Durum Yönetimi ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_round' not in st.session_state:
    st.session_state.current_round = 1
if 'total_rounds' not in st.session_state:
    st.session_state.total_rounds = 5
if 'current_word_data' not in st.session_state:
    st.session_state.current_word_data = random.choice(WORD_DATA)
if 'round_active' not in st.session_state:
    st.session_state.round_active = True
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'round_won' not in st.session_state:
    st.session_state.round_won = False
if 'hint_level' not in st.session_state:
    st.session_state.hint_level = 0

def initialize_game():
    st.session_state.score = 0
    st.session_state.current_round = 1
    st.session_state.total_rounds = 5
    st.session_state.current_word_data = random.choice(WORD_DATA)
    st.session_state.round_active = True
    st.session_state.start_time = time.time()
    st.session_state.round_won = False
    st.session_state.hint_level = 0

def start_new_round():
    st.session_state.current_word_data = random.choice(WORD_DATA)
    st.session_state.round_active = True
    st.session_state.start_time = time.time()
    st.session_state.round_won = False
    st.session_state.hint_level = 0

# --- Oyun Mantığı ---
st.title("🎨 Pixi ile Çiz ve Öğren! 🇩🇪")
if st.button("Yeni Oyun Başlat"):
    initialize_game()
    st.experimental_rerun()

# Model ve etiketleri yükle
model, labels = load_model_and_labels()

if model is None:
    st.warning("⚠️ Model yüklenemedi! Rastgele tahmin moduna geçiliyor.")
    def predict(image_data):
        return random.choice(labels)
else:
    def predict(image_data):
        processed = preprocess_image(image_data)
        if processed is not None:
            predictions = model.predict(processed)
            top_index = np.argmax(predictions[0])
            return labels[top_index]
        return random.choice(labels)

# Oyun bitti mi kontrol et
if st.session_state.current_round > st.session_state.total_rounds:
    st.header("Oyun Bitti!")
    st.subheader(f"Skorun: {st.session_state.total_rounds} kelimeden {st.session_state.score} tanesini doğru çizdin!")
    st.balloons()
    if st.button("Tekrar Oyna"):
        initialize_game()
        st.experimental_rerun()
    st.stop()

# Mevcut Tur
word_data = st.session_state.current_word_data
target_word_de = word_data['de']
target_word_en = word_data['en']

st.header(f"Tur: {st.session_state.current_round}/{st.session_state.total_rounds} - Haydi çiz: **{target_word_de}**")

col1, col2 = st.columns([3, 2])

with col1:
    canvas_result = st_canvas(
        stroke_width=15, stroke_color="#FFFFFF", background_color="#000000",
        width=400, height=400, drawing_mode="freedraw",
        key=f"canvas_{st.session_state.current_round}",
        update_streamlit=st.session_state.round_active,
    )

with col2:
    time_left_placeholder = st.empty()
    st.write("---")
    st.subheader("🤖 Pixi Düşünüyor...")
    guess_placeholder = st.empty()
    guess_placeholder.info("Çizmeye başla! Çizim yapınca tahmin edeceğim!")

    st.write("---")
    if st.button("Bu kelimeyi bilmiyorum"):
        if st.session_state.hint_level < 2:
            st.session_state.hint_level += 1

    if st.session_state.hint_level >= 1:
        st.warning(f"**1. İpucu:** {word_data['hint1']}")
    if st.session_state.hint_level >= 2:
        st.success(f"**2. İpucu:** Türkçesi **{word_data['hint2']}**")

if st.session_state.round_active:
    elapsed_time = time.time() - st.session_state.start_time
    time_left = max(0, 20 - int(elapsed_time))
    time_left_placeholder.metric("Kalan Süre", f"{time_left} s")

    if canvas_result.image_data is not None and canvas_result.image_data.sum() > 0:
        processed_image = preprocess_image(canvas_result.image_data)

        # --- MODEL TAHMİNİ ---
        current_guess_en = predict(canvas_result.image_data)

        # İngilizce tahmini Almancaya geri çevir
        current_guess_de_list = [d['de'] for d in WORD_DATA if d['en'] == current_guess_en]
        if current_guess_de_list:
            current_guess_de = current_guess_de_list[0]
            guess_placeholder.markdown(random.choice(PIXI_GUESSING_PHRASES).format(f"**{current_guess_de}**"))

            if current_guess_en == target_word_en:
                st.session_state.round_won = True
                st.session_state.round_active = False
        # --- TAHMİN SONU ---

    if time_left <= 0:
        st.session_state.round_active = False

if not st.session_state.round_active:
    time_left_placeholder.metric("Kalan Süre", "Süre Doldu!")
    if st.session_state.round_won:
        st.success(random.choice(PIXI_SUCCESS_PHRASES).format(target_word_de))
        st.session_state.score += 1
    else:
        st.error(random.choice(PIXI_FAIL_PHRASES).format(target_word_de))

    if st.button("Sonraki Kelime →"):
        st.session_state.current_round += 1
        if st.session_state.current_round <= st.session_state.total_rounds:
            start_new_round()
        st.experimental_rerun()