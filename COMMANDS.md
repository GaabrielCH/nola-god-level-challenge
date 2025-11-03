#  Comandos Úteis - Nola Analytics

Referência rápida de comandos para desenvolvimento e troubleshooting.

# Docker Compose

## Básico
```powershell
# Iniciar tudo
docker compose up -d

# Parar tudo
docker compose down

# Ver logs
docker compose logs -f

# Ver logs de um serviço específico
docker compose logs -f backend
docker compose logs -f frontend

# Status dos containers
docker compose ps

# Rebuild containers
docker compose build --no-cache

# Remover tudo (incluindo volumes)
docker compose down -v
```

## Desenvolvimento
```powershell
# Apenas banco de dados
docker compose up -d postgres redis

# Restart um serviço
docker compose restart backend

# Entrar em container
docker compose exec backend bash
docker compose exec postgres psql -U challenge challenge_db
docker compose exec redis redis-cli
```

# Banco de Dados

## PostgreSQL
```powershell
# Conectar ao banco
docker compose exec postgres psql -U challenge challenge_db

# Queries úteis
SELECT COUNT(*) FROM sales;
SELECT COUNT(*) FROM stores;
SELECT COUNT(*) FROM customers;

# Ver tamanho das tabelas
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Ver índices
\di

# Ver estrutura de uma tabela
\d sales

# Backup
docker compose exec postgres pg_dump -U challenge challenge_db > backup.sql

# Restore
docker compose exec -T postgres psql -U challenge challenge_db < backup.sql
```

## Redis
```powershell
# Conectar ao Redis
docker compose exec redis redis-cli

# Ver todas as keys
KEYS *

# Ver valor de uma key
GET dashboard:overview:abc123

# Limpar tudo
FLUSHALL

# Ver estatísticas
INFO stats

# Ver uso de memória
INFO memory
```

# Backend (FastAPI)

## Local Development
```powershell
cd backend

# Criar venv
python -m venv venv

# Ativar venv
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Rodar com logs debug
uvicorn main:app --reload --log-level debug
```

## Testes
```powershell
# Instalar pytest
pip install pytest pytest-cov

# Rodar testes
pytest

# Com coverage
pytest --cov=.

# Teste específico
pytest tests/test_api.py::test_health_check
```

## API Testing
```powershell
# Health check
curl http://localhost:8000/api/health

# Get stores
curl http://localhost:8000/api/stores

# Dashboard (com parâmetros)
$params = @{
    start_date = "2024-01-01"
    end_date = "2024-12-31"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/api/dashboard/overview -Method Post -Body $params -ContentType "application/json"

# Clear cache
Invoke-RestMethod -Uri http://localhost:8000/api/cache/clear -Method Delete
```

# Frontend (React)

## Local Development
```powershell
cd frontend

# Instalar dependências
npm install

# Rodar dev server
npm run dev

# Build para produção
npm run build

# Preview build de produção
npm run preview

# Lint
npm run lint
```

## Troubleshooting
```powershell
# Limpar node_modules e reinstalar
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install

# Limpar cache do Vite
Remove-Item -Recurse -Force .vite
npm run dev
```

# Geração de Dados

## Básico
```powershell
# Gerar dados padrão (500k vendas)
python generate_data.py

# Com URL customizada
python generate_data.py --db-url postgresql://user:pass@host:port/db
```

## Customizado
```powershell
# Mais lojas
python generate_data.py --stores 100

# Mais produtos
python generate_data.py --products 1000

# Mais clientes
python generate_data.py --customers 50000

# Mais meses de histórico
python generate_data.py --months 12

# Combinado
python generate_data.py `
  --stores 100 `
  --products 1000 `
  --customers 50000 `
  --months 12
```

# Performance Monitoring

## Docker Stats
```powershell
# Ver uso de recursos em tempo real
docker stats

# Específico para nossos containers
docker stats nola-analytics-backend nola-analytics-frontend nola-analytics-db nola-analytics-redis
```

## PostgreSQL Performance
```sql
-- Queries mais lentas
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Cache hit ratio (deve ser > 95%)
SELECT
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;

-- Queries ativas
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active';
```

