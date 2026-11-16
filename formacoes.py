"""Formações de batalha.

Cada formação multiplica a força de cada CLASSE de tropa (infantaria, cavalaria, arqueiros).
Existe um ciclo de vantagem: Pinça > Chuva de Flechas > Muralha de Escudos > Pinça
(a formação que vence a do inimigo ganha +15% de força total).

Tudo editável: classes, multiplicadores, diagramas e o bônus de vantagem.
"""

from config import tropas
from i18n import tr

# classe de cada tropa (o que não estiver aqui conta como infantaria)
CLASSES = {
    "campones": "infantaria",
    "miliciano": "infantaria",
    "soldado": "infantaria",
    "sargento": "infantaria",
    "teutonico": "infantaria",
    "cavaleiro": "cavalaria",
    "hospitalario": "cavalaria",
    "templario": "cavalaria",
    "arqueiro": "arqueiros",
    "besteiro": "arqueiros",
}

BONUS_VANTAGEM = 1.15

FORMACOES = {
    "equilibrada": {
        "emoji": "⚖️",
        "nome": "Equilibrada",
        "mult": {"infantaria": 1.0, "cavalaria": 1.0, "arqueiros": 1.0},
        "vence": None,
        "diagrama": " C C   I I I I   C C\n     A A A A A",
    },
    "pinca": {
        "emoji": "🐎",
        "nome": "Pinça",
        "mult": {"infantaria": 0.9, "cavalaria": 1.35, "arqueiros": 0.9},
        "vence": "chuva",
        "diagrama": "C C C           C C C\n   I I I I I I I\n     A A A A",
    },
    "muralha": {
        "emoji": "🧱",
        "nome": "Muralha de Escudos",
        "mult": {"infantaria": 1.3, "cavalaria": 0.8, "arqueiros": 1.0},
        "vence": "pinca",
        "diagrama": " I I I I I I I I I\n I I I I I I I I I\n      A A A\n C             C",
    },
    "chuva": {
        "emoji": "🏹",
        "nome": "Chuva de Flechas",
        "mult": {"infantaria": 0.9, "cavalaria": 0.8, "arqueiros": 1.4},
        "vence": "muralha",
        "diagrama": "    I I I I I I\n A A A A A A A A A\n A A A A A A A A A\n C             C",
    },
}

NOMES_CLASSE = {"infantaria": "Infantaria", "cavalaria": "Cavalaria", "arqueiros": "Arqueiros"}


def classe_da_tropa(nome):
    return CLASSES.get(nome, "infantaria")


def forca_formada(exercito, formacao):
    """Força total do exército (ou da defesa) usando os multiplicadores da formação."""
    mult = FORMACOES.get(formacao, FORMACOES["equilibrada"])["mult"]
    total = 0

    for nome, qtd in exercito.items():
        if nome in tropas:
            total += tropas[nome]["ataque"] * qtd * mult[classe_da_tropa(nome)]

    return int(total)


def vantagens(f_atacante, f_defensor):
    """Devolve (multiplicador_do_atacante, multiplicador_do_defensor)."""
    if FORMACOES.get(f_atacante, {}).get("vence") == f_defensor:
        return BONUS_VANTAGEM, 1.0

    if FORMACOES.get(f_defensor, {}).get("vence") == f_atacante:
        return 1.0, BONUS_VANTAGEM

    return 1.0, 1.0


def texto_confronto(f_atacante, f_defensor):
    a = FORMACOES.get(f_atacante, FORMACOES["equilibrada"])
    d = FORMACOES.get(f_defensor, FORMACOES["equilibrada"])

    linha = f"{a['emoji']} {tr(a['nome'])}  ⚔️  {d['emoji']} {tr(d['nome'])}"
    m_atq, m_def = vantagens(f_atacante, f_defensor)

    if m_atq > 1:
        linha += "\n" + tr("✅ O atacante tinha vantagem de formação (+15%).")
    elif m_def > 1:
        linha += "\n" + tr("❌ O defensor tinha vantagem de formação (+15%).")

    return linha
