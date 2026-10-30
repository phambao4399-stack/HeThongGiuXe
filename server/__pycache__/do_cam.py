import cv2

def do_tim_camera():
    print("--- ĐANG QUÉT CÁC CỔNG CAMERA KHẢ DỤNG ---")
    for i in range(5):
        # Thử mở camera với backend DirectShow (chuẩn trên Windows)
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"✅ Tìm thấy Camera hoạt động tại INDEX: [{i}] (Độ phân giải: {w}x{h})")
            # Chụp thử 1 frame để chắc chắn camera không bị đen
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"   -> Đã đọc thành công dữ liệu hình ảnh từ INDEX [{i}]")
            else:
                print(f"   -> ⚠️ Camera mở được nhưng khung hình bị đen/lỗi!")
            cap.release()
        else:
            print(f"❌ Không có thiết bị tại INDEX: [{i}]")

if __name__ == "__main__":
    do_tim_camera()