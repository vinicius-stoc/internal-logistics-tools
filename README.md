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
- `dashboard`: consulta agregada, filtros, contratos para graficos e exportacao Excel.

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

O dashboard nao le Excel, nao conecta SFTP e nao recalcula dados da planilha original. Os filtros sao aplicados sobre dados persistidos no banco: `invoice_issue_date`, `driver_name`, `route`, `business_unit`, `region`, `frequency`, `delivery_status` e `cargo_status`.

### Regras de SLA

O lead time e calculado em horas uteis.

- SLA operacional: alvo de 48h uteis, medido da emissao da NF ate a entrega.
- SLA transportadora: alvo de 24h uteis, medido do carregamento ate a entrega.

Formulas:

- `operational_sla_rate = ((total_records - operational_late_records) / total_records) * 100`
- `carrier_sla_rate = ((total_records - carrier_late_records) / total_records) * 100`
- `operational_late_percentage = (operational_late_records / total_records) * 100`
- `carrier_late_percentage = (carrier_late_records / total_records) * 100`

### Cards

- `total_records`: total de registros filtrados.
- `delivered_records`: registros em que `delivery_status` contem `entreg`.
- `total_invoice_value`: soma de `invoice_value`.
- `delayed_invoice_value`: soma de `invoice_value` dos registros com atraso operacional ou transportadora.
- `operational_sla_rate`: entregas dentro do alvo operacional de 48h uteis.
- `carrier_sla_rate`: entregas dentro do alvo da transportadora de 24h uteis.
- `operational_lead_time_p90_hours`: percentil 90 do lead time operacional.
- `carrier_lead_time_p90_hours`: percentil 90 do lead time da transportadora.
- `average_operational_lead_time_hours`: media de `operational_lead_time_hours`.
- `average_carrier_lead_time_hours`: media de `carrier_lead_time_hours`.
- `operational_late_percentage`: percentual de registros acima de 48h uteis.
- `carrier_late_percentage`: percentual de registros acima de 24h uteis.
- `top_critical_route`: rota com maior score de criticidade v2.
- `pending_records`: `total_records - delivered_records`.
- `status_inconsistency_count`: entregas concluidas com status de carga incoerente.
- `status_inconsistency_percentage`: percentual de divergencias de status sobre o total filtrado.
- `peak_billing_day`: dia com maior volume de faturamento/emissao.
- `last_3_business_days_records`: registros emitidos nos ultimos 3 dias uteis do mes.
- `last_3_business_days_percentage`: concentracao percentual do volume nos ultimos 3 dias uteis.
- `normal_daily_average_records`: media diaria de emissao fora dos ultimos 3 dias uteis.

### Graficos

- `records_by_day`: volume por data de emissao da NF.
- `driver_efficiency_scatter`: volume x lead time medio por motorista, com raio proporcional ao valor NF.
- `critical_routes_ranking`: ranking de rotas por score de criticidade v2.
- `weekday_bottleneck`: percentual de atraso por dia da semana.
- `delay_pareto`: rotas que concentram atrasos e percentual acumulado.
- `lead_time_distribution`: distribuicao de lead time por faixas de horas.
- `region_lead_time_comparison`: lead time e atraso por regiao, quando a coluna opcional existe.
- `frequency_lead_time_comparison`: lead time e atraso por frequencia, quando a coluna opcional existe.
- `billing_vs_delivery_by_day`: compara registros faturados por data de emissao com entregas por data de entrega.
- `delay_by_issue_day`: cruza volume faturado por data de emissao com atraso operacional e transportadora.

### Tabelas

- `driver_outliers`: motoristas fora da curva por volume, atrasos, valor, severidade e score.
- `critical_routes`: rotas criticas.
- `critical_cities`: cidades criticas.
- `critical_regions`: regioes criticas, quando `region` estiver preenchido.
- `critical_frequencies`: frequencias criticas, quando `frequency` estiver preenchido.
- `invoice_outliers`: notas fiscais com maiores lead times.
- `status_inconsistencies`: registros entregues com status de carga nao entregue ou vazio.
- `commercial_pressure_summary`: compara periodo normal contra ultimos 3 dias uteis do mes para evidenciar pressao de fechamento comercial.

