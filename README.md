🎥 Media Progress Tracker (Auto)
This is an automated progress tracking tool built with Python and Eel (to create a desktop application with a web-based UI). It records the time spent watching movies, series, or any media content by monitoring the currently active window title on your operating system.

✨ Features
Automated Tracking: Periodically captures the active window title and records the duration spent on that specific media.

Intelligent Title Parsing: Uses Regular Expressions (Regex) to extract the media name and, if available, the episode/season number from complex window titles (e.g., from VLC, browsers, etc.).

Blacklist Management: Allows the user to define keywords (like "Code Editor," "Terminal," "Settings") to ignore and prevent unwanted tracking of work or non-media applications.

Responsive UI: A modern, clean, and fully responsive user interface built with Tailwind CSS.

Persistent Storage: All progress and configuration data are stored locally in JSON files (media_data.json and tracker_config.json).

⚙️ How It Works (Technical Flow)
The application utilizes a two-part architecture: a Python backend handling the core logic and a Web frontend (HTML/CSS/JS) for the UI, linked via the Eel library.

Initialization: On startup, the Python script (1.py) loads the configuration and stored data, initializes Eel, and starts a background thread (auto_tracking_loop).

Window Polling: The background thread runs every 10 seconds (defined by AUTO_TRACKING_INTERVAL_SECONDS). In each cycle, it calls platform-specific functions (Windows, Linux, or generic fallback) to get the active window title.

Blacklist Check: The title is immediately checked against the user-defined blacklist_keywords. If a match is found, the cycle is skipped, and no time is recorded.

Media Identification: If the title passes the check, a Regex pattern is used to identify and isolate the Main Title and any Episode/Season information.

Progress Recording:

If the current title is the same as the title tracked in the previous cycle, the elapsed time (10 seconds) is calculated and added to the total time spent for that media entry in media_data.json.

If the current title is new, a new entry is created, and tracking begins from that moment.

UI Synchronization: After updating the data, the Python backend uses eel.expose and the corresponding JavaScript functions (eel.updateList, eel.updateStats) to send the updated data to the web interface in real-time. This ensures the user sees their progress instantly.

🚀 Installation and Setup
This guide assumes your main Python file is named 1.py and your UI files are in the web/ folder.

1. Prerequisites
You must have Python 3.x installed on your system.

2. Install Dependencies
Install all required modules using pip:

pip install eel pynput
# For Linux users, you might also need Xlib depending on your distribution:
# pip install python-xlib

3. Run the Application
Execute the Python script from your terminal:

python 1.py

A desktop window containing the tracking application UI will open.

🎥 ردیاب پیشرفت رسانه (خودکار)
این یک ابزار ردیابی پیشرفت خودکار است که با استفاده از پایتون و فریم‌ورک Eel (برای ساخت برنامه دسکتاپ با رابط کاربری وب) توسعه یافته است. این برنامه زمان صرف‌شده برای تماشای فیلم‌ها، سریال‌ها و هر محتوای رسانه‌ای را با نظارت بر عنوان پنجره فعال سیستم‌عامل شما ثبت می‌کند.

✨ ویژگی‌ها
ردیابی خودکار: عنوان پنجره فعال را به‌طور دوره‌ای ثبت کرده و مدت زمان صرف شده برای آن محتوای رسانه‌ای خاص را به سوابق اضافه می‌کند.

تجزیه عنوان هوشمند: از عبارت‌های باقاعده (Regex) برای استخراج نام اصلی محتوا و در صورت وجود، شماره قسمت/فصل از عناوین پیچیده پنجره‌ها (مانند پلیرها، مرورگرها و...) استفاده می‌کند.

مدیریت لیست سیاه: کاربر می‌تواند کلمات کلیدی خاصی (مانند "Code Editor"، "Terminal"، "Settings") را تعریف کند تا پنجره‌های مربوط به کار یا برنامه‌های غیررسانه‌ای را نادیده بگیرد.

رابط کاربری واکنش‌گرا: یک رابط کاربری مدرن، تمیز و کاملاً واکنش‌گرا که با Tailwind CSS ساخته شده است.

ذخیره‌سازی دائمی: تمامی پیشرفت‌ها و تنظیمات در فایل‌های JSON محلی (media_data.json و tracker_config.json) ذخیره می‌شوند.

⚙️ نحوه عملکرد (جریان فنی)
این برنامه از یک معماری دو بخشی استفاده می‌کند: بک‌اند پایتون که منطق اصلی را مدیریت می‌کند، و فرانت‌اند وب (HTML/CSS/JS) برای رابط کاربری، که از طریق کتابخانه Eel به هم متصل شده‌اند.

راه‌اندازی: در هنگام شروع، اسکریپت پایتون (1.py) تنظیمات و داده‌های ذخیره‌شده را بارگذاری می‌کند، Eel را مقداردهی اولیه کرده و یک ترد (Thread) پس‌زمینه (auto_tracking_loop) را شروع می‌کند.

نظرسنجی پنجره: ترد پس‌زمینه هر ۱۰ ثانیه (که توسط AUTO_TRACKING_INTERVAL_SECONDS تعریف شده) اجرا می‌شود. در هر چرخه، توابع خاص سیستم‌عامل (ویندوز، لینوکس یا عمومی) را فراخوانی می‌کند تا عنوان پنجره فعال را به دست آورد.

بررسی لیست سیاه: عنوان به دست آمده بلافاصله با blacklist_keywords تعریف شده توسط کاربر بررسی می‌شود. اگر مطابقت پیدا شود، چرخه نادیده گرفته شده و زمانی ثبت نمی‌شود.

شناسایی رسانه: اگر عنوان از بررسی لیست سیاه عبور کند، از یک الگوی Regex برای شناسایی و جداسازی عنوان اصلی و اطلاعات قسمت/فصل استفاده می‌شود.

ثبت پیشرفت:

اگر عنوان فعلی همان عنوانی باشد که در چرخه قبلی ردیابی شده، زمان سپری شده (۱۰ ثانیه) محاسبه شده و به کل زمان صرف‌شده برای آن محتوا در فایل media_data.json اضافه می‌شود.

اگر عنوان فعلی جدید باشد، یک ورودی جدید ایجاد می‌شود و ردیابی از آن لحظه شروع می‌شود.

همگام‌سازی رابط کاربری: پس از به‌روزرسانی داده‌ها، بک‌اند پایتون با استفاده از eel.expose و توابع جاوااسکریپت مربوطه (eel.updateList، eel.updateStats) داده‌های به‌روز شده را به‌صورت بی‌درنگ به رابط وب ارسال می‌کند تا کاربر فوراً پیشرفت خود را مشاهده کند.

🚀 نصب و راه‌اندازی
این راهنما فرض می‌کند که فایل اصلی پایتون شما 1.py و فایل‌های رابط کاربری شما در پوشه web/ قرار دارند.

۱. پیش‌نیازها
باید پایتون نسخه 3.x بر روی سیستم شما نصب باشد.

۲. نصب وابستگی‌ها
تمام ماژول‌های مورد نیاز را از طریق pip نصب کنید:

pip install eel pynput
# برای کاربران لینوکس، ممکن است به Xlib نیز نیاز داشته باشید:
# pip install python-xlib

۳. اجرای برنامه
اسکریپت پایتون را از ترمینال خود اجرا کنید:

python 1.py

پس از اجرا، یک پنجره دسکتاپ شامل رابط کاربری برنامه ردیابی باز خواهد شد.
