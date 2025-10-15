# simulator.py
import requests
import time
import random

# รายการคอมเมนต์ตัวอย่างที่เราจะใช้สุ่มส่ง
COMMENTS = [
    "สินค้าคุณภาพดีมากครับ ประทับใจสุดๆ",
    "ส่งของเร็วดีนะ แต่แพ็คเกจบุบไปหน่อย",
    "เฉยๆ อะ ไม่ได้ดีเท่าที่คาดหวังไว้",
    "โคตรห่วย! ใช้ได้วันเดียวพัง",
    "บริการหลังการขายดีเยี่ยม ตอบแชทไว",
    "สีสวยตรงปก ชอบมากค่ะ",
    "รอนานมากกกกกกกกก",
    "แพ็คของมาดีมากๆ เลยครับ",
    "กลิ่นไม่ค่อยหอมเท่าไหร่"
]

# URL ของ Backend Server ที่เรารันไว้อยู่
API_URL = "http://127.0.0.1:8000/new-comment/"

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