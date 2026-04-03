import streamlit as st
import pandas as pd
from telethon import TelegramClient
from datetime import datetime
import asyncio
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium
import requests
from openai import OpenAI

# ==============================
# 🔐 Secrets
# ==============================
api_id = st.secrets["API_ID"]
api_hash = st.secrets["API_HASH"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
BOT_TOKEN = st.secrets["BOT_TOKEN"]
CHAT_ID = st.secrets["CHAT_ID"]

# ==============================
# Telegram channels
# ==============================
channels = ["QudsN", "ShehabTelegram", "PalinfoAr"]

KEYWORDS = ["قصف", "غارة", "استهداف", "شهيد", "اصابة", "نزوح", "معبر", "تنسيقات", "اشتباكات"]
CRITICAL_KEYWORDS = ["قصف", "غارة", "استهداف", "معبر"]

PLACES = ["غزة", "رفح", "خانيونس", "جباليا", "النصيرات", "دير البلح"]

# ==============================
# تصنيف
# ==============================
def classify(text):
    if any(w in text for w in ["قصف", "غارة", "استهداف"]):
        return "🔴 عسكري"
    elif any(w in text for w in ["نزوح", "اصابة", "شهيد"]):
        return "🟡 إنساني"
    elif any(w in text for w in ["معبر", "تنسيقات"]):
        return "🚨 معابر"
    return "⚪ أخرى"

# ==============================
# استخراج موقع
# ==============================
def extract_location(text):
    for p in PLACES:
        if p in text:
            return p
    return None

# ==============================
# Geolocation
# ==============================
geolocator = Nominatim(user_agent="acf_tracker")

def get_location(place):
    try:
        loc = geolocator.geocode(place)
        if loc:
            return (loc.latitude, loc.longitude)
    except:
        return None

# ==============================
# Telegram Fetch
# ==============================
async def fetch_messages():
    client = TelegramClient("session", api_id, api_hash)
    await client.start()

    data = []
    seen = set()

    for ch in channels:
        try:
            async for msg in client.iter_messages(ch, limit=20):
                if msg.text and any(k in msg.text for k in KEYWORDS):
                    h = hash(msg.text)
                    if h not in seen:
                        seen.add(h)
                        data.append({
                            "channel": ch,
                            "text": msg.text,
                            "time": msg.date,
                            "category": classify(msg.text)
                        })
        except:
            continue

    await client.disconnect()
    return data

# ==============================
# Cache
# ==============================
@st.cache_data(ttl=60)
def get_data():
    return asyncio.run(fetch_messages())

# ==============================
# AI
# ==============================
client_ai = OpenAI(api_key=OPENAI_API_KEY)

def summarize_news(texts):
    combined = "\n".join(texts[:20])
    response = client_ai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "أنت محلل أمني مختص في غزة"},
            {"role": "user", "content": f"لخص هذه الأخبار:\n{combined}"}
        ]
    )
    return response.choices[0].message.content

# ==============================
# Telegram Alert
# ==============================
def send_alert(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ==============================
# UI
# ==============================
st.set_page_config(page_title="ACF Pro Tracker", layout="wide")

st.title("📡 ACF Pro Media Tracker")

# حماية
password = st.text_input("Enter Password", type="password")
if password != "ACF2026":
    st.stop()

# تحميل البيانات
try:
    data = get_data()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

if not data:
    st.warning("لا توجد بيانات")
    st.stop()

df = pd.DataFrame(data)

# ==============================
# Dashboard
# ==============================
col1, col2, col3 = st.columns(3)
col1.metric("📊 الأخبار", len(df))
col2.metric("🔴 عسكري", len(df[df["category"] == "🔴 عسكري"]))
col3.metric("🚨 معابر", len(df[df["category"] == "🚨 معابر"]))

# ==============================
# Alerts
# ==============================
for _, row in df.iterrows():
    if any(k in row["text"] for k in CRITICAL_KEYWORDS):
        st.error(f"🚨 {row['text']}")
        send_alert(row["text"])

# ==============================
# Map
# ==============================
st.subheader("🗺️ الخريطة")

m = folium.Map(location=[31.4, 34.3], zoom_start=9)

for _, row in df.iterrows():
    place = extract_location(row["text"])
    if place:
        coords = get_location(place)
        if coords:
            folium.Marker(
                location=coords,
                popup=row["text"],
                tooltip=row["category"]
            ).add_to(m)

st_folium(m, width=700, height=500)

# ==============================
# AI Summary
# ==============================
st.subheader("🧠 التحليل الذكي")
summary = summarize_news(df["text"].tolist())
st.info(summary)

# ==============================
# Filter
# ==============================
category = st.selectbox("التصنيف", ["الكل"] + list(df["category"].unique()))

if category != "الكل":
    df = df[df["category"] == category]

search = st.text_input("بحث")
if search:
    df = df[df["text"].str.contains(search)]

# ==============================
# News Display
# ==============================
for _, row in df.iterrows():
    st.markdown(f"""
    ---
    **{row['category']} | @{row['channel']}**  
    🕒 {row['time']}  
    {row['text']}
    """)

# ==============================
# Save log
# ==============================
df.to_csv("media_log.csv", index=False)
