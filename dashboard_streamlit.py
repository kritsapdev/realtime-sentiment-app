# dashboard_streamlit.py
import streamlit as st
import pandas as pd
import requests
import time
import os
import plotly.graph_objects as go

# --- การตั้งค่า ---
# ดึง URL ของ Backend มาจาก Environment Variable
# ถ้าหาไม่เจอ ให้ใช้ค่า localhost เป็นค่าเริ่มต้น (สำหรับทดสอบบนเครื่อง)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
API_ENDPOINT = f"{BACKEND_URL}/get-comments"

# ตั้งค่าหน้าเว็บให้เป็นแบบ Wide Mode
st.set_page_config(layout="wide")

# --- หน้าตาของ Dashboard ---
st.title("📊 Real-time Product Review Sentiment Dashboard (Streamlit)")

# สร้าง Layout แบบ 2 คอลัมน์
col1, col2 = st.columns([1, 2]) # คอลัมน์แรกกว้าง 1 ส่วน, คอลัมน์สองกว้าง 2 ส่วน

# สร้าง "พื้นที่ว่าง" สำหรับรอใส่กราฟและตาราง
with col1:
    pie_chart_placeholder = st.empty()
with col2:
    st.subheader("Latest Reviews")
    table_placeholder = st.empty()

# --- Loop การทำงานหลัก ---
while True:
    try:
        # 1. "วิ่งไปถาม" ข้อมูลจาก Backend
        response = requests.get(API_ENDPOINT)
        response.raise_for_status()
        data = response.json()

        if data:
            df = pd.DataFrame(data)

            # --- อัปเดตตาราง ---
            with table_placeholder.container():
                st.dataframe(df, use_container_width=True)

            # --- อัปเดตกราฟวงกลม ---
            sentiment_counts = df['label'].value_counts()
            with pie_chart_placeholder.container():
                st.subheader("Sentiment Distribution")
                fig = go.Figure(data=[go.Pie(
                    labels=sentiment_counts.index,
                    values=sentiment_counts.values,
                    marker_colors={'Positive':'#28a745', 'Negative':'#dc3545', 'Neutral':'#6c757d'},
                    hole=.3
                )])
                st.plotly_chart(fig, use_container_width=True)
        else:
            # ถ้ายังไม่มีข้อมูล ให้แสดงข้อความรอ
            with table_placeholder.container():
                st.info("Waiting for new comments...")
            with pie_chart_placeholder.container():
                st.subheader("Sentiment Distribution")
                st.info("No data to display.")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to backend: {e}")

    # 2. "นอนรอ" 3 วินาที ก่อนจะไปถามใหม่
    time.sleep(3)
