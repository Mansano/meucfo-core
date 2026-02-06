# MeuCFO.ai - Dashboard de Análise Financeira

Sistema completo de análise financeira para PMEs com cálculo de precificação, análise competitiva e dashboards interativos.

## 🚀 Funcionalidades

### 1. Cálculo de Formação de Preço
- Precificação para varejo e serviços
- Considera todos os impostos brasileiros (ICMS, IPI, PIS/COFINS, ISS)
- Diferenciação por regime tributário
- Cálculo de ICMS interestadual

### 2. Análise Competitiva
- Coleta estruturada de dados do negócio
- Integração com webhooks para análise por LLM
- Projeções financeiras automatizadas
- Análise de rentabilidade por categoria

### 3. Dashboard Interativo
- Métricas financeiras em tempo real
- Gráficos com Chart.js
- Interface glassmorphism moderna
- Responsivo para mobile

### 4. Administração
- Aprovação de usuários
- Monitoramento do sistema
- Gestão de acessos

## 🏗️ Arquitetura
Frontend (Jinja2) → FastAPI → Cloudflare D1 (SQLite)
↓
Redis (Rate Limiting)
↓
Webhooks (N8n/LLM)

## 📦 Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Conta Cloudflare com D1 ativado
- Redis

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd meucfo-ai
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Execute localmente
```bash
# Desenvolvimento
uvicorn app.main:app --reload --port 8000

# Ou
python app/main.py
```

### 5. Ou execute com Docker
```bash
docker-compose up --build
```
