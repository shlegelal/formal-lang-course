import sys
from pathlib import Path

from project.interpretator.parser import parse
from project.interpretator.visitor import InterpretVisitor


def GQLang(path):
    program = read_script(filename=Path(path))

    return interpret(program)


def interpret(text: str):
    parser = parse(text)
    tree = parser.prog()
    if parser.getNumberOfSyntaxErrors() > 0:
        raise ValueError("broken parser")

    visitor = InterpretVisitor()
    visitor.visit(tree)


def read_script(filename: Path) -> str:
    script = filename.open()

    if not filename.name.endswith(".gql"):
        raise FileNotFoundError()

    return "".join(script.readlines())
