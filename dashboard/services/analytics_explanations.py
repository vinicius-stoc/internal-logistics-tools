def get_analytics_explanations():
    return {
        "cards": {
            "total_records": _item(
                "Registros",
                "Total de registros filtrados no banco.",
                "Conta as linhas de LeadTimeRecord que passam pelos filtros aplicados.",
                "Mostra o tamanho da base analisada no recorte atual.",
                "Registros = count(LeadTimeRecord filtrados)",
            ),
            "delivered_records": _item(
                "Entregues",
                "Quantidade de registros com status de entrega concluido.",
                "Conta registros em que delivery_status contem 'entreg', sem diferenciar maiusculas.",
                "Indica o volume ja concluido dentro do recorte filtrado.",
                "Entregues = count(delivery_status contem 'entreg')",
            ),
            "total_invoice_value": _item(
                "Valor total NF",
                "Soma do valor financeiro das notas filtradas.",
                "Soma invoice_value dos registros filtrados.",
                "Ajuda a dimensionar o impacto financeiro do recorte analisado.",
                "Valor total NF = soma(invoice_value)",
            ),
            "delayed_invoice_value": _item(
                "Valor NF em atraso",
                "Soma do valor financeiro de registros com atraso operacional ou transportadora.",
                "Soma invoice_value quando is_operational_late ou is_carrier_late e verdadeiro.",
                "Mostra quanto valor financeiro esta associado a atrasos.",
                "Valor NF em atraso = soma(invoice_value dos registros atrasados)",
            ),
            "operational_sla_rate": _item(
                "SLA operacional",
                "Percentual de entregas dentro do limite operacional de 48h uteis.",
                "Conta todos os registros filtrados e subtrai os registros com atraso operacional.",
                "Mostra se a operacao interna esta cumprindo o prazo esperado.",
                "SLA operacional = ((Registros totais - Atrasos operacionais) / Registros totais) x 100",
            ),
            "carrier_sla_rate": _item(
                "SLA transportadora",
                "Percentual de entregas dentro do limite da transportadora de 24h uteis.",
                "Conta todos os registros filtrados e subtrai os registros com atraso de transportadora.",
                "Mostra se a etapa de transporte esta cumprindo o prazo esperado.",
                "SLA transportadora = ((Registros totais - Atrasos transportadora) / Registros totais) x 100",
            ),
            "operational_lead_time_p90_hours": _item(
                "P90 operacional",
                "Tempo abaixo do qual estao 90% dos lead times operacionais.",
                "Ordena os lead times operacionais e seleciona o percentil 90.",
                "Mostra a cauda do processo sem depender apenas da media.",
                "P90 = valor na posicao ceil(0,90 x total)",
            ),
            "carrier_lead_time_p90_hours": _item(
                "P90 transportadora",
                "Tempo abaixo do qual estao 90% dos lead times da transportadora.",
                "Ordena os lead times da transportadora e seleciona o percentil 90.",
                "Mostra a cauda da etapa de transporte.",
                "P90 = valor na posicao ceil(0,90 x total)",
            ),
            "average_operational_lead_time_hours": _item(
                "Lead time operacional medio",
                "Media de horas uteis da emissao da NF ate a entrega.",
                "Calcula a media de operational_lead_time_hours dos registros filtrados.",
                "Indica o tempo medio do fluxo completo da operacao.",
                "Media operacional = soma(LT operacional) / total com LT operacional",
            ),
            "average_carrier_lead_time_hours": _item(
                "Lead time transportadora medio",
                "Media de horas uteis do carregamento ate a entrega.",
                "Calcula a media de carrier_lead_time_hours dos registros filtrados.",
                "Indica o tempo medio sob responsabilidade da transportadora.",
                "Media transportadora = soma(LT transportadora) / total com LT transportadora",
            ),
            "operational_late_percentage": _item(
                "Atraso operacional",
                "Percentual de registros acima de 48h uteis no ciclo operacional.",
                "Divide registros com is_operational_late pelo total filtrado.",
                "Mostra a fatia do recorte que rompeu o alvo operacional.",
                "Atraso operacional = (Atrasos operacionais / Registros totais) x 100",
            ),
            "carrier_late_percentage": _item(
                "Atraso transportadora",
                "Percentual de registros acima de 24h uteis na etapa da transportadora.",
                "Divide registros com is_carrier_late pelo total filtrado.",
                "Mostra a fatia do recorte que rompeu o alvo da transportadora.",
                "Atraso transportadora = (Atrasos transportadora / Registros totais) x 100",
            ),
            "top_critical_route": _item(
                "Ponto critico",
                "Rota com maior score de criticidade no recorte filtrado.",
                "Ordena rotas pelo score de criticidade v2 e seleciona a primeira.",
                "Aponta onde a acao gerencial deve comecar.",
                "Ponto critico = max(criticality_score_v2 por rota)",
            ),
            "pending_records": _item(
                "Pendentes",
                "Registros filtrados que ainda nao aparecem como entregues.",
                "Subtrai entregues do total de registros filtrados.",
                "Ajuda a medir backlog operacional no recorte atual.",
                "Pendentes = Registros totais - Entregues",
            ),
            "status_inconsistency_count": _item(
                "Divergencias de status",
                "Registros entregues com status de carga incoerente.",
                "Conta registros em que delivery_status contem 'entreg' e cargo_status nao contem 'entreg' ou esta vazio.",
                "Aponta falha de atualizacao operacional ou inconsistencia sistemica.",
                "Divergencias = count(delivery_status contem 'entreg' e cargo_status nao contem 'entreg')",
            ),
            "status_inconsistency_percentage": _item(
                "Divergencia de status %",
                "Percentual de registros filtrados com divergencia de status.",
                "Divide as divergencias de status pelo total filtrado.",
                "Mede a qualidade da atualizacao de status no recorte analisado.",
                "Divergencia % = (Divergencias / Registros totais) x 100",
            ),
        },
        "charts": {
            "records_by_day": _item(
                "Registros por dia",
                "Volume diario de registros por data de emissao da NF.",
                "Agrupa registros por invoice_issue_date e conta linhas.",
                "Mostra dias com maior volume operacional.",
                "Registros por dia = count(registros) por invoice_issue_date",
            ),
            "driver_efficiency_scatter": _item(
                "Eficiencia por motorista: volume x lead time",
                "Cruza quantidade de entregas com lead time medio por motorista.",
                "Cada ponto representa um motorista; X e volume, Y e LT operacional medio, raio e valor NF.",
                "Identifica motoristas com alto volume e baixo ou alto lead time.",
                "X = registros; Y = media LT operacional; Raio = escala por valor NF",
            ),
            "critical_routes_ranking": _item(
                "Rotas criticas",
                "Ranking de rotas pelo score de criticidade v2.",
                "Ordena rotas pela pontuacao relativa de prioridade.",
                "Ajuda a priorizar rotas com maior impacto operacional e financeiro.",
                "Score = ((Volume% x 0,20) + (Atrasos% x 0,30) + (Valor NF% x 0,20) + (Severidade h% x 0,30)) x 100",
            ),
            "weekday_bottleneck": _item(
                "Gargalo por dia da semana",
                "Percentual de atraso por dia da semana.",
                "Agrupa registros pelo dia da semana da emissao e calcula atraso operacional e transportadora.",
                "Mostra padroes semanais de gargalo.",
                "Atraso dia % = (Atrasos no dia / Registros no dia) x 100",
            ),
            "delay_pareto": _item(
                "Pareto de atrasos por rota",
                "Rotas com maior quantidade de atrasos e percentual acumulado.",
                "Ordena rotas por atrasos e calcula o acumulado sobre o total atrasado.",
                "Ajuda a identificar poucas rotas que concentram muitos atrasos.",
                "Acumulado % = (Atrasos acumulados / Total de atrasos) x 100",
            ),
            "lead_time_distribution": _item(
                "Distribuicao de lead time",
                "Distribuicao dos lead times em faixas de horas.",
                "Classifica lead times operacionais e da transportadora em buckets.",
                "Mostra concentracao ou dispersao dos tempos.",
                "Bucket = contagem de registros por faixa de horas",
            ),
            "region_lead_time_comparison": _item(
                "Lead time por regiao",
                "Compara lead time e atraso por regiao quando a planilha possui esse campo.",
                "Agrupa registros por region e calcula medias, atrasos e score.",
                "Mostra regioes com maior pressao operacional.",
                "Metricas por regiao = agregacoes dos registros com mesma region",
            ),
            "frequency_lead_time_comparison": _item(
                "Lead time por frequencia",
                "Compara lead time e atraso por frequencia quando a planilha possui esse campo.",
                "Agrupa registros por frequency e calcula medias, atrasos e score.",
                "Mostra frequencias de atendimento com maior criticidade.",
                "Metricas por frequencia = agregacoes dos registros com mesma frequency",
            ),
        },
        "tables": {
            "driver_outliers": _table_item("Motoristas fora da curva", "driver_name"),
            "critical_routes": _table_item("Rotas criticas", "route"),
            "critical_cities": _table_item("Cidades criticas", "city"),
            "critical_regions": _table_item("Regioes criticas", "region"),
            "critical_frequencies": _table_item("Frequencias criticas", "frequency"),
            "invoice_outliers": _item(
                "Notas fiscais fora da curva",
                "Notas com maiores lead times no recorte filtrado.",
                "Ordena registros por LT operacional e LT transportadora em ordem decrescente.",
                "Ajuda a investigar casos individuais de atraso elevado.",
                "Ranking = order by LT operacional desc, LT transportadora desc",
            ),
            "status_inconsistencies": _item(
                "Divergencias de status",
                "Registros entregues com status de carga incoerente.",
                "Lista os registros divergentes ordenando por entrega, emissao e NF.",
                "Ajuda a limpar base, cobrar atualizacao e evitar leitura falsa do processo.",
                "Filtro = delivery_status contem 'entreg' e cargo_status nao contem 'entreg'",
            ),
        },
        "scores": {
            "criticality_score_v2": _item(
                "Score de criticidade",
                "Pontuacao relativa usada para priorizar rotas, motoristas, cidades, regioes ou frequencias.",
                "Combina participacao em volume, atrasos, valor financeiro e severidade total de atraso em horas.",
                "Ajuda a priorizar onde agir primeiro sem olhar apenas quantidade de atrasos.",
                "Score = ((Volume% x 0,20) + (Atrasos% x 0,30) + (Valor NF% x 0,20) + (Severidade h% x 0,30)) x 100",
            )
        },
    }


def _table_item(title, group_key):
    return _item(
        title,
        "Ranking investigativo por criticidade.",
        f"Agrupa registros por {group_key}, calcula volume, atrasos, valor NF, severidade e score.",
        "Ajuda a localizar prioridades gerenciais no recorte filtrado.",
        "Score = ((Volume% x 0,20) + (Atrasos% x 0,30) + (Valor NF% x 0,20) + (Severidade h% x 0,30)) x 100",
    )


def _item(title, summary, calculation, insight, formula):
    return {
        "title": title,
        "summary": summary,
        "calculation": calculation,
        "insight": insight,
        "formula": formula,
    }
