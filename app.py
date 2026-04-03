import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# إعدادات الصفحة
st.set_page_config(page_title="ACF Media Tracker", layout="wide", initial_sidebar_state="collapsed")

# --- تنسيق CSS لمحاكاة الصورة تماماً وإصلاح الخطوط ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #ffffff; }
    
    .main-title {
        text-align: center;
        color: #555;
        font-size: 3.5rem;
        font-weight: bold;
        margin: 0;
        padding: 0;
    }

    .news-card {
        background: white;
        padding: 35px;
        border-radius: 10px;
        border-left: 12px solid #005691;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .source-tag {
        color: #005691;
        font-weight: bold;
        font-size: 1.5rem;
        margin-bottom: 15px;
        text-align: left;
    }
    
    .news-text {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
        font-size: 1.3rem;
        line-height: 1.8;
        color: #222;
    }
    
    .time-tag {
        color: #aaa;
        font-size: 0.9rem;
        text-align: right;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- الهيدر (استخدام روابط صور بديلة ومستقرة) ---
col_left, col_mid, col_right = st.columns([1, 2, 1])

with col_left:
    # شعار الرمز (رابط PNG بديل ومستقر)
    st.image("https://i.ibb.co/pLg4b4v/ACF-Logo-Tracker.png", width=250)

with col_mid:
    st.markdown("<h1 class='main-title'>Media Tracker</h1>", unsafe_allow_html=True)
    pal_time = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d | %I:%M %p")
    st.markdown(f"<p style='text-align:center; color:#666; font-size:1.2rem; margin-top:10px;'>Palestine Time: {pal_time}</p>", unsafe_allow_html=True)

with col_right:
    # شعار النص (رابط PNG بديل ومستقر)
    st.image("https://i.ibb.co/m0fHHRz/ACF-Full-Logo.png", width=300)

# --- القائمة الجانبية ---
with st.sidebar:
    st.title("Control Panel")
    sound_on = st.toggle("Audio Notifications", value=True)
    search_q = st.text_input("Filter News (Keyword):", "")
    st.divider()
    st.info("System updates every 30 seconds.")

# --- محرك الجلب ---
CHANNELS = ["mumenjmmeqdad", "hanialshaer", "asmailpress", "rafa0", "hamza20300", "Nuseirat1", "QudsN", "ShehabTelegram", "PalinfoAr", "almayadeen", "hpress", "gazaalanar", "alhodhud", "EabriLive", "nailkhn"]
KEYWORDS = ["غزة", "رفح", "خانيونس", "جباليا", "الشمال", "الوسطى", "النصيرات", "قصف", "غارة", "استهداف", "شهيد", "اصابة", "اشتباكات", "توغل", "آليات", "كواد كابتر", "طيران", "مدفعي", "نزوح", "مجزرة", "عاجل", "المستشفى", "الاحتلال", "المقاومة", "صواريخ", "صافرات الإنذار", "معبر", "معابر", "كرم ابو سالم", "بوابة", "تنسيقات", "سفر", "كشف مسافرين"]

def get_live_data():
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
                    results.append({"ch": ch, "txt": t, "tm": (