## Redis Performance
```redis
# Estatísticas de cache
INFO stats

# Hit rate
INFO stats | grep keyspace

# Comandos mais usados
INFO commandstats
```

# Troubleshooting Comum

## Port Already in Use
```powershell
# Ver o que está usando a porta 5432
netstat -ano | findstr :5432

# Matar processo (substitua PID)
taskkill /PID <PID> /F

# Ou mudar porta no docker-compose.yml
```

## Out of Memory
```powershell
# Ver uso de memória
docker stats --no-stream

# Limpar images não usadas
docker image prune -a

# Limpar volumes não usados
docker volume prune

# Limpar tudo
docker system prune -a --volumes
```

## Database Connection Error
```powershell
# Verificar se PostgreSQL está rodando
docker compose ps postgres

# Ver logs
docker compose logs postgres

# Restart
docker compose restart postgres

# Testar conexão
docker compose exec postgres pg_isready -U challenge
```

## Frontend Can't Connect to Backend
```powershell
# Verificar se backend está rodando
docker compose ps backend

# Ver logs
docker compose logs backend

# Testar API diretamente
curl http://localhost:8000/api/health

# Verificar variável de ambiente no frontend
docker compose exec frontend env | grep VITE_API_URL
```

# Git

## Workflow
```powershell
# Status
git status

# Add changes
git add .

# Commit
git commit -m "feat: add new feature"

# Push
git push origin main

# Ver histórico
git log --oneline --graph --all

# Criar branch
git checkout -b feature/nova-feature

# Merge branch
git checkout main
git merge feature/nova-feature
```

## Conventional Commits
```
feat: Nova feature
fix: Correção de bug
docs: Documentação
style: Formatação
refactor: Refatoração
test: Testes
chore: Manutenção
```

# Deploy

## Produção
```powershell
# Build e start
docker compose -f docker-compose.prod.yml up -d --build

# Ver logs
docker compose -f docker-compose.prod.yml logs -f

# Stop
docker compose -f docker-compose.prod.yml down
```

## Backup Completo
```powershell
# Criar diretório de backup
New-Item -ItemType Directory -Path backup -Force

# Backup do banco
docker compose exec postgres pg_dump -U challenge challenge_db > backup/db_backup_$(Get-Date -Format "yyyy-MM-dd").sql

# Backup de volumes
docker run --rm -v nola-god-level-desafio_postgres_data:/data -v ${PWD}/backup:/backup alpine tar czf /backup/postgres_data_$(Get-Date -Format "yyyy-MM-dd").tar.gz -C /data .

# Backup de código
git archive --format=zip --output=backup/code_$(Get-Date -Format "yyyy-MM-dd").zip HEAD
```

# Monitoring

## Health Checks
```powershell
# API Health
$response = Invoke-RestMethod -Uri http://localhost:8000/api/health
Write-Host "API Status: $($response.status)"

# Database Health
docker compose exec postgres pg_isready -U challenge

# Redis Health
docker compose exec redis redis-cli ping
```

## Logs em Tempo Real
```powershell
# Todos os serviços
docker compose logs -f --tail=100

# Específico com timestamp
docker compose logs -f --tail=100 --timestamps backend
```

# Úteis para Demo

## Aquece Cache
```powershell
# Faz algumas requests para popular cache
$dates = @{
    start_date = "2024-01-01"
    end_date = "2024-12-31"
} | ConvertTo-Json

# Dashboard
Invoke-RestMethod -Uri http://localhost:8000/api/dashboard/overview -Method Post -Body $dates -ContentType "application/json"

# Stores
Invoke-RestMethod -Uri http://localhost:8000/api/stores

# Channels
Invoke-RestMethod -Uri http://localhost:8000/api/channels
```

## Reset Completo
```powershell
# Para tudo, remove volumes, rebuild, restart
docker compose down -v
docker compose build --no-cache
docker compose up -d postgres
Start-Sleep -Seconds 30
python generate_data.py
docker compose up -d
```

---

** Dica**: Salve esses comandos como aliases no seu PowerShell profile para acesso rápido!
