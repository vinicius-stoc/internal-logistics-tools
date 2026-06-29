# Manual do Usuario - Dashboard de Logistica

Este manual explica como usar o dashboard de logistica para acompanhar a operacao, identificar atrasos, priorizar problemas e apoiar decisoes do dia a dia.

O documento foi escrito para usuarios da logistica. Nao e necessario conhecer programacao, banco de dados ou detalhes tecnicos do sistema.

## Objetivo do dashboard

O dashboard mostra indicadores gerenciais da operacao logistica com base nos dados importados da planilha oficial.

Ele ajuda a responder perguntas como:

- Quantas entregas existem no periodo analisado?
- Quantas ja foram entregues?
- Quanto valor financeiro esta envolvido?
- Onde estao os maiores atrasos?
- Quais rotas, motoristas, cidades, regioes ou frequencias precisam de atencao?
- Existem status incoerentes entre carga e entrega?
- Qual ponto deve ser investigado primeiro?

O dashboard deve ser usado como ferramenta de analise e priorizacao. Ele nao substitui a investigacao operacional, mas mostra onde a equipe deve olhar primeiro.

## Como acessar

1. Acesse o sistema pelo navegador.
2. Faca login com seu usuario e senha.
3. Entre no menu `Dashboard`.
4. Aguarde os indicadores carregarem.

Se aparecer a mensagem de que nao ha dados, pode significar que ainda nao houve importacao valida ou que os filtros aplicados nao retornaram registros.

## Como usar os filtros

Os filtros ficam na parte superior da tela.

Voce pode filtrar por:

- data inicial;
- data final;
- motorista;
- pauta;
- unidade de negocio;
- regiao;
- frequencia;
- status de entrega;
- status da carga.

Depois de escolher os filtros, clique em `Filtrar`.

Para voltar ao painel completo, clique em `Limpar filtros`.

Regra importante: todos os cards, graficos, tabelas e exportacao Excel respeitam os filtros aplicados.

## Exportacao Excel

O botao `Exportar Excel` gera uma planilha com os dados do recorte atual.

Use a exportacao quando precisar:

- enviar dados para conferencia;
- montar uma analise complementar;
- compartilhar registros especificos com outra area;
- verificar notas fiscais, motoristas, rotas ou status com mais detalhe.

A exportacao segue os mesmos filtros aplicados no dashboard.

## Botao de ajuda

Os cards, graficos e tabelas possuem um botao `?`.

Use esse botao quando quiser entender:

- como o indicador e calculado;
- qual insight ele traz;
- qual formula ou regra esta por tras da analise.

Ao passar o mouse, aparece um resumo curto.

Ao clicar, aparece uma explicacao completa.

## Regras principais de prazo

O dashboard usa duas regras de SLA.

### SLA operacional

Meta: ate 48 horas uteis.

Mede o tempo entre a emissao da nota fiscal e a entrega ao cliente.

Esse indicador mostra se o processo completo da operacao esta dentro do prazo esperado.

### SLA transportadora

Meta: ate 24 horas uteis.

Mede o tempo entre o carregamento e a entrega ao cliente.

Esse indicador mostra se a etapa da transportadora esta dentro do prazo esperado.

## Como interpretar os cards

Os cards ficam no topo do dashboard e mostram uma visao rapida da situacao.

### Registros

Mostra a quantidade total de entregas ou notas fiscais no recorte filtrado.

Use para entender o tamanho da base que esta sendo analisada.

### Entregues

Mostra quantos registros estao com entrega concluida.

Use para acompanhar o volume ja finalizado.

### Pendentes

Mostra quantos registros ainda nao aparecem como entregues.

Use para acompanhar o que ainda pode precisar de acao.

### Valor total NF

Mostra a soma do valor das notas fiscais do recorte filtrado.

Use para entender o impacto financeiro total da operacao analisada.

### Valor NF em atraso

Mostra quanto valor financeiro esta associado a registros com atraso.

Use para avaliar o impacto financeiro dos problemas de prazo.

### SLA operacional

Mostra o percentual de registros dentro do prazo operacional de 48 horas uteis.

Quanto maior, melhor.

Quedas nesse indicador indicam gargalo no processo completo, desde a emissao da nota ate a entrega.

### SLA transportadora

Mostra o percentual de registros dentro do prazo da transportadora de 24 horas uteis.

Quanto maior, melhor.

Quedas nesse indicador indicam problema mais concentrado na etapa de transporte.

### P90 operacional

Mostra um tempo de referencia para os maiores prazos operacionais.

Leitura simples: 90% dos registros ficaram ate esse tempo.

Use para entender se existem entregas demorando muito acima da media.

### P90 transportadora

Mostra um tempo de referencia para os maiores prazos da transportadora.

