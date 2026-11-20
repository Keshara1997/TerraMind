# Multi-Tenancy

## 1. Overview

Multi-tenancy allows a single application instance to serve multiple organizations while keeping their data and resources logically separated.

TERRAMIND is designed as a multi-tenant geospatial intelligence platform.

Different organizations should be able to use the same application infrastructure without accessing one another's private information.

Each organization can manage its own:

- Users and memberships.
- Projects.
- Geographical areas.
- Satellite datasets.
- Raster files.
- Geospatial analysis results.
- AI conversations and reports.
- Organization settings.
- Audit records.

The main objectives are:

1. Support multiple organizations.
2. Isolate organization data.
3. Control user access.
4. Support organization-level roles.
5. Enforce project-level permissions.
6. Maintain secure data storage.
7. Support tenant-aware background processing.
8. Provide organization-level monitoring and auditing.
9. Scale the platform as organizations grow.

This document describes the target architecture. The actual database models, migrations, and authorization implementation must be verified in the repository.

## 2. What Is Multi-Tenancy?

A tenant represents an organization or customer using TERRAMIND.

For example:

```text
                 TERRAMIND
                     |
          +----------+----------+
          |                     |
          v                     v
    Organization A        Organization B
          |                     |
     +----+----+           +----+----+
     |         |           |         |
     v         v           v         v
   Users    Projects      Users    Projects
     |         |           |         |
     v         v           v         v
  Datasets  Analysis     Datasets  Analysis
```

Organization A must not access Organization B's private information.

Both organizations can use the same application, but their data access must be controlled independently.

## 3. Multi-Tenant Architecture

The proposed architecture uses a shared application and database with tenant-aware data access.

```text
+--------------------------------------+
|              TERRAMIND              |
|                                      |
|          Next.js Frontend            |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|             FastAPI Backend          |
|                                      |
|          Authentication              |
|          Tenant Resolution           |
|          Authorization               |
|          Business Logic              |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|          Tenant Context Layer        |
|                                      |
|          Organization ID             |
|          User ID                     |
|          Role                        |
|          Permissions                  |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|        Tenant-Aware Data Layer       |
|                                      |
|          PostgreSQL                  |
|          PostGIS                      |
|          Redis                       |
|          Object Storage              |
+--------------------------------------+
```

### Main components

| Component | Responsibility |
|---|---|
| Frontend | Organization selection and user interface |
| Authentication | Identifies the user |
| Tenant resolution | Identifies the active organization |
| Authorization | Checks roles and permissions |
| Backend services | Apply tenant-aware business logic |
| Database | Stores tenant-associated records |
| Object storage | Stores organization-owned files |
| Background workers | Process jobs using the correct tenant context |

## 4. Tenant Identification

After authentication, the backend must determine which organization the user is allowed to access.

A user may belong to one or more organizations.

Example:

```text
User: user-123

Organization memberships:

- Organization A
- Organization B

Active organization:

- Organization A
```

The active organization determines the context for organization-scoped operations.

### Tenant resolution workflow

```text
User Request
     |
     v
Authenticate User
     |
     v
Identify User Account
     |
     v
Resolve Requested Organization
     |
     v
Check Organization Membership
     |
     +---- Not a Member ----> Reject
     |
     v
Load Membership and Permissions
     |
     v
Create Trusted Tenant Context
     |
     v
Execute Authorized Operation
```

The backend must verify organization membership on every relevant request.

Never trust an organization ID simply because it appears in a request header, URL, query parameter, or request body.

## 5. Database Design

The proposed database architecture uses a shared PostgreSQL database with tenant identifiers on organization-owned records.

### 5.1 Organizations table

Stores organization information.

Proposed fields:

| Field | Type | Description |
|---|---|---|
| id | UUID | Organization identifier |
| name | VARCHAR | Organization name |
| slug | VARCHAR | Unique organization slug |
| status | VARCHAR | Organization status |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update |

### 5.2 Organization members table

Connects users with organizations.

| Field | Type | Description |
|---|---|---|
| id | UUID | Membership identifier |
| organization_id | UUID | Organization reference |
| user_id | UUID | User reference |
| role | VARCHAR | Organization role |
| status | VARCHAR | Membership status |
| joined_at | TIMESTAMP | Membership date |

A user may have multiple organization memberships.

