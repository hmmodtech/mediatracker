import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# 1. إعداد الصفحة (إلغاء الحالة الجانبية لتقليل العناصر)
st.set_page_config(page_title="Media Tracker", layout="wide")

# 2. أمر "إعدام" لأي صورة أو عمود خفي
st.markdown("""
    <style>
    /* إخفاء نهائي لأي وسم صورة في الصفحة */
    img, [data-testid="stImage"] { display: none !important; }
    
    /* توحيد الخط والاتجاه */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    /* تصميم الهيدر في المنتصف بدون أعمدة */
    .header-box {
        text-align: center;
        padding: 30px 0;
        border-bottom: 2px solid #eee;
        margin-bottom: 30px;
        width: 100%;
    }
    .main-title { color: #333; font-size: 3rem; font-weight: bold; }

    /* تصميم البطاقات */
    .news-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-right: 8px solid #005691;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .source-name { color: #005691; font-weight: bold; font-size: 1.2rem; }
    .time-stamp { color: #888; font-size: 0.8rem; float: left; }
    </style>
    """, unsafe_allow_html=True)

# 3. الهيدر (نص فقط ومستحيل يظهر بجانبه أي شيء)
st.markdown(f"""
    <div class="header-box">
        <div class="main-title">Media Tracker</div>
        <div style="color: #666;">
            📡 رصد ميداني مباشر | توقيت فلسطين: {(datetime.utcnow() + timedelta(hours=3)).strftime("%I:%M %p")}
        </div>
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
                    results.append({"ch": ch, "txt": t, "tm": (datetime.utcnow() + timedelta(hours=3)).strftime("%I:%M %p")})
                    seen.add(t[:50])
        except: continue
    return results[::-1]

# 5. العرض
data = fetch_data()
for item in data:
    st.markdown(f"""
        <div class="news-card">
            <span class="time-stamp">{item['tm']}</span>
            <div class="source-name">@{item['ch']}</div>
            <p style="margin-top:10px;">{item['txt']}</p>
        </div>
        """, unsafe_allow_html=True)

time.sleep(30)
st.rerun()
