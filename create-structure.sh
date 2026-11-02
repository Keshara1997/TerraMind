
#!/usr/bin/env bash

set -e

echo "Creating TerraMind project structure..."

# GitHub workflows
mkdir -p .github/workflows

# Backend directories
mkdir -p backend/app/api/v1/endpoints
mkdir -p backend/app/core
mkdir -p backend/app/database
mkdir -p backend/app/models
mkdir -p backend/app/schemas
mkdir -p backend/app/repositories
mkdir -p backend/app/services
mkdir -p backend/app/security
mkdir -p backend/app/providers
mkdir -p backend/app/geospatial
mkdir -p backend/app/storage
mkdir -p backend/app/workers
mkdir -p backend/app/ai
mkdir -p backend/app/mcp
mkdir -p backend/app/monitoring
mkdir -p backend/app/integrations

mkdir -p backend/alembic/versions
mkdir -p backend/tests/unit
mkdir -p backend/tests/integration
mkdir -p backend/tests/security

# Frontend directories
mkdir -p frontend/public/images
mkdir -p frontend/public/icons

mkdir -p "frontend/src/app/(auth)/login"
mkdir -p "frontend/src/app/(auth)/register"
mkdir -p "frontend/src/app/(auth)/forgot-password"

mkdir -p "frontend/src/app/(dashboard)/dashboard"
mkdir -p "frontend/src/app/(dashboard)/projects/[projectId]"
mkdir -p "frontend/src/app/(dashboard)/map"
mkdir -p "frontend/src/app/(dashboard)/captures"
mkdir -p "frontend/src/app/(dashboard)/datasets"
mkdir -p "frontend/src/app/(dashboard)/analysis/time-series"
mkdir -p "frontend/src/app/(dashboard)/analysis/change-detection"
mkdir -p "frontend/src/app/(dashboard)/ai"
mkdir -p "frontend/src/app/(dashboard)/monitoring"
mkdir -p "frontend/src/app/(dashboard)/reports"
mkdir -p "frontend/src/app/(dashboard)/organizations/[organizationId]"
mkdir -p "frontend/src/app/(dashboard)/settings"
mkdir -p "frontend/src/app/(dashboard)/audit-logs"

mkdir -p frontend/src/components/ui
mkdir -p frontend/src/components/layout
mkdir -p frontend/src/components/dashboard
mkdir -p frontend/src/components/maps
mkdir -p frontend/src/components/projects
mkdir -p frontend/src/components/captures
mkdir -p frontend/src/components/analysis
mkdir -p frontend/src/components/ai
mkdir -p frontend/src/components/monitoring
mkdir -p frontend/src/components/organizations
mkdir -p frontend/src/components/reports

mkdir -p frontend/src/services
mkdir -p frontend/src/store
mkdir -p frontend/src/hooks
mkdir -p frontend/src/lib
mkdir -p frontend/src/providers
mkdir -p frontend/src/types

# Infrastructure
mkdir -p infrastructure/docker
mkdir -p infrastructure/nginx/conf.d
mkdir -p infrastructure/aws/terraform
mkdir -p infrastructure/aws/ecs
mkdir -p infrastructure/aws/scripts
mkdir -p infrastructure/monitoring/grafana/dashboards
mkdir -p infrastructure/scripts

# Documentation
mkdir -p docs

# Scripts
mkdir -p scripts

# Storage
mkdir -p storage/datasets
mkdir -p storage/temporary
mkdir -p storage/exports

# Helper function
create_files() {
    for file in "$@"; do
        touch "$file"
    done
}

# GitHub workflows
create_files \
.github/workflows/ci.yml \
.github/workflows/backend-tests.yml \
.github/workflows/frontend-tests.yml \
.github/workflows/security-scan.yml \
.github/workflows/production-deploy.yml

