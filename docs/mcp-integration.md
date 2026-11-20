# MCP Integration

## 1. Overview

TERRAMIND will use the **Model Context Protocol (MCP)** to provide a standardized way for AI assistants to interact with application capabilities and geospatial information.

MCP allows AI applications to communicate with external tools and data sources through a consistent protocol.

Instead of allowing an AI model to access the database or backend directly, TERRAMIND can expose selected application operations through an MCP server.

Examples include:

- Retrieving authorized project information.
- Listing geographical areas.
- Searching satellite datasets.
- Retrieving NDVI analysis results.
- Retrieving change detection results.
- Generating geospatial reports.
- Explaining analysis results using verified application data.

MCP integration is a planned capability. The actual MCP server, tools, authentication, and transport configuration must be implemented and tested.

## 2. Why TERRAMIND Needs MCP

The platform will contain several types of geospatial information and processing capabilities.

An AI assistant could help users understand and interact with this information through natural-language requests.

For example:

**User request:**

> Show me the latest NDVI analysis for my selected project.

**Expected workflow:**

1. The AI assistant identifies the user's request.
2. The assistant selects an appropriate MCP tool.
3. The MCP server receives the tool request.
4. The backend validates the user's identity and permissions.
5. The backend retrieves the authorized NDVI results.
6. The MCP server returns structured information.
7. The AI assistant explains the results.

The AI model should not directly access PostgreSQL, PostGIS, Redis, or internal infrastructure.

## 3. MCP Architecture

The proposed architecture separates the AI application, MCP communication layer, and application backend.

```text
+--------------------------------------+
|             User Interface           |
|                                      |
|       Next.js AI Assistant           |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|             AI Integration           |
|                                      |
|       AI Provider / Model            |
|                                      |
|       Tool Selection                 |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|              MCP Client              |
|                                      |
|       MCP Connection Management      |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|              MCP Server              |
|                                      |
|       Tools                          |
|       Resources                      |
|       Prompts                        |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|          TERRAMIND Backend          |
|                                      |
|       Authentication                |
|       Authorization                 |
|       Business Logic                 |
|       Geospatial Services            |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|           Application Data           |
|                                      |
|       PostgreSQL / PostGIS           |
|       Redis                          |
|       Object Storage                 |
+--------------------------------------+
```

### Main components

| Component | Responsibility |
|---|---|
| Next.js AI Assistant | Provides the user interface |
| AI Provider | Understands requests and decides when to use tools |
| MCP Client | Connects to MCP servers |
| MCP Server | Exposes approved tools, resources, and prompts |
| Backend | Handles authentication, authorization, and business logic |
| Database | Stores application and geospatial information |
| Object Storage | Stores raster files, datasets, and generated reports |

The AI provider and MCP client may be implemented as part of the same AI integration service or as separate components.

## 4. MCP Core Concepts

MCP provides three important server capabilities.

### 4.1 Tools

Tools allow an AI application to request specific operations.

Examples:

- `get_project_details`
- `list_project_areas`
- `search_satellite_datasets`
- `get_ndvi_statistics`
- `get_change_detection_results`
- `generate_analysis_report`

Tools can retrieve information or initiate approved operations.

Every tool must validate its input and enforce backend authorization.

### 4.2 Resources

Resources provide structured information that an MCP client can read.

Possible TERRAMIND resources include:

| Resource | Description |
|---|---|
| Project metadata | Project name, description, and status |
| Area metadata | Selected geographical area information |
| Dataset metadata | Satellite dataset details |
| Analysis metadata | Analysis type, status, and timestamps |
| NDVI metadata | NDVI statistics and processing information |
| Report metadata | Generated report information |

Resources must follow the same access-control rules as the application APIs.

### 4.3 Prompts

Prompts provide reusable instructions for common AI workflows.

Examples:

- Geospatial assistant.
- NDVI analysis explanation.
- Satellite imagery summary.
- Change detection explanation.
- Geospatial report generation.

Prompts help standardize AI interactions, but they do not replace application validation or authorization.

## 5. Planned MCP Folder Structure

The following is a proposed structure for the backend.

