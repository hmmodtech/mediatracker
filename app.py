import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# إعداد الصفحة
st.set_page_config(page_title="ACF Media Tracker", layout="wide", initial_sidebar_state="collapsed")

# --- التنسيق البصري الفخم ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #f8f9fa; }
    
    .header-container {
        text-align: center;
        padding: 40px 0;
        background: #ffffff;
        border-bottom: 5px solid #97be2f;
        margin-bottom: 40px;
    }

    .main-title {
        color: #005691;
        font-size: 4.2rem;
        font-weight: bold;
        margin: 0;
        letter-spacing: -1px;
    }

    .pal-time-text {
        color: #666;
        font-size: 1.3rem;
        margin-top: 10px;
    }

    .news-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        border-left: 12px solid #005691;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    .source-tag {
        color: #005691;
        font-weight: bold;
        font-size: 1.6rem;
        margin-bottom: 15px;
        text-align: left;
    }
    
    .news-text {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
        font-size: 1.4rem;
        line-height: 1.8;
        color: #111;
    }
    
    .time-tag {
        color: #aaa;
        font-size: 0.95rem;
        text-align: right;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- الهيدر (عنوان فقط بدون صور) ---
st.markdown(f"""
    <div class="header-container">
        <h1 class="main-title">Media Tracker</h1>
        <div class="pal-time-text">
            📡 Live Field Monitoring | Palestine Time: {(datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %I:%M %p")}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.title("Settings")
    sound_on = st.toggle("Audio Notifications", value=True)
    search_q = st.text_input("🔍 Filter News:", placeholder="Keywords...")
    st.divider()
    st.info("System auto-refreshes every 30 seconds.")

# --- محرك جلب الأخبار ---
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
if search_q:
    data = [d for d in data if search_q in d['txt']]

# نظام الصوت
if 'last_count' not in st.session_state: st.session_state.last_count = 0
if sound_on and len(data) > st.session_state.last_count:
    st.markdown('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"></audio>', unsafe_allow_html=True)
st.session_state.last_count = len(data)

# --- عرض التغذية الإخبارية ---
for item in data:
    st.markdown(f"""
        <div class="news-card">
            <div class="source-tag">@{item['ch']}</div>
            <div class="news-text">{item['txt']}</div>
            <div class="time-tag">Captured at: {item['tm']}</div>
        </div>
        """, unsafe_allow_html=True)

time.sleep(30)
st.rerun()
