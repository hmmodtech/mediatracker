import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# إعداد الصفحة
st.set_page_config(page_title="Media Tracker", layout="wide", initial_sidebar_state="collapsed")

# --- تنسيق CSS نظيف تماماً (بدون صور) ---
st.markdown("""
    <style>
    @import url('https://github.com/hmmodtech/mediatracker/blob/main/ACF%20logo.png');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #ffffff; }
    
    /* منع أي ظهور لأيقونات الصور */
    img { display: none !important; }
    
    .header-center {
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid #eee;
        margin-bottom: 30px;
    }

    .main-title { color: #333; font-size: 3rem; font-weight: bold; margin: 0; }
    .pal-time { color: #888; font-size: 1.1rem; }

    .news-card {
        background: white;
        padding: 25px;
        border-radius: 8px;
        border-left: 10px solid #005691;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .source-tag { color: #005691; font-weight: bold; font-size: 1.4rem; margin-bottom: 8px; text-align: left; }
    .news-text { font-family: 'Cairo', sans-serif !important; direction: rtl; text-align: right; font-size: 1.3rem; line-height: 1.7; color: #222; }
    .time-tag { color: #bbb; font-size: 0.85rem; text-align: right; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- الهيدر (نص فقط في منتصف الصفحة) ---
st.markdown(f"""
    <div class="header-center">
        <div class="main-title">Media Tracker</div>
        <div class="pal-time">
            Palestine Time: {(datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d | %I:%M %p")}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    st.title("Settings")
    sound_on = st.toggle("Audio Notifications", value=True)
    search_q = st.text_input("Filter News:", "")

# --- محرك الجلب ---
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

# --- عرض التغذية ---
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
