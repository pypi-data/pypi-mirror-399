---
name: opensearch-server
description: Start and manage OpenSearch server with Docker. Use when starting OpenSearch locally, setting up development environment, or managing OpenSearch containers.
allowed-tools: Bash
---

# OpenSearch Server

Docker-based OpenSearch server with Korean (Nori) analyzer.

## Start Server

```bash
# Using docker-compose (recommended, with persistent data)
cp .env.example .env  # Set password first
docker compose -f docker-compose.dev.yml up -d

# Or using pre-built image (amd64/arm64)
docker run -d --name opensearch \
  -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "plugins.security.disabled=true" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=YourStr0ngP@ss!" \
  a1rtisan/opensearch-nori:latest
```

**Note**: Password requires 8+ chars with upper/lower/digit/special.

## Stop Server

```bash
docker stop opensearch && docker rm opensearch

# Or with docker-compose
docker compose -f docker-compose.dev.yml down
```

## Check Status

```bash
# Health check
curl -s http://localhost:9200

# Check Nori plugin
curl -s http://localhost:9200/_cat/plugins | grep nori
```

## Test Korean Analyzer

```bash
curl -X POST "http://localhost:9200/_analyze" \
  -H "Content-Type: application/json" \
  -d '{"tokenizer": "nori_tokenizer", "text": "한국어 형태소 분석"}'
```

## Ports

| Port | Service |
|------|---------|
| 9200 | REST API |
| 9600 | Performance Analyzer |

## Docker Images

| Image | Description |
|-------|-------------|
| `a1rtisan/opensearch-nori:latest` | OpenSearch 3.0 + Nori plugin |
| `opensearchproject/opensearch:latest` | Official (no Nori) |

## Links

- Docker Hub: https://hub.docker.com/r/a1rtisan/opensearch-nori
- GitHub: https://github.com/namyoungkim/opensearch-client
