# AWS Deployment Guide

## 1. Overview

This document describes the target AWS deployment architecture for TERRAMIND.

TERRAMIND is a geospatial intelligence application built around:

- Next.js frontend
- FastAPI backend
- PostgreSQL with PostGIS
- Redis for caching and background job coordination
- Background workers for geospatial processing
- Satellite and geospatial data integrations
- AI assistant and MCP integration
- Object storage for raster datasets, reports, and generated files

The deployment should provide:

- Secure access to the application
- Reliable API and frontend services
- Private database and cache access
- Scalable background processing
- Secure storage for geospatial data
- Monitoring and logging
- A repeatable deployment process

**Important:** This document describes the planned AWS architecture. It does not confirm that these AWS resources have already been created or configured.

---

## 2. AWS Architecture

The target architecture uses AWS managed services where they provide a clear operational benefit.

### 2.1 High-Level Architecture

```text
                       Users
                         |
                         |
                    Route 53
                         |
                         |
                  Application Load
                     Balancer
                         |
              HTTPS / TLS (ACM)
                         |
              ---------------------
              |                   |
              |                   |
        Frontend Service     Backend API
          Next.js              FastAPI
              |                   |
              |              ----------
              |              |        |
              |           Redis    PostgreSQL
              |              |       + PostGIS
              |              |
              |          Background
              |            Workers
              |              |
              |              |
              |         Geospatial
              |         Processing
              |              |
              |          S3 Storage
              |
              |
        Browser Application

              Supporting Services
              -------------------
              Amazon ECR
              AWS IAM
              Secrets Manager
              CloudWatch
              GitHub Actions
```

The exact deployment design depends on the selected hosting option.

### 2.2 Main AWS Services

| AWS service | Purpose |
|---|---|
| Amazon EC2 | Virtual machines for application hosting |
| Amazon ECS | Container orchestration |
| AWS Fargate | Managed container compute |
| Amazon ECR | Docker image registry |
| Amazon RDS | Managed PostgreSQL database |
| Amazon ElastiCache | Managed Redis |
| Amazon S3 | Geospatial and application file storage |
| Application Load Balancer | Distributes incoming traffic |
| Amazon Route 53 | DNS management |
| AWS Certificate Manager | HTTPS certificates |
| AWS IAM | Access control and permissions |
| AWS Secrets Manager | Secure application secrets |
| Amazon CloudWatch | Logs, metrics, and alarms |
| AWS VPC | Private network infrastructure |

Not every service is required for the initial deployment.

---

## 3. Deployment Options

TERRAMIND can be deployed using different AWS architectures.

### 3.1 Option A: EC2 with Docker Compose

This option runs the application containers on an EC2 instance.

```text
                  Internet
                     |
                EC2 Instance
                     |
               Docker Compose
                     |
       -----------------------------
       |       |        |          |
    Frontend Backend  PostgreSQL  Redis
                       + PostGIS
                     |
                  Workers
                     |
                    S3
```

Advantages:

- Simple initial setup
- Easy to understand and maintain
- Supports an existing Docker Compose workflow
- Suitable for development and initial production deployments
- Provides control over the server environment

Disadvantages:

- Server maintenance is required
- Application scaling requires additional configuration
- Database availability depends on the selected database architecture
- A single EC2 instance can become a single point of failure

This option can be used for an initial deployment or a small installation.

### 3.2 Option B: ECS with Fargate

Amazon ECS runs the application containers, while Fargate manages the underlying compute infrastructure.

```text
                 Internet
                    |
               Application
               Load Balancer
                    |
             ----------------
             |              |
         Frontend        Backend API
          Task              Task
                            |
                     Background Workers
                            |
                   ------------------
                   |        |       |
                  RDS    Redis      S3
```

Advantages:

- Managed container infrastructure
- Independent service scaling
- No need to manage EC2 operating systems
- Integration with ECR, IAM, and CloudWatch
- Suitable for larger deployments

Disadvantages:

- More AWS configuration
- Additional networking and service configuration
- Costs depend on running tasks and supporting resources
- Requires ECS task definitions and deployment configuration

