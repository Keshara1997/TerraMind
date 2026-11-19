# Repository Structure

## 1. Purpose

This document describes the directory structure and organization of the TERRAMIND repository.

TERRAMIND is designed as a geospatial intelligence platform with a Next.js frontend, FastAPI backend, geospatial processing services, AI integrations, and cloud infrastructure.

The structure described here is the **target repository structure**. It is a reference for development and organization. The existence and implementation status of individual files must be verified against the actual repository.

## 2. Root Directory

```text
aleph-next/
├── .github/
├── backend/
├── frontend/
├── infrastructure/
├── docs/
├── scripts/
├── storage/
├── .dockerignore
├── .env
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
├── LICENSE
└── README.md
```

### Main directories

| Directory | Purpose |
|---|---|
| `.github/` | GitHub Actions workflows and repository automation |
| `backend/` | FastAPI application and backend services |
| `frontend/` | Next.js web application |
| `infrastructure/` | Docker, AWS, Nginx, and monitoring configuration |
| `docs/` | Project documentation |
| `scripts/` | Development, maintenance, and deployment scripts |
| `storage/` | Local datasets, temporary files, and generated exports |

### Root configuration files

| File | Purpose |
|---|---|
| `.env` | Local environment configuration; must not be committed |
| `.env.example` | Example environment variables without real secrets |
| `.gitignore` | Files and directories excluded from Git |
| `.dockerignore` | Files excluded from Docker build contexts |
| `.pre-commit-config.yaml` | Pre-commit checks and formatting |
| `docker-compose.yml` | Local development services |
| `docker-compose.prod.yml` | Production-oriented service configuration |
| `Makefile` | Common development and operational commands |
| `LICENSE` | Project license |
| `README.md` | Main project introduction and setup instructions |

## 3. Backend Structure

