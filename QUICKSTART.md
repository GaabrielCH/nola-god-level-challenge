# 🚀 Quick Start Guide - 5 Minutos para Começar

## Pré-requisitos

Certifique-se de ter instalado:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows)
- [Git](https://git-scm.com/downloads)
- PowerShell 5.1+ (vem com Windows)

## Passo a Passo

### 1. Clone o Repositório

```powershell
git clone <seu-repositorio>
cd nola-god-level-desafio
```

### 2. Inicie o Banco de Dados

```powershell
# Inicia só o PostgreSQL
docker compose up -d postgres

# Aguarda 30 segundos para o banco ficar pronto
Start-Sleep -Seconds 30
```

### 3. Gere os Dados

```powershell
# Gera 500k vendas (leva 5-15 minutos)
python generate_data.py --db-url postgresql://challenge:challenge_2024@localhost:5432/challenge_db

# OU com Docker:
docker compose build data-generator
docker compose run --rm data-generator
```

**Aguarde** enquanto os dados são gerados. Você verá:
```
Setting up base data...
✓ Base data: 3 sub-brands, 6 channels
Generating 50 stores...
✓ 50 stores created
...
✓ Total: 500000 sales generated!
```

### 4. Inicie a Aplicação Completa

```powershell
# Sobe backend, frontend e Redis
docker compose up -d

# Verifica se está rodando
docker compose ps
```

Você deve ver:
```
NAME                      STATUS
nola-analytics-backend    Up
nola-analytics-frontend   Up
nola-analytics-db         Up
nola-analytics-redis      Up
```

### 5. Acesse a Aplicação

Abra seu navegador em:

- **Frontend**: http://localhost:3000
- **API Backend**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs

## Primeiros Passos na Aplicação

### 1. Dashboard Principal

1. Acesse http://localhost:3000
2. Veja as métricas principais:
   - Faturamento Total
   - Total de Vendas
   - Ticket Médio
3. Ajuste o período de datas
4. Selecione lojas específicas

### 2. Análises Customizadas

1. Clique em "Análises" no menu
2. Escolha uma métrica (ex: Faturamento)
3. Agrupe por dimensão (ex: Canal)
4. Veja o gráfico e tabela atualizarem

### 3. Comparação de Lojas

1. Clique em "Comparar Lojas"
2. Ajuste o período
3. Veja ranking de lojas por faturamento

### 4. Insights Automáticos

1. Clique em "Dashboard Customizado"
2. Veja insights gerados automaticamente
3. Identifique tendências e anomalias

## Troubleshooting

### Erro: "port 5432 already in use"

Você tem PostgreSQL rodando localmente. Pare ele:

```powershell
# Lista serviços
Get-Service -Name *postgre*

# Para serviço
Stop-Service -Name postgresql-x64-XX
```

OU altere a porta no `docker-compose.yml`:

```yaml
postgres:
  ports:
    - "5433:5432"  # Usa porta 5433 no host
```

### Erro: "Cannot connect to API"

1. Verifique se backend está rodando:
   ```powershell
   docker compose logs backend
   ```

2. Teste API diretamente:
   ```powershell
   curl http://localhost:8000/api/health
   ```

3. Reinicie:
   ```powershell
   docker compose restart backend
   ```

### Erro: "Data generation failed"

1. Verifique conexão com banco:
   ```powershell
   docker compose exec postgres psql -U challenge challenge_db -c "SELECT 1"
   ```

2. Limpe e tente novamente:
   ```powershell
   docker compose down -v
   docker compose up -d postgres
   Start-Sleep -Seconds 30
   python generate_data.py
   ```

### Frontend não carrega

1. Verifique logs:
   ```powershell
   docker compose logs frontend
   ```

2. Acesse diretamente em outra porta:
   ```powershell
   cd frontend
   npm install
   npm run dev
   # Acesse http://localhost:5173
   ```

## Comandos Úteis

```powershell
# Ver logs
docker compose logs -f backend
docker compose logs -f frontend

# Parar tudo
docker compose down

# Parar e remover volumes (limpa dados)
docker compose down -v

# Rebuild containers
docker compose build --no-cache

# Entrar em container
docker compose exec backend bash
docker compose exec postgres psql -U challenge challenge_db

# Ver uso de recursos
docker stats
```

## Desenvolvimento Local (Sem Docker)

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure .env
copy .env.example .env
# Edite .env com suas configurações

# Rode
uvicorn main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Acesse http://localhost:5173

## Próximos Passos

1. ✅ Explore o Dashboard Principal
2. ✅ Crie análises personalizadas
3. ✅ Compare lojas
4. ✅ Veja insights automáticos
5. ✅ Teste diferentes períodos e filtros

## Ajuda

- 📚 README completo: [README.md](./README.md)
- 🏗️ Arquitetura: [ARCHITECTURE.md](./ARCHITECTURE.md)
- 💬 Discord: https://discord.gg/pRwmm64Vej
- 📧 Email: gsilvestre@arcca.io

---

**Dúvidas? Entre em contato!** 🚀
