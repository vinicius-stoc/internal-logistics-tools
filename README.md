# Plataforma Interna de Logística

Monolito Django para acompanhamento gerencial de dados logísticos importados de planilha Excel e, futuramente, de origem SFTP.

## Arquitetura

O arquivo `arquitetura_projeto.txt` é a fonte da verdade arquitetural do projeto.

Diretrizes principais:

- monolito Django;
- Django Templates, Bootstrap, JavaScript simples, Chart.js e SweetAlert;
- autenticação com Django Auth, Groups e Permissions;
- regra de negócio em services;
- rotinas de importação via management commands;
- dashboard consumindo dados persistidos no banco;
- sem Excel ou SFTP dentro de views.

## Apps oficiais

- `core`: estrutura visual base, templates globais e helpers compartilhados.
- `accounts`: autenticação e futuros fluxos administrativos de usuários.
- `imports`: futura importação local/SFTP, validação e persistência.
- `dashboard`: futura consulta agregada, filtros e contratos para gráficos.

## Setup local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse:

```text
http://127.0.0.1:8000/
```

## Banco de dados

Sem `DATABASE_URL`, o projeto usa SQLite local para protótipo.

Para PostgreSQL, configure `DATABASE_URL` no `.env`.

## Variáveis de ambiente

Use `.env.example` como referência. Credenciais reais não devem ser versionadas.

## Escopo atual

Esta base prepara o projeto para execução local e evolução futura. Ainda não implementa:

- leitura real da planilha Excel;
- conexão SFTP;
- pipeline de importação;
- models de negócio;
- gráficos finais;
- exportação Excel;
- Celery ou Redis;
- API REST completa.
