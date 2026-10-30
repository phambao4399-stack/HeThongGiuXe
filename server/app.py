import os
import cv2
import sqlite3
import math
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify
from database import (verify_admin, find_card, insert_log, get_latest_logs, 
                      get_stats, get_all_cards, save_card, delete_card, 
                      delete_log, clear_all_logs, DB_PATH)
from camera_mgr import CameraManager
from ai_pipeline import run_ocr, save_capture

# 👉 ĐÃ SỬA: Lùi 2 cấp từ thư mục 'server' ra ngoài gốc project để nạp đúng thư mục giao diện
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = "bao_smart_parking_pro_key"

cam_mgr = CameraManager()

def calculate_guest_fee(entry_time_str):
    try:
        time_in = datetime.strptime(entry_time_str, "%d/%m/%Y %H:%M:%S")
        now = datetime.now()
        duration = now - time_in
        hours = duration.total_seconds() / 3600.0
        
        if hours <= 8: return 5000
        else:
            extra_hours = hours - 8
            return 5000 + math.ceil(extra_hours) * 2000
    except Exception as e:
        print(f"[FEE ERROR] Lỗi tính phí: {e}")
        return 5000

@app.route("/")
def home():
    if "admin" in session: return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username, password = request.form.get("username", "").strip(), request.form.get("password", "").strip()
        if verify_admin(username, password):
            session["admin"] = username
            return redirect(url_for("dashboard"))
        error = "Tài khoản hoặc mật khẩu không chính xác!"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "admin" not in session: return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["admin"])

def gen_frames(gate_type):
    while True:
        frame = cam_mgr.get_frame_in() if gate_type == "in" else cam_mgr.get_frame_out()
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret: yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        else:
            time.sleep(0.1)

