# Nola Restaurant Analytics Platform

> Solução completa de analytics para restaurantes - Nola God Level Challenge 2025

Uma plataforma moderna e intuitiva que permite donos de restaurantes explorarem seus dados de forma flexível, criarem análises personalizadas e tomarem decisões baseadas em insights reais.

# O Problema que Resolvemos

Maria, dona de 3 restaurantes, tem acesso a dados de **vendas, produtos, clientes e operações** através de múltiplos canais (presencial, iFood, Rappi, app próprio), mas não consegue:

- Responder perguntas específicas sobre seu negócio
- Criar visualizações personalizadas sem depender de desenvolvedores
- Identificar tendências e anomalias rapidamente
- Comparar performance de lojas e canais facilmente

# Nossa Solução

Uma plataforma de analytics **específica para restaurantes** que oferece:

- **Dashboard Principal**: Visão geral com métricas-chave e comparação temporal
- **Análises Customizadas**: Query builder visual para criar análises sob demanda
- **Comparação de Lojas**: Performance detalhada de cada loja
- **Insights Automáticos**: IA identifica padrões, anomalias e oportunidades
- **Performance**: Queries otimizadas com cache (< 500ms)
- **UX Intuitiva**: Interface moderna e responsiva

# Quick Start

## Pré-requisitos

- Docker e Docker Compose
- Git

## Instalação Rápida (Recomendado)

```powershell
# 1. Clone o repositório
git clone https://github.com/GaabrielCH/nola-god-level-challenge.git
cd nola-god-level-challenge

# 2. Suba o banco de dados PostgreSQL
docker compose up -d postgres

# 3. Aguarde o banco ficar pronto (20-30 segundos)
Start-Sleep -Seconds 30

# 4. Instale dependências Python para o gerador de dados
pip install psycopg2-binary faker tqdm

# 5. Gere os dados de teste (300k vendas - leva 5-10 minutos)
python generate_data.py

# 6. Inicie todos os serviços (backend, frontend, redis)
docker compose up -d

# 7. Aguarde os containers iniciarem (15-20 segundos)
Start-Sleep -Seconds 20

# 8. Acesse a aplicação
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs (Swagger): http://localhost:8000/docs
```

**Verificar se está rodando:**
```powershell
docker compose ps
# Deve mostrar 4 containers: postgres, redis, backend, frontend
```

## Sem Docker (Desenvolvimento Local)

**Backend:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure .env
copy .env.example .env

# Inicie o servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```powershell
cd frontend
npm install
npm run dev
```

# Funcionalidades

## 1. Dashboard Principal

**Métricas em tempo real:**
- Faturamento total com comparação ao período anterior
- Número de vendas e crescimento
- Ticket médio e variação
- Total de descontos aplicados

**Visualizações:**
- Série temporal de faturamento
- Performance por canal (iFood, Rappi, Presencial, etc.)
- Top 10 produtos mais vendidos
- Distribuição de vendas por horário

**Filtros:**
- Intervalo de datas customizável
- Seleção múltipla de lojas
- Atualização em tempo real

## 2. Análises Customizadas

**Query Builder Visual:**
- Selecione a **métrica**: Faturamento, Vendas, Ticket Médio, Tempo de Produção, Tempo de Entrega
- Agrupe por: Loja, Canal, Produto, Dia da Semana, Horário
- Escolha o período: Hora, Dia, Semana, Mês
- Filtre por intervalo de datas

**Visualizações Dinâmicas:**
- Gráfico de linha (série temporal)
- Gráfico de barras (agregações)
- Tabela de dados detalhados
- Exportação de dados (CSV)

## 3. Comparação de Lojas

**Análise Competitiva:**
- Ranking de lojas por faturamento
- Comparação de número de vendas
- Ticket médio por loja
- Localização e cidade de cada loja

**Visualizações:**
- Gráficos de barras horizontais para fácil comparação
- Cards individuais com métricas de cada loja
- Destaque para top performers

## 4. Insights Automáticos

**IA identifica automaticamente:**
- **Tendências**: Crescimento/queda de receita significativa
- **Anomalias**: Quedas críticas que precisam atenção
- **Performance**: Canais e horários de melhor desempenho
- **Recomendações**: Ações sugeridas baseadas nos dados

**Tipos de Insights:**
- **Info**: Padrões interessantes identificados
- **Warning**: Situações que merecem atenção
- **Critical**: Problemas urgentes detectados

# Arquitetura

## Stack Tecnológica

**Backend:**
- **FastAPI**: API REST moderna e rápida
- **PostgreSQL**: Banco de dados relacional
- **Redis**: Cache para otimização de queries
- **SQLAlchemy**: ORM para queries complexas
- **Pandas**: Manipulação e análise de dados

**Frontend:**
- **React 18**: UI moderna e reativa
- **TypeScript**: Type safety e melhor DX
- **Recharts**: Visualizações de dados
- **TanStack Query**: Gerenciamento de estado e cache
- **Vite**: Build tool rápida

**Infraestrutura:**
- **Docker & Docker Compose**: Containerização
- **Nginx** (produção): Reverse proxy

## Arquitetura de Alto Nível

```

   Cliente   
  (Browser)  

       
        HTTP
       

   Frontend      
   React + TS    

       
        REST API
       
      
   Backend API       Redis    
    FastAPI               (Cache)   
      
       
        SQL
       

   PostgreSQL    
   (500k sales)  

