# simulator.py
import requests
import time
import random

# รายการคอมเมนต์ตัวอย่างที่เราจะใช้สุ่มส่ง
COMMENTS = [
"The product is of excellent quality. I'm super impressed!",  
"Fast delivery, but the package was a bit dented.",
"It's just okay. Not as good as I expected.",
"Terrible! It broke after just one day of use.",  
"Excellent after-sales service. Very responsive in chat.",  
"The color matches the pictures. I really love it!",
"Waited for soooo long!",  
"The packaging was done really well.",  
"The scent is not very pleasant."
]

# URL ของ Backend Server ที่เรารันไว้อยู่
# NEW - CORRECT CODE
API_URL = "https://realtime-sentiment-app-256576118647.asia-southeast1.run.app/new-comment/"

print("--- Comment Simulator กำลังจะเริ่มทำงาน ---")
print("--- กด CTRL+C เพื่อหยุดการทำงาน ---")
time.sleep(2)

# วนลูปทำงานไปเรื่อยๆ ไม่มีวันหยุด
while True:
    try:
        # 1. สุ่มเลือกคอมเมนต์จากในลิสต์
        comment = random.choice(COMMENTS)
        print(f"กำลังส่งคอมเมนต์: '{comment}'")

        # 2. ส่งคอมเมนต์ไปที่ Backend ผ่าน HTTP POST
        response = requests.post(API_URL, json={"text": comment})
        response.raise_for_status() # เช็คว่าส่งสำเร็จหรือไม่ (ถ้าไม่จะ error)

        # 3. พิมพ์ผลลัพธ์ที่ได้กลับมาจาก Server
        print(f"Server ตอบกลับ: {response.json()}")
        print("-" * 20)

        # 4. หน่วงเวลา 3-8 วินาที ก่อนจะส่งคอมเมนต์ถัดไป
        time.sleep(random.randint(3, 8))

    except requests.exceptions.RequestException as e:
        print(f"\n!!! ไม่สามารถเชื่อมต่อกับ Server ได้: {e}")
        print("!!! โปรดตรวจสอบว่า Backend (uvicorn) กำลังทำงานอยู่หรือไม่")
        break
    except KeyboardInterrupt:
        print("\n--- หยุดการทำงาน Simulator ---")
        break