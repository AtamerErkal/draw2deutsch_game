import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import cv2
import random
import time
import tensorflow as tf
import os

# --- Uygulama Ayarları ve Sabitler ---
st.set_page_config(page_title="Pixi ile Çiz ve Öğren", page_icon="🤖")

# Kelime Veri Tabanı (WORD_DATA listesi önceki cevaptaki gibi kalacak)
WORD_DATA = [
    {'de': 'Apfel', 'en': 'apple', 'hint1': 'Kırmızı veya yeşil renkli bir meyvedir.', 'hint2': 'Elma'},
    {'de': 'Auto', 'en': 'car', 'hint1': 'Dört tekerleği vardır ve yolda gider.', 'hint2': 'Araba'},
    {'de': 'Banane', 'en': 'banana', 'hint1': 'Sarı renkli, uzun bir meyvedir.', 'hint2': 'Muz'},
    {'de': 'Baum', 'en': 'tree', 'hint1': 'Yaprakları ve dalları olan büyük bir bitkidir.', 'hint2': 'Ağaç'},
    {'de': 'Bett', 'en': 'bed', 'hint1': 'Üzerinde uyuduğumuz bir mobilyadır.', 'hint2': 'Yatak'},
    {'de': 'Brille', 'en': 'eyeglasses', 'hint1': 'Daha iyi görmek için gözümüze takarız.', 'hint2': 'Gözlük'},
    {'de': 'Buch', 'en': 'book', 'hint1': 'İçinde hikayeler ve bilgiler olan bir nesnedir.', 'hint2': 'Kitap'},
    {'de': 'Fisch', 'en': 'fish', 'hint1': 'Suda yaşar ve yüzer.', 'hint2': 'Balık'},
    {'de': 'Haus', 'en': 'house', 'hint1': 'İçinde yaşadığımız bir yapıdır.', 'hint2': 'Ev'},
    {'de': 'Hut', 'en': 'hat', 'hint1': 'Başımıza taktığımız bir aksesuardır.', 'hint2': 'Şapka'},
    {'de': 'Katze', 'en': 'cat', 'hint1': 'Miyav diye ses çıkaran bir evcil hayvandır.', 'hint2': 'Kedi'},
    {'de': 'Mond', 'en': 'moon', 'hint1': 'Geceleri gökyüzünde parlayan gök cismidir.', 'hint2': 'Ay'},
    {'de': 'Sonne', 'en': 'sun', 'hint1': 'Gündüzleri gökyüzünü aydınlatan büyük sarı yıldızdır.', 'hint2': 'Güneş'},
    {'de': 'Stuhl', 'en': 'chair', 'hint1': 'Üzerine oturmak için kullanılır.', 'hint2': 'Sandalye'},
    {'de': 'Tisch', 'en': 'table', 'hint1': 'Üzerine yemek veya eşya koyduğumuz mobilyadır.', 'hint2': 'Masa'},
    # ... Önceki cevaptaki 50 kelimenin tamamını buraya ekleyin ...
]

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

# --- GERÇEK MODEL YÜKLEME VE İŞLEME FONKSİYONLARI ---

@st.cache_resource
def load_model_and_labels():
    """Modeli ve etiketleri yükler, sadece bir kez çalışır."""
    try:
        model = tf.keras.models.load_model('model/quickdraw_model.h5')
        with open('model/labels.txt', 'r') as f:
            labels = [line.strip() for line in f.readlines()]
        return model, labels
    except Exception as e:
        st.error(f"Model veya etiket dosyası yüklenemedi! 'model' klasörünü kontrol edin. Hata: {e}")
        return None, None

def preprocess_image(image_data):
    """Canvas'tan gelen çizimi modelin anlayacağı formata dönüştürür."""
    if image_data is not None:
        # RGBA'dan gri tonlamaya çevir
        img = cv2.cvtColor(image_data.astype(np.uint8), cv2.COLOR_RGBA2GRAY)
        
        # Çizimi (siyah) arka plandan (beyaz) ayırmak için threshold uygula
        _, img = cv2.threshold(img, 25, 255, cv2.THRESH_BINARY)

        # Görüntüyü yeniden boyutlandır
        img = cv2.resize(img, (28, 28))
        
        # Modelin girişi için normalize et ve boyutu ayarla (1, 28, 28, 1)
        img = img.reshape(1, 28, 28, 1).astype('float32') / 255.0
        return img
    return None

# --- Oyun Yönetim Fonksiyonları (Değişiklik yok) ---
def initialize_game():
    st.session_state.game_in_progress = True
    st.session_state.current_round = 1
    st.session_state.total_rounds = 5
    st.session_state.score = 0
    st.session_state.game_word_list = random.sample(WORD_DATA, st.session_state.total_rounds)
    start_new_round()

def start_new_round():
    st.session_state.round_active = True
    st.session_state.start_time = time.time()
    st.session_state.round_won = False
    st.session_state.hint_level = 0
    st.session_state.current_word_data = st.session_state.game_word_list[st.session_state.current_round - 1]

# --- ANA UYGULAMA ---

# Modeli ve etiketleri yükle
model, labels = load_model_and_labels()

st.title("🤖 Pixi ile Çiz ve Öğren!")

if 'game_in_progress' not in st.session_state:
    st.session_state.game_in_progress = False

if not st.session_state.game_in_progress:
    st.write("Merhaba! Ben Pixi, senin çizim robotun. Almanca kelimeleri birlikte çizip öğrenmeye ne dersin? Sana bir kelime vereceğim, sen çizeceksin ve ben ne olduğunu tahmin etmeye çalışacağım!")
    if st.button("Oyuna Başla!", type="primary", disabled=(model is None)):
        initialize_game()
        st.experimental_rerun()
    if model is None:
        st.error("Model yüklenemediği için oyun başlatılamıyor. Lütfen README.md dosyasındaki kurulum adımlarını kontrol et.")
else:
    # Oyun bitişi
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
        guess_placeholder.info("Çizmeye başla!")

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
            
            # --- GERÇEK MODEL TAHMİNİ ---
            predictions = model.predict(processed_image)
            top_index = np.argmax(predictions[0])
            current_guess_en = labels[top_index]
            
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