# main.py
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


@app.post("/new-comment/")
async def new_comment_received(data: dict):
    """
    Endpoint สำหรับรับคอมเมนต์ใหม่ๆ
    เมื่อมีคนยิงข้อมูลมาที่นี่ ระบบจะเริ่มทำงาน
    """
    comment_text = data.get("text", "")
    if not comment_text:
        return {"error": "Text is required"}

    # 1. เรียกใช้ AI เพื่อวิเคราะห์ความรู้สึก
    analysis_result = analyze_sentiment(comment_text)

    # 2. เตรียมข้อมูลที่จะส่งไปให้ Dashboard
    payload = {
        "text": comment_text,
        "label": analysis_result["label"],
        "score": analysis_result["score"]
    }

    # 3. สั่งให้ผู้จัดการส่งข้อมูล (broadcast) ไปยังทุก Dashboard
    await manager.broadcast(json.dumps(payload))

    return {"message": "Analysis broadcasted successfully", "data": payload}