### 3.3 Deployment Comparison

| Feature | EC2 + Docker Compose | ECS + Fargate |
|---|---|---|
| Initial setup | Simpler | More configuration |
| Server management | Required | Managed compute |
| Container orchestration | Docker Compose | ECS |
| Independent scaling | More manual | Supported |
| Infrastructure control | Higher | More abstracted |
| Operational complexity | Lower initially | Higher initially |
| Production scalability | Requires additional design | Better suited |

### 3.4 Recommended Approach

Start with EC2 and Docker Compose if the immediate goal is to get a working deployment with a manageable setup.

Consider ECS with Fargate when the application requires independent scaling, stronger service isolation, and more managed container operations.

Do not attempt to use Docker Compose commands as a replacement for ECS task definitions. They are different deployment approaches.

---

## 4. AWS Network Architecture

### 4.1 Virtual Private Cloud

Create an AWS Virtual Private Cloud (VPC) for TERRAMIND.

The VPC provides an isolated network for the application infrastructure.

Example:

```text
VPC: 10.0.0.0/16

Public Subnets:
- Public Subnet A
- Public Subnet B

Private Subnets:
- Private Subnet A
- Private Subnet B
```

### 4.2 Public Subnets

Public subnets can contain resources that need controlled internet access.

Examples:

- Application Load Balancer
- NAT Gateway, if required

Do not expose the database or Redis directly to the public internet.

### 4.3 Private Subnets

Private subnets should contain internal application resources.

Examples:

- Backend services
- Background workers
- PostgreSQL database
- Redis cache

The exact placement depends on whether EC2 or ECS is selected.

### 4.4 Security Groups

Security groups control inbound and outbound network traffic.

Example security rules:

| Resource | Port | Allowed source |
|---|---:|---|
| Application Load Balancer | 443 | Internet |
| Application Load Balancer | 80 | Internet, for HTTPS redirection |
| Frontend | Application port | Load Balancer |
| Backend API | Application port | Load Balancer or frontend, as designed |
| PostgreSQL | 5432 | Authorized application security group |
| Redis | 6379 | Authorized application security group |
| SSH | 22 | Restricted administrator IP, if required |

Use security group references instead of opening internal services to all IP addresses.

Do not expose PostgreSQL, Redis, or internal worker ports publicly.

---

## 5. Application Deployment

### 5.1 Frontend

The frontend is built using Next.js.

The deployment process should:

1. Install frontend dependencies.
2. Run the frontend production build.
3. Build a Docker image.
4. Push the image to Amazon ECR.
5. Deploy the container using the selected hosting option.
6. Configure the frontend's API URL.
7. Verify that the application loads correctly.

Example environment variable:

```env
NEXT_PUBLIC_API_URL=https://api.example.com
```

The `NEXT_PUBLIC_` prefix means the value can be exposed to browser-side code. Never put secrets in public frontend variables.

Verify whether the frontend uses Next.js server-side rendering, static generation, or another deployment mode before selecting its container configuration.

### 5.2 Backend API

The backend uses FastAPI.

The deployment process should:

1. Install Python dependencies.
2. Build the backend Docker image.
3. Push the image to Amazon ECR.
4. Configure production environment variables.
5. Configure database and Redis connections.
6. Run database migrations in a controlled deployment step.
7. Start the FastAPI application.
8. Verify health and readiness endpoints.

Example production command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

This is an illustrative command. Confirm the actual Python package path and application entry point in the repository.

### 5.3 Background Workers

Geospatial operations may take longer than normal API requests.

Use separate background workers for operations such as:

- Satellite data downloads
- Raster processing
- NDVI calculations
- Change detection
- Large-area analysis
- Report generation
- Scheduled data processing

Workers should be deployable independently from the API.

For example:

```text
Backend API
    |
    | Submit processing job
    |
 Redis / Task Queue
    |
    |
Background Worker
    |
    | Process geospatial data
    |
 S3 Object Storage
    |
    |
Database Job Status
```

