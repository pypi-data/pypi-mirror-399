def limpar_cnpj(cnpj: str) -> str:
    return ''.join(c for c in cnpj if c.isdigit())


def validar_cnpj(cnpj: str) -> bool:
    if not isinstance(cnpj, str):
        return False

    cnpj = limpar_cnpj(cnpj)

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    def calcular_digito(cnpj_parcial: str) -> int:
        pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(d) * p for d, p in zip(cnpj_parcial, pesos[-len(cnpj_parcial):]))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    digito1 = calcular_digito(cnpj[:12])
    if int(cnpj[12]) != digito1:
        return False

    digito2 = calcular_digito(cnpj[:13])
    if int(cnpj[13]) != digito2:
        return False

    return True


def formatar_cnpj(cnpj: str) -> str:
    cnpj = limpar_cnpj(cnpj)
    if len(cnpj) != 14:
        raise ValueError("CNPJ deve conter 14 dígitos.")
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
