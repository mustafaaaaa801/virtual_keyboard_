# virtual_keyboard_
# Virtual Hand Keyboard — Pinch Press (Arabic README)

مشروع بسيط لكيبورد ظاهر فوق فيديو الكاميرا، يدعم:
- ضغط بالأصابع (pinch بين الإبهام والسبابة) لكتابة الأحرف.
- أيقونات برامج يمكن فتحها عند الضغط (مثال: Word، Calculator).
- مظهر جمالي للأزرار، زر DEL للحذف، وميزة حفظ النص في ملفات نصية.
- دعم يدين مع debounce لمنع الضغطة المتكررة.

---

## المتطلبات
- Python 3.10 أو 3.11 (موصى به).
- Windows / Linux (الكود يعتمد أوامر فتح برامج يمكن تعديلها حسب النظام).
- كاميرا متصلة.

---

## تجهيز بيئة (موصى به — Windows example)
افتح PowerShell أو CMD داخل مجلد المشروع ثم:

```powershell
# إنشاء بيئة افتراضية خاصة بالمشروع
py -3.11 -m venv venv_capture
venv_capture\Scripts\activate   # على Windows

# حدّث pip ثم ثبّت الحزم
python -m pip install --upgrade pip
pip install -r requirements.txt
مهم: هذه البيئة مخصصة لتشغيل MediaPipe + OpenCV.
إذا تريد استخدام TensorFlow لاحقًا (لتدريب/تشغيل نموذج AI)، أنشئ بيئة ثانية منفصلة لأن TensorFlow يطلب إصدارات مختلفة من numpy و protobuf.

تشغيل السكربت
بعد تفعيل البيئة:

powershell
نسخ
تحرير
python virtual_keyboard_pinch_with_icons_beautiful_save.py
ستفتح نافذة الكاميرا بواجهة الكيبورد.
إرشادات الاستخدام:

ضع يدك أمام الكاميرا.

مرّر رأس السبابة فوق زر ثم قرب الإبهام (pinch) — الزر سيُسجل.

أيقونة Save ستحفظ النص الحالي في مجلد saved_texts (اسم الملف يبدأ بـ typed_YYYYMMDD_HHMMSS.txt).

اضغط ESC للخروج.

تخصيص سريع
تغيير موقع الكيبورد:

عدِّل قيمة start_y عند استدعاء get_positions(...) داخل السكربت (مثلاً start_y=h//2 - 80).

تغيير حجم الأزرار:

عدّل button_w وbutton_h في get_positions(...).

تغيير حساسية الضغط:

PINCH_THRESHOLD_PX (قيمة أصغر = حساسية أعلى).

DEBOUNCE_DELAY (ثواني لمنع الضربات المتكررة).

إضافة/تعديل أيقونات برامج:

حرّر قائمة icons = [ (id, label, icon_path, cmd), ... ]

icon_path: مسار صورة (PNG أو JPG). قابلية الشفافية مدعومة.

cmd: مسار الـ .exe أو أمر نظامي (مثلاً "calc.exe") أو None لو تفعل زرًا داخليًا (مثل Save).

مجلدات وملفات مفيدة
saved_texts/ — يحتوي ملفات النص المحفوظة.

C:\Icons\ — مثال لمجلد الأيقونات؛ يمكنك وضع أيقوناتك وتعديل المسارات في السكربت.

مشاكل وحلول سريعة
لا تعمل الكاميرا؟

تأكد من أن كاميرا أخرى لا تستخدمها، جرّب cap = cv2.VideoCapture(0) وغيّر الرقم إن لزم.

ImportError / تعارض حزم (protobuf / numpy)

لا تمزج TensorFlow في نفس البيئة؛ أنشئ بيئة منفصلة عند الحاجة لتدريب/neural net.

إذا ظهر خطأ متعلقًا بـ protobuf أو numpy، أنشئ بيئة جديدة ونفّذ pip install -r requirements.txt.

الزركشة أو البطء

قلّل دقة الكاميرا (cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) و ..._HEIGHT, 480)).

أغلق البرامج الأخرى التي تستهلك CPU.

اقتراحات تحسين مستقبلية
تسجيل dataset عند كل ضغطة (حاليًا محفوظ نص فقط — يمكن حفظ صورة الإطار عند الضغط).

دعم gestures إضافية (رفع سبابة = Enter، حركة palm = مسح الشاشة).

تحويل الأزرار إلى HTML/JS لواجهة WebCam أكثر تفاعلية (باستخدام Electron أو Flask).

ترخيص (License)
ضع هنا ترخيص المشروع الذي تفضله، مثال:

nginx
نسخ
تحرير
MIT License
مثال لأوامر مفيدة (ملف batch)
batch
نسخ
تحرير
:: setup_env.bat
py -3.11 -m venv venv_capture
venv_capture\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
في حال واجهت أي مشاكل في الكود يرجى التواصل على الايميل mustafazamzamkazak@gmail.com
