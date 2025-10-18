# DroitDraft Backend Setup Guide

This guide provides step-by-step instructions for setting up the backend development environment for DroitDraft.

## 1. Prerequisites

### 1.1. Python 3.9+

Ensure you have Python 3.9 or a later version installed. You can verify your installation by running:

```bash
python --version
```

If you don't have Python installed, download it from [python.org](https://www.python.org/downloads/).

### 1.2. System Dependencies

You'll need to install the following system-level dependencies:

*   **PostgreSQL Client:** Required for interacting with the PostgreSQL database.
*   **Tesseract OCR:** Required for Optical Character Recognition.

#### PostgreSQL Installation

**Windows:**
Download and run the installer from the [PostgreSQL website](https://www.postgresql.org/download/windows/).

**macOS (using Homebrew):**
```bash
brew install postgresql
```

**Linux (using apt):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### Tesseract OCR Installation

**Windows:**
Download and run the installer from the [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) page. Make sure to add the installation directory to your system's `PATH` environment variable.

**macOS (using Homebrew):**
```bash
brew install tesseract
```

**Linux (using apt):**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

## 2. Project Setup

### 2.1. Clone the Repository

```bash
git clone <your-repository-url>
cd droitdraft
```

### 2.2. Create a Virtual Environment

Navigate to the `backend` directory and create a Python virtual environment named `dd`.

```bash
cd backend
python -m venv dd
```

### 2.3. Activate the Virtual Environment

**Windows:**
```bash
dd\Scripts\activate
```

**macOS and Linux:**
```bash
source dd/bin/activate
```

### 2.4. Install Dependencies

With the virtual environment activated, install the required Python packages:

```bash
pip install -r requirements.txt
```

## 3. Database Setup

### 3.1. Local PostgreSQL Database

1.  Start the PostgreSQL service if it's not already running.
2.  Create a new database and user for DroitDraft. You can use `psql` or a graphical tool like pgAdmin.

    ```sql
    CREATE DATABASE droitdraft_dev;
    CREATE USER droitdraft_user WITH PASSWORD 'your_secure_password';
    GRANT ALL PRIVILEGES ON DATABASE droitdraft_dev TO droitdraft_user;
    ```

## 4. Environment Variables

1.  Navigate to the `backend` directory.
2.  Create a `.env` file by copying the example file:

    ```bash
    cp .env.example .env
    ```

3.  Open the `.env` file and fill in the required values for the database connection, API keys, and other settings.

## 5. Running the Application

Once the setup is complete, you can run the backend server:

```bash
# Ensure your virtual environment is activated
uvicorn main:app --reload
```

## 6. Docker Setup (Future Consideration)

For easier deployment and environment management, we will eventually use Docker. Here are some preliminary notes:

*   A `Dockerfile` will be created for the backend service.
*   `docker-compose.yml` will be used to orchestrate the backend, frontend, PostgreSQL, and ChromaDB services.
*   This will simplify setup by abstracting away the need to manually install dependencies like PostgreSQL and Tesseract.