A unique constraint should prevent duplicate membership records for the same user and organization.

### 5.3 Projects table

Each organization-owned project should reference its organization.

| Field | Type | Description |
|---|---|---|
| id | UUID | Project identifier |
| organization_id | UUID | Tenant identifier |
| name | VARCHAR | Project name |
| description | TEXT | Project description |
| status | VARCHAR | Project status |
| created_by | UUID | Creator user |
| created_at | TIMESTAMP | Creation time |

### 5.4 Areas table

Each area should be associated with an authorized project and organization.

| Field | Type | Description |
|---|---|---|
| id | UUID | Area identifier |
| organization_id | UUID | Tenant identifier |
| project_id | UUID | Project reference |
| name | VARCHAR | Area name |
| geometry | GEOMETRY | Spatial boundary |
| created_at | TIMESTAMP | Creation time |

### 5.5 Datasets table

Satellite and other geospatial datasets should have tenant ownership or an explicitly defined sharing model.

| Field | Type | Description |
|---|---|---|
| id | UUID | Dataset identifier |
| organization_id | UUID | Tenant identifier |
| project_id | UUID | Project reference |
| name | VARCHAR | Dataset name |
| source | VARCHAR | Data provider |
| storage_path | TEXT | Storage reference |
| created_at | TIMESTAMP | Creation time |

### 5.6 Analysis results table

Analysis results should retain their tenant and project relationships.

| Field | Type | Description |
|---|---|---|
| id | UUID | Analysis identifier |
| organization_id | UUID | Tenant identifier |
| project_id | UUID | Project reference |
| dataset_id | UUID | Input dataset |
| analysis_type | VARCHAR | Analysis type |
| status | VARCHAR | Processing status |
| result_path | TEXT | Result storage reference |
| created_at | TIMESTAMP | Creation time |

These schemas are proposed designs. Actual columns and relationships must match the implemented SQLAlchemy models and Alembic migrations.

## 6. Entity Relationships

The intended relationship structure is:

```text
Organization
     |
     +------ Organization Members
     |                |
     |                +------ Users
     |
     +------ Projects
                  |
                  +------ Areas
                  |
                  +------ Datasets
                  |
                  +------ Captures
                  |
                  +------ Analysis Results
                  |
                  +------ Reports
                  |
                  +------ Audit Logs
```

Organization-owned resources should have a consistent and verifiable relationship to their tenant.

For resources shared across organizations, implement an explicit sharing model rather than removing ownership checks.

## 7. Tenant Isolation Strategy

TERRAMIND will initially use a shared database with logical tenant isolation.

### Shared database approach

```text
PostgreSQL Database
        |
        +------ organizations
        |
        +------ users
        |
        +------ organization_members
        |
        +------ projects
        |          |
        |          +------ organization_id
        |
        +------ areas
        |          |
        |          +------ organization_id
        |
        +------ datasets
        |          |
        |          +------ organization_id
        |
        +------ analysis_results
                   |
                   +------ organization_id
```

Each tenant-owned record must be queried within the correct organization context.

### Isolation requirements

- Apply organization filters to tenant-owned queries.
- Validate resource ownership.
- Use foreign-key constraints.
- Prevent cross-tenant relationships.
- Protect background processing.
- Protect exports and downloads.
- Apply tenant restrictions to AI and MCP operations.

## 8. Tenant-Aware Backend Services

Backend services should receive a trusted tenant context.

Example conceptual context:

```python
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class TenantContext:
    user_id: UUID
    organization_id: UUID
    role: str
```

This is an illustrative structure. The actual context should be created only after authentication and membership validation.

### Example project query

```python
async def get_projects(
    db,
    tenant_context,
):
    result = await db.execute(
        select(Project).where(
            Project.organization_id
            == tenant_context.organization_id
        )
    )

    return result.scalars().all()
```

The example assumes SQLAlchemy and an existing `Project` model. Adapt it to the actual database and repository implementation.

### Important rules

1. Do not accept tenant identity as trusted input.
2. Derive tenant context from authenticated membership.
3. Apply tenant filtering to all organization-owned resources.
4. Check project-level permissions separately.
5. Keep tenant context consistent across service calls.
6. Never bypass tenant filtering for convenience.

## 9. Database-Level Protection

Application-level filtering should be supported by database constraints and, where appropriate, PostgreSQL Row-Level Security.

