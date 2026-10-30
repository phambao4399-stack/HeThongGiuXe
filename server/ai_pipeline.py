import cv2
import easyocr
import numpy as np
import os
import time
import re

print("[AI] Đang tải mô hình EasyOCR (Hỗ trợ Tiếng Việt)...")
reader = easyocr.Reader(['vi', 'en'], gpu=False)
print("[AI] Sẵn sàng!")

def clean_text(text: str) -> str:
    return re.sub(r'[^A-Z0-9Đ\-.]', '', text.upper())

def locate_plate_opencv(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 30, 200)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.03 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            if 0.8 <= (float(w)/h) <= 2.0 and w > 50: 
                return (x, y, x + w, y + h)
    return None

def run_ocr(image, db_plate=""):
    if image is None: return "", None, "No Image"
    annotated = image.copy()
    final_text, warning_msg = "", "Không tìm thấy biển"
    
    box = locate_plate_opencv(image)
    
    if box:
        x1, y1, x2, y2 = box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
        crop = image[y1:y2, x1:x2]
    else:
        crop = image  

    gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, thresh_crop = cv2.threshold(gray_crop, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    resized = cv2.resize(thresh_crop, (400, int(thresh_crop.shape[0]*(400/thresh_crop.shape[1]))))
    
    results = reader.readtext(resized, allowlist='0123456789ABCDEFGHKLMNPRSTUVXYZĐ-. ')
    
    items = []
    for (bbox, text, prob) in results:
        t = clean_text(text)
        if t: items.append({'t': t, 'x': (bbox[0][0]+bbox[1][0])/2, 'y': (bbox[0][1]+bbox[2][1])/2})
        
    if items:
        avg_y = sum(i['y'] for i in items)/len(items)
        l1 = sorted([i for i in items if i['y'] < avg_y], key=lambda x: x['x'])
        l2 = sorted([i for i in items if i['y'] >= avg_y], key=lambda x: x['x'])
        
        full_raw = "".join([i['t'] for i in l1]) + "".join([i['t'] for i in l2])
        cleaned = re.sub(r'[^A-Z0-9Đ]', '', full_raw)
        
        if len(cleaned) >= 8:
            if cleaned[:2].isdigit() and cleaned[2].isdigit() and not cleaned[3].isdigit():
                cleaned = cleaned[:2] + cleaned[3:]
            cleaned = cleaned.replace('MD', 'MĐ').replace('ND', 'MĐ')
            if 'NĐ' in cleaned:
                cleaned = cleaned.replace('NĐ', 'MĐ')
                
        final_text = cleaned[:10]
        warning_msg = f"AI đọc: {final_text}"
        
    return final_text, annotated, warning_msg

def save_capture(image, prefix):
    # 👉 ĐÃ SỬA: Lùi 2 cấp để ảnh lưu thẳng vào thư mục 'static/captures/' ở gốc project
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cap_dir = os.path.join(base_dir, "static", "captures")
    os.makedirs(cap_dir, exist_ok=True)
    fname = f"{prefix}_{int(time.time())}.jpg"
    cv2.imwrite(os.path.join(cap_dir, fname), image)
    return f"static/captures/{fname}"