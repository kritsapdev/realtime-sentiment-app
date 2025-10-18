# sentiment_analyzer.py
import os
import google.generativeai as genai

# 1. ดึง API Key ที่เราเก็บไว้ใน Secret
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("ไม่พบ Gemini API Key กรุณาตั้งค่าใน Environment Variable ชื่อ GEMINI_API_KEY")

# 2. ตั้งค่าการเชื่อมต่อกับ Gemini
genai.configure(api_key=GEMINI_API_KEY)

# 3. สร้าง Instance ของโมเดล Gemini
model = genai.GenerativeModel('gemini-2.5-flash')

# 4. สร้าง "Prompt" หรือ "บทสนทนา" เพื่อสอนให้ Gemini วิเคราะห์ Sentiment
# การให้ตัวอย่าง (few-shot prompting) จะทำให้ผลลัพธ์แม่นยำและคงที่มาก
prompt_template = """
Analyze the sentiment of the following product review.
Your response must be a single word: Positive, Negative, or Neutral.

Review: "สินค้าดีมาก ส่งไว คุณภาพเยี่ยม!"
Sentiment: Positive

Review: "ห่วยแตกที่สุด ใช้ได้วันเดียวก็พัง"
Sentiment: Negative

Review: "ก็โอเคนะ สมราคา"
Sentiment: Neutral

Review: "{review_text}"
Sentiment:
"""

def analyze_sentiment(text: str):
    """
    ฟังก์ชันสำหรับส่งข้อความไปวิเคราะห์โดย Gemini API
    """
    if not text or not isinstance(text, str):
        return {"label": "Neutral", "score": 0.0}

    try:
        # 5. เติมข้อความรีวิวลงใน "บทสนทนา" ของเรา
        prompt = prompt_template.format(review_text=text)

        # 6. ส่ง Prompt ไปให้ Gemini ประมวลผล
        response = model.generate_content(prompt)

        # 7. จัดการคำตอบที่ได้กลับมา
        # Gemini จะตอบกลับมาเป็นข้อความ เราจึงต้องทำความสะอาดเล็กน้อย
        result_text = response.text.strip().capitalize()

        # ตรวจสอบเพื่อให้แน่ใจว่าคำตอบอยู่ในรูปแบบที่เราต้องการ
        if result_text not in ["Positive", "Negative", "Neutral"]:
            result_text = "Neutral" # ถ้า Gemini ตอบอย่างอื่น ให้ถือว่าเป็น Neutral

        # หมายเหตุ: Gemini ไม่ได้ให้ค่า score มาเหมือนโมเดลก่อนหน้า
        # เราจึงใส่ค่า 1.0 เพื่อให้โครงสร้างข้อมูลเหมือนเดิม
        return {"label": result_text, "score": 1.0}

    except Exception as e:
        # ถ้าเกิด error ในการเรียก API ให้พิมพ์ error และ trả về ค่ากลางๆ
        print(f"Error calling Gemini API: {e}")
        return {"label": "Neutral", "score": 0.0}