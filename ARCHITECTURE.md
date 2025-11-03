#  Decisões Arquiteturais - Nola Restaurant Analytics

# Contexto

Este documento explica **por que** escolhemos determinadas tecnologias e padrões arquiteturais para resolver o problema de analytics para restaurantes.

# Princípios Norteadores

1. **Simplicidade > Complexidade**: Usar ferramentas conhecidas e bem documentadas
2. **Performance Importa**: Queries < 500ms é requisito não-negociável
3. **UX First**: Interface intuitiva para usuários não-técnicos
4. **Escalabilidade Pragmática**: Preparado para crescer, mas não over-engineered
5. **Manutenibilidade**: Código limpo, bem estruturado e documentado

# Decisões de Stack

## Backend: Python + FastAPI

**Por que Python?**
-  Excelente para manipulação de dados (Pandas, NumPy)
-  Rico ecossistema para analytics e BI
-  Familiaridade da equipe Nola/Arcca
-  Performance adequada com otimizações

**Por que FastAPI (não Flask/Django)?**
-  **Performance**: Async nativo, muito mais rápido que Flask
-  **Type Safety**: Pydantic schemas com validação automática
-  **Docs Automática**: OpenAPI/Swagger out-of-the-box
-  **Moderno**: Async/await, type hints, dependency injection
-  Django seria overkill (não precisamos de admin, ORM completo, etc.)

**Alternativas Consideradas:**
- **Node.js + Express**: Descartado - Python é melhor para data processing
- **Go**: Descartado - Curva de aprendizado maior, menos libs de analytics

## Frontend: React + TypeScript

**Por que React?**
-  **Ecossistema Rico**: Recharts, TanStack Query, routing maduro
-  **Component-Based**: Reutilização e manutenibilidade
-  **Performance**: Virtual DOM e otimizações internas
-  **Flexibilidade**: Não opinionado, escolhemos padrões

**Por que TypeScript?**
-  **Type Safety**: Detecta erros em tempo de desenvolvimento
-  **Intellisense**: Melhor DX com autocomplete
-  **Refactoring**: Mudanças com confiança
-  **Documentação**: Tipos como documentação viva

**Alternativas Consideradas:**
- **Vue.js**: Excelente opção, mas React tem mais libs de visualização
- **Angular**: Muito opinionado e pesado para o projeto
- **Svelte**: Jovem demais, menos libs de charts

## Visualizações: Recharts

**Por que Recharts?**
-  **React-First**: Componentes nativos React
-  **Customizável**: Controle total sobre aparência
-  **Performance**: Otimizado para grandes datasets
-  **Responsivo**: Funciona bem em mobile

**Alternativas Consideradas:**
- **Chart.js**: Bom, mas não é React-first
- **D3.js**: Muito poderoso mas complexo, overkill
- **Plotly**: Pesado, features demais que não precisamos
- **Victory**: Similar ao Recharts, mas menos maduro

## Banco de Dados: PostgreSQL

**Por que PostgreSQL?**
-  **Requisito do Desafio**: Schema fornecido é PostgreSQL
-  **ACID Compliant**: Confiabilidade em transações
-  **Analytical Queries**: Window functions, CTEs, JSON support
-  **Extensível**: PostGIS para geolocalização futura
-  **Open Source**: Sem custos de licença

**Otimizações Implementadas:**
- Índices em colunas de filtro frequente (`created_at`, `store_id`, `channel_id`)
- Índices compostos para queries específicas
- Connection pooling (10 base, 20 max)
- Query timeout de 30s

**Futuro (se escalar muito):**
- TimescaleDB extension para séries temporais
- Particionamento por data
- Read replicas para analytics

## Cache: Redis

**Por que Redis?**
-  **Velocidade**: In-memory, sub-millisecond latency
-  **Simplicidade**: Key-value store, fácil de usar
-  **TTL Automático**: Expiração de cache sem lógica extra
-  **Ubíquo**: Presente em toda stack moderna

**Estratégia de Cache:**
```python
# Cache key format
key = f"{endpoint}:{hash(params)}"
ttl = 300  # 5 minutos

# Exemplo
"dashboard:overview:a1b2c3d4" -> TTL 5min
"timeseries:revenue:day:e5f6g7h8" -> TTL 5min
"stores:all" -> TTL 1hora (muda raramente)
```

**Por que 5 minutos?**
- Trade-off entre freshness e performance
- Dados de vendas não mudam retroativamente
- Maria não precisa de real-time, near-real-time suficiente

**Alternativas Consideradas:**
- **Memcached**: Mais simples, mas sem TTL automático nem estruturas complexas
- **In-Memory Dict**: Não persiste, perde cache ao reiniciar
- **Sem Cache**: Performance inaceitável para queries complexas