```text
backend/
└── app/
    ├── mcp/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── server.py
    │   ├── api_client.py
    │   ├── tools/
    │   │   ├── __init__.py
    │   │   ├── projects.py
    │   │   ├── areas.py
    │   │   ├── datasets.py
    │   │   ├── ndvi.py
    │   │   ├── change_detection.py
    │   │   └── reports.py
    │   ├── resources/
    │   │   ├── __init__.py
    │   │   ├── projects.py
    │   │   ├── datasets.py
    │   │   └── analysis.py
    │   ├── prompts/
    │   │   ├── __init__.py
    │   │   ├── geospatial.py
    │   │   ├── ndvi.py
    │   │   └── reports.py
    │   └── tests/
    │       ├── __init__.py
    │       ├── test_server.py
    │       ├── test_tools.py
    │       ├── test_resources.py
    │       └── test_authorization.py
    │
    ├── api/
    ├── core/
    ├── models/
    ├── schemas/
    └── services/
```

This structure is a target design. Adjust it to match the existing backend architecture before creating directories or moving existing code.

## 6. MCP Transport

MCP supports different communication transports.

### 6.1 Standard Input / Output (stdio)

stdio is suitable when an MCP client launches and communicates with a local MCP server process.

Typical use cases:

- Local development.
- Developer tools.
- Local AI assistant integrations.
- Testing an MCP server.

The MCP server communicates through standard input and output.

Do not print application logs or debugging messages to standard output when using stdio. Use standard error or a configured logging system.

### 6.2 Streamable HTTP

Streamable HTTP is suitable for remote MCP server deployments.

Typical use cases:

- Cloud-hosted MCP services.
- Remote AI application connections.
- Multiple authorized users.
- Containerized deployments.

The MCP server exposes an HTTP endpoint using the transport supported by the selected MCP SDK.

### 6.3 Transport selection

| Environment | Recommended transport |
|---|---|
| Local development | stdio or Streamable HTTP |
| Automated testing | stdio or an HTTP test client |
| Docker development | Streamable HTTP where remote access is needed |
| AWS production | Authenticated Streamable HTTP |

Select the transport based on the MCP SDK version and deployment requirements.

Do not assume older HTTP+SSE examples are interchangeable with the current Streamable HTTP transport.

## 7. MCP Tools for TERRAMIND

Tools should expose specific application operations rather than unrestricted infrastructure access.

### 7.1 Project tools

| Tool | Description | Access |
|---|---|---|
| `get_project_details` | Retrieve project information | Read |
| `list_user_projects` | List accessible projects | Read |
| `get_project_statistics` | Retrieve project statistics | Read |

Example request:

```json
{
  "project_id": "project-123"
}
```

Example response:

```json
{
  "project_id": "project-123",
  "name": "Colombo Development Project",
  "status": "active"
}
```

The example values are illustrative. The actual response must use the application's verified schema.

### 7.2 Area tools

| Tool | Description | Access |
|---|---|---|
| `list_project_areas` | List areas belonging to a project | Read |
| `get_area_details` | Retrieve area information | Read |
| `get_area_boundary` | Retrieve a permitted area boundary | Read |
| `get_area_statistics` | Retrieve calculated area statistics | Read |

Example request:

```json
{
  "project_id": "project-123",
  "area_id": "area-456"
}
```

Example response:

```json
{
  "area_id": "area-456",
  "name": "Test Area",
  "geometry_type": "Polygon",
  "area_hectares": 125.5
}
```

### 7.3 Satellite dataset tools

| Tool | Description | Access |
|---|---|---|
| `search_satellite_datasets` | Search available satellite data | Read |
| `get_dataset_details` | Retrieve dataset metadata | Read |
| `list_dataset_assets` | List permitted dataset assets | Read |
| `get_latest_satellite_capture` | Retrieve the latest matching capture | Read |

Example request:

```json
{
  "area_id": "area-456",
  "collection": "sentinel-2-l2a",
  "limit": 10
}
```

The actual collection identifiers and search parameters must match the configured STAC providers.

### 7.4 NDVI tools

