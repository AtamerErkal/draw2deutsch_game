# pixi_almanca_oyun.py
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import cv2
import random
import time
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Sayfa yapılandırması
st.set_page_config(
    page_title="🎨 Pixi'nin Almanca Macerası", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gelişmiş CSS stilleri
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka+One:wght@400&family=Comic+Neue:wght@300;400;700&display=swap');

:root {
    --primary-blue: #4A90E2;
    --primary-pink: #FF69B4;
    --primary-yellow: #FFD700;
    --primary-green: #32CD32;
    --primary-orange: #FF8C00;
    --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --card-shadow: 0 10px 30px rgba(0,0,0,0.2);
    --text-dark: #2C3E50;
    --text-light: #7F8C8D;
    --success-color: #2ECC71;
    --warning-color: #F39C12;
    --error-color: #E74C3C;
}

body {
    background: var(--bg-gradient);
    font-family: 'Comic Neue', cursive;
}

.main-header {
    background: linear-gradient(90deg, #FF69B4, #4A90E2, #32CD32, #FFD700);
    background-size: 400% 400%;
    animation: gradientShift 4s ease infinite;
    text-align: center;
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 20px;
    box-shadow: var(--card-shadow);
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.main-title {
    font-family: 'Fredoka One', cursive;
    font-size: 3rem;
    color: white;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    margin: 0;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
}

.subtitle {
    color: white;
    font-size: 1.2rem;
    margin: 10px 0 0 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.game-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 25px;
    box-shadow: var(--card-shadow);
    border: 3px solid transparent;
    background-image: linear-gradient(white, white), linear-gradient(45deg, #FF69B4, #4A90E2);
    background-origin: border-box;
    background-clip: content-box, border-box;
    margin-bottom: 20px;
}

.pixi-character {
    text-align: center;
    font-size: 4rem;
    animation: pixiDance 3s ease-in-out infinite;
    margin: 20px 0;
}

@keyframes pixiDance {
    0%, 100% { transform: rotate(-5deg) scale(1); }
    25% { transform: rotate(5deg) scale(1.1); }
    50% { transform: rotate(-3deg) scale(1.05); }
    75% { transform: rotate(3deg) scale(1.1); }
}

.word-display {
    text-align: center;
    background: linear-gradient(135deg, #FFD700, #FF8C00);
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.german-word {
    font-family: 'Fredoka One', cursive;
    font-size: 2.5rem;
    color: var(--text-dark);
    margin: 0;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

.word-hint {
    font-size: 1.1rem;
    color: var(--text-light);
    margin: 5px 0 0 0;
}

.score-panel {
    background: linear-gradient(135deg, #32CD32, #228B22);
    color: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin: 15px 0;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.score-value {
    font-family: 'Fredoka One', cursive;
    font-size: 2.5rem;
    margin: 10px 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.stars-display {
    font-size: 2rem;
    margin: 10px 0;
}

.action-button {
    background: linear-gradient(135deg, #FF69B4, #FF1493);
    color: white;
    border: none;
    padding: 15px 30px;
    border-radius: 25px;
    font-family: 'Fredoka One', cursive;
    font-size: 1.2rem;
    cursor: pointer;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
    margin: 10px 5px;
}

.action-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 7px 20px rgba(0,0,0,0.3);
}

.prediction-panel {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    padding: 20px;
    margin: 20px 0;
    border: 2px solid #4A90E2;
}

.prediction-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    margin: 5px 0;
    border-radius: 10px;
    font-weight: bold;
}

.prediction-correct {
    background: linear-gradient(135deg, #2ECC71, #27AE60);
    color: white;
    animation: correctPulse 1s ease-in-out;
}

.prediction-wrong {
    background: linear-gradient(135deg, #FFB3BA, #FF6B7D);
    color: var(--text-dark);
}

@keyframes correctPulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.progress-bar {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    height: 20px;
    margin: 10px 0;
    overflow: hidden;
}

.progress-fill {
    background: linear-gradient(90deg, #32CD32, #228B22);
    height: 100%;
    transition: width 0.5s ease;
    border-radius: 10px;
}

.tips-panel {
    background: linear-gradient(135deg, #87CEEB, #4682B4);
    color: white;
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
}

.celebration {
    text-align: center;
    font-size: 4rem;
    animation: celebrate 2s ease-in-out;
}

@keyframes celebrate {
    0%, 100% { transform: scale(1) rotate(0deg); }
    25% { transform: scale(1.2) rotate(-5deg); }
    50% { transform: scale(1.3) rotate(5deg); }
    75% { transform: scale(1.1) rotate(-2deg); }
}

.canvas-container {
    border: 4px solid #FF69B4;
    border-radius: 15px;
    padding: 10px;
    background: white;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
}

.topic-badge {
    display: inline-block;
    background: linear-gradient(135deg, #FF8C00, #FF4500);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: bold;
    margin: 5px;
    font-size: 0.9rem;
}

.level-indicator {
    background: linear-gradient(135deg, #9932CC, #8A2BE2);
    color: white;
    padding: 10px 20px;
    border-radius: 15px;
    text-align: center;
    margin: 10px 0;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Ana başlık
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🎨 Pixi'nin Almanca Macerası</h1>
    <p class="subtitle">Çiz, Öğren, Eğlen! Her çizim bir macera, her kelime bir başarı! 🌟</p>
</div>
""", unsafe_allow_html=True)

# Kelime veri seti (genişletilmiş)
WORD_DATA = [
    # Hayvanlar (Animals)
    {"de": "der Hund", "en": "dog", "topic": "🐕 Hayvanlar", "difficulty": 1, "hint": "En sadık arkadaş"},
    {"de": "die Katze", "en": "cat", "topic": "🐕 Hayvanlar", "difficulty": 1, "hint": "Miyav miyav yapar"},
    {"de": "der Vogel", "en": "bird", "topic": "🐕 Hayvanlar", "difficulty": 1, "hint": "Gökyüzünde uçar"},
    {"de": "der Fisch", "en": "fish", "topic": "🐕 Hayvanlar", "difficulty": 1, "hint": "Suda yaşar"},
    {"de": "das Pferd", "en": "horse", "topic": "🐕 Hayvanlar", "difficulty": 2, "hint": "Çiftlikte koşar"},
    {"de": "die Kuh", "en": "cow", "topic": "🐕 Hayvanlar", "difficulty": 1, "hint": "Süt verir"},
    {"de": "das Schaf", "en": "sheep", "topic": "🐕 Hayvanlar", "difficulty": 2, "hint": "Yumuşak yünü var"},
    {"de": "der Elefant", "en": "elephant", "topic": "🐕 Hayvanlar", "difficulty": 2, "hint": "Çok büyük ve güçlü"},
    
    # Meyveler (Fruits)  
    {"de": "der Apfel", "en": "apple", "topic": "🍎 Meyveler", "difficulty": 1, "hint": "Kırmızı ve yuvarlak"},
    {"de": "die Banane", "en": "banana", "topic": "🍎 Meyveler", "difficulty": 1, "hint": "Sarı ve uzun"},
    {"de": "die Erdbeere", "en": "strawberry", "topic": "🍎 Meyveler", "difficulty": 2, "hint": "Kırmızı ve küçük"},
    {"de": "die Orange", "en": "orange", "topic": "🍎 Meyveler", "difficulty": 1, "hint": "Turuncu renkte"},
    {"de": "die Traube", "en": "grapes", "topic": "🍎 Meyveler", "difficulty": 2, "hint": "Salkım halinde"},
    
    # Ev Eşyaları (Home)
    {"de": "das Haus", "en": "house", "topic": "🏠 Ev", "difficulty": 1, "hint": "İçinde yaşarız"},
    {"de": "der Stuhl", "en": "chair", "topic": "🏠 Ev", "difficulty": 1, "hint": "Üzerinde otururuz"},
    {"de": "der Tisch", "en": "table", "topic": "🏠 Ev", "difficulty": 1, "hint": "Yemek yeriz üzerinde"},
    {"de": "das Bett", "en": "bed", "topic": "🏠 Ev", "difficulty": 1, "hint": "Uyuruz içinde"},
    {"de": "die Lampe", "en": "lamp", "topic": "🏠 Ev", "difficulty": 2, "hint": "Işık verir"},
    
    # Doğa (Nature)
    {"de": "die Sonne", "en": "sun", "topic": "🌞 Doğa", "difficulty": 1, "hint": "Gündüz parlar"},
    {"de": "der Mond", "en": "moon", "topic": "🌞 Doğa", "difficulty": 1, "hint": "Gecenin ışığı"},
    {"de": "der Baum", "en": "tree", "topic": "🌞 Doğa", "difficulty": 1, "hint": "Yeşil yaprakları var"},
    {"de": "die Blume", "en": "flower", "topic": "🌞 Doğa", "difficulty": 1, "hint": "Güzel kokar"},
    {"de": "die Wolke", "en": "cloud", "topic": "🌞 Doğa", "difficulty": 2, "hint": "Gökyüzünde beyaz"},
    
    # Ulaşım (Transport)
    {"de": "das Auto", "en": "car", "topic": "🚗 Ulaşım", "difficulty": 1, "hint": "Dört tekerlekli"},
    {"de": "der Bus", "en": "bus", "topic": "🚗 Ulaşım", "difficulty": 1, "hint": "Çok kişi biner"},
    {"de": "das Flugzeug", "en": "airplane", "topic": "🚗 Ulaşım", "difficulty": 2, "hint": "Havada uçar"},
    {"de": "das Fahrrad", "en": "bicycle", "topic": "🚗 Ulaşım", "difficulty": 2, "hint": "Pedal çevirerek gideriz"},
    
    # Oyuncaklar (Toys)
    {"de": "der Ball", "en": "ball", "topic": "🎾 Oyuncaklar", "difficulty": 1, "hint": "Yuvarlak ve zıplar"},
    {"de": "die Puppe", "en": "doll", "topic": "🎾 Oyuncaklar", "difficulty": 2, "hint": "Kızların oyuncağı"},
    {"de": "der Teddy", "en": "teddy bear", "topic": "🎾 Oyuncaklar", "difficulty": 2, "hint": "Yumuşak ayıcık"},
]

# Mock AI tahmin fonksiyonu (gerçek model olmadığı için)
def mock_ai_prediction(target_word, canvas_data):
    """Gerçek AI modeli olmadığı için mock tahmin fonksiyonu"""
    if canvas_data is None or canvas_data.sum() == 0:
        return []
    
    # Basit mock logic: target word'ü %70 ihtimalle ilk 3'e koyar
    all_words = [w["en"] for w in WORD_DATA]
    target_en = target_word["en"]
    
    # Target word'ü çıkar
    other_words = [w for w in all_words if w != target_en]
    random.shuffle(other_words)
    
    predictions = []
    if random.random() < 0.4:  # %40 ihtimalle 1. sırada
        predictions = [(target_en, 0.85)]
        predictions.extend([(w, random.uniform(0.1, 0.4)) for w in other_words[:4]])
    elif random.random() < 0.7:  # %30 ihtimalle 2-3. sırada
        wrong_word = random.choice(other_words)
        predictions = [(wrong_word, random.uniform(0.4, 0.6))]
        predictions.append((target_en, random.uniform(0.3, 0.5)))
        predictions.extend([(w, random.uniform(0.1, 0.3)) for w in other_words[:3] if w != wrong_word])
    else:  # %30 ihtimalle top 5'te değil
        predictions = [(w, random.uniform(0.1, 0.6)) for w in other_words[:5]]
    
    # Normalize probabilities
    total_prob = sum(p[1] for p in predictions)
    predictions = [(word, prob/total_prob) for word, prob in predictions]
    
    return sorted(predictions, key=lambda x: x[1], reverse=True)[:5]

# Oyun durumu başlatma
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = "🐕 Hayvanlar"
if 'current_round' not in st.session_state:
    st.session_state.current_round = 0
if 'total_score' not in st.session_state:
    st.session_state.total_score = 0
if 'stars_earned' not in st.session_state:
    st.session_state.stars_earned = 0
if 'current_words' not in st.session_state:
    st.session_state.current_words = []
if 'last_predictions' not in st.session_state:
    st.session_state.last_predictions = []
if 'show_celebration' not in st.session_state:
    st.session_state.show_celebration = False
if 'rounds_per_game' not in st.session_state:
    st.session_state.rounds_per_game = 5

# Sidebar - Oyun kontrolleri
with st.sidebar:
    st.markdown("""
    <div class="game-card">
        <div class="pixi-character">🤖</div>
        <h3 style="text-align: center; color: var(--primary-blue);">Pixi'nin Kontrol Paneli</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Konu seçimi
    topics = sorted(list(set([w["topic"] for w in WORD_DATA])))
    selected_topic = st.selectbox("🎯 Konu Seç:", topics, 
                                 index=topics.index(st.session_state.current_topic))
    
    # Zorluk seviyesi
    difficulty = st.select_slider("⭐ Zorluk Seviyesi:", 
                                 options=[1, 2], 
                                 format_func=lambda x: "Kolay ⭐" if x == 1 else "Orta ⭐⭐",
                                 value=1)
    
    # Tur sayısı
    rounds = st.slider("🎲 Kaç Tur Oynayalım?", 3, 10, 5)
    st.session_state.rounds_per_game = rounds
    
    st.markdown("---")
    
    # Yeni oyun başlatma
    if st.button("🎮 Yeni Macera Başlat!", key="new_game"):
        st.session_state.current_topic = selected_topic
        topic_words = [w for w in WORD_DATA if w["topic"] == selected_topic and w["difficulty"] <= difficulty]
        
        if len(topic_words) >= rounds:
            st.session_state.current_words = random.sample(topic_words, rounds)
            st.session_state.game_started = True
            st.session_state.current_round = 0
            st.session_state.total_score = 0
            st.session_state.stars_earned = 0
            st.session_state.last_predictions = []
            st.session_state.show_celebration = False
            st.experimental_rerun()
        else:
            st.error("Bu konuda yeterli kelime yok!")
    
    # Skor paneli
    st.markdown(f"""
    <div class="score-panel">
        <h3>📊 Skor Tablosu</h3>
        <div class="score-value">{st.session_state.total_score}</div>
        <div class="stars-display">{'⭐' * min(st.session_state.stars_earned, 10)}</div>
        <div>Seviye: {st.session_state.stars_earned // 3 + 1}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # İpuçları
    st.markdown("""
    <div class="tips-panel">
        <h4>💡 Pixi'nin İpuçları</h4>
        <ul>
            <li>🎨 Kalın fırça kullan</li>
            <li>🖼️ Büyük çiz</li>
            <li>⚡ Net çizgiler çek</li>
            <li>🎯 Merkeze çiz</li>
            <li>🌟 Eğlen!</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Ana oyun alanı
col1, col2 = st.columns([2, 1])

with col1:
    if not st.session_state.game_started:
        st.markdown("""
        <div class="game-card">
            <div class="pixi-character">🤖✨</div>
            <h2 style="text-align: center; color: var(--primary-blue);">Merhaba! Ben Pixi! 👋</h2>
            <p style="text-align: center; font-size: 1.2rem;">
                Seninle Almanca kelimeler öğrenmek için buradayım! <br>
                Sol taraftan bir konu seç ve maceraya başlayalım! 🚀
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    elif st.session_state.current_round >= len(st.session_state.current_words):
        # Oyun bitti
        final_stars = st.session_state.stars_earned
        performance = "Mükemmel! 🏆" if final_stars >= rounds * 3 * 0.8 else "Harika! 🎉" if final_stars >= rounds * 3 * 0.6 else "İyi çalışma! 👍"
        
        st.markdown(f"""
        <div class="game-card">
            <div class="celebration">🎉🏆🎉</div>
            <h2 style="text-align: center; color: var(--success-color);">Tebrikler! Macera Tamamlandı!</h2>
            <div style="text-align: center; margin: 20px 0;">
                <div class="score-value" style="color: var(--primary-blue);">{st.session_state.total_score} Puan</div>
                <div class="stars-display">{'⭐' * min(final_stars, 15)}</div>
                <h3 style="color: var(--primary-green);">{performance}</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Tekrar Oyna!", key="play_again"):
            st.session_state.game_started = False
            st.experimental_rerun()
    
    else:
        # Oyun devam ediyor
        current_word = st.session_state.current_words[st.session_state.current_round]
        
        # İlerleme çubuğu
        progress = (st.session_state.current_round / len(st.session_state.current_words)) * 100
        st.markdown(f"""
        <div class="level-indicator">
            🎯 Tur: {st.session_state.current_round + 1} / {len(st.session_state.current_words)}
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Kelime gösterimi
        st.markdown(f"""
        <div class="word-display">
            <div class="german-word">{current_word['de']}</div>
            <div class="word-hint">💡 {current_word['hint']}</div>
            <div class="topic-badge">{current_word['topic']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Çizim alanı
        st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=st.slider("🖌️ Fırça Kalınlığı", 5, 50, 20),
            stroke_color=st.color_picker("🎨 Fırça Rengi", "#000000"),
            background_color="#FFFFFF",
            background_image=None,
            update_streamlit=True,
            width=600,
            height=400,
            drawing_mode="freedraw",
            point_display_radius=0,
            key=f"canvas_{st.session_state.current_round}",
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Aksiyon butonları
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("🎯 Pixi Tahmin Et!", key="predict", help="Çizimini Pixi'ye göster"):
                if canvas_result.image_data is not None:
                    with st.spinner("🤖 Pixi düşünüyor..."):
                        time.sleep(1)  # Dramatik etki
                        predictions = mock_ai_prediction(current_word, canvas_result.image_data)
                        st.session_state.last_predictions = predictions
                        
                        # Doğru tahmin kontrolü
                        if predictions and predictions[0][0] == current_word["en"]:
                            # Başarılı tahmin
                            if predictions[0][1] > 0.7:  # Yüksek güven
                                points = 10
                                stars = 3
                                message = "🎉 MÜKEMMEL! İlk tahminde doğru!"
                            else:  # Düşük güven
                                points = 7
                                stars = 2
                                message = "👏 İYİ! Doğru tahmin ama biraz belirsizdi"
                            
                            st.session_state.total_score += points
                            st.session_state.stars_earned += stars
                            st.success(message)
                            st.balloons()
                            
                        elif any(pred[0] == current_word["en"] for pred in predictions):
                            # Top 5'te var ama ilk değil
                            position = next(i for i, pred in enumerate(predictions) if pred[0] == current_word["en"]) + 1
                            points = max(1, 6 - position)
                            stars = 1
                            st.session_state.total_score += points
                            st.session_state.stars_earned += stars
                            st.info(f"📍 İyi deneme! {position}. sırada buldum ({points} puan)")
                        else:
                            # Bulamadı
                            points = 1
                            st.session_state.total_score += points
                            st.warning(f"😅 Bu sefer bulamadım ama denediğin için +{points} puan!")
                        
                        st.experimental_rerun()
                else:
                    st.warning("🎨 Önce bir şey çiz!")
        
        with col_btn2:
            if st.button("⏭️ Sonraki Tur", key="next_round"):
                st.session_state.current_round += 1
                st.session_state.last_predictions = []
                st.experimental_rerun()
        
        with col_btn3:
            if st.button("🔄 Temizle", key="clear"):
                st.experimental_rerun()

with col2:
    # Pixi karakteri ve konuşma balonu
    if st.session_state.game_started and st.session_state.current_round < len(st.session_state.current_words):
        current_word = st.session_state.current_words[st.session_state.current_round]
        
        # Pixi'nin motivasyonel mesajları
        pixi_messages = [
            "🎨 Hadi, güzel bir çizim yap!",
            "✨ Sen çok yeteneklisin!",
            "🌟 Her çizim daha iyi oluyor!",
            "🚀 Macera devam ediyor!",
            "💪 Başarabilirsin!"
        ]
        
        current_message = pixi_messages[st.session_state.current_round % len(pixi_messages)]
        
        st.markdown(f"""
        <div class="game-card">
            <div class="pixi-character">🤖</div>
            <div style="background: linear-gradient(135deg, #FFE5F1, #FFB3E6); padding: 15px; border-radius: 15px; margin: 10px 0; border: 2px solid #FF69B4;">
                <h4 style="margin: 0; color: var(--text-dark); text-align: center;">💬 Pixi Diyor Ki:</h4>
                <p style="margin: 10px 0 0 0; text-align: center; font-size: 1.1rem; color: var(--text-dark);">"{current_message}"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Son tahminleri göster
    if st.session_state.last_predictions:
        current_word = st.session_state.current_words[st.session_state.current_round-1] if st.session_state.current_round > 0 else st.session_state.current_words[st.session_state.current_round]
        
        st.markdown("""
        <div class="prediction-panel">
            <h4 style="color: var(--primary-blue); text-align: center; margin-bottom: 15px;">🧠 Pixi'nin Tahminleri</h4>
        """, unsafe_allow_html=True)
        
        for i, (word, confidence) in enumerate(st.session_state.last_predictions, 1):
            is_correct = word == current_word["en"]
            css_class = "prediction-correct" if is_correct else "prediction-wrong"
            confidence_pct = int(confidence * 100)
            
            icon = "🎯" if is_correct else f"{i}️⃣"
            
            st.markdown(f"""
            <div class="prediction-item {css_class}">
                <span>{icon} {word.title()}</span>
                <span>{confidence_pct}%</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Günlük hedefler ve başarımlar
    st.markdown("""
    <div class="game-card">
        <h4 style="color: var(--primary-blue); text-align: center;">🏆 Günlük Hedefler</h4>
        <div style="margin: 15px 0;">
    """, unsafe_allow_html=True)
    
    # Hedef 1: 5 kelime çiz
    words_drawn = st.session_state.current_round
    goal1_progress = min(100, (words_drawn / 5) * 100)
    goal1_icon = "✅" if words_drawn >= 5 else "⏳"
    
    st.markdown(f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>{goal1_icon} 5 Kelime Çiz</span>
                <span>{words_drawn}/5</span>
            </div>
            <div class="progress-bar" style="height: 8px;">
                <div class="progress-fill" style="width: {goal1_progress}%; height: 100%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Hedef 2: 50 puan kazan
    goal2_progress = min(100, (st.session_state.total_score / 50) * 100)
    goal2_icon = "✅" if st.session_state.total_score >= 50 else "⏳"
    
    st.markdown(f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>{goal2_icon} 50 Puan Kazan</span>
                <span>{st.session_state.total_score}/50</span>
            </div>
            <div class="progress-bar" style="height: 8px;">
                <div class="progress-fill" style="width: {goal2_progress}%; height: 100%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Hedef 3: 10 yıldız topla
    goal3_progress = min(100, (st.session_state.stars_earned / 10) * 100)
    goal3_icon = "✅" if st.session_state.stars_earned >= 10 else "⏳"
    
    st.markdown(f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>{goal3_icon} 10 Yıldız Topla</span>
                <span>{st.session_state.stars_earned}/10</span>
            </div>
            <div class="progress-bar" style="height: 8px;">
                <div class="progress-fill" style="width: {goal3_progress}%; height: 100%;"></div>
            </div>
        </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Rozet sistemi
    badges = []
    if st.session_state.total_score >= 25:
        badges.append("🎨 İlk Sanatçı")
    if st.session_state.stars_earned >= 5:
        badges.append("⭐ Yıldız Toplayıcı")
    if words_drawn >= 3:
        badges.append("🚀 Keşifçi")
    if st.session_state.total_score >= 50:
        badges.append("🏆 Usta Çizer")
    
    if badges:
        st.markdown(f"""
        <div class="game-card">
            <h4 style="color: var(--primary-blue); text-align: center;">🎖️ Kazanılan Rozetler</h4>
            <div style="text-align: center;">
                {' '.join(f'<div style="display: inline-block; margin: 5px; padding: 8px; background: linear-gradient(135deg, #FFD700, #FFA500); border-radius: 10px; font-size: 0.9rem;">{badge}</div>' for badge in badges)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Eğlenceli istatistikler
    if st.session_state.game_started:
        avg_score = st.session_state.total_score / max(1, st.session_state.current_round) if st.session_state.current_round > 0 else 0
        
        st.markdown(f"""
        <div class="game-card">
            <h4 style="color: var(--primary-blue); text-align: center;">📈 İstatistikler</h4>
            <div style="text-align: center; margin: 15px 0;">
                <div style="margin: 8px 0;">
                    <span style="font-weight: bold;">📊 Ortalama Puan:</span><br>
                    <span style="font-size: 1.3rem; color: var(--primary-green);">{avg_score:.1f}</span>
                </div>
                <div style="margin: 8px 0;">
                    <span style="font-weight: bold;">🎯 Başarı Oranı:</span><br>
                    <span style="font-size: 1.3rem; color: var(--primary-blue);">{(st.session_state.stars_earned / max(1, st.session_state.current_round * 3) * 100):.0f}%</span>
                </div>
                <div style="margin: 8px 0;">
                    <span style="font-weight: bold;">⚡ Enerji:</span><br>
                    <span style="font-size: 1.3rem;">{'🔥' * min(5, st.session_state.stars_earned // 2 + 1)}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Alt kısım - Oyun hakkında bilgi
if not st.session_state.game_started:
    st.markdown("---")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown("""
        <div class="game-card">
            <div style="text-align: center; font-size: 3rem; margin-bottom: 10px;">🎨</div>
            <h4 style="color: var(--primary-blue); text-align: center;">Nasıl Oynanır?</h4>
            <p style="text-align: center;">Pixi sana Almanca bir kelime verir. Sen o kelimeyi çizersin, Pixi tahmin etmeye çalışır!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info2:
        st.markdown("""
        <div class="game-card">
            <div style="text-align: center; font-size: 3rem; margin-bottom: 10px;">⭐</div>
            <h4 style="color: var(--primary-green); text-align: center;">Puan Sistemi</h4>
            <p style="text-align: center;">Pixi doğru tahmin ettikçe puan ve yıldız kazanırsın. Rozetleri toplama!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info3:
        st.markdown("""
        <div class="game-card">
            <div style="text-align: center; font-size: 3rem; margin-bottom: 10px;">🧠</div>
            <h4 style="color: var(--primary-orange); text-align: center;">Öğrenme</h4>
            <p style="text-align: center;">Eğlenerek Almanca kelimeler öğren ve görsel hafızanı geliştir!</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-light); margin: 20px 0;">
    <p>🤖✨ Pixi ile birlikte öğrenmek çok eğlenceli! ✨🎨</p>
    <p style="font-size: 0.9rem;">Her çizim bir başarı, her kelime yeni bir macera! 🌟</p>
</div>
""", unsafe_allow_html=True)