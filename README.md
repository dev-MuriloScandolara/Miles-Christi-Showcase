# Miles Christi — Discord bot (code showcase)

🇬🇧 English · [🇧🇷 Português](#-português)

> **Beta.** A feature-rich Discord bot in Python with an economy, a war game, a Catholic
> module and full English/Portuguese support. This repository is a **showcase** of selected
> parts of the code. The complete bot lives in a private repository (access on request).

## What it does

- **Hybrid commands:** every command works with a prefix (`;command`) *and* as a slash command (`/command`), built with `discord.py` cogs.
- **Per-server modules:** administrators turn each feature on or off with a button panel (`;modules`). A single global check blocks every command of a disabled cog, and related cogs can be grouped (disabling *War* also disables *Forge*, *Formations* and *Buildings*).
- **Bilingual (PT/EN):** translations live in JSON files; the language is chosen per server. Command names, descriptions, options and answers are all localized, and a small script lists any text missing a translation.
- **Catholic module (optional):** saint of the day, saint search, Gospel verse, liturgy readings, liturgical calendar (computed from the date of Easter), rosary guide and daily reminders. Uses public APIs with local data as fallback.
- **Economy and games:** daily rewards, jobs, bank, casino, quiz, missions and profiles.
- **War system:** territories, troops and alliances, plus:
  - **Forge:** researchable weapons, armor and shields with costs and research time.
  - **Formations:** a rock-paper-scissors cycle (Pincer → Arrow Rain → Shield Wall → Pincer) with per-unit-class multipliers; the defender's formation is secret.
  - **City buildings:** walls, towers, moats and infirmaries with levels, requirements by city size and random events (e.g. attackers falling into the moat).
- **Per-server bot profile:** one command switches the bot's nickname, avatar, banner and bio in a single server.

## Technical highlights

| Topic | Approach |
|---|---|
| Language | Python 3, `discord.py` (app commands + cogs), `aiohttp` |
| Storage | JSON files (planned migration to SQLite) |
| i18n | JSON catalog + per-guild language, localized command and parameter names |
| Game logic | Pure functions kept separate from Discord code, so it can be unit-tested |
| Resilience | External APIs time out quickly and fall back to local data |

## What is in this repository

```
liturgia.py              Liturgical calendar (Easter, Advent, colors) and saint search
gerenciador_modulos.py   Per-server on/off state and module grouping
cogs/modulos.py          Global check + button panel for the modules
i18n.py, i18n_comandos.py  Translation system and localized command names
cogs/idioma.py           Per-server language command and the check that applies it
locales/                 Translation catalogs
changelog.py             Bilingual changelog and the logic that formats release notes
forja.py                 Forge: equipment levels, costs and bonuses
formacoes.py             Battle formations and advantage cycle
construcoes.py           City buildings, requirements and random events
testar_traducoes.py      Lists texts that are still missing a translation
cogs/catolicismo.py      Catholic module: APIs with fallback, daily reminders (background task)
cogs/construcoes.py      City buildings: hybrid commands, embeds and localized texts
```

These files are excerpts. They import other parts of the bot (such as `config.py`), so
they are meant to be read, not run on their own.

## Try the bot

https://discord.gg/Q4AMdraDKp

## License

[MIT](LICENSE) for the code in this repository.

---

# 🇧🇷 Português

> **Beta.** Um bot de Discord em Python com economia, jogo de guerra, módulo católico e
> suporte completo a português e inglês. Este repositório é uma **vitrine** com partes
> selecionadas do código. O bot completo fica em um repositório privado (acesso sob pedido).

## O que ele faz

- **Comandos híbridos:** todo comando funciona com prefixo (`;comando`) e também como barra (`/comando`), usando cogs do `discord.py`.
- **Módulos por servidor:** administradores ligam e desligam cada função por um painel de botões (`;modulos`). Uma checagem global bloqueia todos os comandos de um cog desligado, e cogs relacionados podem ser agrupados (desligar *Guerra* também desliga *Forja*, *Formações* e *Construções*).
- **Bilíngue (PT/EN):** as traduções ficam em arquivos JSON e o idioma é escolhido por servidor. Nomes de comandos, descrições, opções e respostas são traduzidos, e um script lista os textos que ainda não têm tradução.
- **Módulo católico (opcional):** santo do dia, pesquisa de santos, versículo, liturgia, calendário litúrgico (calculado a partir da data da Páscoa), guia do terço e lembretes diários. Usa APIs públicas, com dados locais como alternativa.
- **Economia e jogos:** recompensa diária, trabalho, banco, cassino, quiz, missões e perfis.
- **Sistema de guerra:** territórios, tropas e alianças, mais:
  - **Forja:** armas, armaduras e escudos pesquisáveis, com custo e tempo de pesquisa.
  - **Formações:** ciclo de vantagem (Pinça → Chuva de Flechas → Muralha de Escudos → Pinça) com multiplicadores por classe de tropa; a formação do defensor é secreta.
  - **Construções das cidades:** muralhas, torres, fossos e enfermarias com níveis, exigência de tamanho da cidade e eventos aleatórios (por exemplo, o inimigo cair no fosso).
- **Perfil do bot por servidor:** um comando troca nome, foto, banner e bio do bot em um servidor só.

## Destaques técnicos

| Tema | Abordagem |
|---|---|
| Linguagem | Python 3, `discord.py` (comandos de aplicação + cogs), `aiohttp` |
| Armazenamento | Arquivos JSON (migração para SQLite planejada) |
| i18n | Catálogo em JSON + idioma por servidor, nomes de comandos e parâmetros traduzidos |
| Lógica de jogo | Funções puras separadas do código do Discord, o que facilita testes |
| Resiliência | APIs externas com tempo limite curto e dados locais como alternativa |

## O que há neste repositório

```
liturgia.py              Calendário litúrgico (Páscoa, Advento, cores) e busca de santos
gerenciador_modulos.py   Estado ligado/desligado por servidor e agrupamento de módulos
cogs/modulos.py          Checagem global + painel de botões dos módulos
i18n.py, i18n_comandos.py  Sistema de tradução e nomes de comandos traduzidos
cogs/idioma.py           Comando de idioma por servidor e a checagem que o aplica
locales/                 Catálogos de tradução
changelog.py             Changelog bilíngue e a lógica que formata as notas de versão
forja.py                 Forja: níveis de equipamento, custos e bônus
formacoes.py             Formações de batalha e ciclo de vantagem
construcoes.py           Construções das cidades, exigências e eventos aleatórios
testar_traducoes.py      Lista os textos que ainda não têm tradução
cogs/catolicismo.py      Módulo católico: APIs com alternativa local e lembretes diários (tarefa em segundo plano)
cogs/construcoes.py      Construções das cidades: comandos híbridos, embeds e textos traduzidos
```

Os arquivos são trechos. Eles importam outras partes do bot (como o `config.py`), então
servem para ler, não para rodar sozinhos.

## Experimente o bot

https://discord.gg/Q4AMdraDKp

## Licença

[MIT](LICENSE) para o código deste repositório.
