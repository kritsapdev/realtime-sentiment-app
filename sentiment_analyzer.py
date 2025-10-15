# sentiment_analyzer.py
from transformers import pipeline

# 1. โหลดโมเดล AI สำเร็จรูปสำหรับวิเคราะห์ความรู้สึก
# เราจะโหลดโมเดลนี้แค่ครั้งเดียวตอนโปรแกรมเริ่มทำงาน เพื่อความรวดเร็ว
# โมเดล "lxyuan/distilbert-base-multilingual-cased-sentiments-student"
# ถูกฝึกมาให้เข้าใจหลายภาษา รวมถึงภาษาไทย
print("กำลังโหลดโมเดล... (อาจใช้เวลาสักครู่ในครั้งแรก)")
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="poom-sci/WangchanBERTa-finetuned-sentiment"
)
print("โมเดลพร้อมใช้งาน!")


def analyze_sentiment(text: str):
    """
    ฟังก์ชันสำหรับรับข้อความ (text) และส่งคืนผลการวิเคราะห์
    ในรูปแบบของ dictionary ที่มี 'label' และ 'score'
    """
    if not text or not isinstance(text, str):
        return {"label": "neutral", "score": 0.0}

    # ใช้โมเดลที่โหลดไว้มาทำการวิเคราะห์
    result = sentiment_pipeline(text)[0]
    return {"label": result['label'], "score": round(result['score'], 4)}


# --- ส่วนนี้สำหรับทดสอบการทำงานของไฟล์นี้โดยตรง ---
if __name__ == "__main__":
    # ลองทดสอบกับข้อความตัวอย่าง
    text1 = "สินค้าดีมาก ส่งไว คุณภาพเยี่ยม!"
    text2 = "ห่วยแตกที่สุด ใช้ได้วันเดียวก็พัง"
    text3 = "ก็โอเคนะ สมราคา"

    print("\n--- ผลการทดสอบ ---")
    print(f"รีวิว: '{text1}' -> ผลลัพธ์: {analyze_sentiment(text1)}")
    print(f"รีวิว: '{text2}' -> ผลลัพธ์: {analyze_sentiment(text2)}")
    print(f"รีวิว: '{text3}' -> ผลลัพธ์: {analyze_sentiment(text3)}")