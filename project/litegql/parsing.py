import antlr4

from project.litegql.grammar.LiteGQLLexer import LiteGQLLexer
from project.litegql.grammar.LiteGQLParser import LiteGQLParser


def check(inp: str) -> bool:
    chars = antlr4.InputStream(inp)
    lexer = LiteGQLLexer(chars)
    tokens = antlr4.CommonTokenStream(lexer)
    parser = LiteGQLParser(tokens)
    parser.removeErrorListeners()
    parser.prog()
    return parser.getNumberOfSyntaxErrors() == 0
