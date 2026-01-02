def limpar_cpf(cpf: str) -> str:
    return ''.join(c for c in cpf if c.isdigit())


def validar_cpf(cpf: str) -> bool:
    if not isinstance(cpf, str):
        return False

    cpf = limpar_cpf(cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = 0 if soma % 11 < 2 else 11 - (soma % 11)

    if int(cpf[9]) != digito1:
        return False

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = 0 if soma % 11 < 2 else 11 - (soma % 11)

    if int(cpf[10]) != digito2:
        return False

    return True
