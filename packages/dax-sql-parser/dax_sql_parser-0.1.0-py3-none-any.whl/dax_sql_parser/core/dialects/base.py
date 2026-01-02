from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, cast

import sqlglot.expressions as exp

from ..ast import ColumnReference, FunctionCall, Literal, Node, TableReference


class BaseDialect(ABC):
    """
    Base class for all SQL dialects supported by the DAX parser.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the dialect (e.g., 'trino', 'snowflake')."""
        pass

    @property
    def sqlglot_dialect(self) -> str:
        """
        The corresponding sqlglot dialect name.
        Defaults to the dialect name if not overridden.
        """
        return self.name

    @property
    @abstractmethod
    def type_mapping(self) -> dict[str, exp.DataType.Type]:
        """
        Mapping of DAX types to SQLGlot types for this dialect.
        """
        pass

    @abstractmethod
    def get_function_mappings(self) -> dict[str, Callable[[list[exp.Expression]], exp.Expression]]:
        """
        Returns a mapping of DAX function names (uppercase) to SQLGlot expression builders.
        """
        pass

    def get_custom_visitor(self, node_type: str) -> Callable[..., Any] | None:
        """
        Returns a custom visitor method for a specific DAX node type if implemented by the dialect.
        """
        method_name = f"visit_{node_type}"
        return getattr(self, method_name, None)

    @property
    def binary_ops(self) -> dict[str, Callable[[Any, Any], exp.Expression]]:
        """
        Mapping of DAX binary operators to SQLGlot expression builders.
        """
        return {
            "&&": lambda left, right: exp.And(this=left, expression=right),
            "||": lambda left, right: exp.Or(this=left, expression=right),
            "=": lambda left, right: exp.EQ(this=left, expression=right),
            "==": lambda left, right: exp.EQ(this=left, expression=right),
            "<>": lambda left, right: exp.NEQ(this=left, expression=right),
            ">": lambda left, right: exp.GT(this=left, expression=right),
            ">=": lambda left, right: exp.GTE(this=left, expression=right),
            "<": lambda left, right: exp.LT(this=left, expression=right),
            "<=": lambda left, right: exp.LTE(this=left, expression=right),
            "+": lambda left, right: exp.Add(this=left, expression=right),
            "-": lambda left, right: exp.Sub(this=left, expression=right),
            "*": lambda left, right: exp.Mul(this=left, expression=right),
            "/": lambda left, right: exp.Div(this=left, expression=right),
            "&": lambda left, right: exp.Concat(expressions=[left, right]),
            "IN": lambda left, right: exp.In(
                this=left, expressions=[right] if not isinstance(right, list) else right
            ),
        }

    def get_table_handler(self, name: str) -> Callable[..., exp.Expression] | None:
        """
        Returns a specialized handler for a DAX table function.
        """
        method_name = f"_translate_{name.upper()}"
        return getattr(self, method_name, None)

    def translate_table_reference(self, table_path: str) -> exp.Table:
        """
        Translates a table path string into a SQLGlot Table expression.
        Default implementation handles 1, 2, and 3 part names.
        """
        parts = table_path.split(".")
        if len(parts) == 3:  # noqa: PLR2004
            return exp.Table(
                this=exp.to_identifier(parts[2], quoted=True),
                db=exp.to_identifier(parts[1], quoted=True),
                catalog=exp.to_identifier(parts[0], quoted=True),
            )
        elif len(parts) == 2:  # noqa: PLR2004
            return exp.Table(
                this=exp.to_identifier(parts[1], quoted=True),
                db=exp.to_identifier(parts[0], quoted=True),
            )

        return exp.to_table(table_path, quoted=True)

    def _translate_SUMMARIZE(self, translator: Any, args: list[Node]) -> exp.Expression:
        source = translator.visit(args[0])
        group_cols = []
        aggregations = []

        i = 1
        while i < len(args):
            arg = args[i]
            if isinstance(arg, Literal) and arg.type_name == "STRING":
                col_name = arg.value
                expr = translator.visit(args[i + 1])
                aggregations.append(
                    exp.Alias(this=expr, alias=exp.to_identifier(col_name, quoted=True))
                )
                i += 2
            else:
                col_expr = translator.visit(arg)
                group_cols.append(col_expr)
                i += 1

        projection = group_cols + aggregations
        return exp.select(*projection).from_(source).group_by(*group_cols)

    def _translate_ADDCOLUMNS(self, translator: Any, args: list[Node]) -> exp.Expression:
        source = translator.visit(args[0])
        extensions = []
        i = 1
        while i < len(args):
            name_arg = args[i]
            col_name = getattr(name_arg, "value", str(name_arg))
            expr = translator.visit(args[i + 1])
            extensions.append(exp.Alias(this=expr, alias=exp.to_identifier(col_name, quoted=True)))
            i += 2

        if isinstance(source, exp.Table):
            return exp.select(exp.Star(), *extensions).from_(source)
        else:
            return exp.select(exp.Star(), *extensions).from_(source.subquery("addcol_subq"))

    def _translate_SELECTCOLUMNS(self, translator: Any, args: list[Node]) -> exp.Expression:
        source = translator.visit(args[0])
        projection = []
        i = 1
        while i < len(args):
            name_arg = args[i]
            col_name = getattr(name_arg, "value", str(name_arg))
            expr = translator.visit(args[i + 1])
            projection.append(exp.Alias(this=expr, alias=exp.to_identifier(col_name, quoted=True)))
            i += 2
        return exp.select(*projection).from_(cast(Any, source))

    def _translate_ROW(self, translator: Any, args: list[Node]) -> exp.Expression:
        projection = []
        i = 0
        while i < len(args):
            name_arg = args[i]
            col_name = getattr(name_arg, "value", str(name_arg))
            expr = translator.visit(args[i + 1])
            projection.append(exp.Alias(this=expr, alias=exp.to_identifier(col_name, quoted=True)))
            i += 2
        return exp.select(*projection)

    def _translate_TABLE_CONSTRUCTOR(self, translator: Any, args: list[Node]) -> exp.Expression:
        rows = []
        for arg_row in args:
            if isinstance(arg_row, FunctionCall) and arg_row.function_name.upper() == "ROW":
                row_values = [translator.visit(a) for a in arg_row.arguments]
                rows.append(exp.Tuple(expressions=row_values))
            else:
                rows.append(exp.Tuple(expressions=[translator.visit(arg_row)]))
        return exp.Values(expressions=rows)

    def _translate_CALCULATE(self, translator: Any, args: list[Node]) -> exp.Expression:
        expression = translator.visit(args[0])
        if len(args) == 1:
            return cast(exp.Expression, expression)

        conditions = [translator.visit(a) for a in args[1:]]
        combined_filter = exp.and_(*conditions)

        if isinstance(expression, exp.Select):
            return expression.where(combined_filter)
        return exp.select(expression).where(combined_filter)

    def _translate_CALCULATETABLE(self, translator: Any, args: list[Node]) -> exp.Expression:
        source = translator.visit(args[0])
        if len(args) > 1:
            conditions = [translator.visit(a) for a in args[1:]]
            combined_filter = exp.and_(*conditions)
            if isinstance(source, exp.Table):
                return exp.select("*").from_(source).where(combined_filter)
            else:
                return exp.select("*").from_(source.subquery("calc_subq")).where(combined_filter)
        return cast(exp.Expression, source)

    def _translate_TOPN(self, translator: Any, args: list[Node]) -> exp.Expression:
        n_val = translator.visit(args[0])
        source = translator.visit(args[1])
        query = (
            exp.select("*").from_(source)
            if isinstance(source, exp.Table)
            else exp.select("*").from_(source.subquery("topn_subq"))
        )
        if len(args) > 2:  # noqa: PLR2004
            order_expr = translator.visit(args[2])
            is_desc = True
            if len(args) > 3:  # noqa: PLR2004
                dir_node = args[3]
                if isinstance(dir_node, Literal) and dir_node.value == "ASC":
                    is_desc = False
            query = query.order_by(exp.Ordered(this=order_expr, desc=is_desc))
        return query.limit(n_val.this if isinstance(n_val, exp.Literal) else n_val)

    def _translate_DISTINCT(self, translator: Any, args: list[Node]) -> exp.Expression:
        arg = args[0]
        if isinstance(arg, ColumnReference):
            col = translator.visit(arg)
            if not arg.table_name:
                raise ValueError("DISTINCT on column requires fully qualified name or context")
            return exp.select(col).distinct().from_(exp.to_table(arg.table_name, quoted=True))
        elif isinstance(arg, TableReference):
            return exp.select("*").distinct().from_(translator.visit(arg))
        raise NotImplementedError("DISTINCT on expression not supported")

    def _translate_VALUES(self, translator: Any, args: list[Node]) -> exp.Expression:
        return self._translate_DISTINCT(translator, args)

    def _translate_GENERATE(self, translator: Any, args: list[Node]) -> exp.Expression:
        t1 = translator.visit(args[0])
        t2 = translator.visit(args[1])

        if isinstance(t1, exp.Select):
            t1 = t1.subquery("gen_source")

        q = exp.select("*").from_(t1)

        if not isinstance(t2, exp.Table):
            t2 = t2.subquery("gen_subq")

        return q.join(t2, join_type="CROSS")

    def _translate_CROSSJOIN(self, translator: Any, args: list[Node]) -> exp.Expression:
        t1 = translator.visit(args[0])
        if isinstance(t1, exp.Select):
            t1 = t1.subquery("cj_source")

        q = exp.select("*").from_(t1)
        for other in args[1:]:
            other_val = translator.visit(other)
            other_alias = (
                other_val if isinstance(other_val, exp.Table) else other_val.subquery("cj_sub")
            )
            q = q.join(other_alias, join_type="CROSS")
        return q

    def _translate_UNION(self, translator: Any, args: list[Node]) -> exp.Expression:
        return exp.union(translator.visit(args[0]), translator.visit(args[1]))

    def _translate_INTERSECT(self, translator: Any, args: list[Node]) -> exp.Expression:
        return exp.intersect(translator.visit(args[0]), translator.visit(args[1]))

    def _translate_EXCEPT(self, translator: Any, args: list[Node]) -> exp.Expression:
        return exp.except_(translator.visit(args[0]), translator.visit(args[1]))

    def _translate_NATURALINNERJOIN(self, translator: Any, args: list[Node]) -> exp.Expression:
        left = translator.visit(args[0])
        right = translator.visit(args[1])
        q = exp.select("*").from_(left)
        right_sub = right if isinstance(right, exp.Table) else right.subquery("nj_sub")
        join = exp.Join(this=right_sub, kind="INNER")
        join.set("natural", True)
        q.set("joins", [join])
        return q

    def _translate_NATURALLEFTOUTERJOIN(self, translator: Any, args: list[Node]) -> exp.Expression:
        left = translator.visit(args[0])
        right = translator.visit(args[1])
        q = exp.select("*").from_(left)
        right_sub = right if isinstance(right, exp.Table) else right.subquery("nj_sub")
        join = exp.Join(this=right_sub, kind="LEFT")
        join.set("natural", True)
        q.set("joins", [join])
        return q

    def _translate_SWITCH(self, translator: Any, args: list[Node]) -> exp.Expression:
        expr = translator.visit(args[0])
        cases = []
        i = 1
        while i + 1 < len(args):
            case_val = translator.visit(args[i])
            case_res = translator.visit(args[i + 1])
            cases.append((case_val, case_res))
            i += 2

        default = translator.visit(args[i]) if i < len(args) else exp.Null()
        return exp.Case(this=expr, ifs=[exp.If(this=v, true=r) for v, r in cases], default=default)

    def _translate_TOTALYTD(self, translator: Any, args: list[Node]) -> exp.Expression:
        # TOTALYTD(SUM(Sales[Amount]), 'Date'[Date])
        # This is often dialect-specific. Default is a placeholder.
        expr = translator.visit(args[0])
        return exp.Anonymous(this="SUM", expressions=[expr])
