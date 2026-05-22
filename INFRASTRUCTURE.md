# AryaX Platform - Infrastructure Setup Guide

## Overview

The AryaX Platform is built on a modern, scalable architecture using:
- **FastAPI** for high-performance async API
- **PostgreSQL** for primary data storage with ACID compliance
- **Redis** for caching and session management
- **Elasticsearch** for audit logging and analytics
- **Docker** for containerization
- **Kubernetes** for orchestration

## Project Structure

```
.
├── src/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application factory
│   ├── config.py             # Configuration management
│   ├── database.py           # Database setup and session management
│   ├── cache.py              # Redis cache and session management
│   ├── search.py             # Elasticsearch integration
│   └── models.py             # SQLAlchemy ORM models
├── alembic/
│   ├── env.py                # Alembic environment configuration
│   ├── script.py.mako        # Migration template
│   └── versions/
│       └── 001_initial_schema.py  # Initial database schema
├── k8s/
│   ├── namespace.yaml        # Kubernetes namespace
│   ├── configmap.yaml        # Configuration management
│   ├── secret.yaml           # Secrets management
│   ├── postgres-deployment.yaml   # PostgreSQL StatefulSet
│   ├── redis-deployment.yaml      # Redis StatefulSet
│   ├── elasticsearch-deployment.yaml  # Elasticsearch StatefulSet
│   ├── api-deployment.yaml   # API Deployment with HPA
│   └── ingress.yaml          # Ingress configuration
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker Compose for local development
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
└── run.py                    # Development server runner
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized setup)
- PostgreSQL 16+ (if running locally)
- Redis 7+ (if running locally)
- Elasticsearch 8.11+ (if running locally)

### Local Development Setup

1. **Clone and setup environment:**
   ```bash
   cd d:\Project\ AryaX
   cp .env.example .env
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start services with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

5. **Start development server:**
   ```bash
   python run.py
   ```

   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Docker Setup

1. **Build Docker image:**
   ```bash
   docker build -t aryax:latest .
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Check service health:**
   ```bash
   docker-compose ps
   docker-compose logs -f api
   ```

## Database Management

### Alembic Migrations

Alembic is used for database schema versioning and migrations.

**Create a new migration:**
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback migrations:**
```bash
alembic downgrade -1
```

**View migration history:**
```bash
alembic history
```

### Database Schema

The database includes the following tables:

- **organizations** - Enterprise customer accounts
- **users** - Individual users with RBAC
- **api_keys** - API credentials for programmatic access
- **subscriptions** - Billing plans and status
- **usage_records** - Metered usage for billing
- **invoices** - Generated billing documents
- **audit_logs** - Security and compliance events
- **conversations** - AI interactions with analytics
- **finetuning_jobs** - Custom model training jobs
- **webhooks** - Event notification registrations

All tables include:
- UUID primary keys
- Timestamps (created_at, updated_at)
- Proper indexing for query performance
- Foreign key constraints for referential integrity
- Check constraints for data validation

## Redis Configuration

Redis is used for:
- **Session Management** - User sessions with 24-hour TTL
- **Caching** - API responses and computed data with 5-minute TTL
- **Rate Limiting** - Sliding window counters per API key
- **RBAC Matrix** - Cached permissions for fast authorization

### Redis Commands

```bash
# Connect to Redis
redis-cli -h localhost -p 6379

# Check connection
ping

# View all keys
keys *

# Get session data
get session:session_id

# Clear cache
flushdb
```

## Elasticsearch Configuration

Elasticsearch is used for:
- **Audit Logging** - Immutable security event logs
- **Analytics** - Time-series metrics and aggregations
- **Full-text Search** - Searching audit logs and analytics

### Index Management

Indices are created with daily rotation:
- `aryax-audit-logs-YYYY.MM.DD` - Audit events
- `aryax-analytics-YYYY.MM.DD` - Analytics metrics

### Elasticsearch Queries

```bash
# Check cluster health
curl http://localhost:9200/_cluster/health

# List indices
curl http://localhost:9200/_cat/indices

# Search audit logs
curl -X GET "localhost:9200/aryax-audit-logs-*/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "event_type": "login"
    }
  }
}'
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Docker registry access
- Persistent volume provisioner

### Deployment Steps

1. **Create namespace and secrets:**
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/secret.yaml
   kubectl apply -f k8s/configmap.yaml
   ```

2. **Deploy infrastructure services:**
   ```bash
   kubectl apply -f k8s/postgres-deployment.yaml
   kubectl apply -f k8s/redis-deployment.yaml
   kubectl apply -f k8s/elasticsearch-deployment.yaml
   ```

3. **Wait for services to be ready:**
   ```bash
   kubectl wait --for=condition=ready pod -l app=postgres -n aryax --timeout=300s
   kubectl wait --for=condition=ready pod -l app=redis -n aryax --timeout=300s
   kubectl wait --for=condition=ready pod -l app=elasticsearch -n aryax --timeout=300s
   ```

4. **Deploy API:**
   ```bash
   kubectl apply -f k8s/api-deployment.yaml
   ```

5. **Deploy Ingress:**
   ```bash
   kubectl apply -f k8s/ingress.yaml
   ```

### Monitoring Deployment

```bash
# Check pod status
kubectl get pods -n aryax

