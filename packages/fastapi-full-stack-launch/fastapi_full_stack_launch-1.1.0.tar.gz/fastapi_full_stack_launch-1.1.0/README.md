# 🚀 FastAPI Full Stack Launch

A powerful CLI tool to scaffold production-ready full-stack projects with **FastAPI** backend and **React + Vite + TypeScript** frontend.

[![PyPI version](https://badge.fury.io/py/fastapi-full-stack-launch.svg)](https://pypi.org/project/fastapi-full-stack-launch/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 📁 **Full-Stack Project Structure** - Backend, frontend, and API proxy in one command
- ⚡ **Fast Setup** - Uses `uv` for lightning-fast Python package management
- ⚛️ **Modern Frontend** - React 18 + TypeScript + Vite
- 🐍 **Production Backend** - FastAPI with proper project structure

- 🔧 **Pre-configured Components**:
  - **Backend (FastAPI)**:
    - RESTful API Router (v1)
    - CORS configured for frontend
    - Environment config with python-dotenv
    - SQLAlchemy + MySQL Database Setup
    - Testing Framework
  - **Frontend (React + Vite)**:
    - TypeScript configured
    - ESLint setup
    - Hot Module Replacement


## 📋 Prerequisites

| Requirement | Version | Installation |
|-------------|---------|--------------|
| Python | 3.8+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| uv | Latest | See [Installing uv](#-installing-uv) |

## 📦 Installation

**Windows:**
```bash
pip install fastapi-full-stack-launch
```

**macOS / Linux:**
```bash
pip3 install fastapi-full-stack-launch
```

## 🛠️ Usage

Create a new full-stack project:

```bash
fastapi-full-stack-launch project <project_name>
```

**Example:**

```bash
fastapi-full-stack-launch project my-awesome-app
```

This generates a complete project structure:

```
my-awesome-app/
├── .venv/                    # Python virtual environment
├── backend/                  # Backend (FastAPI)
│   └── app/
│       ├── api/v1/
│       │   └── router.py
│       ├── core/
│       │   ├── config.py
│       │   └── logging.py
│       ├── db/
│       │   └── database.py
│       ├── models/
│       ├── schemas/
│       ├── services/
│       ├── tests/
│       ├── utils/
│       └── main.py
├── frontend/                 # Frontend (React + Vite + TypeScript)
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── index.html
├── .env                      # Environment configuration
├── .gitignore
├── pyproject.toml
└── README.md
```

## 🚀 Quick Start

After creating your project:

**Start the Backend:**

macOS / Linux:
```bash
cd my-awesome-app
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload
```

Windows:
```bash
cd my-awesome-app
.venv\Scripts\activate
cd backend
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

**Start the Frontend:**

```bash
cd my-awesome-app/frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

## ⚙️ Environment Configuration

The `.env` file in your project root contains:

```env
FASTAPI_APP_URL=http://localhost:8000
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/my-awesome-app_db
FRONTEND_URL=http://localhost:5173
```

## 📥 Installing uv

`uv` is required for backend scaffolding. Install it using:

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with ❤️ by <a href="https://whoiskrishi.vercel.app/">Krishi Devani</a>
</p>
