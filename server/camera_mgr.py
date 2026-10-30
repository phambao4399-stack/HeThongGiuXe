import cv2
import time

class CameraManager:
    def __init__(self):
        index_cam_vao = 1
        index_cam_ra = 2
        
        print(f"[CAM] Đang khởi tạo Camera Vào (Index {index_cam_vao})...")
        self.cam_in = cv2.VideoCapture(index_cam_vao, cv2.CAP_DSHOW)
        
        print(f"[CAM] Đang khởi tạo Camera Ra (Index {index_cam_ra})...")
        self.cam_out = cv2.VideoCapture(index_cam_ra, cv2.CAP_DSHOW)

        for name, cam in [("VÀO", self.cam_in), ("RA", self.cam_out)]:
            if cam.isOpened():
                cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                print(f"✅ Đã kết nối thành công Camera rời cổng [{name}]")
            else:
                print(f"❌ LỖI: Không thể mở luồng hình ảnh từ Camera [{name}]")

    def get_frame_in(self):
        if self.cam_in.isOpened():
            ret, frame = self.cam_in.read()
            if ret and frame is not None:
                return frame
        return None

    def get_frame_out(self):
        if self.cam_out.isOpened():
            ret, frame = self.cam_out.read()
            if ret and frame is not None:
                return frame
        return None 