@app.route("/video_feed_in")
def video_feed_in(): return Response(gen_frames("in"), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/video_feed_out")
def video_feed_out(): return Response(gen_frames("out"), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- LOGIC CỔNG VÀO ---
@app.route("/api/gate_in", methods=["POST"])
def gate_in():
    data = request.get_json()
    rfid_uid = data.get("rfid_uid", "").strip().upper()
    card = find_card(rfid_uid)
    
    if card and card[4] == "Trong bãi":
        insert_log(rfid_uid, card[2], "GATE_IN", "denied", f"CẢNH BÁO: Thẻ {card[3]} đang ở trong bãi!", "")
        return jsonify({"allowed": False, "msg": "ERR_TRONG_BAI"})

    frame = cam_mgr.get_frame_in()
    ocr_text, annotated, warning, saved_path = "", None, "Không tìm thấy biển", ""
    
    if frame is not None:
        expected_plate = card[2] if card else ""
        ocr_text, annotated, warning = run_ocr(frame, expected_plate)
        saved_path = save_capture(annotated, f"IN_{rfid_uid}")
        
    if not ocr_text or ocr_text.strip() == "":
        insert_log(rfid_uid, "--", "GATE_IN", "denied", "LỖI: Không phát hiện biển số xe!", saved_path)
        return jsonify({"allowed": False, "msg": "ERR_KHONG_BIEN"})

    if card:
        db_plate = card[2]
        if ocr_text != db_plate:
            insert_log(rfid_uid, ocr_text, "GATE_IN", "denied", f"Sai biển! ĐK: {db_plate} | Cam: {ocr_text}", saved_path)
            return jsonify({"allowed": False, "msg": "ERR_SAI_BIEN"})
        save_card(rfid_uid, card[1], db_plate, card[3], "Trong bãi")
    else:
        save_card(rfid_uid, "Khách vãng lai", ocr_text, "VÉ LƯỢT", "Trong bãi")

    insert_log(rfid_uid, ocr_text, "GATE_IN", "allowed", f"AI đọc: {ocr_text}", saved_path)
    return jsonify({"allowed": True, "msg": f"INOK:{ocr_text}"})

# --- LOGIC CỔNG RA ---
@app.route("/api/gate_out", methods=["POST"])
def gate_out():
    data = request.get_json()
    rfid_uid = data.get("rfid_uid", "").strip().upper()
    card = find_card(rfid_uid)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT time_log, ocr_plate FROM logs WHERE rfid_uid=? AND gate_id='GATE_IN' AND result='allowed' ORDER BY id DESC LIMIT 1", (rfid_uid,))
    last_in = c.fetchone()
    conn.close()

    if not last_in:
        insert_log(rfid_uid, "--", "GATE_OUT", "denied", "LỖI: Xe chưa quét thẻ lối vào!", "")
        return jsonify({"allowed": False, "msg": "ERR_CHUA_VAO"})

    time_in_str = last_in[0]
    expected_plate = card[2] if card else last_in[1]

    frame = cam_mgr.get_frame_out()
    ocr_text, annotated, warning, saved_path = "", None, "Không tìm thấy biển", ""
    if frame is not None:
        ocr_text, annotated, warning = run_ocr(frame, expected_plate)
        saved_path = save_capture(annotated, f"OUT_{rfid_uid}")

    if not ocr_text or ocr_text.strip() == "":
        insert_log(rfid_uid, "--", "GATE_OUT", "denied", "LỖI: Không phát hiện xe lối ra!", saved_path)
        return jsonify({"allowed": False, "msg": "ERR_KHONG_BIEN"})

    if ocr_text != expected_plate:
        insert_log(rfid_uid, ocr_text, "GATE_OUT", "denied", f"Sai biển xe ra! Vào: {expected_plate} | Ra: {ocr_text}", saved_path)
        return jsonify({"allowed": False, "msg": "ERR_SAI_BIEN"})

    fee, is_guest = 0, True
    if card and card[3] != "VÉ LƯỢT":
        is_guest = False

    if is_guest:
        fee = calculate_guest_fee(time_in_str)
        delete_card(rfid_uid) 
    else:
        save_card(rfid_uid, card[1], card[2], card[3], "Hoạt động") 

    fee_str = f"{fee:,}đ" if fee > 0 else "0đ (Cư dân)"
    insert_log(rfid_uid, ocr_text, "GATE_OUT", "allowed", f"Hợp lệ | Thu: {fee_str}", saved_path)
    return jsonify({"allowed": True, "msg": f"OUTOK:{ocr_text}", "fee": fee})

@app.route("/api/card/scan_cam", methods=["GET"])
def api_scan_cam_for_reg():
    if "admin" not in session: return jsonify({"success": False, "msg": "Chưa đăng nhập"}), 401
    frame = cam_mgr.get_frame_in()
    if frame is None: return jsonify({"success": False, "msg": "Không lấy được hình từ Cam VÀO!"})
    ocr_text, _, _ = run_ocr(frame, "")
    if not ocr_text: return jsonify({"success": False, "msg": "AI không đọc được biển số!"})
    return jsonify({"success": True, "plate": ocr_text, "msg": f"Đã nhận diện: {ocr_text}"})

@app.route("/api/logs")
def api_logs(): return jsonify(get_latest_logs())

@app.route("/api/stats")
def api_stats(): return jsonify(get_stats())

@app.route("/api/cards")
def api_cards(): return jsonify(get_all_cards())

@app.route("/api/card/save", methods=["POST"])
def api_save_card():
    if "admin" not in session: return jsonify({"success": False, "msg": "Chưa đăng nhập"}), 401
    data = request.get_json()
    save_card(data.get("uid"), data.get("name"), data.get("plate"), data.get("type"), data.get("status"))
    return jsonify({"success": True, "msg": "Lưu thẻ thành công!"})

@app.route("/api/card/delete/<uid>", methods=["DELETE"])
def api_delete_card(uid):
    if "admin" not in session: return jsonify({"success": False, "msg": "Chưa đăng nhập"}), 401
    delete_card(uid)
    return jsonify({"success": True, "msg": "Xóa thẻ thành công!"})

@app.route("/api/log/delete/<int:log_id>", methods=["DELETE"])
def api_delete_log(log_id):
    if "admin" not in session: return jsonify({"success": False, "msg": "Chưa đăng nhập"}), 401
    delete_log(log_id)
    return jsonify({"success": True, "msg": "Đã xóa bản ghi!"})

@app.route("/api/log/clear", methods=["DELETE"])
def api_clear_logs():
    if "admin" not in session: return jsonify({"success": False, "msg": "Chưa đăng nhập"}), 401
    clear_all_logs()
    return jsonify({"success": True, "msg": "Đã dọn sạch lịch sử!"})

if __name__ == "__main__":
    os.makedirs(os.path.join(STATIC_DIR, "captures"), exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)