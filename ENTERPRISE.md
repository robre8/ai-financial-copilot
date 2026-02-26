# 🏢 Enterprise Guide - AI Financial Copilot

> Enterprise-grade production deployments, compliance frameworks, and advanced configurations for regulated financial environments.

**Quick Links**: [README.md](./README.md) | [Architecture](#enterprise-architecture) | [Security](#security--compliance) | [Deployment](#deployment--infrastructure) | [Operations](#operational-runbooks)

---

## 🔄 Deployment Pipeline

```
Git Commit
    ↓
feature/improvements (PR testing)
    ├── GitHub Actions: Run 50+ tests
    ├── Vercel: Auto-deploy preview
    └── Review & test before merge
    ↓
main (production approval)
    ├── Create release (semantic version)
    └── GitHub Actions: Deploy to Render.com
         ├── Backend: https://ai-financial-copilot-3.onrender.com
         ├── Database: PostgreSQL 15 + pgvector
         └── Storage: Persistent volumes
```

**Release Process**:
1. Features merged to `main` are automatically deployed
2. Tag releases with semantic versions for version control
3. Render hooks trigger automatic deployment on main branch updates
4. Rollback: Revert commit and re-push to main

---

## 📑 Table of Contents

1. [Enterprise Architecture](#enterprise-architecture)
2. [Security & Compliance](#security--compliance)
3. [Authentication & Authorization](#authentication--authorization)
4. [Deployment & Infrastructure](#deployment--infrastructure)
5. [Monitoring & Observability](#monitoring--observability)
6. [Scalability & Performance](#scalability--performance)
7. [Disaster Recovery](#disaster-recovery)
8. [Operational Runbooks](#operational-runbooks)
9. [Integration Patterns](#integration-patterns)
10. [Cost Optimization](#cost-optimization)

---

## Enterprise Architecture

### Current Stack (Production Ready)

```
┌─────────────────────────────────────────────────────────────┐
│           Frontend (React 18 + Vite + Tailwind)             │
│    Deployed: Vercel (Preview: feature/improvements)         │
│    Production: Soon via CI/CD                               │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTPS/TLS 1.3
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend + Uvicorn                      │
│  Deployed: Render.com (https://ai-financial-copilot-3...)   │
│  • REST API Endpoints (/upload, /ask, /analyze)            │
│  • Firebase JWT Authentication                             │
│  • Rate Limiting (10 req/min per user)                     │
│  • Structured Logging                                      │
└────────┬──────────────────────┬────────────────────┬────────┘
         │                      │                    │
    RAG Logic            Agent Service         Webhooks
    • Chunking          • ReAct pattern       • Event dispatch
    • Embedding         • Tool execution      • Async delivery
    • Search            • Reasoning           • Retry logic
         │                      │                    │
         └──────────────┬───────┴────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
    PostgreSQL    HuggingFace      Groq API
    + pgvector    (Embeddings)     (LLM)
    (Render)      (Free Tier)      (Free Tier)
                                   3-model fallback
```

### Microservices Layer

| Component | Technology | Responsibility | Scaling |
|-----------|-----------|-----------------|---------|
| **Frontend** | React 18 + Vite | Web UI, auth flow, PDF upload | CDN (Vercel) |
| **Web Server** | FastAPI + Uvicorn | HTTP API, routing, middleware | Horizontal (replicas) |
| **Vector DB** | PostgreSQL 15 + pgvector | Persistent semantic search | Vertical (postgres-plan) |
| **Embeddings** | Huggingface API | Vector generation (all-MiniLM, 384-dim) | Rate-limited free tier |
| **LLM** | Groq API | Fast inference with 3-model fallback | Rate-limited free tier |
| **Auth** | Firebase Admin SDK | JWT validation, user management | Managed service |
| **Storage** | Render volumes | PDF documents, vector cache | 1GB included |

### Deployment Architecture

**Development** (feature/improvements):
```
Push to GitHub
  ↓
GitHub Actions tests (50+ tests)
  ↓
Vercel preview build
  ↓
Live at: https://ai-financial-copilot-preview.vercel.app
  ↓
Manual test → Merge to main when ready
```

**Production** (main):
```
Merge to main
  ↓
GitHub Actions: Run tests + Docker build
  ↓
Vercel auto-deployment (frontend)
  ↓
Live at: https://ai-financial-copilot.vercel.app
  ↓
Render.com auto-deployment (backend)
  ↓
Live at: https://ai-financial-copilot-3.onrender.com
  ↓
PostgreSQL persistent data maintained
```

---

## Security & Compliance

### 1. Authentication & Identity

#### Firebase Authentication (Recommended for Production)

Firebase provides industry-standard OAuth2 + JWT authentication with minimal infrastructure setup:

**Sign-in Methods**:
- 🔐 **Google OAuth2**: Federated identity
- 📧 **Email/Password**: Traditional authentication
- 🔄 **JWT Tokens**: Automatic refresh & validation

**How it Works**:
```
1. Frontend: User signs in (Google or Email/Password)
   ↓
2. Firebase: Issues JWT ID token (1 hour expiry)
   ↓
3. Frontend: Stores token in localStorage
   ↓
4. Every API request: Include token in Authorization header
   Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6...
   ↓
5. Backend: Validates token using Firebase Admin SDK
   ↓
6. Request proceeds with user_id in security context
```

**Backend Implementation**:
```python
# backend/app/core/security.py
from firebase_admin import auth
from fastapi import Security

async def verify_firebase_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
) -> dict:
    """Validate Firebase JWT token"""
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return decoded_token  # {"uid": "user123", "email": "user@example.com", ...}
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token expired")

# Protected endpoint
@router.post("/ask")
async def ask(
    question: str, 
    user = Security(verify_firebase_token)
):
    user_id = user.get("uid")
    # Process request
```

**Environment Configuration**:
```bash
# backend/.env
FIREBASE_SERVICE_ACCOUNT_JSON='{"type": "service_account", "project_id": "your-project-id", "private_key": "..."}'
FRONTEND_ORIGINS=https://your-frontend.example.com,https://preview.example.com
```

#### Alternative: Enterprise OIDC Integration

For corporate environments with existing IdP (Okta, Azure AD, etc):
```python
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='oidc_provider',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    server_metadata_url='https://your-idp/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'},
)
```

### 2. Data Protection

#### Encryption at Rest
- **PostgreSQL encryption**: Enable at host level (AWS RDS encryption, or full-disk encryption on VPS)
- **Connection string**: Use SSL mode for PostgreSQL connections
```python
DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require
```

#### Encryption in Transit
- **HTTPS/TLS 1.3**: All traffic encrypted end-to-end
- **Certificate**: Automatically renewed via Let's Encrypt
- **HSTS**: Enabled to prevent downgrade attacks
- **CORS**: Restrict to expected origins only

**Nginx Configuration** (recommended reverse proxy):
```nginx
server {
    listen 443 ssl http2;
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:...
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

#### Sensitive Data Handling
- Never log API keys, tokens, or PII
- Document PDFs may contain sensitive financial data → implement document-level access control
- Mask or tokenize PII before vector encoding

```python
# Mask sensitive data before embedding
import re

def sanitize_for_embedding(text: str) -> str:
    """Remove PII before creating vectors"""
    # Mask SSN
    text = re.sub(r'\d{3}-\d{2}-\d{4}', '[SSN]', text)
    # Mask email  
    text = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', text)
    # Mask phone
    text = re.sub(r'\+?1?\W?\d{3}\W?\d{3}\W?\d{4}', '[PHONE]', text)
    return text
```

### 3. Compliance Frameworks

#### GDPR (General Data Protection Regulation)

For EU users, implement these mandatory features:

**Right to Erasure** (Article 17):
```python
@router.delete("/users/{user_id}/data")
async def delete_user_data(user_id: str, token = Security(verify_firebase_token)):
    """Permanently delete user data including vectors"""
    if token.get("uid") != user_id:
        raise HTTPException(status_code=403)
    
    # Delete all user documents
    db.session.query(Document).filter(Document.user_id == user_id).delete()
    
    # Delete embeddings from vector DB
    vector_db.delete_embeddings(user_id=user_id)
    
    # Log for audit trail
    audit_log("GDPR_RIGHT_TO_ERASURE", user_id=user_id)
    db.session.commit()
    return {"status": "success", "message": "All user data deleted"}
```

**Data Portability** (Article 20):
```python
@router.get("/users/{user_id}/export")
async def export_user_data(user_id: str, token = Security(verify_firebase_token)):
    """Export all user data in machine-readable format"""
    if token.get("uid") != user_id:
        raise HTTPException(status_code=403)
    
    docs = db.session.query(Document).filter(Document.user_id == user_id).all()
    data = {
        "user_id": user_id,
        "export_date": datetime.now().isoformat(),
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "created_at": doc.created_at.isoformat(),
                "content": doc.extracted_text
            }
            for doc in docs
        ]
    }
    return JSONResponse(content=data)
```

**Data Processing Agreement**: Ensure DPA with Firebase and external API providers (Groq, Huggingface)

#### SOC 2 Type II
- **Availability** (C): 99.95% uptime SLA, monitoring + alerting
- **Security** (S1): Encryption, access controls, vulnerability scanning
- **Processing Integrity** (P): Checksums, audit logs, error handling
- **Confidentiality** (C2): RBAC, field-level encryption, data minimization
- **Privacy** (P2): Minimal PII collection, retention policies, user consent

**Implementation**:
```python
# Audit logging for SOC 2 compliance
from datetime import datetime

def log_audit_event(event: str, user_id: str, details: dict = None):
    """Log security-relevant events for compliance audit trails"""
    audit_entry = AuditLog(
        event_type=event,
        user_id=user_id,
        timestamp=datetime.utcnow(),
        ip_address=request.client.host,
        details=details or {}
    )
    db.session.add(audit_entry)
    db.session.commit()

# Usage
log_audit_event("LOGIN", user_id="user123")
log_audit_event("DOCUMENT_UPLOADED", user_id="user123", details={"document_id": "doc456"})
log_audit_event("API_CALL", user_id="user123", details={"endpoint": "/ask", "status": 200})
```

#### PCI DSS (if handling payment data)
- ✅ No credit card storage (use Stripe/payment processor instead)
- ✅ HTTPS/TLS for all transmission
- ✅ No sensitive authentication data in logs

---

## Authentication & Authorization

### Role-Based Access Control (RBAC)

Firebase provides custom claims for role management:

```python
# Set custom claims in Firebase (via Firebase Console or Admin SDK)
claims = {
    "role": "analyst",
    "organization": "org_123",
    "permissions": ["read", "upload", "analyze"]
}
auth.set_custom_user_claims("user_id", claims)

# Backend: Verify roles
async def require_role(required_role: str):
    async def role_checker(token = Security(verify_firebase_token)):
        user_role = token.get("custom_claims", {}).get("role")
        if user_role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return token
    return role_checker

# Protected endpoint
@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    token = Security(require_role("admin"))
):
    # Only admins can delete documents
    db.session.query(Document).filter(Document.id == doc_id).delete()
    return {"status": "deleted"}
```

### Scoping & Multi-Tenancy

For future multi-tenant deployments:

```python
class TenantScope:
    """Enforce user can only access their own organization's data"""
    
    @staticmethod
    def filter_documents(user_token: dict) -> list:
        user_org = user_token.get("custom_claims", {}).get("organization")
        return db.session.query(Document).filter(
            Document.organization_id == user_org
        ).all()

# Usage
@router.get("/documents")
async def list_documents(token = Security(verify_firebase_token)):
    return TenantScope.filter_documents(token)
```
    VIEWER = "viewer"

class Permission(str, Enum):
    UPLOAD_DOCUMENT = "upload:document"
    QUERY_DOCUMENT = "query:document"
    DELETE_DOCUMENT = "delete:document"
    EXPORT_REPORT = "export:report"
    MANAGE_USERS = "manage:users"

ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.UPLOAD_DOCUMENT,
        Permission.QUERY_DOCUMENT,
        Permission.DELETE_DOCUMENT,
        Permission.EXPORT_REPORT,
        Permission.MANAGE_USERS,
    ],
    Role.ANALYST: [
        Permission.UPLOAD_DOCUMENT,
        Permission.QUERY_DOCUMENT,
        Permission.EXPORT_REPORT,
    ],
    Role.VIEWER: [
        Permission.QUERY_DOCUMENT,
    ],
}

def require_permission(permission: Permission):
    async def permission_checker(credentials = Depends(security)):
        user = get_user_from_token(credentials.credentials)
        role = user.get("role")
        if permission not in ROLE_PERMISSIONS.get(role, []):
            raise HTTPException(403, "Insufficient permissions")
        return user
    return permission_checker

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile, user=Depends(require_permission(Permission.UPLOAD_DOCUMENT))):
    # Only ADMIN and ANALYST can upload
    ...
```

### Multi-Tenant Isolation

```python
# backend/app/models.py
from sqlalchemy import Column, String, ForeignKey

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String, primary_key=True)
    name = Column(String)
    api_key = Column(String, unique=True)

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True)
    organization_id = Column(String, ForeignKey("organizations.id"))  # Tenant isolation
    filename = Column(String)
    created_at = Column(DateTime)

class ReadOnlyQuery(Base):
    __tablename__ = "read_only_queries"
    
    def get_documents_for_org(org_id: str):
        """All queries must filter by org_id"""
        return db.query(Document).filter(Document.organization_id == org_id).all()
```

### API Key Management

This is an optional enterprise add-on for service-to-service access.
The default open-source implementation uses Firebase JWTs for user authentication.

```python
# backend/app/core/api_keys.py
import secrets
from datetime import datetime, timedelta

def generate_api_key(organization_id: str) -> str:
    token = secrets.token_urlsafe(32)
    hashed = hash_token(token)  # Store hash, not plain token
    db.save_api_key(organization_id, hashed, expires_at=datetime.now() + timedelta(days=365))
    return token  # Return once to user

def validate_api_key(token: str) -> dict:
    hashed = hash_token(token)
    api_key = db.get_api_key(hashed)
    if not api_key or api_key.expires_at < datetime.now():
        raise HTTPException(401, "Invalid or expired API key")
    return {"org_id": api_key.organization_id}

@router.post("/ask")
async def ask(request: QuestionRequest, api_key: str = Header(...)):
    org = validate_api_key(api_key)
    # Enforce org isolation in all queries
    ...
```

---

## Deployment & Infrastructure

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-financial-copilot
spec:
  replicas: 3  # Horizontal scaling
  selector:
    matchLabels:
      app: copilot
  template:
    metadata:
      labels:
        app: copilot
    spec:
      containers:
      - name: fastapi
        image: ai-financial-copilot:latest
        ports:
        - containerPort: 8000
        env:
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: groq-api-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: postgres-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

### Infrastructure as Code (Terraform)

```hcl
# terraform/main.tf
provider "aws" {
  region = "us-east-1"
}

# PostgreSQL RDS with pgvector extension
resource "aws_db_instance" "postgres" {
  identifier            = "financial-copilot-db"
  engine                = "postgres"
  engine_version        = "15.2"
  instance_class        = "db.t3.medium"
  allocated_storage      = 100
  storage_type          = "gp3"
  storage_encrypted     = true
  multi_az              = true  # Disaster recovery
  backup_retention_days = 30
  
  # Enable pgvector extension
  parameter_group_name = aws_db_parameter_group.postgres.id
}

# Redis for caching
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "copilot-cache"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version_parameter_group_name = "default.redis7"
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
}

# S3 for document storage
resource "aws_s3_bucket" "documents" {
  bucket = "financial-copilot-docs"
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  versioning_configuration {
    status = "Enabled"  # Document versioning
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ECS Cluster for FastAPI
resource "aws_ecs_cluster" "copilot" {
  name = "financial-copilot"
}

resource "aws_ecs_service" "copilot" {
  name            = "copilot"
  cluster         = aws_ecs_cluster.copilot.id
  task_definition = aws_ecs_task_definition.copilot.arn
  desired_count   = 3
  launch_type     = "FARGATE"
  
  load_balancer {
    target_group_arn = aws_lb_target_group.copilot.arn
    container_name   = "fastapi"
    container_port   = 8000
  }
}
```

---

## Monitoring & Observability

### Structured Logging (ELK Stack)

```python
# backend/app/core/logger.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_logger():
    logger = logging.getLogger("copilot")
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    return logger

logger = setup_logger()

# Usage in code
logger.info("pdf_uploaded", extra={
    "user_id": user_id,
    "document_id": doc_id,
    "file_size": file_size,
})
```

### Metrics & Tracing (Prometheus)

```python
# backend/app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Counters
uploads_total = Counter(
    'document_uploads_total',
    'Total documents uploaded',
    ['organization_id', 'status']
)

# Histograms (response times)
query_duration_seconds = Histogram(
    'query_duration_seconds',
    'Query response time',
    ['model', 'status'],
    buckets=(0.5, 1, 2, 5, 10)
)

# Gauges (current state)
active_embeddings = Gauge(
    'active_embeddings',
    'Number of vectors in index'
)

# Usage
@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile):
    try:
        # ... upload logic
        uploads_total.labels(organization_id=org_id, status="success").inc()
    except Exception as e:
        uploads_total.labels(organization_id=org_id, status="failure").inc()
        raise

@router.post("/ask")
async def ask(request: QuestionRequest):
    with query_duration_seconds.labels(model="llama-3.1-8b", status="success").time():
        # ... query logic
        pass
```

### Distributed Tracing (Jaeger)

```python
# backend/app/core/tracing.py
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent",
    agent_port=6831,
)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

FastAPIInstrumentor().instrument_app(app)

# Manual tracing in services
tracer = trace.get_tracer(__name__)

@staticmethod
def ask(query: str) -> dict:
    with tracer.start_as_current_span("rag_pipeline") as span:
        span.set_attribute("query", query)
        
        with tracer.start_as_current_span("embedding") as span:
            q_emb = EmbeddingService.embed_text(query)
        
        with tracer.start_as_current_span("vector_search") as span:
            context_chunks = RAGService.vector_store.search(q_emb, k=3)
        
        with tracer.start_as_current_span("llm_generation") as span:
            answer = LLMService.generate(context_chunks, query)
        
        return {"answer": answer, ...}
```

### Health Checks & Alerts

```python
# backend/app/api/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health():
    """Liveness probe for Kubernetes"""
    return {"status": "ok"}

@router.get("/ready")
async def readiness():
    """Readiness probe - checks all dependencies"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "groq_api": await check_groq(),
        "huggingface": await check_embeddings(),
    }
    
    if not all(checks.values()):
        raise HTTPException(503, "Service not ready", detail=checks)
    
    return {"status": "ready"}

async def check_database():
    try:
        await db.execute("SELECT 1")
        return True
    except:
        return False
```

---

## Scalability & Performance

### Horizontal Scaling Strategy

| Component | Scale Method | Limits |
|-----------|------------|--------|
| **FastAPI App** | K8s HPA (CPU >75%) | 50 replicas |
| **PostgreSQL** | Read replicas + sharding | 10TB+ with partitioning |
| **Redis** | Redis Cluster | 16 nodes max |
| **Groq API** | Batch requests | Rate: 500 req/min (free tier) |
| **S3 Storage** | Unlimited | Pay per GB |

### Database Optimization

```sql
-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Optimized embeddings table
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    document_id UUID NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(384),  -- 384-dimensional
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Create IVFFlat index for fast similarity search
CREATE INDEX ON embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Partition by organization for multi-tenancy
CREATE TABLE embeddings_org1 PARTITION OF embeddings
    FOR VALUES IN ('org-uuid-1');

-- Query with reranking (Reciprocal Rank Fusion)
SELECT id, chunk_text, embedding <-> $1::vector as distance
FROM embeddings
WHERE organization_id = $2::UUID
ORDER BY distance
LIMIT 10;
```

### Query Caching Strategy

```python
# backend/app/core/cache.py
import redis
import json
import hashlib
from datetime import timedelta

redis_client = redis.Redis(host="localhost", port=6379, db=0)

def get_cache_key(user_id: str, question: str) -> str:
    question_hash = hashlib.md5(question.encode()).hexdigest()
    return f"answer:{user_id}:{question_hash}"

def cache_answer(user_id: str, question: str, answer: dict, ttl_hours: int = 24):
    key = get_cache_key(user_id, question)
    redis_client.setex(
        key,
        timedelta(hours=ttl_hours),
        json.dumps(answer)
    )

def get_cached_answer(user_id: str, question: str) -> dict | None:
    key = get_cache_key(user_id, question)
    cached = redis_client.get(key)
    return json.loads(cached) if cached else None

@router.post("/ask")
async def ask(request: QuestionRequest, user = Depends(get_current_user)):
    # Try cache first
    cached = get_cached_answer(user["id"], request.question)
    if cached:
        return cached
    
    # Compute if not cached
    result = rag_pipeline.ask(request.question)
    
    # Cache result
    cache_answer(user["id"], request.question, result)
    
    return result
```

---

## Disaster Recovery

### Backup Strategy

| Data | Backup Method | Frequency | Retention |
|------|---------------|-----------|-----------|
| PostgreSQL | AWS RDS automated backups | Daily | 30 days |
| S3 Documents | Versioning + Cross-region replication | Continuous | 7 years |
| Redis | RDB snapshots | Hourly | 7 days |
| Application Code | GitHub (git history) | Per commit | Unlimited |

```hcl
# Terraform: Enable multi-region replication
resource "aws_s3_bucket_replication_configuration" "documents" {
  bucket   = aws_s3_bucket.documents.id
  role     = aws_iam_role.replication.arn
  
  rule {
    status = "Enabled"
    filter {
      prefix = ""
    }
    destination {
      bucket       = aws_s3_bucket.documents_backup.arn
      region       = "eu-west-1"  # Disaster recovery region
      storage_class = "GLACIER"   # Cost-optimized
    }
  }
}
```

### RTO and RPO Targets

- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 1 hour
- **Failover**: Automated DNS failover to backup region
- **Testing**: Monthly disaster recovery drills

### Runbook: Database Recovery

```bash
#!/bin/bash
# scripts/recovery/postgres_restore.sh

set -e

BACKUP_ID=${1:-latest}
RESTORE_DB="financial_copilot_restored"

echo "Starting PostgreSQL recovery from backup: $BACKUP_ID"

# 1. Get backup snapshot
SNAPSHOT=$(aws rds describe-db-snapshots \
  --db-instance-identifier financial-copilot-db \
  --query "DBSnapshots[0].DBSnapshotIdentifier" \
  --output text)

echo "Using snapshot: $SNAPSHOT"

# 2. Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier $RESTORE_DB \
  --db-snapshot-identifier $SNAPSHOT

# 3. Wait for restoration
aws rds wait db-instance-available \
  --db-instance-identifier $RESTORE_DB

echo "Database restored successfully"

# 4. Run integrity checks
psql postgresql://user:pass@$RESTORE_DB.xxxx.us-east-1.rds.amazonaws.com/copilot \
  --command "SELECT COUNT(*) FROM embeddings;"

echo "Recovery complete. Update DNS to point to $RESTORE_DB"
```

---

## Operational Runbooks

### Scaling Operations

#### Emergency Scale-Up
```bash
# 1. Increase replicas immediately
kubectl scale deployment copilot --replicas=10

# 2. Monitor metrics
kubectl top pods -l app=copilot

# 3. Fine-tune resources
kubectl set resources deployment copilot \
  --limits=cpu=1000m,memory=2Gi \
  --requests=cpu=500m,memory=512Mi
```

#### Database Connection Pooling Alert
```python
# Alert: If active connections > 80
if active_connections > db.max_connections * 0.8:
    # 1. Notify team
    send_alert("High database connections: " + active_connections)
    
    # 2. Kill idle connections
    for conn in db.get_idle_connections(idle_for_seconds=300):
        conn.terminate()
    
    # 3. Scale replicas for read
    increase_read_replicas()
```

### Incident Response

#### P1: API Down (99% requests failing)
```
1. Declare incident in Slack #incident-channel
2. Run: kubectl get pods -l app=copilot
3. If OOMKilled: Increase memory limits
4. If CrashLoopBackOff: Check logs with: kubectl logs <pod>
5. Rollback to last known good version: git revert <hash>
6. Update #incidents channel with status every 15 mins
```

#### P2: High Latency (>10 sec response time)
```
1. Check load balancer health: curl /health
2. Check database query performance: EXPLAIN ANALYZE
3. Check Redis hit rate: redis-cli INFO stats
4. Scale horizontally if CPU >80%
5. Investigate slow queries in application logs
```

---

## Integration Patterns

### Enterprise Systems Integration

#### Salesforce Integration
```python
# backend/app/integrations/salesforce.py
from simple_salesforce import Salesforce

sf = Salesforce(
    username=os.getenv("SALESFORCE_USERNAME"),
    password=os.getenv("SALESFORCE_PASSWORD"),
    security_token=os.getenv("SALESFORCE_SECURITY_TOKEN"),
)

@router.post("/integrations/salesforce/analyze")
async def analyze_salesforce_document(account_id: str):
    # 1. Get opportunity from Salesforce
    opportunity = sf.query(f"
        SELECT Id, Name, Description 
        FROM Opportunity 
        WHERE AccountId = '{account_id}' 
        LIMIT 1
    ")
    
    # 2. Generate AI insights using our copilot
    insights = await rag_service.ask(opportunity_description)
    
    # 3. Store insights back in Salesforce
    sf.Opportunity.update(opportunity_id, {
        'AI_Analysis__c': insights['answer'],
        'AI_Model_Used__c': insights['model'],
    })
    
    return insights
```

#### LMS Systems Integration
```python
# backend/app/integrations/lms.py
@router.post("/integrations/lms/upload")
async def upload_from_lms(
    course_id: str,
    document_id: str,
    lms_token: str = Header(...)
):
    # 1. Validate LMS token
    lms_user = validate_lms_token(lms_token)
    
    # 2. Fetch document from LMS
    doc_url = f"https://lms.example.com/api/documents/{document_id}"
    response = requests.get(doc_url, headers={"Authorization": f"Bearer {lms_token}"})
    
    # 3. Upload to our system
    result = await upload_and_index(response.content)
    
    # 4. Notify LMS of completion
    requests.post(f"{doc_url}/processed", json={"status": "success"})
    
    return result
```

### API Marketplace Listing

```json
{
  "api": {
    "title": "AI Financial Copilot API",
    "version": "1.0.0",
    "base_url": "https://api.ai-financial-copilot.com",
    "auth": {
      "type": "apiKey",
      "header": "X-API-Key"
    },
    "endpoints": [
      {
        "path": "/documents/upload",
        "method": "POST",
        "rate_limit": "100/minute",
        "pricing": "free ($0-$2/1000 documents)"
      },
      {
        "path": "/documents/{id}/query",
        "method": "POST",
        "rate_limit": "1000/minute",
        "pricing": "pay-as-you-go ($0.01/query)"
      }
    ]
  }
}
```

---

## Cost Optimization

### Cost Breakdown (Monthly)

| Component | Cost | Optimization |
|-----------|------|--------------|
| AWS ECS (3 replicas, t3.medium) | $120 | Use spot instances (-70%) |
| RDS PostgreSQL (db.t3.medium) | $80 | Reserve instance (-40%) |
| S3 Storage (1TB) | $25 | S3 Glacier for older docs |
| Redis (cache.t3.medium) | $50 | ElastiCache reserved (-35%) |
| **Groq API calls** | $200 | Batch requests, caching |
| **Huggingface API** | $50 | Local model hosting |
| **Total** | **~$525** | → **~$250 optimized** |

### Reserved Instances (45-55% savings)

```hcl
# Terraform: Purchase all 1-year reserved instances
resource "aws_ec2_reserved_instances" "fastapi" {
  instance_class   = "t3.medium"
  count            = 3
  instance_type    = "on-demand"
  offering_class   = "all-upfront"
  term             = "one_year"  # Cheapest option
}
```

### Smart Caching to Reduce API Calls

```python
# Cache strategies reduce external API costs
CACHE_STRATEGIES = {
    "hot": {"ttl": 24*3600, "hit_rate": 0.85},  # Frequently accessed
    "warm": {"ttl": 7*24*3600, "hit_rate": 0.50},  # Less frequent
    "cold": {"ttl": 30*24*3600, "hit_rate": 0.10},  # Rarely accessed
}

# Expected monthly savings:
# 10,000 queries/month
# Cache hit rate: 75% average
# Result: 7,500 cache hits, only 2,500 API calls
# Savings: 7,500 * $0.01 = $75/month
```

---

## SLA & Support

### Service Level Agreement (SLA)

| Metric | Target | Penalty |
|--------|--------|---------|
| Availability | 99.95% | 5% monthly credit per 0.1% below |
| Query Response Time (p95) | <10 sec | 2% credit if >10 sec |
| Document Upload Time (p95) | <5 sec | 2% credit if >5 sec |
| Mean Time to Recovery (MTTR) | <1 hour | 5% credit if MTTR >2 hours |

### Support Tiers

| Tier | Response Time | Support Hours | Cost |
|------|---------------|---------------|------|
| **Community** | Best effort | 24/7 (async) | Free |
| **Startup** | 4 hours | 5x9 | $500/month |
| **Professional** | 1 hour | 24/7 | $2000/month |
| **Enterprise** | 15 minutes | 24/7 + dedicated | Custom |

---

## Version & Changelog

**Current Version**: 1.0.0  
**Release Date**: February 2026

### Roadmap

- [ ] **v1.1.0**: Multi-document sessions, document versioning
- [ ] **v1.2.0**: Local LLM support (Llama2 on-prem)
- [ ] **v1.3.0**: Real-time streaming responses
- [ ] **v2.0.0**: GraphQL API, multi-tenant SaaS platform

---

## Contact & Support

- **Email**: enterprise-support@example.com
- **Slack**: #ai-copilot-enterprise (private)
- **Status Page**: https://status.ai-financial-copilot.com
- **Docs**: https://api.ai-financial-copilot.com/docs

---

**Last Updated**: February 23, 2026  
**Maintained By**: Platform Engineering Team