```

## Fluxo de Dados

1. **Usuário** seleciona filtros e métricas no frontend
2. **Frontend** faz requisição à API com parâmetros
3. **Backend** verifica cache Redis
   - Se cached: retorna imediatamente
   - Se não: executa query no PostgreSQL
4. **Query Service** constrói query SQL dinâmica com:
   - Filtros (data, loja, canal)
   - Agregações (SUM, AVG, COUNT)
   - Group by (loja, canal, produto, tempo)
5. **PostgreSQL** executa query otimizada (< 500ms)
6. **Backend** processa resultado e cacheia
7. **Frontend** renderiza visualizações

## Otimizações de Performance

**Banco de Dados:**
- Índices em colunas chave (`created_at`, `store_id`, `channel_id`)
- Índices compostos para queries frequentes
- Particionamento por data (futura melhoria)
- Agregações pré-computadas para queries comuns

**API:**
- Cache Redis com TTL de 5 minutos
- Cache key baseado em hash de parâmetros
- Connection pooling (10 conexões base, 20 max)
- Queries assíncronas quando possível

**Frontend:**
- React Query para cache client-side
- Debouncing em filtros
- Lazy loading de componentes
- Virtualization para listas grandes

# Estrutura do Projeto

```
nola-god-level-desafio/
 backend/
    main.py              # FastAPI app principal
    models.py            # SQLAlchemy models
    schemas.py           # Pydantic schemas
    database.py          # Conexão e sessão DB
    query_service.py     # Query builder dinâmico
    cache_service.py     # Redis cache
    config.py            # Configurações
    requirements.txt     # Dependências Python
    Dockerfile

 frontend/
    src/
       main.tsx         # Entry point
       App.tsx          # App principal
       api.ts           # Client API
       pages/
          Dashboard.tsx
          Analytics.tsx
          StoreComparison.tsx
          CustomDashboard.tsx
       index.css        # Estilos globais
    package.json
    tsconfig.json
    vite.config.ts
    Dockerfile

 docker-compose.yml       # Orquestração
 database-schema.sql      # Schema PostgreSQL
 generate_data.py         # Gerador de dados
 README.md                # Este arquivo
 ARCHITECTURE.md          # Decisões arquiteturais
```

# Screenshots

## Dashboard Principal
- Visão geral com métricas-chave
- Gráficos de linha e barras
- Filtros interativos

## Análises Customizadas
- Query builder visual
- Múltiplas visualizações
- Tabela de dados detalhados

## Comparação de Lojas
- Ranking de performance
- Gráficos comparativos
- Cards individuais por loja

## Insights Automáticos
- Lista de insights categorizados
- Recomendações acionáveis
- Alertas de anomalias

# Configuração Avançada

## Variáveis de Ambiente

**Backend (`.env`):**
```env
DATABASE_URL=postgresql://challenge:challenge_2024@postgres:5432/challenge_db
REDIS_URL=redis://redis:6379
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Frontend (`.env`):**
```env
VITE_API_URL=http://localhost:8000
```

