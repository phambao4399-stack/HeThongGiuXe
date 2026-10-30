import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parking.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS admins (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cards (rfid_uid TEXT PRIMARY KEY, owner_name TEXT, plate TEXT, card_type TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, time_log TEXT, rfid_uid TEXT, ocr_plate TEXT, gate_id TEXT, result TEXT, warning_flag TEXT, image_path TEXT)''')
    c.execute("INSERT OR IGNORE INTO admins VALUES ('admin', '123456')")
    conn.commit()
    conn.close()
    print(f"[DB] Database sẵn sàng tại: {DB_PATH}")

def verify_admin(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM admins WHERE username=? AND password=?", (username.strip(), password.strip()))
    user = c.fetchone()
    conn.close()
    return user is not None

def find_card(rfid_uid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE rfid_uid=?", (rfid_uid.strip(),))
    card = c.fetchone()
    conn.close()
    return card

def insert_log(rfid_uid, ocr_plate, gate_id, result, warning_flag, image_path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.execute("INSERT INTO logs (time_log, rfid_uid, ocr_plate, gate_id, result, warning_flag, image_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (now, rfid_uid, ocr_plate, gate_id, result, warning_flag, image_path))
    conn.commit()
    conn.close()

def get_latest_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, time_log, rfid_uid, ocr_plate, result, warning_flag, image_path, gate_id FROM logs ORDER BY id DESC LIMIT 15")
    rows = [{'id': r[0], 'time_in': r[1], 'rfid_uid': r[2], 'plate_in': r[3] if r[3] else "--", 'result': r[4], 'warning_flag': r[5], 'image_in_path': r[6], 'gate_id': r[7]} for r in c.fetchall()]
    conn.close()
    return rows

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    c.execute("SELECT COUNT(*) FROM logs WHERE gate_id='GATE_IN' AND time_log LIKE ?", (f"{today}%",))
    in_today = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM logs WHERE gate_id='GATE_OUT' AND time_log LIKE ?", (f"{today}%",))
    out_today = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM cards WHERE status='Trong bãi'")
    inside = c.fetchone()[0]
    
    conn.close()
    return {"inside": inside, "in_today": in_today, "revenue": out_today * 5000, "empty": max(0, 20 - inside)}

def get_all_cards():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT rfid_uid, owner_name, plate, card_type, status FROM cards")
    rows = [{"uid": r[0], "name": r[1], "plate": r[2], "type": r[3], "status": r[4]} for r in c.fetchall()]
    conn.close()
    return rows

def save_card(rfid_uid, owner_name, plate, card_type, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO cards (rfid_uid, owner_name, plate, card_type, status) VALUES (?, ?, ?, ?, ?)",
              (rfid_uid.strip().upper(), owner_name.strip(), plate.strip().upper(), card_type.strip(), status.strip()))
    conn.commit()
    conn.close()

def delete_card(rfid_uid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM cards WHERE rfid_uid=?", (rfid_uid.strip().upper(),))
    conn.commit()
    conn.close()

def delete_log(log_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM logs WHERE id=?", (int(log_id),))
    conn.commit()
    conn.close()

def clear_all_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM logs")
    conn.commit()
    conn.close()

init_db()