| Tool | Description | Access |
|---|---|---|
| `get_ndvi_statistics` | Retrieve NDVI statistics | Read |
| `get_ndvi_summary` | Retrieve an NDVI summary | Read |
| `compare_ndvi_results` | Compare two NDVI results | Read |
| `get_ndvi_time_series` | Retrieve historical NDVI values | Read |

Example request:

```json
{
  "analysis_id": "ndvi-789"
}
```

Example response:

```json
{
  "analysis_id": "ndvi-789",
  "mean_ndvi": 0.62,
  "minimum_ndvi": 0.12,
  "maximum_ndvi": 0.91,
  "valid_pixel_percentage": 96.5
}
```

These values are examples, not actual analysis results.

### 7.5 Change detection tools

| Tool | Description | Access |
|---|---|---|
| `get_change_detection_results` | Retrieve change detection results | Read |
| `get_change_statistics` | Retrieve change statistics | Read |
| `compare_capture_dates` | Compare selected capture dates | Read |

Change detection tools must return the processing method, input datasets, dates, and relevant quality information.

### 7.6 Report tools

| Tool | Description | Access |
|---|---|---|
| `get_report_details` | Retrieve report information | Read |
| `generate_analysis_report` | Start report generation | Write |
| `get_report_status` | Check report generation status | Read |

Report generation changes application state. It must require explicit authorization and appropriate confirmation where necessary.

## 8. Tool Implementation Design

Each MCP tool should follow a predictable structure:

1. Define its name and description.
2. Define and validate its input schema.
3. Retrieve the authenticated user context.
4. Verify organization and project permissions.
5. Call the appropriate backend service.
6. Format the result.
7. Return a structured response.
8. Record relevant audit information.

### Example tool workflow

The following is illustrative pseudocode. It is not a complete MCP SDK implementation.

```python
async def get_ndvi_statistics(
    user_context,
    analysis_id: str,
):
    # Validate the supplied analysis identifier.
    if not analysis_id:
        raise ValueError("Analysis ID is required")

    # Retrieve the analysis using the authorized
    # backend service.
    analysis = await analysis_service.get_authorized_analysis(
        user=user_context,
        analysis_id=analysis_id,
    )

    if analysis is None:
        raise ValueError("Analysis not found")

    # Return only the information the user
    # is authorized to access.
    return {
        "analysis_id": analysis.id,
        "mean_ndvi": analysis.mean_ndvi,
        "minimum_ndvi": analysis.minimum_ndvi,
        "maximum_ndvi": analysis.maximum_ndvi,
    }
```

Important:

- `analysis_service.get_authorized_analysis` represents a proposed service operation.
- The actual authentication context must be established by the server integration.
- The actual MCP SDK registration and return types must follow the installed SDK version.
- Do not trust a project ID or organization ID supplied by the AI model.

## 9. Backend Integration

The MCP server should reuse existing application services wherever possible.

```text
MCP Server
    |
    v
Application Service Layer
    |
    +---- Project Service
    |
    +---- Area Service
    |
    +---- Dataset Service
    |
    +---- Raster Service
    |
    +---- NDVI Service
    |
    +---- Change Detection Service
    |
    +---- Report Service
    |
    v
Database / Storage
```

### Integration principles

- Reuse business logic instead of duplicating it inside MCP tools.
- Use the same authorization rules as REST API endpoints.
- Keep database access inside the backend service layer.
- Validate every tool input.
- Return only necessary information.
- Keep long-running processing operations asynchronous.
- Record tool execution and failures.

MCP should be an additional interface to the application, not a replacement for the backend API.

## 10. MCP Resources

Resources provide a structured way to expose application information.

Proposed resource categories:

### Project resource

```text
aleph://projects/{project_id}
```

Contains:

- Project name.
- Description.
- Status.
- Creation date.
- Authorized project metadata.

### Area resource

```text
aleph://areas/{area_id}
```

Contains:

- Area name.
- Geometry type.
- Area size.
- Coordinate reference system.
- Associated project metadata.

### Dataset resource

```text
aleph://datasets/{dataset_id}
```

Contains:

- Dataset identifier.
- Provider.
- Collection.
- Acquisition date.
- Processing information.
- Asset metadata.

### Analysis resource

```text
aleph://analyses/{analysis_id}
```

