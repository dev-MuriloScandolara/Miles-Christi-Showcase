"""Construções das cidades (defesa do território).

Tudo editável aqui. Cada construção tem níveis; cada nível tem:
  nome, custo (moedas), min_tipo (tipo mínimo do território para construir esse nível),
  defesa    -> +% na defesa do território
  chance    -> chance (0 a 1) de um evento contra o atacante
  penal     -> -% na força do atacante quando o evento acontece
  perda_extra -> +% de perdas de tropas do atacante quando o evento acontece
  reducao   -> -% nas perdas de tropas do defensor
Os níveis ficam no território, em mapa.json:  "construcoes": {"muralha": 2, "fosso": 1}
"""

import random

# do pior ao melhor (mesmos tipos do ;evoluir)
ORDEM_TIPOS = [
    "aldeia_pequena", "aldeia", "aldeia_grande", "cidade",
    "cidade_grande", "castelo", "fortaleza", "capital_economica",
]

# ao conquistar a cidade, cada construção perde 1 nível
CONQUISTA_DANIFICA = True


def n(nome, custo, min_tipo, **efeitos):
    return {"nome": nome, "custo": custo, "min_tipo": min_tipo, **efeitos}


CONSTRUCOES = {
    "muralha": {
        "emoji": "🧱",
        "nome": "Muralha",
        "niveis": [
            n("Paliçada de Madeira", 2500, "aldeia", defesa=0.10),
            n("Muralha de Pedra", 7000, "cidade", defesa=0.22),
            n("Fortaleza Abaluartada", 18000, "castelo", defesa=0.38),
            n("Cidadela Inexpugnável", 45000, "fortaleza", defesa=0.55),
        ],
    },
    "torre": {
        "emoji": "🏹",
        "nome": "Torre de Arqueiros",
        "evento": "🏹 As torres descobriram sua posição e dispararam flechas contra o seu exército!",
        "niveis": [
            n("Torre de Vigia", 2000, "aldeia_grande", defesa=0.03, chance=0.10, penal=0.08),
            n("Torre de Arqueiros", 6000, "cidade", defesa=0.06, chance=0.18, penal=0.12),
            n("Torre de Balistas", 15000, "cidade_grande", defesa=0.10, chance=0.25, penal=0.18),
        ],
    },
    "fosso": {
        "emoji": "💧",
        "nome": "Fosso",
        "evento": "💧 Seu exército caiu no fosso ao redor da cidade!",
        "niveis": [
            n("Vala Seca", 2500, "cidade", defesa=0.04, chance=0.12, penal=0.10, perda_extra=0.20),
            n("Fosso com Água", 8000, "cidade_grande", defesa=0.08, chance=0.20, penal=0.15, perda_extra=0.35),
            n("Fosso com Estacas", 20000, "castelo", defesa=0.12, chance=0.30, penal=0.22, perda_extra=0.50),
        ],
    },
    "enfermaria": {
        "emoji": "⚕️",
        "nome": "Enfermaria",
        "niveis": [
            n("Enfermaria", 1500, "aldeia_grande", reducao=0.10),
            n("Hospital", 5000, "cidade", reducao=0.20),
            n("Hospital dos Cavaleiros", 12000, "castelo", reducao=0.30),
        ],
    },
}


def nivel(territorio, chave):
    return territorio.get("construcoes", {}).get(chave, 0)


def dados_do_nivel(territorio, chave):
    """Dados do nível atual da construção (ou None se não tiver)."""
    n_atual = nivel(territorio, chave)
    return CONSTRUCOES[chave]["niveis"][n_atual - 1] if n_atual > 0 else None


def tipo_suficiente(tipo_do_territorio, min_tipo):
    return ORDEM_TIPOS.index(tipo_do_territorio) >= ORDEM_TIPOS.index(min_tipo)


def efeitos_construcoes(territorio):
    """Resumo do que as construções fazem numa invasão (sorteia os eventos).

    Devolve {"bonus_defesa", "reducao_perdas", "perda_extra", "eventos": [{"texto", "penal_ataque"}]}
    """
    bonus = 0.0
    reducao = 0.0
    perda_extra = 0.0
    eventos = []

    for chave, info in CONSTRUCOES.items():
        d = dados_do_nivel(territorio, chave)

        if d is None:
            continue

        bonus += d.get("defesa", 0)
        reducao += d.get("reducao", 0)

        if d.get("chance") and random.random() < d["chance"]:
            eventos.append({"texto": info["evento"], "penal_ataque": d["penal"]})
            perda_extra += d.get("perda_extra", 0)

    return {"bonus_defesa": bonus, "reducao_perdas": reducao, "perda_extra": perda_extra, "eventos": eventos}


def danificar_construcoes(territorio):
    """Chamar quando o território é conquistado: cada construção perde 1 nível."""
    if not CONQUISTA_DANIFICA:
        return

    atuais = territorio.get("construcoes", {})

    for chave in list(atuais):
        atuais[chave] -= 1

        if atuais[chave] <= 0:
            del atuais[chave]
