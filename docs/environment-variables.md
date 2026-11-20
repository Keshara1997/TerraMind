# Environment Variables

## 1. Introduction

This document describes the environment variables used to configure TERRAMIND.

Environment variables allow the application to use different settings for local development, testing, staging, and production without changing application source code.

TERRAMIND is designed to use environment variables for:

- Application configuration
- Database connections
- Redis connections
- Authentication and security
- Frontend API configuration
- Satellite data providers
- AI integrations
- Cloud storage
- Background processing
- Logging and monitoring

**Important:** The variables in this document describe the intended configuration. Actual variable names and requirements must match the application's configuration code and deployment files.

## 2. Environment Files

Different parts of the application may use separate environment files.

| File | Purpose |
|---|---|
| `.env` | Root-level local development configuration |
| `.env.example` | Example root environment configuration |
| `backend/.env` | Local backend configuration, if supported |
| `frontend/.env.local` | Local frontend configuration |
| `frontend/.env.local.example` | Example frontend configuration |

The application must explicitly load the environment file appropriate to its configuration.

Do not assume that every service automatically reads the root `.env` file.

## 3. Environment Types

Use separate configurations for each environment.

| Environment | Purpose |
|---|---|
| Development | Local development and debugging |
| Testing | Automated tests |
| Staging | Pre-production testing |
| Production | Live application |

Production credentials must never be copied into development or testing configuration files.

## 4. Application Variables

These variables control general application behavior.

| Variable | Description | Example |
|---|---|---|
| `APP_NAME` | Application name | `TERRAMIND` |
| `APP_ENV` | Application environment | `development` |
| `DEBUG` | Enables debugging | `true` |
| `API_V1_PREFIX` | API version prefix | `/api/v1` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `SECRET_KEY` | Application secret | Generate a secure random value |
| `FRONTEND_URL` | Frontend origin | `http://localhost:3000` |
| `BACKEND_URL` | Backend origin | `http://localhost:8000` |

### Example

```env
APP_NAME="TERRAMIND"
APP_ENV=development
DEBUG=true
API_V1_PREFIX=/api/v1
LOG_LEVEL=INFO
SECRET_KEY=replace-with-a-secure-random-secret
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

Use `DEBUG=false` in production.

## 5. Database Variables

TERRAMIND is designed to use PostgreSQL with PostGIS for spatial data.

| Variable | Description | Example |
|---|---|---|
| `POSTGRES_HOST` | Database hostname | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `POSTGRES_DB` | Database name | `aleph_next` |
| `POSTGRES_USER` | Database username | `aleph_user` |
| `POSTGRES_PASSWORD` | Database password | Secret value |
| `DATABASE_URL` | Full database connection URL | PostgreSQL connection string |

### Example

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aleph_next
POSTGRES_USER=aleph_user
POSTGRES_PASSWORD=replace-with-a-secure-password

DATABASE_URL=postgresql+psycopg://aleph_user:replace-with-a-secure-password@localhost:5432/aleph_next
```

The application may use either individual database variables or a complete connection URL. Avoid maintaining conflicting values.

### Docker networking

When the backend runs inside Docker Compose, the database hostname should normally be the PostgreSQL service name rather than `localhost`.

For example:

```env
POSTGRES_HOST=postgres
```

The actual service name must match `docker-compose.yml`.

## 6. Redis Variables

Redis is intended for caching, temporary data, and background task coordination.

| Variable | Description | Example |
|---|---|---|
| `REDIS_HOST` | Redis hostname | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_PASSWORD` | Redis password, if configured | Secret value |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |

### Example

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/0
```

If Redis authentication is enabled, configure the password securely.

When running inside Docker Compose, use the Redis service name as the hostname.

## 7. Authentication and Security Variables

These variables control authentication and token configuration.

