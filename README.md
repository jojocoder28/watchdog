# Watchdog: Intelligent Observability Platform

An enterprise-grade SRE observability platform with Apple-inspired design, automated anomaly detection, and Gemini-powered incident analysis.

## Features 🚀

- 💎 **Apple-Grade UI**: High-fidelity glassmorphism dashboard with fluid motion design and dark mode.
- 🧠 **AI-Powered Insights**: Automated incident summarization and root cause analysis using Gemini 2.5 Flash.
- 🔍 **Smart Ingestion**: Multi-format log parsing (.log, .csv, .json) with automated deduplication.
- 📈 **Anomaly Engine**: Multi-method detection (Thresholds, Z-Score, and Isolation Forest ML).
- 🔔 **Multi-Channel Alerts**: Simulated webhook dispatchers for Slack, Discord, and Email with exponential backoff.
- 🐳 **Docker Ready**: Fully containerized setup with multi-stage builds and Nginx reverse proxy.

## Tech Stack 🛠️

| Component | Technology |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS v4, TanStack Query, Recharts |
| **Backend** | FastAPI, SQLAlchemy, Pydantic v2, Python 3.11 |
| **AI/ML** | Google Gemini 2.5 Flash, Scikit-Learn (Isolation Forest) |
| **Database** | SQLite (Production-ready with Docker volumes) |
| **DevOps** | Docker, Docker Compose, Nginx, Makefile |

## Prerequisites 📋

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Google Gemini API Key

## Quick Start (Docker) 🐳

1. **Clone the repository**
2. **Setup environment**
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY to .env
   ```
3. **Spin up the platform**
   ```bash
   docker-compose up -d
   ```
4. **Access the platform**
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000/docs`

## Local Development Setup 💻

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Default Credentials 🔐

- **Operative Account**: Create any account via the /register page.
- **Admin Access**: Role-based access is available for SRE, DevOps, and Lead roles.

## Screenshot Placeholders 📸

![Dashboard Overview](https://via.placeholder.com/1200x600/0a0a0f/ffffff?text=Watchdog+Dashboard+Overview)
![Incident Triage](https://via.placeholder.com/1200x600/0a0a0f/ffffff?text=AI+Powered+Incident+Analysis)

## Project Structure 📁

```text
├── backend/            # FastAPI source code
├── frontend/           # React + TypeScript source code
├── docs/               # Detailed documentation
├── dataset/            # SQLite storage and simulated emails
├── docker/             # Nginx and container configs
└── docker-compose.yml  # Orchestration
```

## License 📄

MIT License - Copyright (c) 2026 Watchdog Team
