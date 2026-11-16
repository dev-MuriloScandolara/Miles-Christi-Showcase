from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from config import CORES
from i18n import canonico, tr, usar_interacao, atual as idioma_agora, usar as usar_idioma
from gerenciador_modulos import (
    MODULOS,
    ModuloDesativado,
    achar_chave,
    definir,
    desativados,
    modulo_ativo,
)
from gerenciador_modulos import PROTEGIDOS
from gerenciador_modulos import AGRUPAR


def montar_embed(guild):
    off = desativados(guild.id)

    linhas = []
    for chave, (emoji, nome, desc) in MODULOS.items():
        estado = "🔴" if chave in off else "🟢"
        linhas.append(f"{estado} {emoji} **{tr(nome)}** — {tr(desc)}")

    embed = discord.Embed(
        title=tr("🧩 Módulos do bot"),
        description="\n".join(linhas),
        color=CORES["adm"],
    )
    embed.set_footer(text=tr("Toque num botão para ligar/desligar. Só administradores podem mexer."))
    return embed


class PainelModulos(discord.ui.View):

    def __init__(self, ctx):
        super().__init__(timeout=120)
        self.idioma = idioma_agora()
        self.ctx = ctx
        self.message = None
        self.montar_botoes()

    def montar_botoes(self):
        self.clear_items()
        off = desativados(self.ctx.guild.id)

        for chave, (emoji, nome, _desc) in MODULOS.items():
            botao = discord.ui.Button(
                label=tr(nome),
                emoji=emoji,
                style=discord.ButtonStyle.danger if chave in off else discord.ButtonStyle.success,
            )
            botao.callback = self.criar_callback(chave)
            self.add_item(botao)

    def criar_callback(self, chave):

        async def callback(interaction):
            try:
                await interaction.response.defer()
                ligado = modulo_ativo(self.ctx.guild.id, chave)
                definir(self.ctx.guild.id, chave, not ligado)
                self.montar_botoes()
                await interaction.edit_original_response(embed=montar_embed(self.ctx.guild), view=self)
            except Exception:
                import traceback
                traceback.print_exc()
        return callback

    async def interaction_check(self, interaction):
        usar_interacao(interaction)

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(tr("❌ Só administradores podem mexer nos módulos."), ephemeral=True)
            return False

        return True

    async def on_timeout(self):
        usar_idioma(self.idioma)
        for item in self.children:
            item.disabled = True

        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


class Modulos(commands.Cog):
    """Liga e desliga os módulos (cogs) em cada servidor."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # check GLOBAL: vale para todo comando (; e /) de qualquer cog
        self.bot.add_check(self.checar_modulo)

    async def cog_unload(self):
        self.bot.remove_check(self.checar_modulo)

    async def checar_modulo(self, ctx):
        if ctx.guild is None or ctx.cog is None:
            return True

        chave = ctx.cog.qualified_name.lower()
        chave = AGRUPAR.get(chave, chave)

        if chave in PROTEGIDOS or chave not in MODULOS:
            return True

        if modulo_ativo(ctx.guild.id, chave):
            return True

        raise ModuloDesativado(MODULOS[chave][1])

    @commands.hybrid_command(description="Painel para ligar/desligar módulos do bot (admin)")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def modulos(self, ctx):
        view = PainelModulos(ctx)
        view.message = await ctx.reply(embed=montar_embed(ctx.guild), view=view)

    @commands.hybrid_command(description="Liga ou desliga um módulo específico (admin)")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @app_commands.choices(acao=[
        app_commands.Choice(name="Ativar", value="ativar"),
        app_commands.Choice(name="Desativar", value="desativar"),
    ])
    async def modulo(self, ctx, acao: str, nome: str):
        acao = canonico(acao, "acao_modulo")

        if acao is None:
            await ctx.reply(tr("❌ Use `ativar` ou `desativar`."), ephemeral=True)
            return


        chave = achar_chave(nome)

        if chave is None:
            lista = ", ".join(f"`{tr(n).lower()}`" for _e, n, _d in MODULOS.values())
            await ctx.reply(tr("❌ Não achei esse módulo. Disponíveis: {lista}", lista=lista), ephemeral=True)
            return

        definir(ctx.guild.id, chave, acao == "ativar")
        emoji, nome_bonito, _desc = MODULOS[chave]
        verbo = tr("ativado 🟢") if acao == "ativar" else tr("desativado 🔴")

        await ctx.reply(embed=discord.Embed(
            description=tr("{emoji} Módulo **{nome_bonito}** {verbo} neste servidor.", emoji=emoji, nome_bonito=tr(nome_bonito), verbo=verbo),
            color=CORES["adm"],
        ))

    @modulo.autocomplete("nome")
    async def modulo_autocomplete(self, interaction: discord.Interaction, atual: str):
        atual = atual.lower()
        return [
            app_commands.Choice(name=f"{e} {tr(n)}", value=n.lower())
            for _chave, (e, n, _d) in MODULOS.items()
            if atual in n.lower()
        ][:25]


async def setup(bot):
    await bot.add_cog(Modulos(bot))