| Variable | Description |
|---|---|
| `SECRET_KEY` | Secret used by application security functions |
| `JWT_SECRET_KEY` | JWT signing secret, if separately configured |
| `JWT_ALGORITHM` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime |
| `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` | Password reset token lifetime |

### Example

```env
JWT_SECRET_KEY=replace-with-a-secure-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=15
```

Use a cryptographically secure secret for signing tokens.

Do not reuse development secrets in production.

The algorithm and expiration settings must match the authentication implementation.

## 8. Frontend Variables

The Next.js application uses environment variables for frontend configuration.

Example file:

`frontend/.env.local`

| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |
| `NEXT_PUBLIC_MAP_STYLE_URL` | Map style URL, if configured | Provider-specific URL |

### Example

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAP_STYLE_URL=replace-with-your-map-style-url
```

Only expose values through the `NEXT_PUBLIC_` prefix when they are safe for browser access.

Never place the following in a `NEXT_PUBLIC_` variable:

- Database passwords
- JWT secrets
- AWS secret access keys
- OpenAI API keys
- Private provider credentials

These values can be included in frontend JavaScript bundles and accessed by users.

## 9. AI Integration Variables

AI integration may require provider configuration.

| Variable | Description |
|---|---|
| `AI_PROVIDER` | Selected AI provider |
| `OPENAI_API_KEY` | OpenAI API credential |
| `OPENAI_MODEL` | Configured model identifier |
| `AI_REQUEST_TIMEOUT` | Request timeout |
| `AI_MAX_RETRIES` | Maximum retry attempts |

### Example

```env
AI_PROVIDER=openai
OPENAI_API_KEY=replace-with-your-api-key
OPENAI_MODEL=replace-with-a-supported-model
AI_REQUEST_TIMEOUT=60
AI_MAX_RETRIES=3
```

Use a valid model identifier supported by the selected provider and application integration.

AI credentials must remain on the backend.

## 10. Satellite Data Provider Variables

Satellite data providers may require API credentials or endpoint configuration.

Possible variables include:

| Variable | Description |
|---|---|
| `EARTH_SEARCH_URL` | Earth Search API endpoint |
| `PLANETARY_COMPUTER_URL` | Planetary Computer endpoint |
| `SENTINEL_HUB_CLIENT_ID` | Sentinel Hub client ID, if used |
| `SENTINEL_HUB_CLIENT_SECRET` | Sentinel Hub client secret, if used |
| `STAC_REQUEST_TIMEOUT` | STAC request timeout |

### Example

```env
EARTH_SEARCH_URL=replace-with-the-configured-earth-search-endpoint
PLANETARY_COMPUTER_URL=replace-with-the-configured-planetary-computer-endpoint
STAC_REQUEST_TIMEOUT=60
```

Only configure credentials for providers actually used by the project.

Do not assume that every public STAC catalog requires authentication.

## 11. AWS and Cloud Storage Variables

AWS configuration may be required for object storage and production deployment.

| Variable | Description |
|---|---|
| `AWS_REGION` | AWS region |
| `AWS_ACCESS_KEY_ID` | AWS access key ID, if explicitly configured |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key, if explicitly configured |
| `AWS_STORAGE_BUCKET` | S3 bucket name |
| `AWS_S3_ENDPOINT_URL` | Optional S3-compatible endpoint |

### Example

```env
AWS_REGION=ap-south-1
AWS_STORAGE_BUCKET=replace-with-your-bucket-name
```

Prefer IAM roles and temporary credentials for AWS workloads running on AWS infrastructure.

Avoid hardcoding long-lived access keys in application environment files.

## 12. Background Worker Variables

Celery workers may use Redis as a broker and result backend.

| Variable | Description |
|---|---|
| `CELERY_BROKER_URL` | Message broker connection |
| `CELERY_RESULT_BACKEND` | Task result storage |
| `CELERY_TASK_TIME_LIMIT` | Maximum task execution time |
| `CELERY_TASK_SOFT_TIME_LIMIT` | Soft execution time limit |

### Example

```env
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_TASK_TIME_LIMIT=3600
CELERY_TASK_SOFT_TIME_LIMIT=3300
```

Ensure the worker and backend use compatible broker and result-backend configuration.

## 13. CORS Variables

Cross-Origin Resource Sharing controls which frontend origins can access the backend API from browsers.

An application may use a variable such as:

```env
CORS_ORIGINS=http://localhost:3000
```

For multiple origins, use the format expected by the backend settings implementation.

Production CORS configuration should contain only trusted application origins.

Avoid allowing every origin in production.

## 14. Example Environment File

The following is a reference example for the root `.env.example`.

Only retain variables that are supported by the actual application configuration.

```env
# Application
APP_NAME="TERRAMIND"
APP_ENV=development
DEBUG=true
API_V1_PREFIX=/api/v1
LOG_LEVEL=INFO