Contains:

- Analysis identifier.
- Analysis type.
- Processing status.
- Input datasets.
- Result metadata.
- Quality information.

Resource URI patterns are proposed identifiers. Their actual templates and resolution behavior must be implemented using the selected MCP SDK.

## 11. MCP Prompts

Reusable prompts can support common geospatial workflows.

### 11.1 Geospatial assistant

Purpose:

Help users understand their projects, geographical areas, datasets, and analysis results.

Expected behavior:

- Ask for missing project or area context.
- Retrieve information through authorized tools.
- Explain results in simple language.
- Avoid inventing missing geospatial information.

### 11.2 NDVI explanation

Purpose:

Explain NDVI analysis results.

The assistant should consider:

- Mean NDVI.
- Minimum and maximum NDVI.
- Valid pixel percentage.
- Acquisition date.
- Satellite source.
- Cloud masking.
- Processing methodology.

The assistant must explain that NDVI is a spectral vegetation index, not a direct measurement of plant health or agricultural productivity.

### 11.3 Change detection explanation

Purpose:

Explain differences between two selected observations.

The assistant should consider:

- First observation date.
- Second observation date.
- Input imagery.
- Change detection method.
- Detected changes.
- Data quality.
- Processing limitations.

The assistant must distinguish actual calculated results from possible explanations.

### 11.4 Report generation

Purpose:

Help users create reports from authorized application results.

The assistant should:

1. Identify the requested project and analysis.
2. Retrieve the relevant information.
3. Check whether required results are available.
4. Generate a report through an authorized operation.
5. Return the report status or location.

## 12. Authentication and Authorization

MCP integration must follow the same security model as the main application.

### Authentication

For remote MCP connections, use an appropriate authentication mechanism supported by the selected MCP transport and SDK.

Possible requirements include:

- Secure authentication tokens.
- Token expiration.
- Token validation.
- Secure credential handling.
- TLS for remote connections.
- Appropriate client identity verification.

Do not assume that a user authenticated in the Next.js application is automatically authenticated to a separate remote MCP server.

The application must establish a trusted user context for each request.

### Authorization

Every tool and resource must verify:

- User identity.
- Organization membership.
- Project access.
- User role.
- Required permission.
- Resource ownership or sharing rules.

Example:

```text
User Request
     |
     v
Authenticate User
     |
     v
Identify Organization
     |
     v
Check Project Permission
     |
     v
Check Requested Operation
     |
     +---- Unauthorized ---> Reject Request
     |
     v
Execute Backend Service
     |
     v
Return Authorized Result
```

### Multi-tenant security

TERRAMIND will support multiple organizations.

MCP operations must not allow one organization to access another organization's data.

Tenant context must be derived from a trusted authenticated identity and verified membership, not accepted directly from untrusted tool arguments.

## 13. AI and MCP Interaction

The AI model should decide when an available tool is useful.

The MCP server should execute only the operation requested through the validated tool interface.

Example:

**User:**

> What is the average NDVI value for my latest analysis?

**Workflow:**

1. Next.js sends the user's request to the AI integration service.
2. The AI model identifies the need for NDVI information.
3. The AI integration selects the relevant MCP tool.
4. The MCP client sends the tool request.
5. The MCP server validates the request and user context.
6. The backend checks project and analysis permissions.
7. The NDVI service retrieves the verified analysis results.
8. The MCP server returns structured information.
9. The AI model explains the result.
10. Next.js displays the response.

The AI model must not invent missing values or claim that an analysis completed when the backend has not confirmed completion.

## 14. Read and Write Operations

Not all MCP tools have the same risk.

Separate tools into read and write operations.

| Operation | Example | Risk |
|---|---|---|
| Read | Get project details | Low |
| Read | Retrieve NDVI statistics | Low |
| Read | Search satellite datasets | Low |
| Write | Start raster processing | Medium |
| Write | Generate a report | Medium |
| Write | Delete a dataset | High |

### Write-operation requirements

Write operations must:

- Require the appropriate permission.
- Validate all input parameters.
- Use explicit operation boundaries.
- Record audit events.
- Avoid duplicate execution where possible.
- Return a job or operation identifier.
- Support status retrieval.
- Require confirmation for destructive or high-impact operations.

