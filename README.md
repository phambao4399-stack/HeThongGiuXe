# DO AN 1: HE THONG BAI DO XE THONG MINH TICH HOP AI, IOT VA COMPUTER VISION

Day la tai lieu mo ta chi tiet cho he thong quan ly bai do xe tu dong, duoc phat trien trong khuon kho Do an 1 tai Truong Dai hoc Su pham Ky thuat TP.HCM (HCMUTE). Du an tap trung giai quyet bai toan khao sat, thiet ke kien truc va trien khai mot he thong kiem soat phuong tien vao/ra hoan toan tu dong.

Bang cach phoi hop chat che giua module vi dieu khien thu thap du lieu (Hardware/IoT) va server xu ly thi giac may tinh (AI/Computer Vision), he thong giup nang cao tinh bao mat, giam thieu tac dong cua con nguoi va toi uu hoa thoi gian xu ly tai cac tram kiem soat cua bai do xe.

## 1. TINH NANG KY THUAT CUA HE THONG

* **Nhan dien bien so xe tu dong (ANPR - Automatic Number Plate Recognition):** He thong co kha nang detect va extract ky tu tren bien so xe ngay ca trong dieu kien moi truong phuc tap. Giai phap nay ung dung cac mo hinh Deep Learning tien tien de dam bao do chinh xac cao nhat co the khi trich xuat text.

* **Xac thuc kep (Dual-Factor Authentication):** De nang cao bao mat, he thong yeu cau doi chieu dong thoi ID cua the RFID va chuoi ky tu bien so xe. Giai phap logic nay ngan chan triet de tinh trang su dung the gia hoac the bi danh cap de dua xe cua nguoi khac ra khoi bai.

* **Kiem soat luong giao thong doc lap (Dual-Gate Control):** Ho tro dieu khien dong thoi hai cong vao (Check-in) va ra (Check-out) rieng biet. Vi dieu khien se xu ly tin hieu da luong (multithreading hoac ngat - interrupt) de dieu khien hai dong co servo mot cach doc lap ma khong gay hien tuong blocking.

* **Giao tiep nguoi - may (HMI):** Hien thi trang thai he thong theo thoi gian thuc, cung cap thong bao chao mung, bao loi xac thuc hoac thong bao tu choi truy cap truc tiep tren man hinh LCD tai tung lane.

* **Luu tru va truy van du lieu Backend:** Cung cap cac RESTful API endpoints de luu log he thong (bao gom thoi gian vao/ra, hinh anh bien so duoc crop, trang thai the RFID) vao he quan tri co so du lieu quan he de de dang truy xuat, bao cao sau nay.

## 2. CONG NGHE VA NEN TANG TRIEN KHAI

### 2.1. Phan he Tri tue nhan tao (AI & Computer Vision)

* **YOLOv8 (You Only Look Once version 8):** Duoc su dung va tinh chinh (fine-tuning) tren tap du lieu bien so xe. Nhiem vu cua YOLOv8 la phat hien (object detection) va tra ve toa do khung bao (bounding box) cua bien so xe trong buc anh toan canh voi do tre thap nhat.

* **PaddleOCR:** Mo hinh nhan dien ky tu quang hoc (OCR) hieu suat cao ung dung kien truc CRNN. PaddleOCR xu ly anh bien so da duoc crop tu bounding box cua YOLO, co kha nang chong nhieu va nhan dien format bien so xe Viet Nam rat tot de tra ve chuoi text cuoi cung.

* **OpenCV:** Su dung de tien xu ly anh (image pre-processing) truoc khi dua qua cac mo hinh AI, bao gom viec chuyen doi khong gian mau (RGB to Grayscale), can bang do sang (Histogram Equalization) va giam nhieu (Noise reduction).

### 2.2. Phan he Phan cung va IoT

* **ESP32 DevKit:** Vi dieu khien trung tam, tich hop san module Wi-Fi. ESP32 chiu trach nhiem xu ly tin hieu tu cam bien, giao tiep voi HTTP Server qua giao thuc REST API (su dung HTTPClient) va dieu khien cac co cau chap hanh (actuators).

* **Module RFID RC522:** Hoat dong o tan so radio 13.56MHz, lam nhiem vu doc Unique ID (UID) cua the tu mifare va truyen du lieu ve ESP32 thong qua giao thuc truyen thong dong bo SPI.

* **Dong co Servo SG90:** Nhan tin hieu xung PWM tu cac chan cua ESP32 de mo/dong thanh chan barie tai cac lane.

