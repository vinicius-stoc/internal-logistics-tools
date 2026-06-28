# Plataforma Interna de Logistica

Monolito Django para acompanhamento gerencial de dados logisticos importados de planilha Excel e, futuramente, de origem SFTP.

## Arquitetura

O arquivo `arquitetura_projeto.txt` e a fonte da verdade arquitetural do projeto.

Diretrizes principais:

- monolito Django;
- Django Templates, Bootstrap, JavaScript simples, Chart.js e SweetAlert;
- autenticacao com Django Auth, Groups e Permissions;
- regra de negocio em services;
- rotinas de importacao via management commands;
- dashboard consumindo dados persistidos no banco;
- sem Excel ou SFTP dentro de views.

## Apps oficiais

- `core`: estrutura visual base, templates globais e helpers compartilhados.
- `accounts`: autenticacao e futuros fluxos administrativos de usuarios.
- `imports`: importacao local/SFTP futura, validacao e persistencia.
- `dashboard`: futura consulta agregada, filtros e contratos para graficos.

## Setup local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py setup_rbac
python manage.py createsuperuser
python manage.py runserver
```

Acesse:

```text
http://127.0.0.1:8000/
```

## Banco de dados

Sem `DATABASE_URL`, o projeto usa SQLite local para prototipo.

Para PostgreSQL, configure `DATABASE_URL` no `.env`.

## Variaveis de ambiente

Use `.env.example` como referencia. Credenciais reais nao devem ser versionadas.

Variaveis principais para importacao local:

- `EXCEL_SOURCE_MODE=local`
- `LOCAL_EXCEL_PATH=data/Acompanhamento Lead Time - Tabaco mes de Maio 2026.xlsx`

## Importacao local de lead time

Nesta etapa, a origem funcional e somente arquivo Excel local. A conexao SFTP continua preparada apenas de forma conceitual.

Regras atuais:

- aba importada: `COM 001`;
- intervalo importado: colunas `A:AH`;
- segunda coluna `Placa` descartada;
- colunas `AI` em diante descartadas;
- `business_unit` derivado do nome do arquivo, por exemplo `TABACO`;
- dashboard deve consumir apenas dados persistidos no banco.

Execute:

```powershell
python manage.py migrate
python manage.py import_lead_time_records
```

Para testar outro arquivo local:

```powershell
python manage.py import_lead_time_records --file-path "data/Acompanhamento Lead Time - Tabaco mes de Maio 2026.xlsx"
```

Arquivos Excel locais em `data/` nao devem ser versionados.

## RBAC e usuarios internos

O projeto usa Django Auth, Groups e Permissions.

Execute apos as migrations:

```powershell
python manage.py setup_rbac
```

O command e idempotente e cria/atualiza:

- `LogisticaViewer`: acesso ao dashboard e futura exportacao;
- `LogisticaAdmin`: acesso ao dashboard, gestao de usuarios, historico de importacao, reset interno e futura exportacao.

Usuarios criados pela tela interna recebem senha temporaria e ficam marcados para troca obrigatoria no primeiro acesso.

Rotas principais:

- `/accounts/login/`
- `/accounts/logout/`
- `/accounts/users/`
- `/accounts/password/force-change/`

Superusers continuam com acesso total pelo mecanismo nativo do Django, mas nao devem ser usados como usuarios operacionais diarios.

## Testes

Execute:

```powershell
python manage.py test accounts
python manage.py test dashboard
python manage.py test imports
python manage.py check
```

## Dashboard analytics

O dashboard consome somente dados persistidos em `LeadTimeRecord` e metadados de `ImportBatch`.

Contratos implementados nesta etapa:

- filtros: `date_start`, `date_end`, `driver_name`, `route`, `business_unit`, `delivery_status`, `cargo_status`;
- cards: totais, entregas, pendencias, valor de notas, medias de lead time e percentuais de atraso;
- graficos: registros por dia, motorista, pauta, status de entrega e lead time medio por motorista;
- tabelas: resumo por motorista e por pauta.

O filtro de periodo usa `invoice_issue_date`, por ser campo obrigatorio e indexado. O label visual de pauta usa o campo tecnico `route`.

## Escopo atual

Esta base prepara o projeto para execucao local e evolucao futura. Ja implementa:

- modelagem inicial de `ImportBatch` e `LeadTimeRecord`;
- leitura local da planilha Excel;
- validacao estrutural da aba `COM 001`;
- persistencia dos dados tratados;
- idempotencia por hash do arquivo;
- command local de importacao.
- contratos iniciais de analytics do dashboard.
- RBAC simples com Django Groups e Permissions.
- administracao interna basica de usuarios.
- troca obrigatoria de senha no primeiro acesso.

Ainda nao implementa:

- conexao SFTP real;
- acabamento visual final dos graficos;
- exportacao Excel;
- Celery ou Redis;
- API REST completa.
