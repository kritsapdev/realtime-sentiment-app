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

async def process_and_broadcast_comment(comment_text: str):
    """
    ฟังก์ชันกลางสำหรับวิเคราะห์คอมเมนต์และส่งผลลัพธ์ไปยัง Dashboards
    """
    if not comment_text:
        return

    analysis_result = analyze_sentiment(comment_text)
    payload = {
        "text": comment_text,
        "label": analysis_result["label"],
        "score": analysis_result["score"]
    }
    await manager.broadcast(json.dumps(payload))

# <--- ลบ Endpoint ที่ซ้ำซ้อนออกไปแล้ว ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint สำหรับ WebSocket ให้ Dashboard เข้ามาเชื่อมต่อเพื่อรอฟังข้อมูล
    """
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/new-comment/")
async def new_comment_received(data: dict):
    comment_text = data.get("text", "")
    await process_and_broadcast_comment(comment_text)
    return {"message": "Analysis broadcasted successfully"}

async def run_simulation_loop():
    print("Starting simulation loop for 1 minute...")
    for i in range(12):
        comment_to_simulate = random.choice(COMMENTS)
        print(f"Loop {i+1}/12: Simulating '{comment_to_simulate}'")
        await process_and_broadcast_comment(comment_to_simulate)
        await asyncio.sleep(5)
    print("Simulation loop finished.")

@app.post("/simulate-new-comment")
async def trigger_simulation(background_tasks: BackgroundTasks):
    print("Received trigger from Cloud Scheduler.")
    background_tasks.add_task(run_simulation_loop)
    return {"status": "ok", "message": "Simulation loop started in background."}