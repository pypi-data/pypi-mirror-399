# OpenSearch Server Setup Guide

This guide explains how to run an OpenSearch server for use with `opensearch-client`.

## Overview

`opensearch-client` is a **client library** that connects to an OpenSearch server. You need to run the server separately.

```
┌─────────────────────────────────────────────────────────────┐
│  Your Application                                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  from opensearch_client import OpenSearchClient       │  │
│  │  client = OpenSearchClient(host="...", port=9200)     │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                │
│                   opensearch-client (this package)          │
└────────────────────────────┼────────────────────────────────┘
                             │ HTTP/HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  OpenSearch Server (separate process)                       │
│  - Docker container (local development)                     │
│  - AWS OpenSearch Service (production)                      │
│  - Self-hosted cluster                                      │
└─────────────────────────────────────────────────────────────┘
```

## Local Development

### Option 1: Simple Docker Run

```bash
docker run -d -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "plugins.security.disabled=true" \
  --name opensearch \
  opensearchproject/opensearch:latest
```

### Option 2: Docker Compose with Nori Plugin (Recommended)

Use the provided `docker-compose.dev.yml` for Korean text support:

```bash
# Start OpenSearch with Nori analyzer
docker compose -f docker-compose.dev.yml up -d

# Check status
curl http://localhost:9200

# Stop
docker compose -f docker-compose.dev.yml down

# Stop and remove data
docker compose -f docker-compose.dev.yml down -v
```

### Docker Compose Files

| File | Port | Purpose | Data Persistence |
|------|------|---------|------------------|
| `docker-compose.dev.yml` | 9200 | Local development | Yes (volume) |
| `docker-compose.test.yml` | 9201 | CI/Testing | No |

## Production Options

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **AWS OpenSearch Service** | Managed, auto-scaling, backups | Cost, vendor lock-in | Most production use cases |
| **Self-hosted (Kubernetes)** | Flexibility, cost control | Operational complexity | Large-scale, multi-tenant |
| **Self-hosted (Docker/VM)** | Simple, low overhead | Limited scaling | Small deployments |

### AWS OpenSearch Service

```python
from opensearch_client import OpenSearchClient

client = OpenSearchClient(
    host="search-my-domain.us-east-1.es.amazonaws.com",
    port=443,
    use_ssl=True,
    verify_certs=True,
    # Use IAM authentication or master user credentials
    user="master_user",
    password="Master_Password_123"
)
```

### Self-hosted Kubernetes

See [OpenSearch Kubernetes Operator](https://github.com/opensearch-project/opensearch-k8s-operator) for production-grade Kubernetes deployment.

## Environment-based Configuration

Manage different environments (local, staging, production) using environment variables:

```python
import os
from opensearch_client import OpenSearchClient

client = OpenSearchClient(
    host=os.getenv("OPENSEARCH_HOST", "localhost"),
    port=int(os.getenv("OPENSEARCH_PORT", "9200")),
    user=os.getenv("OPENSEARCH_USER", "admin"),
    password=os.getenv("OPENSEARCH_PASSWORD", "admin"),
    use_ssl=os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true",
    verify_certs=os.getenv("OPENSEARCH_VERIFY_CERTS", "true").lower() == "true",
)
```

### Environment File Examples

**.env.local** (local development):
```bash
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=admin
OPENSEARCH_USE_SSL=false
```

**.env.staging**:
```bash
OPENSEARCH_HOST=search-staging.internal
OPENSEARCH_PORT=9200
OPENSEARCH_USER=app_user
OPENSEARCH_PASSWORD=staging_password
OPENSEARCH_USE_SSL=true
OPENSEARCH_VERIFY_CERTS=true
```

**.env.production**:
```bash
OPENSEARCH_HOST=search-prod.example.com
OPENSEARCH_PORT=443
OPENSEARCH_USER=app_user
OPENSEARCH_PASSWORD=${AWS_SECRETS_MANAGER_VALUE}
OPENSEARCH_USE_SSL=true
OPENSEARCH_VERIFY_CERTS=true
```

### Using python-dotenv

```python
from dotenv import load_dotenv
import os

# Load environment-specific .env file
env = os.getenv("ENVIRONMENT", "local")
load_dotenv(f".env.{env}")

from opensearch_client import OpenSearchClient

client = OpenSearchClient(
    host=os.getenv("OPENSEARCH_HOST"),
    port=int(os.getenv("OPENSEARCH_PORT")),
    # ... other settings
)
```

## Security Best Practices

1. **Never commit credentials**: Use environment variables or secrets management
2. **Enable SSL/TLS**: Always use `use_ssl=True` in production
3. **Verify certificates**: Keep `verify_certs=True` unless testing
4. **Use least privilege**: Create application-specific users with minimal permissions
5. **Rotate credentials**: Regularly update passwords and API keys

## Troubleshooting

### Connection Refused

```bash
# Check if OpenSearch is running
curl http://localhost:9200

# Check Docker container status
docker ps | grep opensearch

# View logs
docker logs opensearch-dev
```

### Memory Issues

OpenSearch requires significant memory. Ensure Docker has at least 4GB allocated:

```yaml
# In docker-compose.yml
environment:
  - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
```

### Port Conflicts

If port 9200 is in use:

```bash
# Find process using port 9200
lsof -i :9200

# Use alternative port
docker run -d -p 9201:9200 ...
```

---

*Last Updated: 2025-01-01*
