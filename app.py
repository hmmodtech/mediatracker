import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import base64

# Page Configuration
st.set_page_config(page_title="ACF Media Tracker", layout="wide", initial_sidebar_state="collapsed")

# --- دالة لتحويل الصورة المرفوعة إلى كود Base64 لضمان ظهورها للأبد ---
def get_image_base64(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return ""

# شعارات بديلة مستقرة جداً
LOGO_ICON_URL = "https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Action_Against_Hunger_logo.svg/512px-Action_Against_Hunger_logo.svg.png"
LOGO_TEXT_URL = "https://www.actionagainsthunger.org/wp-content/themes/action-against-hunger/assets/img/logo-acf.svg"

# --- Custom CSS Matching your Request ---
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
        line-height: 1.2;
    }
    .news-card {
        background: white;
        padding: 30px;
        border-radius: 12px;
        border-left: 12px solid #005691;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .source-tag { color: #005691; font-weight: bold; font-size: 1.5rem; margin-bottom: 15px; }
    .news-text {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
        font-size: 1.3rem;
        line-height: 1.8;
        color: #222;
    }
    .time-tag { color: #aaa; font-size: 0.9rem; text-align: right; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- Header Section (Layout matching your screenshot) ---
header_col1, header_col2, header_col3 = st.columns([1, 2, 1])

with header_col1:
    # عرض الشعار الذي أرسلته (باستخدام الرابط المباشر لضمان السرعة)
    st.image(LOGO_ICON_URL, width=200)

with header_col2:
    st.markdown("<h1 class='main-title'>Media Tracker</h1>", unsafe_allow_html=True)
    pal_time = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d | %I:%M %p")
    st.markdown(f"<p style='text-align:center; color:#666; font-size:1.2rem;'>Palestine Time: {pal_time}</p>", unsafe_allow_html=True)

with header_col3:
    # عرض الشعار النصي على اليمين
    st.image(LOGO_TEXT_URL, width=280)

# --- Sidebar Controls ---
with st.sidebar:
    st.title("Control Panel")
    sound_on = st.toggle("Audio Notifications", value=True)
    search_input = st.text_input("Filter News:", placeholder="Type to search...")
    st.divider()

# --- News Scraping Engine ---
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
if search_input:
    data = [d for d in data if search_input in d['txt']]

# Audio Notification Logic
if 'p_count' not in st.session_state: st.session_state.p_count = 0
if sound_on and len(data) > st.session_state.p_count:
    st.markdown('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"></audio>', unsafe_allow_html=True)
st.session_state.p_count = len(data)

st.divider()

# --- Display News Feed ---
if not data:
    st.info("Searching for updates...")
else:
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
