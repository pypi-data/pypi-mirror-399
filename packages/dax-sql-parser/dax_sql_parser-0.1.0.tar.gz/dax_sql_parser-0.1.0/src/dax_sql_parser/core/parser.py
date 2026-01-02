from typing import Any, cast

from antlr4 import CommonTokenStream, InputStream  # type: ignore
from antlr4.error.ErrorListener import ErrorListener  # type: ignore

from ..grammar.DaxLexer import DaxLexer
from ..grammar.DaxParser import DaxParser
from ..grammar.DaxVisitor import DaxVisitor
from .ast import (
    BinaryExpression,
    ColumnReference,
    Expression,
    FunctionCall,
    Literal,
    Node,
    OrderClause,
    OrderExpression,
    Query,
    TableReference,
    UnaryExpression,
    VarDeclaration,
)
from .exceptions import DaxParsingError


class DaxErrorListener(ErrorListener):
    def syntaxError(
        self, recognizer: Any, offendingSymbol: Any, line: int, column: int, msg: str, e: Any
    ) -> None:
        start = offendingSymbol.start if offendingSymbol else None
        stop = offendingSymbol.stop if offendingSymbol else None
        raise DaxParsingError(
            f"Line {line}:{column} {msg}",
            line=line,
            column=column,
            start_offset=start,
            end_offset=stop,
        )