# Backend Python files
create_files \
backend/app/__init__.py \
backend/app/main.py \
backend/app/api/__init__.py \
backend/app/api/v1/__init__.py \
backend/app/api/v1/router.py \
backend/app/api/v1/endpoints/__init__.py \
backend/app/api/v1/endpoints/health.py \
backend/app/api/v1/endpoints/auth.py \
backend/app/api/v1/endpoints/users.py \
backend/app/api/v1/endpoints/organizations.py \
backend/app/api/v1/endpoints/organization_members.py \
backend/app/api/v1/endpoints/projects.py \
backend/app/api/v1/endpoints/areas.py \
backend/app/api/v1/endpoints/captures.py \
backend/app/api/v1/endpoints/datasets.py \
backend/app/api/v1/endpoints/stac.py \
backend/app/api/v1/endpoints/raster.py \
backend/app/api/v1/endpoints/analysis.py \
backend/app/api/v1/endpoints/change_detection.py \
backend/app/api/v1/endpoints/ai.py \
backend/app/api/v1/endpoints/agent.py \
backend/app/api/v1/endpoints/monitoring.py \
backend/app/api/v1/endpoints/reports.py \
backend/app/api/v1/endpoints/exports.py \
backend/app/api/v1/endpoints/audit_logs.py

create_files \
backend/app/core/__init__.py \
backend/app/core/config.py \
backend/app/core/security.py \
backend/app/core/logging.py \
backend/app/core/exceptions.py \
backend/app/core/middleware.py \
backend/app/core/redis.py \
backend/app/core/constants.py

create_files \
backend/app/database/__init__.py \
backend/app/database/base.py \
backend/app/database/session.py \
backend/app/database/init_db.py

create_files \
backend/app/models/__init__.py \
backend/app/models/user.py \
backend/app/models/auth_session.py \
backend/app/models/organization.py \
backend/app/models/organization_member.py \
backend/app/models/project.py \
backend/app/models/area.py \
backend/app/models/capture.py \
backend/app/models/data_source.py \
backend/app/models/dataset.py \
backend/app/models/agent_action.py \
backend/app/models/monitoring.py \
backend/app/models/environmental_alert.py \
backend/app/models/audit_log.py

create_files \
backend/app/schemas/__init__.py \
backend/app/schemas/common.py \
backend/app/schemas/auth.py \
backend/app/schemas/user.py \
backend/app/schemas/organization.py \
backend/app/schemas/organization_member.py \
backend/app/schemas/project.py \
backend/app/schemas/area.py \
backend/app/schemas/capture.py \
backend/app/schemas/dataset.py \
backend/app/schemas/stac.py \
backend/app/schemas/raster.py \
backend/app/schemas/time_series.py \
backend/app/schemas/change_detection.py \
backend/app/schemas/ai.py \
backend/app/schemas/agent.py \
backend/app/schemas/monitoring.py \
backend/app/schemas/report.py \
backend/app/schemas/export.py \
backend/app/schemas/audit_log.py

create_files \
backend/app/repositories/__init__.py \
backend/app/repositories/user_repository.py \
backend/app/repositories/organization_repository.py \
backend/app/repositories/project_repository.py \
backend/app/repositories/area_repository.py \
backend/app/repositories/capture_repository.py \
backend/app/repositories/dataset_repository.py \
backend/app/repositories/agent_action_repository.py \
backend/app/repositories/monitoring_repository.py \
backend/app/repositories/audit_repository.py

create_files \
backend/app/services/__init__.py \
backend/app/services/auth_service.py \
backend/app/services/user_service.py \
backend/app/services/organization_service.py \
backend/app/services/project_service.py \
backend/app/services/area_service.py \
backend/app/services/capture_service.py \
backend/app/services/dataset_service.py \
backend/app/services/stac_service.py \
backend/app/services/raster_service.py \
backend/app/services/time_series_service.py \
backend/app/services/change_detection_service.py \
backend/app/services/export_service.py \
backend/app/services/report_service.py

create_files \
backend/app/security/__init__.py \
backend/app/security/dependencies.py \
backend/app/security/permissions.py \
backend/app/security/organization_access.py \
backend/app/security/password.py \
backend/app/security/jwt.py \
backend/app/security/rate_limit.py \
backend/app/security/audit.py

create_files \
backend/app/providers/__init__.py \
backend/app/providers/base.py \
backend/app/providers/registry.py \
backend/app/providers/earth_search.py \
backend/app/providers/sentinel2.py \
backend/app/providers/sentinel1.py \
backend/app/providers/landsat.py \
backend/app/providers/planetary_computer.py

