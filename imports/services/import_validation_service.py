class ImportValidationError(Exception):
    pass


EXPECTED_SHEET_NAME = "COM 001"

EXPECTED_HEADERS_A_TO_AH = [
    "Data Mapa",
    "Nr Mapa",
    "Proprietario",
    "Rota",
    "Ptos Entrega",
    "Peso",
    "Volume",
    "Valor",
    "Placa",
    "Cod Mot",
    "Nome Motorista",
    "Conf",
    "Nome Conferente",
    "Situacao",
    "Data",
    "Nota Fiscal",
    "Serie",
    "Emissao",
    "Bordero",
    "CodCli",
    "Razao Social",
    "Cidade",
    "Valor2",
    "Placa",
    "SitNF",
    "SitCarga",
    "Data3",
    "SitEntrega",
    "Data4",
    "Hora Entrega",
    "Exportado",
    "Observacao",
    "Vendedor",
    "Equipe",
]


def validate_sheet_name(workbook):
    if EXPECTED_SHEET_NAME not in workbook.sheetnames:
        raise ImportValidationError(
            f"Aba obrigatória não encontrada: {EXPECTED_SHEET_NAME}"
        )


def validate_headers(header_values):
    current_headers = [
        str(value).strip() if value is not None and str(value).strip() else ""
        for value in header_values[: len(EXPECTED_HEADERS_A_TO_AH)]
    ]

    if current_headers != EXPECTED_HEADERS_A_TO_AH:
        differences = []
        for position, expected in enumerate(EXPECTED_HEADERS_A_TO_AH, start=1):
            found = current_headers[position - 1] if position <= len(current_headers) else ""
            if found != expected:
                differences.append(
                    {
                        "position": position,
                        "expected": expected,
                        "found": found,
                    }
                )

        raise ImportValidationError(
            "Cabeçalho da planilha diferente do esperado.",
            differences,
        )
