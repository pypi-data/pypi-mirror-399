from pygments.lexer import RegexLexer
from pygments.lexers.markup import MarkdownLexer
from temper_pygments.adapt import adapt_tokens, lexers
from temper_syntax import temper_pygments as t


_temper = t.TemperLexer()
_tempermd = t.TemperMdLexer()


class TemperLexer(RegexLexer):
    name = _temper.name
    aliases = _temper.aliases
    filenames = _temper.filenames
    tokens = adapt_tokens(_temper.tokens)


lexers["Temper"] = TemperLexer


class TemperMdLexer(MarkdownLexer):
    name = _tempermd.name
    aliases = _tempermd.aliases
    filenames = _tempermd.filenames
    tokens = adapt_tokens(_tempermd.tokens)


# print(TemperMdLexer.tokens)
