import json
import random
import re
from datetime import date, datetime, timedelta, timezone
from typing import Literal
from urllib.parse import quote

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import BASE_DIR
from i18n import canonico, data_curta, data_longa, idioma_atual, tr, usar_servidor
from gerenciador_modulos import modulo_ativo
from liturgia import (
    COR_EMOJI,
    DIAS_SEMANA,
    buscar_santo,
    estacao,
    normalizar,
    proximas_datas,
)
from santos import CALENDARIO, MISTERIO_DO_DIA, MISTERIOS, ORACOES, SANTOS, VERSICULOS

# Horário de Brasília (sem horário de verão desde 2019). Mude se o bot for para outro fuso.
FUSO = timezone(timedelta(hours=-3))

ARQUIVO = BASE_DIR / "catolicismo.json"

COR_EMBED = discord.Color.from_rgb(212, 175, 55)  # dourado

# ---- APIs externas (todas opcionais: se falharem, o bot usa dados locais) ----
LITURGIA_URL = "https://liturgia.up.railway.app/v2/"   # liturgia diária (API da comunidade)
BIBLIA_URL = "https://bible-api.com/{ref}?translation=almeida"  # texto (Almeida, domínio público)
WIKIPEDIA_BUSCA = "https://pt.wikipedia.org/w/api.php"
WIKIPEDIA_RESUMO = "https://pt.wikipedia.org/api/rest_v1/page/summary/{titulo}"
LINK_LITURGIA = "https://www.vaticannews.va/pt/palavra-do-dia.html"
CABECALHO = {"User-Agent": "TesteBot/1.0 (https://github.com/dev-MuriloScandolara) aiohttp"}
# versões em inglês (usadas quando o servidor está em English)
BIBLIA_URL_EN = "https://bible-api.com/{ref}?translation=web"  # World English Bible (domínio público)
WIKIPEDIA_BUSCA_EN = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_RESUMO_EN = "https://en.wikipedia.org/api/rest_v1/page/summary/{titulo}"
LINK_LITURGIA_EN = "https://bible.usccb.org/daily-bible-reading"
SUFIXO_BUSCA_EN = "Catholic saint"
PADRAO_SANTO = re.compile(
    r"\b(canoniz\w*|m[áa]rtir|martyr|ap[óo]stolo|apostle|beat[oa]|saint|bispo|bishop|padroeir[oa]|frade|freira|monge|monja)\b",
    re.IGNORECASE,
)
TEXTO_LEITURAS_EN = "Detailed readings are only available in Portuguese for now. See the full readings at the link below."

OPCOES_MISTERIO = [
    app_commands.Choice(name="Gozosos", value="gozosos"),
    app_commands.Choice(name="Luminosos", value="luminosos"),
    app_commands.Choice(name="Dolorosos", value="dolorosos"),
    app_commands.Choice(name="Gloriosos", value="gloriosos"),
]
OPCOES_ORACAO = [
    app_commands.Choice(name="Sinal da Cruz", value="sinal"),
    app_commands.Choice(name="Creio", value="creio"),
    app_commands.Choice(name="Pai-Nosso", value="pai_nosso"),
    app_commands.Choice(name="Ave-Maria", value="ave_maria"),
    app_commands.Choice(name="Glória", value="gloria"),
    app_commands.Choice(name="Oração de Fátima", value="fatima"),
    app_commands.Choice(name="Salve Rainha", value="salve_rainha"),
]
OPCOES_ACAO = [
    app_commands.Choice(name="Ligar", value="ligar"),
    app_commands.Choice(name="Desligar", value="desligar"),
]

LIVROS_API = {
    "Salmos": "Psalms", "Provérbios": "Proverbs", "Isaías": "Isaiah", "Jeremias": "Jeremiah",
    "Josué": "Joshua", "Deuteronômio": "Deuteronomy", "Lamentações": "Lamentations", "Miqueias": "Micah",
    "Mateus": "Matthew", "Marcos": "Mark", "Lucas": "Luke", "João": "John", "Romanos": "Romans",
    "1 Coríntios": "1 Corinthians", "2 Coríntios": "2 Corinthians", "Gálatas": "Galatians",
    "Efésios": "Ephesians", "Filipenses": "Philippians", "Colossenses": "Colossians",
    "1 Tessalonicenses": "1 Thessalonians", "Hebreus": "Hebrews", "Tiago": "James",
    "1 Pedro": "1 Peter", "1 João": "1 John", "Apocalipse": "Revelation",
}


