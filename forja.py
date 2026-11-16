"""Melhorias de equipamento (armas, armaduras e escudos) do sistema de guerra.

Tudo editável aqui: nomes, custos (moedas), tempo de pesquisa (segundos) e bônus por nível.
Os níveis ficam em economia.json, em cada jogador:
    "melhorias": {"arma": 2, "armadura": 0, "escudo": 1}
    "pesquisa":  {"item": "arma", "nivel": 3, "fim": 1767225600}   (ou ausente)
"""

import time

NIVEL_MAX = 5

# nome do nível, custo em moedas, tempo de pesquisa em segundos
ITENS = {
    "arma": {
        "emoji": "🗡️",
        "nome": "Armas",
        "efeito": "ataque",       # +% na força de ataque
        "por_nivel": 0.08,
        "niveis": [
            ("Espada de Ferro", 600, 600),
            ("Espada de Aço", 1800, 1800),
            ("Espada Bastarda", 5000, 3600),
            ("Montante", 12000, 10800),
            ("Espada Abençoada", 30000, 21600),
        ],
    },
    "armadura": {
        "emoji": "🛡️",
        "nome": "Armaduras",
        "efeito": "defesa",       # +% na força de defesa dos seus territórios
        "por_nivel": 0.08,
        "niveis": [
            ("Gibão Acolchoado", 800, 600),
            ("Cota de Malha", 2200, 1800),
            ("Brigantina", 6000, 3600),
            ("Armadura de Placas", 14000, 10800),
            ("Armadura Completa de Placas", 35000, 21600),
        ],
    },
    "escudo": {
        "emoji": "🔰",
        "nome": "Escudos",
        "efeito": "perdas",       # -% nas perdas de tropas (atacando e defendendo)
        "por_nivel": 0.08,
        "niveis": [
            ("Escudo de Madeira", 700, 600),
            ("Escudo Reforçado", 2000, 1800),
            ("Escudo de Aço", 5500, 3600),
            ("Pavês", 13000, 10800),
            ("Escudo de Cruzado", 32000, 21600),
        ],
    },
}


def agora():
    return int(time.time())


def pesquisa_pronta(conta):
    p = conta.get("pesquisa")
    return bool(p) and p["fim"] <= agora()


def nivel(conta, item):
    """Nível atual do item, já contando uma pesquisa que terminou mas ainda não foi gravada."""
    n = conta.get("melhorias", {}).get(item, 0)
    p = conta.get("pesquisa")

    if p and p["item"] == item and p["fim"] <= agora():
        n = max(n, p["nivel"])

    return n


def concluir_pesquisa(conta):
    """Grava no jogador a pesquisa que terminou. Devolve (item, nivel) ou None. Quem chama salva."""
    if not pesquisa_pronta(conta):
        return None

    p = conta.pop("pesquisa")
    conta.setdefault("melhorias", {})[p["item"]] = p["nivel"]
    return p["item"], p["nivel"]


def bonus_ataque(conta):
    return ITENS["arma"]["por_nivel"] * nivel(conta, "arma") if conta else 0


def bonus_defesa(conta):
    return ITENS["armadura"]["por_nivel"] * nivel(conta, "armadura") if conta else 0


def reducao_perdas(conta):
    return ITENS["escudo"]["por_nivel"] * nivel(conta, "escudo") if conta else 0


def formatar_tempo(segundos):
    if segundos >= 3600:
        h, resto = divmod(segundos, 3600)
        return f"{h} h" + (f" {resto // 60} min" if resto else "")

    return f"{segundos // 60} min"
