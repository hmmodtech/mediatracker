import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# إعدادات الصفحة الأساسية - تعطيل القائمة الافتراضية المزعجة
st.set_page_config(page_title="ACF Media Tracker", layout="wide", initial_sidebar_state="expanded")

# --- تنسيق CSS "داخلي" لضمان عدم التعليق ---
st.markdown("""
    <style>
    /* خط بديل في حال فشل تحميل Cairo */
    * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; direction: rtl; text-align: right; }
    
    .main { background-color: #f4f7f6 !important; }
    
    /* تنسيق البطاقات */
    .news-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border-right: 6px solid #005691;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* تنسيق الهيدر لضمان ظهور العنوان والشعار */
    .header-container {
        display: flex;
        align-items: center;
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-bottom: 4px solid #97be2f;
    }
    
    .sidebar .sidebar-content { background-image: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- الهيدر (طريقة عرض مختلفة) ---
col1, col2 = st.columns([1, 3])
with col1:
    # رابط شعار بديل جداً (PNG مباشر)
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Action_Against_Hunger_logo.svg/1200px-Action_Against_Hunger_logo.svg.png", width=180)
with col2:
    st.markdown("<h1 style='color:#005691; margin:0;'>Media Tracker</h1>", unsafe_allow_html=True)
    pal_time = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d | %I:%M %p")
    st.write(f"📅 تحديث ميداني | **فلسطين: {pal_time}**")

# --- القنوات والكلمات ---
CHANNELS = ["mumenjmmeqdad", "hanialshaer", "asmailpress", "rafa0", "hamza20300", "Nuseirat1", "QudsN", "ShehabTelegram", "PalinfoAr", "almayadeen", "hpress", "gazaalanar", "alhodhud", "EabriLive", "nailkhn"]
KEYWORDS = ["غزة", "رفح", "خانيونس", "جباليا", "الشمال", "الوسطى", "النصيرات", "قصف", "غارة", "استهداف", "شهيد", "اصابة", "اشتباكات", "توغل", "آليات", "كواد كابتر", "طيران", "مدفعي", "نزوح", "مجزرة", "عاجل", "المستشفى", "الاحتلال", "المقاومة", "صواريخ", "صافرات الإنذار", "معبر", "معابر", "كرم ابو سالم", "بوابة", "تنسيقات", "سفر", "كشف مسافرين"]

def fetch_data():
    results = []
    seen = set()
    for ch in CHANNELS:
        try:
            res = requests.get(f"https://t.me/s/{ch}", timeout=15) # زيادة وقت الانتظار
            soup = BeautifulSoup(res.text, 'html.parser')
            msgs = soup.find_all('div', class_='tgme_widget_message_text')
            for m in msgs[-1:]:
                t = m.get_text().strip()
                if any(w in t for w in KEYWORDS) and t[:50] not in seen:
                    results.append({"ch": ch, "txt": t, "tm": (datetime.utcnow() + timedelta(hours=3)).strftime("%I:%M %p")})
                    seen.add(t[:50])
        except: continue
    return results[::-1]

# --- التحكم الجانبي (مبسط جداً لتفادي التعليق) ---
st.sidebar.title("⚙️ الإعدادات")
sound_check = st.sidebar.radio("التنبيه الصوتي:", ["مفعل", "معطل"], index=0)
search_input = st.sidebar.text_input("🔍 بحث عاجل:")

# جلب البيانات
data = fetch_data()
if search_input:
    data = [d for d in data if search_input in d['txt']]

# نظام الصوت (طريقة حقن مباشرة)
if 'old_len' not in st.session_state: st.session_state.old_len = 0
if sound_check == "مفعل" and len(data) > st.session_state.old_len:
    st.markdown('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"></audio>', unsafe_allow_html=True)
st.session_state.old_len = len(data)

# --- العرض الرئيسي ---
st.divider()
if not data:
    st.info("جاري فحص القنوات... لا يوجد تحديثات حالياً.")
else:
    for item in data:
        st.markdown(f"""
            <div class="news-card">
                <div style="color:#888; font-size:0.8rem; float:left;">{item['tm']}</div>
                <div style="color:#005691; font-weight:bold;">@{item['ch']}</div>
                <div style="margin-top:10px; line-height:1.6;">{item['txt']}</div>
            </div>
            """, unsafe_allow_html=True)

# تحديث كل 30 ثانية
time.sleep(30)
st.rerun()
