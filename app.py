import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# إعدادات الصفحة
st.set_page_config(page_title="ACF Media Tracker", layout="wide", initial_sidebar_state="collapsed")

# --- تنسيق CSS لمحاكاة الصورة تماماً ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* تنسيق الهيدر الثلاثي */
    .header-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 0;
        margin-bottom: 40px;
    }
    
    .main-title {
        text-align: center;
        color: #555;
        font-size: 3rem;
        font-weight: bold;
        margin: 0;
    }

    /* تنسيق البطاقات كما في الصورة */
    .news-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        border-left: 10px solid #005691;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    .source-tag {
        color: #005691;
        font-weight: bold;
        font-size: 1.4rem;
        margin-bottom: 15px;
        text-align: left;
    }
    
    .news-text {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: justify;
        font-size: 1.25rem;
        line-height: 1.8;
        color: #333;
    }
    
    .time-tag {
        color: #999;
        font-size: 0.9rem;
        text-align: right;
        margin-top: 15px;
    }

    hr { border: 0.5px solid #eee; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- الهيدر (توزيع الشعارات كما في الصورة) ---
col_left, col_mid, col_right = st.columns([1, 2, 1])

with col_left:
    # شعار الرمز (السنبلة والقطرة)
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Action_Against_Hunger_logo.svg/1200px-Action_Against_Hunger_logo.svg.png", width=250)

with col_mid:
    st.markdown("<h1 class='main-title'>Media Tracker</h1>", unsafe_allow_html=True)
    pal_time = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d | %I:%M %p")
    st.markdown(f"<p style='text-align:center; color:#666; font-size:1.1rem;'>Palestine Time: {pal_time}</p>", unsafe_allow_html=True)

with col_right:
    # شعار النص (Action Against Hunger)
    st.image("https://www.actionagainsthunger.org/wp-content/themes/action-against-hunger/assets/img/logo-acf.svg", width=280)

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.title("Settings")
    sound_on = st.toggle("Audio Notifications", value=True)
    search_q = st.text_input("Filter News:", placeholder="Keyword...")
    st.divider()
    st.info("System updates every 30 seconds.")

# --- محرك البحث والجلب ---
CHANNELS = ["mumenjmmeqdad", "hanialshaer", "asmailpress", "rafa0", "hamza20300", "Nuseirat1", "QudsN", "ShehabTelegram", "PalinfoAr", "almayadeen", "hpress", "gazaalanar", "alhodhud", "EabriLive", "nailkhn"]
KEYWORDS = ["غزة", "رفح", "خانيونس", "جباليا", "الشمال", "الوسطى", "النصيرات", "قصف", "غارة", "استهداف", "شهيد", "اصابة", "اشتباكات", "توغل", "آليات", "كواد كابتر", "طيران", "مدفعي", "نزوح", "مجزرة", "عاجل", "المستشفى", "الاحتلال", "المقاومة", "صواريخ", "صافرات الإنذار", "معبر", "معابر", "كرم ابو سالم", "بوابة", "تنسيقات", "سفر", "كشف مسافرين"]

def get_data():
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

data = get_data()
if search_q:
    data = [d for d in data if search_q in d['txt']]

# نظام الصوت
if 'prev_count' not in st.session_state: st.session_state.prev_count = 0
if sound_on and len(data) > st.session_state.prev_count:
    st.markdown('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"></audio>', unsafe_allow_html=True)
st.session_state.prev_count = len(data)

st.divider()

# --- عرض التغذية الإخبارية (News Feed) ---
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
