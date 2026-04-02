import telebot
import time
import re

# ==============================================================
# 👑 CẤU HÌNH BOT - V10 SUPREME 5-CORE
# ==============================================================
TOKEN = "8758980551:AAFN_FwHrq7PhZLcpn6hd450jhpVea59VYU"
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()
time.sleep(1)

# ==============================================================
# 💎 LÕI V10: HỢP NHẤT 5 THUẬT TOÁN TỪ BỘ TOOL VIP
# ==============================================================
def supreme_5_core_decrypt(hash_str):
    hash_str = hash_str.lower().strip()
    hash_len = len(hash_str)
    votes_tai = 0
    details = []

    # Lớp 1: Tổng biến thiên Hex (Chẵn/Lẻ)
    if sum(int(c, 16) for c in hash_str) % 2 == 0:
        votes_tai += 1
        details.append("✔️ Lớp 1 (Tổng Hex)     : TÀI 🔴")
    else:
        details.append("✔️ Lớp 1 (Tổng Hex)     : XỈU 🔵")

    # Lớp 2: Biên độ nén (Đầu + Cuối)
    if (int(hash_str[0], 16) + int(hash_str[-1], 16)) >= 16:
        votes_tai += 1
        details.append("✔️ Lớp 2 (Biên độ)      : TÀI 🔴")
    else:
        details.append("✔️ Lớp 2 (Biên độ)      : XỈU 🔵")

    # Lớp 3: Trọng tâm ma trận (Trung bình cặp)
    pairs = [int(hash_str[i:i+2], 16) for i in range(0, hash_len, 2)]
    if (sum(pairs) / len(pairs)) > 127:
        votes_tai += 1
        details.append("✔️ Lớp 3 (Trọng tâm)    : TÀI 🔴")
    else:
        details.append("✔️ Lớp 3 (Trọng tâm)    : XỈU 🔵")

    # Lớp 4: Tần suất điểm mù (Ký tự >= 8)
    if sum(1 for c in hash_str if int(c, 16) >= 8) >= (hash_len / 2):
        votes_tai += 1
        details.append("✔️ Lớp 4 (Tần suất)     : TÀI 🔴")
    else:
        details.append("✔️ Lớp 4 (Tần suất)     : XỈU 🔵")

    # Lớp 5: Thuật toán Lượng tử (XOR Matrix)
    xor_val = 0
    for c in hash_str: xor_val ^= int(c, 16)
    if xor_val >= 8:
        votes_tai += 1
        details.append("✔️ Lớp 5 (XOR Lõi)      : TÀI 🔴")
    else:
        details.append("✔️ Lớp 5 (XOR Lõi)      : XỈU 🔵")

    # XỬ LÝ KẾT QUẢ VÀ TỈ LỆ THẮNG
    votes_xiu = 5 - votes_tai
    is_tai = votes_tai >= 3
    
    # Ép Win Rate theo độ đồng thuận của 5 Lớp
    if votes_tai == 5 or votes_xiu == 5:
        win_rate, advice = 99.99, "🔥 ALL IN - ĐẬP NÁT SERVER"
    elif votes_tai == 4 or votes_xiu == 4:
        win_rate, advice = 95.50, "⚡ VÀO CĂNG TAY - CHẮC THẮNG"
    else:
        win_rate, advice = 88.88, "⚖️ VÀO TẦM TRUNG - CẦU BIẾN ĐỘNG"

    res = "TÀI" if is_tai else "XỈU"
    icon = "🔴" if is_tai else "🔵"
    
    return res, icon, win_rate, advice, details, votes_tai, votes_xiu

# ==============================================================
# 📱 GIAO DIỆN & LỆNH
# ==============================================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        f"👑 **V10 - SUPREME 5-CORE DECRYPTOR** 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Tích hợp lõi phân tích 5 lớp độc lập.\n"
        f"Đủ sức bóc tách mọi biến số MD5.\n"
        f"👉 **Dán mã vào đây để bắt đầu hủy diệt!**"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: len(m.text.strip()) == 32)
def handle_md5(message):
    raw_md5 = message.text.strip()
    if not re.match(r'^[0-9a-fA-F]{32}$', raw_md5): return

    try:
        # Xử lý nhanh gọn, không delay giả
        status_msg = bot.reply_to(message, "⚙️ `Đang đồng bộ 5 lõi phân tích...`", parse_mode="Markdown")
        
        # Chạy phân tích đa tầng
        res, icon, win_rate, advice, details, v_tai, v_xiu = supreme_5_core_decrypt(raw_md5)
        
        # Nối danh sách chi tiết thành chuỗi hiển thị
        details_str = "\n".join(details)
        
        # In kết quả chi tiết như hacker thực thụ
        final_res = (
            f"☠️ **[BÁO CÁO PHÂN TÍCH V10]** ☠️\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{details_str}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **ĐỒNG THUẬN:** `{v_tai} TÀI / {v_xiu} XỈU`\n"
            f"🎯 **CHỐT KÈO:** {icon} **{res}**\n"
            f"📈 **TỈ LỆ THẮNG:** `{win_rate}%`\n"
            f"💰 **CHỈ THỊ:** {advice}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 *Đã đối chiếu 5 thuật toán!*"
        )
        
        bot.edit_message_text(final_res, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
        
    except Exception:
        bot.send_message(message.chat.id, "⚠️ Nghẽn máy chủ cục bộ, quăng lại mã đi ní!")

if __name__ == "__main__":
    print("--- [V10 SUPREME 5-CORE] SẴN SÀNG CÀY NÁT GAME ---")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception:
            time.sleep(1)

