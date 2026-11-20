# Security

## 1. Overview

Security is a core requirement of TERRAMIND.

The platform will handle user accounts, organization information, geospatial datasets, satellite imagery, analysis results, and AI-generated reports.

The security architecture must protect:

- User accounts and credentials.
- Organization and project information.
- Geospatial data.
- Satellite datasets and raster files.
- Analysis results.
- API endpoints.
- AI and MCP integrations.
- Application infrastructure.
- System configuration and secrets.

The main security objectives are:

1. Prevent unauthorized access.
2. Protect user and organization data.
3. Enforce role-based permissions.
4. Maintain strict tenant isolation.
5. Protect API endpoints.
6. Secure uploaded files and datasets.
7. Protect application secrets.
8. Record important security events.
9. Reduce infrastructure vulnerabilities.
10. Support secure production deployment.

This document describes the target security architecture. Actual implementation and compliance must be verified separately.

## 2. Security Architecture

The proposed security architecture protects the application at multiple levels.

```text
+--------------------------------------+
|             User Interface           |
|                                      |
|          Next.js Frontend            |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|          API Security Layer          |
|                                      |
|          HTTPS / TLS                 |
|          CORS                        |
|          Rate Limiting               |
|          Input Validation            |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|       Authentication Layer          |
|                                      |
|          Login                       |
|          Access Tokens               |
|          Token Validation            |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|       Authorization Layer            |
|                                      |
|          Roles                       |
|          Permissions                 |
|          Organization Access         |
|          Project Access              |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|          Application Layer           |
|                                      |
|          Business Logic              |
|          Geospatial Services         |
|          AI / MCP Services           |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|            Data Security             |
|                                      |
|          PostgreSQL / PostGIS        |
|          Redis                       |
|          Object Storage              |
|          Audit Logs                  |
+--------------------------------------+
```

Security must be enforced by the backend. Frontend checks are useful for user experience but are not a substitute for server-side authorization.

## 3. Authentication

Authentication verifies the identity of a user.

TERRAMIND will use a secure authentication mechanism for user access.

### 3.1 Authentication features

Planned features include:

- User registration.
- User login.
- Password hashing.
- Access token generation.
- Token validation.
- Token expiration.
- Refresh token handling, if implemented.
- Logout.
- Password reset.
- Account status management.

### 3.2 Login workflow

```text
User
 |
 v
Enter Email and Password
 |
 v
Next.js Login Page
 |
 v
FastAPI Authentication API
 |
 v
Find User Account
 |
 v
Verify Password Hash
 |
 +---- Invalid ----> Reject Login
 |
 v
Check Account Status
 |
 v
Generate Access Token
 |
 v
Return Authentication Result
 |
 v
Access Protected Resources
```

### 3.3 Password storage

Passwords must never be stored as plain text.

Use a suitable password hashing algorithm such as Argon2id or bcrypt.

Password hashing requirements:

- Use a well-maintained library.
- Use secure configuration.
- Verify passwords using the hashing library.
- Never log passwords.
- Never return password hashes through APIs.
- Support secure password changes and resets.

Password hashing is different from encryption. Password hashes are designed to be verified, not decrypted.

### 3.4 Token security

If JWT access tokens are used, they should:

- Have an appropriate expiration time.
- Be signed using a secure algorithm.
- Be validated by the backend.
- Include only necessary claims.
- Be rejected when invalid or expired.
- Avoid containing confidential information.

For refresh tokens, use rotation and revocation controls where appropriate.

Never store long-lived authentication credentials in browser local storage without a deliberate security assessment.

A common browser architecture uses Secure, HttpOnly, and appropriate SameSite cookies for authentication credentials. Cookie-based authentication must also address CSRF protection.

## 4. Authorization

Authorization determines what an authenticated user is allowed to do.

TERRAMIND should implement role-based access control (RBAC), with resource-level checks.

### 4.1 Proposed roles