create_files \
backend/app/geospatial/__init__.py \
backend/app/geospatial/geometry.py \
backend/app/geospatial/coordinates.py \
backend/app/geospatial/spatial_queries.py \
backend/app/geospatial/raster_processor.py \
backend/app/geospatial/raster_utils.py \
backend/app/geospatial/band_mapping.py \
backend/app/geospatial/reflectance.py \
backend/app/geospatial/cloud_mask.py \
backend/app/geospatial/indices.py \
backend/app/geospatial/ndvi.py \
backend/app/geospatial/evi.py \
backend/app/geospatial/savi.py \
backend/app/geospatial/ndwi.py \
backend/app/geospatial/nbr.py \
backend/app/geospatial/change_detector.py \
backend/app/geospatial/land_cover.py \
backend/app/geospatial/classification.py \
backend/app/geospatial/forecasting.py \
backend/app/geospatial/risk_assessment.py

create_files \
backend/app/storage/__init__.py \
backend/app/storage/base.py \
backend/app/storage/local_storage.py \
backend/app/storage/s3_storage.py \
backend/app/storage/storage_factory.py

create_files \
backend/app/workers/__init__.py \
backend/app/workers/celery_app.py \
backend/app/workers/capture_tasks.py \
backend/app/workers/raster_tasks.py \
backend/app/workers/change_tasks.py \
backend/app/workers/classification_tasks.py \
backend/app/workers/forecasting_tasks.py \
backend/app/workers/report_tasks.py \
backend/app/workers/monitoring_tasks.py

create_files \
backend/app/ai/__init__.py \
backend/app/ai/base.py \
backend/app/ai/factory.py \
backend/app/ai/openai_provider.py \
backend/app/ai/context_builder.py \
backend/app/ai/prompts.py \
backend/app/ai/ai_analysis_service.py \
backend/app/ai/anomaly_detector.py \
backend/app/ai/agent.py \
backend/app/ai/agent_context.py \
backend/app/ai/agent_tools.py \
backend/app/ai/agent_prompts.py \
backend/app/ai/agent_guardrails.py \
backend/app/ai/agent_service.py

create_files \
backend/app/mcp/__init__.py \
backend/app/mcp/config.py \
backend/app/mcp/api_client.py \
backend/app/mcp/server.py \
backend/app/mcp/prompts.py \
backend/app/mcp/test_client.py \
backend/app/mcp/test_tool_call.py

create_files \
backend/app/monitoring/__init__.py \
backend/app/monitoring/models.py \
backend/app/monitoring/schemas.py \
backend/app/monitoring/service.py \
backend/app/monitoring/tasks.py

create_files \
backend/app/integrations/__init__.py \
backend/app/integrations/email.py \
backend/app/integrations/notifications.py \
backend/app/integrations/external_apis.py

# Alembic and tests
create_files \
backend/alembic/versions/__init__.py \
backend/alembic/env.py \
backend/alembic/script.py.mako \
backend/tests/conftest.py \
backend/tests/unit/test_auth.py \
backend/tests/unit/test_projects.py \
backend/tests/unit/test_areas.py \
backend/tests/unit/test_geometry.py \
backend/tests/unit/test_indices.py \
backend/tests/unit/test_raster_processor.py \
backend/tests/unit/test_stac.py \
backend/tests/unit/test_ai.py \
backend/tests/unit/test_monitoring.py \
backend/tests/integration/test_database.py \
backend/tests/integration/test_api.py \
backend/tests/integration/test_capture_pipeline.py \
backend/tests/integration/test_ndvi_pipeline.py \
backend/tests/integration/test_raster_tiles.py \
backend/tests/integration/test_agent_workflow.py \
backend/tests/security/test_organization_isolation.py \
backend/tests/security/test_rbac_permissions.py \
backend/tests/security/test_auth_sessions.py \
backend/tests/security/test_rate_limits.py \
backend/tests/security/test_dataset_access.py \
backend/tests/security/test_agent_authorization.py \
backend/tests/security/test_audit_logs.py \
backend/.dockerignore \
backend/alembic.ini \
backend/Dockerfile \
backend/pyproject.toml \
backend/README.md

