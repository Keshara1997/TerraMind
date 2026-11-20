# Monitoring and Observability

## 1. Overview

Monitoring and observability are essential for maintaining the reliability, availability, and performance of TERRAMIND.

TERRAMIND is designed to include several interconnected services:

- Next.js frontend.
- FastAPI backend.
- PostgreSQL database.
- PostGIS geospatial extension.
- Redis.
- Background workers.
- Satellite data integrations.
- Raster processing services.
- AI and MCP integrations.
- AWS infrastructure.

Monitoring should help developers and administrators identify problems before they significantly affect users.

The main objectives are:

1. Monitor application availability.
2. Identify application errors.
3. Measure API performance.
4. Monitor database health.
5. Monitor background processing.
6. Track geospatial processing failures.
7. Monitor external provider availability.
8. Track infrastructure resource usage.
9. Support troubleshooting and incident investigation.

This document describes the target monitoring architecture. The actual monitoring services and configurations must be verified in the repository.

## 2. Monitoring Architecture

The proposed architecture collects information from application components and infrastructure.

```text
+--------------------------------------+
|             TERRAMIND               |
|                                      |
|  Next.js Frontend                    |
|  FastAPI Backend                     |
|  MCP Server                          |
|  Background Workers                  |
|  Geospatial Processing               |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|          Monitoring Layer            |
|                                      |
|  Application Logs                    |
|  Metrics                             |
|  Distributed Traces                  |
|  Health Checks                       |
|  Error Tracking                      |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|       Monitoring Infrastructure      |
|                                      |
|  Prometheus                          |
|  Grafana                             |
|  CloudWatch                          |
|  OpenTelemetry                       |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
|          Alerts and Reports          |
|                                      |
|  Service Availability                |
|  Application Errors                  |
|  Resource Usage                      |
|  Processing Failures                 |
|  Performance Problems                |
+--------------------------------------+
```

## 3. Monitoring Categories

TERRAMIND should monitor the following categories.

| Category | What to monitor |
|---|---|
| Application | API errors and application exceptions |
| Frontend | Page errors and frontend availability |
| API | Request count, latency, and response codes |
| Database | Connections, queries, and storage |
| Redis | Memory, connections, and cache performance |
| Background workers | Queue size and job failures |
| Geospatial processing | Raster and vector processing status |
| Satellite providers | Provider availability and request failures |
| AI integration | Request failures, latency, and usage |
| MCP | Tool execution and connection failures |
| Infrastructure | CPU, memory, disk, and network |
| Security | Authentication failures and suspicious activity |

## 4. Application Logging

Application logging records events that happen inside the system.

Logs are useful when investigating errors and understanding application behavior.

### 4.1 Backend logging

The FastAPI backend should record:

- Application startup and shutdown.
- API requests.
- Authentication failures.
- Authorization failures.
- Database connection errors.
- Background job execution.
- Geospatial processing failures.
- External provider failures.
- Unexpected application exceptions.

Use structured logging instead of relying only on plain text messages.

Example:

```python
import logging

logger = logging.getLogger(__name__)

logger.info(
    "Raster processing started",
    extra={
        "job_id": "job-123",
        "dataset_id": "dataset-456",
    },
)
```

The example illustrates the desired logging information. The actual logging formatter must serialize structured fields correctly.

### 4.2 Frontend logging

The Next.js application should monitor:

- JavaScript errors.
- Failed API requests.
- Authentication problems.
- Map rendering failures.
- Raster visualization errors.
- Unexpected application crashes.

Avoid logging private user information or authentication tokens.

### 4.3 Log levels

| Level | Purpose |
|---|---|
| DEBUG | Detailed development information |
| INFO | Normal application events |
| WARNING | Unexpected but recoverable conditions |
| ERROR | Operation failures |
| CRITICAL | Severe failures affecting application availability |

Production logging should use an appropriate log level to avoid excessive output.

### 4.4 Example structured log

```json
{
  "timestamp": "2026-11-20T10:30:00Z",
  "level": "INFO",
  "service": "aleph-backend",
  "event": "raster_processing_completed",
  "job_id": "job-123",
  "duration_ms": 24500,
  "status": "success"
}
```

