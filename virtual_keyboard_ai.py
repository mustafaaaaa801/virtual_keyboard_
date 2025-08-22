# virtual_keyboard_pinch_with_icons_beautiful_save.py
import cv2
import os
import time
import mediapipe as mp
import numpy as np
import subprocess
from datetime import datetime

# ---------- إعدادات عامة ----------
DEBOUNCE_DELAY = 0.6
PINCH_THRESHOLD_PX = 40

# مجلد حفظ النصوص
SAVED_TEXTS_DIR = "saved_texts"
os.makedirs(SAVED_TEXTS_DIR, exist_ok=True)

# ترتيب الأزرار مع زر حذف واضح (DEL)
keyboard_rows = [
    ["Q","W","E","R","T","Y","U","I","O","P"],
    ["A","S","D","F","G","H","J","K","L"],
    ["Z","X","C","V","B","N","M","SPACE","DEL"]
]

# ---------- أيقونات البرامج (عدل المسارات/الأوامر هنا) ----------
# أضفت أيقونة "save" لحفظ النص بدلاً من فتح برنامج.
icons = [
    ("word", "Word", r"C:\Icons\word.png", r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"),
    ("calc", "Calc", r"C:\Icons\calc.png", "calc.exe"),
    ("save", "Save", r"C:\Icons\save.png", None),  # زر حفظ النص - cmd=None يعني حفظ داخلي
]

# ------------ دوال رسم مساعدة لجمالية الأزرار ------------
def rounded_rect(img, x1, y1, x2, y2, color, radius=12, thickness=-1):
    """يرسم مستطيل بزوايا مدورة على img."""
    if thickness == -1:
        cv2.rectangle(img, (x1+radius, y1), (x2-radius, y2), color, -1)
        cv2.rectangle(img, (x1, y1+radius), (x2, y2-radius), color, -1)
        cv2.circle(img, (x1+radius, y1+radius), radius, color, -1)
        cv2.circle(img, (x2-radius, y1+radius), radius, color, -1)
        cv2.circle(img, (x1+radius, y2-radius), radius, color, -1)
        cv2.circle(img, (x2-radius, y2-radius), radius, color, -1)
    else:
        cv2.rectangle(img, (x1+radius, y1), (x2-radius, y2), color, thickness)
        cv2.rectangle(img, (x1, y1+radius), (x2, y2-radius), color, thickness)
        cv2.ellipse(img, (x1+radius, y1+radius), (radius, radius), 180, 0, 90, color, thickness)
        cv2.ellipse(img, (x2-radius, y1+radius), (radius, radius), 270, 0, 90, color, thickness)
        cv2.ellipse(img, (x1+radius, y2-radius), (radius, radius), 90, 0, 90, color, thickness)
        cv2.ellipse(img, (x2-radius, y2-radius), (radius, radius), 0, 0, 90, color, thickness)

def draw_button_beauty(overlay, x1,y1,x2,y2, base_color, highlight=False, pressed=False):
    """يرسم زر جميل مع ظل، حدود، ولمعان عند المرور والضغط."""
    shadow_col = (8,8,8)
    shadow_offset = 6
    rounded_rect(overlay, x1+shadow_offset, y1+shadow_offset, x2+shadow_offset, y2+shadow_offset, shadow_col, radius=12)

    top = tuple(int(c*0.95) for c in base_color)
    if highlight:
        top = tuple(min(255, int(c*1.25)) for c in base_color)
    rounded_rect(overlay, x1, y1, x2, y2, top, radius=12)

    border_col = tuple(min(255, int(c*1.4)) for c in base_color)
    rounded_rect(overlay, x1+2, y1+2, x2-2, y2-2, border_col, radius=10, thickness=2)

    if pressed:
        cx = (x1+x2)//2; cy = (y1+y2)//2
        cv2.circle(overlay, (cx, cy), min((x2-x1)//6, (y2-y1)//6), (230,230,230), -1)
        cv2.circle(overlay, (cx, cy), min((x2-x1)//6, (y2-y1)//6)-4, (20,20,20), 2)

def overlay_icon(overlay, icon_img, x1, y1, w, h):
    if icon_img is None: return
    ih, iw = icon_img.shape[:2]
    if iw == 0 or ih == 0: 
        return
    scale = min(w/iw, h/ih)
    new_w, new_h = int(iw*scale), int(ih*scale)
    icon_resized = cv2.resize(icon_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    ox = x1 + (w - new_w)//2
    oy = y1 + (h - new_h)//2
    if icon_resized.shape[2] == 4:
        alpha_s = icon_resized[:,:,3] / 255.0
        for c in range(3):
            overlay[oy:oy+new_h, ox:ox+new_w, c] = (alpha_s * icon_resized[:,:,c] + (1-alpha_s) * overlay[oy:oy+new_h, ox:ox+new_w, c])
    else:
        overlay[oy:oy+new_h, ox:ox+new_w] = icon_resized

# ------------ وظائف لوحة الأزرار والأيقونات ------------
def get_positions(frame_shape, keyboard_rows, center_x=None, start_y=None, button_w=88, button_h=68, gap_x=12, gap_y=14):
    h, w, _ = frame_shape
    if center_x is None:
        center_x = w // 2
    positions = {}
    for row_idx, row in enumerate(keyboard_rows):
        row_len = len(row)
        row_width = row_len * button_w + (row_len-1)*gap_x
        start_x = center_x - row_width//2
        y1 = start_y + row_idx * (button_h + gap_y)
        for col_idx, b in enumerate(row):
            x1 = start_x + col_idx * (button_w + gap_x)
            x2 = x1 + button_w
            y2 = y1 + button_h
            positions[b] = (x1, y1, x2, y2)
    return positions

def draw_keyboard_with_icons_beauty(frame, positions, icons_positions, icons_imgs, alpha=0.9, highlights=None, press_effect=None):
    overlay = frame.copy()
    if highlights is None: highlights = []

    for b, (x1,y1,x2,y2) in positions.items():
        base_color = (50,140,220)
        if b == "SPACE":
            base_color = (70,160,240)
        if b == "DEL":
            base_color = (200,70,70)
        highlight = (b in highlights)
        pressed = (press_effect and press_effect.get("button")==b)
        draw_button_beauty(overlay, x1,y1,x2,y2, base_color, highlight=highlight, pressed=pressed)

        cx = (x1+x2)//2
        cy = (y1+y2)//2 + 8
        label = b
        if b == "SPACE":
            label = "SPACE"
        font_scale = 0.95 if (x2-x1)>80 else 0.75
        color_text = (255,255,255)
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
        cv2.putText(overlay, label, (cx - text_size[0]//2, cy), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color_text, 2, cv2.LINE_AA)

    for key_id, (ix1,iy1,ix2,iy2) in icons_positions.items():
        r = (ix2-ix1)//2
        cx = (ix1+ix2)//2
        cy = (iy1+iy2)//2
        cv2.circle(overlay, (cx+4, cy+4), r+4, (10,10,10), -1)
        cv2.circle(overlay, (cx, cy), r, (40,40,40), -1)
        icon_img = icons_imgs.get(key_id)
        if icon_img is not None:
            overlay_icon(overlay, icon_img, ix1, iy1, ix2-ix1, iy2-iy1)
        else:
            cv2.putText(overlay, key_id[0].upper(), (cx-10, cy+8), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200,200,200), 2)

    # دمج بصيغة alpha
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

def compute_icons_positions(frame_shape, icons, center_x=None, start_y=None, icon_w=68, icon_h=68, gap=16):
    h, w, _ = frame_shape
    if center_x is None:
        center_x = w//2
    total_w = len(icons)*icon_w + (len(icons)-1)*gap
    if start_y is None:
        start_y = h - 220 - icon_h - 8
    start_x = center_x - total_w//2
    positions = {}
    x = start_x
    for key_id, label, icon_path, cmd in icons:
        positions[key_id] = (x, start_y, x+icon_w, start_y+icon_h)
        x += icon_w + gap
    return positions

def open_program(cmd):
    try:
        if isinstance(cmd, (list, tuple)):
            subprocess.Popen(cmd)
        else:
            if os.path.isfile(cmd):
                subprocess.Popen([cmd])
            else:
                subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print("خطأ في فتح البرنامج:", e)

# ------------ التحضير وMediaPipe والكاميرا ------------
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cv2.namedWindow("Virtual Keyboard - Beautiful", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Virtual Keyboard - Beautiful", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# إعداد أيقونات الصور محليًا
icons_imgs = {}
for key_id, label, icon_path, cmd in icons:
    if os.path.exists(icon_path):
        img = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)
        icons_imgs[key_id] = img
    else:
        icons_imgs[key_id] = None

# debounce dictionary (يشمل الأزرار والأيقونات)
all_buttons = [b for row in keyboard_rows for b in row] + [k[0] for k in icons]
last_pressed = {k: 0 for k in all_buttons}

typed_text = ""

# رسالة حفظ مؤقتة للـ toast
save_message = ""
save_message_time = 0.0
TOAST_DURATION = 1.6  # ثواني

def press_key(label):
    global typed_text
    if label == "SPACE":
        typed_text += " "
    elif label == "DEL":
        typed_text = typed_text[:-1] if typed_text else ""
    else:
        typed_text += label

def save_typed_text_to_file(text):
    """يحفظ النص في ملف نصي مع طابع زمني ويعرض رسالة مؤقتة"""
    global save_message, save_message_time
    if not text:
        save_message = "لا يوجد نص للحفظ"
        save_message_time = time.time()
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"typed_{ts}.txt"
    path = os.path.join(SAVED_TEXTS_DIR, fname)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        save_message = f"تم الحفظ: {fname}"
    except Exception as e:
        save_message = f"خطأ بالحفظ: {e}"
    save_message_time = time.time()

with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.6, min_tracking_confidence=0.6) as hands:
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # مواقع الأزرار والأيقونات: الآن اللوحة في منتصف الشاشة (كما طلبت)
        positions = get_positions(frame.shape, keyboard_rows, center_x=w//2, start_y=h//2 - 80, button_w=88, button_h=68, gap_x=12, gap_y=14)
        icons_positions = compute_icons_positions(frame.shape, icons, center_x=w//2, start_y=h//2 - 220, icon_w=68, icon_h=68, gap=18)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        highlights = []
        press_effect = None

        if res.multi_hand_landmarks:
            for hand_landmarks in res.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                ix = int(hand_landmarks.landmark[8].x * w)
                iy = int(hand_landmarks.landmark[8].y * h)
                tx = int(hand_landmarks.landmark[4].x * w)
                ty = int(hand_landmarks.landmark[4].y * h)

                cv2.circle(frame, (ix, iy), 6, (0,0,255), -1)
                cv2.circle(frame, (tx, ty), 5, (0,255,0), -1)

                pinch_dist = np.hypot(tx - ix, ty - iy)
                now = time.time()

                # فحص الأيقونات أولاً
                for key_id, (ix1,iy1,ix2,iy2) in icons_positions.items():
                    if ix1 < ix < ix2 and iy1 < iy < iy2:
                        highlights.append(key_id)
                        if pinch_dist < PINCH_THRESHOLD_PX and (now - last_pressed.get(key_id,0) > DEBOUNCE_DELAY):
                            # افتح البرنامج المرتبط أو احفظ النص إن كانت أيقونة save
                            for ik, label, icon_path, cmd in icons:
                                if ik == key_id:
                                    if ik == "save" or label.lower() == "save":
                                        # حفظ النص
                                        save_typed_text_to_file(typed_text)
                                    else:
                                        # فتح برنامج خارجي
                                        if cmd:
                                            open_program(cmd)
                                    last_pressed[key_id] = now
                                    press_effect = {"button": key_id}
                                    break
                        break

                # فحص أزرار الكيبورد
                for btn, (x1,y1,x2,y2) in positions.items():
                    if x1 < ix < x2 and y1 < iy < y2:
                        highlights.append(btn)
                        if pinch_dist < PINCH_THRESHOLD_PX and (now - last_pressed.get(btn,0) > DEBOUNCE_DELAY):
                            press_key(btn)
                            last_pressed[btn] = now
                            press_effect = {"button": btn}
                        break

        # رسم لوحة مفاتيح جميلة + أيقونات
        draw_keyboard_with_icons_beauty(frame, positions, icons_positions, icons_imgs, alpha=0.92, highlights=highlights, press_effect=press_effect)

        # عرض رسالة حفظ (toast) إن وُجدت
        if save_message and (time.time() - save_message_time) < TOAST_DURATION:
            # خلفية شبه شفافة للمساحة
            toast_w = 420
            toast_h = 44
            tx = (w - toast_w) // 2
            ty = 24
            overlay = frame.copy()
            rounded_rect(overlay, tx, ty, tx+toast_w, ty+toast_h, (20,120,20), radius=10)
            cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
            # نص الرسالة
            cv2.putText(frame, save_message, (tx+16, ty+30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        else:
            save_message = ""

        # عرض النص المكتوب وتعليمات
        cv2.putText(frame, "Pinch (thumb+index) to click. ESC to exit.", (40, h-34), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230,230,230), 2, cv2.LINE_AA)
        # عرض آخر 4 أسطر من النص (مقسومة)
        lines = []
        max_chars = 40
        txt = typed_text
        # simple wrap
        while txt:
            lines.append(txt[:max_chars])
            txt = txt[max_chars:]
        lines = lines[-4:]
        y_text = 40
        for line in lines:
            cv2.putText(frame, line, (40, y_text), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (245,245,245), 2, cv2.LINE_AA)
            y_text += 36

        cv2.imshow("Virtual Keyboard - Beautiful", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
