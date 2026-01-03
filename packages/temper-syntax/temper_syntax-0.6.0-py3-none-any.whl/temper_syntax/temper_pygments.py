from temper_syntax.pygments import include as include_15, default as default_13, bygroups as bygroups_19, using as using_21, inherit as inherit_22, RuleOption, Rule, Kind, TokenKind
from builtins import str as str1
from typing import Sequence as Sequence4
from types import MappingProxyType as MappingProxyType9
from temper_core import Pair as Pair5, map_constructor as map_constructor6, str_cat as str_cat7, list_join as list_join8
from temper_syntax.pygments import RuleOption, Rule, Kind
pair_358 = Pair5
map_constructor_359 = map_constructor6
str_cat_360 = str_cat7
list_join_361 = list_join8
class TemperLexer:
    name_23: 'str1'
    aliases_24: 'Sequence4[str1]'
    filenames_25: 'Sequence4[str1]'
    tokens_26: 'MappingProxyType9[str1, (Sequence4[RuleOption])]'
    __slots__ = ('name_23', 'aliases_24', 'filenames_25', 'tokens_26')
    def __init__(this_0) -> None:
        this_0.name_23 = 'Temper'
        t_146: 'Sequence4[str1]' = ('temper',)
        this_0.aliases_24 = t_146
        t_148: 'Sequence4[str1]' = ('*.temper',)
        this_0.filenames_25 = t_148
        t_348: 'MappingProxyType9[str1, (Sequence4[RuleOption])]' = map_constructor_359((pair_358('root', (include_15('commentsandwhitespace'), Rule(words_7('false', 'NaN', 'null', 'true', 'void'), Kind.keyword_constant), Rule(words_7('class', 'interface', 'let', 'private', 'public', 'sealed', 'var'), Kind.keyword_declaration), Rule(words_7('do', 'else', 'export', 'extends', 'fn', 'if', 'import', 'is', 'when', 'new', 'orelse'), Kind.keyword), Rule(words_7('return', 'yield'), Kind.keyword, 'slashstartsregex'), Rule(words_7('AnyValue', 'Boolean', 'Bubble', 'Float64', 'Function', 'Int', 'List', 'ListBuilder', 'Listed', 'Map', 'MapBuilder', 'MapKey', 'Mapped', 'Null', 'String', 'StringIndex', 'Void'), Kind.name_builtin), Rule('(?<=\\brgx)"', Kind.string_regex, 'stringregex'), Rule('"""', Kind.string_plain, 'stringmulti'), Rule('"', Kind.string_plain, 'string'), Rule('[-=+*&|<>]+|/=?', Kind.operator, 'slashstartsregex'), Rule('[{}();:.,]', Kind.punctuation, 'slashstartsregex'), Rule('\\d+\\.?\\d*|\\.\\d+', Kind.number), Rule('@[_<<Lu>><<Ll>>][_<<Lu>><<Ll>>0-9]*', Kind.name_decorator), Rule('[_<<Lu>><<Ll>>][_<<Lu>><<Ll>>0-9]*', Kind.name_kind))), pair_358('commentsandwhitespace', (Rule('\\s+', Kind.whitespace), Rule('//.*?$', Kind.comment_singleline), Rule('/\\*', Kind.comment_multiline, 'nestedcomment'))), pair_358('nestedcomment', (Rule('[^*/]+', Kind.comment_multiline), Rule('/\\*', Kind.comment_multiline, '#push'), Rule('\\*/', Kind.comment_multiline, '#pop'), Rule('[*/]', Kind.comment_multiline))), pair_358('slashstartsregex', (include_15('commentsandwhitespace'), Rule('/(\\\\.|[^[/\\\\\\n]|\\[(\\\\.|[^\\]\\\\\\n])*])+/([gimuysd]+\\b|\\B)', Kind.string_regex, '#pop'), default_13('#pop'))), pair_358('interpolation', (Rule('}', Kind.string_interpol, '#pop'), include_15('root'))), stringish_6('string', Kind.string_plain), pair_358('stringline', (Rule('\\$\\{', Kind.string_interpol, 'interpolation'), Rule('.+', Kind.string_plain), Rule('$', Kind.string_plain, '#pop'))), pair_358('stringmulti', (include_15('commentsandwhitespace'), Rule('"', Kind.string_plain, 'stringline'), Rule('(?=.)', Kind.string_plain, '#pop'))), stringish_6('stringregex', Kind.string_regex)))
        this_0.tokens_26 = t_348
    @property
    def name(this_46) -> 'str1':
        return this_46.name_23
    @property
    def aliases(this_49) -> 'Sequence4[str1]':
        return this_49.aliases_24
    @property
    def filenames(this_52) -> 'Sequence4[str1]':
        return this_52.filenames_25
    @property
    def tokens(this_55) -> 'MappingProxyType9[str1, (Sequence4[RuleOption])]':
        return this_55.tokens_26
class TemperMdLexer:
    name_34: 'str1'
    aliases_35: 'Sequence4[str1]'
    filenames_36: 'Sequence4[str1]'
    tokens_37: 'MappingProxyType9[str1, (Sequence4[RuleOption])]'
    __slots__ = ('name_34', 'aliases_35', 'filenames_36', 'tokens_37')
    def __init__(this_4) -> None:
        this_4.name_34 = 'TemperMarkdown'
        t_131: 'Sequence4[str1]' = ('temper.md', 'tempermd')
        this_4.aliases_35 = t_131
        t_133: 'Sequence4[str1]' = ('*.temper.md', '*.tempermd')
        this_4.filenames_36 = t_133
        t_289: 'MappingProxyType9[str1, (Sequence4[RuleOption])]' = map_constructor_359((pair_358('root', (Rule('^\\s*\\n {4}', Kind.whitespace, 'indented'), inherit_22)), pair_358('indented', (Rule('(?s)(.*?)(?=\\Z|\\n(?: {1,3}[^ ]|[^ ]|$))', bygroups_19((using_21('Temper'),)), '#pop'),))))
        this_4.tokens_37 = t_289
    @property
    def name(this_58) -> 'str1':
        return this_58.name_34
    @property
    def aliases(this_61) -> 'Sequence4[str1]':
        return this_61.aliases_35
    @property
    def filenames(this_64) -> 'Sequence4[str1]':
        return this_64.filenames_36
    @property
    def tokens(this_67) -> 'MappingProxyType9[str1, (Sequence4[RuleOption])]':
        return this_67.tokens_37
def words_7(*names_31: 'str1') -> 'str1':
    def fn_355(x_33: 'str1') -> 'str1':
        return x_33
    return str_cat_360('\\', 'b(?:', list_join_361(names_31, '|', fn_355), ')', '\\', 'b')
def stringish_6(key_28: 'str1', kind_29: 'TokenKind') -> 'Pair5[str1, (Sequence4[RuleOption])]':
    t_353: 'Sequence4[RuleOption]' = (Rule('"', kind_29, '#pop'), Rule('\\$\\{', Kind.string_interpol, 'interpolation'), Rule('(?:[^"$]|\\$[^{])+', kind_29))
    return pair_358(key_28, t_353)
