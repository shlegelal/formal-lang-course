from pathlib import Path

from project.interpretator.grammar.GQLangVisitor import GQLangVisitor
from project.interpretator.grammar.GQLangParser import GQLangParser

from antlr4 import ParserRuleContext

import sys

from project.interpretator import pattern
from project.interpretator.types.automata import GQLangAutomata
from project.interpretator.types.cfg import GQLangCFG
from project.interpretator.types.fa import GQLangFA
from project.interpretator.types.pair import GQLangPair
from project.interpretator.types.set import GQLangSet
from project.interpretator.types.triple import GQLangTriple


class InterpretVisitor(GQLangVisitor):
    def __init__(self):
        self._scopes = [{}]

    def set_var(self, var: str, value):
        self._scopes[-1][var] = value

    def get_var(self, var: str):
        for scope in reversed(self._scopes):
            if var in scope:
                return scope[var]
        raise RuntimeError(f"Unknown variable: {var}")

    def add_scope(self, scope: dict):
        self._scopes.append(scope)

    def pop_scope(self):
        assert len(self._scopes) > 1  # Cannot pop the global scope
        self._scopes.pop()

    # prog
    def visitProg(self, ctx: ParserRuleContext):
        return self.visitChildren(ctx)

    # stmt
    def visitPrint(self, ctx: GQLangParser.PrintContext):
        value = self.visit(ctx.expr())
        sys.stdout.write(str(value) + "\n")

    def visitBind(self, ctx: GQLangParser.BindContext):
        name = ctx.VAR().getText()
        value = self.visit(ctx.expr())
        self.set_var(name, value)

    # expr
    def visitParens(self, ctx: GQLangParser.ParensContext):
        return self.visit(ctx.expr())

    # type
    def visitBool(self, ctx: GQLangParser.BoolContext):
        return ctx.BOOL().getText() == "true"

    def visitNot(self, ctx: GQLangParser.NotContext):
        res = self.visit(ctx.expr())
        if isinstance(res, bool):
            raise TypeError(f"Not: Expects bool, not {type(res)}")
        return not res

    def visitInt(self, ctx: GQLangParser.IntContext):
        return int(ctx.INT().getText())

    def visitString(self, ctx: GQLangParser.StringContext):
        return ctx.STRING().getText()[1:-1]

    def visitSet(self, ctx: GQLangParser.SetContext):
        vs = {self.visit(elem) for elem in ctx.expr()}
        return GQLangSet(vs)

    def visitRange(self, ctx: GQLangParser.RangeContext):
        start = int(ctx.INT(0).getText())
        end = int(ctx.INT(1).getText())
        return GQLangSet(set(range(start, end + 1)))

    def visitReg(self, ctx: GQLangParser.RegContext):
        return GQLangFA.from_str(ctx.REGEX().getText()[2:-1])

    def visitCfg(self, ctx: GQLangParser.CfgContext):
        return GQLangCFG.from_str(ctx.CFG().getText()[2:-1])

    def visitPair(self, ctx: GQLangParser.PairContext):
        fst = self.visit(ctx.expr(0))
        snd = self.visit(ctx.expr(1))
        return GQLangPair(fst, snd)

    def visitTriple(self, ctx: GQLangParser.TripleContext):
        st = self.visit(ctx.expr(0))
        lab = str(self.visit(ctx.expr(1)))
        fn = self.visit(ctx.expr(2))
        return GQLangTriple(st, lab, fn)

    # var
    def visitVar(self, ctx: GQLangParser.VarContext):
        var = ctx.VAR().getText()
        return self.get_var(var)

    # operation
    def visitContains(self, ctx: GQLangParser.ContainsContext):
        item = self.visit(ctx.expr(0))
        elems = self.visit(ctx.expr(1))
        if not isinstance(elems, GQLangSet):
            raise TypeError(f"Contains: Type elem is {type(elems)}, not GQLangSet")
        return item in elems

    def visitLoad_dot(self, ctx: GQLangParser.Load_dotContext):
        path = Path(str(self.visit(ctx.expr())))
        if path.name.startswith("cfg"):
            return GQLangCFG.from_file(path)
        else:
            return GQLangFA.from_file(path)

    def visitLoad_graph(self, ctx: GQLangParser.Load_graphContext):
        arg = str(self.visit(ctx.expr()))
        return GQLangFA.from_str(arg)

    # lambda
    def visitWildcard(self, ctx: GQLangParser.WildcardContext):
        return pattern.Wildcard()

    def visitName(self, ctx: GQLangParser.NameContext):
        return pattern.Name(ctx.VAR().getText())

    def visitUnpair(self, ctx: GQLangParser.UnpairContext):
        fst = self.visit(ctx.pattern(0))
        snd = self.visit(ctx.pattern(1))
        return pattern.Unpair(fst, snd)

    def visitUntriple(self, ctx: GQLangParser.UntripleContext):
        st = self.visit(ctx.pattern(0))
        lab = self.visit(ctx.pattern(1))
        fn = self.visit(ctx.pattern(2))
        return pattern.Untriple(st, lab, fn)

    def visitLambda(self, ctx: GQLangParser.LambdaContext):
        pat = self.visit(ctx.pattern())

        def action():
            value = self.visit(ctx.expr())
            return value

        return pat, action

    def visitMap(self, ctx: GQLangParser.MapContext):
        pat, action = self.visit(ctx.lambda_())
        elems: GQLangSet = self.visit(ctx.expr())()
        if not isinstance(elems, GQLangSet):
            raise TypeError(f"Map: Type elem is {type(elems)}, not GQLangSet")
        mapped = set()
        for elem in elems.items():
            if isinstance(elem, GQLangPair) or isinstance(elem, GQLangTriple):
                elem = elem.to_tuple
            self.add_scope(pattern.match(pat, elem))
            mapped.add(action())
            self.pop_scope()

        return GQLangSet(mapped)

    def visitFilter(self, ctx: GQLangParser.FilterContext):
        pat, action = self.visit(ctx.lambda_())
        elems: GQLangSet = self.visit(ctx.expr())
        if not isinstance(elems, GQLangSet):
            raise TypeError(f"Filter: Type elem is {type(elems)}, not GQLangSet")
        filtered = set()
        for elem in elems.items():
            if isinstance(elem, GQLangPair) or isinstance(elem, GQLangTriple):
                elem = elem.to_tuple
            self.add_scope(pattern.match(pat, elem))
            res = action()
            if not isinstance(res, bool):
                raise TypeError(
                    f"Filter: Expects lambda to return bool, got {type(res)}"
                )
            if res:
                filtered.add(elem)
            self.pop_scope()
        return GQLangSet(filtered)

    # graph
    def visitAddStarts(self, ctx: GQLangParser.AddStartsContext):
        arg1: GQLangAutomata = self.visit(ctx.expr(0))
        arg2 = self.visit(ctx.expr(1))
        return arg1.add_starts(arg2)

    def visitAddFinals(self, ctx: GQLangParser.AddFinalsContext):
        arg1: GQLangAutomata = self.visit(ctx.expr(0))
        arg2 = self.visit(ctx.expr(1))
        return arg1.add_finals(arg2)

    def visitSetStarts(self, ctx: GQLangParser.SetStartsContext):
        arg1: GQLangAutomata = self.visit(ctx.expr(0))
        arg2 = self.visit(ctx.expr(1))
        return arg1.set_starts(arg2)

    def visitSetFinals(self, ctx: GQLangParser.SetFinalsContext):
        arg1: GQLangAutomata = self.visit(ctx.expr(0))
        arg2 = self.visit(ctx.expr(1))
        return arg1.set_finals(arg2)

    def visitGetStarts(self, ctx: GQLangParser.GetStartsContext):
        arg1: GQLangAutomata = self.visit(ctx.expr())
        return arg1.starts

    def visitGetFinals(self, ctx: GQLangParser.GetFinalsContext):
        arg1: GQLangAutomata = self.visit(ctx.expr())
        return arg1.finals

    def visitGetEdges(self, ctx: GQLangParser.GetEdgesContext):
        arg1: GQLangAutomata = self.visit(ctx.expr())
        return arg1.edges

    def visitGetLabels(self, ctx: GQLangParser.GetLabelsContext):
        arg1: GQLangAutomata = self.visit(ctx.expr())
        return arg1.labels

    def visitGetNodes(self, ctx: GQLangParser.GetNodesContext):
        arg1: GQLangAutomata = self.visit(ctx.expr())
        return arg1.nodes

    def visitGetReachable(self, ctx: GQLangParser.GetReachableContext):
        arg1: GQLangAutomata = self.visit(ctx.expr())
        return arg1.reachable

    def visitConcat(self, ctx: GQLangParser.ConcatContext):
        arg1: GQLangAutomata = self.visit(ctx.expr(0))
        arg2: GQLangAutomata = self.visit(ctx.expr(1))
        return arg1.concat(arg2)

    def visitIntersect(self, ctx: GQLangParser.IntersectContext):
        arg1: GQLangAutomata = self.visit(ctx.expr(0))
        arg2: GQLangAutomata = self.visit(ctx.expr(1))
        return arg1.intersect(arg2)

    def visitUnion(self, ctx: GQLangParser.UnionContext):
        arg1: GQLangAutomata = self.visit(ctx.expr(0))
        arg2: GQLangAutomata = self.visit(ctx.expr(1))
        return arg1.union(arg2)

    def visitStar(self, ctx: GQLangParser.StarContext):
        arg1: GQLangFA = self.visit(ctx.expr())
        return arg1.star()
