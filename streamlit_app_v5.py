# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import random
import time

# Sayfa yapılandırması
st.set_page_config(
    page_title="🎨 Nixi ve Pixi'nin Almanca Oyunu", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gelişmiş CSS stilleri (Değişiklik yapıldı)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka+One:wght@400&family=Comic+Neue:wght@300;400;700&display=swap');
:root {
    --primary-blue: #4A90E2; --primary-pink: #FF69B4; --primary-yellow: #FFD700;
    --primary-green: #32CD32; --primary-orange: #FF8C00; 
    --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --card-shadow: 0 10px 30px rgba(0,0,0,0.2); --text-dark: #2C3E50; --text-light: #7F8C8D;
    --success-color: #2ECC71; --warning-color: #F39C12; --error-color: #E74C3C;
}
body { background: var(--bg-gradient); font-family: 'Comic Neue', cursive; }
.main-header {
    background: linear-gradient(90deg, #FF69B4, #4A90E2, #32CD32, #FFD700);
    background-size: 400% 400%; animation: gradientShift 4s ease infinite;
    text-align: center; padding: 20px; border-radius: 20px; margin-bottom: 20px;
    box-shadow: var(--card-shadow);
}
@keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
.main-title { font-family: 'Fredoka One', cursive; font-size: 3rem; color: white; text-shadow: 3px 3px 6px rgba(0,0,0,0.3); margin: 0; animation: bounce 2s infinite; }
@keyframes bounce { 0%, 20%, 50%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-10px); } 60% { transform: translateY(-5px); } }
.subtitle { color: white; font-size: 1.2rem; margin: 10px 0 0 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
.game-card {
    background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border-radius: 20px; padding: 25px;
    box-shadow: var(--card-shadow); border: 3px solid transparent; background-image: linear-gradient(white, white), linear-gradient(45deg, #FF69B4, #4A90E2);
    background-origin: border-box; background-clip: content-box, border-box; margin-bottom: 20px;
}
.game-card p, .game-card h2, .game-card h3 { color: var(--text-dark); }
.pixi-character, .nixi-character { text-align: center; font-size: 4rem; margin: 20px 0; }
.pixi-character { animation: pixiDance 3s ease-in-out infinite; }
.nixi-character { animation: nixiSpin 4s ease-in-out infinite; }
@keyframes pixiDance { 0%, 100% { transform: rotate(-5deg) scale(1); } 25% { transform: rotate(5deg) scale(1.1); } 50% { transform: rotate(-3deg) scale(1.05); } 75% { transform: rotate(3deg) scale(1.1); } }
@keyframes nixiSpin { 0%, 100% { transform: rotate(0deg) scale(1); } 25% { transform: rotate(10deg) scale(1.05); } 50% { transform: rotate(-5deg) scale(1.1); } 75% { transform: rotate(5deg) scale(1.05); } }
.word-display { text-align: center; background: linear-gradient(135deg, #FFD700, #FF8C00); padding: 20px; border-radius: 15px; margin: 20px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
.german-word { font-family: 'Fredoka One', cursive; font-size: 2.5rem; color: var(--text-dark); margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
.timer-display { text-align: center; background: linear-gradient(135deg, #FF6B6B, #EE5A24); color: white; padding: 15px; border-radius: 15px; margin: 10px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
.timer-value { font-family: 'Fredoka One', cursive; font-size: 2rem; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
.score-panel { background: linear-gradient(135deg, #32CD32, #228B22); color: white; padding: 20px; border-radius: 15px; text-align: center; margin: 15px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
.score-value { font-family: 'Fredoka One', cursive; font-size: 2.5rem; margin: 10px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
.stars-display { font-size: 1.8rem; margin: 10px 0; line-height: 1.2; }
.prediction-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; margin: 8px 0; border-radius: 12px; font-weight: bold; font-size: 1.1rem; transition: all 0.3s ease; }
.prediction-correct { background: linear-gradient(135deg, #2ECC71, #27AE60); color: white; animation: correctPulse 1s ease-in-out; box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4); }
.prediction-wrong { background: linear-gradient(135deg, #FFB3BA, #FF8A9B); color: var(--text-dark); }
@keyframes correctPulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
.progress-bar { background: rgba(255, 255, 255, 0.3); border-radius: 10px; height: 20px; margin: 10px 0; overflow: hidden; }
.progress-fill { background: linear-gradient(90deg, #32CD32, #228B22); height: 100%; transition: width 0.5s ease; border-radius: 10px; }
.tips-panel { background: linear-gradient(135deg, #87CEEB, #4682B4); color: white; padding: 20px; border-radius: 15px; margin: 20px 0; }
.celebration { text-align: center; font-size: 4rem; animation: celebrate 2s ease-in-out; }
@keyframes celebrate { 0%, 100% { transform: scale(1) rotate(0deg); } 25% { transform: scale(1.2) rotate(-5deg); } 50% { transform: scale(1.3) rotate(5deg); } 75% { transform: scale(1.1) rotate(-2deg); } }
.canvas-container { border: 4px solid #FF69B4; border-radius: 15px; padding: 10px; background: white; box-shadow: inset 0 2px 10px rgba(0,0,0,0.1); }
.topic-badge { display: inline-block; background: linear-gradient(135deg, #FF8C00, #FF4500); color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; margin: 5px; font-size: 0.9rem; }
.level-indicator { background: linear-gradient(135deg, #9932CC, #8A2BE2); color: white; padding: 10px 20px; border-radius: 15px; text-align: center; margin: 10px 0; font-weight: bold; }
.rules-panel { background: rgba(255, 255, 255, 0.98); color: var(--text-dark); padding: 25px; border-radius: 20px; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.2); border: 3px solid #6C5CE7; }
.rules-title { font-family: 'Fredoka One', cursive; font-size: 2rem; text-align: center; margin-bottom: 20px; color: #6C5CE7; }
.nixi-intro { background: linear-gradient(135deg, #A29BFE, #74B9FF); color: white; padding: 25px; border-radius: 20px; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center; }
.badges-panel { background: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 20px; box-shadow: var(--card-shadow); margin-top: 20px; }
.badges-panel h4 { text-align: center; color: var(--text-dark); }
.badges-panel ul { list-style-type: none; padding: 0; }
.badges-panel li { background: #f0f0f0; border-radius: 10px; padding: 10px; margin-bottom: 8px; color: var(--text-dark); }
.badge-unlocked { background: linear-gradient(135deg, #FFD700, #FF8C00) !important; color: white !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Ana başlık
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🎨 Pixi & Nixi'nin Almanca Macerası</h1>
    <p class="subtitle">Çiz, Yarış, Öğren! Zamanla yarış ve en yüksek puanı topla! 🏁⚡</p>
</div>
""", unsafe_allow_html=True)

# Kelime veri seti (Genişletildi ve Zorluk seviyesi kaldırıldı)
WORD_DATA = [
    {"de": "der Hund", "en": "dog", "topic": "🐕 Hayvanlar", "meaning": "Köpek - İnsanın en sadık dostu"},
    {"de": "die Katze", "en": "cat", "topic": "🐕 Hayvanlar", "meaning": "Kedi - Miyav miyav yapan sevimli hayvan"},
    {"de": "der Vogel", "en": "bird", "topic": "🐕 Hayvanlar", "meaning": "Kuş - Gökyüzünde uçan kanatlı hayvan"},
    {"de": "der Fisch", "en": "fish", "topic": "🐕 Hayvanlar", "meaning": "Balık - Suda yaşayan hayvan"},
    {"de": "das Pferd", "en": "horse", "topic": "🐕 Hayvanlar", "meaning": "At - Çiftlikte yaşayan büyük ve güçlü hayvan"},
    {"de": "die Maus", "en": "mouse", "topic": "🐕 Hayvanlar", "meaning": "Fare - Küçük bir kemirgen hayvan"},
    {"de": "der Löwe", "en": "lion", "topic": "🐕 Hayvanlar", "meaning": "Aslan - Ormanların kralı"},
    {"de": "der Elefant", "en": "elephant", "topic": "🐕 Hayvanlar", "meaning": "Fil - Gri renkli, büyük kulaklı ve uzun hortumlu hayvan"},
    {"de": "der Apfel", "en": "apple", "topic": "🍎 Meyveler", "meaning": "Elma - Kırmızı veya yeşil yuvarlak meyve"},
    {"de": "die Banane", "en": "banana", "topic": "🍎 Meyveler", "meaning": "Muz - Sarı renkli uzun ve kavisli meyve"},
    {"de": "die Birne", "en": "pear", "topic": "🍎 Meyveler", "meaning": "Armut - Tatlı, sulu ve yeşil veya sarı meyve"},
    {"de": "die Traube", "en": "grape", "topic": "🍎 Meyveler", "meaning": "Üzüm - Salkımlar halinde yetişen küçük meyve"},
    {"de": "die Zitrone", "en": "lemon", "topic": "🍎 Meyveler", "meaning": "Limon - Sarı ve ekşi bir narenciye"},
    {"de": "die Erdbeere", "en": "strawberry", "topic": "🍎 Meyveler", "meaning": "Çilek - Kırmızı ve lezzetli bir meyve"},
    {"de": "die Kirsche", "en": "cherry", "topic": "🍎 Meyveler", "meaning": "Kiraz - Küçük, yuvarlak ve kırmızı meyve"},
    {"de": "das Haus", "en": "house", "topic": "🏠 Ev", "meaning": "Ev - İçinde yaşadığımız yapı"},
    {"de": "der Stuhl", "en": "chair", "topic": "🏠 Ev", "meaning": "Sandalye - Üzerinde oturduğumuz eşya"},
    {"de": "der Tisch", "en": "table", "topic": "🏠 Ev", "meaning": "Masa - Üzerinde yemek yediğimiz eşya"},
    {"de": "das Bett", "en": "bed", "topic": "🏠 Ev", "meaning": "Yatak - İçinde uyuduğumuz eşya"},
    {"de": "das Fenster", "en": "window", "topic": "🏠 Ev", "meaning": "Pencere - Dışarıyı görmek için evde bulunan cam açıklık"},
    {"de": "die Tür", "en": "door", "topic": "🏠 Ev", "meaning": "Kapı - Bir odaya giriş veya çıkış noktası"},
    {"de": "der Schrank", "en": "wardrobe", "topic": "🏠 Ev", "meaning": "Dolap - Kıyafetlerimizi koyduğumuz mobilya"},
    {"de": "die Sonne", "en": "sun", "topic": "🌞 Doğa", "meaning": "Güneş - Gündüz parlayan ışık kaynağı"},
    {"de": "der Mond", "en": "moon", "topic": "🌞 Doğa", "meaning": "Ay - Gecenin ışığı, yuvarlak gök cismi"},
    {"de": "der Baum", "en": "tree", "topic": "🌞 Doğa", "meaning": "Ağaç - Yeşil yapraklı büyük bitki"},
    {"de": "der Berg", "en": "mountain", "topic": "🌞 Doğa", "meaning": "Dağ - Yüksek ve sivri yer şekli"},
    {"de": "der Fluss", "en": "river", "topic": "🌞 Doğa", "meaning": "Nehir - Akar su kütlesi"},
    {"de": "die Blume", "en": "flower", "topic": "🌞 Doğa", "meaning": "Çiçek - Kokulu ve renkli bitki"},
    {"de": "das Auto", "en": "car", "topic": "🚗 Ulaşım", "meaning": "Araba - Dört tekerlekli taşıt"},
    {"de": "das Fahrrad", "en": "bicycle", "topic": "🚗 Ulaşım", "meaning": "Bisiklet - Pedal çevirerek gittiğimiz taşıt"},
    {"de": "der Bus", "en": "bus", "topic": "🚗 Ulaşım", "meaning": "Otobüs - Çok sayıda insan taşıyan büyük araç"},
    {"de": "das Schiff", "en": "ship", "topic": "🚗 Ulaşım", "meaning": "Gemi - Suda giden büyük araç"},
    {"de": "das Flugzeug", "en": "airplane", "topic": "🚗 Ulaşım", "meaning": "Uçak - Havada uçan taşıt"},
    {"de": "der Zug", "en": "train", "topic": "🚗 Ulaşım", "meaning": "Tren - Raylarda giden taşıt"},
    {"de": "das Brot", "en": "bread", "topic": "🍞 Yiyecekler", "meaning": "Ekmek - Un ve sudan yapılan temel yiyecek"},
    {"de": "die Milch", "en": "milk", "topic": "🍞 Yiyecekler", "meaning": "Süt - İnek gibi hayvanlardan elde edilen beyaz içecek"},
    {"de": "das Wasser", "en": "water", "topic": "🍞 Yiyecekler", "meaning": "Su - İçtiğimiz renksiz ve kokusuz sıvı"},
    {"de": "das Ei", "en": "egg", "topic": "🍞 Yiyecekler", "meaning": "Yumurta - Tavuktan elde edilen besin"},
    {"de": "der Käse", "en": "cheese", "topic": "🍞 Yiyecekler", "meaning": "Peynir - Sütten yapılan katı yiyecek"},
    {"de": "der Löffel", "en": "spoon", "topic": "🍽️ Mutfak", "meaning": "Kaşık - Çorba gibi sıvıları yemek için kullanılan gereç"},
    {"de": "die Gabel", "en": "fork", "topic": "🍽️ Mutfak", "meaning": "Çatal - Yiyecekleri batırmak için kullanılan gereç"},
    {"de": "das Messer", "en": "knife", "topic": "🍽️ Mutfak", "meaning": "Bıçak - Kesmek için kullanılan gereç"},
    {"de": "der Teller", "en": "plate", "topic": "🍽️ Mutfak", "meaning": "Tabak - Yiyecekleri koymak için kullanılan düz gereç"},
    {"de": "der Kopf", "en": "head", "topic": "🧍 Vücut", "meaning": "Kafa - Vücudun en üst kısmı"},
    {"de": "das Auge", "en": "eye", "topic": "🧍 Vücut", "meaning": "Göz - Görmeye yarayan organ"},
    {"de": "die Hand", "en": "hand", "topic": "🧍 Vücut", "meaning": "El - Parmakları olan ve nesneleri tutmaya yarayan organ"},
    {"de": "der Fuß", "en": "foot", "topic": "🧍 Vücut", "meaning": "Ayak - Vücudu taşıyan ve yürümemize yarayan alt kısım"},
    {"de": "der Arm", "en": "arm", "topic": "🧍 Vücut", "meaning": "Kol - Omuzdan ele kadar olan uzuv"},
    {"de": "das Bein", "en": "leg", "topic": "🧍 Vücut", "meaning": "Bacak - Kalçadan ayağa kadar olan uzuv"},
    {"de": "die Stadt", "en": "city", "topic": "🏙️ Şehir", "meaning": "Şehir - Çok sayıda insanın yaşadığı yerleşim yeri"},
    {"de": "die Straße", "en": "street", "topic": "🏙️ Şehir", "meaning": "Cadde - Şehirde araçların ve insanların geçtiği yol"},
    {"de": "der Park", "en": "park", "topic": "🏙️ Şehir", "meaning": "Park - Dinlenmek için kullanılan yeşil alan"},
    {"de": "das Kino", "en": "cinema", "topic": "🏙️ Şehir", "meaning": "Sinema - Film izlenen yer"},
    {"de": "der Bahnhof", "en": "train station", "topic": "🏙️ Şehir", "meaning": "Tren istasyonu - Trenlerin durduğu yer"}
]

EMOJIS = {
    'medal': '🎖️', 'art': '🎨', 'star': '🌟', 'book': '📚', 'fire': '🔥'
}

# Rozet sistemi (Yeni rozet eklendi)
BADGES = {
    "speed_demon": {"name": f"{EMOJIS['medal']} Hızlı Çizer", "desc": "3 kez 20 saniyeden fazla süre bırak", "condition": "speed_achievements", "target": 3},
    "artist": {"name": f"{EMOJIS['art']} Sanatçı", "desc": "5 kez üst üste ilk tahminde doğru", "condition": "consecutive_firsts", "target": 5},
    "perfectionist": {"name": f"{EMOJIS['star']} Mükemmeliyetçi", "desc": "10 kez ilk tahminde doğru", "condition": "total_firsts", "target": 10},
    "word_master": {"name": f"{EMOJIS['book']} Kelime Ustası", "desc": "20 farklı kelime çiz", "condition": "unique_words", "target": 20},
    "streak_master": {"name": f"{EMOJIS['fire']} Seri Usta", "desc": "7 kez üst üste doğru tahmin ettir", "condition": "win_streak", "target": 7},
}

# Mock AI tahmin fonksiyonu
def mock_ai_prediction(target_word_en, canvas_data):
    if canvas_data is None or canvas_data.sum() == 0:
        return []
    
    all_words_en = [w["en"] for w in WORD_DATA]
    other_words = [w for w in all_words_en if w != target_word_en]
    random.shuffle(other_words)
    
    predictions = []
    pixel_density = canvas_data[:, :, 3].sum() / (canvas_data.shape[0] * canvas_data.shape[1] * 255)
    
    correct_chance = 0.3 + (pixel_density * 3)
    
    if random.random() < correct_chance:
        predictions.append((target_word_en, random.uniform(0.7, 0.95)))
        predictions.extend([(w, random.uniform(0.1, 0.5)) for w in other_words[:2]])
    else:
        predictions.extend([(w, random.uniform(0.1, 0.6)) for w in other_words[:3]])
    
    return sorted(predictions, key=lambda x: x[1], reverse=True)[:3]

# Oyun durumu başlatma (Yeni durumlar eklendi)
def initialize_session_state():
    defaults = {
        'game_started': False, 'intro_shown': False, 'current_topic': "🐕 Hayvanlar",
        'current_round': 0, 'total_score': 0, 'stars_earned': 0, 'current_words': [],
        'last_predictions': [], 'show_celebration': False, 'rounds_per_game': 5,
        'show_rules': False, 'timer_started': False, 'start_time': None, 'time_left': 25,
        'game_time': 25, 'show_word_meaning': False, 'consecutive_firsts': 0,
        'total_firsts': 0, 'speed_achievements': 0, 'drawn_words': set(),
        'win_streak': 0, 'canvas_clear_trigger': 0
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="game-card">
        <div class="pixi-character">🤖</div>
        <div class="nixi-character">🧠</div>
        <h3 style="text-align: center; color: var(--primary-blue);">Pixi & Nixi Kontrol Paneli</h3>
    </div>
    """, unsafe_allow_html=True)
    
    topics = sorted(list(set([w["topic"] for w in WORD_DATA])))
    selected_topic = st.selectbox("🎯 Konu Seç:", topics, index=topics.index(st.session_state.current_topic))
    rounds = st.slider("🎲 Kaç Tur Oynayalım?", 3, 10, 5)
    game_time = st.slider("⏰ Çizim Süresi (saniye)", 15, 30, 25)
    
    if st.button("🎮 Yeni Macera Başlat!", key="new_game"):
        st.session_state.rounds_per_game = rounds
        st.session_state.game_time = game_time
        st.session_state.current_topic = selected_topic
        topic_words = [w for w in WORD_DATA if w["topic"] == selected_topic]
        
        if len(topic_words) >= rounds:
            st.session_state.current_words = random.sample(topic_words, rounds)
            st.session_state.game_started = True
            st.session_state.intro_shown = False
            st.session_state.current_round = 0
            st.session_state.total_score = 0
            st.session_state.stars_earned = 0
            st.session_state.last_predictions = []
            st.session_state.show_rules = False
            st.session_state.timer_started = False
            st.session_state.time_left = game_time
            st.session_state.show_word_meaning = False
            st.session_state.consecutive_firsts = 0
            st.session_state.total_firsts = 0
            st.session_state.speed_achievements = 0
            st.session_state.drawn_words = set()
            st.session_state.win_streak = 0
            st.session_state.canvas_clear_trigger = 0
        else:
            st.error("Bu konuda yeterli kelime yok! Lütfen tur sayısını azaltın.")

    if st.button("📖 Oyun Kuralları", key="show_rules_btn"):
        st.session_state.show_rules = not st.session_state.show_rules
    
    stars_display = '⭐' * st.session_state.stars_earned if st.session_state.stars_earned > 0 else '☆☆☆☆☆'
    st.markdown(f"""
    <div class="score-panel">
        <h3>📊 Skor Tablosu</h3>
        <div class="score-value">{st.session_state.total_score}</div>
        <div class="stars-display">{stars_display}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='badges-panel'>", unsafe_allow_html=True)
    st.markdown("<h4>🏆 Özel Rozetler</h4>", unsafe_allow_html=True)
    st.markdown("<ul>", unsafe_allow_html=True)
    for key, badge in BADGES.items():
        is_unlocked = st.session_state.get(badge['condition'], 0) >= badge['target']
        class_name = "badge-unlocked" if is_unlocked else ""
        st.markdown(f'<li class="{class_name}"><strong>{badge["name"]}:</strong> {badge["desc"]}</li>', unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# Oyun kuralları
if st.session_state.show_rules:
    st.markdown("""
    <div class="rules-panel">
        <h2 class="rules-title">📖 Oyun Kuralları ve Puanlama</h2>
        <div class="rule-item"><h4>🎯 Nasıl Oynanır?</h4><p><strong>Nixi</strong> sana Almanca bir kelime verir. Sen o kelimeyi çizersin. <strong>Pixi</strong> 3 tahmin yapar. Hem doğru tahmin hem de kalan süreye göre puan kazanırsın!</p></div>
        <div class="rule-item"><h4>⭐ Puanlama Sistemi</h4><p><strong>Puan = Kalan Süre × Tahmin Çarpanı</strong></p>
        <ul><li><strong>🥇 1. tahminde doğru:</strong> × 20 çarpan + 3 yıldız</li><li><strong>🥈 2. tahminde doğru:</strong> × 10 çarpan + 2 yıldız</li><li><strong>🥉 3. tahminde doğru:</strong> × 5 çarpan + 1 yıldız</li><li><strong>❌ Bulamazsa:</strong> Kalan süre kadar puan</li></ul></div>
    </div>
    """, unsafe_allow_html=True)

# Nixi tanıtımı
elif st.session_state.game_started and not st.session_state.intro_shown:
    st.markdown("""
    <div class="nixi-intro">
        <div class="nixi-character">🧠</div><h2>Merhaba! Ben Nixi, bu maceranın erkek robotu 🧠✨</h2>
        <div class="intro-text"><p>Ben sana Almanca bir kelime vereceğim ve sen onu çizeceksin. Ne kadar hızlı ve net çizersen, dişi robot arkadaşım <span style="font-weight: bold; color: yellow;">Pixi 🤖</span> o kadar doğru tahmin eder!</p></div>
        <div class="intro-text"><p>Haydi, fırçanı kap ve çizmeye başla!</p></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Hadi Başlayalım!", key="start_intro"):
        st.session_state.intro_shown = True

# Ana oyun alanı
elif st.session_state.game_started and st.session_state.intro_shown:
    col1, col2 = st.columns([2, 1])

    with col1:
        # Oyun Bitti Ekranı
        if st.session_state.current_round >= len(st.session_state.current_words):
            st.markdown(f"""
            <div class="game-card">
                <div class="celebration">🎉🏆🎉</div>
                <h2 style="text-align: center; color: var(--success-color);">Tebrikler! Macera Tamamlandı!</h2>
                <div style="text-align: center; margin: 20px 0;">
                    <div class="score-value" style="color: var(--primary-blue);">{st.session_state.total_score} Puan</div>
                    <div class="stars-display">{stars_display}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Tekrar Oyna!", key="play_again"):
                st.session_state.game_started = False
                st.session_state.intro_shown = False
        
        # Oyun Devam Ediyor
        else:
            current_word = st.session_state.current_words[st.session_state.current_round]
            progress = ((st.session_state.current_round + 1) / len(st.session_state.current_words)) * 100
            st.markdown(f"""
            <div class="level-indicator">Tur: {st.session_state.current_round + 1} / {len(st.session_state.current_words)}
                <div class="progress-bar"><div class="progress-fill" style="width: {progress}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.timer_started:
                elapsed = time.time() - st.session_state.start_time
                st.session_state.time_left = max(0, st.session_state.game_time - elapsed)
                if st.session_state.time_left == 0:
                    st.session_state.timer_started = False
                st.markdown(f'<div class="timer-display"><div class="timer-value">⏰ {int(st.session_state.time_left)} saniye</div></div>', unsafe_allow_html=True)
            
            st.markdown(f"<div class='word-display'><div class='german-word'>{current_word['de']}</div><div class='topic-badge'>{current_word['topic']}</div></div>", unsafe_allow_html=True)
            
            if st.button("❓ Anlamı Göster", key="help_button"):
                st.session_state.show_word_meaning = not st.session_state.show_word_meaning

            if st.session_state.show_word_meaning:
                st.info(f"💡 **{current_word['de']}** = {current_word['meaning']}")
            
            st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
            canvas_result = st_canvas(
                stroke_width=st.slider("🖌️ Fırça Kalınlığı", 5, 50, 20),
                stroke_color=st.color_picker("🎨 Fırça Rengi", "#000000"),
                background_color="#FFFFFF",
                width=600, height=400, drawing_mode="freedraw",
                key=f"canvas_{st.session_state.current_round}_{st.session_state.canvas_clear_trigger}"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            btn_cols = st.columns(4)
            with btn_cols[0]:
                if st.button("🎯 Tahmin!", key="predict"):
                    if canvas_result.image_data is not None:
                        st.session_state.timer_started = False
                        st.session_state.drawn_words.add(current_word["en"])
                        
                        # Hızlı Çizer rozeti için kontrol
                        if st.session_state.time_left >= 20:
                             st.session_state.speed_achievements += 1

                        with st.spinner("🤖 Pixi düşünüyor..."):
                            time.sleep(1)
                            predictions = mock_ai_prediction(current_word["en"], canvas_result.image_data)
                            st.session_state.last_predictions = predictions
                            
                            correct_position = next((i for i, (p, _) in enumerate(predictions) if p == current_word["en"]), None)
                            
                            if correct_position is not None:
                                multipliers = {0: 20, 1: 10, 2: 5}
                                stars = {0: 3, 1: 2, 2: 1}
                                points = int(st.session_state.time_left) * multipliers[correct_position]
                                st.session_state.total_score += points
                                st.session_state.stars_earned += stars[correct_position]
                                st.success(f"Harika! {correct_position+1}. tahminde doğru! +{points} Puan, +{stars[correct_position]} Yıldız!")
                                st.balloons()
                                st.session_state.win_streak += 1
                                if correct_position == 0:
                                    st.session_state.consecutive_firsts += 1
                                    st.session_state.total_firsts += 1
                                else:
                                    st.session_state.consecutive_firsts = 0
                            else:
                                points = int(st.session_state.time_left)
                                st.session_state.total_score += points
                                st.warning(f"Bu sefer olmadı ama {points} puan kazandın! Doğrusu: **{current_word['de']}**")
                                st.session_state.consecutive_firsts = 0
                                st.session_state.win_streak = 0
            
            with btn_cols[1]:
                if not st.session_state.timer_started and st.session_state.time_left > 0:
                    if st.button("▶️ Başla", key="start_timer"):
                        st.session_state.timer_started = True
                        st.session_state.start_time = time.time()
                elif st.session_state.timer_started:
                    if st.button("⏸️ Durdur", key="pause_timer"):
                        st.session_state.timer_started = False
            
            with btn_cols[2]:
                if st.button("⏭️ Sonraki", key="next_round"):
                    st.session_state.current_round += 1
                    st.session_state.last_predictions = []
                    st.session_state.timer_started = False
                    st.session_state.time_left = st.session_state.game_time
                    st.session_state.show_word_meaning = False
            
            with btn_cols[3]:
                if st.button("🧽 Silgi", key="eraser"):
                    st.session_state.canvas_clear_trigger += 1

    with col2:
        st.markdown("""
        <div class="game-card">
            <div class="nixi-character">🧠</div><div class="pixi-character">🤖</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.last_predictions:
            st.markdown('<div class="prediction-panel"><h4 style="text-align: center; color: var(--text-dark);">Pixi\'nin Tahminleri</h4>', unsafe_allow_html=True)
            target_en = st.session_state.current_words[st.session_state.current_round]["en"]
            for i, (word, conf) in enumerate(st.session_state.last_predictions):
                is_correct = word == target_en
                css_class = "prediction-correct" if is_correct else "prediction-wrong"
                icon = "🎯" if is_correct else f"{i+1}️⃣"
                st.markdown(f'<div class="prediction-item {css_class}"><span>{icon} {word.title()}</span><span>{int(conf*100)}%</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.current_round > 0:
            avg_score = st.session_state.total_score / (st.session_state.current_round)
            avg_score_html = f"<span style='font-size: 1.3rem; color: var(--primary-green); font-weight: bold;'>{avg_score:.0f}</span>"
            st.markdown(f"""
            <div class="game-card">
                <h4 style="text-align: center;">İstatistikler</h4>
                <div style="text-align: center;"><span class="stats-text">Ort. Puan:</span><br>{avg_score_html}</div>
            </div>
            """, unsafe_allow_html=True)

# Giriş ekranı
else:
    st.markdown("""
    <div class="game-card">
        <div class="pixi-character">🤖</div><div class="nixi-character">🧠</div>
        <h2 style="text-align: center;">Merhaba! Biz Pixi & Nixi!</h2>
        <p style="text-align: center;">Seninle hızlı çizim yarışı yaparak Almanca kelimeler öğrenmek için buradayız! Soldaki menüden ayarlarını yap ve maceraya başla!</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('<p style="text-align: center;">Pixi & Nixi ile birlikte hızlı öğrenme macerası!</p>', unsafe_allow_html=True)