Leitura simples: 90% dos registros ficaram ate esse tempo.

Use para identificar se a etapa de transporte tem casos muito demorados.

### Lead time operacional medio

Mostra o tempo medio entre a emissao da nota fiscal e a entrega.

Use para acompanhar o desempenho geral do processo.

### Lead time transportadora medio

Mostra o tempo medio entre o carregamento e a entrega.

Use para acompanhar o desempenho da transportadora.

### Atraso operacional

Mostra o percentual de registros acima de 48 horas uteis no ciclo operacional.

Quanto menor, melhor.

### Atraso transportadora

Mostra o percentual de registros acima de 24 horas uteis na etapa da transportadora.

Quanto menor, melhor.

### Ponto critico

Mostra a rota com maior prioridade de investigacao dentro do recorte filtrado.

Esse card usa o score de criticidade.

Use para saber onde comecar a analise.

### Divergencias de status

Mostra registros em que a entrega aparece como concluida, mas o status da carga nao acompanha essa informacao.

Use para identificar possiveis falhas de atualizacao ou inconsistencias sistemicas.

### Divergencia de status %

Mostra o percentual de divergencias de status dentro do total filtrado.

Quanto maior o percentual, maior a necessidade de limpeza ou conferencia da base.

## Como interpretar os graficos

Os graficos ajudam a visualizar padroes que nem sempre aparecem nos cards.

## Pressao Comercial

A secao `Pressao Comercial` foi criada para separar a demanda gerada pelo faturamento da execucao feita pela Logistica.

Essa analise ajuda a mostrar quando o Comercial concentra pedidos em poucos dias e qual impacto isso gera na operacao.

Use essa secao para responder:

- o volume foi distribuido ao longo do mes ou concentrado no fechamento?
- qual foi o maior dia de faturamento?
- quantos registros foram emitidos nos ultimos 3 dias uteis?
- a Logistica conseguiu entregar no mesmo ritmo do faturamento?
- os pedidos faturados nos dias de pico atrasaram mais?

### Maior dia de faturamento

Mostra o dia com mais notas emitidas no periodo filtrado.

Use para apontar o pico de demanda criado pelo faturamento.

### Faturados nos ultimos 3 dias uteis

Mostra quantos registros foram emitidos nos ultimos 3 dias uteis do mes.

Use para demonstrar concentracao de fechamento.

### Concentracao no fim do mes

Mostra qual percentual do volume total foi emitido nos ultimos 3 dias uteis.

Quanto maior esse percentual, maior a pressao criada no fechamento.

### Media diaria normal

Mostra a media de registros emitidos fora dos ultimos 3 dias uteis.

Use essa media como referencia para comparar com o pico de fechamento.

### Faturados x entregues por dia

Compara duas curvas:

- faturados: demanda criada pelo Comercial;
- entregues: resposta da Logistica.

Esse grafico mostra se a demanda foi criada em volume maior do que a capacidade normal de entrega.

### Atrasos por data de faturamento

Mostra se os pedidos emitidos em dias de pico geraram mais atraso.

Use para defender a Logistica quando o atraso estiver ligado a concentracao de faturamento, e nao apenas a execucao da entrega.

### Resumo de pressao comercial

Compara:

- periodo normal;
- ultimos 3 dias uteis.

A tabela mostra volume, participacao, media diaria, valor financeiro, atrasos, lead time e severidade.

Essa e a tabela mais importante para apresentacao executiva, porque mostra o impacto do fechamento comercial em numeros.

### Registros por dia

Mostra o volume de registros por data.

Use para identificar dias com maior movimento.

Perguntas que esse grafico ajuda a responder:

- Houve pico de volume em algum dia?
- O volume esta concentrado em poucos dias?
- Um aumento de atraso pode estar ligado a aumento de volume?

### Eficiencia por motorista

Compara motoristas considerando volume e tempo medio de entrega.

Cada ponto representa um motorista.

Use para identificar:

- motoristas com alto volume e bom desempenho;
- motoristas com alto volume e lead time elevado;
- motoristas com poucos registros, mas desempenho fora do padrao.

Esse grafico nao deve ser usado sozinho para julgamento individual. Ele aponta onde investigar.

### Rotas criticas

Mostra as rotas com maior score de criticidade.

Use para priorizar rotas que combinam volume, atrasos, valor financeiro e gravidade dos atrasos.

### Gargalo por dia da semana

Mostra o percentual de atraso por dia da semana.

Use para identificar se os problemas acontecem mais em determinados dias.

Exemplos de decisao:

- revisar planejamento de carregamento em dias criticos;
- reforcar equipe em dias com maior risco;
- investigar atraso recorrente em inicio ou fim de semana operacional.