# Application security
SECRET_KEY=replace-with-a-secure-random-secret
JWT_SECRET_KEY=replace-with-a-secure-random-secret

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aleph_next
POSTGRES_USER=aleph_user
POSTGRES_PASSWORD=change-me
DATABASE_URL=postgresql+psycopg://aleph_user:change-me@localhost:5432/aleph_next

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/0

# Frontend and backend
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# CORS
CORS_ORIGINS=http://localhost:3000

# Authentication
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI
AI_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=

# Satellite data
STAC_REQUEST_TIMEOUT=60

# AWS
AWS_REGION=ap-south-1
AWS_STORAGE_BUCKET=

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

This file is a template, not a guarantee that every variable is currently implemented.

## 15. Generating Secure Secrets

Generate a random application secret using Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Generate separate secrets for application signing and JWT signing if the implementation uses separate keys.

Do not use the example values in a real deployment.

## 16. Environment Variable Security

Follow these security practices:

1. Never commit `.env` files containing credentials.
2. Keep `.env.example` free of real secrets.
3. Use separate secrets for development and production.
4. Restrict access to production credentials.
5. Prefer AWS IAM roles for AWS workloads.
6. Rotate credentials when they may have been exposed.
7. Do not log passwords, API keys, or access tokens.
8. Do not expose private keys through frontend variables.
9. Store production secrets in an appropriate secrets manager.
10. Review Git changes before committing configuration files.

## 17. Git Ignore Configuration

The root `.gitignore` should exclude local environment files and generated content.

Example:

```gitignore
# Environment files
.env
.env.*
!.env.example

# Python
venv/
.venv/
__pycache__/
*.py[cod]

# Node
node_modules/
.next/
out/

# Local storage and generated files
storage/datasets/
storage/temporary/
storage/exports/

# Logs
*.log

# IDE
.vscode/
.idea/
```

If frontend example files are needed, explicitly allow the appropriate example file in `.gitignore`.

Review existing ignore rules before replacing them.

## 18. Production Configuration

Production configuration should be managed separately from local development configuration.

Recommended practices:

- Set `APP_ENV=production`.
- Set `DEBUG=false`.
- Use managed database credentials.
- Use private networking for database and Redis access.
- Use IAM roles for AWS services.
- Configure trusted CORS origins.
- Use HTTPS.
- Store secrets in AWS Secrets Manager or another approved secret-management system.
- Avoid printing environment variables in deployment logs.

## 19. Implementation Status

This document provides a reference environment-variable catalogue.

Before using these variables:

1. Inspect backend settings and configuration code.
2. Inspect frontend environment-variable usage.
3. Review Docker Compose service definitions.
4. Review deployment configuration.
5. Remove variables that are not implemented.
6. Add missing variables required by actual services.
7. Keep `.env.example` synchronized with the documented configuration.

The application configuration is the source of truth for variable names, defaults, types, and required values.

---

**Document:** Environment Variables  
**Project:** TERRAMIND  
**Status:** Reference configuration / requires implementation verification