| Role | Responsibility |
|---|---|
| Super Admin | Platform-level administration |
| Organization Owner | Manages an organization |
| Organization Admin | Manages organization users and settings |
| Project Manager | Manages assigned projects |
| Analyst | Performs permitted geospatial analysis |
| Viewer | Reads permitted project information |

These are proposed roles. Actual roles and permissions should be defined according to application requirements.

### 4.2 Permission examples

| Operation | Owner | Admin | Manager | Analyst | Viewer |
|---|---|---|---|---|---|
| View project | Yes | Yes | Yes | Assigned | Assigned |
| Create project | Yes | Yes | Configurable | No | No |
| Update project | Yes | Yes | Assigned | No | No |
| View datasets | Yes | Yes | Assigned | Assigned | Assigned |
| Run analysis | Yes | Yes | Configurable | Assigned | No |
| Manage members | Yes | Yes | No | No | No |
| Delete project | Yes | Configurable | No | No | No |

The final permission matrix must be implemented in the backend.

### 4.3 Authorization workflow

```text
Incoming Request
       |
       v
Authenticate User
       |
       v
Identify Organization
       |
       v
Identify Requested Resource
       |
       v
Check User Role
       |
       v
Check Required Permission
       |
       +---- Denied ----> Return 403
       |
       v
Execute Operation
       |
       v
Return Authorized Result
```

Never rely only on frontend button visibility to enforce permissions.

## 5. Multi-Tenant Security

TERRAMIND is designed to support multiple organizations.

Each organization must access only its own authorized resources.

### Security requirements

- Every organization-owned resource must have an appropriate tenant association.
- User membership must be validated.
- Project access must be checked.
- Database queries must apply tenant restrictions.
- Background jobs must preserve the correct tenant context.
- Exports must respect tenant permissions.
- AI and MCP operations must use authorized tenant context.
- Audit records must identify the organization where appropriate.

### Example

```text
Organization A
    |
    +---- User A1
    |
    +---- Project A1
    |
    +---- Dataset A1

Organization B
    |
    +---- User B1
    |
    +---- Project B1
    |
    +---- Dataset B1
```

Organization A must never access Organization B's information through a modified project ID, dataset ID, API request, MCP tool, or background job.

For additional protection, evaluate PostgreSQL Row-Level Security (RLS) where appropriate. RLS does not remove the need for correct application-level authorization and carefully managed database roles.

## 6. API Security

All protected backend endpoints must enforce authentication and authorization.

### 6.1 HTTPS

Production API communication must use HTTPS.

HTTPS protects data transmitted between clients and services.

Do not send authentication credentials over unencrypted public HTTP connections.

### 6.2 CORS

Configure Cross-Origin Resource Sharing (CORS) using explicitly permitted frontend origins.