The exact queue and worker implementation must match the actual backend configuration.

### 5.4 MCP Service

If MCP is deployed as a separate service, it should:

- Use authenticated communication.
- Validate the user's identity and organization context.
- Access only authorized tools and resources.
- Avoid exposing internal service ports publicly.
- Record relevant tool execution events.

MCP deployment can be introduced after the core API and geospatial processing services are stable.

---

## 6. Database Deployment

### 6.1 Amazon RDS

Amazon RDS for PostgreSQL can be used for the main application database.

The database must support the PostGIS extension and the required extension version.

Before selecting an RDS engine version:

1. Check the available PostgreSQL versions.
2. Check PostGIS extension compatibility.
3. Verify required spatial functions.
4. Test migrations against the selected engine.
5. Confirm backup and restore requirements.

Do not assume every PostgreSQL feature or extension configuration is identical across local Docker and RDS.

### 6.2 Database Security

Recommended configuration:

- Deploy RDS in private subnets.
- Disable public accessibility.
- Restrict inbound traffic to authorized application security groups.
- Use encryption at rest.
- Require encrypted connections where supported.
- Store credentials in Secrets Manager.
- Use separate database users for different application responsibilities where appropriate.

### 6.3 Database Migrations

Use Alembic for database schema migrations if that is the migration framework configured in the backend.

Example:

```bash
alembic upgrade head
```

Run this command from the correct backend environment and working directory.

Recommended deployment order:

1. Create or verify the database.
2. Confirm database connectivity.
3. Back up the database before a risky migration.
4. Run the migration as a controlled deployment task.
5. Verify migration status.
6. Deploy application services that depend on the new schema.

Do not run migrations independently from every API container during startup.

For production, review migration compatibility with the currently running application version before deployment.

---

## 7. Redis Deployment

Redis can support:

- Caching
- Background job coordination
- Temporary processing state
- Rate-limiting data
- Other short-lived application data

Amazon ElastiCache for Redis or a compatible managed Redis offering can be considered.

Recommended configuration:

- Private network access only
- Authentication and encryption where supported
- Restricted security group rules
- Memory and eviction policy monitoring
- Backup and recovery settings based on the data's importance

Do not use Redis as the only permanent storage location for important application data.

---

## 8. Geospatial File Storage

### 8.1 Amazon S3

Use Amazon S3 to store large geospatial files and generated application outputs.

Examples:

- GeoTIFF files
- Cloud Optimized GeoTIFF files
- Satellite imagery assets
- Raster analysis outputs
- NDVI results
- GeoJSON exports
- 3D model files
- Generated reports

Example bucket structure:

```text
aleph-next-storage/
│
├── organizations/
│   ├── organization-001/
│   │   ├── projects/
│   │   │   ├── project-001/
│   │   │   │   ├── datasets/
│   │   │   │   ├── raster/
│   │   │   │   ├── analysis/
│   │   │   │   └── exports/
│   │
│   └── organization-002/
│
├── shared/
│   ├── public-boundaries/
│   └── reference-data/
│
└── temporary/
```

This is an example storage layout. The actual key structure should be aligned with the application's tenant isolation and storage implementation.

### 8.2 Storage Security

Configure:

- S3 Block Public Access
- Encryption at rest
- IAM-based access
- Restricted bucket policies
- Lifecycle rules
- Temporary access through presigned URLs when appropriate

The backend must verify organization and resource permissions before generating a presigned URL.

Do not rely only on a file path or object key to authorize access.

### 8.3 Large Raster Files

Large raster datasets can require substantial storage and processing resources.

Consider:

- Cloud Optimized GeoTIFF
- Raster tiling
- Compression
- Window-based processing
- Temporary processing storage
- S3 lifecycle policies

Avoid downloading entire large raster files when only a small spatial window is needed.

---

## 9. Container Image Management

### 9.1 Amazon ECR

Use Amazon Elastic Container Registry (ECR) to store application Docker images.

Suggested repositories:

```text
aleph-next-frontend
aleph-next-backend
aleph-next-worker
aleph-next-mcp
```

