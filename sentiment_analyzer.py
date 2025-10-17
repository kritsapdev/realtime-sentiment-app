# sentiment_analyzer.py
import requests
import os

# 1. URL ของ API ที่จะเรียกใช้ (เรายังคงใช้โมเดลเดิม แต่รันบนเซิร์ฟเวอร์ของ Hugging Face)
API_URL = "https://api-inference.huggingface.co/models/poom-sci/WangchanBERTa-finetuned-sentiment"

# 2. ดึง Token ที่เราเก็บไว้ใน Secret ซึ่ง CI/CD จะตั้งค่าให้เป็น Environment Variable
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    # ถ้าหา Token ไม่เจอ (เช่นตอนรันบนเครื่องตัวเอง) ให้แจ้งเตือนและหยุดทำงาน
    raise ValueError("ไม่พบ Hugging Face API Token กรุณาตั้งค่าใน Environment Variable ชื่อ HF_TOKEN")

# 3. เตรียม Header สำหรับยืนยันตัวตน
headers = {"Authorization": f"Bearer {hf_token}"}

def analyze_sentiment(text: str):
    """
    ฟังก์ชันสำหรับส่งข้อความไปวิเคราะห์ที่ Hugging Face Inference API
    """
    if not text or not isinstance(text, str):
        return {"label": "neutral", "score": 0.0}

    try:
        # 4. ส่ง request ไปยัง API พร้อมข้อความที่ต้องการวิเคราะห์
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        response.raise_for_status() # เช็คว่ามี error (เช่น 4xx, 5xx) หรือไม่

        # 5. จัดการผลลัพธ์ที่ได้กลับมา
        result = response.json()[0]
        # หา label ที่มี score สูงที่สุดจากผลลัพธ์ที่ได้
        top_sentiment = max(result, key=lambda x: x['score'])
        return {"label": top_sentiment['label'], "score": round(top_sentiment['score'], 4)}

    except requests.exceptions.RequestException as e:
        # ถ้าเกิด error ในการเชื่อมต่อ ให้พิมพ์ error และ trả về ค่ากลางๆ ไปก่อน
        print(f"Error calling Hugging Face API: {e}")
        return {"label": "neutral", "score": 0.0}