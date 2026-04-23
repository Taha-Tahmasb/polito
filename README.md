# 💼 Polito - Portfolio Management System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**سیستم مدیریت حرفه‌ای پورتفولیو سرمایه‌گذاری**

[نصب](#-نصب-و-راه‌اندازی) • [ویژگی‌ها](#-ویژگی‌ها) • [تکنولوژی](#-تکنولوژی) • [مستندات](#-مستندات)

</div>

---

## 📖 درباره پروژه

**Polito** یک سیستم مدیریت پورتفولیو سرمایه‌گذاری است که با Django توسعه یافته و امکان ردیابی دارایی‌های مالی، تحلیل عملکرد و مدیریت تراکنش‌ها را فراهم می‌کند.

این پروژه به عنوان یک نمونه کار حرفه‌ای برای نمایش مهارت‌های توسعه وب با Django طراحی شده است.

## ✨ ویژگی‌ها

- 🔐 **سیستم احراز هویت کامل** - ثبت‌نام، ورود و مدیریت پروفایل کاربری
- 📊 **مدیریت پورتفولیو** - ایجاد و مدیریت چندین پورتفولیو سرمایه‌گذاری
- 💰 **ردیابی دارایی‌ها** - پیگیری سهام، ارزهای دیجیتال و سایر دارایی‌ها
- 📈 **تحلیل عملکرد** - نمودارها و گزارش‌های تحلیلی
- 🔄 **مدیریت تراکنش‌ها** - ثبت خرید، فروش و انتقال دارایی‌ها
- 📱 **رابط کاربری ریسپانسیو** - سازگار با موبایل و تبلت
- 🌐 **API RESTful** - برای یکپارچه‌سازی با سرویس‌های خارجی

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها

- Python 3.11 یا بالاتر
- pip
- virtualenv (پیشنهادی)
- Git

### مراحل نصب
```bash
# 1. کلون کردن مخزن
git clone https://github.com/Taha-Tahmasb/polito.git
cd polito

# 2. ایجاد محیط مجازی
python -m venv venv

# فعال‌سازی در لینوکس/مک:
source venv/bin/activate

# فعال‌سازی در ویندوز:
venv\Scripts\activate

# 3. نصب وابستگی‌ها
pip install -r requirements.txt

# 4. تنظیمات محیطی
cp .env.example .env
# فایل .env را ویرایش کنید

# 5. مایگریشن دیتابیس
python manage.py migrate

# 6. ایجاد سوپریوزر
python manage.py createsuperuser

# 7. اجرای سرور توسعه
python manage.py runserver

پروژه روی `http://127.0.0.1:8000/` در دسترس خواهد بود.

## 🛠 تکنولوژی

### Backend
- **Django 5.0+** - فریمورک اصلی
- **Django REST Framework** - API Development
- **PostgreSQL** - پایگاه داده اصلی
- **Celery** - پردازش غیرهمزمان
- **Redis** - کش و صف پیام

### Frontend
- **HTML5 / CSS3**
- **JavaScript (ES6+)**
- **Bootstrap 5** - فریمورک UI
- **Chart.js** - نمودارها و تجسم داده

### DevOps
- **Docker** - کانتینریزیشن
- **GitHub Actions** - CI/CD
- **Gunicorn** - WSGI Server

## 📁 ساختار پروژه


polito/
├── config/              # تنظیمات اصلی Django
├── apps/
│   ├── accounts/        # مدیریت کاربران
│   ├── portfolio/       # مدیریت پورتفولیو
│   ├── analytics/       # تحلیل و گزارش‌گیری
│   └── market/          # داده‌های بازار
├── static/              # فایل‌های استاتیک
├── templates/           # قالب‌های HTML
├── media/               # فایل‌های آپلود شده
├── requirements.txt     # وابستگی‌های Python
└── manage.py

## 📚 مستندات

مستندات کامل API و راهنمای توسعه در پوشه `docs/` موجود است.

## 🤝 مشارکت

مشارکت‌ها، گزارش باگ‌ها و درخواست‌های ویژگی جدید همیشه خوش‌آمد هستند!

1. Fork کنید
2. برنچ ویژگی بسازید (`git checkout -b feature/AmazingFeature`)
3. تغییرات را commit کنید (`git commit -m 'Add some AmazingFeature'`)
4. Push کنید (`git push origin feature/AmazingFeature`)
5. Pull Request باز کنید

## 📝 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. فایل [LICENSE](LICENSE) را برای جزئیات بیشتر مطالعه کنید.

## 👨‍💻 توسعه‌دهنده

**Taha Tahmasb**

- GitHub: [@Taha-Tahmasb](https://github.com/Taha-Tahmasb)
- پروژه: [github.com/Taha-Tahmasb/polito](https://github.com/Taha-Tahmasb/polito)

---

<div align="center">
ساخته شده با ❤️ توسط Taha Tahmasb
</div>


این README شامل:
- بج‌های حرفه‌ای
- توضیحات کامل پروژه
- دستورات نصب با لینک مخزن تو
- لیست تکنولوژی‌ها
- ساختار پروژه
- بخش توسعه‌دهنده با لینک پروفایل GitHub تو

