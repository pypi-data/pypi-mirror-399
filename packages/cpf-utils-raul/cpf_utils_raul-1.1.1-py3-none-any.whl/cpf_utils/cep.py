def limpar_cep(cep: str) -> str:
    return ''.join(c for c in cep if c.isdigit())


def validar_cep(cep: str) -> bool:
    if not isinstance(cep, str):
        return False

    cep = limpar_cep(cep)

    return len(cep) == 8


def formatar_cep(cep: str) -> str:
    cep = limpar_cep(cep)
    if len(cep) != 8:
        raise ValueError("CEP deve conter 8 dígitos.")
    return f"{cep[:5]}-{cep[5:]}"