All example identifiers and timestamps are illustrative.

## 5. API Monitoring

The FastAPI application should collect metrics for API requests.

Important measurements include:

- Total requests.
- Successful requests.
- Failed requests.
- HTTP response codes.
- Request duration.
- Requests per endpoint.
- Slow requests.
- Authentication failures.

### Example API metrics

| Metric | Description |
|---|---|
| `http_requests_total` | Total HTTP requests |
| `http_request_duration_seconds` | Request processing duration |
| `http_requests_in_progress` | Currently active requests |
| `http_request_errors_total` | Failed HTTP requests |

These are proposed metric names. Use the naming conventions of the selected instrumentation library.

### API response time

Response time helps identify slow endpoints.

Example targets for initial performance planning:

| Endpoint category | Initial target |
|---|---:|
| Health check | Under 200 ms |
| Simple read API | Under 500 ms |
| Project metadata | Under 500 ms |
| Dataset search | Under 2 seconds |
| Analysis status | Under 500 ms |

These are planning targets, not measured performance guarantees.

Raster processing and satellite downloads should be handled asynchronously rather than treated as ordinary short API requests.

## 6. Health Checks

Health checks help determine whether a service is operating correctly.

### 6.1 Backend health

A basic health endpoint:

```http
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "service": "aleph-backend"
}
```

### 6.2 Readiness check

A readiness endpoint should verify whether the service can accept requests.

```http
GET /health/ready
```

Possible checks:

- Database connectivity.
- Required Redis connectivity.
- Required dependencies.
- Application initialization.

### 6.3 Liveness check

A liveness endpoint should verify whether the application process is alive.

```http
GET /health/live
```

Liveness checks should not depend on every external service being available.

### 6.4 Service health table

| Service | Health information |
|---|---|
| Frontend | Application availability |
| Backend | Process and API availability |
| PostgreSQL | Database connectivity |
| Redis | Cache connectivity |
| Worker | Worker process availability |
| MCP | MCP service availability |
| Satellite integration | Provider connectivity |
| Object storage | Storage accessibility |

Do not expose sensitive infrastructure information through public health endpoints.

## 7. Database Monitoring

PostgreSQL and PostGIS are important components of TERRAMIND.

Database monitoring should include:

- Active connections.
- Maximum connections.
- Slow queries.
- Query execution time.
- Database size.
- Table size.
- Index usage.
- Lock waits.
- Deadlocks.
- Transaction activity.
- Connection pool utilization.
- Replication health, if replication is configured.

### Example PostgreSQL checks

Active connections:

```sql
SELECT
    state,
    COUNT(*) AS connection_count
FROM pg_stat_activity
GROUP BY state;
```

Database size:

```sql
SELECT
    pg_size_pretty(
        pg_database_size(current_database())
    ) AS database_size;
```

Slow running queries:

```sql
SELECT
    pid,
    now() - query_start AS duration,
    state,
    query
FROM pg_stat_activity
WHERE state = 'active'
  AND query_start IS NOT NULL
ORDER BY duration DESC;
```

Query monitoring must follow the database's privacy and security requirements. Avoid exposing query text containing sensitive values in general-purpose dashboards.

### PostGIS monitoring

Monitor:

- Spatial query execution time.
- Spatial index usage.
- Large geometry operations.
- Invalid geometry processing failures.
- Spatial table growth.
- Expensive geometry transformations.

Use `EXPLAIN` and `EXPLAIN ANALYZE` when investigating query performance.

Do not execute expensive analysis queries against production data without considering their impact.

## 8. Redis Monitoring

Redis may be used for:

- Caching.
- Background job coordination.
- Temporary application data.
- Rate limiting.
- Task state.

Monitor:

| Metric | Purpose |
|---|---|
| Memory usage | Detect memory pressure |
| Connected clients | Monitor active connections |
| Cache hit rate | Understand cache effectiveness |
| Evicted keys | Identify memory pressure |
| Commands per second | Measure activity |
| Queue length | Monitor pending jobs |
| Redis availability | Detect service failures |

