# discord_bot.py
import discord
import os
import requests

# --- การตั้งค่า ---
# โหลดจาก Environment Variables เพื่อความปลอดภัย
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
# ชื่อของ Channel ที่จะให้บอททำงาน (ต้องตรงเป๊ะ!)
TARGET_CHANNEL = "sentiment-test" 
# URL ของ Backend บน Cloud Run
BACKEND_API_URL = "https://realtime-sentiment-app-256576118647.asia-southeast1.run.app/new-comment/" # <-- แก้ไขตรงนี้

# --- สิ้นสุดการตั้งค่า ---

# ตั้งค่า "ความตั้งใจ" (Intents) ของบอท
intents = discord.Intents.default()
intents.message_content = True # อนุญาตให้บอทอ่านเนื้อหาข้อความได้

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'บอทล็อกอินสำเร็จในชื่อ {client.user}')
    print(f'กำลังดักฟังข้อความใน Channel: #{TARGET_CHANNEL}')

@client.event
async def on_message(message):
    # 1. ไม่สนใจข้อความจากตัวเอง (บอท)
    if message.author == client.user:
        return

    # 2. ทำงานเฉพาะใน Channel ที่กำหนดไว้เท่านั้น
    if message.channel.name == TARGET_CHANNEL:
        print("-" * 30)
        print(f"พบคอมเมนต์ใหม่จาก {message.author}:")
        print(f"ข้อความ: {message.content}")

        try:
            # 3. ส่งข้อความไปที่ Backend เพื่อวิเคราะห์
            payload = {"text": message.content}
            response = requests.post(BACKEND_API_URL, json=payload)
            response.raise_for_status()
            print(f"✅ ส่งไปที่ backend สำเร็จ!")

        except requests.exceptions.RequestException as e:
            print(f"❌ เกิดข้อผิดพลาดในการส่งไปที่ backend: {e}")

# รันบอท
if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("!!! ข้อผิดพลาด: กรุณาตั้งค่า DISCORD_BOT_TOKEN")
else:
    client.run(BOT_TOKEN)