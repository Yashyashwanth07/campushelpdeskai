# 🎓 SmartCampus AI — Campus Helpdesk Portal

An AI-powered campus helpdesk web application where students can submit, track, and resolve complaints across departments. Built with Flask, SQLite, and integrated AI for smart categorization and response generation.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4-orange?logo=chartdotjs)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### 👤 Student Portal
- **Submit Complaints** — Report issues across 9+ campus departments (Hostel, Canteen, Library, Transport, etc.)
- **AI Suggestions** — Get real-time AI-powered tips while writing your complaint
- **Track Status** — Monitor complaint progress: Pending → In Progress → Resolved
- **File Attachments** — Upload images, PDFs, or documents as evidence
- **Delete Complaints** — Remove your own complaints (soft delete — admin can still view)

### 🛡️ Admin Dashboard
- **Analytics Overview** — Total complaints, resolution rate, urgent count, top department
- **Department Charts** — Visual breakdown with Chart.js bar and line graphs
- **AI Weekly Summary** — One-click AI-generated summary of weekly complaint trends
- **Smart Reply** — Generate AI-drafted professional responses, review/edit before sending
- **Search & Filter** — Filter complaints by department, status, or keyword
- **Status Management** — Update complaint status from the detail page

### 🤖 AI Capabilities
- **Sentiment Analysis** — Auto-detects urgency: 🔴 Urgent, 🟡 Neutral, 🟢 Positive
- **Auto-Categorization** — Routes complaints to the right department automatically
- **AI Reply Drafting** — Generates professional responses for admin to review
- **Smart Suggestions** — Suggests solutions to students as they type
- **Weekly Reports** — Summarizes complaint trends and provides recommendations

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.12, Flask 3.0 |
| **Database** | SQLite with Flask-SQLAlchemy |
| **Auth** | Flask-Login with password hashing |
| **Frontend** | Bootstrap 5.3, Custom CSS (Glassmorphism) |
| **Charts** | Chart.js 4.4 |
| **AI** | Together AI API |
| **Icons** | Bootstrap Icons |
| **Fonts** | Google Fonts (Inter) |

---

## 📁 Project Structure

```
campushelpdeskai/
├── app.py                  # Main Flask application & routes
├── models.py               # SQLAlchemy models (User, Complaint, Reply)
├── ai_helper.py            # AI integration (sentiment, categorize, reply, suggest)
├── config.py               # App configuration & API keys
├── requirements.txt        # Python dependencies
├── templates/
│   ├── base.html           # Base layout with navbar & footer
│   ├── index.html          # Landing page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── complaint_form.html # New complaint form with AI suggestions
│   ├── my_complaints.html  # Student complaints list
│   ├── complaint_detail.html # Complaint detail with reply thread
│   └── dashboard.html      # Admin analytics dashboard
└── static/
    ├── css/custom.css       # Custom styles (glass-card, animations)
    ├── js/main.js           # Chart.js, AJAX handlers, filters
    └── uploads/             # Uploaded attachments
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Yashyashwanth07/campushelpdeskai.git
cd campushelpdeskai

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app will start at **http://127.0.0.1:5000**

### Default Admin Account
| Email | Password |
|-------|----------|
| `admin@smartcampus.com` | `admin123` |

---

## 📸 Screenshots

### Landing Page
> Campus helpdesk portal with hero section and feature overview

### Admin Dashboard
> Analytics with department-wise charts, weekly trends, and complaint management

### Complaint Detail
> Threaded replies with AI-generated response drafting for admin

---

## 🔐 Roles & Permissions

| Feature | Student | Admin |
|---------|---------|-------|
| Submit Complaint | ✅ | ❌ |
| View Own Complaints | ✅ | ❌ |
| Delete Own Complaints | ✅ | ❌ |
| View All Complaints | ❌ | ✅ |
| Reply to Complaints | ❌ | ✅ |
| Update Status | ❌ | ✅ |
| AI Weekly Summary | ❌ | ✅ |
| Generate AI Reply | ❌ | ✅ |
| Dashboard Analytics | ❌ | ✅ |

---

## ⚙️ Configuration

Edit `config.py` to update:
- `SECRET_KEY` — Flask session secret
- `TOGETHER_API_KEY` — Your Together AI API key
- `TOGETHER_MODEL` — AI model to use
- `SQLALCHEMY_DATABASE_URI` — Database path

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">
  <b>SmartCampus AI</b> — Built with ❤️ for a smarter campus
</p>