### 9.1 Foreign keys

Use foreign keys to preserve relationships between organizations and their resources.

For example:

- Projects reference organizations.
- Memberships reference organizations and users.
- Areas reference their organization and project.
- Datasets reference their organization and project.
- Analysis results reference their organization and relevant inputs.

### 9.2 Composite constraints

Where appropriate, use composite foreign keys to ensure that related records belong to the same organization.

For example, a dataset associated with a project should not reference a project belonging to another organization.

Conceptual SQL:

```sql
ALTER TABLE projects
ADD CONSTRAINT uq_project_id_organization
UNIQUE (id, organization_id);
```

A dependent table can then reference both columns using a composite foreign key.

This requires compatible column definitions and constraints in the actual schema.

### 9.3 Row-Level Security

PostgreSQL Row-Level Security can provide an additional database-level isolation layer.

Conceptual example:

```sql
ALTER TABLE projects
ENABLE ROW LEVEL SECURITY;
```

A tenant policy can compare the row's organization ID with a trusted database session setting.

Example policy concept:

```sql
CREATE POLICY project_tenant_policy
ON projects
USING (
    organization_id =
    current_setting('app.current_organization_id', true)::uuid
);
```

This example requires careful implementation.

Before enabling RLS:

- Define how the application sets tenant context.
- Use transaction-scoped settings.
- Ensure connection pooling does not leak tenant context.
- Understand table-owner and privileged-role behavior.
- Test all access paths.
- Configure policies for both reading and writing.

RLS is an additional security layer, not a replacement for application authorization.

## 10. Tenant-Aware API Design

Organization-scoped APIs should make the organization context clear.

Example API structure:

```text
/api/v1/organizations/

/api/v1/organizations/{organization_id}

/api/v1/organizations/{organization_id}/members

/api/v1/organizations/{organization_id}/projects

/api/v1/organizations/{organization_id}/datasets

/api/v1/organizations/{organization_id}/analyses
```

The backend must verify that the authenticated user belongs to the requested organization.

The URL organization ID identifies the requested context; it does not grant access.

### Example request

```http
GET /api/v1/organizations/org-123/projects
Authorization: Bearer <access-token>
```

The backend must:

1. Validate the access token.
2. Identify the user.
3. Verify organization membership.
4. Check the relevant permission.
5. Retrieve only authorized projects.
6. Return the result.

The API route structure is proposed and should be aligned with the actual API design.

## 11. Tenant-Aware Redis Usage

Redis may be used for caching, rate limiting, and background job coordination.

Cache keys must include sufficient tenant context to prevent data from one organization being returned to another.

Example key patterns:

```text
tenant:{organization_id}:project:{project_id}

tenant:{organization_id}:dataset:{dataset_id}

tenant:{organization_id}:analysis:{analysis_id}

tenant:{organization_id}:user:{user_id}
```

### Redis security rules

- Include tenant context in tenant-specific keys.
- Validate permissions before returning cached private data.
- Avoid using user-controlled tenant IDs as authorization.
- Apply suitable expiration.
- Invalidate affected caches after updates.
- Avoid placing secrets in cache values.

Cache isolation must be tested, not assumed from key naming alone.

## 12. Tenant-Aware Object Storage

TERRAMIND may store satellite imagery, raster outputs, vector datasets, and generated reports in object storage.

A logical key structure could be:

```text
storage/
├── organizations/
│   ├── {organization_id}/
│   │   ├── projects/
│   │   │   ├── {project_id}/
│   │   │   │   ├── datasets/
│   │   │   │   ├── captures/
│   │   │   │   ├── analysis/
│   │   │   │   └── reports/
```

This is a logical organization scheme, not a requirement to use a particular bucket layout.

### Storage security

- Keep private datasets in private storage.
- Validate organization and project access before downloads.
- Use short-lived signed URLs where appropriate.
- Restrict storage permissions.
- Avoid predictable public download links.
- Validate upload ownership.
- Audit sensitive downloads and exports.

A storage path containing an organization ID does not automatically provide access control.

## 13. Tenant-Aware Background Jobs

Background jobs must preserve the correct tenant context.

Examples:

- Satellite downloads.
- Raster processing.
- NDVI analysis.
- Change detection.
- Report generation.
- Data exports.

### Job workflow