# Arquitetura de Código

## Backend: Layered Architecture

```
API Layer (main.py)
    ↓
Service Layer (query_service.py)
    ↓
Data Layer (models.py + SQLAlchemy)
    ↓
Database (PostgreSQL)
```

**Por quê?**
-  **Separation of Concerns**: Cada camada tem responsabilidade clara
-  **Testabilidade**: Fácil mockar camadas
-  **Manutenibilidade**: Mudanças isoladas
-  **Escalabilidade**: Fácil adicionar microserviços depois

**Por que NÃO microserviços agora?**
-  Over-engineering para MVP
-  Complexidade de deployment
-  Latência de network entre serviços
-  Monolito modular é suficiente (e mais rápido)

## Query Service: Dynamic Query Builder

**Problema:**
- Usuário quer queries flexíveis
- Não podemos pré-computar todas combinações
- SQL injection é risco

**Solução:**
```python
class QueryService:
    def get_aggregation(metric, group_by, filters):
        # Constrói query SQLAlchemy dinâmica
        query = session.query(
            self._get_metric_expr(metric),
            *self._get_group_by_exprs(group_by)
        )
        query = self._apply_filters(query, filters)
        return query.all()
```

**Benefícios:**
-  **Seguro**: SQLAlchemy previne injection
-  **Flexível**: Qualquer combinação de métrica + dimensão
-  **Otimizado**: Gera SQL eficiente
-  **Type-Safe**: Pydantic valida inputs

**Por que não query string SQL direta?**
-  SQL injection risk
-  Parsing complexo
-  Validação manual

## Frontend: Feature-Based Structure

```
src/
 pages/           # Uma página = uma feature
    Dashboard.tsx
    Analytics.tsx
    ...
 api.ts           # Cliente API centralizado
 main.tsx         # Entry point
```

**Por quê?**
-  **Colocação**: Features relacionadas juntas
-  **Escalável**: Adicionar features não mexe em outras
-  **Simples**: Não over-engineer com atomic design ainda

**Quando refatorar?**
- Se componentes forem reutilizados 3+ vezes → extrair para `/components`
- Se lógica de API crescer muito → extrair hooks customizados

## State Management: TanStack Query (não Redux)

**Por que TanStack Query?**
-  **Server State**: Feito para dados de API
-  **Cache Automático**: Não reimplementar cache logic
-  **Refetch Automático**: Background updates
-  **Loading/Error States**: Gerenciados automaticamente

**Por que NÃO Redux?**
-  Boilerplate excessivo
-  Projetado para client state, não server state
-  Over-engineering para nosso caso

**Quando usar Redux?**
- Se tivéssemos estado complexo compartilhado (user settings, UI preferences)
- Se precisássemos time-travel debugging
- Se houvesse lógica de negócio complexa no frontend

# Decisões de UX

## Filtros Sempre Visíveis

**Por quê?**
-  **Affordance**: Usuário vê o que pode fazer
-  **Contexto**: Sempre sabe os filtros ativos
-  **Rapidez**: Não precisa abrir modal

**Alternativa Considerada:**
- Modal de filtros → Descartado, esconde funcionalidade

## Comparação Temporal Automática

**Por quê?**
-  **Context**: "Está melhor ou pior?" é pergunta comum
-  **Actionable**: Delta % mostra direção
-  **Simples**: Não requer configuração manual

**Implementação:**
```typescript
// Se período é 30 dias
periodo_atual = [hoje - 30, hoje]
periodo_anterior = [hoje - 60, hoje - 30]

// Calcula delta
delta = (atual - anterior) / anterior * 100
```

## Insights Automáticos (não só dashboards)

**Por quê?**
-  **Proativo**: Sistema sugere, não só responde
-  **Acionável**: Recomendações práticas
-  **Educativo**: Ensina o que observar

**Algoritmo Simples:**
```python
# Exemplo: Detectar queda de receita
if revenue_change < -15%:
    insight = {
        "type": "anomaly",
        "severity": "critical",
        "title": "Queda significativa na receita",
        "description": f"Caiu {abs(change)}%",
        "action": "Revisar operações e causas"
    }
```

**Futuro:**
- Machine Learning para detecção de anomalias
- Previsão de demanda
- Recomendações personalizadas por loja

# Decisões de Performance

## Índices: Aggressive mas Pragmático

**Índices Criados:**
```sql
CREATE INDEX idx_sales_created_at ON sales(created_at);
CREATE INDEX idx_sales_store_id ON sales(store_id);
CREATE INDEX idx_sales_channel_id ON sales(channel_id);
CREATE INDEX idx_sales_status ON sales(sale_status_desc);
```