* **Man hinh LCD 16x2 kem module I2C:** Hien thi text de huong dan nguoi dung. Ket noi voi ESP32 qua giao thuc I2C, giup tiet kiem dang ke so luong chan GPIO can su dung (chi can SDA va SCL).

### 2.3. Phan he Backend Server

* **Python Flask:** Web framework WSGI duoc su dung de xay dung cac API endpoints (chiu trach nhiem lang nghe POST/GET requests tu ESP32, khoi chay mo hinh AI va tinh toan logic nghiep vu).

* **SQLite:** He quan tri co so du lieu quan he serverless tich hop san trong thu vien chuan cua Python. Su dung cac bang (tables) de mapping thong tin quan he giua Nguoi dung (Users), The RFID (Cards) va Nhat ky ra vao (Parking Logs).

### 2.4. Ngon ngu lap trinh (Programming Languages)

* **Python (Phien ban 3.8+):** Day la ngon ngu chu dao de phat trien toan bo khoi server backend va he thong AI. Voi uu diem la he sinh thai thu vien phong phu, Python giup tich hop nhanh chong cac framework nhu Flask cho API, cung nhu xu ly ma tran anh phuc tap thong qua OpenCV va cac mo hinh Deep Learning (YOLOv8, PaddleOCR). Toan bo logic kiem tra dieu kien, doi chieu chuoi va ket noi database deu duoc thuc thi bang Python.

* **C/C++:** Ngon ngu bac thap duoc dung de viet firmware (ma nguon dieu khien) cho vi dieu khien ESP32. Viec su dung C/C++ tren moi truong Arduino IDE dam bao hieu suat thuc thi cao, kiem soat truc tiep cac thanh ghi, cap nhat trang thai ngat (interrupts) va tuong tac thoi gian thuc (real-time) voi cac thiet bi ngoai vi nhu the tu, man hinh LCD va dong co servo voi do tre phan cung gan nhu bang khong.

* **SQL (Structured Query Language):** Ngon ngu truy van mang tinh cau truc, duoc ung dung de thao tac voi co so du lieu SQLite. SQL duoc dung de tao cac bang (CREATE TABLE), them nhat ky ra vao (INSERT), va dac biet la thuc hien cac cau lenh SELECT de truy van, doi chieu UID cua the RFID voi thong tin bien so xe luu trong database mot cach toi uu.

## 3. KIEN TRUC VA LUONG XU LY DU LIEU (SYSTEM DATA FLOW)

### 3.1. Luong xu ly tai cong vao (Check-in Pipeline)

1. Nguoi dung dieu khien phuong tien vao lane va quet the RFID tren thiet bi doc RC522.

2. ESP32 doc UID cua the qua giao thuc SPI. Dong thoi camera (IP Camera hoac ESP32-CAM) se chup lai frame anh toan canh mat truoc cua phuong tien.

3. ESP32 dong goi UID va hinh anh (duoc ma hoa duoi dang Base64 hoac truyen qua binary multipart) de gui HTTP POST Request den Flask Backend Server.

4. Flask Server nhan request, boc tach hinh anh va dua vao pipeline: YOLOv8 (Detect & Crop) -> OpenCV (Pre-process) -> PaddleOCR (Text Extraction).

5. Backend Server kiem tra UID the co hop le khong. Neu hop le, no se map UID nay voi chuoi bien so xe vua nhan dien, dong thoi luu tru timestamp vao bang `CheckIn` trong SQLite.

6. Server tra ve HTTP Response voi Status Code 200 kem JSON payload xac nhan cap quyen (`status: success`).

7. ESP32 parse file JSON, xuat xung PWM mo dong co Servo cua barie cong vao va in dong chu "Welcome - Access Granted" len man hinh LCD.

### 3.2. Luong xu ly tai cong ra (Check-out Pipeline)

1. Nguoi dung tien den lane ra va thuc hien quet lai the RFID.

2. Qua trinh doc the, chup anh va truyen POST Request dien ra tuong tu nhu quy trinh tai cong vao.

3. Flask Server nhan request, thuc hien pipeline nhan dien de trich xuat ra bien so xe tai thoi diem ra.

4. He thong thuc hien query vao Database bang UID the de lay ra bien so xe da duoc luu tai thoi diem Check-in.

5. He thong tien hanh thuat toan doi chieu chuoi (String matching): Bien so nhan dien tai cong ra phai TRUNG KHOP (co the dung ty le giong nhau threshold > 90%) voi bien so luu tai cong vao cua chinh UID do.

6. Neu du lieu khop hoan toan: He thong cap nhat trang thai the trong DB thanh "Available", ghi nhan thoi gian Check-out, tinh toan chi phi (neu co) va tra ve tin hieu dong y xuyen qua API.