Example Redis command:

```bash
redis-cli INFO memory
```

Check Redis connectivity:

```bash
redis-cli PING
```

Expected response:

```text
PONG
```

## 9. Background Job Monitoring

TERRAMIND will use background workers for operations that take longer than normal API requests.

Examples:

- Satellite dataset downloads.
- Raster processing.
- NDVI calculation.
- Change detection.
- Report generation.
- Large exports.

Monitor:

- Pending jobs.
- Running jobs.
- Completed jobs.
- Failed jobs.
- Retried jobs.
- Job execution duration.
- Worker availability.
- Queue processing time.

### Job lifecycle

```text
Job Submitted
      |
      v
   Pending
      |
      v
   Running
      |
      +-------> Failed
      |            |
      |            v
      |          Retry
      |            |
      |            v
      |          Running
      |
      v
  Completed
```

The actual job states depend on the selected task-processing system.

### Example job metadata

```json
{
  "job_id": "job-123",
  "job_type": "ndvi_analysis",
  "status": "completed",
  "started_at": "2026-11-20T10:00:00Z",
  "completed_at": "2026-11-20T10:02:30Z",
  "duration_seconds": 150
}
```

### Failed job handling

The system should:

1. Record the failure reason.
2. Store the relevant job identifier.
3. Apply a retry policy where appropriate.
4. Avoid infinite retry loops.
5. Send permanently failed jobs to a dead-letter mechanism if supported.
6. Notify administrators when necessary.

## 10. Geospatial Processing Monitoring

Geospatial processing requires additional monitoring because operations can consume significant CPU, memory, storage, and processing time.

Monitor:

### Raster processing

- Raster processing duration.
- Input file size.
- Output file size.
- Number of bands.
- Raster dimensions.
- NoData percentage.
- Processing failures.
- Temporary storage usage.

### NDVI analysis

- Analysis duration.
- Source dataset.
- Acquisition date.
- Cloud masking status.
- Valid pixel percentage.
- Output generation status.

### Change detection

- Input dataset availability.
- Comparison date range.
- Processing duration.
- Output generation status.
- Processing errors.

### Vector processing

- Geometry validation failures.
- Geometry repair operations.
- Feature count.
- Spatial query duration.
- Invalid geometry count.

Scientific quality metrics should be monitored separately from infrastructure health. A successful processing job does not automatically mean that its scientific output is valid.

## 11. Satellite Provider Monitoring

TERRAMIND may integrate with external satellite data providers.

External provider failures can affect dataset search and download operations.

Monitor:

- Provider availability.
- Request latency.
- Authentication failures.
- HTTP response codes.
- Search failures.
- Download failures.
- Rate-limit responses.
- Timeout errors.

Example providers:

- Copernicus Data Space.
- Microsoft Planetary Computer.
- Earth Search.
- Other authorized STAC-compatible providers.

Provider-specific availability and performance should be measured rather than assumed.

Implement reasonable request timeouts and retry policies.

Do not retry permanent authorization or invalid-request errors indefinitely.

## 12. AI and MCP Monitoring

AI and MCP integrations require separate monitoring because they depend on external services and tool execution.

### AI monitoring

Track:

- Request count.
- Request duration.
- Provider errors.
- Model response failures.
- Token usage where available.
- Estimated usage cost.
- Tool invocation count.
- Timeout count.

### MCP monitoring

Track:

- MCP server availability.
- Client connection failures.
- Tool execution count.
- Tool execution duration.
- Tool errors.
- Authorization failures.
- Resource access failures.

Never log API keys, access tokens, or private conversation contents unnecessarily.

## 13. Monitoring Technology Stack

The following tools are possible choices for the target architecture.

| Technology | Purpose |
|---|---|
| Python logging | Backend application logs |
| Prometheus | Metrics collection |
| Grafana | Metrics dashboards |
| OpenTelemetry | Traces and instrumentation |
| AWS CloudWatch | AWS infrastructure and application monitoring |
| Sentry | Frontend and backend error tracking |

These are proposed options, not confirmed dependencies.

