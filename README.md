# DroitDraft - AI-Powered Legal Platform

DroitDraft is a state-of-the-art AI-powered legal document generation platform. This repository is a monorepo containing both the FastAPI backend and the Next.js frontend.

## Prerequisites

- **Docker**: For running the PostgreSQL database.
- **Python 3.9+**: For the backend.
- **Node.js 18+**: For the frontend.
- **Git**: For version control.

---

## 1. Database Setup (Docker)

The project uses PostgreSQL running in a Docker container.

1. **Start the database container**:
   ```powershell
   docker start postgres_db
   ```
   *(Ensure your Docker Desktop or daemon is running)*

2. **Database Permissions Fix** (Required for first-time setup or if migrations fail):
   ```powershell
   docker exec -it postgres_db psql -U droitdraft_user -d droitdraft_dev -c "GRANT ALL ON SCHEMA public TO droitdraft_user;"
   ```

---

## 2. Backend Setup

1. **Navigate to backend directory**:
   ```powershell
   cd backend
   ```

2. **Create and Activate Virtual Environment**:
   ```powershell
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   Create a `.env` file in the `backend/` directory from `.env.example`. Ensure your `DATABASE_URL` matches your local docker setup.

5. **Run the Backend Server**:
   ```powershell
   uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
   ```
   *The API will be available at `http://localhost:8002`*

---

## 3. Frontend Setup

1. **Navigate to frontend directory**:
   ```powershell
   cd frontend
   ```

2. **Install Dependencies**:
   ```powershell
   npm install
   ```

3. **Environment Configuration**:
   Ensure `frontend/.env.local` has the following:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8002
   ```

4. **Run the Frontend Server**:
   ```powershell
   npm run dev
   ```
   *The application will be available at `http://localhost:3001`*

---

## 4. Testing & Verification

- **API Documentation**: Visit `http://localhost:8002/docs` (Swagger UI).
- **Dashboard**: Visit `http://localhost:3001/dashboard`.
- **Sign In**: `http://localhost:3001/auth/signin`.

---

## Key Features Implemented

- **JWT Authentication**: Secure login and session management across frontend and backend.
- **AI Document Orchestrator**: Logic to generate legal clauses via LLMs.
- **Rich Text Editor**: Custom editor with auto-save and document persistence.
- **Legal Research Integration**: Connected to Indian Kanoon for legal references.