Example configuration:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-production-domain.com",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)
```

This is an illustrative configuration. Replace the example origin with the actual deployment domain.

Avoid wildcard origins when credentials are enabled.

### 6.3 Rate limiting

Rate limiting helps prevent excessive requests and abuse.

Apply limits to:

- Login attempts.
- Registration.
- Password reset.
- API requests.
- Dataset searches.
- Satellite downloads.
- Raster processing.
- AI requests.
- MCP tool calls.

Use appropriate limits based on user, organization, endpoint, and infrastructure capacity.

### 6.4 Input validation

Validate every request before processing.

Examples:

- User identifiers.
- Project identifiers.
- Organization identifiers.
- Dataset identifiers.
- Date ranges.
- Coordinates.
- Geometry values.
- File metadata.
- Pagination values.

Use Pydantic schemas for FastAPI request validation where appropriate.

### 6.5 SQL injection protection

Use SQLAlchemy parameterized queries and safe ORM operations.

Avoid constructing SQL statements by directly inserting untrusted input.

For unavoidable raw SQL, use bound parameters and carefully review the query.

### 6.6 HTTP security headers

Consider appropriate headers, including:

- Content-Security-Policy.
- X-Content-Type-Options.
- Referrer-Policy.
- Strict-Transport-Security.
- Frame-ancestors through CSP.

Configure headers according to the frontend and deployment architecture.

## 7. File Upload Security

TERRAMIND may allow users to upload geospatial datasets and related files.

Uploaded files must be treated as untrusted input.

### Requirements

- Validate file extensions.
- Validate actual file formats.
- Apply file size limits.
- Use generated storage filenames.
- Prevent path traversal.
- Restrict executable file types.
- Store uploads outside public web directories.
- Apply access control to downloads.
- Scan files where appropriate.
- Validate archive contents before extraction.

### Geospatial-specific validation

For raster and vector files, consider:

- File format validation.
- Raster dimensions.
- Band count.
- Coordinate reference system.
- Geometry validity.
- Archive size and expansion limits.
- External references inside datasets.
- Malformed or malicious metadata.

Do not assume that a file is safe simply because it has a `.tif`, `.zip`, `.geojson`, or `.gpkg` extension.

Use appropriate GDAL and library security controls when processing untrusted geospatial files.

## 8. Data Protection

Application data should be protected both during transmission and at rest.

### 8.1 Data in transit

Use TLS for:

- Browser-to-API communication.
- Service-to-service communication where required.
- Database connections across untrusted networks.
- Remote MCP connections.
- External provider connections.

### 8.2 Data at rest

Protect:

- PostgreSQL database storage.
- Uploaded satellite datasets.
- Raster outputs.
- Generated reports.
- Backups.
- Secrets.

Use encryption supported by the selected database, storage service, and infrastructure.

### 8.3 Data classification

A proposed classification:

| Classification | Example |
|---|---|
| Public | Public documentation |
| Internal | Internal operational information |
| Confidential | Organization project information |
| Restricted | Credentials and sensitive access information |

Apply access and retention controls based on the actual classification requirements.

## 9. Secrets Management

Application secrets must never be committed to Git.

Examples include:

- Database passwords.
- JWT signing keys.
- AI provider API keys.
- Satellite provider credentials.
- AWS access credentials.
- Redis credentials.
- External integration secrets.

### Development

Use a local environment file:

```text
.env
```

Ensure it is excluded from version control.

Example `.gitignore` entries:

```gitignore
.env
.env.*
!.env.example

*.pem
*.key

