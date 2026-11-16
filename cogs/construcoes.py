import discord
from discord import app_commands
from discord.ext import commands

from construcoes import CONSTRUCOES, ORDEM_TIPOS, nivel, tipo_suficiente
from dados import carregar, carregar_mapa, criar_conta, criar_mundo, salvar, salvar_mapa
from i18n import canonico, idioma_atual, tr


def nome_tipo(tipo):
    return tr(tipo) if idioma_atual() == "en" else tipo.replace("_", " ")


def pct(valor):
    return round(valor * 100)


def texto_efeito(chave, d):
    partes = []

    if d.get("defesa"):
        partes.append(tr("+{pct}% de defesa", pct=pct(d["defesa"])))

    if d.get("chance"):
        if chave == "torre":
            partes.append(tr("{chance}% de chance de flechas (-{pen}% de ataque inimigo)", chance=pct(d["chance"]), pen=pct(d["penal"])))
        else:
            partes.append(tr("{chance}% de chance de o inimigo cair (-{pen}% de ataque, +{extra}% de perdas)", chance=pct(d["chance"]), pen=pct(d["penal"]), extra=pct(d["perda_extra"])))

    if d.get("reducao"):
        partes.append(tr("-{pct}% de perdas do defensor", pct=pct(d["reducao"])))

    return " · ".join(partes)


class Construcoes(commands.Cog):
    """Muralhas, torres, fossos e enfermarias nas cidades."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Mostra as construções de um território")
    @commands.guild_only()
    @app_commands.describe(territorio="Nome do território")
    async def construcoes(self, ctx, territorio: str):

        criar_mundo(ctx.guild.id)
        territorios = carregar_mapa()[str(ctx.guild.id)]["territorios"]

        if territorio not in territorios:
            await ctx.reply(tr("❌ Território não existe."), ephemeral=True)
            return

        t = territorios[territorio]

        embed = discord.Embed(
            title=tr("🏗️ Construções de {territorio}", territorio=territorio),
            description=tr("Tipo: {tipo}", tipo=nome_tipo(t["tipo"])),
            color=discord.Color.dark_orange(),
        )

        for chave, info in CONSTRUCOES.items():
            n_atual = nivel(t, chave)
            maximo = len(info["niveis"])
            linhas = []

            if n_atual:
                d = info["niveis"][n_atual - 1]
                linhas.append(tr("Atual: {nome} ({efeito})", nome=tr(d["nome"]), efeito=texto_efeito(chave, d)))
            else:
                linhas.append(tr("Nenhuma"))

            if n_atual < maximo:
                prox = info["niveis"][n_atual]
                linhas.append(tr("Próximo: {nome} — {custo} moedas (exige: {tipo})", nome=tr(prox["nome"]), custo=prox["custo"], tipo=nome_tipo(prox["min_tipo"])))
            else:
                linhas.append(tr("Nível máximo alcançado!"))

            embed.add_field(
                name=tr("{emoji} {nome} — nível {n}/{maximo}", emoji=info["emoji"], nome=tr(info["nome"]), n=n_atual, maximo=maximo),
                value="\n".join(linhas),
                inline=False,
            )

        await ctx.reply(embed=embed)

    @commands.hybrid_command(description="Constrói ou melhora algo num território seu")
    @commands.guild_only()
    @app_commands.describe(territorio="Nome do território", construcao="muralha, torre, fosso ou enfermaria")
    @app_commands.choices(construcao=[
        app_commands.Choice(name="Muralha", value="muralha"),
        app_commands.Choice(name="Torre de Arqueiros", value="torre"),
        app_commands.Choice(name="Fosso", value="fosso"),
        app_commands.Choice(name="Enfermaria", value="enfermaria"),
    ])
    async def construir(self, ctx, territorio: str, construcao: str):

        chave = canonico(construcao, "construcao")

        if chave is None:
            await ctx.reply(tr("❌ Construção inválida. Use `muralha`, `torre`, `fosso` ou `enfermaria`."), ephemeral=True)
            return

        criar_conta(ctx.guild.id, ctx.author.id)
        criar_mundo(ctx.guild.id)
        data = carregar()
        mapa = carregar_mapa()
        gid = str(ctx.guild.id)
        territorios = mapa[gid]["territorios"]

        if territorio not in territorios:
            await ctx.reply(tr("❌ Território não existe."), ephemeral=True)
            return

        t = territorios[territorio]

        if t.get("dono") != str(ctx.author.id):
            await ctx.reply(tr("❌ Esse território não é seu."), ephemeral=True)
            return

        info = CONSTRUCOES[chave]
        n_atual = nivel(t, chave)

        if n_atual >= len(info["niveis"]):
            await ctx.reply(tr("❌ Essa construção já está no nível máximo."), ephemeral=True)
            return

        alvo = info["niveis"][n_atual]

        if not tipo_suficiente(t["tipo"], alvo["min_tipo"]):
            await ctx.reply(
                tr("❌ Seu território é pequeno demais. Evolua para **{tipo}** primeiro com `;evoluir`.", tipo=nome_tipo(alvo["min_tipo"])),
                ephemeral=True,
            )
            return

        conta = data[gid][str(ctx.author.id)]

        if conta["saldo"] < alvo["custo"]:
            await ctx.reply(tr("❌ Você precisa de {custo} moedas (você tem {saldo}).", custo=alvo["custo"], saldo=conta["saldo"]), ephemeral=True)
            return

        conta["saldo"] -= alvo["custo"]
        t.setdefault("construcoes", {})[chave] = n_atual + 1
        salvar(data)
        salvar_mapa(mapa)

        embed = discord.Embed(
            title=tr("🏗️ Construção concluída!"),
            description=tr("**{nome}** (nível {nivel}) em **{territorio}**.\nCusto: {custo} moedas.", nome=tr(alvo["nome"]), nivel=n_atual + 1, territorio=territorio, custo=alvo["custo"]),
            color=discord.Color.dark_orange(),
        )
        embed.add_field(name=tr("Efeito"), value=texto_efeito(chave, alvo))

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Construcoes(bot))