```text
User Request
     |
     v
Authenticate User
     |
     v
Validate Tenant Access
     |
     v
Create Background Job
     |
     v
Store Tenant Context
     |
     v
Worker Receives Job
     |
     v
Revalidate Resource Ownership
     |
     v
Execute Authorized Processing
     |
     v
Store Tenant-Owned Result
```

### Example job payload

```json
{
  "job_id": "job-123",
  "organization_id": "org-456",
  "project_id": "project-789",
  "analysis_id": "analysis-001",
  "job_type": "ndvi_analysis"
}
```

These identifiers are illustrative.

### Background job requirements

- Validate the tenant before job creation.
- Store the required tenant context.
- Revalidate resource ownership in the worker.
- Avoid trusting arbitrary queue payloads.
- Store outputs under the correct tenant.
- Prevent cross-tenant result retrieval.
- Record failures and audit events.

Workers should use controlled service credentials and must not rely on the original user's browser session.

## 14. Tenant-Aware AI and MCP

AI and MCP tools must follow the same tenant isolation rules as normal backend APIs.

Example:

```text
User
 |
 v
AI Assistant
 |
 v
MCP Client
 |
 v
MCP Server
 |
 v
Authenticated User Context
 |
 v
Organization Membership Check
 |
 v
Project Permission Check
 |
 v
Backend Service
 |
 v
Authorized Result
```

Important requirements:

- Do not trust organization IDs supplied by AI.
- Validate the user context on each tool call.
- Restrict resource access.
- Apply tenant filtering to search results.
- Avoid exposing private conversation history across tenants.
- Validate report generation requests.
- Audit sensitive operations.

The AI model must not make tenant authorization decisions.

## 15. Tenant Roles and Permissions

Organization roles define what users can do within their organization.

Proposed roles:

| Role | Description |
|---|---|
| Owner | Full organization management |
| Admin | Manages organization operations |
| Project Manager | Manages assigned projects |
| Analyst | Performs authorized analysis |
| Viewer | Reads authorized information |

Permissions should be defined separately from role names.

Example permission identifiers:

```text
organization.read
organization.update
organization.members.read
organization.members.manage

project.create
project.read
project.update
project.delete

dataset.read
dataset.upload
dataset.delete

analysis.read
analysis.execute

report.read
report.generate
report.export
```

This makes the authorization system easier to maintain when additional roles are introduced.

## 16. Tenant Lifecycle Management

The platform should support the organization lifecycle.

### Organization creation

1. Validate the request.
2. Create the organization.
3. Create the owner membership.
4. Apply default settings.
5. Record an audit event.

### Member invitation

1. Organization administrator creates an invitation.
2. Validate the administrator's permission.
3. Generate a secure invitation token.
4. Send the invitation.
5. Validate the invitation when accepted.
6. Create the membership.
7. Record the event.

### Member removal

1. Verify administrator permission.
2. Remove or deactivate the membership.
3. Revoke relevant sessions or access where appropriate.
4. Update relevant authorization caches.
5. Record an audit event.

### Organization suspension

A suspended organization should not be able to perform restricted operations.

The backend should enforce organization status checks consistently across APIs, workers, AI, and MCP operations.

### Organization deletion

Deletion requires a carefully defined retention and recovery policy.

Before deleting an organization:

- Check ownership and administrative permissions.
- Review dependent resources.
- Apply retention requirements.
- Consider legal and contractual obligations.
- Create required backups.
- Audit the operation.

Do not automatically delete all associated data without a confirmed retention and deletion policy.

## 17. Tenant Monitoring and Auditing

Monitoring should support organization-level operational visibility without exposing another tenant's information.

Potential metrics:

- Active users per organization.
- Project count.
- Dataset count.
- Storage usage.
- Processing job count.
- Analysis execution count.
- API request volume.
- AI usage.
- Failed operations.

Audit events should include the organization context where relevant.

Example:

```json
{
  "event_type": "dataset.uploaded",
  "organization_id": "org-456",
  "user_id": "user-123",
  "resource_id": "dataset-789",
  "status": "success"
}
```

These identifiers are illustrative.

## 18. Tenant Migration Strategy

When adding tenant support to an existing database, existing records must be handled carefully.

A safe migration process should:

