# Development Setup

## 1. Introduction

This document explains how to configure a local development environment for TERRAMIND.

TERRAMIND is designed with the following technologies:

| Component | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Backend | Python, FastAPI |
| Database | PostgreSQL, PostGIS |
| Cache | Redis |
| Background processing | Celery |
| Containerization | Docker, Docker Compose |
| Geospatial processing | GDAL, Rasterio, GeoPandas |
| Map visualization | MapLibre GL JS |
| AI integration | OpenAI API |
| Cloud storage | AWS S3 |

The instructions target Windows 11 with Git Bash. Commands may need small adjustments for Linux or macOS.

**Important:** These instructions describe the intended development environment. Confirm the actual dependencies and configuration files in the repository before running commands.

## 2. Prerequisites

Install the following tools before starting development.

### 2.1 Git

Git is used for source code management.

Check the installation:

```bash
git --version
```

### 2.2 Python

The backend requires Python.

Check the installation:

```bash
python --version
```

A Python 3.12 environment is a suitable starting point, provided it is compatible with the project's dependency configuration.

### 2.3 Node.js and npm

The frontend requires Node.js and npm.

Check the installation:

```bash
node --version
npm --version
```

Use a Node.js version compatible with the frontend's `package.json` and Next.js version.

### 2.4 Docker Desktop

Docker is used to run application services in containers.

Check the installation:

```bash
docker --version
docker compose version
```

Make sure Docker Desktop is running before starting containers.

### 2.5 Code editor

Recommended editors:

- Visual Studio Code
- Cursor

Useful extensions include:

- Python
- Pylance
- ESLint
- Prettier
- Docker
- PostgreSQL
- GitLens

## 3. Verify the Repository

Open Git Bash and navigate to the project:

```bash
cd /d/Github/aleph-next
```

Check the current directory:

```bash
pwd
```

Check the Git status:

```bash
git status
```

Inspect the root directory:

```bash
ls -la
```

Confirm that the expected application directories exist:

```bash
ls backend
ls frontend
ls docs
```

Do not assume that every target directory already exists.

## 4. Backend Setup

The backend is intended to use FastAPI and Python.

### 4.1 Navigate to the backend

```bash
cd /d/Github/aleph-next/backend
```

### 4.2 Create a virtual environment

If the repository does not already contain a suitable virtual environment:

```bash
python -m venv venv
```

### 4.3 Activate the virtual environment

For Git Bash:

```bash
source venv/Scripts/activate
```

Verify Python:

```bash
python --version
```

### 4.4 Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4.5 Install backend dependencies

If the backend uses `requirements.txt`:

```bash
pip install -r requirements.txt
```

If the backend uses `pyproject.toml`, follow its configured dependency manager and installation instructions instead.

For a Poetry-managed project, for example:

```bash
pip install poetry
poetry install
```

Do not install dependencies from both files unless the project explicitly requires that.

### 4.6 Configure backend environment variables

Create a local environment file if the project provides an example:

```bash
cp .env.example .env
```

If no example exists, check the actual configuration implementation before creating one.

Update the values for your local database, Redis, authentication, and other required services.

Never commit real credentials or API keys.

### 4.7 Run database migrations

If Alembic is configured, inspect the current migration status:

```bash
alembic current
```

Apply migrations:

```bash
alembic upgrade head
```

Run these commands only after configuring and starting the database.

### 4.8 Start the backend

For a FastAPI application with an `app.main:app` entry point:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The entry-point module must match the actual backend structure.

Expected local API address:

```text
http://localhost:8000
```

If FastAPI documentation is enabled:

```text
http://localhost:8000/docs
```

## 5. Frontend Setup

The frontend is intended to use Next.js, React, and TypeScript.

### 5.1 Navigate to the frontend

Open another Git Bash terminal:

```bash
cd /d/Github/aleph-next/frontend
```

### 5.2 Install dependencies

If `package-lock.json` exists:

```bash
npm ci
```

Otherwise:

```bash
npm install
```

### 5.3 Configure environment variables

If `.env.local.example` exists:

```bash
cp .env.local.example .env.local
```

Update the backend API address and other required frontend settings.

For local development, the API address may look like:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

The actual variable name must match the frontend's API configuration.

