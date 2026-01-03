from abc import ABCMeta as ABCMeta0
from builtins import str as str1
from typing import Union as Union2, ClassVar as ClassVar3, Sequence as Sequence4
class RuleOption(metaclass = ABCMeta0):
    pass
class Rule(RuleOption):
    regex_20: 'str1'
    kind_21: 'TokenKind'
    state_22: 'Union2[str1, None]'
    __slots__ = ('regex_20', 'kind_21', 'state_22')
    def __init__(this_0, regex_24: 'str1', kind_25: 'TokenKind', state_26: 'Union2[str1, None]' = None) -> None:
        _state_26: 'Union2[str1, None]' = state_26
        this_0.regex_20 = regex_24
        this_0.kind_21 = kind_25
        this_0.state_22 = _state_26
    @property
    def regex(this_75) -> 'str1':
        return this_75.regex_20
    @property
    def kind(this_78) -> 'TokenKind':
        return this_78.kind_21
    @property
    def state(this_81) -> 'Union2[str1, None]':
        return this_81.state_22
class TokenKind(metaclass = ABCMeta0):
    pass
class Default(RuleOption):
    'Default state transition if nothing else matches.'
    state_27: 'str1'
    __slots__ = ('state_27',)
    def __init__(this_3, state_29: 'str1') -> None:
        this_3.state_27 = state_29
    @property
    def state(this_84) -> 'str1':
        return this_84.state_27
class Include(RuleOption):
    state_32: 'str1'
    __slots__ = ('state_32',)
    def __init__(this_6, state_34: 'str1') -> None:
        this_6.state_32 = state_34
    @property
    def state(this_87) -> 'str1':
        return this_87.state_32
class Inherit(RuleOption):
    __slots__ = ()
    def __init__(this_9) -> None:
        pass
class Kind(TokenKind):
    name_38: 'str1'
    comment_multiline: ClassVar3['Kind']
    comment_singleline: ClassVar3['Kind']
    keyword: ClassVar3['Kind']
    keyword_constant: ClassVar3['Kind']
    keyword_declaration: ClassVar3['Kind']
    name_kind: ClassVar3['Kind']
    name_builtin: ClassVar3['Kind']
    name_decorator: ClassVar3['Kind']
    number: ClassVar3['Kind']
    operator: ClassVar3['Kind']
    punctuation: ClassVar3['Kind']
    string_plain: ClassVar3['Kind']
    string_regex: ClassVar3['Kind']
    string_interpol: ClassVar3['Kind']
    whitespace: ClassVar3['Kind']
    __slots__ = ('name_38',)
    def __init__(this_11, name_55: 'str1') -> None:
        this_11.name_38 = name_55
    @property
    def name(this_90) -> 'str1':
        return this_90.name_38
Kind.comment_multiline = Kind('Comment.Multiline')
Kind.comment_singleline = Kind('Comment.Singleline')
Kind.keyword = Kind('Keyword')
Kind.keyword_constant = Kind('Keyword.Constant')
Kind.keyword_declaration = Kind('Keyword.Declaration')
Kind.name_kind = Kind('Name')
Kind.name_builtin = Kind('Name.Builtin')
Kind.name_decorator = Kind('Name.Decorator')
Kind.number = Kind('Number')
Kind.operator = Kind('Operator')
Kind.punctuation = Kind('Punctuation')
Kind.string_plain = Kind('String')
Kind.string_regex = Kind('String.Regex')
Kind.string_interpol = Kind('String.Interpol')
Kind.whitespace = Kind('Whitespace')
class ByGroups(TokenKind):
    kinds_56: 'Sequence4[TokenKind]'
    __slots__ = ('kinds_56',)
    def __init__(this_13, kinds_58: 'Sequence4[TokenKind]') -> None:
        this_13.kinds_56 = kinds_58
    @property
    def kinds(this_93) -> 'Sequence4[TokenKind]':
        return this_93.kinds_56
class Using(TokenKind):
    lexer_61: 'str1'
    __slots__ = ('lexer_61',)
    def __init__(this_17, lexer_63: 'str1') -> None:
        this_17.lexer_61 = lexer_63
    @property
    def lexer(this_96) -> 'str1':
        return this_96.lexer_61
def default(state_30: 'str1') -> 'Default':
    return Default(state_30)
def include(state_35: 'str1') -> 'Include':
    return Include(state_35)
inherit: 'Inherit' = Inherit()
def bygroups(kinds_59: 'Sequence4[TokenKind]') -> 'ByGroups':
    return ByGroups(kinds_59)
def using(lexer_64: 'str1') -> 'Using':
    return Using(lexer_64)