### Pareto de atrasos por rota

Mostra quais rotas concentram mais atrasos.

A ideia do Pareto e identificar se poucos grupos concentram grande parte do problema.

Use para priorizar as rotas que mais contribuem para o total de atrasos.

### Distribuicao de lead time

Mostra em quais faixas de horas os registros estao concentrados.

Use para entender se a maioria das entregas esta dentro de um prazo aceitavel ou se existe muita dispersao.

### Lead time por regiao

Compara regioes por tempo medio e percentual de atraso.

Use para identificar regioes com maior dificuldade operacional.

Exemplos de decisao:

- revisar cobertura por regiao;
- entender se uma regiao especifica precisa de ajuste de rota;
- priorizar conversa com transportadora sobre regioes mais criticas.

### Lead time por frequencia

Compara frequencias de atendimento por tempo medio e percentual de atraso.

Use para entender se entregas diarias, semanais, quinzenais ou outras frequencias apresentam comportamento diferente.

Exemplos de decisao:

- revisar frequencias com maior atraso;
- avaliar se a agenda atual esta adequada;
- identificar se entregas menos frequentes acumulam maior criticidade.

## Como interpretar as tabelas

As tabelas mostram detalhes para investigacao.

Use as tabelas depois de olhar os cards e graficos.

### Motoristas fora da curva

Lista motoristas com maior criticidade no recorte filtrado.

Use para investigar desempenho, volume, atrasos e severidade.

Nao use a tabela para conclusao isolada sem verificar contexto operacional.

### Rotas criticas

Lista rotas com maior prioridade de analise.

Use para decidir quais rotas devem ser revisadas primeiro.

### Cidades criticas

Lista cidades com maior criticidade.

Use para identificar destinos que concentram atrasos ou maior tempo de entrega.

### Regioes criticas

Lista regioes com maior criticidade.

Use para identificar problemas regionais e apoiar decisoes de planejamento.

### Frequencias criticas

Lista frequencias com maior criticidade.

Use para avaliar se a frequencia atual de atendimento pode estar contribuindo para atrasos.

### Notas fiscais fora da curva

Lista casos individuais com maiores tempos.

Use para investigacao pontual.

Essa tabela ajuda a encontrar entregas especificas que merecem conferencia.

### Divergencias de status

Lista registros em que a entrega consta como concluida, mas o status da carga esta incoerente.

Use para:

- cobrar atualizacao de status;
- limpar base;
- evitar interpretacao errada do processo;
- identificar falha recorrente no fluxo de atualizacao.

## Score de criticidade

O score de criticidade e uma pontuacao de prioridade.

Ele nao e percentual de atraso.

Ele responde a pergunta:

```text
Onde a gestao deve olhar primeiro?
```

O score combina quatro fatores:

- volume de registros;
- quantidade de atrasos;
- valor financeiro;
- gravidade dos atrasos em horas.

Quanto maior o score, maior a prioridade de investigacao.

### Exemplo simples

Rota A:

- muitos atrasos pequenos.

Rota B:

- menos atrasos, mas atrasos muito maiores.

Mesmo com menos ocorrencias, a Rota B pode ser mais critica se a gravidade em horas for maior.

Por isso o score e mais util que olhar somente a quantidade de atrasos.

### Como usar o score

Use score alto para:

- definir prioridade de analise;
- escolher qual rota, motorista, cidade, regiao ou frequencia investigar primeiro;
- direcionar conversa com equipe ou transportadora;
- comparar problemas dentro do mesmo filtro.

Nao use o score para:

- dizer que um item atrasou exatamente aquele percentual;
- comparar periodos muito diferentes sem contexto;
- concluir culpa de motorista, rota ou transportadora sem investigacao.

## Regras praticas de decisao

### Quando investigar uma rota

Investigue quando:

- a rota aparece no ponto critico;
- a rota tem score alto;
- a rota concentra muitos atrasos;
- a rota tem alta severidade de atraso;
- a rota aparece no Pareto de atrasos.

### Quando investigar um motorista

Investigue quando:

- o motorista aparece como fora da curva;
- tem lead time medio alto;
- tem muitos atrasos;
- tem alto volume e desempenho abaixo do esperado.

Sempre considere contexto: volume, tipo de rota, regiao, distancia e dificuldade operacional.

### Quando investigar uma regiao

Investigue quando:

- a regiao aparece com score alto;
- a regiao tem atraso operacional ou transportadora elevado;
- o lead time medio esta acima das demais regioes.

### Quando investigar uma frequencia

Investigue quando:

- a frequencia aparece com score alto;
- a frequencia tem muitos atrasos;
- a frequencia tem maior severidade em horas.

### Quando cobrar atualizacao de status