Create only the repositories required by the actual application architecture.

### 9.2 Image Tagging

Use meaningful image tags.

Example:

```text
aleph-next-backend:1.0.0
aleph-next-backend:staging
aleph-next-backend:production
```

For automated builds, prefer immutable identifiers such as Git commit SHAs.

Example:

```text
aleph-next-backend:a1b2c3d
```

Avoid relying only on the `latest` tag in production. It does not identify a specific, reproducible application version.

### 9.3 Image Security

Before deploying an image:

- Use a trusted base image.
- Keep dependencies updated.
- Avoid copying `.env` files into images.
- Avoid running containers as root where possible.
- Scan images for known vulnerabilities.
- Use small production images.
- Exclude development tools from production images.

---

## 10. Domain and HTTPS Configuration

### 10.1 Route 53

Amazon Route 53 can manage the application's domain and DNS records.

Example domain structure:

```text
example.com
    |
    |-- Application frontend

api.example.com
    |
    |-- Backend API

monitoring.example.com
    |
    |-- Restricted monitoring interface, if required
```

These are example hostnames. Configure them using a domain that you own.

### 10.2 AWS Certificate Manager

Use AWS Certificate Manager (ACM) to provision and manage TLS certificates for supported AWS load balancers.

Recommended:

- Use HTTPS for application traffic.
- Redirect HTTP to HTTPS.
- Renew certificates automatically through the supported AWS integration.
- Avoid sending authentication tokens over plain HTTP.

### 10.3 Application Load Balancer

An Application Load Balancer can route requests to different services.

Example:

```text
https://example.com
    |
    |-- Frontend target group

https://api.example.com
    |
    |-- Backend target group
```

Configure health checks that match the actual application's health endpoints.

Do not expose internal services through the load balancer unless there is a clear requirement and suitable authentication.

---

## 11. IAM and Secrets Management

### 11.1 IAM Roles

Use IAM roles to provide AWS permissions to application services.

Examples:

- Backend role: access approved S3 buckets and required AWS services.
- Worker role: access processing inputs and output storage.
- Deployment role: push images and update the selected deployment resources.
- Monitoring role: access required monitoring information.

Apply the principle of least privilege.

Avoid using permanent AWS access keys inside application containers.

### 11.2 AWS Secrets Manager

Use Secrets Manager for sensitive values such as:

```text
DATABASE_URL
JWT_SECRET_KEY
REDIS_URL
OPENAI_API_KEY
EXTERNAL_PROVIDER_API_KEYS
```

These are illustrative names. Match them to the actual application configuration.

Secrets should:

- Never be committed to Git.
- Never be included in Docker images.
- Be accessible only to authorized IAM roles.
- Be rotated when appropriate.
- Be excluded from application logs.

### 11.3 Parameter Store

AWS Systems Manager Parameter Store can be used for non-secret configuration values.

For example:

```text
/aleph-next/production/APP_ENV
/aleph-next/production/LOG_LEVEL
/aleph-next/production/FRONTEND_URL
```

Choose Secrets Manager or Parameter Store according to the application's secret-management requirements.

---

## 12. CI/CD Deployment

### 12.1 GitHub Actions

GitHub Actions can automate the application deployment workflow.

Example pipeline:

```text
Developer Push
      |
      |
GitHub Repository
      |
      |
GitHub Actions
      |
      |-- Run Tests
      |
      |-- Build Frontend
      |
      |-- Build Backend
      |
      |-- Scan Images
      |
      |-- Push Images to ECR
      |
      |-- Run Database Migration
      |
      |-- Deploy Application
      |
      |-- Verify Health Checks
      |
      |
Production Environment
```

### 12.2 Recommended Workflow

A deployment pipeline should:

1. Trigger on an approved branch or release.
2. Check out the repository.
3. Install dependencies.
4. Run backend tests.
5. Run frontend checks and tests.
6. Build production Docker images.
7. Scan images where configured.
8. Authenticate to AWS using a secure identity mechanism.
9. Push versioned images to ECR.
10. Run reviewed database migrations when required.
11. Deploy the new application version.
12. Verify service health.
13. Report deployment success or failure.