### Pressao comercial

A secao de pressao comercial separa a demanda criada pelo faturamento da resposta operacional da logistica.

Contratos principais:

- `billing_vs_delivery_by_day`: `Faturados` usa data de emissao da NF; `Entregues` usa data de entrega ao cliente.
- `delay_by_issue_day`: agrupa por data de emissao da NF e calcula atraso operacional e transportadora dos registros emitidos em cada dia.
- `commercial_pressure_summary`: compara `Periodo normal` contra `Ultimos 3 dias uteis`.

Essa analise existe para demonstrar concentracao de faturamento no fechamento do mes e seu impacto em lead time, atrasos, valor financeiro e severidade.

### Score de criticidade v2

O score nao e percentual de atraso. Ele e uma pontuacao relativa de prioridade dentro dos dados filtrados.

Para cada registro:

- `operational_delay_hours = max(operational_lead_time_hours - 48, 0)`
- `carrier_delay_hours = max(carrier_lead_time_hours - 24, 0)`
- `total_delay_severity_hours = operational_delay_hours + carrier_delay_hours`

Para cada grupo, o dashboard calcula participacao em volume, atrasos, valor financeiro e severidade de atraso:

```text
criticality_score =
((records_share * 0.20)
+ (delayed_share * 0.30)
+ (value_share * 0.20)
+ (severity_share * 0.30)) * 100
```

Quanto maior o score, maior a prioridade gerencial.

### Divergencia de status

Um registro e divergente quando:

- `delivery_status` contem `entreg`, sem diferenciar maiusculas;
- e `cargo_status` nao contem `entreg` ou esta vazio.

Essa analise aponta falha de atualizacao operacional ou inconsistencia sistemica entre carga e entrega.

### Region e frequency

`region` e `frequency` sao campos opcionais da planilha fonte.

- A validacao obrigatoria continua limitada a `A:AH`.
- Arquivos antigos sem essas colunas continuam funcionando.
- Quando as colunas opcionais existem, os valores sao persistidos em `LeadTimeRecord`.
- Quando ausentes, os campos sao salvos como string vazia.
- Graficos e tabelas de regiao/frequencia ficam vazios quando nao ha dados preenchidos.

Cabecalhos aceitos:

- Regiao: `Regiao`, `Regiao` com acento, `REGIAO`.
- Frequencia: `Frequencia`, `Frequencia` com acento, `FREQ`, `FREQUENCIA`.

### Explicacoes no dashboard

Cards, graficos, tabelas e score possuem botao `?`.

- Hover: mostra resumo curto.
- Clique: abre explicacao completa com calculo, insight e formula.
- SweetAlert e usado quando disponivel; caso contrario, o fallback e `alert`.

## Exportacao Excel

A exportacao do dashboard usa os mesmos filtros aplicados na tela e consome somente dados persistidos em `LeadTimeRecord`.

Rota:

```text
/dashboard/export/excel/
```

Regras:

- exige login;
- exige troca de senha concluida;
- exige permissao `accounts.export_dashboard`;
- nao le a planilha original;
- nao conecta SFTP;
- gera `.xlsx` em memoria com `openpyxl`.

## Demonstracao local

Fluxo recomendado para apresentacao:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py setup_rbac
python manage.py createsuperuser
python manage.py import_lead_time_records --file-path "data/Acompanhamento Lead Time - Tabaco mes de Maio 2026.xlsx"
python manage.py runserver
```

No navegador:

1. Acesse `http://127.0.0.1:8000/`.
2. Faca login com usuario autorizado.
3. Acesse o dashboard.
4. Aplique filtros de periodo, motorista, pauta, unidade ou status.
5. Clique em `Exportar Excel`.
6. Abra o arquivo `.xlsx` gerado e confira a aba `Dados filtrados`.

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
- exportacao Excel da visao filtrada do dashboard.

Ainda nao implementa:

- conexao SFTP real;
- scheduler em producao;
- Celery ou Redis;
- API REST completa.
