"""Histórico de atualizações do bot.

Fonte única usada pelo ;log e pelos anúncios automáticos no canal de atualizações.

Para lançar uma versão nova: adicione uma entrada NO TOPO de ATUALIZACOES.
Ao ligar, o bot compara a versão da primeira entrada com a última que anunciou em
cada servidor e, se forem diferentes, posta sozinho a novidade no canal.
"""

from i18n import idioma_atual, tr

ATUALIZACOES = [
{
        "versao": "Beta 2.6",
        "titulo": "v beta 2.6 - Siege Update",
        "texto": """-Novo ;forja e ;forjar: pesquise armas, armaduras e escudos que fortalecem seu exército;
-Novas formações de batalha (;formacoes): Pinça, Muralha de Escudos e Chuva de Flechas, com ciclo de vantagem;
-Novas tropas: arqueiro e besteiro;
-Construções nas cidades (;construcoes e ;construir): muralha, torre de arqueiros, fosso e enfermaria.""",
        "nota": "Provavelmente uma das últimas atualizações da versão Beta. Logo entraremos no lançamento oficial.",
        "en": {
            "titulo": "v beta 2.6 - Siege Update",
            "texto": """-New ;gear and ;forge: research weapons, armor and shields that strengthen your army;
-New battle formations (;formations): Pincer, Shield Wall and Arrow Rain, with an advantage cycle;
-New troops: archer and crossbowman;
-City buildings (;buildings and ;build): wall, archer tower, moat and infirmary.""",
            "nota": "Likely one of the final updates for the Beta version. We will soon move to the official launch.",
        },
    },
    {
        "versao": "Beta 2.4",
        "titulo": "v beta 2.4 - Language Update",
        "texto": """-O bot agora funciona em Português e em English! Administradores escolhem com ;idioma;
-Todos os comandos também têm nome em inglês (;balance, ;help, /balance...);
-Correção: ;perfilbot agora aceita laico/Laico;
-Correção: os avisos automáticos do catolicismo não param mais por causa de um erro.""",
        "nota": None,
    },
    {
        "versao": "Beta 2.3",
        "titulo": "v beta 2.3 - Faith & Modules Update",
        "texto": """-Novo ;modulos: administradores ligam/desligam cada parte do bot (cassino, guerra, diversão...) no servidor;
-Novo módulo de catolicismo: ;santododia, ;santo, ;versiculo, ;liturgia, ;calendarioliturgico, ;terco e ;oracao;
-Avisos automáticos opcionais: ;lembreterco e ;santodiaauto.""",
        "nota": None,
    },
    {
        "versao": "Beta 2.2",
        "titulo": "v beta 2.2 - Slash Update",
        "texto": """-Todos os comandos agora funcionam também com / (barra), além do ;
-;escolher aceita opções separadas por vírgula (ex: ;escolher pizza grande, sushi);
-;meme não trava mais o bot enquanto busca o meme.""",
        "nota": None,
    },
    {
        "versao": "Beta 2.1",
        "titulo": "v beta 2.1 - Economy Update",
        "texto": """-Novo ;banco: guarde moedas com ;depositar e ;sacar e ganhe 1% de juros ao dia;
-Novo ;roubar: tente roubar a carteira de alguém (o banco protege seu dinheiro);
-Novos jogos: ;slots (caça-níquel) e ;blackjack, com botões;
-;duelo agora usa botões de Aceitar e Recusar;
-;trabalhar com vários trabalhos diferentes;
-Novas ;missoes diárias com recompensa e bônus;
-Novo ;quiz com moedas de prêmio;
-Novo ;perfil com saldo, exército, territórios e posição no ranking;
-Alguns comandos também funcionam como / (barra);
-Mensagens de erro mais claras e backup automático dos dados.""",
        "nota": None,
    },
    {
        "versao": "Beta 2.0",
        "titulo": "v beta 2.0 - Defense Updade",
        "texto": """-Sistema de defesa adicionado ao sistema de guerra;
-sistema de alianças adicionado;
-Sistema de doar tropas adicionado;
-;mapa melhorado;
Dê ;ajuda e vá para a parte de guerra para ver tudo o que foi adicionado.""",
        "nota": "Depois de mil bugs, eu finalmente consegui! 😭",
    },
    {
        "versao": "Beta 1.6",
        "titulo": "v beta 1.6 - War Updade",
        "texto": """-Sistema de guerra/invasão feito, uma atualização tão grande que não é possível mostrar aqui
Utilize ;ajudainvasao para ver todos os comandos adicionados""",
        "nota": "Meu Deus... que coisa aterrorizante de programar...",
    },
    {
        "versao": "Beta 1.0",
        "titulo": "v beta 1.0 - UI Update",
        "texto": """-;interface do ;ajuda melhorada;
-Comandos do ;duelo melhorados;
-Rework do ;ship;
-Rework nas UIs de comandos de economia;
-Rework nas UIs de comandos de diversão;
-Rework nas UIs de comandos de aposta;
-rework nas UIs de comandos de interação;""",
        "nota": "Apenas alguns comandos não receberam novas UIs por conta de já estarem com uma UI que combina com eles.",
    },
    {
        "versao": "Alpha 0.46.1",
        "titulo": "v alpha 0.46.1",
        "texto": """-;roleta rebalanceado (estava muito nerfado);
-Correção de bugs.""",
        "nota": None,
    },
]


def formatar_entrada(entrada):
    en = entrada.get("en") if idioma_atual() == "en" else None

    if en:
        titulo, texto, nota = en["titulo"], en["texto"], en.get("nota")
    else:
        titulo = tr(entrada["titulo"])
        texto = tr(entrada["texto"])
        nota = tr(entrada["nota"]) if entrada.get("nota") else None

    partes = ["## " + titulo, texto.strip()]

    if nota:
        partes += [tr("### Nota do dev:"), nota.strip()]

    return "\n".join(partes)


def formatar_entradas(entradas):
    return "\n\n".join(formatar_entrada(e) for e in entradas)


def formatar_log():
    """Texto completo do ;log."""
    return tr("# Últimas atualizações:\n\n") + formatar_entradas(ATUALIZACOES)


def entradas_novas(ultima_versao):
    """Entradas lançadas depois de `ultima_versao`, da mais antiga para a mais nova.

    Se a versão não for encontrada (ou for None), devolve só a mais recente.
    """
    ids = [e["versao"] for e in ATUALIZACOES]
    if ultima_versao in ids:
        novas = ATUALIZACOES[:ids.index(ultima_versao)]
    else:
        novas = ATUALIZACOES[:1]
    return list(reversed(novas))


def dividir_mensagem(texto, limite=1900):
    """Quebra o texto em partes que cabem no limite de 2000 caracteres do Discord."""
    partes = []
    atual = ""
    for linha in texto.split("\n"):
        while len(linha) > limite:
            if atual:
                partes.append(atual.rstrip("\n"))
                atual = ""
            partes.append(linha[:limite])
            linha = linha[limite:]
        if atual and len(atual) + len(linha) + 1 > limite:
            partes.append(atual.rstrip("\n"))
            atual = ""
        atual += linha + "\n"
    if atual.strip():
        partes.append(atual.rstrip("\n"))
    return partes
