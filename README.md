# 🏦 QuickLoan - Agentic AI Loan Sales Assistant

An AI-powered loan sales assistant for Indian NBFCs that completes the entire loan journey in a single chat session.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18.2-blue?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-purple?logo=postgresql)

---

## ✨ Features

- 🤖 **Multi-Agent AI System** - Master, Sales, Verification & Underwriting agents
- 💬 **Human-like Conversations** - Natural language loan processing
- ⚡ **Instant Decisions** - Real-time credit evaluation
- 📄 **PDF Generation** - Automated sanction letter creation
- 🔐 **Secure Auth** - JWT + Email OTP verification
- 🎨 **Modern UI** - React + Tailwind + 3D animations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (Neon recommended)

### Installation

```bash
# Clone repository
git clone https://github.com/PranshuSharma14/Innovate-3.0.git
cd Innovate-3.0/NBFC-Loan-Approval

# Backend setup
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
cd ..
```

### Configuration

**Backend (.env):**
```env
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
JWT_SECRET=your_secret_key
OPENAI_API_KEY=sk-xxx  # Optional
```

**Frontend (frontend/.env):**
```env
VITE_EMAILJS_SERVICE_ID=your_service_id
VITE_EMAILJS_TEMPLATE_ID=your_template_id
VITE_EMAILJS_PUBLIC_KEY=your_public_key
VITE_EMAILJS_WELCOME_TEMPLATE_ID=your_welcome_template
```

### Run

```bash
# Terminal 1 - Backend
venv\Scripts\activate
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              Frontend (React)               │
└──────────────────────┬──────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────┐
│              Backend (FastAPI)              │
│  ┌─────────────────────────────────────┐    │
│  │           Master Agent              │    │
│  │  ┌───────────┬───────────┬───────┐  │    │
│  │  │   Sales   │Verification│Under- │  │    │
│  │  │   Agent   │   Agent   │writing│  │    │
│  │  └───────────┴───────────┴───────┘  │    │
│  └─────────────────────────────────────┘    │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│         PostgreSQL (Neon Serverless)        │
└─────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
NBFC-Loan-Approval/
├── app/
│   ├── agents/          # AI agents (master, sales, verification, underwriting)
│   ├── api/             # FastAPI routes (auth, chat, dummy_apis)
│   ├── database/        # Database models
│   ├── models/          # Pydantic schemas
│   ├── services/        # Business logic (PDF, AI)
│   └── utils/           # Helpers
├── frontend/
│   └── src/
│       ├── components/  # UI components
│       ├── pages/       # Login, Signup, Dashboard, Chat
│       └── context/     # Auth context
├── main.py              # Entry point
└── requirements.txt     # Dependencies
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register user |
| POST | `/api/auth/login` | Login + OTP |
| POST | `/api/auth/verify-login` | Verify OTP |
| POST | `/api/chat` | Chat with AI |
| GET | `/api/auth/me` | Get user info |

---

## ⚙️ External Services Setup

### EmailJS (for OTP)
1. Create account at [emailjs.com](https://www.emailjs.com/)
2. Create email service + OTP template
3. Template variables: `{{to_email}}`, `{{to_name}}`, `{{otp}}`, `{{purpose}}`

### Neon PostgreSQL
1. Create account at [neon.tech](https://neon.tech/)
2. Create project and copy connection string

---

## 📊 Loan Decision Logic

| Condition | Result |
|-----------|--------|
| Credit Score < 700 | ❌ Reject |
| Loan ≤ Pre-approved | ✅ Approve |
| Loan ≤ 2× Pre-approved | 📄 Need Salary Slip |
| EMI > 50% Salary | ❌ Reject |

---

## ⚠️ Disclaimer

This is a **demo project** for Innovate 3.0 Hackathon. Uses synthetic data only - no real transactions.

---

## 👨‍💻 Author

**Pranshu Sharma**

[![GitHub](https://img.shields.io/badge/GitHub-PranshuSharma14-black?logo=github)](https://github.com/PranshuSharma14)

---

<p align="center">Built with ❤️ for Innovate 3.0 Hackathon</p>