"""Nomes dos comandos em inglês e sinônimos de argumentos (pt/en).

* NOMES_COMANDOS_EN: nome em português -> nome em inglês. Viram apelidos do ; (;balance)
  e nomes traduzidos do / para quem usa o Discord em inglês (/balance).
* NOMES_PARAMETROS_EN: nomes dos parâmetros do / em inglês.
* SINONIMOS: o que o usuário pode digitar (em português ou inglês) -> valor interno.
"""

NOMES_COMANDOS_EN = {
    # economia / banco / perfil
    "saldo": "balance", "daily": "daily", "trabalhar": "work", "ranking": "leaderboard", "loja": "shop",
    "pagar": "pay", "comprar": "buy", "inventario": "inventory",
    "banco": "bank", "depositar": "deposit", "sacar": "withdraw", "roubar": "rob", "perfil": "profile",
    # cassino / jogos
    "apostar": "bet", "roleta": "roulette", "slots": "slots", "blackjack": "blackjack", "duelo": "duel",
    "missoes": "missions", "quiz": "quiz",
    # territórios / guerra
    "construcoes": "buildings", "construir": "build",
    "formacoes": "formations", "formacao": "formation",
    "forja": "gear", "forjar": "forge",
    "mapa": "map", "territorios": "territories", "evoluir": "upgrade", "coletar": "collect",
    "admfundar": "admfound", "admeditar": "admedit", "admremover": "admremove",
    "recrutar": "recruit", "defender": "defend", "retirardefesa": "withdrawdefense", "defesa": "defense",
    "exercito": "army", "invadir": "invade", "quartel": "barracks", "doartropas": "donatetroops",
    "aliar": "ally", "desaliar": "unally",
    # diversão / interação
    "caracoroa": "coinflip", "jdado": "rolldice", "meme": "meme", "avaliar": "rate", "ola": "hello",
    "escolher": "choose", "pergunte": "ask",
    "abraçar": "hug", "beijar": "kiss", "tapa": "slap", "atacar": "attack", "morder": "bite",
    "ship": "ship", "exorcizar": "exorcise",
    # admin / ajuda / sistema
    "additem": "additem", "removeitem": "removeitem", "admcomm": "admcommands",
    "ajuda": "help", "ajudainvasao": "helpinvasion", "ajudadefender": "helpdefend",
    "ajudaevolucao": "helpupgrade", "info": "info", "log": "changelog",
    "canalatualizacoes": "updateschannel", "anunciar": "announce", "desativaratualizacoes": "disableupdates",
    "modulos": "modules", "modulo": "module", "perfilbot": "botprofile", "idioma": "language",
    "backup": "backup", "sincronizar": "sync",
    # catolicismo
    "santododia": "saintoftheday", "santo": "saint", "versiculo": "verse", "liturgia": "liturgy",
    "calendarioliturgico": "liturgicalcalendar", "terco": "rosary", "oracao": "prayer",
    "lembreterco": "rosaryreminder", "santodiaauto": "autosaintoftheday",
}

# apelidos extras do ; (além do nome em inglês)
APELIDOS_EXTRAS = {"idioma": ["lang"]}

NOMES_PARAMETROS_EN = {
    "construcao": "building",
    "formacao": "formation",
    "acao": "action", "aleatorio": "random", "balas": "bullets", "campo": "field", "canal": "channel",
    "cargo": "role", "coisa": "thing", "cor": "color", "data": "date", "hora": "time", "item": "item",
    "membro": "member", "misterio": "mystery", "nome": "name", "numero": "number", "opcao": "option",
    "opcoes": "options", "pergunta": "question", "preco": "price", "quantidade": "quantity",
    "territorio": "territory", "tipo": "type", "tropa": "troop", "valor": "amount", "idioma": "language",
}

