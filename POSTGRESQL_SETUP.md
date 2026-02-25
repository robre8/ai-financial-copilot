# 🗄️ PostgreSQL + pgvector Setup Guide

Este proyecto usa **PostgreSQL con pgvector** para almacenamiento persistente de embeddings vectoriales. Aquí te explico cómo configurarlo localmente y en producción con Render.

---

## 📋 Tabla de Contenidos

1. [Setup Local con Docker](#setup-local-con-docker)
2. [Setup con PostgreSQL Local](#setup-con-postgresql-local)
3. [Setup en Render (Producción)](#setup-en-render-producción)
4. [Verificar Instalación](#verificar-instalación)
5. [Troubleshooting](#troubleshooting)

---

## 🐳 Setup Local con Docker

**La forma más fácil de empezar:**

### 1. Instalar Docker Desktop

- Windows/Mac: https://www.docker.com/products/docker-desktop
- Linux: https://docs.docker.com/engine/install/

### 2. Levantar PostgreSQL con pgvector

```bash
# En la raíz del proyecto
docker-compose up -d postgres
```

Esto crea:
- PostgreSQL 15 con extensión **pgvector**
- Base de datos: `ai_copilot`
- Usuario: `postgres`
- Password: `postgres`
- Puerto: `5432`

### 3. Verificar que está corriendo

```bash
docker ps
```

Deberías ver el contenedor `ai-copilot-postgres` running.

### 4. Configurar .env

```bash
cd backend
cp .env.example .env
```

Edita `backend/.env` y asegúrate de tener:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_copilot
```

### 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 6. Iniciar backend

```bash
cd backend
uvicorn app.main:app --reload
```

El servidor creará las tablas automáticamente en el evento `startup`.

---

## 💻 Setup con PostgreSQL Local

Si prefieres instalar PostgreSQL directamente en tu máquina:

### 1. Instalar PostgreSQL 15+

- **Windows**: https://www.postgresql.org/download/windows/
- **Mac**: `brew install postgresql@15`
- **Linux**: `sudo apt install postgresql-15`

### 2. Instalar extensión pgvector

```bash
# Clone pgvector
git clone https://github.com/pgvector/pgvector.git
cd pgvector

# Build and install
make
sudo make install
```

O con Homebrew (Mac):
```bash
brew install pgvector
```

### 3. Crear base de datos

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE ai_copilot;

# Conectar a la base de datos
\c ai_copilot

# Habilitar extensión pgvector
CREATE EXTENSION vector;

# Verificar
\dx
```

### 4. Configurar .env

```env
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/ai_copilot
```

---

## ☁️ Setup en Render (Producción)

### Paso 1: Crear PostgreSQL Database

1. **Ir a Render Dashboard**: https://dashboard.render.com
2. **New → PostgreSQL**
3. Configurar:
   - **Name**: `ai-copilot-db`
   - **Database**: `ai_copilot`
   - **User**: (autogenerado)
   - **Region**: Oregon (US West) - más barato
   - **Plan**: Free (si es para testing) o Starter ($7/mes)

4. **Esperar 2-3 minutos** hasta que diga "Available"

### Paso 2: Habilitar pgvector

Render incluye pgvector por defecto en PostgreSQL 15+, pero debes habilitarlo:

**Opción A - Desde Render Dashboard:**

1. En tu database, ir a **"Shell"** tab
2. Ejecutar:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

**Opción B - Conectarte con psql:**

1. Copiar "External Database URL" desde Render
2. Conectarte:
   ```bash
   psql [EXTERNAL_DATABASE_URL]
   ```
3. Ejecutar:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   \dx  -- verificar que vector aparece
   \q
   ```

### Paso 3: Configurar Variables de Entorno

En tu **Web Service** de Render (el backend de FastAPI):

1. Ir a **Environment** tab
2. Agregar:

```env
DATABASE_URL = [Internal Database URL]
```

⚠️ **IMPORTANTE**: Usa la **Internal Database URL**, NO la External. Es más rápida y gratis.

Para copiarla:
- Ve a tu PostgreSQL database en Render
- Copia la **"Internal Database URL"**
- Formato: `postgresql://user:pass@dpg-xxxxx/ai_copilot`

### Paso 4: Otras Variables Requeridas

Asegúrate de tener también:

```env
HF_TOKEN=hf_...
GROQ_API_KEY=gsk_...
API_KEYS=prod-key-xyz:admin:ProductionKey
LLM_TIMEOUT=30
EMBEDDING_TIMEOUT=20
MAX_RETRIES=3
RETRY_MULTIPLIER=2
FRONTEND_ORIGINS=https://tu-frontend.vercel.app
```

### Paso 5: Redesplegar Backend

```bash
# Push changes para trigger redeploy
git push origin main
```

O desde Render Dashboard:
- **Manual Deploy → Deploy latest commit**

### Paso 6: Verificar Logs

Render logs deberían mostrar:

```
🚀 Starting Financial RAG Copilot...
✅ pgvector extension enabled
✅ Database tables created
✅ Database initialized successfully
```

---

## ✅ Verificar Instalación

### Test local:

```bash
# 1. Verificar conexión a PostgreSQL
python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    print(result.fetchone())
"

# 2. Verificar pgvector
python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT * FROM pg_extension WHERE extname = \\'vector\\''))
    print('pgvector:', result.fetchone())
"

# 3. Verificar tablas creadas
python -c "
from app.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print('Tables:', inspector.get_table_names())
"
```

### Test con API:

```bash
# Upload a PDF
curl -X POST http://localhost:8000/upload-pdf \
  -H "X-API-Key: demo-key-12345" \
  -F "file=@test.pdf"

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the revenue?"}'
```

---

## 🔧 Troubleshooting

### Error: "No module named 'pgvector'"

```bash
pip install pgvector==0.3.7
```

### Error: "extension 'vector' does not exist"

```sql
-- Conectar a la base de datos
psql [DATABASE_URL]

-- Crear extensión
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar
\dx
```

### Error: "could not connect to server"

Verifica:
1. PostgreSQL está corriendo: `docker ps` o `pg_isready`
2. DATABASE_URL está correcto en `.env`
3. Puerto 5432 está abierto: `telnet localhost 5432`

### Error: "relation 'documents' does not exist"

Las tablas se crean automáticamente en startup. Si no:

```python
python -c "
from app.database import init_db
init_db()
"
```

### Render: "Connection refused"

1. Verifica que usas **Internal Database URL**, no External
2. Asegúrate de que el database está "Available" (no "Creating")
3. Verifica que ambos servicios están en la **misma región**

### Tests fallan con "SQLite doesn't support vector"

Los integration tests usan SQLite in-memory por defecto. Para tests completos con pgvector:

1. Levanta PostgreSQL de testing:
   ```bash
   docker run -d -p 5433:5432 \
     -e POSTGRES_PASSWORD=test \
     ankane/pgvector:latest
   ```

2. Actualiza tests para usar:
   ```python
   TEST_DATABASE_URL = "postgresql://postgres:test@localhost:5433/postgres"
   ```

---

## 📊 Monitoring en Producción

### Ver documentos indexados:

```sql
SELECT COUNT(*) FROM documents;
```

### Ver tamaño de la base de datos:

```sql
SELECT 
    pg_size_pretty(pg_database_size('ai_copilot')) as size;
```

### Ver queries más lentas:

```sql
SELECT 
    query, 
    mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

### Limpiar documentos viejos:

```sql
DELETE FROM documents 
WHERE created_at < NOW() - INTERVAL '30 days';
```

---

## 🚀 Siguientes Pasos

- [ ] Configurar backups automáticos en Render
- [ ] Agregar índices HNSW para búsquedas más rápidas
- [ ] Implementar partitioning por fecha
- [ ] Agregar monitoring con Sentry
- [ ] Configurar connection pooling con PgBouncer

---

## 📚 Recursos

- **pgvector Docs**: https://github.com/pgvector/pgvector
- **Render PostgreSQL**: https://render.com/docs/databases
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **FastAPI Database Tutorial**: https://fastapi.tiangolo.com/tutorial/sql-databases/

---

¿Problemas? Abre un issue en GitHub o consulta los logs de Render.