## Geração de Dados Customizada

```powershell
python generate_data.py `
  --db-url postgresql://user:pass@host:port/db `
  --stores 100 `
  --products 1000 `
  --customers 50000 `
  --months 12
```

# API Endpoints

## Metadata
- `GET /api/stores` - Lista de lojas
- `GET /api/channels` - Lista de canais
- `GET /api/products` - Lista de produtos
- `GET /api/categories` - Lista de categorias

## Dashboard
- `POST /api/dashboard/overview` - Overview com métricas principais

## Analytics
- `POST /api/analytics/time-series` - Série temporal
- `POST /api/analytics/aggregation` - Agregações customizadas
- `POST /api/analytics/top-products` - Top produtos
- `POST /api/analytics/store-comparison` - Comparação de lojas
- `GET /api/analytics/insights` - Insights automáticos

## Utilities
- `GET /api/health` - Health check
- `DELETE /api/cache/clear` - Limpar cache

**Documentação interativa:** http://localhost:8000/docs

# Testes

```powershell
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test

# E2E
npm run test:e2e
```

# Deploy (Produção)

## Opção 1: Docker Compose (Recomendado)

```powershell
# Build e start
docker compose -f docker-compose.prod.yml up -d

# Acesse em http://seu-dominio.com
```

## Opção 2: Cloud (AWS/Azure/GCP)

**Backend:** Deploy FastAPI como container ou serverless
**Frontend:** Deploy estático (S3, Vercel, Netlify)
**Banco:** RDS PostgreSQL ou similar
**Cache:** ElastiCache Redis ou similar

## Troubleshooting

### Porta já em uso
```powershell
# Verificar o que está usando a porta
netstat -ano | findstr :5432
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Parar containers e tentar novamente
docker compose down
docker compose up -d
```

### Backend não está carregando dados
```powershell
# Ver logs do backend
docker compose logs backend --tail=50

# Reiniciar backend
docker compose restart backend

# Limpar cache Redis
docker compose exec redis redis-cli FLUSHALL
```

### Frontend mostra página em branco
```powershell
# Ver logs do frontend
docker compose logs frontend --tail=30

# Rebuild e restart
docker compose down
docker compose up -d --build
```

### Dados não foram gerados
```powershell
# Verificar se PostgreSQL está rodando
docker compose ps postgres

# Verificar conexão com banco
docker compose exec postgres psql -U challenge -d challenge_db -c "SELECT COUNT(*) FROM sales;"

# Se não houver dados, gerar novamente
python generate_data.py
```

### Docker Desktop não está rodando (Windows)
```powershell
# Iniciar Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Aguardar 30-60 segundos
Start-Sleep -Seconds 60

# Tentar novamente
docker compose up -d
```

## Métricas de Performance

**Queries:**
- Média: < 200ms
- P95: < 500ms
- P99: < 1000ms

**API Response Time:**
- Cached: < 50ms
- Uncached: < 500ms

**Frontend:**
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Lighthouse Score: > 90

# Contribuindo

Este é um projeto do Nola God Level Challenge. Para questões ou sugestões:

- Discord: https://discord.gg/pRwmm64Vej
- Email: gsilvestre@arcca.io

# Decisões Arquiteturais

Para entender as escolhas técnicas e trade-offs, leia: [ARCHITECTURE.md](./ARCHITECTURE.md)

# Licença

Este projeto foi desenvolvido para o Nola God Level Challenge 2025.

# Autor

Desenvolvido para o Nola God Level Challenge
- Challenge: Resolver analytics para 10.000+ restaurantes
- Prazo: 1 semana
- Stack: Python/FastAPI + React/TypeScript + PostgreSQL + Redis

---

Feito para Maria e todos os donos de restaurantes que precisam de insights para crescer!