7. ESP32 nhan tin hieu, kich hoat Servo mo cong ra, hien thi "Goodbye" tren LCD.

8. Trong truong hop sai lech thong tin, ESP32 se giu nguyen trang thai dong cua barie, hien thi thong bao "Error: Unmatched Plate" tren LCD va co the kich hoat coi bao dong (Buzzer).

## 4. SO DO KET NOI PHAN CUNG (HARDWARE PINOUT MAPPING)

Viec ket noi giua ESP32 va cac thiet bi ngoai vi can tuan thu so do chan tieu chuan sau (co the thay doi tuy vao ma nguon firmware):

* **Ket noi voi Module RFID RC522 (Giao thuc SPI):**

  * SDA (SS) ket noi voi chan GPIO 5

  * SCK (SCLK) ket noi voi chan GPIO 18

  * MOSI ket noi voi chan GPIO 23

  * MISO ket noi voi chan GPIO 19

  * RST ket noi voi chan GPIO 4

  * 3.3V va GND ket noi voi nguon tuong ung tren ESP32.

* **Ket noi voi Man hinh LCD 16x2 I2C (Giao thuc I2C):**

  * SDA ket noi voi chan GPIO 21

  * SCL ket noi voi chan GPIO 22

  * VCC (5V) va GND ket noi voi nguon tuong ung.

* **Ket noi voi Dong co Servo SG90 (Xung PWM):**

  * Day tin hieu (Signal) cua Servo Cong Vao: GPIO 12

  * Day tin hieu (Signal) cua Servo Cong Ra: GPIO 13

  * VCC (5V) va GND noi voi nguon roi de tranh sut ap cho ESP32.

## 5. HUONG DAN TRIEN KHAI VA CAI DAT (DEPLOYMENT GUIDE)

### 5.1. Cai dat Moi truong Backend Server

1. Clone ma nguon cua he thong ve may tinh cuc bo thong qua Git.

2. Dam bao may tinh da cai dat Python phien ban 3.8 tro len. Khuyen nghi su dung Virtual Environment (`venv`) de tranh xung dot thu vien.

3. Kich hoat moi truong ao va chay lenh cai dat cac dependency tu file `requirements.txt`:
   `pip install -r requirements.txt`
   (Cac thu vien chinh se duoc tai ve bao gom: Flask, Ultralytics YOLO, PaddleOCR, OpenCV-python, SQLAlchemy, v.v.).

4. Khoi tao co so du lieu SQLite bang lenh script duoc cung cap trong thu muc `database`.

5. Run server bang lenh:
   `python app.py`
   Server se bat dau lang nghe cac ket noi den tai dia chi IP Local cua may tinh tren port 5000 (Vi du: `http://192.168.1.100:5000`).

### 5.2. Cai dat Firmware cho ESP32

1. Mo ma nguon phan cung (thu muc `firmware`) bang phan mem Arduino IDE.

2. Truy cap `Sketch -> Include Library -> Manage Libraries` de tai ve cac thu vien sau:

   * `MFRC522` (Ho tro giao tiep voi the tu).

   * `LiquidCrystal_I2C` (Ho tro xuat hinh anh dang text ra LCD).

   * `ESP32Servo` (Thay the cho thu vien Servo tieu chuan cua Arduino, tuong thich tot hon voi bo dinh thuyen thoi gian cua ESP32).

3. Trong file ma nguon `.ino`, can thay doi cac tham so mang bao gom: `SSID`, `PASSWORD` cua mang Wi-Fi dang su dung, va chuoi `SERVER_URL` tro ve dung dia chi IP cua may tinh dang chay Flask Server.

4. Ket noi board ESP32 vao may tinh, chon dung Port COM, chon Board la "DOIT ESP32 DEVKIT V1" va nhan nut Upload (co the can giu nut BOOT tren board trong qua trinh nap ma).

5. Mo Serial Monitor de kiem tra log khoi dong va kiem tra trang thai ket noi Wi-Fi.

## 6. TAC GIA VA THONG TIN DANG KY

* Du an duoc thuc hien boi sinh vien Khoa Dien - Dien tu / CNTT, Truong Dai hoc Su pham Ky thuat TP.HCM (HCMUTE).

* Hoc ky trien khai: Do an 1 - Thang 5/2024.

* Giay phep: Du an phat hanh theo giay phep MIT License. Cac ca nhan va to chuc co the su dung ma nguon nay vao muc dich hoc tap va nghien cuu mo rong ma khong bi rang buoc ve ban quyen thuong mai.