### Prometheus

Prometheus can collect metrics from instrumented services.

Example configuration:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "aleph-backend"
    metrics_path: "/metrics"
    static_configs:
      - targets:
          - "backend:8000"
```

The backend must expose a compatible metrics endpoint before this configuration can work.

### Grafana

Grafana can visualize metrics collected by Prometheus or other supported data sources.

Possible dashboards:

1. Application overview.
2. API performance.
3. Database performance.
4. Redis health.
5. Background worker status.
6. Geospatial processing.
7. AI and MCP usage.
8. Infrastructure health.

### OpenTelemetry

OpenTelemetry can provide distributed tracing across multiple services.

Example request flow:

```text
Next.js Frontend
       |
       v
FastAPI API
       |
       v
Project Service
       |
       v
PostgreSQL
```

A trace can help identify which part of the request takes the most time.

## 14. AWS CloudWatch Monitoring

When TERRAMIND is deployed on AWS, CloudWatch can monitor infrastructure and application logs.

Possible monitored services:

- EC2.
- ECS, if used.
- RDS.
- ElastiCache, if used.
- Application Load Balancer.
- S3.
- CloudWatch Logs.

Important infrastructure metrics include:

| Service | Metrics |
|---|---|
| EC2 | CPU, network, disk-related metrics where available |
| RDS | CPU, connections, storage, read/write latency |
| ECS | CPU and memory utilization |
| ALB | Request count, response time, HTTP errors |
| S3 | Storage and request metrics where enabled |
| ElastiCache | Memory, connections, CPU, cache activity |

Configure alarms for important service failures and resource limits.

## 15. Alerting Strategy

Alerts should notify administrators when important problems occur.

Examples:

| Alert | Condition |
|---|---|
| Backend unavailable | Health check fails repeatedly |
| High API error rate | Error rate exceeds configured threshold |
| Slow API | Response time remains above target |
| Database connection pressure | Connections approach configured limits |
| High CPU usage | CPU remains above threshold |
| Worker unavailable | Required worker is not running |
| Queue backlog | Pending jobs exceed operational limits |
| Raster failures | Processing failures exceed threshold |
| Provider unavailable | External provider repeatedly fails |
| Disk pressure | Available storage becomes critically low |

Thresholds must be configured based on actual workload and infrastructure capacity.

### Alert severity

| Severity | Meaning |
|---|---|
| Critical | Major service outage or serious security issue |
| High | Important functionality unavailable |
| Medium | Performance degradation or repeated failures |
| Low | Informational or non-urgent issue |

Avoid sending alerts for every individual recoverable event. Use aggregation and alert grouping to reduce notification noise.

## 16. Performance Monitoring

Performance monitoring helps identify bottlenecks before they affect application reliability.

### Frontend performance

Monitor:

- Page loading time.
- JavaScript errors.
- API response time from the browser.
- Map rendering performance.
- Large image loading.
- Memory usage where observable.

### Backend performance

Monitor:

- Request processing time.
- CPU usage.
- Memory usage.
- Concurrent requests.
- Database query duration.
- External API latency.

### Geospatial performance

Monitor:

- Raster read and write duration.
- Geometry processing time.
- Spatial query performance.
- Temporary storage usage.
- Worker memory consumption.

Use real production measurements to establish performance targets.

## 17. Monitoring Environment Variables

The following are proposed configuration examples.

```env
# Logging

LOG_LEVEL=INFO
LOG_FORMAT=json

# Metrics

METRICS_ENABLED=false
METRICS_PATH=/metrics

# Tracing

TRACING_ENABLED=false
OTEL_SERVICE_NAME=aleph-backend
OTEL_EXPORTER_OTLP_ENDPOINT=

# Error Tracking

SENTRY_DSN=

# Health Checks

