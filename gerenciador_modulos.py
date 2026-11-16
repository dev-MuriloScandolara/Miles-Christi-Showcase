"""Liga/desliga módulos (cogs) por servidor.

Guarda em modulos.json, no formato {"id_do_servidor": ["cassino", "catolicismo"]}
(a lista contém só os módulos DESATIVADOS naquele servidor).

Para um cog novo aparecer no painel `;modulos`, adicione uma linha em MODULOS.
A chave é o nome da CLASSE do cog em minúsculas (class Cassino -> "cassino").
"""

import json

from discord.ext import commands

from config import BASE_DIR
from i18n import tr

ARQUIVO = BASE_DIR / "modulos.json"

# chave: (emoji, nome, descrição curta)
MODULOS = {
    "economia": ("💰", "Economia", "Daily, trabalhar, pagar, loja, ranking, roubar"),
    "banco": ("🏦", "Banco", "Depositar, sacar e juros"),
    "cassino": ("🎰", "Cassino", "Apostar, roleta, slots, blackjack"),
    "duelos": ("⚔️", "Duelos", "Duelo entre jogadores"),
    "territorios": ("🗺️", "Territórios", "Mapa, evoluir e coletar impostos"),
    "guerra": ("🪖", "Guerra", "Invadir, defender, tropas e alianças"),
    "diversao": ("🎲", "Diversão", "Dado, cara ou coroa, memes, escolher"),
    "interacao": ("🤝", "Interação", "Abraçar, beijar, tapa, ship etc."),
    "perfil": ("👤", "Perfil", "Perfil do jogador"),
    "missoes": ("🎯", "Missões", "Missões diárias"),
    "quiz": ("🧠", "Quiz", "Perguntas com prêmio em moedas"),
    "catolicismo": ("🇻🇦", "Catolicismo", "Santo do dia, santos, liturgia, terço, versículo"),
}

# Nunca podem ser desligados (senão ninguém conseguiria religar).
PROTEGIDOS = {"admin", "ajuda", "atualizacoes", "erros", "sistema", "modulos"}

# Cogs que seguem outro módulo: {cog: "módulo_pai"}
# Desativar o pai desativa todos os filhos juntos (e eles não aparecem no painel)
AGRUPAR = {
    "forja": "guerra",
    "formacao": "guerra",
    "construcoes": "guerra",
}

# Módulos que já começam DESLIGADOS em servidores novos (ex.: {"catolicismo"}).
PADRAO_DESATIVADO = set()

_cache = None


class ModuloDesativado(commands.CheckFailure):
    """Levantada quando alguém usa um comando de um módulo desligado no servidor."""

    def __init__(self, nome):
        self.nome = nome
        super().__init__(tr("Módulo {nome} desativado.", nome=nome))


def _carregar():
    global _cache

    if _cache is None:
        try:
            with ARQUIVO.open("r", encoding="utf-8-sig") as f:
                _cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            _cache = {}

    return _cache


def _salvar():
    with ARQUIVO.open("w", encoding="utf-8") as f:
        json.dump(_cache, f, indent=4, ensure_ascii=False)


def desativados(guild_id):
    dados = _carregar()
    gid = str(guild_id)

    if gid not in dados:
        return set(PADRAO_DESATIVADO)

    return set(dados[gid])


def modulo_ativo(guild_id, chave):
    return chave not in desativados(guild_id)


def definir(guild_id, chave, ativo):
    dados = _carregar()
    atuais = desativados(guild_id)

    if ativo:
        atuais.discard(chave)
    else:
        atuais.add(chave)

    dados[str(guild_id)] = sorted(atuais)
    _salvar()


def achar_chave(texto):
    """Aceita 'cassino', 'Cassino', 'territórios'... e devolve a chave, ou None."""
    texto = texto.strip().lower()
    sem_acento = texto.translate(str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc"))

    if sem_acento in AGRUPAR:
        return AGRUPAR[sem_acento]

    from i18n import catalogo

    tira = str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc")
    en = catalogo("en")

    for chave, (_, nome, _desc) in MODULOS.items():
        candidatos = {chave, nome.lower().translate(tira), en.get(nome, "").lower().translate(tira)}

        if sem_acento in candidatos:
            return chave

    return None
