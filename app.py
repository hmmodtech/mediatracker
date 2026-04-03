import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# إعدادات التصميم (هوية ACF الرسمية)
st.set_page_config(page_title="ACF Media Tracker", layout="wide", page_icon="📡")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main { background-color: #f8f9fa; }
    .news-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-right: 8px solid #005691;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .source-tag { color: #005691; font-weight: bold; font-size: 1.3rem; }
    .time-tag { color: #888; font-size: 0.9rem; float: left; }
    .crossing-box {
        background-color: #fff5f5;
        border: 2px solid #e03131;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 30px;
    }
    h1 { color: #005691; border-bottom: 4px solid #97be2f; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# الهيدر
# ابحث عن قسم الهيدر في كود app.py واستبدله بهذا لضمان ظهور الصورة
st.image("https://upload.wikimedia.org/wikipedia/commons/e/e0/Action_Against_Hunger_logo.svg", width=250)
st.markdown("<h1 style='margin-top:-30px;'>Media Tracker</h1>", unsafe_allow_html=True)

# القنوات
CHANNELS = ["mumenjmmeqdad", "hanialshaer", "asmailpress", "rafa0", "hamza20300", "Nuseirat1", "QudsN", "ShehabTelegram", "PalinfoAr", "almayadeen", "hpress", "gazaalanar", "alhodhud", "EabriLive", "nailkhn"]
KEYWORDS = ["غزة", "رفح", "خانيونس", "جباليا", "الشمال", "الوسطى", "النصيرات", "قصف", "غارة", "استهداف", "شهيد", "اصابة", "اشتباكات", "توغل", "آليات", "كواد كابتر", "طيران", "مدفعي", "نزوح", "مجزرة", "عاجل", "المستشفى", "الاحتلال", "المقاومة", "صواريخ", "صافرات الإنذار", "معبر", "معابر", "كرم ابو سالم", "بوابة", "تنسيقات", "سفر", "كشف مسافرين"]
CROSS_WORDS = ["معبر", "تنسيقات", "بوابة", "سفر"]

def fetch_news():
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

# التحكم الجانبي
with st.sidebar:
    st.header("⚙️ الإعدادات")
    sound = st.toggle("🔔 صوت التنبيه", value=True)
    search = st.text_input("🔍 بحث سري داخل النتائج:", "")

data = fetch_news()
if search: data = [d for d in data if search in d['txt']]

# التنبيه الصوتي
if 'count' not in st.session_state: st.session_state.count = 0
if sound and len(data) > st.session_state.count:
    st.markdown('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"></audio>', unsafe_allow_html=True)
st.session_state.count = len(data)

# عرض المعابر
crossings = [n for n in data if any(w in n['txt'] for w in CROSS_WORDS)]
if crossings:
    st.markdown('<div class="crossing-box"><h3>🚨 تنبيهات المعابر والتنسيقات</h3>', unsafe_allow_html=True)
    for c in crossings: st.error(f"**@{c['ch']}**: {c['txt']}")
    st.markdown('</div>', unsafe_allow_html=True)

# عرض الأخبار
for item in data:
    st.markdown(f"""
        <div class="news-card">
            <span class="time-tag">{item['tm']}</span>
            <span class="source-tag">@{item['ch']}</span>
            <p style="margin-top:15px; font-size:1.1rem;">{item['txt']}</p>
        </div>
        """, unsafe_allow_html=True)

time.sleep(30)
st.rerun()
