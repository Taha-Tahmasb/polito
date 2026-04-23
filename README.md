<div align="center">

# 💼 Polito
### Portfolio Management System

سیستم حرفه‌ای مدیریت و تحلیل پورتفولیوی سرمایه‌گذاری

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192?style=for-the-badge&logo=postgresql&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)]()

</div>

---

## 📖 About

**Polito** یک سیستم مدیریت پورتفولیو سرمایه‌گذاری است که با **Django** توسعه داده شده و امکان مدیریت دارایی‌ها، ثبت تراکنش‌ها و تحلیل عملکرد سرمایه‌گذاری را فراهم می‌کند.

هدف این پروژه ارائه یک **نمونه‌کار حرفه‌ای Backend** با معماری تمیز، ماژولار و قابل توسعه است.

---

## ✨ Features

- 🔐 **Authentication System**
  - ثبت‌نام و ورود کاربران
  - مدیریت پروفایل

- 📊 **Portfolio Management**
  - ایجاد چندین پورتفولیو
  - مدیریت دارایی‌ها

- 💰 **Asset Tracking**
  - پشتیبانی از انواع دارایی
  - محاسبه سود و زیان

- 🔄 **Transaction System**
  - ثبت خرید و فروش
  - تاریخچه کامل تراکنش‌ها

- 📈 **Analytics**
  - تحلیل عملکرد پورتفولیو
  - نمودارهای آماری

- 🌐 **REST API**
  - API کامل برای ارتباط با سرویس‌های خارجی

---

## 🛠 Tech Stack

### Backend
- **Django**
- **Django REST Framework**
- **PostgreSQL**
- **Celery**
- **Redis**

### Frontend
- HTML
- CSS
- JavaScript
- Bootstrap
- Chart.js

### DevOps
- Docker
- GitHub Actions
- Gunicorn

---

## 🚀 Installation
```bash
# Clone repository
git clone https://github.com/Taha-Tahmasb/polito.git

cd polito

# Create virtual environment
python -m venv venv

# Linux / Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

### Environment Variables

bash
cp .env.example .env

سپس مقادیر مورد نیاز را در فایل `.env` تنظیم کنید.

### Database

bash
python manage.py migrate

### Create Admin User

bash
python manage.py createsuperuser

### Run Server

bash
python manage.py runserver

آدرس اجرا:


http://127.0.0.1:8000

---

## 📁 Project Structure


polito
│
├── config/                # Django settings
├── apps/
│   ├── accounts/          # User management
│   ├── portfolio/         # Portfolio logic
│   ├── analytics/         # Analytics & reports
│   └── market/            # Market data
│
├── templates/
├── static/
├── media/
│
├── requirements.txt
└── manage.py

---

## 🤝 Contributing

1. Fork کنید  
2. یک branch بسازید


git checkout -b feature/new-feature

3. تغییرات را commit کنید


git commit -m "add new feature"

4. push کنید


git push origin feature/new-feature

5. Pull Request ایجاد کنید

---

## 📝 License

این پروژه تحت لایسنس **MIT** منتشر شده است.

---

## 👨‍💻 Developer

**Taha Tahmasb**

GitHub  
https://github.com/Taha-Tahmasb

Project Repository  
https://github.com/Taha-Tahmasb/polito


اگر بخواهی می‌توانم یک نسخه **حتی حرفه‌ای‌تر مخصوص رزومه (سطح GitHub portfolio projects)** هم بسازم که شامل این‌ها باشد:

- architecture diagram  
- API documentation section  
- screenshots section  
- roadmap  
- badges حرفه‌ای‌تر  
- contribution graph friendly structure  