Never place private API keys or server-only secrets in `NEXT_PUBLIC_` variables. These variables are exposed to the browser.

### 5.4 Start the frontend

```bash
npm run dev
```

Expected local frontend address:

```text
http://localhost:3000
```

## 6. Database and Redis Setup

TERRAMIND is designed to use PostgreSQL with PostGIS and Redis.

These services can be started through Docker Compose if the repository contains the corresponding service definitions.

From the repository root:

```bash
cd /d/Github/aleph-next
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

Check service logs:

```bash
docker compose logs
```

Check a specific service:

```bash
docker compose logs -f postgres
```

The service name `postgres` is an example. Use the actual service names from `docker-compose.yml`.

Do not start a second PostgreSQL or Redis instance if the required service is already running.

## 7. Running the Application

For local development, the intended workflow is:

1. Start PostgreSQL and PostGIS.
2. Start Redis.
3. Apply database migrations.
4. Start the FastAPI backend.
5. Start the Next.js frontend.
6. Verify API connectivity.
7. Test the main application features.

Keep the backend and frontend running in separate terminals when running them directly outside Docker.

## 8. Basic Verification

### 8.1 Verify backend availability

```bash
curl http://localhost:8000/
```

Use the actual health endpoint if the root endpoint is not configured:

```bash
curl http://localhost:8000/api/v1/health
```

### 8.2 Verify frontend availability

Open:

```text
http://localhost:3000
```

### 8.3 Verify Docker services

```bash
docker compose ps
```

### 8.4 Verify database migrations

From the backend directory:

```bash
alembic current
```

### 8.5 Verify frontend build

From the frontend directory:

```bash
npm run build
```

### 8.6 Verify backend tests

Use the configured test runner. If pytest is installed:

```bash
pytest
```

A successful startup does not necessarily mean all application features are working. Verify database access, authentication, API operations, and geospatial processing separately.

## 9. Development Workflow

Recommended workflow for each development task:

1. Pull the latest changes from the relevant Git branch.
2. Review the existing implementation.
3. Understand the affected modules.
4. Make the smallest required change.
5. Run relevant tests.
6. Check application logs.
7. Review the Git diff.
8. Commit the changes with a meaningful message.

Useful Git commands:

```bash
git status
git diff
git add .
git commit -m "Describe the change"
```

Avoid committing:

- `.env` files containing secrets.
- Virtual environments.
- `node_modules/`.
- Large temporary raster files.
- Generated datasets.
- Application logs.

## 10. Troubleshooting

### Python virtual environment is not activated

Run:

```bash
source venv/Scripts/activate
```

### Python dependencies cannot be installed

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Check that the active Python version is compatible with the project dependencies.

### npm dependencies fail

Remove and reinstall dependencies only if necessary:

```bash
npm install
```

Check the Node.js version and npm error output before deleting lockfiles or changing dependency versions.

### Docker services are unavailable

Check Docker Desktop and container status:

```bash
docker info
docker compose ps
```

### Backend cannot connect to PostgreSQL

Check:

- Database container status.
- Database host and port.
- Database name.
- Username and password.
- Backend environment variables.
- Docker network configuration.

When the backend runs inside Docker, `localhost` usually refers to the backend container itself, not the PostgreSQL container. Use the Compose service name as the database hostname.

### Frontend cannot connect to backend

Check:

- Backend availability.
- API base URL.
- CORS configuration.
- Frontend environment variables.
- Browser console errors.

### Port is already in use

Identify the process using the port and stop it safely, or configure the application to use another available port.

## 11. Development Guidelines

- Use the project's existing dependency versions.
- Keep local configuration separate from production configuration.
- Do not expose secrets through frontend environment variables.
- Use migrations for database schema changes.
- Add tests for new functionality.
- Validate geospatial outputs against known reference data.
- Document new environment variables and setup requirements.
- Keep development and production configurations separate.

## 12. Implementation Status

This guide describes the intended development workflow.

Before treating a command as verified, check that the relevant files, scripts, services, and application entry points exist in the repository.

Update this document whenever the development environment or dependency management process changes.

---

**Document:** Development Setup  
**Project:** TERRAMIND  
**Status:** Development guide / commands require repository verification