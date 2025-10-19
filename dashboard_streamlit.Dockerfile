# dashboard_streamlit.Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# คำสั่งสำหรับรัน Streamlit Server
# --server.port $PORT บอกให้ Streamlit ใช้ Port ที่ Cloud Run กำหนด
# --server.headless true เป็นการตั้งค่าที่แนะนำสำหรับ Production
CMD ["streamlit", "run", "dashboard_streamlit.py", "--server.port", "8080", "--server.headless", "true"]
