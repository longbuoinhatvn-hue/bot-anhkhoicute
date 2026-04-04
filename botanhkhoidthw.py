import asyncio
import json
import time
import requests
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

# ===== CONFIG =====
TOKEN = "8266148297:AAFLEr7V8XpPMw4M4Xw4d3RFNZPKs-rN1xI"
ADMIN_ID = 6094686933
API_URL = "https://lc79md5khoiancute.onrender.com/api/taixiu"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== DATA =====
users = set()
keys = {}
admins = {ADMIN_ID}
history = []
auto_users = set()
last_phien = None

# ===== LOAD/SAVE =====
def save():
    with open("data.json", "w") as f:
        json.dump({
            "users": list(users),
            "keys": keys,
            "admins": list(admins),
            "history": history,
            "auto_users": list(auto_users)
        }, f)

def load():
    global users, keys, admins, history, auto_users
    try:
        with open("data.json") as f:
            data = json.load(f)
            users = set(data["users"])
            keys = data["keys"]
            admins = set(data["admins"])
            history = data["history"]
            auto_users = set(data.get("auto_users", []))
    except:
        pass

load()

# ===== API =====
def get_data():
    try:
        return requests.get(API_URL, timeout=5).json()
    except:
        return None

# ===== AUTO LOOP =====
async def auto_check():
    global last_phien

    while True:
        data = get_data()

        if data:
            phien = data["phien_hien_tai"]

            if phien != last_phien:
                last_phien = phien

                du_doan = data["du_doan"]
                do_tin_cay = data["do_tin_cay"]
                pattern = data["pattern"]

                history.append(du_doan)
                if len(history) > 50:
                    history.pop(0)

                text = f"""🎰 [ LẨU CUA MD5 AI ]

📜 Phiên: #{phien}
━━━━━━━━━━━━━━
🎯 Dự đoán: {du_doan.upper()}
📊 Tin cậy: {do_tin_cay}
📉 Cầu: {pattern}
━━━━━━━━━━━━━━"""

                for u in auto_users:
                    try:
                        await bot.send_message(u, text)
                    except:
                        pass

        await asyncio.sleep(1)

# ===== START =====
@dp.message(Command("start"))
async def start(msg: Message):
    users.add(msg.from_user.id)
    save()
    await msg.reply("🤖 Bot Lẩu Cua MD5\nDùng /help")

# ===== HELP =====
@dp.message(Command("help"))
async def help_cmd(msg: Message):
    await msg.reply("""📌 LỆNH BOT

👤 USER:
/dudoanmd5
/key <key>
/on - bật auto
/off - tắt auto

👑 ADMIN:
/taokey <ngày>
/listkey
/xoakey <key>
/thongbao <text>
/thongke
""")

# ===== AUTO ON/OFF =====
@dp.message(Command("on"))
async def auto_on(msg: Message):
    if msg.from_user.id not in users:
        return await msg.reply("❌ Chưa có key")

    auto_users.add(msg.from_user.id)
    save()
    await msg.reply("✅ Đã bật auto")

@dp.message(Command("off"))
async def auto_off(msg: Message):auto_users.discard(msg.from_user.id)
    save()
    await msg.reply("⛔ Đã tắt auto")

# ===== KEY =====
@dp.message(Command("taokey"))
async def create_key(msg: Message):
    if msg.from_user.id not in admins:
        return
    try:
        days = int(msg.text.split()[1])
        key = f"KEY{int(time.time())}"
        keys[key] = time.time() + days * 86400
        save()
        await msg.reply(f"🔑 {key} | {days} ngày")
    except:
        await msg.reply("Sai cú pháp")

@dp.message(Command("key"))
async def use_key(msg: Message):
    try:
        key = msg.text.split()[1]
        if key in keys and time.time() < keys[key]:
            users.add(msg.from_user.id)
            save()
            await msg.reply("✅ Kích hoạt OK")
        else:
            await msg.reply("❌ Key lỗi")
    except:
        await msg.reply("Sai cú pháp")

# ===== DỰ ĐOÁN TAY =====
@dp.message(Command("dudoanmd5"))
async def predict(msg: Message):
    if msg.from_user.id not in users:
        return await msg.reply("❌ Chưa có key")

    data = get_data()
    if not data:
        return await msg.reply("API lỗi")

    await msg.reply(
        f"""🎰 [ LẨU CUA MD5 ]

📜 Phiên: #{data["phien_hien_tai"]}
━━━━━━━━━━━━━━
🎯 Dự đoán: {data["du_doan"].upper()}
📊 Tin cậy: {data["do_tin_cay"]}
📉 Cầu: {data["pattern"]}
━━━━━━━━━━━━━━"""
    )

# ===== THỐNG KÊ =====
@dp.message(Command("thongke"))
async def stats(msg: Message):
    if msg.from_user.id not in admins:
        return

    tai = history.count("tài")
    xiu = history.count("xiu")

    await msg.reply(f"Tài: {tai}\nXỉu: {xiu}")

# ===== RUN =====
async def main():
    print("Bot đang chạy...")
    asyncio.create_task(auto_check())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
