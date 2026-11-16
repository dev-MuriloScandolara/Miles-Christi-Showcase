"""Sistema de idiomas do bot (Português e English).

Como funciona

* Cada servidor tem um idioma (guardado em idiomas.json). O padrão é português.
* O texto-fonte do código fica em português: tr("Você ganhou {valor} moedas", valor=10).
  Em português, o texto sai como está. Em inglês, procuramos a tradução em locales/en.json
  (a chave é o próprio texto em português). Sem tradução, cai no português (nada quebra).
* O idioma "da vez" fica em uma variável de contexto, definida a cada comando/botão
  com usar_ctx(...) / usar_interacao(...) / usar_servidor(...).

Para adicionar um texto novo: escreva em português dentro de tr(...) e acrescente a
tradução em locales/en.json (o teste de catálogo avisa se faltar).
"""

import contextvars
import json
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ARQUIVO = BASE_DIR / "idiomas.json"
PASTA_LOCALES = BASE_DIR / "locales"

IDIOMAS = {"pt": "Português", "en": "English"}
PADRAO = "pt"

_atual = contextvars.ContextVar("idioma", default=PADRAO)
_catalogos = {}
_config = None




def catalogo(lang):
    """Dicionário {texto em português: texto traduzido} do idioma (vazio para o padrão)."""
    if lang == PADRAO or lang not in IDIOMAS:
        return {}

    if lang not in _catalogos:
        try:
            with (PASTA_LOCALES / f"{lang}.json").open("r", encoding="utf-8-sig") as f:
                _catalogos[lang] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            _catalogos[lang] = {}

    return _catalogos[lang]


def recarregar_catalogos():
    _catalogos.clear()




def _ler():
    global _config

    if _config is None:
        try:
            with ARQUIVO.open("r", encoding="utf-8-sig") as f:
                _config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            _config = {}

    return _config


def idioma_do_servidor(guild_id):
    if guild_id is None:
        return PADRAO

    return _ler().get(str(guild_id), PADRAO)


def definir_idioma(guild_id, lang):
    dados = _ler()
    dados[str(guild_id)] = lang

    with ARQUIVO.open("w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def recarregar_config():
    global _config
    _config = None




def atual():
    return _atual.get()


idioma_atual = atual


def usar(lang):
    _atual.set(lang if lang in IDIOMAS else PADRAO)


def usar_servidor(guild_id):
    usar(idioma_do_servidor(guild_id))


def usar_ctx(ctx):
    usar_servidor(ctx.guild.id if getattr(ctx, "guild", None) else None)


def usar_interacao(interaction):
    usar_servidor(getattr(interaction, "guild_id", None))




def tr(texto, /, **kw):
    """Traduz `texto` (em português) para o idioma atual e preenche os {campos}."""
    if not isinstance(texto, str):
        return texto

    modelo = texto

    lang = _atual.get()
    if lang != PADRAO:
        modelo = catalogo(lang).get(texto, texto)

    if not kw:
        return modelo

    try:
        return modelo.format(**kw)
    except (KeyError, IndexError, ValueError):
        # tradução com campo errado: melhor mostrar em português do que quebrar o comando
        return texto.format(**kw)


def traduzir_botoes(view):
    """Traduz os rótulos dos botões de uma View (definidos na importação, antes de saber o idioma)."""
    for item in view.children:
        if getattr(item, "label", None):
            item.label = tr(item.label)




def data_curta(d):
    return d.strftime("%d/%m") if atual() == "pt" else d.strftime("%b %d")


def data_longa(d):
    return d.strftime("%d/%m/%Y") if atual() == "pt" else d.strftime("%b %d, %Y")




def _chave(valor):
    valor = unicodedata.normalize("NFD", str(valor).strip().lower())
    valor = "".join(c for c in valor if unicodedata.category(c) != "Mn")
    return "_".join(valor.replace("-", " ").split())


def canonico(valor, grupo):
    """Converte o que o usuário digitou (pt ou en) para o valor interno; None se não existir."""
    from i18n_comandos import SINONIMOS

    return SINONIMOS.get(grupo, {}).get(_chave(valor))


def normalizar_idioma(texto):
    return canonico(texto, "idioma")