# View pod logs
kubectl logs -n aryax deployment/aryax-api

# Check service status
kubectl get svc -n aryax

# Monitor HPA
kubectl get hpa -n aryax -w

# Describe deployment
kubectl describe deployment aryax-api -n aryax
```

### Scaling

The API deployment includes Horizontal Pod Autoscaling (HPA):
- **Min replicas:** 3
- **Max replicas:** 20
- **CPU threshold:** 70%
- **Memory threshold:** 80%

Manual scaling:
```bash
kubectl scale deployment aryax-api --replicas=5 -n aryax
```

## Configuration Management

### Environment Variables

All configuration is managed through environment variables defined in:
- `.env` - Local development
- `k8s/configmap.yaml` - Kubernetes ConfigMap
- `k8s/secret.yaml` - Kubernetes Secrets

### Key Configuration Options

```python
# Application
APP_NAME = "AryaX Platform"
DEBUG = False
ENVIRONMENT = "production"

# Database
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/db"
DATABASE_POOL_SIZE = 20

# Redis
REDIS_URL = "redis://localhost:6379/0"
REDIS_CACHE_TTL = 300

# Elasticsearch
ELASTICSEARCH_HOSTS = ["http://localhost:9200"]

# JWT
JWT_SECRET_KEY = "your-secret-key"
JWT_EXPIRATION_HOURS = 1

# Stripe
STRIPE_API_KEY = "sk_live_..."
```

## Security Best Practices

1. **Database**
   - Use strong passwords
   - Enable SSL connections
   - Restrict network access
   - Regular backups

2. **Redis**
   - Use authentication
   - Disable dangerous commands
   - Enable persistence
   - Monitor memory usage

3. **Elasticsearch**
   - Enable security features
   - Use authentication
   - Restrict network access
   - Enable audit logging

4. **API**
   - Use HTTPS/TLS
   - Implement rate limiting
   - Validate all inputs
   - Use strong JWT secrets
   - Rotate API keys regularly

5. **Kubernetes**
   - Use RBAC
   - Enable network policies
   - Use secrets for sensitive data
   - Regular security updates
   - Pod security policies

## Monitoring and Observability

### Health Checks

All services include health checks:

```bash
# API health
curl http://localhost:8000/health

# Database
pg_isready -h localhost -U aryax

# Redis
redis-cli ping

# Elasticsearch
curl http://localhost:9200/_cluster/health
```

### Logging

Logs are available through:
- Docker: `docker-compose logs -f service_name`
- Kubernetes: `kubectl logs -n aryax pod_name`
- Elasticsearch: Audit logs indexed automatically

### Metrics

Prometheus metrics are exposed at `/metrics` endpoint (when enabled).

## Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -h localhost -U aryax -d aryax_db

# Check connection pool
SELECT count(*) FROM pg_stat_activity;
```

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli -h localhost ping

# Check memory usage
redis-cli info memory
```

### Elasticsearch Connection Issues

```bash
# Check cluster status
curl http://localhost:9200/_cluster/health

# Check node status
curl http://localhost:9200/_nodes
```

### API Issues

```bash
# Check API logs
docker-compose logs -f api

# Test API endpoint
curl http://localhost:8000/health

# Check database migrations
alembic current
```

## Performance Tuning

### Database
- Connection pooling: 20 connections
- Query result caching: 5 minutes
- Index optimization for frequently queried columns

### Redis
- Memory limit: 512MB
- Eviction policy: LRU
- Persistence: RDB + AOF

### Elasticsearch
- Heap size: 512MB
- Refresh interval: 1 second
- Index rotation: Daily

### API
- Worker processes: Auto (CPU count)
- Worker threads: 4 per worker
- Request timeout: 60 seconds

## Backup and Recovery

### Database Backups

```bash
# Create backup
pg_dump -h localhost -U aryax aryax_db > backup.sql

# Restore backup
psql -h localhost -U aryax aryax_db < backup.sql
```

### Redis Backups

```bash
# Create backup
redis-cli --rdb /path/to/backup.rdb

# Restore backup
cp /path/to/backup.rdb /var/lib/redis/dump.rdb
```

## Support and Documentation

- **API Documentation:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **FastAPI:** https://fastapi.tiangolo.com/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **Alembic:** https://alembic.sqlalchemy.org/
- **Kubernetes:** https://kubernetes.io/docs/

## Next Steps

1. Configure external services (Stripe, OpenAI, Gemini)
2. Set up monitoring and alerting
3. Configure backup and disaster recovery
4. Implement CI/CD pipeline
5. Set up production environment