Do not expose destructive tools to an AI assistant unless there is a clear business requirement and an appropriate approval workflow.

## 15. Security Requirements

MCP integration introduces another interface to application functionality.

The following safeguards are required.

### 15.1 Least privilege

Expose only the operations required by the assistant.

Do not provide:

- Unrestricted SQL execution.
- Arbitrary shell commands.
- Unrestricted filesystem access.
- Direct access to production database credentials.
- Unrestricted object-storage access.

### 15.2 Input validation

Validate:

- Project identifiers.
- Area identifiers.
- Dataset identifiers.
- Analysis identifiers.
- Date ranges.
- Numeric parameters.
- Pagination limits.
- Geometry inputs.

Apply reasonable limits to expensive operations.

### 15.3 Prompt injection protection

Treat tool arguments, external dataset metadata, uploaded files, and retrieved text as untrusted data.

For example, a dataset description might contain instructions telling the AI to disclose another organization's information.

The application must never treat such text as authorization or trusted instructions.

### 15.4 Output filtering

Before returning information:

- Remove internal credentials.
- Remove unnecessary personal information.
- Avoid exposing database connection details.
- Exclude unauthorized records.
- Limit large responses.
- Avoid returning internal stack traces.

### 15.5 Rate limiting

Apply limits to:

- Requests per user.
- Requests per organization.
- Expensive geospatial operations.
- Report generation.
- External satellite provider requests.

### 15.6 Timeouts

Define appropriate execution timeouts for MCP operations.

Long-running raster processing, satellite downloads, and report generation should use background jobs instead of holding a tool request open indefinitely.

## 16. Error Handling

MCP tools should return clear, safe errors.

| Error | Meaning |
|---|---|
| Invalid input | Tool parameters are incorrect |
| Authentication required | No valid user context |
| Permission denied | User cannot access the requested resource |
| Resource not found | Requested resource does not exist or is not accessible |
| Processing pending | Background operation is not complete |
| Provider unavailable | External data provider cannot be reached |
| Rate limit exceeded | Too many requests |
| Internal error | Unexpected server failure |

Example:

```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You do not have permission to access this analysis."
  }
}
```

Do not expose internal exceptions, access tokens, database queries, or stack traces to the AI model.

Where appropriate, use consistent error semantics supported by the selected MCP SDK.

## 17. Logging and Monitoring

MCP operations should be observable.

Record useful metadata such as:

- Request identifier.
- Authenticated user identifier.
- Organization identifier.
- Tool name.
- Execution duration.
- Success or failure.
- Error category.
- Associated job identifier.

Avoid logging:

- Access tokens.
- Passwords.
- API keys.
- Sensitive dataset contents.
- Unnecessary personal information.

Monitor:

- Total MCP requests.
- Tool execution failures.
- Average execution duration.
- Slow tools.
- Unauthorized access attempts.
- Rate-limit events.
- AI tool usage.
- External provider failures.

Integrate MCP monitoring with the platform's general logging and monitoring architecture.

## 18. Testing Strategy

Testing must cover both protocol behavior and application security.

### Unit tests

Test:

- Tool input validation.
- Tool output formatting.
- Service integration.
- Error handling.
- Permission checks.
- Resource resolution.

### MCP integration tests

Test:

- MCP server initialization.
- Client connection.
- Tool discovery.
- Tool invocation.
- Resource discovery and reading.
- Prompt discovery where supported.
- Transport behavior.
- Connection failures.

### Security tests

Test:

- Unauthenticated requests.
- Unauthorized project access.
- Cross-organization access attempts.
- Invalid identifiers.
- Malicious input.
- Excessive requests.
- Sensitive output filtering.

### Example test scenarios

| Scenario | Expected result |
|---|---|
| Authorized user requests project details | Return permitted project information |
| User requests another organization's project | Reject access |
| Invalid analysis ID | Return a safe error |
| NDVI processing is incomplete | Return processing status |
| MCP server is unavailable | Handle connection failure |
| User requests unrestricted SQL | Do not expose such a capability |

## 19. Deployment Architecture

