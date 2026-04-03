import os
import time
import requests
import telebot
from flask import Flask
from threading import Thread

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG
# ==========================================
# Gắn cứng Token của ní luôn
BOT_TOKEN = "8636406117:AAHwKMo5jhwijTbfPrP5yOTjxmOVPq7g1PI"
bot = telebot.TeleBot(BOT_TOKEN)

API_URL = "https://lc79md5khoiancute.onrender.com/api/taixiu"

# Biến toàn cục để lưu trạng thái
TARGET_CHAT_ID = None # Sẽ tự nhận diện khi ní gõ /start trong nhóm
CURRENT_SESSION = None
PENDING_PREDICT = None
STATS = {"win": 5029, "loss": 5017} # Set số ảo ban đầu cho đẹp như hình của ní

# ==========================================
# 2. SERVER GIỮ NHIỆT (CHỐNG NGỦ GẬT)
# ==========================================
app = Flask(__name__)
@app.route('/')
def home():
    return "🚀 BOT AUTO KÉO LC79 ĐANG CHẠY 24/7!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 3. THUẬT TOÁN DỰ ĐOÁN & % TIN CẬY
# ==========================================
def calculate_prediction(session_id):
    # Thuật toán nội suy ảo dựa vào ID Phiên để ra kết quả "có vẻ nguy hiểm"
    numeric_id = int(''.join(filter(str.isdigit, str(session_id))) or 0)
    is_tai = (numeric_id * 7 + 13) % 2 == 0
    
    # Random tỷ lệ từ 50.1% đến 85.9%
    base_rate = 50 + (numeric_id % 35) + (numeric_id % 100) / 100.0
    
    return {
        "choice": "Tài" if is_tai else "Xỉu",
        "rate": f"{base_rate:.1f}%"
    }

# ==========================================
# 4. VÒNG LẶP AUTO QUÉT API (Mỗi 3 giây)
# ==========================================
def auto_monitor():
    global CURRENT_SESSION, PENDING_PREDICT, STATS
    
    while True:
        if not TARGET_CHAT_ID:
            time.sleep(3)
            continue # Đợi sếp gõ /start để biết phải gửi tin vào đâu
            
        try:
            res = requests.get(f"{API_URL}?t={int(time.time())}", timeout=5)
            if res.status_code == 200:
                data = res.json()
                
                # Cấu trúc API giả định (ní tự chỉnh sửa nếu tên biến của ní khác)
                api_phien = data.get("phien") or data.get("id") or data.get("session")
                api_kq = data.get("ket_qua") or data.get("result") or data.get("kq")
                
                if not api_phien:
                    time.sleep(3)
                    continue

                # A. NẾU LÀ PHIÊN MỚI TINH -> BẮN LỆNH DỰ ĐOÁN
                if api_phien != CURRENT_SESSION:
                    # 1. Chốt kết quả phiên cũ nếu chưa chốt
                    if CURRENT_SESSION and PENDING_PREDICT and api_kq:
                        process_result(CURRENT_SESSION, PENDING_PREDICT, api_kq)
                    
                    # 2. Cập nhật phiên mới và tính toán
                    CURRENT_SESSION = api_phien
                    PENDING_PREDICT = calculate_prediction(api_phien)
                    
                    # 3. Bắn 4 tin nhắn liên tục lên Channel như ảnh mẫu
                    bot.send_message(TARGET_CHAT_ID, f"💎 PHIÊN: #{CURRENT_SESSION}")
                    time.sleep(0.5)
                    bot.send_message(TARGET_CHAT_ID, f"🔮 Dự đoán: {PENDING_PREDICT['choice']}")
                    time.sleep(0.5)
                    bot.send_message(TARGET_CHAT_ID, f"⚡ Độ tin cậy: {PENDING_PREDICT['rate']}")
                    time.sleep(0.5)
                    bot.send_message(TARGET_CHAT_ID, "🎲 *Hãy vào lệnh hợp lý!*", parse_mode="Markdown")
                
                # B. NẾU VẪN LÀ PHIÊN ĐÓ, NHƯNG ĐÃ CÓ KẾT QUẢ THỰC TẾ TRẢ VỀ
                elif CURRENT_SESSION == api_phien and api_kq and str(api_kq).strip() != "":
                    # Nếu đang đợi kết quả thì xử lý luôn
                    if PENDING_PREDICT:
                        process_result(CURRENT_SESSION, PENDING_PREDICT, api_kq)
                        PENDING_PREDICT = None # Xóa để không báo lại nhiều lần
                        
        except Exception as e:
            print(f"Lỗi quét API: {e}")
            
        time.sleep(3) # Quét lại sau 3 giây

def process_result(phien, predict, actual_result):
    global STATS
    
    # Chuẩn hóa kết quả thực tế
    act_str = str(actual_result).upper()
    act_choice = "Tài" if "T" in act_str or "TÀI" in act_str else ("Xỉu" if "X" in act_str or "XỈU" in act_str else act_str)
    
    is_win = (predict["choice"].upper() == act_choice.upper())
    
    if is_win:
        STATS["win"] += 1
        status_icon = "✅"
        status_text = "THẮNG"
    else:
        STATS["loss"] += 1
        status_icon = "❌"
        status_text = "THUA"
        
    # Bắn tin nhắn trả thưởng
    bot.send_message(TARGET_CHAT_ID, f"{status_icon} *KẾT QUẢ PHIÊN #{phien}*", parse_mode="Markdown")
    time.sleep(0.5)
    bot.send_message(TARGET_CHAT_ID, f"📍 {act_choice}\n📢 {status_text}")
    time.sleep(0.5)
    bot.send_message(TARGET_CHAT_ID, f"📊 Thắng: {STATS['win']} | Thua: {STATS['loss']}")

# ==========================================
# 5. LỆNH ĐIỀU KHIỂN TỪ TELEGRAM
# ==========================================
@bot.message_handler(commands=['start'])
def start_auto_bot(message):
    global TARGET_CHAT_ID
    TARGET_CHAT_ID = message.chat.id # Lấy ID của nhóm/kênh hiện tại
    bot.reply_to(message, f"🎯 Đã khóa mục tiêu vào nhóm/kênh này (ID: {TARGET_CHAT_ID}).\nHệ thống Auto Kéo LC79 đang khởi động...")

@bot.message_handler(commands=['stop'])
def stop_auto_bot(message):
    global TARGET_CHAT_ID
    TARGET_CHAT_ID = None
    bot.reply_to(message, "🛑 Đã tạm dừng bắn lệnh tự động.")

# ==========================================
# 6. KÍCH HOẠT ĐA LUỒNG
# ==========================================
if __name__ == "__main__":
    # Bật Web Server
    Thread(target=run_server, daemon=True).start()
    
    # Bật luồng tự động quét API
    Thread(target=auto_monitor, daemon=True).start()
    
    # Bật Bot Tele
    print("Bot Auto Kéo đã lên nòng...")
    bot.infinity_polling()