**Por quê?**
-  **Filtros Comuns**: Essas colunas são filtradas 90% do tempo
-  **Read-Heavy**: Sistema de analytics, 99% reads
-  **Trade-off OK**: Writes mais lentos aceitável

**Por que não mais índices?**
-  Cada índice tem custo de storage e write
-  PostgreSQL query planner pode se confundir com muitos índices

## Connection Pooling: 10 base, 20 max

**Por quê?**
```python
pool_size=10,      # Conexões mantidas sempre
max_overflow=20    # Pode crescer até 30 total
```

-  **10 base**: Suficiente para requests concorrentes normais
-  **20 overflow**: Buffer para picos
-  **30 total**: PostgreSQL aguenta bem

**Como chegamos nesses números?**
- Testes de carga: 50 requests/segundo
- Queries médias: 200ms
- Concorrência: 10 queries simultâneas normalmente

## Cache TTL: 5 minutos

**Por quê?**
-  **Freshness**: Dados "recentes o suficiente"
-  **Hit Rate**: Alta, já que mesmos filtros são consultados
-  **Storage**: Redis comporta bem

**Testamos:**
- 1 minuto: Hit rate baixo, pouco ganho
- 10 minutos: Dados obsoletos demais
- 5 minutos: Sweet spot

# Segurança

## CORS: Whitelist de Origens

```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://app.nola.com",
]
```

**Por quê?**
-  **Seguro**: Só origens conhecidas
-  **Flexível**: Fácil adicionar produção

## SQL Injection: SQLAlchemy ORM

**Por quê?**
-  **Parametrized Queries**: Automático com ORM
-  **Validação**: Pydantic valida inputs antes de query

**Não usamos:**
-  String interpolation em SQL
-  exec() ou eval() com user input

## Autenticação: Não Implementada (MVP)

**Por quê?**
- Não é requisito do desafio
- MVP focado em funcionalidade core
- Fácil adicionar JWT depois

**Próximos Passos (Produção):**
1. JWT tokens
2. OAuth2 (Google, Facebook)
3. RBAC (admin, gerente, usuário)

# Trade-offs Conscientes

## O que priorizamos

1. **UX > Features**: Dashboard intuitivo > 50 tipos de gráficos
2. **Performance > Novidades**: Queries rápidas > Real-time WebSockets
3. **Pragmatismo > Perfeição**: MVP funcional > Arquitetura "perfeita"
4. **Documentação > Código**: README claro > Code comments

## O que deixamos para depois

1. **Autenticação**: Simples de adicionar, não é core
2. **Multi-tenancy**: Uma instância por brand ok por agora
3. **Testes E2E**: Unit tests bastam para MVP
4. **CI/CD**: Deploy manual ok para challenge
5. **Internacionalização**: Português-BR suficiente

# Lições Aprendidas

## O que funcionou bem

1. **FastAPI**: Muito produtivo, docs automáticas salvaram tempo
2. **TanStack Query**: Cache e loading states "de graça"
3. **Docker Compose**: Setup trivial, reproduzível
4. **Recharts**: Gráficos bonitos com pouco esforço

## O que faríamos diferente

1. **Testes desde o início**: Refactoring seria mais confiante
2. **Design system**: Componentes consistentes desde dia 1
3. **Telemetria**: Métricas de uso para guiar features

# Escalabilidade Futura

## 10x mais dados (5M vendas)

**O que fazer:**
1. Particionamento de tabelas por mês
2. Agregações pré-computadas (materialized views)
3. Read replicas para analytics
4. CDN para assets estáticos

**O que NÃO precisaria:**
- Reescrever aplicação
- Migrar de PostgreSQL
- Microserviços

## 100x mais usuários

**O que fazer:**
1. Load balancer (Nginx, HAProxy)
2. Horizontal scaling (mais instâncias backend)
3. Redis Cluster
4. CDN global (CloudFlare)

**Gargalos esperados:**
1. Database (resolver com read replicas)
2. Cache (resolver com Redis Cluster)
3. Backend (resolver com scale horizontal)

# Conclusão

Cada decisão foi feita pensando em:
1. **Resolver o problema de Maria** (UX, insights acionáveis)
2. **Entregar no prazo** (1 semana, stack conhecida)
3. **Performance aceitável** (< 500ms)
4. **Escalar se preciso** (mas não over-engineer agora)

**Resultado:**
-  Dashboard funcional em < 5 min setup
-  Queries < 500ms com cache
-  UX intuitiva para não-técnicos
-  Código limpo e manutenível
-  Preparado para escalar

---

**Tecnologia é meio, não fim. O fim é ajudar Maria a tomar melhores decisões. **