The backend is built with Python and FastAPI. It is responsible for API requests, authentication, business logic, database operations, geospatial processing, AI integration, and background jobs.

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── security/
│   ├── providers/
│   ├── geospatial/
│   ├── storage/
│   ├── workers/
│   ├── ai/
│   ├── mcp/
│   ├── monitoring/
│   └── integrations/
├── alembic/
│   └── versions/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── security/
├── .dockerignore
├── alembic.ini
├── Dockerfile
├── pyproject.toml
└── README.md
```

### 3.1 API endpoints

Location: `backend/app/api/v1/endpoints/`

API endpoint modules expose application functionality through REST APIs.

Expected modules:

```text
endpoints/
├── health.py
├── auth.py
├── users.py
├── organizations.py
├── organization_members.py
├── projects.py
├── areas.py
├── captures.py
├── datasets.py
├── stac.py
├── raster.py
├── analysis.py
├── change_detection.py
├── ai.py
├── agent.py
├── monitoring.py
├── reports.py
├── exports.py
└── audit_logs.py
```

### 3.2 Core configuration

Location: `backend/app/core/`

Contains application-wide configuration and shared functionality.

```text
core/
├── config.py
├── security.py
├── logging.py
├── exceptions.py
├── middleware.py
├── redis.py
└── constants.py
```

Responsibilities:

- Load application settings.
- Configure logging.
- Handle shared exceptions.
- Configure middleware.
- Manage Redis connections.
- Define shared constants.

### 3.3 Database

Location: `backend/app/database/`

```text
database/
├── base.py
├── session.py
└── init_db.py
```

Responsibilities:

- Configure SQLAlchemy.
- Create database sessions.
- Initialize database-related functionality.

Database migrations are managed separately through Alembic.

### 3.4 Models

Location: `backend/app/models/`

Contains SQLAlchemy database models.

Expected model modules:

```text
models/
├── user.py
├── auth_session.py
├── organization.py
├── organization_member.py
├── project.py
├── area.py
├── capture.py
├── data_source.py
├── dataset.py
├── agent_action.py
├── monitoring.py
├── environmental_alert.py
└── audit_log.py
```

### 3.5 Schemas

Location: `backend/app/schemas/`

Contains Pydantic request and response schemas.

Expected modules:

```text
schemas/
├── auth.py
├── user.py
├── organization.py
├── organization_member.py
├── project.py
├── area.py
├── capture.py
├── dataset.py
├── stac.py
├── raster.py
├── time_series.py
├── change_detection.py
├── ai.py
├── agent.py
├── monitoring.py
├── report.py
├── export.py
└── audit_log.py
```

### 3.6 Repositories

Location: `backend/app/repositories/`

Responsible for database access and query operations.

Expected modules:

```text
repositories/
├── user.py
├── organization.py
├── project.py
├── area.py
├── capture.py
├── dataset.py
├── agent_action.py
├── monitoring.py
└── audit.py
```

### 3.7 Services

Location: `backend/app/services/`

Contains application business logic.

Expected modules:

```text
services/
├── auth.py
├── user.py
├── organization.py
├── project.py
├── area.py
├── capture.py
├── dataset.py
├── stac.py
├── raster.py
├── time_series.py
├── change_detection.py
├── export.py
└── report.py
```

### 3.8 Security

Location: `backend/app/security/`

Responsible for access control and security-related functionality.

```text
security/
├── dependencies.py
├── permissions.py
├── organization_access.py
├── password.py
├── jwt.py
├── rate_limit.py
└── audit.py
```

### 3.9 Data providers

Location: `backend/app/providers/`

Contains integrations with external geospatial data providers.

```text
providers/
├── base.py
├── registry.py
├── earth_search.py
├── sentinel2.py
├── sentinel1.py
├── landsat.py
└── planetary_computer.py
```

### 3.10 Geospatial processing

Location: `backend/app/geospatial/`

Contains geospatial operations and processing algorithms.

```text
geospatial/
├── geometry.py
├── coordinates.py
├── spatial_queries.py
├── raster_processor.py
├── raster_utils.py
├── band_mapping.py
├── reflectance.py
├── cloud_mask.py
├── indices.py
├── ndvi.py
├── evi.py
├── savi.py
├── ndwi.py
├── nbr.py
├── change_detector.py
├── land_cover.py
├── classification.py
├── forecasting.py
└── risk_assessment.py
```

### 3.11 Storage

Location: `backend/app/storage/`

Responsible for storing and retrieving datasets and generated files.

```text
storage/
├── base.py
├── local_storage.py
├── s3_storage.py
└── storage_factory.py
```

### 3.12 Background workers

Location: `backend/app/workers/`

Contains background processing tasks.

```text
workers/
├── celery_app.py
├── capture_tasks.py
├── raster_tasks.py
├── change_tasks.py
├── classification_tasks.py
├── forecasting_tasks.py
├── report_tasks.py
└── monitoring_tasks.py
```

### 3.13 AI integration

Location: `backend/app/ai/`

Contains AI providers, analysis services, agent functionality, and safety controls.

```text
ai/
├── base.py
├── factory.py
├── openai_provider.py
├── context_builder.py
├── prompts.py
├── ai_analysis_service.py
├── anomaly_detector.py
├── agent.py
├── agent_context.py
├── agent_tools.py
├── agent_prompts.py
├── agent_guardrails.py
└── agent_service.py
```

### 3.14 MCP integration

Location: `backend/app/mcp/`

Contains Model Context Protocol integration.

```text
mcp/
├── config.py
├── api_client.py
├── server.py
├── prompts.py
├── test_client.py
└── test_tool_call.py
```

### 3.15 Monitoring and integrations

Locations:

- `backend/app/monitoring/`
- `backend/app/integrations/`

Expected monitoring modules:

```text
monitoring/
├── models.py
├── schemas.py
├── service.py
└── tasks.py
```

Expected integration modules:

```text
integrations/
├── email.py
├── notifications.py
└── external_apis.py
```

## 4. Frontend Structure

The frontend uses Next.js and TypeScript. It provides the user interface for maps, projects, datasets, analysis, AI tools, and organization management.

```text
frontend/
├── public/
│   ├── images/
│   ├── icons/
│   └── logo.svg
├── src/
│   ├── app/
│   ├── components/
│   ├── services/
│   ├── store/
│   ├── hooks/
│   ├── lib/
│   ├── providers/
│   └── types/
├── .dockerignore
├── .env.local.example
├── Dockerfile
├── next.config.ts
├── package.json
├── package-lock.json
├── tsconfig.json
├── eslint.config.mjs
└── README.md
```

### 4.1 Application routes

Location: `frontend/src/app/`

Expected route groups and pages:

```text
app/
├── auth/
├── dashboard/
├── projects/
├── map/
├── captures/
├── datasets/
├── analysis/
├── ai/
├── monitoring/
├── reports/
├── organizations/
├── settings/
└── audit-logs/
```

Use Next.js route conventions such as `page.tsx`, `layout.tsx`, and `loading.tsx` where appropriate.

### 4.2 Components

Location: `frontend/src/components/`

```text
components/
├── ui/
├── layout/
├── dashboard/
├── maps/
├── projects/
├── captures/
├── analysis/
├── ai/
├── monitoring/
├── organizations/
└── reports/
```

Responsibilities:

- `ui/`: Reusable interface elements.
- `layout/`: Navigation, headers, sidebars, and application layouts.
- `maps/`: Map views, layers, controls, and drawing tools.
- Other feature folders: Components specific to their application areas.

### 4.3 Supporting frontend modules

| Directory | Purpose |
|---|---|
| `services/` | API clients and backend communication |
| `store/` | Shared application state |
| `hooks/` | Reusable React hooks |
| `lib/` | Shared utilities and helper functions |
| `providers/` | React context and application providers |
| `types/` | Shared TypeScript types |

## 5. Infrastructure Structure

Location: `infrastructure/`

```text
infrastructure/
├── docker/
├── nginx/
├── aws/
│   ├── terraform/
│   ├── ecs/
│   └── scripts/
├── monitoring/
└── scripts/
```

| Directory | Purpose |
|---|---|
| `docker/` | Docker-related configuration |
| `nginx/` | Reverse proxy and web server configuration |
| `aws/terraform/` | Infrastructure as Code |
| `aws/ecs/` | ECS task and service configuration |
| `aws/scripts/` | AWS deployment and maintenance scripts |
| `monitoring/` | Monitoring and observability configuration |
| `scripts/` | Infrastructure automation |

## 6. GitHub Actions

Location: `.github/workflows/`

Expected workflows:

```text
workflows/
├── ci.yml
├── backend-tests.yml
├── frontend-tests.yml
├── security-scan.yml
└── production-deploy.yml
```

These workflows are intended to support:

- Code quality checks.
- Backend testing.
- Frontend testing.
- Security scanning.
- Production deployment.

## 7. Project Documentation

Location: `docs/`

```text
docs/
├── README.md
├── architecture.md
├── repository-structure.md
├── development-setup.md
├── environment-variables.md
├── docker-setup.md
├── database-schema.md
├── api-documentation.md
├── authentication.md
├── geospatial-processing.md
├── satellite-data-sources.md
├── raster-processing.md
├── ndvi-analysis.md
├── ai-integration.md
├── mcp-integration.md
├── monitoring.md
├── security.md
├── multi-tenancy.md
├── aws-deployment.md
├── backup-and-recovery.md
└── troubleshooting.md
```

Each document explains a specific part of the platform. Documentation should be updated when the corresponding implementation changes.

## 8. Local Storage

Location: `storage/`

```text
storage/
├── datasets/
├── temporary/
└── exports/
```

Purpose:

- `datasets/`: Local development datasets.
- `temporary/`: Temporary processing files.
- `exports/`: Generated reports and downloadable results.

Do not commit large datasets, private user data, credentials, or generated files to Git.

## 9. Naming Conventions

### Python

- Use `snake_case` for modules, functions, and variables.
- Use `PascalCase` for classes.
- Keep modules focused on a clear responsibility.

### TypeScript and React

- Use `PascalCase` for React component names.
- Use `camelCase` for functions and variables.
- Use descriptive names for hooks, typically starting with `use`.
- Use consistent naming for API services and TypeScript types.

### General

- Keep configuration files at the appropriate project or application level.
- Avoid duplicate implementations.
- Keep business logic out of route handlers where practical.
- Keep secrets outside version control.
- Prefer small, focused modules over large files with unrelated responsibilities.

## 10. Repository Organization Principles

1. Keep frontend and backend responsibilities separate.
2. Keep API endpoints focused on HTTP request and response handling.
3. Place reusable business logic in backend services.
4. Separate database access from business logic.
5. Keep geospatial algorithms in dedicated modules.
6. Isolate external provider integrations.
7. Use background workers for long-running processing tasks.
8. Keep tenant access checks centralized and consistent.
9. Keep tests organized by scope and purpose.
10. Update documentation as the project evolves.

## 11. Implementation Status

This document describes the intended organization of TERRAMIND.

The listed folders and files are not automatically considered implemented. Before creating or changing repository files:

1. Inspect the current repository.
2. Compare the actual structure with this reference.
3. Identify missing or differently named modules.
4. Confirm existing responsibilities before moving files.
5. Update this document when the agreed structure changes.

Do not create empty placeholder files simply to make the repository match this document.

---

**Document:** Repository Structure  
**Project:** TERRAMIND  
**Status:** Target structure / implementation requires verification