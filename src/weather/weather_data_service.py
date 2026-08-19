# ==========================================================
# Serviço de dados climáticos
# ==========================================================

PRECIPITATION_MM = 20.0


def get_precipitation_mm() -> float:
    """
    Retorna a precipitação acumulada em milímetros.

    Atualmente utiliza um valor fixo para permitir o
    desenvolvimento e teste da aplicação.

    Futuramente esta função será responsável por obter
    o valor através da integração com uma API climática.
    """

    return PRECIPITATION_MM