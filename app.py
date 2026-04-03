import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# Page Config - English Layout (Left-to-Right)
st.set_page_config(page_title="ACF Media Tracker", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Professional English Layout ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Cairo:wght@400;700&display=swap');
    
    /* English UI Fonts */
    .main, .sidebar-content, h1, h2, h3 { font-family: 'Inter', sans-serif; }
    
    /* Arabic News Content Font */
    .news-text { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; font-size: 1.1rem; line-height: 1.6; }
    
    .news-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #005691; /* Border on the left for English UI */
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .source-tag { color: #005691; font-weight: bold; font-size: 1.1rem; text-align: left; }
    .time-tag { color: #888; font-size: 0.85rem; text-align: right; }
    
    /* Header Styling */
    .header-container { display: flex; align-items: center; gap: 20px; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- Header Section ---
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Action_Against_Hunger_logo.svg/1200px-Action_Against_Hunger_logo.svg.png", width=180)
with col2:
    st.markdown("<h1 style='color:#005691; margin-bottom:0;'>ACF Media Tracker</h1>", unsafe_allow_html=True)
    pal_time = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d | %I:%M %p")
    st.write(f"📡 Live Field Monitoring | **Palestine Time: {pal_time}**")

# --- Sidebar (English UI) ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.write("Manage your tracking preferences here.")
    sound_option = st.radio("Notification Sound:", ["Enabled", "Disabled"], index=0)
    search_query = st.text_input("🔍 Quick Search:", placeholder="Search keywords...")
    st.divider()
    st.info("The tracker auto-refreshes every 30 seconds.")

# --- News Fetching Engine ---
CHANNELS = ["mumenjmmeqdad", "hanialshaer", "asmailpress", "rafa0", "hamza20300", "Nuseirat1", "QudsN", "ShehabTelegram", "PalinfoAr", "almayadeen", "hpress", "gazaalanar", "alhodhud", "EabriLive", "nailkhn"]
KEYWORDS = ["غزة", "رفح", "خانيونس", "جباليا", "الشمال", "الوسطى", "النصيرات", "قصف", "غارة", "استهداف", "شهيد", "اصابة", "اشتباكات", "توغل", "آليات", "كواد كابتر", "طيران", "مدفعي", "نزوح", "مجزرة", "عاجل", "المستشفى", "الاحتلال", "المقاومة", "صواريخ", "صافرات الإنذار", "معبر", "معابر", "كرم ابو سالم", "بوابة", "تنسيقات", "سفر", "كشف مسافرين"]

def fetch_data():
    results = []
    seen = set()
    for ch in CHANNELS:
        try:
            res = requests.get(f"https://t.me/s/{ch}", timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            msgs = soup.find_all('div', class_='tgme_widget_message_text')
            for m in msgs[-1:]:
                t = m.get_text().strip()
                if any(w in t for w in KEYWORDS) and t[:50] not in seen:
                    results.append({"ch": ch, "txt": t, "tm": (datetime.utcnow() + timedelta(hours=3)).strftime("%I:%M %p")})
                    seen.add(t[:50])
        except: continue
    return results[::-1]

data = fetch_data()
if search_query:
    data = [d for d in data if search_query in d['txt']]

# Audio Notification Logic
if 'last_count' not in st.session_state: st.session_state.last_count = 0
if sound_option == "Enabled" and len(data) > st.session_state.last_count:
    st.markdown('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"></audio>', unsafe_allow_html=True)
st.session_state.last_count = len(data)

st.divider()

# --- News Feed Display ---
if not data:
    st.warning("Scanning sources... No new updates at the moment.")
else:
    for item in data:
        st.markdown(f"""
            <div class="news-card">
                <div class="source-tag">@{item['ch']}</div>
                <div class="news-text">{item['txt']}</div>
                <hr style="margin: 10px 0; border: 0.5px solid #eee;">
                <div class="time-tag">Captured at: {item['tm']}</div>
            </div>
            """, unsafe_allow_html=True)

# Auto-Refresh Script
time.sleep(30)
st.rerun()