SINONIMOS = {
    "formacao": {
        "equilibrada": "equilibrada", "balanced": "equilibrada",
        "pinca": "pinca", "pincer": "pinca",
        "muralha": "muralha", "wall": "muralha", "shieldwall": "muralha",
        "chuva": "chuva", "rain": "chuva", "arrows": "chuva", "volley": "chuva",
    },
    "idioma": {
        "pt": "pt", "pt_br": "pt", "ptbr": "pt", "br": "pt", "portugues": "pt", "portuguese": "pt",
        "en": "en", "en_us": "en", "en_gb": "en", "english": "en", "ingles": "en", "us": "en",
    },
    "perfil": {
        "laico": "Laico", "laica": "Laico", "secular": "Laico", "lay": "Laico",
        "padrao": "padrao", "default": "padrao", "catolico": "padrao", "catholic": "padrao",
    },
    "acao_modulo": {
        "ativar": "ativar", "ativa": "ativar", "ligar": "ativar", "on": "ativar", "enable": "ativar",
        "activate": "ativar",
        "desativar": "desativar", "desativa": "desativar", "desligar": "desativar", "off": "desativar",
        "disable": "desativar", "deactivate": "desativar",
    },
    "acao_aviso": {
        "ligar": "ligar", "ativar": "ligar", "on": "ligar", "enable": "ligar", "start": "ligar",
        "desligar": "desligar", "desativar": "desligar", "off": "desligar", "disable": "desligar",
        "stop": "desligar",
    },
    "misterio": {
        "gozosos": "gozosos", "joyful": "gozosos", "joyous": "gozosos",
        "luminosos": "luminosos", "luminous": "luminosos",
        "dolorosos": "dolorosos", "sorrowful": "dolorosos",
        "gloriosos": "gloriosos", "glorious": "gloriosos",
    },
    "oracao": {
        "sinal": "sinal", "sinal_da_cruz": "sinal", "sign_of_the_cross": "sinal", "sign": "sinal", "cross": "sinal",
        "creio": "creio", "credo": "creio", "creed": "creio", "apostles_creed": "creio",
        "pai_nosso": "pai_nosso", "painosso": "pai_nosso", "our_father": "pai_nosso", "lords_prayer": "pai_nosso",
        "ave_maria": "ave_maria", "avemaria": "ave_maria", "hail_mary": "ave_maria",
        "gloria": "gloria", "glory_be": "gloria", "glory": "gloria",
        "fatima": "fatima", "fatima_prayer": "fatima", "oracao_de_fatima": "fatima",
        "salve_rainha": "salve_rainha", "hail_holy_queen": "salve_rainha", "salve": "salve_rainha",
    },
    "cor_aposta": {
        "vermelho": "vermelho", "red": "vermelho", "preto": "preto", "black": "preto",
        "verde": "verde", "green": "verde",
    },
    "tropa": {
        "campones": "campones", "peasant": "campones",
        "miliciano": "miliciano", "militiaman": "miliciano", "militia": "miliciano",
        "soldado": "soldado", "soldier": "soldado",
        "cavaleiro": "cavaleiro", "knight": "cavaleiro",
        "sargento": "sargento", "sergeant": "sargento",
        "hospitalario": "hospitalario", "hospitaller": "hospitalario", "hospitalier": "hospitalario",
        "teutonico": "teutonico", "teutonic": "teutonico",
        "templario": "templario", "templar": "templario",
        "arqueiro": "arqueiro", "archer": "arqueiro",
        "besteiro": "besteiro", "crossbowman": "besteiro", "crossbow": "besteiro",
    },
    "construcao": {
        "muralha": "muralha", "wall": "muralha", "walls": "muralha",
        "torre": "torre", "tower": "torre",
        "fosso": "fosso", "moat": "fosso", "ditch": "fosso",
        "enfermaria": "enfermaria", "infirmary": "enfermaria", "hospital": "enfermaria",
    },
        "equipamento": {
        "arma": "arma", "armas": "arma", "weapon": "arma", "weapons": "arma", "sword": "arma",
        "armadura": "armadura", "armaduras": "armadura", "armor": "armadura", "armour": "armadura",
        "escudo": "escudo", "escudos": "escudo", "shield": "escudo", "shields": "escudo",
    },
}


def registrar_aliases(bot):
    """Registra o nome em inglês de cada comando como apelido do ; (ex.: ;balance)."""
    for cmd in list(bot.commands):
        nomes = []
        en = NOMES_COMANDOS_EN.get(cmd.name)
        if en and en != cmd.name:
            nomes.append(en)
        nomes += APELIDOS_EXTRAS.get(cmd.name, [])

        for nome in nomes:
            if nome in bot.all_commands:
                continue

            bot.all_commands[nome] = cmd
            cmd.aliases = list(cmd.aliases) + [nome]
