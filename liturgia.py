"""Cálculos do calendário litúrgico e busca de santos (sem depender do discord.py)."""

import unicodedata

from i18n import catalogo
from datetime import date, timedelta
from i18n import tr

DIAS_SEMANA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]

COR_EMOJI = {"verde": "🟢", "roxo": "🟣", "branco": "⚪", "vermelho": "🔴", "rosa": "🌸"}


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return " ".join(texto.replace("'", " ").replace("-", " ").split())


def pascoa(ano):
    """Domingo de Páscoa (algoritmo gregoriano anônimo)."""
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes, dia = divmod(h + l - 7 * m + 114, 31)
    return date(ano, mes, dia + 1)


def primeiro_domingo_advento(ano):
    natal = date(ano, 12, 25)
    quarto = natal - timedelta(days=(natal.isoweekday() % 7) or 7)
    return quarto - timedelta(days=21)


def batismo_do_senhor(ano):
    """Domingo depois de 6 de janeiro (aproximação: encerra o Tempo do Natal)."""
    d = date(ano, 1, 6)
    return d + timedelta(days=7 - d.isoweekday() % 7)


def datas_principais(ano):
    p = pascoa(ano)
    return {
        "Quarta-feira de Cinzas": p - timedelta(days=46),
        "Domingo de Ramos": p - timedelta(days=7),
        "Páscoa": p,
        "Pentecostes": p + timedelta(days=49),
        "Corpus Christi": p + timedelta(days=60),
        "1º Domingo do Advento": primeiro_domingo_advento(ano),
        "Natal": date(ano, 12, 25),
    }


def estacao(d):
    """Devolve (tempo, cor, observação)."""
    ano = d.year
    p = pascoa(ano)
    advento = primeiro_domingo_advento(ano)
    natal = date(ano, 12, 25)

    if d >= natal:
        return tr("Tempo do Natal"), "branco", ""

    if d >= advento:
        obs = ""
        cor = "roxo"

        if d == advento + timedelta(days=14):
            cor, obs = "rosa", tr("Domingo Gaudete (da alegria)")

        return tr("Advento"), cor, obs

    if d <= batismo_do_senhor(ano):
        return tr("Tempo do Natal"), "branco", ""

    cinzas = p - timedelta(days=46)
    quinta_santa = p - timedelta(days=3)

    if cinzas <= d < quinta_santa:
        if d == p - timedelta(days=7):
            return tr("Quaresma"), "vermelho", tr("Domingo de Ramos")

        if d == p - timedelta(days=21):
            return tr("Quaresma"), "rosa", tr("Domingo Laetare (da alegria)")

        return tr("Quaresma"), "roxo", ""

    if quinta_santa <= d < p:
        nomes = {0: ("branco", tr("Quinta-feira Santa")), 1: ("vermelho", tr("Sexta-feira Santa")), 2: ("branco", tr("Sábado Santo"))}
        cor, obs = nomes[(d - quinta_santa).days]
        return tr("Tríduo Pascal"), cor, obs

    if p <= d <= p + timedelta(days=49):
        if d == p + timedelta(days=49):
            return tr("Tempo Pascal"), "vermelho", tr("Pentecostes")

        return tr("Tempo Pascal"), "branco", ""

    return tr("Tempo Comum"), "verde", ""


def proximas_datas(hoje, quantas=4):
    todas = {}

    for ano in (hoje.year, hoje.year + 1):
        for nome, d in datas_principais(ano).items():
            todas[(d, nome)] = True

    futuras = sorted(k for k in todas if k[0] >= hoje)
    return futuras[:quantas]


def tirar_prefixo(nome):
    for pref in ("nossa senhora do ", "nossa senhora da ", "nossa senhora de ", "nossa senhora ",
                 "our lady of ", "our lady ", "saint ", "holy ", "blessed ", "santo ", "santa ", "sao ", "sto ", "sta ", "st "):
        if nome.startswith(pref):
            return nome[len(pref):]

    return nome


def buscar_santo(texto, santos):
    """Devolve (melhor_resultado_ou_None, lista_de_sugestoes)."""
    alvo = normalizar(texto)
    sem_pref = tirar_prefixo(alvo)

    if not alvo:
        return None, []

    pontuados = []

    for santo in santos:
        chaves = {normalizar(santo["nome"]), tirar_prefixo(normalizar(santo["nome"]))}
        chaves |= {normalizar(a) for a in santo["aliases"]}

        # nome em inglês (do catálogo de tradução), ex.: "Saint Jude Thaddeus"
        em = normalizar(catalogo("en").get(santo["nome"], ""))
        if em:
            chaves |= {em, tirar_prefixo(em)}

        if alvo in chaves or sem_pref in chaves:
            pontuados.append((100, santo))

    pontuados.sort(key=lambda x: -x[0])

    if not pontuados:
        return None, []

    return pontuados[0][1], [s["nome"] for _p, s in pontuados[1:4]]