HEALTH_CHECK_ENABLED=true
```

These variable names must be aligned with the actual configuration implementation.

Never commit private monitoring credentials or production service tokens.

## 18. Docker Monitoring

For Docker-based development, monitor container status and resource usage.

List running containers:

```bash
docker compose ps
```

View service logs:

```bash
docker compose logs
```

Follow backend logs:

```bash
docker compose logs -f backend
```

View container resource usage:

```bash
docker stats
```

Inspect a specific service:

```bash
docker compose logs --tail=100 backend
```

The service names above are examples. Use the names defined in the actual Compose configuration.

## 19. Incident Response

When a production issue occurs, follow a consistent process.

### Step 1: Identify the problem

Check:

- Application health.
- Error logs.
- API response codes.
- Infrastructure metrics.
- Recent deployments.

### Step 2: Determine the affected service

Identify whether the problem affects:

- Frontend.
- Backend.
- Database.
- Redis.
- Background workers.
- Satellite providers.
- Geospatial processing.
- AI or MCP services.

### Step 3: Investigate the cause

Review relevant logs, traces, and metrics.

Use request IDs and job IDs to connect related events.

### Step 4: Restore service

Apply an appropriate recovery action.

Examples:

- Restart an unhealthy service.
- Restore database connectivity.
- Resolve a failed deployment.
- Restart a worker after investigating its failure.
- Temporarily disable an unavailable external integration.

Do not restart services blindly before collecting relevant diagnostic information.

### Step 5: Verify recovery

Check health endpoints, logs, metrics, and affected functionality.

### Step 6: Document the incident

Record:

- Incident description.
- Start and end time.
- Affected services.
- Root cause.
- Recovery actions.
- Preventive improvements.

## 20. Monitoring Security

Monitoring systems can contain sensitive operational information.

Apply the following controls:

- Restrict dashboard access.
- Protect metrics endpoints.
- Avoid exposing internal service details publicly.
- Redact credentials from logs.
- Restrict log retention and access.
- Protect alerting integrations.
- Use secure communication.
- Audit access to monitoring infrastructure.

Monitoring must not become an alternative route to accessing confidential application data.

## 21. Implementation Roadmap

Implement monitoring in stages.

| Phase | Implementation |
|---|---|
| 1 | Configure structured backend logging |
| 2 | Add application health endpoints |
| 3 | Monitor API request metrics |
| 4 | Monitor PostgreSQL and Redis |
| 5 | Add background worker monitoring |
| 6 | Add geospatial processing metrics |
| 7 | Add frontend error tracking |
| 8 | Integrate Prometheus and Grafana if required |
| 9 | Add distributed tracing |
| 10 | Configure AWS CloudWatch |
| 11 | Configure alerts |
| 12 | Test incident recovery procedures |

Start with basic logging, health checks, and error monitoring before introducing a larger monitoring stack.

## 22. Verification Checklist

- [ ] Backend logs are available.
- [ ] Logs include useful timestamps and service identifiers.
- [ ] Sensitive credentials are excluded from logs.
- [ ] Backend health endpoint works.
- [ ] Readiness and liveness checks are implemented appropriately.
- [ ] API metrics are available.
- [ ] Database connections are monitored.
- [ ] Redis health is monitored.
- [ ] Background jobs expose useful status information.
- [ ] Geospatial processing failures are recorded.
- [ ] Satellite provider errors are recorded.
- [ ] AI and MCP operations are monitored.
- [ ] Frontend errors can be investigated.
- [ ] Infrastructure metrics are available.
- [ ] Important alerts are configured.
- [ ] Monitoring access is secured.
- [ ] Incident recovery procedures are documented.

## 23. Important Design Principles

1. Monitoring should cover the complete application, not only the backend.
2. Logs, metrics, and traces serve different purposes.
3. Every important background job should have a trackable identifier.
4. Expensive geospatial operations require dedicated monitoring.
5. External provider failures should not be mistaken for internal application failures.
6. Monitoring endpoints must be protected.
7. Alerts should focus on actionable problems.
8. Production thresholds must be based on real measurements.
9. Monitoring data must not expose confidential information.
10. Monitoring configuration must be tested before production deployment.

**Important:** This document describes the target monitoring strategy for TERRAMIND. It does not confirm that Prometheus, Grafana, OpenTelemetry, Sentry, CloudWatch alarms, or any other monitoring service is currently configured.