# Frontend application files
create_files \
frontend/public/logo.svg \
frontend/src/app/layout.tsx \
frontend/src/app/page.tsx \
frontend/src/app/globals.css \
"frontend/src/app/(auth)/login/page.tsx" \
"frontend/src/app/(auth)/register/page.tsx" \
"frontend/src/app/(auth)/forgot-password/page.tsx" \
"frontend/src/app/(dashboard)/layout.tsx" \
"frontend/src/app/(dashboard)/dashboard/page.tsx" \
"frontend/src/app/(dashboard)/projects/page.tsx" \
"frontend/src/app/(dashboard)/projects/[projectId]/page.tsx" \
"frontend/src/app/(dashboard)/map/page.tsx" \
"frontend/src/app/(dashboard)/captures/page.tsx" \
"frontend/src/app/(dashboard)/datasets/page.tsx" \
"frontend/src/app/(dashboard)/analysis/page.tsx" \
"frontend/src/app/(dashboard)/analysis/time-series/page.tsx" \
"frontend/src/app/(dashboard)/analysis/change-detection/page.tsx" \
"frontend/src/app/(dashboard)/ai/page.tsx" \
"frontend/src/app/(dashboard)/monitoring/page.tsx" \
"frontend/src/app/(dashboard)/reports/page.tsx" \
"frontend/src/app/(dashboard)/organizations/page.tsx" \
"frontend/src/app/(dashboard)/organizations/[organizationId]/page.tsx" \
"frontend/src/app/(dashboard)/settings/page.tsx" \
"frontend/src/app/(dashboard)/audit-logs/page.tsx"

# Frontend components
create_files \
frontend/src/components/ui/button.tsx \
frontend/src/components/ui/input.tsx \
frontend/src/components/ui/dialog.tsx \
frontend/src/components/ui/dropdown.tsx \
frontend/src/components/ui/select.tsx \
frontend/src/components/ui/table.tsx \
frontend/src/components/ui/card.tsx \
frontend/src/components/ui/badge.tsx \
frontend/src/components/ui/loader.tsx \
frontend/src/components/layout/app-shell.tsx \
frontend/src/components/layout/sidebar.tsx \
frontend/src/components/layout/topbar.tsx \
frontend/src/components/layout/organization-switcher.tsx \
frontend/src/components/dashboard/stats-cards.tsx \
frontend/src/components/dashboard/recent-projects.tsx \
frontend/src/components/dashboard/activity-feed.tsx \
frontend/src/components/maps/map-explorer.tsx \
frontend/src/components/maps/area-editor.tsx \
frontend/src/components/maps/raster-layer-viewer.tsx \
frontend/src/components/maps/map-controls.tsx \
frontend/src/components/maps/layer-selector.tsx \
frontend/src/components/projects/project-list.tsx \
frontend/src/components/projects/project-card.tsx \
frontend/src/components/projects/project-form.tsx \
frontend/src/components/captures/capture-form.tsx \
frontend/src/components/captures/capture-list.tsx \
frontend/src/components/captures/ndvi-scene-list.tsx \
frontend/src/components/analysis/ndvi-time-series-chart.tsx \
frontend/src/components/analysis/change-detection-viewer.tsx \
frontend/src/components/analysis/index-selector.tsx \
frontend/src/components/analysis/classification-map.tsx \
frontend/src/components/analysis/risk-dashboard.tsx \
frontend/src/components/ai/geospatial-assistant.tsx \
frontend/src/components/ai/agent-chat.tsx \
frontend/src/components/ai/action-approval-card.tsx \
frontend/src/components/monitoring/monitoring-settings.tsx \
frontend/src/components/monitoring/environmental-alert-list.tsx \
frontend/src/components/organizations/organization-members.tsx \
frontend/src/components/organizations/organization-settings.tsx \
frontend/src/components/organizations/invite-member-dialog.tsx \
frontend/src/components/reports/report-builder.tsx \
frontend/src/components/reports/report-preview.tsx