The MCP server can be deployed as a separate service or integrated into an existing backend process, depending on operational requirements.

Proposed deployment:

```text
                 AWS Environment
                       |
                       v
                Application Gateway
                       |
          +------------+------------+
          |                         |
          v                         v
     Next.js Frontend          FastAPI Backend
                                    |
                    +---------------+---------------+
                    |               |               |
                    v               v               v
                MCP Server     Application      Background
                                  Services          Workers
                    |               |               |
                    +---------------+---------------+
                                    |
                                    v
                          PostgreSQL / PostGIS
                                    |
                                    v
                              Object Storage
```

### Deployment requirements

- Use authenticated connections.
- Enable TLS for remote access.
- Keep credentials in a secrets manager.
- Restrict network access.
- Configure health checks.
- Configure request timeouts.
- Apply rate limits.
- Monitor service availability.
- Keep development and production credentials separate.

If the MCP server is deployed separately, define its internal service authentication and network permissions explicitly.

## 20. Environment Variables

The following names are proposed examples. They must be aligned with the actual application settings.

```env
# MCP Configuration

MCP_ENABLED=false

MCP_SERVER_NAME=aleph-next-mcp

MCP_TRANSPORT=streamable-http

MCP_SERVER_HOST=0.0.0.0

MCP_SERVER_PORT=8001

# Internal backend integration

MCP_BACKEND_BASE_URL=http://backend:8000

# Request configuration

MCP_REQUEST_TIMEOUT=30

MCP_MAX_TOOL_RESULT_SIZE=100000

# Authentication configuration

MCP_AUTH_ENABLED=true
```

Security requirements:

- Do not store passwords or tokens directly in source code.
- Do not commit production credentials.
- Do not expose private MCP configuration through `NEXT_PUBLIC_` variables.
- Use the platform's secret-management system in production.
- Validate the actual environment variable names against the implemented configuration.

## 21. Implementation Roadmap

Implement MCP integration gradually.

| Phase | Work |
|---|---|
| 1 | Select and verify the MCP SDK |
| 2 | Create the MCP server structure |
| 3 | Configure the selected transport |
| 4 | Implement authentication |
| 5 | Implement project and area read tools |
| 6 | Implement dataset search tools |
| 7 | Implement NDVI and analysis tools |
| 8 | Implement resources and prompts |
| 9 | Add report-generation tools |
| 10 | Add authorization and tenant-isolation tests |
| 11 | Add monitoring and audit logging |
| 12 | Deploy and validate the MCP service |

Begin with read-only operations before introducing write operations.

## 22. Verification Checklist

Before considering MCP integration complete, verify:

- [ ] MCP SDK and version are documented.
- [ ] MCP server starts successfully.
- [ ] Selected transport works.
- [ ] MCP client can connect.
- [ ] Available tools can be discovered.
- [ ] Tool inputs are validated.
- [ ] Project access is authorized.
- [ ] Organization isolation is enforced.
- [ ] Resources return authorized information.
- [ ] Prompts are available where required.
- [ ] NDVI results are retrieved from verified backend services.
- [ ] Long-running operations use background jobs.
- [ ] Write operations require appropriate permissions.
- [ ] Audit logging is implemented.
- [ ] Sensitive data is filtered.
- [ ] Rate limits and timeouts are configured.
- [ ] Integration and security tests pass.
- [ ] Production transport and authentication are configured.

## 23. Important Design Principles

The following principles should guide all MCP development in TERRAMIND:

1. MCP is an additional application integration layer, not a replacement for REST APIs.
2. The backend remains responsible for business logic and authorization.
3. Every tool must validate its input.
4. Every request must use a trusted authentication context.
5. Organization and project isolation must be enforced.
6. AI-generated tool arguments must be treated as untrusted input.
7. Tools should expose specific operations instead of unrestricted system access.
8. Long-running geospatial operations should use background processing.
9. AI explanations must be based on verified application results.
10. MCP implementation must be tested against the selected SDK and transport versions.

**Important:** This document describes the target MCP architecture for TERRAMIND. It does not confirm that the MCP server, tools, resources, prompts, or deployment configuration already exist in the repository.