1. Identify existing organization-owned tables.
2. Create the organization model and membership model.
3. Decide how existing records map to organizations.
4. Add nullable tenant columns where required for a staged migration.
5. Backfill organization IDs.
6. Validate that no records remain incorrectly assigned.
7. Add foreign keys and indexes.
8. Enforce non-null constraints where appropriate.
9. Add tenant filtering to application queries.
10. Test cross-tenant access prevention.
11. Enable RLS if selected.
12. Deploy with a rollback and recovery plan.

Do not assign all existing records to an arbitrary organization.

Do not enforce a non-null tenant constraint until the backfill has been validated.

For production migrations, test against a recent backup or representative copy of the database first.

## 19. Indexing and Performance

Tenant-aware queries should be designed for efficient filtering.

Consider indexes such as:

```sql
CREATE INDEX idx_projects_organization_id
ON projects (organization_id);
```

For project and organization lookups:

```sql
CREATE INDEX idx_projects_organization_status
ON projects (organization_id, status);
```

For tenant-owned spatial data:

```sql
CREATE INDEX idx_areas_organization_id
ON areas (organization_id);
```

Spatial geometry columns should also have suitable PostGIS spatial indexes.

Index design must be based on actual query patterns and verified using query plans.

Avoid creating unnecessary indexes because they increase storage requirements and write overhead.

## 20. Testing Strategy

Multi-tenant security requires dedicated automated tests.

### Organization isolation tests

- Organization A can access its own projects.
- Organization B can access its own projects.
- Organization A cannot access Organization B's projects.
- Organization A cannot access Organization B's datasets.
- Organization A cannot access Organization B's analysis results.

### Membership tests

- Organization members can access permitted resources.
- Non-members cannot access organization resources.
- Suspended members cannot perform restricted operations.
- Removed members lose access.

### Role tests

- Owners can perform permitted administrative operations.
- Admins can manage only allowed resources.
- Analysts can execute permitted analyses.
- Viewers cannot perform write operations.

### Integration tests

- API endpoints enforce tenant access.
- Redis cache keys do not leak tenant data.
- Background workers preserve tenant context.
- Object-storage downloads enforce authorization.
- MCP tools enforce tenant access.
- AI-generated requests cannot bypass permissions.

## 21. Implementation Roadmap

| Phase | Work |
|---|---|
| 1 | Define organization and membership models |
| 2 | Define tenant-owned resources |
| 3 | Add tenant identifiers and constraints |
| 4 | Implement tenant resolution |
| 5 | Implement organization membership checks |
| 6 | Implement role and permission checks |
| 7 | Add tenant-aware service queries |
| 8 | Secure Redis and object storage access |
| 9 | Implement tenant-aware background jobs |
| 10 | Secure AI and MCP operations |
| 11 | Add audit logging and monitoring |
| 12 | Implement automated tenant isolation tests |
| 13 | Review production migration and recovery |

## 22. Verification Checklist

- [ ] Organization model exists.
- [ ] Organization membership model exists.
- [ ] Users can belong to multiple organizations where required.
- [ ] Organization membership is validated.
- [ ] Tenant context is created from trusted identity information.
- [ ] Organization-owned records have tenant relationships.
- [ ] Database relationships prevent cross-tenant associations.
- [ ] Tenant-aware queries are implemented.
- [ ] Project-level permissions are enforced.
- [ ] Redis usage is tenant-aware.
- [ ] Object-storage access is tenant-aware.
- [ ] Background jobs preserve tenant context.
- [ ] AI and MCP tools enforce tenant isolation.
- [ ] Audit records include appropriate tenant information.
- [ ] Cross-tenant access tests pass.
- [ ] Existing records are safely migrated.
- [ ] Production tenant isolation has been reviewed.

## 23. Important Design Principles

1. Every organization-owned resource must have a clear tenant relationship.
2. Tenant identity must come from trusted authentication and membership validation.
3. Frontend organization selection is not an authorization mechanism.
4. Every backend operation must enforce tenant access.
5. Database constraints should support tenant integrity.
6. Background workers must preserve and validate tenant context.
7. Redis and object storage must not leak tenant data.
8. AI and MCP integrations must follow the same authorization rules.
9. Existing data must be migrated safely.
10. Tenant isolation must be verified through automated security tests.

**Important:** This document describes the target multi-tenant architecture for TERRAMIND. It does not confirm that tenant isolation, database constraints, RLS policies, or tenant-aware services are already implemented.