# Frontend services, state, hooks, libraries and types
create_files \
frontend/src/services/auth.service.ts \
frontend/src/services/user.service.ts \
frontend/src/services/organization.service.ts \
frontend/src/services/project.service.ts \
frontend/src/services/area.service.ts \
frontend/src/services/capture.service.ts \
frontend/src/services/dataset.service.ts \
frontend/src/services/health.service.ts \
frontend/src/services/raster.service.ts \
frontend/src/services/analysis.service.ts \
frontend/src/services/ai.service.ts \
frontend/src/services/agent.service.ts \
frontend/src/services/monitoring.service.ts \
frontend/src/services/report.service.ts \
frontend/src/services/export.service.ts \
frontend/src/store/auth.store.ts \
frontend/src/store/map.store.ts \
frontend/src/store/project.store.ts \
frontend/src/store/organization.store.ts \
frontend/src/hooks/use-auth.ts \
frontend/src/hooks/use-projects.ts \
frontend/src/hooks/use-areas.ts \
frontend/src/hooks/use-organization.ts \
frontend/src/lib/api.ts \
frontend/src/lib/utils.ts \
frontend/src/lib/constants.ts \
frontend/src/lib/query-client.ts \
frontend/src/lib/map-config.ts \
frontend/src/lib/validators.ts \
frontend/src/providers/query-provider.tsx \
frontend/src/providers/auth-provider.tsx \
frontend/src/providers/theme-provider.tsx \
frontend/src/types/auth.ts \
frontend/src/types/user.ts \
frontend/src/types/organization.ts \
frontend/src/types/project.ts \
frontend/src/types/area.ts \
frontend/src/types/capture.ts \
frontend/src/types/dataset.ts \
frontend/src/types/geospatial.ts \
frontend/src/types/analysis.ts \
frontend/src/types/api.ts

# Frontend configuration
create_files \
frontend/.dockerignore \
frontend/.env.local.example \
frontend/Dockerfile \
frontend/next.config.ts \
frontend/package.json \
frontend/tsconfig.json \
frontend/eslint.config.mjs \
frontend/README.md

# Infrastructure files
create_files \
infrastructure/docker/backend.Dockerfile \
infrastructure/docker/frontend.Dockerfile \
infrastructure/docker/worker.Dockerfile \
infrastructure/docker/titiler.Dockerfile \
infrastructure/nginx/nginx.conf \
infrastructure/nginx/conf.d/aleph-next.conf \
infrastructure/aws/terraform/main.tf \
infrastructure/aws/terraform/variables.tf \
infrastructure/aws/terraform/outputs.tf \
infrastructure/aws/terraform/providers.tf \
infrastructure/aws/terraform/networking.tf \
infrastructure/aws/terraform/security-groups.tf \
infrastructure/aws/terraform/rds.tf \
infrastructure/aws/terraform/redis.tf \
infrastructure/aws/terraform/s3.tf \
infrastructure/aws/terraform/ecr.tf \
infrastructure/aws/terraform/ecs.tf \
infrastructure/aws/terraform/alb.tf \
infrastructure/aws/terraform/iam.tf \
infrastructure/aws/terraform/cloudwatch.tf \
infrastructure/aws/terraform/terraform.tfvars.example \
infrastructure/aws/ecs/frontend-task-definition.json \
infrastructure/aws/ecs/backend-task-definition.json \
infrastructure/aws/ecs/worker-task-definition.json \
infrastructure/aws/ecs/beat-task-definition.json \
infrastructure/aws/ecs/titiler-task-definition.json \
infrastructure/aws/scripts/build-and-push.sh \
infrastructure/aws/scripts/deploy-ecs.sh \
infrastructure/aws/scripts/run-migrations.sh \
infrastructure/monitoring/prometheus.yml \
infrastructure/scripts/backup-database.sh \
infrastructure/scripts/restore-database.sh \
infrastructure/scripts/health-check.sh

# Documentation files
create_files \
docs/README.md \
docs/architecture.md \
docs/repository-structure.md \
docs/development-setup.md \
docs/environment-variables.md \
docs/docker-setup.md \
docs/database-schema.md \
docs/api-documentation.md \
docs/authentication.md \
docs/geospatial-processing.md \
docs/satellite-data-sources.md \
docs/raster-processing.md \
docs/ndvi-analysis.md \
docs/ai-integration.md \
docs/mcp-integration.md \
docs/monitoring.md \
docs/security.md \
docs/multi-tenancy.md \
docs/aws-deployment.md \
docs/backup-and-recovery.md \
docs/troubleshooting.md

# Root scripts
create_files \
scripts/setup.sh \
scripts/start-dev.sh \
scripts/stop-dev.sh \
scripts/reset-database.sh \
scripts/run-backend-tests.sh \
scripts/run-frontend-tests.sh \
scripts/lint.sh \
scripts/check-repository.sh

# Root files
create_files \
.dockerignore \
.env \
.env.example \
.gitignore \
.pre-commit-config.yaml \
docker-compose.yml \
docker-compose.prod.yml \
Makefile \
LICENSE \
README.md

echo ""
echo "TerraMind directory structure created successfully!"
echo ""
echo "Run: find . -type f | sort"
