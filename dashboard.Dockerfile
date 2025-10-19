# dashboard.Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# คำสั่งสำหรับรัน Dashboard Server
# ใช้ shell form เพื่อให้ $PORT ทำงานได้
# CMD ใหม่ (ที่ถูกต้องสำหรับ Production):
#CMD waitress-serve --host=0.0.0.0 --port=$PORT dashboard:server
CMD ["waitress-serve", "--host=0.0.0.0", "--port=8080", "dashboard:server"]