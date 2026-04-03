import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# 1. إعداد الصفحة الأساسي
st.set_page_config(page_title="Media Tracker", layout="wide")

# 2. تنسيق CSS لمنع الصور وتعديل الخطوط (نص فقط)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* منع ظهور أي وسم صورة نهائياً */
    img, svg, [data-testid="stImage"] { display: none !important; }
    
    html, body, [class*="css"] { 
        font-family: 'Cairo', sans-serif; 
        direction: rtl; 
        text-align: right; 
    }
    
    .main-title-box {
        text-align: center;
        padding: 20px;
        border-bottom: 4px solid #97be2f;
        margin-bottom: 30px;
    }
    
    .news-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-right: 8px solid #005691;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .source-name { color: #005691; font-weight: bold; font-size: 1.3rem; }
    .time-stamp { color: #888; font-size: 0.8rem; float: left; }
    </style>
    """, unsafe_allow_html=True)

# 3. الهيدر (نص بسيط في المنتصف)
st.markdown(f"""
    <div class="main-title-box">
        <h1 style="color: #333; margin:0; font-size: 3rem;">Media Tracker</h1>
        <p style="color: #666; font-size: 1.2rem;">
            📡 رصد ميداني مباشر | توقيت فلسطين: {(datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d | %I:%M %p")}
        </p>
    </div>
    """, unsafe_allow_html=True)

# 4. محرك الأخبار
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
                    results.append({
                        "ch": ch, 
                        "txt": t, 
                        "tm": (datetime.utcnow() + timedelta(hours=3)).strftime("%I:%M %p")
                    })
                    seen.add(t[:50])
        except: continue
    return results[::-1]

# 5. عرض البيانات
data = fetch_data()

# تنبيه صوتي بسيط
if 'old_count' not in st.session_state: st.session_state.old_count = 0
if len(data) > st.session_state.old_count:
    st.markdown('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"></audio>', unsafe_allow_html=True)
st.session_state.old_count = len(data)

for item in data:
    st.markdown(f"""
        <div class="news-card">
            <span class="time-stamp">{item['tm']}</span>
            <div class="source-name">@{item['ch']}</div>
            <p style="margin-top:10px; line-height:1.6; font-size:1.1rem;">{item['txt']}</p>
        </div>
        """, unsafe_allow_html=True)

# تحديث تلقائي كل 30 ثانية
time.sleep(30)
st.rerun()
