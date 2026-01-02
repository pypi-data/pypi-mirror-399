def limpar_rg(rg: str) -> str:
    return ''.join(c for c in rg if c.isdigit())


def validar_rg(rg: str) -> bool:
    if not isinstance(rg, str):
        return False

    rg = limpar_rg(rg)

    if not (5 <= len(rg) <= 14):
        return False

    if rg == rg[0] * len(rg):
        return False

    return True
