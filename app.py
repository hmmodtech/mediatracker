import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# إعدادات الصفحة
st.set_page_config(page_title="ACF Media Tracker", layout="wide", initial_sidebar_state="collapsed")

# --- تنسيق CSS لمحاكاة الصورة المطلوبة بدقة ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #ffffff; }
    
    .main-title {
        text-align: center;
        color: #555;
        font-size: 4rem;
        font-weight: bold;
        margin: 0;
        line-height: 1;
    }

    .news-card {
        background: white;
        padding: 30px;
        border-radius: 10px;
        border-left: 15px solid #005691;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
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
        color: #222;
    }
    
    .time-tag {
        color: #aaa;
        font-size: 0.95rem;
        text-align: right;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- الهيدر (استخدام روابط مباشرة ومجربة) ---
col_left, col_mid, col_right = st.columns([1, 2, 1])

with col_left:
    # شعار الرمز (رابط مباشر ومستقر جداً من ويكيبيديا PNG)
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Action_Against_Hunger_logo.svg/512px-Action_Against_Hunger_logo.svg.png", width=220)

with col_mid:
    st.markdown("<h1 class='main-title'>Media Tracker</h1>", unsafe_allow_html=True)
    pal_time = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d | %I:%M %p")
    st.markdown(f"<p style='text-align:center; color:#666; font-size:1.3rem; margin-top:15px;'>Palestine Time: {pal_time}</p>", unsafe_allow_html=True)

with col_right:
    # شعار النص الكامل (Action Against Hunger)
    st.image("https://www.actionagainsthunger.org.uk/wp-content/themes/action-against-hunger/assets/img/logo-acf.svg", width=300)

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.title("Control Panel")
    sound_on = st.toggle("Audio Notifications", value=True)
    search_query = st.text_input("Filter News (Keyword):", "")
    st.divider()
    st.info("System updates every 30 seconds.")

# --- محرك جلب البيانات ---
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
                    # تم إصلاح القوس المفقود هنا أيضاً لضمان الاستقرار
                    results.append({"ch": ch, "txt": t, "tm": (datetime.utcnow() + timedelta(hours=3)).strftime("%I:%M %p")})
                    seen.add(t[:50])
        except: continue
    return results[::-1]

data = fetch_data()
if search_query:
    data = [d for d in data if search_query in d['txt']]

# نظام الصوت (Session State)
if 'p_count' not in st.session_state: st.session_state.p_count = 0
if sound_on and len(data) > st.session_state.p_count:
    st.markdown('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"></audio>', unsafe_allow_html=True)
st.session_state.p_count = len(data)

st.divider()

# --- العرض الإخباري ---
if not data:
    st.warning("Scanning channels... No new updates.")
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