### 12.3 AWS Authentication from GitHub Actions

Prefer GitHub Actions OpenID Connect (OIDC) with an appropriately restricted AWS IAM role.

Avoid storing long-lived AWS access keys in repository secrets unless there is a specific reason and suitable controls.

Restrict the deployment role to:

- The intended GitHub repository.
- Approved branches or environments.
- Required ECR repositories.
- Required deployment resources.

### 12.4 Deployment Approval

For production deployments, consider:

- Protected branches
- Pull request reviews
- GitHub environment protection
- Required test checks
- Manual approval for sensitive releases

---

## 13. Example EC2 Deployment

This section shows an illustrative workflow for an EC2 deployment using Docker Compose.

The commands assume:

- An EC2 instance has already been created.
- Docker and the Compose plugin are installed.
- The repository is available on the instance.
- Production environment variables are configured securely.
- The Compose file and service names match the actual repository.

### 13.1 Connect to EC2

From your local machine:

```bash
ssh -i "your-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

Replace the key path and public IP with your actual values.

### 13.2 Navigate to the Project

```bash
cd /opt/aleph-next
```

### 13.3 Check the Repository

```bash
git status
git branch --show-current
git pull origin main
```

Confirm that pulling the branch will not overwrite uncommitted production changes.

### 13.4 Check Docker

```bash
docker --version
docker compose version
```

### 13.5 Build and Start Containers

Only after verifying the actual Compose file and service configuration:

```bash
docker compose up --build -d
```

### 13.6 Check Containers

```bash
docker compose ps
```

### 13.7 Check Logs

```bash
docker compose logs --tail=100
```

For a specific service:

```bash
docker compose logs --tail=100 backend
```

The service name `backend` is an example. Use the service name defined in your Compose file.

### 13.8 Verify the Application

Check the configured frontend URL and API health endpoint.

For example:

```bash
curl -I https://example.com
```

```bash
curl https://api.example.com/health
```

The health endpoint is illustrative. Use the route actually implemented by the backend.

---

## 14. Production Configuration

Before deploying production services, review the following.

### 14.1 Application Configuration

- Set the production environment mode.
- Configure the correct frontend URL.
- Configure the backend API URL.
- Configure database connections.
- Configure Redis connections.
- Configure CORS origins.
- Configure authentication secrets.
- Configure external provider credentials.
- Disable development-only features.
- Set appropriate logging levels.

### 14.2 Database Configuration

- Use private network access.
- Enable encryption.
- Configure automated backups.
- Configure database monitoring.
- Use secure credentials.
- Verify PostGIS support.
- Test migrations before production deployment.

### 14.3 Container Configuration

- Use production Docker images.
- Set resource limits where supported.
- Configure health checks.
- Use non-root users where possible.
- Avoid storing permanent data inside disposable containers.
- Use persistent storage where required.

### 14.4 File Storage Configuration

- Use private S3 buckets.
- Configure encryption.
- Configure lifecycle policies.
- Verify tenant-level authorization.
- Test large file uploads and downloads.

---

## 15. Monitoring and Logging

Use Amazon CloudWatch to collect application and infrastructure information.

Monitor:

- Application errors
- API response times
- CPU usage
- Memory usage
- Container restarts
- Database connections
- Database storage
- Redis memory usage
- Background job failures
- S3 storage usage
- Load balancer health
- Failed deployments

### 15.1 Application Logs

Application logs should include useful diagnostic information.

Example:

```text
timestamp
log_level
service_name
request_id
organization_id
user_id
message
```

Avoid recording:

- Passwords
- Access tokens
- Secret keys
- Full sensitive request bodies
- Private user data without a valid operational requirement

### 15.2 CloudWatch Alarms

Consider alarms for:

- High CPU utilization
- High memory utilization
- Unhealthy load balancer targets
- Repeated application failures
- Database storage pressure
- Database connection exhaustion
- Background job failures

Monitoring thresholds should be based on actual workloads rather than arbitrary defaults.

For further information, see:

- `monitoring.md`

---

## 16. Scaling Strategy

TERRAMIND may process large satellite and raster datasets.

The architecture should allow application services and processing workers to scale independently.

### 16.1 Frontend Scaling

Scale frontend instances according to:

- Request volume
- Response time
- CPU usage
- Memory usage

### 16.2 Backend Scaling

Scale API services according to:

- Request volume
- API latency
- CPU usage
- Memory usage
- Database connection usage

Ensure that authentication and application state do not depend on local container memory if multiple instances are used.

### 16.3 Worker Scaling

Worker capacity should consider:

- Pending job count
- Job processing duration
- Available memory
- CPU utilization
- Raster file sizes
- External data provider limits

Do not increase worker concurrency without considering memory consumption. Large raster processing jobs can require substantial memory.

### 16.4 Database Scaling

Monitor database performance before increasing database capacity.

Consider:

- Query optimization
- Spatial indexes
- Connection pooling
- Read replicas where appropriate
- Storage performance
- Database instance capacity

A larger database instance does not replace proper query optimization.

---

## 17. Deployment Rollback

Every production deployment should have a rollback strategy.

### 17.1 Application Rollback

Keep the previous known-good application image available.

Example:

```text
Version 1.0.0
Version 1.0.1
Version 1.0.2
```

If the latest version fails:

1. Identify the failing deployment.
2. Review application and infrastructure logs.
3. Stop or replace the unhealthy deployment.
4. Redeploy the previous known-good image.
5. Verify the frontend and API.
6. Confirm database compatibility.
7. Record the incident.

For ECS, update the service to a previous task definition or image version.

For EC2 with Docker Compose, update the configured image tag and recreate the relevant services.

### 17.2 Database Rollback

Database rollback is more complex than application rollback.

Before a migration:

- Review the migration.
- Back up important data.
- Check whether the migration is reversible.
- Consider compatibility with the previous application version.

Prefer backward-compatible database migrations where possible.

Do not automatically downgrade a production database without understanding the migration's effects.

### 17.3 Infrastructure Rollback

For infrastructure changes, use version-controlled infrastructure configuration where practical.

Consider infrastructure-as-code tools such as:

- AWS CloudFormation
- Terraform
- AWS CDK

The selected tool should be documented and used consistently.

---

## 18. Cost Considerations

AWS costs depend on the selected region, instance sizes, storage usage, data transfer, and running hours.

Review these areas:

| Resource | Cost consideration |
|---|---|
| EC2 | Instance type and running hours |
| ECS / Fargate | CPU and memory allocation and runtime |
| RDS | Database instance, storage, backups |
| ElastiCache | Cache node size and running hours |
| S3 | Storage, requests, and data transfer |
| Load Balancer | Running hours and processed traffic |
| NAT Gateway | Hourly and data processing charges |
| CloudWatch | Log ingestion, retention, and metrics |
| ECR | Image storage |
| Data transfer | Outbound and inter-service traffic |

### 18.1 Cost Optimization

Consider:

- Removing unused EC2 instances.
- Removing unused ECR images.
- Configuring S3 lifecycle policies.
- Choosing suitable database capacity.
- Monitoring idle resources.
- Limiting unnecessary NAT Gateway traffic.
- Setting CloudWatch log retention.
- Using appropriate compute scaling.
- Avoiding oversized worker instances.

Do not choose production capacity based only on the lowest available instance price. Validate the workload and performance requirements first.

---

## 19. Deployment Checklist

### AWS Infrastructure

- [ ] AWS account and deployment region selected.
- [ ] VPC created.
- [ ] Public and private subnets configured.
- [ ] Security groups configured.
- [ ] IAM roles configured.
- [ ] Required ECR repositories created.
- [ ] Required compute resources configured.
- [ ] Database service configured.
- [ ] Redis service configured if required.
- [ ] S3 bucket created.
- [ ] Secrets Manager or Parameter Store configured.

### Application

- [ ] Frontend production build verified.
- [ ] Backend production image verified.
- [ ] Worker image verified if required.
- [ ] MCP deployment verified if required.
- [ ] Production environment variables configured.
- [ ] Database connectivity verified.
- [ ] PostGIS extension verified.
- [ ] Redis connectivity verified.
- [ ] S3 access verified.
- [ ] Authentication verified.
- [ ] Organization isolation verified.
- [ ] Health checks verified.

### Network and Security

- [ ] Domain configured.
- [ ] HTTPS certificate configured.
- [ ] HTTP redirects to HTTPS.
- [ ] Database is not publicly accessible.
- [ ] Redis is not publicly accessible.
- [ ] Secrets are not stored in Git.
- [ ] IAM permissions follow least privilege.
- [ ] S3 public access is blocked.
- [ ] Application security groups are restricted.

### CI/CD and Operations

- [ ] Automated tests configured.
- [ ] Docker image build verified.
- [ ] Image scanning configured.
- [ ] Deployment workflow configured.
- [ ] Database migration process documented.
- [ ] Rollback procedure tested.
- [ ] CloudWatch logging configured.
- [ ] Monitoring alarms configured.
- [ ] Backup and recovery process tested.

---

## 20. Implementation Roadmap

Implement AWS deployment in stages.

### Stage 1: Initial Deployment

- [ ] Select EC2 or ECS.
- [ ] Configure the AWS network.
- [ ] Prepare production Docker images.
- [ ] Configure environment variables.
- [ ] Deploy the frontend.
- [ ] Deploy the backend.
- [ ] Verify application connectivity.

### Stage 2: Managed Infrastructure

- [ ] Configure managed PostgreSQL.
- [ ] Verify PostGIS compatibility.
- [ ] Configure managed Redis if required.
- [ ] Configure S3 storage.
- [ ] Configure IAM roles and permissions.
- [ ] Move application secrets to AWS secret management.

### Stage 3: Production Networking

- [ ] Configure the load balancer.
- [ ] Configure DNS.
- [ ] Configure HTTPS.
- [ ] Restrict internal network access.
- [ ] Verify production CORS and authentication.

### Stage 4: Automation

- [ ] Configure GitHub Actions.
- [ ] Configure secure AWS authentication.
- [ ] Automate image builds.
- [ ] Automate image publishing.
- [ ] Automate deployment.
- [ ] Add deployment health verification.

### Stage 5: Production Operations

- [ ] Configure CloudWatch.
- [ ] Configure alarms.
- [ ] Configure backups.
- [ ] Test restore procedures.
- [ ] Test rollback.
- [ ] Review performance and costs.

---

## 21. Important Notes

1. This document describes a target deployment design, not proof of an existing AWS deployment.
2. Select one primary deployment approach before writing production infrastructure configuration.
3. Verify Docker Compose service names and Dockerfile paths against the actual repository.
4. Verify the FastAPI application entry point before using the production start command.
5. Verify PostgreSQL and PostGIS compatibility before selecting an RDS version.
6. Keep the database and Redis in private network locations.
7. Never store production secrets in Git or Docker images.
8. Use IAM roles instead of permanent AWS credentials wherever possible.
9. Treat satellite imagery and raster files as potentially large objects that need suitable storage and processing capacity.
10. Test backup restoration and application rollback before relying on them in production.
11. Do not expose administrative, monitoring, or MCP interfaces publicly without appropriate access controls.
12. Validate tenant isolation across API requests, background jobs, and S3 objects.

---

## 22. Related Documentation

- `architecture.md`
- `repository-structure.md`
- `environment-variables.md`
- `docker-setup.md`
- `database-schema.md`
- `authentication.md`
- `geospatial-processing.md`
- `raster-processing.md`
- `multi-tenancy.md`
- `monitoring.md`
- `security.md`
- `backup-and-recovery.md`

---

**Document status:** Target architecture and deployment guidance.

**Implementation status:** AWS resources, infrastructure configuration, and deployment workflows must be verified against the actual TERRAMIND repository and AWS environment.