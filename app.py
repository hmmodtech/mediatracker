import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# إعداد الصفحة بنمط عريض
st.set_page_config(page_title="ACF Media Tracker", layout="wide")

# --- تنسيق CSS بسيط ونظيف ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    .news-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-right: 6px solid #005691;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .source-tag { color: #005691; font-weight: bold; font-size: 1.2rem; }
    .time-tag { color: #888; font-size: 0.8rem; float: left; }
    h1 { color: #005691; text-align: center; border-bottom: 2px solid #97be2f; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- العنوان والوقت ---
st.markdown("<h1>ACF Media Tracker</h1>", unsafe_allow_html=True)
pal_time = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d | %I:%M %p")
st.write(f"<p style='text-align:center;'>📡 رصد ميداني مباشر | <b>توقيت فلسطين: {pal_time}</b></p>", unsafe_allow_html=True)

# --- الإعدادات الجانبية ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    sound = st.checkbox("🔔 تفعيل صوت التنبيه", value=True)
    search = st.text_input("🔍 بحث سريع في النتائج:", "")

# --- محرك القنوات ---
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

# جلب البيانات وتطبيق البحث
data = fetch_data()
if search:
    data = [d for d in data if search in d['txt']]

# نظام الصوت عند وصول خبر جديد
if 'count' not in st.session_state: st.session_state.count = 0
if sound and len(data) > st.session_state.count:
    st.markdown('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"></audio>', unsafe_allow_html=True)
st.session_state.count = len(data)

st.divider()

# --- عرض الأخبار ---
for item in data:
    st.markdown(f"""
        <div class="news-card">
            <span class="time-tag">{item['tm']}</span>
            <span class="source-tag">@{item['ch']}</span>
            <p style="margin-top:10px;">{item['txt']}</p>
        </div>
        """, unsafe_allow_html=True)

# تحديث تلقائي كل 30 ثانية
time.sleep(30)
st.rerun()
