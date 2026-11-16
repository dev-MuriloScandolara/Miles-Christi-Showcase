import discord
from discord import app_commands
from discord.ext import commands

import i18n
from i18n_comandos import NOMES_COMANDOS_EN, NOMES_PARAMETROS_EN
from i18n import tr

LOCALES_EN = (discord.Locale.american_english, discord.Locale.british_english)


class Tradutor(app_commands.Translator):
    """Traduz nomes e descrições dos comandos de barra (/) para quem usa o Discord em inglês."""

    async def translate(self, string, locale, context):
        if locale not in LOCALES_EN:
            return None

        mensagem = string.message
        local = context.location
        Local = app_commands.TranslationContextLocation

        if local is Local.command_name:
            return NOMES_COMANDOS_EN.get(mensagem)

        if local is Local.parameter_name:
            return NOMES_PARAMETROS_EN.get(mensagem)

        if local in (Local.command_description, Local.parameter_description, Local.choice_name):
            traducao = i18n.catalogo("en").get(mensagem)
            return traducao if traducao and len(traducao) <= 100 else None

        return None


class Idioma(commands.Cog):
    """Idioma do bot (Português / English) por servidor."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_check(self.definir_idioma_da_vez)

    async def cog_unload(self):
        self.bot.remove_check(self.definir_idioma_da_vez)

    async def definir_idioma_da_vez(self, ctx):
        # roda antes de todo comando (; ou /): define o idioma das respostas deste servidor
        i18n.usar_ctx(ctx)
        return True

    @commands.hybrid_command(description="Muda o idioma do bot neste servidor (Português / English)")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(idioma="pt (Português) ou en (English)")
    @app_commands.choices(idioma=[
        app_commands.Choice(name="Português", value="pt"),
        app_commands.Choice(name="English", value="en"),
    ])
    async def idioma(self, ctx, idioma: str = None):

        if idioma is None:
            nome = i18n.IDIOMAS[i18n.idioma_do_servidor(ctx.guild.id)]
            await ctx.reply(tr("🌐 Idioma atual: **{nome}**.\nUse `;idioma pt` ou `;idioma en` para mudar.", nome=nome))
            return

        novo = i18n.normalizar_idioma(idioma)

        if novo is None:
            await ctx.reply(tr("❌ Idioma inválido. Use `pt` (Português) ou `en` (English)."), ephemeral=True)
            return

        i18n.definir_idioma(ctx.guild.id, novo)
        i18n.usar(novo)  # a resposta já sai no idioma novo

        await ctx.reply(tr("✅ Idioma alterado para **{i18n_idiomas_novo}**.", i18n_idiomas_novo=i18n.IDIOMAS[novo]))


async def setup(bot):
    await bot.add_cog(Idioma(bot))
