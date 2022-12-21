import antlr4
import pydot

from project.GQLang.GQLangLexer import GQLangLexer
from project.GQLang.GQLangParser import GQLangParser
from project.GQLang.GQLangListener import GQLangListener

__all__ = ["parse", "check"]


def parse(text: str) -> GQLangParser:
    stream = antlr4.InputStream(text)
    lexer = GQLangLexer(stream)
    tokens = antlr4.CommonTokenStream(lexer)

    return GQLangParser(tokens)


def check(text: str) -> bool:
    parser = parse(text)
    parser.removeErrorListeners()
    parser.prog()

    return parser.getNumberOfSyntaxErrors() == 0


def save_to_dot(parser: GQLangParser, path: str):
    tree = parser.prog()
    if parser.getNumberOfSyntaxErrors() > 0:
        raise ValueError("broken parser")
    listener = DotTreeListener()
    walker = antlr4.ParseTreeWalker()
    walker.walk(listener, tree)

    if not listener.dot.write(path):
        raise RuntimeError(f"cannot save to {path}")


class DotTreeListener(GQLangListener):
    def __init__(self):
        self.dot = pydot.Dot("parsed_text", strict=True)
        self.curr = 0
        self.stack = []

    def enterEveryRule(self, ctx: antlr4.ParserRuleContext):
        self.dot.add_node(
            pydot.Node(self.curr, label=GQLangParser.ruleNames[ctx.getRuleIndex()])
        )
        if len(self.stack) > 0:
            self.dot.add_edge(pydot.Edge(self.stack[-1], self.curr))
        self.stack.append(self.curr)
        self.curr += 1

    def exitEveryRule(self, ctx: antlr4.ParserRuleContext):
        self.stack.pop()

    def visitTerminal(self, node: antlr4.TerminalNode):
        self.dot.add_node(pydot.Node(self.curr, label=f"'{node}'", shape="box"))
        self.dot.add_edge(pydot.Edge(self.stack[-1], self.curr))
        self.curr += 1