secrets/
```

Review ignore rules carefully to avoid excluding required non-secret configuration files.

### Production

Use an appropriate secrets-management solution, such as:

- AWS Secrets Manager.
- AWS Systems Manager Parameter Store.

Production credentials should be managed outside source code and rotated when necessary.

Never expose private secrets through `NEXT_PUBLIC_` environment variables.

## 10. Database Security

PostgreSQL and PostGIS contain important application information.

Security requirements:

- Use dedicated application database accounts.
- Follow least-privilege access.
- Restrict database network access.
- Use secure connection configuration.
- Protect database backups.
- Apply database updates.
- Review permissions.
- Monitor unusual access.
- Use parameterized queries.
- Enforce tenant restrictions.

Do not use a PostgreSQL superuser account for normal application requests.

Use separate database roles for application access, migrations, and administration where appropriate.

## 11. Redis Security

Redis may store cache data, task information, and temporary application state.

Apply the following protections:

- Restrict network access.
- Use authentication and TLS where supported and required.
- Avoid exposing Redis publicly.
- Apply appropriate key expiration.
- Protect sensitive cached information.
- Separate environments.
- Monitor access and resource usage.

Do not assume Redis is a secure permanent storage location for sensitive information.

## 12. AI and MCP Security

AI and MCP integrations introduce additional security considerations.

### AI security

- Never send unnecessary confidential data to an AI provider.
- Review provider data handling and retention settings.
- Avoid exposing secrets in prompts.
- Validate AI-generated outputs.
- Do not allow AI responses to bypass application permissions.
- Use approved models and providers.
- Monitor usage and access.

### MCP security

- Authenticate remote MCP clients.
- Validate every tool request.
- Enforce tenant isolation.
- Check permissions for each resource.
- Limit available tools.
- Apply request timeouts.
- Audit sensitive tool operations.

### Tool restrictions

Do not expose unrestricted tools for:

- SQL execution.
- Shell commands.
- Filesystem access.
- Database administration.
- Credential retrieval.
- Destructive operations without authorization.

The AI model must never be treated as a trusted security boundary.

## 13. Audit Logging

Audit logging records important actions performed within the platform.

Potential audit events include:

- Successful login.
- Failed login.
- Password changes.
- User creation.
- Role changes.
- Organization membership changes.
- Project creation.
- Project deletion.
- Dataset uploads.
- Dataset deletion.
- Analysis execution.
- Report generation.
- Sensitive exports.
- Administrative operations.
- Authorization failures.

### Example audit record

```json
{
  "event_type": "project.updated",
  "user_id": "user-123",
  "organization_id": "org-456",
  "resource_id": "project-789",
  "timestamp": "2026-11-20T10:30:00Z",
  "status": "success"
}
```

These identifiers are illustrative.

Audit records should be protected against unauthorized modification and deletion.

Do not store passwords, tokens, or other secrets in audit records.

## 14. Frontend Security

The Next.js application should follow secure frontend development practices.

Requirements:

- Validate user input.
- Avoid unsafe HTML rendering.
- Use safe output encoding.
- Protect authentication credentials.
- Configure secure cookies where applicable.
- Handle authentication errors safely.
- Restrict access to protected routes.
- Apply a suitable Content Security Policy.
- Avoid exposing backend secrets.
- Keep frontend dependencies updated.

Remember that frontend route protection is only a user-interface control. The backend must independently authorize every protected operation.

## 15. Infrastructure Security

Production infrastructure must be configured securely.

### AWS security

Consider:

- IAM least-privilege policies.
- Security groups.
- Private subnets for internal services.
- Restricted database access.
- Encrypted storage.
- Secure backups.
- CloudWatch monitoring.
- Secrets Manager.
- TLS certificates.
- Regular security updates.

### EC2 security

If EC2 is used:

- Restrict SSH access.
- Avoid opening unnecessary ports.
- Use a dedicated application user.
- Keep the operating system updated.
- Configure firewall rules.
- Protect SSH keys.
- Avoid running application processes as root.

### Docker security

- Use trusted base images.
- Pin image versions.
- Avoid privileged containers unless required.
- Run services as non-root users where possible.
- Avoid embedding secrets in images.
- Scan dependencies and images.
- Restrict container permissions.
- Keep Docker and container images updated.

## 16. Dependency Security

Third-party dependencies may introduce vulnerabilities.

Review dependencies for:

- Known vulnerabilities.
- Unmaintained packages.
- Unnecessary dependencies.
- Outdated versions.
- Suspicious package sources.

Possible tools:

| Tool | Purpose |
|---|---|
| pip-audit | Python dependency vulnerability checks |
| npm audit | Node.js dependency vulnerability checks |
| Dependabot | Dependency update alerts |
| Trivy | Container and configuration scanning |
| GitHub Secret Scanning | Detect exposed secrets where available |

Example Python dependency check:

```bash
pip install pip-audit
pip-audit
```

Example Node.js dependency check:

```bash
npm audit
```

Review findings before applying upgrades. An automatic update may introduce compatibility problems.

## 17. Security Testing

Security testing should be part of the development lifecycle.

### Authentication tests

- Invalid login credentials.
- Expired tokens.
- Invalid tokens.
- Disabled user accounts.
- Password reset validation.
- Logout and token revocation where implemented.

### Authorization tests

- Unauthorized project access.
- Unauthorized dataset access.
- Incorrect role permissions.
- Cross-organization access.
- Unauthorized administrative operations.

### API security tests

- Invalid request data.
- SQL injection attempts.
- Excessive request rates.
- Missing authentication.
- Incorrect HTTP methods.
- Unexpected content types.

### File upload tests

- Invalid file formats.
- Oversized files.
- Malformed archives.
- Path traversal attempts.
- Unauthorized downloads.

### Integration security tests

- AI provider access.
- MCP tool authorization.
- Background job tenant context.
- Object-storage permissions.
- Database permissions.

Use a controlled test environment. Do not perform destructive security testing against production systems without explicit authorization and a defined test plan.

## 18. Security Incident Response

If a security incident occurs, follow a structured response.

### Step 1: Identify

Identify the affected service, user accounts, data, or infrastructure.

### Step 2: Contain

Take appropriate steps to limit further access or damage.

Examples:

- Revoke compromised credentials.
- Disable affected accounts.
- Restrict network access.
- Disable a vulnerable integration.

### Step 3: Investigate

Review:

- Application logs.
- Authentication events.
- Audit records.
- Infrastructure logs.
- Relevant database activity.

### Step 4: Recover

Restore secure service operation and rotate affected secrets.

### Step 5: Review

Document:

- Incident details.
- Root cause.
- Affected resources.
- Recovery actions.
- Preventive improvements.

Follow applicable legal and organizational notification requirements when necessary.

## 19. Security Configuration Checklist

### Application

- [ ] Passwords are securely hashed.
- [ ] Authentication is enforced.
- [ ] Authorization is enforced server-side.
- [ ] Input validation is implemented.
- [ ] Secure HTTP headers are configured.
- [ ] CORS is restricted.
- [ ] Rate limiting is configured.

### Data

- [ ] Database access follows least privilege.
- [ ] Tenant isolation is enforced.
- [ ] Uploaded files are validated.
- [ ] Sensitive data is protected.
- [ ] Backups are protected.
- [ ] Database network access is restricted.

### Infrastructure

- [ ] HTTPS is enabled.
- [ ] Secrets are stored securely.
- [ ] AWS IAM permissions are restricted.
- [ ] Docker containers use appropriate permissions.
- [ ] Security groups are reviewed.
- [ ] Dependencies are checked for vulnerabilities.

### Integrations

- [ ] AI provider credentials are protected.
- [ ] MCP operations enforce authorization.
- [ ] External provider credentials are protected.
- [ ] Background jobs preserve tenant context.

### Operations

- [ ] Security audit logging is enabled.
- [ ] Security monitoring is configured.
- [ ] Incident response procedures are documented.
- [ ] Security testing is performed.
- [ ] Dependency updates are reviewed.

## 20. Implementation Roadmap

| Phase | Security work |
|---|---|
| 1 | Implement authentication |
| 2 | Implement role-based authorization |
| 3 | Enforce tenant isolation |
| 4 | Secure API endpoints |
| 5 | Configure CORS and rate limiting |
| 6 | Secure database and Redis access |
| 7 | Implement file upload validation |
| 8 | Configure secrets management |
| 9 | Secure AI and MCP integrations |
| 10 | Implement audit logging |
| 11 | Secure Docker and AWS infrastructure |
| 12 | Add automated security testing |
| 13 | Perform production security review |

## 21. Important Design Principles

1. Security must be enforced by the backend.
2. Authentication and authorization are separate responsibilities.
3. Users must access only their permitted organization resources.
4. Passwords must never be stored in plain text.
5. Secrets must never be committed to source control.
6. Every uploaded file must be treated as untrusted.
7. AI must not make authorization decisions.
8. MCP tools must follow the same security rules as backend APIs.
9. Database and infrastructure access must follow least privilege.
10. Security controls must be tested before production deployment.

**Important:** This document describes the target security requirements for TERRAMIND. It does not confirm that all listed security controls have already been implemented or independently audited.