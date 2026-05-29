# 🍽️ Smart Dine — QR-Based Smart Restaurant System

A full-featured **Django** restaurant management system with contactless QR ordering, real-time kitchen dashboard, waiter notifications, payment integration, and admin analytics.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📱 **QR Table Ordering** | Customers scan a QR code at their table and order directly |
| 🍳 **Live Kitchen Dashboard** | Real-time WebSocket-powered order queue for chefs |
| 🔔 **Waiter Notifications** | Instant alerts for waiters via Django Channels |
| 💳 **Razorpay Payments** | Integrated payment gateway for contactless billing |
| 📊 **Admin Analytics** | Sales, order trends, category stats, table management |
| 🧑‍🍳 **Role-based Access** | Admin / Chef / Waiter role separation |
| 🛒 **Session-based Cart** | No login required for customers to browse and order |

---

## 🛠️ Tech Stack

- **Backend** — Django 5, Django REST Framework, Django Channels (WebSockets)
- **Frontend** — Bootstrap 5, React 18 (CDN, no build step), Axios
- **Database** — SQLite (dev) / PostgreSQL (prod ready)
- **Payments** — Razorpay
- **Static Files** — WhiteNoise

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-restaurant.git
cd smart-restaurant
```

### 2. Create & activate virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your values
```

### 5. Run migrations & seed data
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Start the development server
```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000** 🎉

---

## 📁 Project Structure

```
smart-restaurant/
├── apps/
│   ├── accounts/        # Custom user model, login/signup
│   ├── menu/            # Dishes, categories, images
│   ├── orders/          # Cart, order placement, history
│   ├── kitchen/         # Chef dashboard (WebSocket)
│   ├── supplier/        # Waiter queue (WebSocket)
│   ├── payments/        # Razorpay integration
│   ├── admin_dashboard/ # Analytics, table & menu mgmt
│   └── notifications/   # Django Channels consumers
├── templates/           # HTML templates
├── static/              # CSS, JS assets
├── media/               # Uploaded dish images
├── restaurant_project/  # Django settings & URLs
└── requirements.txt
```

---

## 🔑 Default Roles

| Role | Access |
|---|---|
| **Admin** | Full dashboard, analytics, menu & table management |
| **Chef** | Kitchen order queue dashboard |
| **Waiter** | Waiter notification queue |
| **Customer** | Menu browsing & ordering (no login required) |

---

## 📸 Screenshots

> Add screenshots of your running app here

---

## 📄 License

MIT License — free to use and modify.
