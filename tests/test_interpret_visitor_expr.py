import pytest

from project.litegql.grammar.LiteGQLParser import LiteGQLParser
from project.litegql.interpret_visitor import InterpretVisitor
from project.litegql.types.base_type import BaseType
from project.litegql.types.lgql_bool import Bool
from project.litegql.types.lgql_cfg import Cfg
from project.litegql.types.lgql_int import Int
from project.litegql.types.lgql_pair import Pair
from project.litegql.types.lgql_reg import Reg
from project.litegql.types.lgql_string import String
from tests.test_types_cfg import assert_equivalent_boxes
from tests.testing_utils import are_equivalent  # noqa
from tests.testing_utils import expr_ctx  # noqa
from tests.testing_utils import fail


@pytest.mark.parametrize(
    "ctx, expected",
    [
        ("(true)", Bool(True)),
        ("((((1 , 2))))", Pair(Int(1), Int(2))),
        ('(("a" | "b")*)', String("a").union(String("b")).star()),
        (
            '(r"a b" | ((r"c" | (r"d")) | r"e"))',
            Reg.from_raw_str("c").union(
                Reg.from_raw_str("d").union(
                    Reg.from_raw_str("e").union(Reg.from_raw_str("a b"))
                )
            ),
        ),
        (
            '(("a" | "b") . ("c" | "d"))',
            String("a").union(String("b")).concat(String("c").union(String("d"))),
        ),
    ],
    indirect=["ctx"],
)
def test_visit_parens(ctx: LiteGQLParser.ParensContext, expected: BaseType):
    actual = InterpretVisitor(output=fail).visitParens(ctx)
    if isinstance(actual, Reg):
        assert are_equivalent(actual._nfa, expected._nfa)
    elif isinstance(actual, Cfg):
        assert actual._rsm.start == expected._rsm.start
        assert_equivalent_boxes(
            actual._rsm.boxes, expected._rsm.boxes, wrapped_expected=True
        )
    else:
        assert actual == expected


@pytest.mark.parametrize(
    "ctx, expected",
    [
        ('("a" | "b")*', String("a").union(String("b")).star()),
        (
            'map({(_, l, _) -> l}, get_edges(r"a b c"))',
            Reg.from_raw_str("a b c").get_labels(),
        ),
        (
            'get_reachables(load("skos") & "subClassOf"))',
            Reg.from_dataset("skos").intersect(String("subClassOf")).get_reachables(),
        ),
    ],
    indirect=["ctx"],
)
def test_visit_expr(ctx: LiteGQLParser.ExprContext, expected: BaseType):
    actual = InterpretVisitor(output=fail).visit(ctx)
    if isinstance(actual, Reg):
        assert are_equivalent(actual._nfa, expected._nfa)
    elif isinstance(actual, Cfg):
        assert actual._rsm.start == expected._rsm.start
        assert_equivalent_boxes(
            actual._rsm.boxes, expected._rsm.boxes, wrapped_expected=True
        )
    else:
        assert actual == expected