class DaxAstVisitor(DaxVisitor):
    def _with_pos(self, node: Node, ctx: Any) -> Node:
        """Helper to populate position info from ANTLR context."""
        if ctx:
            node.line = ctx.start.line
            node.column = ctx.start.column
            node.start_offset = ctx.start.start
            node.end_offset = ctx.stop.stop
        return node

    def visitQuery(self, ctx: DaxParser.QueryContext) -> Query:
        table_expr = cast(Expression, self.visit(ctx.tableExpression()))
        order_clause = (
            cast(OrderClause, self.visit(ctx.orderClause())) if ctx.orderClause() else None
        )
        return cast(
            Query, self._with_pos(Query(evaluate_expression=table_expr, order_by=order_clause), ctx)
        )

    def visitOrderClause(self, ctx: DaxParser.OrderClauseContext) -> OrderClause:
        expressions = [self.visit(expr) for expr in ctx.orderExpression()]
        return cast(OrderClause, self._with_pos(OrderClause(expressions=expressions), ctx))

    def visitOrderExpression(self, ctx: DaxParser.OrderExpressionContext) -> OrderExpression:
        expr = self.visit(ctx.expression())
        direction = "DESC" if ctx.DESC() else "ASC"
        return cast(
            OrderExpression,
            self._with_pos(OrderExpression(expression=expr, direction=direction), ctx),
        )

    def visitTableExpression(self, ctx: DaxParser.TableExpressionContext) -> Any:
        return self.visitChildren(ctx)

    def visitLogicalOr(self, ctx: DaxParser.LogicalOrContext) -> Expression:
        if ctx.getChildCount() == 1:
            return cast(Expression, self.visit(ctx.logicalAnd(0)))

        left = cast(Expression, self.visit(ctx.logicalAnd(0)))
        for i in range(1, len(ctx.logicalAnd())):
            right = cast(Expression, self.visit(ctx.logicalAnd(i)))
            left = cast(
                Expression,
                self._with_pos(BinaryExpression(left=left, operator="||", right=right), ctx),
            )
        return left

    def visitLogicalAnd(self, ctx: DaxParser.LogicalAndContext) -> Expression:
        if ctx.getChildCount() == 1:
            return cast(Expression, self.visit(ctx.equality(0)))

        left = cast(Expression, self.visit(ctx.equality(0)))
        for i in range(1, len(ctx.equality())):
            right = cast(Expression, self.visit(ctx.equality(i)))
            left = cast(
                Expression,
                self._with_pos(BinaryExpression(left=left, operator="&&", right=right), ctx),
            )
        return left

    def visitEquality(self, ctx: DaxParser.EqualityContext) -> Expression:
        return cast(Expression, self._visit_binary(ctx, "relational"))

    def _visit_binary(self, ctx: Any, child_rule_name: str) -> Expression:
        children_ctx = getattr(ctx, child_rule_name)()
        if not isinstance(children_ctx, list):
            children_ctx = [children_ctx]

        if len(children_ctx) == 1:
            return cast(Expression, self.visit(children_ctx[0]))

        current = cast(Expression, self.visit(children_ctx[0]))
        idx = 1
        child_count = ctx.getChildCount()

        while idx < child_count:
            op_node = ctx.getChild(idx)
            op = op_node.getText()
            right = cast(Expression, self.visit(ctx.getChild(idx + 1)))
            current = cast(
                Expression,
                self._with_pos(BinaryExpression(left=current, operator=op, right=right), ctx),
            )
            idx += 2
        return current

    def visitRelational(self, ctx: DaxParser.RelationalContext) -> Expression:
        return cast(Expression, self._visit_binary(ctx, "additive"))

    def visitAdditive(self, ctx: DaxParser.AdditiveContext) -> Expression:
        return cast(Expression, self._visit_binary(ctx, "multiplicative"))

    def visitMultiplicative(self, ctx: DaxParser.MultiplicativeContext) -> Expression:
        return cast(Expression, self._visit_binary(ctx, "unary"))

    def visitUnary(self, ctx: DaxParser.UnaryContext) -> Expression:
        if ctx.getChildCount() == 1:
            return cast(Expression, self.visit(ctx.primaryExpression()))

        op = ctx.getChild(0).getText()
        operand = cast(Expression, self.visit(ctx.unary()))
        return cast(Expression, self._with_pos(UnaryExpression(operator=op, operand=operand), ctx))

    def visitPrimaryExpression(self, ctx: DaxParser.PrimaryExpressionContext) -> Any:
        if ctx.OPEN_PAREN():
            return self.visit(ctx.expression())
        return self.visitChildren(ctx)

    def visitVarExpression(self, ctx: DaxParser.VarExpressionContext) -> VarDeclaration:
        name = ctx.IDENTIFIER().getText()
        initializer = cast(Expression, self.visit(ctx.expression(0)))

        if ctx.varExpression():
            body = cast(Expression, self.visit(ctx.varExpression()))
        else:
            body = cast(Expression, self.visit(ctx.expression(1)))

        return cast(
            VarDeclaration,
            self._with_pos(VarDeclaration(name=name, initializer=initializer, body=body), ctx),
        )

    def visitFunctionCall(self, ctx: DaxParser.FunctionCallContext) -> FunctionCall:
        func_name = cast(str, self.visit(ctx.functionName()))
        args: list[Expression] = []
        if ctx.argumentList():
            args = cast(list[Expression], self.visit(ctx.argumentList()))
        return cast(
            FunctionCall, self._with_pos(FunctionCall(function_name=func_name, arguments=args), ctx)
        )

    def visitFunctionName(self, ctx: DaxParser.FunctionNameContext) -> str:
        """
        Extract function name from functionName context.
        (IDENTIFIER, AND_KW, OR_KW, or NOT_KW).
        """
        if ctx.IDENTIFIER():
            return str(ctx.IDENTIFIER().getText())
        elif ctx.AND_KW():
            return "AND"
        elif ctx.OR_KW():
            return "OR"
        elif ctx.NOT_KW():
            return "NOT"
        return str(ctx.getText())

    def visitArgumentList(self, ctx: DaxParser.ArgumentListContext) -> list[Expression]:
        return [cast(Expression, self.visit(e)) for e in ctx.expression()]

    def visitColumnReference(self, ctx: DaxParser.ColumnReferenceContext) -> ColumnReference:
        table_name = None
        if ctx.tableReference():
            table_ref = cast(TableReference, self.visit(ctx.tableReference()))
            table_name = table_ref.name

        bracket_id = ctx.BRACKET_ID().getText()
        col_name = bracket_id[1:-1]

        return cast(
            ColumnReference,
            self._with_pos(ColumnReference(table_name=table_name, column_name=col_name), ctx),
        )

    def visitTableReference(self, ctx: DaxParser.TableReferenceContext) -> TableReference:
        text = ctx.getText()
        if text.startswith("'") and text.endswith("'"):
            name = text[1:-1].replace("''", "'")
        else:
            name = text
        return cast(TableReference, self._with_pos(TableReference(name=name), ctx))

    def visitLiteral(self, ctx: DaxParser.LiteralContext) -> Literal:
        text = ctx.getText()
        node = None
        if ctx.STRING_LITERAL():
            val = text[1:-1].replace('""', '"')
            node = Literal(value=val, type_name="STRING")
        elif ctx.NUMBER():
            try:
                val = int(text)
            except ValueError:
                val = float(text)
            node = Literal(value=val, type_name="NUMBER")
        elif ctx.TRUE():
            node = Literal(value=True, type_name="BOOLEAN")
        elif ctx.FALSE():
            node = Literal(value=False, type_name="BOOLEAN")
        elif ctx.BLANK():
            node = Literal(value=None, type_name="BLANK")
        elif ctx.ASC():
            node = Literal(value="ASC", type_name="KEYWORD")
        elif ctx.DESC():
            node = Literal(value="DESC", type_name="KEYWORD")
        else:
            node = Literal(value=text, type_name="UNKNOWN")
        return cast(Literal, self._with_pos(node, ctx))

    def visitConstructor(self, ctx: DaxParser.ConstructorContext) -> FunctionCall:
        rows = [cast(list[Expression], self.visit(r)) for r in ctx.constructorRow()]
        args: list[Expression] = []
        for row in rows:
            # We don't have the context of the row here easily,
            # but we can pass it if we change visitConstructorRow
            args.append(FunctionCall(function_name="ROW", arguments=row))
        return cast(
            FunctionCall,
            self._with_pos(FunctionCall(function_name="TABLE_CONSTRUCTOR", arguments=args), ctx),
        )

    def visitConstructorRow(self, ctx: DaxParser.ConstructorRowContext) -> list[Expression]:
        if ctx.getChildCount() == 1:
            return [self.visit(ctx.expression(0))]
        return [self.visit(e) for e in ctx.expression()]


def parse_dax(dax_code: str) -> Query:
    input_stream = InputStream(dax_code)
    lexer = DaxLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(DaxErrorListener())

    stream = CommonTokenStream(lexer)
    parser = DaxParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(DaxErrorListener())

    # Parse
    tree = parser.query()

    # Visit
    visitor = DaxAstVisitor()
    return cast(Query, visitor.visit(tree))
