import argparse
import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

# --- Backend Templates ---

t_main = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import API_V1_STR, FRONTEND_URL

app = FastAPI(
    title="{project_name}",
    openapi_url=f"{API_V1_STR}/openapi.json"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to {project_name} API"}

@app.get("/health")
def health():
    return {"status": "healthy", "project": "{project_name}"}
'''

t_router_v1 = """
from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/")
def read_root():
    return {"message": "Hello from API v1"}

@api_router.get("/health")
def health_check():
    return {"status": "healthy"}
"""

t_config = '''
import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env'))

# API Version
API_V1_STR = "/api/v1"

# URLs from .env
FASTAPI_APP_URL = os.getenv("FASTAPI_APP_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/{project_name}_db")
'''

t_logging = """
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()
"""

t_database = """
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

# Create database engine using DATABASE_URL from .env
engine = create_engine(DATABASE_URL,echo=True)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

t_test = '''
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to {project_name} API"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
'''

gitignore_backend = """
__pycache__/
*.pyc
.env
.venv/
env/
venv/
*.db
.DS_Store
"""

# --- Environment File ---

t_root_env = """
FASTAPI_APP_URL=http://localhost:8000
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/{project_name}_db
FRONTEND_URL=http://localhost:5173
"""
# --- Root level templates ---

root_gitignore = """
# Backend
__pycache__/
*.pyc
.env
.venv/
env/
venv/
*.db
.DS_Store

# Frontend
node_modules/
dist/
*.local
*.log
"""

# --- Deployment Scripts ---

root_readme = """
# {project_name}

A full-stack application built with **FastAPI** (backend) and **React + Vite** (frontend).

## 📁 Project Structure

```
{project_name}/
├── backend/               # Backend (FastAPI)
│   └── app/
│       ├── api/v1/        # API routes
│       ├── core/          # Config & settings
│       ├── db/            # Database
│       ├── models/        # SQLAlchemy models
│       ├── schemas/       # Pydantic schemas
│       ├── services/      # Business logic
│       ├── tests/         # Backend tests
│       ├── utils/         # Utilities
│       └── main.py        # FastAPI app entry
├── frontend/              # Frontend (React + Vite)
│   ├── src/               # React source code
│   ├── public/            # Static assets
│   └── package.json       # Node dependencies
├── .gitignore
├── pyproject.toml
└── README.md
```

## 🚀 Getting Started

### Backend Setup

```bash
cd {project_name}

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\\Scripts\\activate

# Run the backend server (from project root)
cd backend
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd {project_name}/frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

Frontend runs at: `http://localhost:5173`

## 🔗 API Proxy

The frontend is configured to proxy `/api` requests to the backend. This means you can make API calls from the frontend like:

```typescript
fetch('/api/v1/health')
```

And it will automatically be proxied to `http://localhost:8000/api/v1/health`.

## 📄 License

MIT License
"""

# --- Logic ---

def create_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created: {path}")

def get_uv_install_instructions():
    """Return platform-specific uv installation instructions."""
    system = platform.system().lower()
    if system == "windows":
        return "powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\""
    else:
        return "curl -LsSf https://astral.sh/uv/install.sh | sh"

def check_uv_installed():
    """Check if uv is installed and provide helpful error messages."""
    if shutil.which("uv") is None:
        print("Error: 'uv' is not installed or not found in PATH.")
        print("\nTo install uv:")
        print(f"  {get_uv_install_instructions()}")
        print("\nAlternatively, you can install via pip (in a virtual environment):")
        print("  pip install uv")
        print("\nFor more info: https://docs.astral.sh/uv/getting-started/installation/")
        sys.exit(1)

def check_npm_installed():
    """Check if npm is installed."""
    if shutil.which("npm") is None:
        print("Warning: 'npm' is not installed. Frontend setup will be skipped.")
        print("Install Node.js from: https://nodejs.org/")
        return False
    return True

def run_command(cmd: list, cwd: Path = None, check: bool = True, capture: bool = True):
    """Run a command with cross-platform compatibility."""
    try:
        if capture:
            # Capture output (silent)
            if platform.system().lower() == "windows":
                result = subprocess.run(
                    cmd,
                    check=check,
                    cwd=cwd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    stdin=subprocess.DEVNULL
                )
            else:
                result = subprocess.run(
                    cmd,
                    check=check,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    stdin=subprocess.DEVNULL
                )
        else:
            # Show output in real-time
            if platform.system().lower() == "windows":
                result = subprocess.run(
                    cmd,
                    check=check,
                    cwd=cwd,
                    shell=True,
                    stdin=subprocess.DEVNULL
                )
            else:
                result = subprocess.run(
                    cmd,
                    check=check,
                    cwd=cwd,
                    stdin=subprocess.DEVNULL
                )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Error output: {e.stderr}")
        raise

def create_project(project_name: str, base_dir: Path):
    project_root = base_dir / project_name
    
    if project_root.exists():
        print(f"Error: Directory '{project_name}' already exists.")
        sys.exit(1)

    check_uv_installed()
    npm_available = check_npm_installed()

    print(f"🚀 Creating FastAPI Full Stack project '{project_name}'...")
    
    try:
        # 1. Initialize uv project
        print("\n📦 Initializing backend with uv...")
        run_command(["uv", "init", project_name], cwd=base_dir)
        
        # 2. Add backend dependencies
        print("📥 Adding backend dependencies...")
        dependencies = [
            "fastapi",
            "uvicorn",
            "pydantic-settings",
            "python-dotenv",
            "sqlalchemy"
        ]
        run_command(["uv", "add"] + dependencies, cwd=project_root)

    except subprocess.CalledProcessError as e:
        print(f"Error running uv command: {e}")
        if project_root.exists():
            shutil.rmtree(project_root)
        sys.exit(1)


    # Define backend file structure (in backend/app folder)
    backend_dir = project_root / "backend"
    app_dir = backend_dir / "app"
    
    backend_files = {
        # App Root
        app_dir / "__init__.py": "",
        app_dir / "main.py": t_main.replace("{project_name}", project_name),

        # API
        app_dir / "api" / "__init__.py": "",
        app_dir / "api" / "v1" / "__init__.py": "",
        app_dir / "api" / "v1" / "router.py": t_router_v1,

        # Core
        app_dir / "core" / "__init__.py": "",
        app_dir / "core" / "config.py": t_config.replace("{project_name}", project_name),
        app_dir / "core" / "logging.py": t_logging,

        # Database
        app_dir / "db" / "__init__.py": "",
        app_dir / "db" / "database.py": t_database,

        # Models
        app_dir / "models" / "__init__.py": "",

        # Schemas
        app_dir / "schemas" / "__init__.py": "",

        # Services
        app_dir / "services" / "__init__.py": "",

        # Tests
        app_dir / "tests" / "__init__.py": "",
        app_dir / "tests" / "test.py": t_test.replace("{project_name}", project_name),

        # Utils
        app_dir / "utils" / "__init__.py": "",
    }

    # Root level files
    root_files = {
        project_root / ".gitignore": root_gitignore,
        project_root / "README.md": root_readme.replace("{project_name}", project_name),
        project_root / ".env": t_root_env.strip().replace("{project_name}", project_name),
    }

    # Cleanup default uv files if present
    default_files_to_remove = ["hello.py", "main.py"]
    for filename in default_files_to_remove:
        default_file = project_root / filename
        if default_file.exists():
            default_file.unlink()

    # Create all files
    print("\n📁 Creating backend structure...")
    for path, content in backend_files.items():
        create_file(path, content)

    # Create frontend using npm create vite (non-interactive with --yes and --template)
    if npm_available:
        print("\n⚛️  Creating frontend with Vite...")
        try:
            # Use -y to skip npm prompts and --template react-ts for non-interactive vite setup
            # capture=False shows real-time output
            run_command(["npm", "create", "-y", "vite@latest", "frontend", "--", "--template", "react-ts"], cwd=project_root, capture=False)
            print("✅ Frontend created!")
            
            # Install frontend dependencies
            frontend_dir = project_root / "frontend"
            print("\n📥 Installing frontend dependencies...")
            run_command(["npm", "install"], cwd=frontend_dir, capture=False)
            print("✅ Frontend dependencies installed!")
        except subprocess.CalledProcessError:
            print("⚠️  Failed to create frontend. Run 'npm create vite@latest frontend -- --template react-ts' manually.")
    else:
        print("\n⚠️  npm not found. Skipping frontend creation.")
        print("   Run 'npm create vite@latest frontend -- --template react-ts' manually after installing Node.js.")


    print("\n📄 Creating root files...")
    for path, content in root_files.items():
        create_file(path, content)

    print("\n" + "=" * 50)
    print("✅ FastAPI Full Stack project created successfully!")
    print("=" * 50)
    
    print(f"\n📂 Project location: {project_root}")
    
    print("\n🔧 To start the BACKEND:")
    print(f"  cd {project_name}")
    print("  # Activate virtual environment:")
    print("  # macOS/Linux: source .venv/bin/activate")
    print("  # Windows:     .venv\\Scripts\\activate")
    print("  cd backend")
    print("  uvicorn app.main:app --reload")
    
    print("\n⚛️  To start the FRONTEND:")
    print(f"  cd {project_name}/frontend")
    if not npm_available:
        print("  npm install")
    print("  npm run dev")
    
    print("\n🌐 URLs:")
    print("  Backend:  http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    print("  Frontend: http://localhost:5173")

def main():
    parser = argparse.ArgumentParser(
        prog="fastapi-full-stack-launch",
        description="FastAPI Full Stack CLI - Create full-stack projects with FastAPI backend and React Vite frontend",
        epilog="Example: fastapi-full-stack-launch project my-awesome-project"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # 'project' subcommand
    project_parser = subparsers.add_parser(
        "project",
        help="Create a new full-stack project"
    )
    project_parser.add_argument(
        "project_name",
        help="Name of the project directory to create"
    )

    args = parser.parse_args()
    
    # Check if command is provided
    if args.command is None:
        parser.print_help()
        print("\n❌ Error: Please specify a command.")
        print("   Usage: fastapi-full-stack-launch project <project_name>")
        sys.exit(1)
    
    if args.command == "project":
        # Validate project name
        if not args.project_name.replace("-", "").replace("_", "").isalnum():
            print("Error: Project name should only contain letters, numbers, hyphens, and underscores.")
            sys.exit(1)
        
        create_project(args.project_name, Path.cwd())

if __name__ == "__main__":
    main()