Investigue ou cobre atualizacao quando:

- o card de divergencia de status estiver alto;
- a tabela de divergencias tiver muitos registros;
- a entrega aparece concluida, mas a carga nao acompanha essa situacao.

## Cuidados na interpretacao

### Nao olhar um indicador sozinho

Um indicador isolado pode enganar.

Exemplo:

- uma rota pode ter muitos atrasos porque tem muito volume;
- outra pode ter poucos atrasos, mas muito graves;
- uma cidade pode parecer critica por causa de poucos casos extremos.

Sempre combine cards, graficos e tabelas.

### Comparar sempre dentro do mesmo filtro

O dashboard muda conforme os filtros aplicados.

Se voce filtrar apenas uma regiao, o score passa a mostrar a prioridade dentro daquela regiao.

Se voce filtrar apenas um periodo, o score passa a mostrar a prioridade daquele periodo.

### Verificar dados antes de concluir

Antes de tomar uma decisao definitiva, confira:

- se o periodo filtrado esta correto;
- se o status esta atualizado;
- se existem divergencias de status;
- se a planilha mais recente ja foi importada;
- se o caso exige analise operacional fora do sistema.

## Fluxo recomendado de analise

1. Escolha o periodo.
2. Veja o volume total de registros.
3. Abra a secao `Pressao Comercial`.
4. Confira o maior dia de faturamento e a concentracao nos ultimos 3 dias uteis.
5. Compare faturados x entregues por dia.
6. Verifique se os atrasos aumentam nos dias de maior faturamento.
7. Confira SLA operacional e SLA transportadora.
8. Veja o valor financeiro em atraso.
9. Verifique o ponto critico.
10. Analise os graficos de rotas, regioes e frequencias.
11. Abra as tabelas para investigar detalhes.
12. Confira divergencias de status.
13. Exporte para Excel se precisar compartilhar ou aprofundar.
14. Defina a acao operacional.

## Exemplos de decisoes apoiadas pelo dashboard

### Exemplo 1: SLA transportadora caiu

Possiveis acoes:

- verificar grafico por rota;
- verificar grafico por regiao;
- olhar tabela de notas fora da curva;
- cobrar transportadora sobre rotas ou regioes especificas.

### Exemplo 2: divergencia de status aumentou

Possiveis acoes:

- abrir tabela de divergencias;
- identificar notas e rotas afetadas;
- cobrar atualizacao de status;
- verificar se existe falha recorrente no processo.

### Exemplo 3: uma regiao aparece como critica

Possiveis acoes:

- analisar rotas dentro da regiao;
- verificar frequencia de atendimento;
- comparar lead time operacional e transportadora;
- revisar planejamento logistico da regiao.

### Exemplo 4: uma frequencia aparece como critica

Possiveis acoes:

- entender se a frequencia atende a demanda real;
- verificar atrasos acumulados;
- avaliar ajuste de agenda;
- revisar capacidade de atendimento.

### Exemplo 5: faturamento concentrado no fim do mes

Possiveis acoes:

- apresentar a concentracao nos ultimos 3 dias uteis;
- comparar faturados x entregues por dia;
- mostrar se os pedidos emitidos no pico atrasaram mais;
- propor limite de horario ou data para faturamento com entrega dentro do mes;
- alinhar Comercial e Logistica com uma capacidade diaria realista.

## Glossario

### SLA

Prazo esperado para uma etapa do processo.

No dashboard:

- operacional: ate 48 horas uteis;
- transportadora: ate 24 horas uteis.

### Lead time

Tempo entre dois eventos.

No dashboard:

- operacional: da emissao da NF ate a entrega;
- transportadora: do carregamento ate a entrega.

### Horas uteis

Horas consideradas dentro de dias uteis.

Finais de semana nao entram no calculo.

### P90

Indicador que mostra ate qual tempo ficaram 90% dos registros.

Serve para analisar casos mais demorados sem depender apenas da media.

### Atraso operacional

Registro que passou de 48 horas uteis entre emissao da NF e entrega.

### Atraso transportadora

Registro que passou de 24 horas uteis entre carregamento e entrega.

### Severidade do atraso

Quantidade de horas acima do prazo esperado.

Exemplo:

- prazo esperado: 48h;
- entrega levou 60h;
- severidade: 12h.

### Score de criticidade

Pontuacao que indica prioridade de analise.

Quanto maior, maior a necessidade de investigar.

### Divergencia de status

Caso em que a entrega aparece como concluida, mas o status da carga nao esta coerente.

## Regra final

O dashboard mostra onde olhar primeiro.

A decisao final deve considerar o contexto operacional, a realidade da rota, a capacidade da equipe, a transportadora e a qualidade da informacao registrada.
