# main.py
import random # เพิ่มบรรทัดนี้
import json
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware # เพิ่มเข้ามาเพื่อ Dashboard ในอนาคต

# Import ฟังก์ชันวิเคราะห์ที่เราสร้างไว้ในขั้นตอนที่แล้ว
from sentiment_analyzer import analyze_sentiment

# สร้างแอปพลิเคชัน FastAPI
app = FastAPI()

# --- ส่วนนี้จำเป็นเพื่อให้ Dashboard (ที่รันคนละที่) คุยกับ Backend ได้ ---
# อนุญาตการเชื่อมต่อจากทุกแหล่ง (สำหรับตอนพัฒนา)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    """
    คลาสสำหรับจัดการการเชื่อมต่อ WebSocket ทั้งหมด
    เปรียบเหมือนผู้จัดการห้องแชท
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # ส่งข้อความไปยังทุก Dashboard ที่เชื่อมต่ออยู่
        for connection in self.active_connections:
            await connection.send_text(message)

# สร้าง instance ของผู้จัดการ
manager = ConnectionManager()


# เพิ่มลิสต์คอมเมนต์ตัวอย่างเข้ามาใน Backend เลย
COMMENTS = [
    "สินค้าคุณภาพดีมากครับ ประทับใจสุดๆ",
    "ส่งของเร็วดีนะ แต่แพ็คเกจบุบไปหน่อย",
    "เฉยๆ อะ ไม่ได้ดีเท่าที่คาดหวังไว้",
    "โคตรห่วย! ใช้ได้วันเดียวพัง",
    "บริการหลังการขายดีเยี่ยม ตอบแชทไว",
    "สีสวยตรงปก ชอบมากค่ะ",
    "รอนานมากกกกกกกกก",
]



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint สำหรับ WebSocket เปรียบเหมือนประตูห้องแชท
    Dashboard จะมาเชื่อมต่อที่นี่เพื่อรอฟังข้อมูล
    """
    await manager.connect(websocket)
    try:
        while True:
            # ทำให้การเชื่อมต่อคงอยู่เรื่อยๆ
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# --- Endpoint ใหม่สำหรับให้ Cloud Scheduler เรียก ---
@app.post("/simulate-new-comment")
async def simulate_new_comment():
    """
    Endpoint นี้จะทำงานเหมือน simulator.py ทุกประการ
    คือสุ่มคอมเมนต์, วิเคราะห์, แล้ว broadcast
    """
    comment_to_simulate = random.choice(COMMENTS)

    # เรียกใช้ฟังก์ชันเดิมที่เรามีอยู่แล้ว
    await new_comment_received({"text": comment_to_simulate})

    return {"status": "ok", "simulated_comment": comment_to_simulate}