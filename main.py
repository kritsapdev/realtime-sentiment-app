# main.py
import json
import random
from typing import List, Dict
from collections import deque
from fastapi import FastAPI
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

# --- NEW: สร้าง "ที่เก็บข้อมูล" แบบจำกัดขนาด ---
# deque จะเก็บข้อมูลล่าสุดไว้ 100 รายการ ถ้ามีอันใหม่เข้ามา อันเก่าสุดจะถูกลบออก
latest_comments: deque = deque(maxlen=100)

# --- NEW: Endpoint สำหรับให้ Streamlit มา "ถาม" ข้อมูล ---
@app.get("/get-comments")
async def get_comments():
    """
    ส่งรายการคอมเมนต์ทั้งหมดที่เก็บไว้อยู่กลับไป
    """
    # แปลง deque ให้เป็น list ธรรมดาก่อนส่ง
    return list(latest_comments)

# --- WebSocket และ ConnectionManager ถูกลบออกไป ---

async def process_comment(comment_text: str):
    """
    ฟังก์ชันกลางสำหรับวิเคราะห์คอมเมนต์และ "เก็บ" ผลลัพธ์
    """
    if not comment_text:
        return

    print(f"INFO: Processing comment: '{comment_text}'")
    analysis_result = analyze_sentiment(comment_text)
    payload = {
        "text": comment_text,
        "label": analysis_result["label"],
        "score": analysis_result["score"]
    }
    # เพิ่มข้อมูลใหม่เข้าไป "ข้างหน้า" ของที่เก็บข้อมูล
    latest_comments.appendleft(payload)
    print(f"INFO: Comment added. Total comments stored: {len(latest_comments)}")

@app.post("/new-comment/")
async def new_comment_received(data: dict):
    """
    Endpoint ที่รับคอมเมนต์ใหม่จาก Discord Bot
    """
    comment_text = data.get("text", "")
    await process_comment(comment_text)
    return {"message": "Comment received and processed successfully"}

# โค้ดส่วน Simulator ยังคงเก็บไว้สำหรับการทดสอบได้ แต่ไม่จำเป็นต้องใช้แล้ว
COMMENTS = [
    "สินค้าคุณภาพดีมากครับ ประทับใจสุดๆ", "ส่งของเร็วดีนะ แต่แพ็คเกจบุบไปหน่อย",
    "เฉยๆ อะ ไม่ได้ดีเท่าที่คาดหวังไว้", "โคตรห่วย! ใช้ได้วันเดียวพัง",
]
@app.post("/simulate-new-comment")
async def simulate_new_comment():
    comment_to_simulate = random.choice(COMMENTS)
    await process_comment(comment_to_simulate)
    return {"status": "ok", "simulated_comment": comment_to_simulate}

