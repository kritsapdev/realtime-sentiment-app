# main.py
import json
import random
import asyncio
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sentiment_analyzer import analyze_sentiment

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

COMMENTS = [
    "สินค้าคุณภาพดีมากครับ ประทับใจสุดๆ", "ส่งของเร็วดีนะ แต่แพ็คเกจบุบไปหน่อย",
    "เฉยๆ อะ ไม่ได้ดีเท่าที่คาดหวังไว้", "โคตรห่วย! ใช้ได้วันเดียวพัง",
    "บริการหลังการขายดีเยี่ยม ตอบแชทไว", "สีสวยตรงปก ชอบมากค่ะ", "รอนานมากกกกกกกกก",
]

# <<< CHANGE 1: สร้าง "ตำราอาหาร" หรือฟังก์ชันกลาง >>>
# ฟังก์ชันนี้จะทำหน้าที่วิเคราะห์และ broadcast ซึ่งเป็นหัวใจหลัก
async def process_and_broadcast_comment(comment_text: str):
    """
    ฟังก์ชันกลางสำหรับวิเคราะห์คอมเมนต์และส่งผลลัพธ์ไปยัง Dashboards
    """
    if not comment_text:
        return

    # 1. เรียกใช้ AI เพื่อวิเคราะห์ความรู้สึก
    analysis_result = analyze_sentiment(comment_text)

    # 2. เตรียมข้อมูลที่จะส่งไปให้ Dashboard
    payload = {
        "text": comment_text,
        "label": analysis_result["label"],
        "score": analysis_result["score"]
    }

    # 3. สั่งให้ผู้จัดการส่งข้อมูล (broadcast)
    await manager.broadcast(json.dumps(payload))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# <<< CHANGE 2: อัปเดต "ไดรฟ์ทรู" ให้มาใช้ "ตำราอาหาร" >>>
@app.post("/new-comment/")
async def new_comment_received(data: dict):
    comment_text = data.get("text", "")
    # เรียกใช้ฟังก์ชันกลาง
    await process_and_broadcast_comment(comment_text)
    return {"message": "Analysis broadcasted successfully"}


async def run_simulation_loop():
    print("Starting simulation loop for 1 minute...")
    for i in range(12):
        comment_to_simulate = random.choice(COMMENTS)
        print(f"Loop {i+1}/12: Simulating '{comment_to_simulate}'")
        # <<< CHANGE 3: อัปเดต "ผู้จัดการ" ให้มาใช้ "ตำราอาหาร" >>>
        await process_and_broadcast_comment(comment_to_simulate)
        await asyncio.sleep(5)
    print("Simulation loop finished.")


@app.post("/simulate-new-comment")
async def trigger_simulation(background_tasks: BackgroundTasks):
    print("Received trigger from Cloud Scheduler.")
    background_tasks.add_task(run_simulation_loop)
    return {"status": "ok", "message": "Simulation loop started in background."}