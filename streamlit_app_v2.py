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

.nixi-character {
    text-align: center;
    font-size: 4rem;
    animation: nixiSpin 4s ease-in-out infinite;
    margin: 20px 0;
}

@keyframes pixiDance {
    0%, 100% { transform: rotate(-5deg) scale(1); }
    25% { transform: rotate(5deg) scale(1.1); }
    50% { transform: rotate(-3deg) scale(1.05); }
    75% { transform: rotate(3deg) scale(1.1); }
}

@keyframes nixiSpin {
    0%, 100% { transform: rotate(0deg) scale(1); }
    25% { transform: rotate(10deg) scale(1.05); }
    50% { transform: rotate(-5deg) scale(1.1); }
    75% { transform: rotate(5deg) scale(1.05); }
}

.word-display {
    text-align: center;
    background: linear-gradient(135deg, #FFD700, #FF8C00);
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    position: relative;
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

.help-button {
    position: absolute;
    top: 10px;
    right: 15px;
    background: linear-gradient(135deg, #FF69B4, #FF1493);
    color: white;
    border: none;
    border-radius: 50%;
    width: 35px;
    height: 35px;
    font-size: 1.2rem;
    cursor: pointer;
    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
}

.timer-display {
    text-align: center;
    background: linear-gradient(135deg, #FF6B6B, #EE5A24);
    color: white;
    padding: 15px;
    border-radius: 15px;
    margin: 10px 0;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.timer-value {
    font-family: 'Fredoka One', cursive;
    font-size: 2rem;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
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
    font-size: 1.8rem;
    margin: 10px 0;
    line-height: 1.2;
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
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 20px;
    margin: 20px 0;
    border: 2px solid #4A90E2;
}

.prediction-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 18px;
    margin: 8px 0;
    border-radius: 12px;
    font-weight: bold;
    font-size: 1.1rem;
    transition: all 0.3s ease;
}

.prediction-correct {
    background: linear-gradient(135deg, #2ECC71, #27AE60);
    color: white;
    animation: correctPulse 1s ease-in-out;
    box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4);
}

.prediction-wrong {
    background: linear-gradient(135deg, #FFB3BA, #FF8A9B);
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

.rules-panel {
    background: rgba(255, 255, 255, 0.98);
    color: var(--text-dark);
    padding: 25px;
    border-radius: 20px;
    margin: 20px 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    border: 3px solid #6C5CE7;
}

.rules-title {
    font-family: 'Fredoka One', cursive;
    font-size: 2rem;
    text-align: center;
    margin-bottom: 20px;
    color: #6C5CE7;
}

.rule-item {
    background: linear-gradient(135deg, #F8F9FA, #E9ECEF);
    padding: 15px;
    border-radius: 12px;
    margin: 15px 0;
    border-left: 4px solid #6C5CE7;
}

.rule-item h4 {
    color: #6C5CE7;
    margin-top: 0;
    margin-bottom: 10px;
}

.rule-item p, .rule-item ul {
    color: var(--text-dark);
    margin-bottom: 5px;
}

.stats-text {
    color: var(--text-dark) !important;
    font-weight: bold;
}

.badge-display {
    display: inline-block;
    background: linear-gradient(135deg, #FFD700, #FFA500);
    color: var(--text-dark);
    padding: 8px 12px;
    border-radius: 20px;
    font-weight: bold;
    margin: 5px;
    font-size: 0.9rem;
    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
}

.nixi-intro {
    background: linear-gradient(135deg, #A29BFE, #74B9FF);
    color: white;
    padding: 25px;
    border-radius: 20px;
    margin: 20px 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    text-align: center;
}

.intro-text {
    font-size: 1.2rem;
    line-height: 1.6;
    margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

# Ana başlık
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🎨 Pixi & Nixi'nin Almanca Macerası</h1>
    <p class="subtitle">Çiz, Yarış, Öğren! Zamanla yarış ve en yüksek puanı topla! 🏁⚡</p>
</div>
""", unsafe_allow_html=True)

# Kelime veri seti (genişletilmiş)
WORD_DATA = [
    # Hayvanlar (Animals)
    {"de": "der Hund", "en": "dog", "topic": "🐕 Hayvanlar", "difficulty": 1, "meaning": "Köpek - İnsanın en sadık dostu"},
    {"de": "die Katze", "en": "cat", "topic": "🐕 Hayvanlar", "difficulty": 1, "meaning": "Kedi - Miyav miyav yapan sevimli hayvan"},
    {"de": "der Vogel", "en": "bird", "topic": "🐕 Hayvanlar", "difficulty": 1, "meaning": "Kuş - Gökyüzünde uçan kanatlı hayvan"},
    {"de": "der Fisch", "en": "fish", "topic": "🐕 Hayvanlar", "difficulty": 1, "meaning": "Balık - Suda yaşayan nefes alan hayvan"},
    {"de": "das Pferd", "en": "horse", "topic": "🐕 Hayvanlar", "difficulty": 2, "meaning": "At - Çiftlikte yaşayan büyük ve güçlü hayvan"},
    {"de": "die Kuh", "en": "cow", "topic": "🐕 Hayvanlar", "difficulty": 1, "meaning": "İnek - Süt veren çiftlik hayvanı"},
    {"de": "das Schaf", "en": "sheep", "topic": "🐕 Hayvanlar", "difficulty": 2, "meaning": "Koyun - Yumuşak yünlü beyaz hayvan"},
    {"de": "der Elefant", "en": "elephant", "topic": "🐕 Hayvanlar", "difficulty": 2, "meaning": "Fil - Çok büyük ve güçlü, hortumlu hayvan"},
    
    # Meyveler (Fruits)  
    {"de": "der Apfel", "en": "apple", "topic": "🍎 Meyveler", "difficulty": 1, "meaning": "Elma - Kırmızı veya yeşil yuvarlak meyve"},
    {"de": "die Banane", "en": "banana", "topic": "🍎 Meyveler", "difficulty": 1, "meaning": "Muz - Sarı renkli uzun ve kavisli meyve"},
    {"de": "die Erdbeere", "en": "strawberry", "topic": "🍎 Meyveler", "difficulty": 2, "meaning": "Çilek - Kırmızı renkte küçük ve tatlı meyve"},
    {"de": "die Orange", "en": "orange", "topic": "🍎 Meyveler", "difficulty": 1, "meaning": "Portakal - Turuncu renkli sulu meyve"},
    {"de": "die Traube", "en": "grapes", "topic": "🍎 Meyveler", "difficulty": 2, "meaning": "Üzüm - Salkım halindeki küçük meyveler"},
    
    # Ev Eşyaları (Home)
    {"de": "das Haus", "en": "house", "topic": "🏠 Ev", "difficulty": 1, "meaning": "Ev - İçinde yaşadığımız yapı"},
    {"de": "der Stuhl", "en": "chair", "topic": "🏠 Ev", "difficulty": 1, "meaning": "Sandalye - Üzerinde oturduğumuz eşya"},
    {"de": "der Tisch", "en": "table", "topic": "🏠 Ev", "difficulty": 1, "meaning": "Masa - Üzerinde yemek yediğimiz eşya"},
    {"de": "das Bett", "en": "bed", "topic": "🏠 Ev", "difficulty": 1, "meaning": "Yatak - İçinde uyuduğumuz eşya"},
    {"de": "die Lampe", "en": "lamp", "topic": "🏠 Ev", "difficulty": 2, "meaning": "Lamba - Işık veren ev eşyası"},
    
    # Doğa (Nature)
    {"de": "die Sonne", "en": "sun", "topic": "🌞 Doğa", "difficulty": 1, "meaning": "Güneş - Gündüz parlayan ışık kaynağı"},
    {"de": "der Mond", "en": "moon", "topic": "🌞 Doğa", "difficulty": 1, "meaning": "Ay - Gecenin ışığı, yuvarlak gök cismi"},
    {"de": "der Baum", "en": "tree", "topic": "🌞 Doğa", "difficulty": 1, "meaning": "Ağaç - Yeşil yapraklı büyük bitki"},
    {"de": "die Blume", "en": "flower", "topic": "🌞 Doğa", "difficulty": 1, "meaning": "Çiçek - Güzel kokan renkli bitki"},
    {"de": "die Wolke", "en": "cloud", "topic": "🌞 Doğa", "difficulty": 2, "meaning": "Bulut - Gökyüzünde beyaz pamuk gibi"},
    
    # Ulaşım (Transport)
    {"de": "das Auto", "en": "car", "topic": "🚗 Ulaşım", "difficulty": 1, "meaning": "Araba - Dört tekerlekli taşıt"},
    {"de": "der Bus", "en": "bus", "topic": "🚗 Ulaşım", "difficulty": 1, "meaning": "Otobüs - Çok kişinin bindiği büyük taşıt"},
    {"de": "das Flugzeug", "en": "airplane", "topic": "🚗 Ulaşım", "difficulty": 2, "meaning": "Uçak - Havada uçan taşıt"},
    {"de": "das Fahrrad", "en": "bicycle", "topic": "🚗 Ulaşım", "difficulty": 2, "meaning": "Bisiklet - Pedal çevirerek gittiğimiz taşıt"},
    
    # Oyuncaklar (Toys)
    {"de": "der Ball", "en": "ball", "topic": "🎾 Oyuncaklar", "difficulty": 1, "meaning": "Top - Yuvarlak oyuncak, zıplar ve yuvarlanır"},
    {"de": "die Puppe", "en": "doll", "topic": "🎾 Oyuncaklar", "difficulty": 2, "meaning": "Bebek - Oyuncak bebek, genellikle kızların oyuncağı"},
    {"de": "der Teddy", "en": "teddy bear", "topic": "🎾 Oyuncaklar", "difficulty": 2, "meaning": "Oyuncak Ayı - Yumuşak, sevimli oyuncak ayıcık"},
]

# Rozet sistemi
BADGES = {
    "speed_demon": {"name": "🏎️ Hızlı Çizer", "desc": "3 kez 20 saniyeden fazla süre bırak", "condition": "speed_achievements", "target": 3},
    "artist": {"name": "🎨 Sanatçı", "desc": "5 kez üst üste Pixi ilk tahminde bulsun", "condition": "consecutive_firsts", "target": 5},
    "perfectionist": {"name": "⭐ Mükemmeliyetçi", "desc": "10 kez ilk tahminde doğru çiz", "condition": "total_firsts", "target": 10},
    "speedster": {"name": "⚡ Sürat Tanrısı", "desc": "Bir oyunda ortalama 22+ saniye bırak", "condition": "avg_time", "target": 22},
    "word_master": {"name": "📚 Kelime Ustası", "desc": "20 farklı kelime çiz", "condition": "unique_words", "target": 20},
    "streak_master": {"name": "🔥 Seri Usta", "desc": "7 kez üst üste doğru tahmin ettir", "condition": "win_streak", "target": 7},
}

# Mock AI tahmin fonksiyonu (3 tahmin)
def mock_ai_prediction(target_word, canvas_data):
    """Gerçek AI modeli olmadığı için mock tahmin fonksiyonu - sadece 3 tahmin"""
    if canvas_data is None or canvas_data.sum() == 0:
        return []
    
    # Basit mock logic: target word'ü %60 ihtimalle ilk 3'e koyar
    all_words = [w["en"] for w in WORD_DATA]
    target_en = target_word["en"]
    
    # Target word'ü çıkar
    other_words = [w for w in all_words if w != target_en]
    random.shuffle(other_words)
    
    predictions = []
    if random.random() < 0.5:  # %50 ihtimalle 1. sırada
        predictions = [(target_en, 0.85)]
        predictions.extend([(w, random.uniform(0.1, 0.4)) for w in other_words[:2]])
    elif random.random() < 0.8:  # %30 ihtimalle 2-3. sırada  
        wrong_word = random.choice(other_words)
        predictions = [(wrong_word, random.uniform(0.4, 0.6))]
        predictions.append((target_en, random.uniform(0.25, 0.45)))
        predictions.append((other_words[0] if other_words[0] != wrong_word else other_words[1], random.uniform(0.1, 0.3)))
    else:  # %20 ihtimalle top 3'te değil
        predictions = [(w, random.uniform(0.1, 0.6)) for w in other_words[:3]]
    
    # Normalize probabilities
    total_prob = sum(p[1] for p in predictions)
    predictions = [(word, prob/total_prob) for word, prob in predictions]
    
    return sorted(predictions, key=lambda x: x[1], reverse=True)[:3]  # Sadece 3 tahmin

# Rozet kontrol fonksiyonu
def check_badges():
    badges_earned = []
    
    # Hızlı çizer
    if st.session_state.get('speed_achievements', 0) >= 3:
        badges_earned.append("speed_demon")
    
    # Sanatçı 
    if st.session_state.get('consecutive_firsts', 0) >= 5:
        badges_earned.append("artist")
    
    # Mükemmeliyetçi
    if st.session_state.get('total_firsts', 0) >= 10:
        badges_earned.append("perfectionist")
    
    # Kelime ustası
    if len(st.session_state.get('drawn_words', set())) >= 20:
        badges_earned.append("word_master")
    
    return badges_earned

# Oyun durumu başlatma
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'intro_shown' not in st.session_state:
    st.session_state.intro_shown = False
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
if 'show_rules' not in st.session_state:
    st.session_state.show_rules = False
if 'timer_started' not in st.session_state:
    st.session_state.timer_started = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'time_left' not in st.session_state:
    st.session_state.time_left = 25
if 'game_time' not in st.session_state:
    st.session_state.game_time = 25
if 'show_word_meaning' not in st.session_state:
    st.session_state.show_word_meaning = False
if 'consecutive_firsts' not in st.session_state:
    st.session_state.consecutive_firsts = 0
if 'total_firsts' not in st.session_state:
    st.session_state.total_firsts = 0
if 'speed_achievements' not in st.session_state:
    st.session_state.speed_achievements = 0
if 'drawn_words' not in st.session_state:
    st.session_state.drawn_words = set()
if 'win_streak' not in st.session_state:
    st.session_state.win_streak = 0

# Sidebar - Oyun kontrolleri
with st.sidebar:
    st.markdown("""
    <div class="game-card">
        <div class="pixi-character">🤖</div>
        <div class="nixi-character">🧠</div>
        <h3 style="text-align: center; color: var(--primary-blue);">Pixi & Nixi Kontrol Paneli</h3>
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
    
    # Zaman ayarı
    game_time = st.slider("⏰ Çizim Süresi (saniye)", 15, 30, 25)
    st.session_state.game_time = game_time
    
    st.markdown("---")
    
    # Yeni oyun başlatma
    if st.button("🎮 Yeni Macera Başlat!", key="new_game"):
        st.session_state.current_topic = selected_topic
        topic_words = [w for w in WORD_DATA if w["topic"] == selected_topic and w["difficulty"] <= difficulty]
        
        if len(topic_words) >= rounds:
            st.session_state.current_words = random.sample(topic_words, rounds)
            st.session_state.game_started = True
            st.session_state.intro_shown = False
            st.session_state.current_round = 0
            st.session_state.total_score = 0
            st.session_state.stars_earned = 0
            st.session_state.last_predictions = []
            st.session_state.show_celebration = False
            st.session_state.show_rules = False
            st.session_state.timer_started = False
            st.session_state.start_time = None
            st.session_state.time_left = game_time
            st.session_state.show_word_meaning = False
            st.experimental_rerun()
        else:
            st.error("Bu konuda yeterli kelime yok!")
    
    # Kuralları göster/gizle
    if st.button("📖 Oyun Kuralları", key="show_rules_btn"):
        st.session_state.show_rules = not st.session_state.show_rules
        st.experimental_rerun()
    
    # Skor paneli - Yıldızları düzeltildi
    star_lines = []
    stars_to_show = min(st.session_state.stars_earned, 15)
    stars_per_line = 5
    
    for i in range(0, stars_to_show, stars_per_line):
        line_stars = min(stars_per_line, stars_to_show - i)
        star_lines.append('⭐' * line_stars)
    
    if not star_lines:
        star_lines = ['☆☆☆☆☆']
    
    stars_display = '<br>'.join(star_lines)
    
    st.markdown(f"""
    <div class="score-panel">
        <h3>📊 Skor Tablosu</h3>
        <div class="score-value">{st.session_state.total_score}</div>
        <div class="stars-display">{stars_display}</div>
        <div>Seviye: {st.session_state.stars_earned // 3 + 1}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Rozet paneli
    current_badges = check_badges()
    if current_badges:
        st.markdown("""
        <div class="game-card">
            <h4 style="color: var(--primary-blue); text-align: center;">🏆 Kazanılan Rozetler</h4>
        """, unsafe_allow_html=True)
        for badge_id in current_badges:
            badge = BADGES[badge_id]
            st.markdown(f"""
            <div class="badge-display">{badge['name']}</div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # İpuçları
    st.markdown("""
    <div class="tips-panel">
        <h4>💡 Nixi'nin İpuçları</h4>
        <ul>
            <li>🎨 Basit ve anlaşılır çiz</li>
            <li>⚡ Hızlı ol, zaman puanın</li>
            <li>🖼️ Büyük çiz</li>
            <li>🎯 Merkeze çiz</li>
            <li>🌟 Eğlen!</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Oyun kuralları paneli
if st.session_state.show_rules:
    st.markdown("""
    <div class="rules-panel">
        <h2 class="rules-title">📖 Oyun Kuralları ve Puanlama</h2>
        
        <div class="rule-item">
            <h4>🎯 Nasıl Oynanır?</h4>
            <p><strong>Nixi</strong> sana Almanca bir kelime verir ve <strong>25 saniye</strong> süre tanır.</p>
            <p>Sen o kelimeyi çizim alanına çizersin.</p>
            <p><strong>Pixi</strong> çizimini görür ve 3 tahmin yapar.</p>
            <p>Hem doğru tahmin hem de kalan süreye göre puan kazanırsın!</p>
        </div>
        
        <div class="rule-item">
            <h4>⭐ Puanlama Sistemi</h4>
            <p><strong>Puan = Kalan Süre × Tahmin Çarpanı</strong></p>
            <ul>
                <li><strong>🥇 1. tahminde doğru:</strong> × 20 çarpan + 3 yıldız</li>
                <li><strong>🥈 2. tahminde doğru:</strong> × 10 çarpan + 2 yıldız</li>
                <li><strong>🥉 3. tahminde doğru:</strong> × 5 çarpan + 1 yıldız</li>
                <li><strong>❌ Bulamazsa:</strong> Kalan süre kadar puan</li>
            </ul>
            <p><em>Örnek: 15 saniye kaldı ve Pixi 1. tahminde buldu = 15 × 20 = 300 puan!</em></p>
        </div>
        
        <div class="rule-item">
            <h4>🏆 Özel Rozetler</h4>
            <ul>
                <li><strong>🏎️ Hızlı Çizer:</strong> 3 kez 20+ saniye bırak</li>
                <li><strong>🎨 Sanatçı:</strong> 5 kez üst üste ilk tahminde doğru</li>
                <li><strong>⭐ Mükemmeliyetçi:</strong> 10 kez ilk tahminde doğru</li>
                <li><strong>📚 Kelime Ustası:</strong> 20 farklı kelime çiz</li>
                <li><strong>🔥 Seri Usta:</strong> 7 kez üst üste doğru tahmin ettir</li>
            </ul>
        </div>
        
        <div class="rule-item">
            <h4>🎨 Çizim İpuçları</h4>
            <ul>
                <li><strong>Hız:</strong> Çabuk ol, her saniye değerli!</li>
                <li><strong>Netlik:</strong> Basit ve anlaşılır çiz</li>
                <li><strong>Boyut:</strong> Büyük ve merkezi çiz</li>
                <li><strong>Detay:</strong> Önemli özellikleri vurgula</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Nixi tanıtım paneli
if st.session_state.game_started and not st.session_state.intro_shown:
    st.markdown("""
    <div class="nixi-intro">
        <div class="nixi-character">🧠</div>
        <h2 style="margin: 0;">Merhaba! Ben Nixi! 🧠✨</h2>
        
        <div class="intro-text">
            <p>Pixi ile oyun oynuyoruz ve sen de katılmak ister misin? 🎮</p>
            <p><strong>İşte plan:</strong> Ben sana Almanca bir kelime vereceğim ve sen onu çizeceksin! 
            Pixi de senin çizdiğin şeyin benim verdiğim kelimeyi tahmin etmeye çalışacak. 🎯</p>
            
            <p><strong>Eğer çok iyi çizersen ve Pixi ilk tahminde bulursa:</strong><br>
            Kalan süre × 20 = SÜPER PUAN! ⚡</p>
            
            <p><strong>Çizimlerine göre sana özel rozetler vereceğim:</strong><br>
            🏎️ Hızlı Çizer, 🎨 Sanatçı, ⭐ Mükemmeliyetçi ve daha fazlası!</p>
            
            <p><strong>25 saniye vereceğim!</strong> Hem hızlı hem anlaşılır çizmelisin. 
            Ne kadar çok zaman kalırsa, o kadar çok puan kazanırsın! 🏁</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_intro1, col_intro2 = st.columns(2)
    with col_intro1:
        if st.button("🚀 Hadi Başlayalım!", key="start_intro"):
            st.session_state.intro_shown = True
            st.experimental_rerun()
    
    with col_intro2:
        if st.button("📖 Önce Kuralları Oku", key="rules_intro"):
            st.session_state.show_rules = True
            st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Ana oyun alanı
elif st.session_state.game_started and st.session_state.intro_shown:
    col1, col2 = st.columns([2, 1])

    with col1:
        if st.session_state.current_round >= len(st.session_state.current_words):
            # Oyun bitti
            final_stars = st.session_state.stars_earned
            total_rounds = len(st.session_state.current_words)
            performance = "Muhteşem! 🏆" if final_stars >= total_rounds * 2.5 else "Harika! 🎉" if final_stars >= total_rounds * 1.5 else "İyi çalışma! 👍"
            
            # Rozet kontrolü
            current_badges = check_badges()
            
            st.markdown(f"""
            <div class="game-card">
                <div class="celebration">🎉🏆🎉</div>
                <h2 style="text-align: center; color: var(--success-color);">Tebrikler! Macera Tamamlandı!</h2>
                <div style="text-align: center; margin: 20px 0;">
                    <div class="score-value" style="color: var(--primary-blue);">{st.session_state.total_score} Puan</div>
                    <div class="stars-display">{stars_display}</div>
                    <h3 style="color: var(--primary-green);">{performance}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            if current_badges:
                st.markdown("<h4 style='text-align: center;'>🎖️ Yeni Rozetler Kazandın!</h4>", unsafe_allow_html=True)
                for badge_id in current_badges:
                    badge = BADGES[badge_id]
                    st.markdown(f"<div style='text-align: center; margin: 10px;'><span class='badge-display'>{badge['name']}</span><br><small>{badge['desc']}</small></div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button("🔄 Tekrar Oyna!", key="play_again"):
                st.session_state.game_started = False
                st.session_state.intro_shown = False
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
            
            # Zamanlayıcı
            if st.session_state.timer_started and st.session_state.start_time:
                elapsed = time.time() - st.session_state.start_time
                time_left = max(0, st.session_state.game_time - elapsed)
                st.session_state.time_left = time_left
                
                if time_left <= 0:
                    # Süre bitti
                    st.session_state.timer_started = False
                    st.warning("⏰ Süre bitti! Yine de tahmin edebiliriz.")
            
            # Timer display
            if st.session_state.timer_started:
                timer_color = "#FF6B6B" if st.session_state.time_left < 10 else "#FFD93D" if st.session_state.time_left < 15 else "#6BCF7F"
                st.markdown(f"""
                <div class="timer-display" style="background: linear-gradient(135deg, {timer_color}, {timer_color}AA);">
                    <div class="timer-value">⏰ {int(st.session_state.time_left)} saniye</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Kelime gösterimi with help button
            st.markdown(f"""
            <div class="word-display">
                <div class="german-word">{current_word['de']}</div>
                <div class="topic-badge">{current_word['topic']}</div>
                <button class="help-button" onclick="document.getElementById('help_button').click()">?</button>
            </div>
            """, unsafe_allow_html=True)
            
            # Gizli help button for streamlit
            if st.button("", key="help_button", help="Kelimenin anlamını öğren"):
                st.session_state.show_word_meaning = not st.session_state.show_word_meaning
                st.experimental_rerun()
            
            # Kelime anlamını göster
            if st.session_state.show_word_meaning:
                st.info(f"💡 **{current_word['de']}** = {current_word['meaning']}")
            
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
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                if st.button("🎯 Pixi Tahmin Et!", key="predict", help="Çizimini Pixi'ye göster"):
                    if canvas_result.image_data is not None:
                        # Timer'ı durdur
                        final_time_left = st.session_state.time_left if st.session_state.timer_started else st.session_state.game_time
                        st.session_state.timer_started = False
                        
                        with st.spinner("🤖 Pixi düşünüyor..."):
                            time.sleep(1)  # Dramatik etki
                            predictions = mock_ai_prediction(current_word, canvas_result.image_data)
                            st.session_state.last_predictions = predictions
                            
                            # Doğru tahmin kontrolü - doğru target ile karşılaştır
                            target_en = current_word["en"]
                            correct_position = None
                            
                            for i, (pred_word, confidence) in enumerate(predictions):
                                if pred_word == target_en:
                                    correct_position = i
                                    break
                            
                            # Kelimeyi çizilen listesine ekle
                            st.session_state.drawn_words.add(target_en)
                            
                            if correct_position is not None:
                                # Başarılı tahmin
                                base_points = int(final_time_left)
                                if correct_position == 0:  # 1. sırada
                                    multiplier = 20
                                    stars = 3
                                    message = "🎉 MÜKEMMEL! İlk tahminde doğru!"
                                    st.session_state.consecutive_firsts += 1
                                    st.session_state.total_firsts += 1
                                    st.session_state.win_streak += 1
                                    if final_time_left >= 20:
                                        st.session_state.speed_achievements += 1
                                    st.success(message)
                                    st.balloons()
                                elif correct_position == 1:  # 2. sırada
                                    multiplier = 10
                                    stars = 2
                                    message = "👏 SÜPER! İkinci tahminde buldum!"
                                    st.session_state.consecutive_firsts = 0
                                    st.session_state.win_streak += 1
                                    st.success(message)
                                else:  # 3. sırada
                                    multiplier = 5
                                    stars = 1
                                    message = "✨ İYİ! Üçüncü tahminde doğru!"
                                    st.session_state.consecutive_firsts = 0
                                    st.session_state.win_streak += 1
                                    st.info(message)
                                
                                points = base_points * multiplier
                                st.session_state.total_score += points
                                st.session_state.stars_earned += stars
                                st.info(f"⚡ {int(final_time_left)} saniye × {multiplier} = **{points} PUAN!**")
                                
                            else:
                                # Bulamadı
                                points = int(final_time_left)
                                st.session_state.total_score += points
                                st.session_state.consecutive_firsts = 0
                                st.session_state.win_streak = 0
                                st.warning(f"😅 Bu sefer bulamadım ama {points} puan kazandın! Doğrusu: **{current_word['de']}**")
                            
                            st.experimental_rerun()
                    else:
                        st.warning("🎨 Önce bir şey çiz!")
            
            with col_btn2:
                if not st.session_state.timer_started:
                    if st.button("▶️ Başla", key="start_timer"):
                        st.session_state.timer_started = True
                        st.session_state.start_time = time.time()
                        st.session_state.time_left = st.session_state.game_time
                        st.experimental_rerun()
                else:
                    if st.button("⏸️ Durdur", key="pause_timer"):
                        st.session_state.timer_started = False
                        st.experimental_rerun()
            
            with col_btn3:
                if st.button("⏭️ Sonraki", key="next_round"):
                    st.session_state.current_round += 1
                    st.session_state.last_predictions = []
                    st.session_state.timer_started = False
                    st.session_state.start_time = None
                    st.session_state.time_left = st.session_state.game_time
                    st.session_state.show_word_meaning = False
                    st.experimental_rerun()
            
            with col_btn4:
                if st.button("🧽 Silgi", key="eraser"):
                    # Canvas'ı temizlemek için key'i değiştir
                    st.session_state[f"canvas_clear_{st.session_state.current_round}"] = True
                    st.experimental_rerun()

    with col2:
        # Nixi ve Pixi karakterleri
        st.markdown("""
        <div class="game-card">
            <div class="nixi-character">🧠</div>
            <div style="background: linear-gradient(135deg, #A29BFE, #74B9FF); padding: 15px; border-radius: 15px; margin: 10px 0; border: 2px solid #6C5CE7;">
                <h4 style="margin: 0; color: white; text-align: center;">💬 Nixi Diyor Ki:</h4>
                <p style="margin: 10px 0 0 0; text-align: center; font-size: 1.1rem; color: white;">"⚡ Hızlı çiz, zaman puanın!"</p>
            </div>
            
            <div class="pixi-character">🤖</div>
            <div style="background: linear-gradient(135deg, #FFE5F1, #FFB3E6); padding: 15px; border-radius: 15px; margin: 10px 0; border: 2px solid #FF69B4;">
                <h4 style="margin: 0; color: var(--text-dark); text-align: center;">💬 Pixi Diyor Ki:</h4>
                <p style="margin: 10px 0 0 0; text-align: center; font-size: 1.1rem; color: var(--text-dark);">"🎨 Tahmin etmeye hazırım!"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Son tahminleri göster - sadece 3 tahmin ve doğru hedefi kontrol et
        if st.session_state.last_predictions:
            current_word_for_pred = st.session_state.current_words[st.session_state.current_round-1] if st.session_state.current_round > 0 else st.session_state.current_words[st.session_state.current_round]
            
            st.markdown("""
            <div class="prediction-panel">
                <h4 style="color: var(--primary-blue); text-align: center; margin-bottom: 15px;">🧠 Pixi'nin Tahminleri</h4>
            """, unsafe_allow_html=True)
            
            for i, (word, confidence) in enumerate(st.session_state.last_predictions, 1):
                is_correct = word == current_word_for_pred["en"]  # Doğru kelime ile karşılaştır
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
        
        # İstatistikler - Beyaz zemin sorunu düzeltildi
        if st.session_state.game_started:
            avg_score = st.session_state.total_score / max(1, st.session_state.current_round) if st.session_state.current_round > 0 else 0
            
            st.markdown(f"""
            <div class="game-card">
                <h4 style="color: var(--primary-blue); text-align: center;">📈 İstatistikler</h4>
                <div style="text-align: center; margin: 15px 0;">
                    <div style="margin: 8px 0;">
                        <span class="stats-text">📊 Ort. Puan:</span><br>
                        <span style="font-size: 1.3rem; color: var(--primary-green); font-weight: bold;">{avg_score:.0f}</span>
                    </div>
                    <div style="margin: 8px 0;">
                        <span class="stats-text">🔥 Seri:</span><br>
                        <span style="font-size: 1.3rem; color: var(--primary-blue); font-weight: bold;">{st.session_state.win_streak}</span>
                    </div>
                    <div style="margin: 8px 0;">
                        <span class="stats-text">🎨 İlk Tahmin:</span><br>
                        <span style="font-size: 1.3rem; color: var(--primary-orange); font-weight: bold;">{st.session_state.total_firsts}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Giriş ekranı
else:
    st.markdown("""
    <div class="game-card">
        <div class="pixi-character">🤖</div>
        <div class="nixi-character">🧠</div>
        <h2 style="text-align: center; color: var(--primary-blue);">Merhaba! Biz Pixi & Nixi! 👋</h2>
        <p style="text-align: center; font-size: 1.2rem;">
            Seninle hızlı çizim yarışı yaparak Almanca kelimeler öğrenmek için buradayız! <br>
            Sol taraftan ayarlarını yap ve maceraya başla! 🚀
        </p>
        <p style="text-align: center; font-size: 1rem; color: var(--text-light);">
            📖 Oyun kurallarını öğrenmek için sol menüden "Oyun Kuralları" butonuna tıkla!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Alt bilgi panelleri
    st.markdown("---")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown("""
        <div class="game-card">
            <div style="text-align: center; font-size: 3rem; margin-bottom: 10px;">⚡</div>
            <h4 style="color: var(--primary-blue); text-align: center;">Hızlı Çizim</h4>
            <p style="text-align: center;">25 saniye içinde çiz! Kalan süre = ekstra puan!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info2:
        st.markdown("""
        <div class="game-card">
            <div style="text-align: center; font-size: 3rem; margin-bottom: 10px;">🏆</div>
            <h4 style="color: var(--primary-green); text-align: center;">Süper Puanlar</h4>
            <p style="text-align: center;">İlk tahminde doğru = Kalan süre × 20 puan!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info3:
        st.markdown("""
        <div class="game-card">
            <div style="text-align: center; font-size: 3rem; margin-bottom: 10px;">🎖️</div>
            <h4 style="color: var(--primary-orange); text-align: center;">Özel Rozetler</h4>
            <p style="text-align: center;">Başarılarınla özel rozetler kazan!</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-light); margin: 20px 0;">
    <p>🤖🧠 Pixi & Nixi ile birlikte hızlı öğrenme macerası! 🚀</p>
    <p style="font-size: 0.9rem;">Her saniye değerli, her çizim bir başarı! ⚡</p>
</div>
""", unsafe_allow_html=True)