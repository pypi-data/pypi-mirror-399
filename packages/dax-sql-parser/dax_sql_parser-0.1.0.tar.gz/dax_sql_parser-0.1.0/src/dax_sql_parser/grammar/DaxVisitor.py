# Generated from Dax.g4 by ANTLR 4.13.2
from antlr4 import *

if "." in __name__:
    from .DaxParser import DaxParser
else:
    from DaxParser import DaxParser

# This class defines a complete generic visitor for a parse tree produced by DaxParser.


class DaxVisitor(ParseTreeVisitor):
    # Visit a parse tree produced by DaxParser#query.
    def visitQuery(self, ctx: DaxParser.QueryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#orderClause.
    def visitOrderClause(self, ctx: DaxParser.OrderClauseContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#orderExpression.
    def visitOrderExpression(self, ctx: DaxParser.OrderExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#expression.
    def visitExpression(self, ctx: DaxParser.ExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#varExpression.
    def visitVarExpression(self, ctx: DaxParser.VarExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#logicalOr.
    def visitLogicalOr(self, ctx: DaxParser.LogicalOrContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#logicalAnd.
    def visitLogicalAnd(self, ctx: DaxParser.LogicalAndContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#equality.
    def visitEquality(self, ctx: DaxParser.EqualityContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#relational.
    def visitRelational(self, ctx: DaxParser.RelationalContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#additive.
    def visitAdditive(self, ctx: DaxParser.AdditiveContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#multiplicative.
    def visitMultiplicative(self, ctx: DaxParser.MultiplicativeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#unary.
    def visitUnary(self, ctx: DaxParser.UnaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#primaryExpression.
    def visitPrimaryExpression(self, ctx: DaxParser.PrimaryExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#tableExpression.
    def visitTableExpression(self, ctx: DaxParser.TableExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#functionCall.
    def visitFunctionCall(self, ctx: DaxParser.FunctionCallContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#functionName.
    def visitFunctionName(self, ctx: DaxParser.FunctionNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#argumentList.
    def visitArgumentList(self, ctx: DaxParser.ArgumentListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#columnReference.
    def visitColumnReference(self, ctx: DaxParser.ColumnReferenceContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#tableReference.
    def visitTableReference(self, ctx: DaxParser.TableReferenceContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#literal.
    def visitLiteral(self, ctx: DaxParser.LiteralContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#constructor.
    def visitConstructor(self, ctx: DaxParser.ConstructorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by DaxParser#constructorRow.
    def visitConstructorRow(self, ctx: DaxParser.ConstructorRowContext):
        return self.visitChildren(ctx)


del DaxParser