def agora():
    return datetime.now(FUSO)


async def pegar_json(url, params=None):
    """GET que devolve JSON ou None se der qualquer problema (rede, timeout, API fora)."""
    try:
        async with aiohttp.ClientSession(headers=CABECALHO, timeout=aiohttp.ClientTimeout(total=8)) as sessao:
            async with sessao.get(url, params=params) as resp:
                if resp.status != 200:
                    return None
                return await resp.json(content_type=None)
    except (aiohttp.ClientError, TimeoutError, ValueError):
        return None


def carregar_config():
    try:
        with ARQUIVO.open("r", encoding="utf-8-sig") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def salvar_config(dados):
    with ARQUIVO.open("w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


# ---------- Montagem dos embeds ----------

def embed_santo_do_dia(d):
    chave = d.strftime("%m-%d")
    celebracoes = CALENDARIO.get(chave, [])
    tempo, cor, obs = estacao(d)

    embed = discord.Embed(
        title=tr("✝️ Santo do dia — {data_curta_d}", data_curta_d=data_curta(d)),
        color=COR_EMBED,
    )

    if celebracoes:
        linhas = []
        for nome, grau in celebracoes:
            linhas.append(f"**{tr(nome)}**\n*{tr(grau)}*")
        embed.description = "\n\n".join(linhas)
    else:
        embed.description = tr("Neste dia não há celebração própria no Calendário Romano Geral. Que tal conhecer um santo com `/santo`?")

    liturgico = tr("{cor_emoji_cor} {tempo} — cor litúrgica **{cor}**", cor_emoji_cor=COR_EMOJI[cor], tempo=tr(tempo), cor=tr(cor))
    if obs:
        liturgico += f"\n*{tr(obs)}*"

    embed.add_field(name=tr("Tempo litúrgico"), value=liturgico, inline=False)
    embed.set_footer(text=tr("Calendário Romano Geral. Algumas datas variam por país ou diocese."))
    return embed


def embed_terco(d, misterio=None):
    chave = misterio or MISTERIO_DO_DIA[d.weekday()]
    info = MISTERIOS[chave]

    embed = discord.Embed(
        title=tr("📿 Santo Terço — Mistérios {chave_capitalize}", chave_capitalize=tr(chave).capitalize()),
        description=tr("{info_emoji} Rezados às **{info_dias}**.", info_emoji=info['emoji'], info_dias=tr(info['dias'])),
        color=COR_EMBED,
    )

    embed.add_field(
        name=tr("Mistérios"),
        value="\n".join(f"**{i}.** {tr(m)}" for i, m in enumerate(info["lista"], start=1)),
        inline=False,
    )

    if misterio is None:
        embed.set_footer(text=tr("Mistérios de hoje ({dias_semana_d_weekday})", dias_semana_d_weekday=tr(DIAS_SEMANA[d.weekday()])))

    return embed


def embed_como_rezar_terco():
    embed = discord.Embed(
        title=tr("📿 Como rezar o Terço"),
        description=tr("O terço tem cinco \"dezenas\". Cada uma medita um mistério da vida de Jesus e Maria."),
        color=COR_EMBED,
    )

    embed.add_field(
        name=tr("Começo (nas contas iniciais)"),
        value=(
            tr("1. Faça o **sinal da cruz** e reze o **Creio**.\n"
            "2. Um **Pai-Nosso**.\n"
            "3. Três **Ave-Marias** (por fé, esperança e caridade).\n"
            "4. Um **Glória**.")
        ),
        inline=False,
    )

    embed.add_field(
        name=tr("Cada dezena (repita 5 vezes)"),
        value=(
            tr("1. Anuncie o mistério e medite nele.\n"
            "2. Um **Pai-Nosso**.\n"
            "3. Dez **Ave-Marias**.\n"
            "4. Um **Glória** e a **Oração de Fátima** (\"Ó meu Jesus...\").")
        ),
        inline=False,
    )

    embed.add_field(
        name=tr("Final"),
        value=tr("Reze a **Salve Rainha** e faça o sinal da cruz."),
        inline=False,
    )

    embed.add_field(
        name=tr("Mistérios por dia"),
        value=(
            tr("Seg e sáb: Gozosos\nTer e sex: Dolorosos\nQua e dom: Gloriosos\nQui: Luminosos\n\n"
            "Use `/terco` para ver os de hoje e `/oracao` para ler cada oração.")
        ),
        inline=False,
    )

    return embed


def separar_referencias(dados):
    """Acha todas as chaves 'referencia' em qualquer formato de JSON que a API devolver."""
    achadas = []

    def andar(no, rotulo=""):
        if isinstance(no, dict):
            if "referencia" in no and no["referencia"]:
                achadas.append((rotulo, str(no["referencia"]), no.get("refrao")))
            for chave, valor in no.items():
                andar(valor, chave if isinstance(valor, (dict, list)) else rotulo)
        elif isinstance(no, list):
            for item in no:
                andar(item, rotulo)

    andar(dados)
    return achadas


ROTULOS_LEITURA = {
    "primeiraleitura": "📖 1ª Leitura",
    "segundaleitura": "📖 2ª Leitura",
    "salmo": "🎶 Salmo",
    "evangelho": "✝️ Evangelho",
}


def rotulo_leitura(chave):
    return ROTULOS_LEITURA.get(normalizar(chave).replace(" ", ""), f"📖 {chave}")


class Catolicismo(commands.Cog):
    """Santo do dia, busca de santos, versículo, liturgia, calendário litúrgico e terço."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.agendador.start()

    async def cog_unload(self):
        self.agendador.cancel()

    # ---------- Comandos ----------

    @commands.hybrid_command(description="Mostra o santo (ou a celebração) do dia")
    @app_commands.describe(data="Opcional, no formato dd/mm (ex: 28/10)")
    async def santododia(self, ctx, data: str = None):

        if data:
            m = re.fullmatch(r"\s*(\d{1,2})/(\d{1,2})\s*", data)

            try:
                a, b = int(m.group(1)), int(m.group(2))
                mes, dia = (a, b) if idioma_atual() == "en" else (b, a)
                d = date(2024, mes, dia)  # 2024 = ano bissexto (aceita 29/02)
            except (AttributeError, ValueError):
                await ctx.reply(tr("❌ Use o formato dd/mm, por exemplo `28/10`."), ephemeral=True)
                return

            d = d.replace(year=agora().year) if not (d.month == 2 and d.day == 29) else d
        else:
            d = agora().date()

        await ctx.reply(embed=embed_santo_do_dia(d))

    @commands.hybrid_command(description="Pesquisa um santo: padroeiro de, significado e história")
    @app_commands.describe(nome="Ex: São Judas Tadeu")
    async def santo(self, ctx, *, nome: str):

        await ctx.defer()

        santo, parecidos = buscar_santo(nome, SANTOS)

        if santo is not None:
            embed = discord.Embed(title=f"✝️ {tr(santo['nome'])}", color=COR_EMBED)
            embed.add_field(name=tr("📅 Festa"), value=tr(santo["festa"]), inline=False)
            embed.add_field(name=tr("🛡️ Padroeiro de"), value=tr(santo["padroeiro"]), inline=False)
            embed.add_field(name=tr("⛪ O que significa para a Igreja"), value=tr(santo["significado"]), inline=False)
            embed.add_field(name=tr("📜 História"), value=tr(santo["historia"])[:1024], inline=False)

            if parecidos:
                embed.set_footer(text=tr("Também pode ser: ") + ", ".join(tr(p) for p in parecidos))

            await ctx.reply(embed=embed)
            return

        # não está na base local: tenta a Wikipédia
        embed = await self.buscar_na_wikipedia(nome)

        if embed is None:
            await ctx.reply(
                tr("❌ Não encontrei esse santo. Tente o nome mais completo (ex: `Santo Antônio de Pádua`)."),
                ephemeral=True,
            )
            return

        await ctx.reply(embed=embed)

    @santo.autocomplete("nome")
    async def santo_autocomplete(self, interaction: discord.Interaction, atual: str):
        alvo = normalizar(atual)
        return [
            app_commands.Choice(name=tr(s["nome"]), value=s["nome"])
            for s in SANTOS
            if alvo in normalizar(s["nome"]) or alvo in normalizar(tr(s["nome"]))
        ][:25]

    async def buscar_na_wikipedia(self, nome):
        em_ingles = idioma_atual() == "en"
        wiki_busca = WIKIPEDIA_BUSCA_EN if em_ingles else WIKIPEDIA_BUSCA
        wiki_resumo = WIKIPEDIA_RESUMO_EN if em_ingles else WIKIPEDIA_RESUMO
        busca = (nome + " " + SUFIXO_BUSCA_EN) if em_ingles else tr("{nome} santo católico", nome=tr(nome))

        achados = await pegar_json(wiki_busca, {
            "action": "query", "list": "search", "srsearch": busca, "srlimit": 5, "format": "json",
        })

        try:
            titulos = [r["title"] for r in achados["query"]["search"]]
        except (TypeError, KeyError):
            return None

        for titulo in titulos:
            resumo = await pegar_json(wiki_resumo.format(titulo=quote(titulo.replace(" ", "_"))))

            if not resumo or not resumo.get("extract") or not PADRAO_SANTO.search(resumo["extract"]):
                continue

            embed = discord.Embed(title=f"✝️ {resumo.get('title', titulo)}", description=resumo["extract"][:1500], color=COR_EMBED)

            try:
                embed.url = resumo["content_urls"]["desktop"]["page"]
            except KeyError:
                pass

            embed.set_footer(text=tr("Fonte: Wikipédia. Verifique a informação em fontes católicas."))
            return embed

        return None

    @commands.hybrid_command(description="Versículo do dia")
    @app_commands.describe(aleatorio="Sorteia um versículo em vez do versículo do dia")
    async def versiculo(self, ctx, aleatorio: bool = False):

        await ctx.defer()

        if aleatorio:
            ref = random.choice(VERSICULOS)
        else:
            ref = VERSICULOS[agora().timetuple().tm_yday % len(VERSICULOS)]

        livro, numeros = ref.rsplit(" ", 1)
        ref_api = f"{LIVROS_API.get(livro, livro)} {numeros}"

        em_ingles = idioma_atual() == "en"
        url_biblia = BIBLIA_URL_EN if em_ingles else BIBLIA_URL
        ref_exibida = ref_api if em_ingles else ref
        dados = await pegar_json(url_biblia.format(ref=quote(ref_api, safe=':-,')))
        texto = (dados or {}).get("text", "").strip()

        embed = discord.Embed(title=tr("📖 Versículo do dia"), color=COR_EMBED)

        if texto:
            embed.description = f"*{texto}*\n\n**— {ref_exibida}**"
            embed.set_footer(text=tr("Tradução João Ferreira de Almeida (domínio público)."))
        else:
            embed.description = tr("**{ref_exibida}**\n\nNão consegui buscar o texto agora. Abra a Bíblia nessa passagem e leia com calma. 🙏", ref_exibida=ref_exibida)

        await ctx.reply(embed=embed)

    @commands.hybrid_command(description="Leituras da liturgia diária")
    async def liturgia(self, ctx):

        await ctx.defer()

        d = agora().date()
        tempo, cor, obs = estacao(d)

        embed = discord.Embed(
            title=tr("📜 Liturgia — {dias_semana_d_weekday}, {data_longa_d}", dias_semana_d_weekday=tr(DIAS_SEMANA[d.weekday()]), data_longa_d=data_longa(d)),
            color=COR_EMBED,
        )

        liturgico = tr("{cor_emoji_cor} {tempo} — cor **{cor}**", cor_emoji_cor=COR_EMOJI[cor], tempo=tr(tempo), cor=tr(cor))
        if obs:
            liturgico += f"\n*{tr(obs)}*"
        embed.add_field(name=tr("Tempo litúrgico"), value=liturgico, inline=False)

        em_ingles = idioma_atual() == "en"
        link_liturgia = LINK_LITURGIA_EN if em_ingles else LINK_LITURGIA
        dados = None if em_ingles else await pegar_json(LITURGIA_URL, {"dia": d.day, "mes": d.month, "ano": d.year})
        referencias = separar_referencias(dados) if dados else []

        for rotulo, ref, refrao in referencias[:6]:
            valor = ref
            if refrao:
                valor += tr("\n*Refrão: {str_refrao_200}*", str_refrao_200=str(refrao)[:200])
            embed.add_field(name=rotulo_leitura(rotulo), value=valor, inline=False)

        if not referencias:
            embed.add_field(
                name=tr("Leituras"),
                value=TEXTO_LEITURAS_EN if em_ingles else tr("Não consegui buscar as leituras agora. Veja a liturgia completa no link abaixo."),
                inline=False,
            )

        embed.add_field(name=tr("Texto completo"), value=tr("[Liturgia diária (Vatican News)]({link_liturgia})", link_liturgia=link_liturgia), inline=False)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(description="Tempo litúrgico de hoje e próximas datas importantes")
    async def calendarioliturgico(self, ctx):

        hoje = agora().date()
        tempo, cor, obs = estacao(hoje)

        embed = discord.Embed(title=tr("🗓️ Calendário Litúrgico"), color=COR_EMBED)

        atual = tr("{cor_emoji_cor} **{tempo}** — cor **{cor}**", cor_emoji_cor=COR_EMOJI[cor], tempo=tr(tempo), cor=tr(cor))
        if obs:
            atual += f"\n*{tr(obs)}*"
        embed.add_field(name=tr("Hoje"), value=atual, inline=False)

        proximas = proximas_datas(hoje, quantas=5)
        embed.add_field(
            name=tr("Próximas datas"),
            value="\n".join(f"**{data_longa(d)}** — {tr(nome)}" for d, nome in proximas),
            inline=False,
        )

        embed.set_footer(text=tr("Datas móveis calculadas a partir da Páscoa (Calendário Romano)."))
        await ctx.reply(embed=embed)

    @commands.hybrid_command(description="Como rezar o terço e os mistérios de hoje")
    @app_commands.describe(misterio="Opcional: ver outros mistérios")
    @app_commands.choices(misterio=OPCOES_MISTERIO)
    async def terco(self, ctx, misterio: str = None):
        if misterio is not None:
            misterio = canonico(misterio, "misterio")

            if misterio is None:
                await ctx.reply(tr("❌ Mistério inválido. Use gozosos, luminosos, dolorosos ou gloriosos."), ephemeral=True)
                return


        embeds = [embed_terco(agora().date(), misterio)]

        if misterio is None:
            embeds.insert(0, embed_como_rezar_terco())

        await ctx.reply(embeds=embeds)

    @commands.hybrid_command(description="Mostra o texto de uma oração")
    @app_commands.describe(nome="Qual oração")
    @app_commands.choices(nome=OPCOES_ORACAO)
    async def oracao(self, ctx, nome: str):
        nome = canonico(nome, "oracao")

        if nome is None:
            await ctx.reply(tr("❌ Oração não encontrada. Escolha uma da lista."), ephemeral=True)
            return


        titulos = {
            "sinal": tr("Sinal da Cruz"), "creio": tr("Creio (Símbolo dos Apóstolos)"), "pai_nosso": tr("Pai-Nosso"),
            "ave_maria": tr("Ave-Maria"), "gloria": tr("Glória"), "fatima": tr("Oração de Fátima"), "salve_rainha": tr("Salve Rainha"),
        }

        await ctx.reply(embed=discord.Embed(title=f"🙏 {titulos[nome]}", description=tr(ORACOES[nome]), color=COR_EMBED))

    # ---------- Posts automáticos ----------

    async def configurar_aviso(self, ctx, chave, acao, canal, hora, cargo):
        acao = canonico(acao, "acao_aviso")

        if acao is None:
            await ctx.reply(tr("❌ Use `ligar` ou `desligar`."), ephemeral=True)
            return

        dados = carregar_config()
        gid = str(ctx.guild.id)

        if acao == "desligar":
            dados.get(gid, {}).pop(chave, None)
            salvar_config(dados)
            await ctx.reply(tr("🔕 Aviso automático desligado neste servidor."))
            return

        if not re.fullmatch(r"([01]?\d|2[0-3]):[0-5]\d", hora):
            await ctx.reply(tr("❌ Horário inválido. Use o formato `HH:MM`, por exemplo `18:00`."), ephemeral=True)
            return

        h, m = hora.split(":")
        hora = f"{int(h):02d}:{m}"
        canal = canal or ctx.channel

        dados.setdefault(gid, {})[chave] = {
            "canal": canal.id,
            "hora": hora,
            "cargo": cargo.id if cargo else None,
            "ultimo": "",
        }
        salvar_config(dados)

        await ctx.reply(tr("✅ Aviso ligado: todo dia às **{hora}** (horário de Brasília) em {canal_mention}.", hora=hora, canal_mention=canal.mention))

    @commands.hybrid_command(description="Liga/desliga o lembrete diário do terço (admin)")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(acao="ligar ou desligar", canal="Canal do lembrete", hora="HH:MM (padrão 18:00)", cargo="Cargo a mencionar (opcional)")
    @app_commands.choices(acao=OPCOES_ACAO)
    async def lembreterco(self, ctx, acao: str, canal: discord.TextChannel = None,
                          hora: str = "18:00", cargo: discord.Role = None):
        await self.configurar_aviso(ctx, "terco", acao, canal, hora, cargo)

    @commands.hybrid_command(description="Liga/desliga o santo do dia automático (admin)")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(acao="ligar ou desligar", canal="Canal do aviso", hora="HH:MM (padrão 07:00)", cargo="Cargo a mencionar (opcional)")
    @app_commands.choices(acao=OPCOES_ACAO)
    async def santodiaauto(self, ctx, acao: str, canal: discord.TextChannel = None,
                           hora: str = "07:00", cargo: discord.Role = None):
        await self.configurar_aviso(ctx, "santodia", acao, canal, hora, cargo)

    @tasks.loop(minutes=1)
    async def agendador(self):
        try:
            await self._rodar_agendador()
        except Exception as erro:
            # sem isso, um erro inesperado para o loop e os avisos somem até reiniciar
            print(f"[catolicismo] erro no agendador: {erro!r}")

    async def _rodar_agendador(self):
        momento = agora()
        hoje = momento.date().isoformat()
        minutos_agora = momento.hour * 60 + momento.minute

        dados = carregar_config()
        alterado = False

        for gid, avisos in dados.items():

            if not modulo_ativo(gid, "catolicismo"):
                continue

            for chave, aviso in avisos.items():
                try:
                    h, m = aviso["hora"].split(":")
                    atraso = minutos_agora - (int(h) * 60 + int(m))

                    # só posta dentro de 30 min do horário (evita postar tarde se o bot ficou desligado)
                    if aviso.get("ultimo") == hoje or not 0 <= atraso < 30:
                        continue

                    aviso["ultimo"] = hoje
                    alterado = True

                    guild = self.bot.get_guild(int(gid))
                    canal = guild.get_channel(aviso["canal"]) if guild else None

                    if canal is None:
                        continue

                    usar_servidor(gid)

                    if chave == "terco":
                        embed = embed_terco(momento.date())
                        embed.title = tr("📿 Hora do Santo Terço")
                    else:
                        embed = embed_santo_do_dia(momento.date())

                    texto = f"<@&{aviso['cargo']}>" if aviso.get("cargo") else None

                    try:
                        await canal.send(texto, embed=embed, allowed_mentions=discord.AllowedMentions(roles=True))
                    except discord.HTTPException as erro:
                        print(f"[catolicismo] não consegui postar no servidor {gid}: {erro}")
                except Exception as erro:
                    print(f"[catolicismo] aviso com problema no servidor {gid} ({chave}): {erro!r}")

        if alterado:
            salvar_config(dados)

    @agendador.before_loop
    async def esperar_bot(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Catolicismo(bot))
