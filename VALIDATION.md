# Validação do Projeto

Este documento contém os passos para validar que o projeto está funcionando corretamente.

## Pré-requisitos

- Docker Desktop rodando
- Porta 3000, 5432, 6379, 8000 disponíveis
- Python 3.10+ instalado
- PowerShell

## Passo a Passo de Validação

### 1. Verificar Docker

```powershell
# Verificar se Docker está rodando
docker --version
docker compose --version

# Deve mostrar versões sem erro
```

### 2. Limpar Estado Anterior (Opcional)

```powershell
# Se estiver rodando anteriormente
docker compose down -v

# Remove containers, volumes e redes
```

### 3. Iniciar PostgreSQL

```powershell
# Subir apenas PostgreSQL
docker compose up -d postgres

# Aguardar estar pronto
Start-Sleep -Seconds 30

# Verificar se está rodando
docker compose ps postgres
# Status deve ser "Up" ou "Healthy"
```

### 4. Verificar Conexão com Banco

```powershell
# Testar conexão
docker compose exec postgres pg_isready -U challenge

# Deve retornar: "accepting connections"
```

### 5. Gerar Dados

```powershell
# Instalar dependências (se ainda não instalou)
pip install psycopg2-binary faker tqdm

# Executar gerador
python generate_data.py

# Deve mostrar progresso e completar com sucesso
# Aguardar 5-10 minutos
```

### 6. Validar Dados Gerados

```powershell
# Conectar ao banco e verificar
docker compose exec postgres psql -U challenge -d challenge_db -c "SELECT COUNT(*) FROM sales;"

# Deve mostrar um número próximo de 300000
```

### 7. Iniciar Todos os Serviços

```powershell
# Subir tudo
docker compose up -d

# Aguardar
Start-Sleep -Seconds 20

# Verificar status de todos
docker compose ps
```

### 8. Validar Status dos Containers

Todos os containers devem estar com status "Up":

```powershell
docker compose ps

# Deve mostrar:
# nola-analytics-backend    Up
# nola-analytics-frontend   Up
# nola-analytics-db         Up (healthy)
# nola-analytics-redis      Up
```

### 9. Validar Backend API

```powershell
# Health check
curl http://localhost:8000/api/health

# Deve retornar: {"status":"ok","database":"connected"}

# Testar endpoint de lojas
curl http://localhost:8000/api/stores

# Deve retornar JSON com lista de lojas
```

### 10. Validar Frontend

```powershell
# Abrir navegador
Start-Process "http://localhost:3000"
```

**Checklist Visual no Frontend:**

- [ ] Página carrega sem erros
- [ ] Sidebar esquerda aparece com 4 itens de menu
- [ ] Dashboard mostra 4 cards de métricas
- [ ] Gráficos aparecem com dados
- [ ] Filtros de data funcionam
- [ ] Ao clicar em "Análises", a página muda e o item fica destacado
- [ ] Ao clicar em "Comparar Lojas", mostra lista de lojas
- [ ] Ao clicar em "Dashboard Customizado", mostra insights

### 11. Testar Navegação

1. **Dashboard** (/)
   - [ ] 4 cards com métricas aparecem
   - [ ] Gráfico de linha temporal mostra dados
   - [ ] Gráfico de canais mostra barras
   - [ ] Top 10 produtos aparece

2. **Análises** (/analytics)
   - [ ] Query builder aparece
   - [ ] Ao selecionar métrica e agrupar, gráficos atualizam
   - [ ] Tabela de dados aparece embaixo

3. **Comparar Lojas** (/stores)
   - [ ] Gráfico de barras horizontal com faturamento
   - [ ] Gráfico de vendas
   - [ ] Cards de lojas aparecem

4. **Dashboard Customizado** (/custom)
   - [ ] Lista de insights aparece ou mensagem de "nenhum insight"

### 12. Testar Filtros

No Dashboard:

1. Mudar data inicial para 30 dias atrás
2. Mudar data final para hoje
3. Dados devem atualizar

### 13. Verificar Logs (Se houver problemas)

```powershell
# Logs do backend
docker compose logs backend --tail=50

# Logs do frontend
docker compose logs frontend --tail=30

# Logs do postgres
docker compose logs postgres --tail=20

# Logs do redis
docker compose logs redis --tail=10
```

### 14. Validar Performance

```powershell
# Testar tempo de resposta da API
Measure-Command { curl http://localhost:8000/api/stores }

# Deve completar em menos de 1 segundo
```

### 15. Validar Cache Redis

```powershell
# Conectar ao Redis
docker compose exec redis redis-cli

# Dentro do Redis CLI:
# > KEYS *
# Deve mostrar algumas chaves de cache

# > INFO stats
# Mostra estatísticas

# > exit
```

## Problemas Comuns e Soluções

### Porta em uso

```powershell
# Descobrir o que está usando a porta
netstat -ano | findstr :8000

# Matar processo (substitua <PID>)
taskkill /PID <PID> /F

# Ou mudar a porta no docker-compose.yml
```

### Container não inicia

```powershell
# Ver logs detalhados
docker compose logs <nome-container>

# Rebuild
docker compose build --no-cache <nome-container>
docker compose up -d
```

### Dados não aparecem no frontend

```powershell
# Verificar se backend está rodando
curl http://localhost:8000/api/health

# Limpar cache do navegador
# Ctrl + Shift + R (hard refresh)

# Verificar console do navegador (F12)
# Não deve ter erros em vermelho
```

### Backend retorna erro 500

```powershell
# Ver logs
docker compose logs backend --tail=100

# Geralmente é problema com conexão ao banco
# Verificar se postgres está rodando:
docker compose ps postgres
```

## Checklist Final de Validação

- [ ] Docker Desktop rodando
- [ ] PostgreSQL iniciado e aceitando conexões
- [ ] Dados gerados com sucesso (300k+ vendas)
- [ ] Backend retorna 200 em /api/health
- [ ] Frontend carrega em http://localhost:3000
- [ ] Navegação entre páginas funciona
- [ ] Item ativo na sidebar muda de cor ao navegar
- [ ] Dados aparecem em todas as páginas
- [ ] Filtros de data funcionam
- [ ] Gráficos renderizam corretamente
- [ ] Não há erros no console do navegador
- [ ] API responde em menos de 500ms

## Comandos Úteis

```powershell
# Parar tudo
docker compose down

# Reiniciar um serviço
docker compose restart backend

# Ver uso de recursos
docker stats

# Limpar tudo e começar do zero
docker compose down -v
docker volume prune -f
docker compose up -d --build
```

## Sucesso!

Se todos os itens acima passaram, o projeto está 100% funcional!

Próximos passos:
1. Gravar vídeo de demonstração (5-10 minutos)
2. Submeter para o desafio: gsilvestre@arcca.io
3. Incluir link do repositório e link do vídeo

Repositório: https://github.com/GaabrielCH/nola-god-level-challenge
