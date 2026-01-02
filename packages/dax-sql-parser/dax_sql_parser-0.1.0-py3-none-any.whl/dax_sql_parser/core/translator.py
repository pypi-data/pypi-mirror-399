import logging
from typing import Any, cast

import sqlglot.expressions as exp

from .ast import (
    BinaryExpression,
    ColumnReference,
    FunctionCall,
    Literal,
    Node,
    OrderExpression,
    Query,
    TableReference,
    UnaryExpression,
    VarDeclaration,
)
from .dialects.base import BaseDialect
from .dialects.common import get_common_mappings
from .dialects.registry import DialectRegistry
from .exceptions import DaxError, DaxTranslationError
from .metadata import MetadataResolver

logger = logging.getLogger(__name__)


class DaxToSqlTranslator:
    def __init__(
        self,
        dialect: str | BaseDialect = "trino",
        schema_mapping: dict[str, str] | None = None,
        metadata: MetadataResolver | None = None,
    ):
        if isinstance(dialect, str):
            self.dialect_obj = DialectRegistry.get(dialect)
        else:
            self.dialect_obj = dialect

        self.dialect = self.dialect_obj.name
        self.schema_mapping = schema_mapping or {}
        self.metadata = metadata or MetadataResolver()
        self.mappings = self._get_dialect_mappings()
        self.type_mapping = self.dialect_obj.type_mapping
        self._variable_scope: set[str] = set()
        self._tables_in_query: set[str] = set()
        logger.debug(f"Initialized DaxToSqlTranslator with dialect={dialect}")

    def _get_dialect_mappings(self) -> dict[str, Any]:
        """Returns a mapping of DAX function names (uppercase) to SQLGlot expression builders."""
        common = get_common_mappings()
        dialect_specific = self.dialect_obj.get_function_mappings()
        return {**common, **dialect_specific}

    def translate(self, node: Node) -> str:
        logger.info(f"Starting translation of DAX node: {node.node_type}")
        expression = self.visit(node)

        # Recursive Join Injection
        if isinstance(expression, exp.Expression):
            self._inject_joins_recursive(expression)
            sql = expression.sql(dialect=self.dialect_obj.sqlglot_dialect)
            logger.debug(f"Translated SQL: {sql}")
            return sql
        return str(expression)

    def _inject_joins_recursive(self, expression: exp.Expression) -> None:
        """Recursively finds all Select nodes and injects missing joins."""
        if not self.metadata or not self.metadata.relationships:
            return

        for select_node in expression.find_all(exp.Select):
            # 1. Collect all table names already present in FROM or JOINs
            current_tables_upper = set()

            # Use a more direct way to find Tables that are actually in the FROM/JOIN of THIS select
            for table in select_node.find_all(exp.Table):
                # Check if this table is directly in FROM or JOIN of THIS select
                parent_from = table.find_ancestor(exp.From)
                parent_join = table.find_ancestor(exp.Join)
                # Ensure these ancestors belong to our select_node
                if (parent_from and parent_from.parent is select_node) or (
                    parent_join and parent_join.parent is select_node
                ):
                    current_tables_upper.add(table.name.upper())

            # 2. Collect all tables mentioned in Columns (local scope)
            mentioned_tables_upper = set()
            for col in select_node.find_all(exp.Column):
                p = col.parent
                while p and not isinstance(p, exp.Select):
                    p = p.parent
                if p is select_node and col.table:
                    if col.table not in self._variable_scope:
                        mentioned_tables_upper.add(col.table.upper())

            # 3. Inject joins
            discovery_set = mentioned_tables_upper.union(current_tables_upper)
            joins_to_inject = self.metadata.get_joins(discovery_set)

            for rel in joins_to_inject:
                if (
                    rel.to_table.upper() not in current_tables_upper
                    and rel.to_table not in self._variable_scope
                ):
                    on_condition = exp.condition(
                        exp.EQ(
                            this=exp.column(rel.from_column, table=rel.from_table, quoted=True),
                            expression=exp.column(rel.to_column, table=rel.to_table, quoted=True),
                        )
                    )
                    select_node.join(
                        exp.Table(this=exp.to_identifier(rel.to_table, quoted=True)),
                        on=on_condition,
                        join_type="INNER",
                        copy=False,
                    )
                    current_tables_upper.add(rel.to_table.upper())

    def visit(self, node: Node) -> exp.Expression | str | list[exp.Expression]:
        method_name = f"visit_{node.node_type}"
        if hasattr(node.node_type, "value"):
            method_name = f"visit_{node.node_type.value}"

        # 1. Try dialect-specific visitor first
        visitor = self.dialect_obj.get_custom_visitor(
            node.node_type.value if hasattr(node.node_type, "value") else node.node_type
        )
        if visitor:
            return cast(exp.Expression | str | list[exp.Expression], visitor(self, node))

        # 2. Try translator visitor
        visitor_callable = getattr(self, method_name, self.generic_visit)
        try:
            return cast(exp.Expression | str | list[exp.Expression], visitor_callable(node))
        except DaxError:
            raise
        except Exception as e:
            raise DaxTranslationError(
                f"Error visiting {node.node_type}: {e!s}",
                line=node.line,
                column=node.column,
                start_offset=node.start_offset,
                end_offset=node.end_offset,
            ) from e

    def generic_visit(self, node: Node) -> Any:
        raise DaxTranslationError(
            f"Translation not implemented for {node.node_type}",
            line=node.line,
            column=node.column,
            start_offset=node.start_offset,
            end_offset=node.end_offset,
        )

    def visit_Query(self, node: Query) -> exp.Expression:
        # EVALUATE -> SELECT * FROM (table expr)
        self._tables_in_query = set()
        relation = self.visit(node.evaluate_expression)

        # If relation is just a string/identifier (Table Name), wrap in SELECT *
        if isinstance(relation, exp.Table):
            relation = exp.select("*").from_(cast(exp.Table, relation))

        # Handle ORDER BY
        if node.order_by:
            if not isinstance(relation, exp.Select):
                relation = exp.select("*").from_(cast(exp.Expression | str, relation))

            for oe in node.order_by.expressions:
                sort_item = cast(exp.Expression, self.visit(oe))
                relation = relation.order_by(sort_item)

        return cast(exp.Expression, relation)

    def visit_OrderExpression(self, node: OrderExpression) -> exp.Ordered:
        # returns exp.Ordered
        expr = self.visit(node.expression)
        desc = node.direction.upper() == "DESC"
        return exp.Ordered(this=expr, desc=desc)

    def visit_TableReference(self, node: TableReference) -> exp.Table | exp.Column:
        # If it's a known variable, it might be used as a table OR a scalar.
        if node.name in self._variable_scope:
            return exp.to_table(node.name, quoted=True)

        self._tables_in_query.add(node.name)

        table_path = self.schema_mapping.get(node.name, node.name)
        return self.dialect_obj.translate_table_reference(table_path)

    def visit_ColumnReference(self, node: ColumnReference) -> exp.Column:
        # 'Table'[Column] -> "Table"."Column"
        # [Column] -> "Column" (Resolve via metadata if possible)
        table_name = node.table_name
        if not table_name:
            # Try to resolve via metadata
            resolved_table = self.metadata.resolve_column(node.column_name)
            if resolved_table:
                table_name = resolved_table

        col = exp.to_column(node.column_name, quoted=True)
        if table_name:
            self._tables_in_query.add(table_name)
            col.set("table", exp.to_identifier(table_name, quoted=True))
        return col

    def visit_Literal(self, node: Literal) -> exp.Expression:
        if node.type_name == "STRING":
            return exp.Literal.string(node.value)
        if node.type_name == "NUMBER":
            return exp.Literal.number(node.value)
        if node.type_name == "BOOLEAN":
            return exp.Boolean(this=node.value)
        if node.type_name == "BLANK":
            return exp.Null()
        if node.type_name == "KEYWORD":
            # ASC/DESC passed as args
            return exp.Var(this=node.value)
        return exp.Literal.string(str(node.value))  # Fallback

    def visit_BinaryExpression(self, node: BinaryExpression) -> exp.Expression:
        left = self.visit(node.left)
        right = self.visit(node.right)

        # 1. COERCE Table to Scalar Subquery if it's a known variable
        if isinstance(left, exp.Table) and left.name in self._variable_scope:
            left = exp.select("value").from_(left).subquery()
        elif isinstance(left, exp.Table):
            left = exp.to_column(left.this)

        if isinstance(right, exp.Table) and right.name in self._variable_scope:
            right = exp.select("value").from_(right).subquery()
        elif isinstance(right, exp.Table):
            right = exp.to_column(right.this)

        # 2. TYPE CAST LITERALS based on Column Metadata
        # If one side is a column and other is a literal, try to match types
        if isinstance(left, exp.Column) and isinstance(right, exp.Literal):
            right = self._cast_literal_to_column(right, left)
        elif isinstance(right, exp.Column) and isinstance(left, exp.Literal):
            left = self._cast_literal_to_column(left, right)

        op = node.operator
        if op in self.dialect_obj.binary_ops:
            return self.dialect_obj.binary_ops[op](left, right)

        raise NotImplementedError(f"Binary op {op} not implemented")

    def _cast_literal_to_column(self, literal: exp.Literal, column: exp.Column) -> exp.Expression:
        """Heuristically cast a literal to match a column's metadata type."""
        table_name = column.table
        col_name = column.this.name

        t_meta = self.metadata.tables.get(table_name.upper() if table_name else "")
        if t_meta:
            col_meta = t_meta.columns.get(col_name.upper())
            if col_meta:
                target_type = col_meta.data_type.lower()
                if target_type in self.type_mapping:
                    return exp.Cast(
                        this=literal, to=exp.DataType.build(target_type, dialect=self.dialect)
                    )

        return literal

    def visit_UnaryExpression(self, node: UnaryExpression) -> exp.Expression:
        # +, -, !
        # NOT -> Not
        operand = self.visit(node.operand)
        if node.operator == "!":
            return exp.Not(this=operand)
        if node.operator == "-":
            return exp.Neg(this=cast(exp.Expression, operand))
        return cast(exp.Expression, operand)  # Ignore +

    def visit_FunctionCall(self, node: FunctionCall) -> exp.Expression:
        name = node.function_name.upper()

        # 1. Handle FILTER specifically as it's a common pattern
        if name == "FILTER":
            if len(node.arguments) < 2:  # noqa: PLR2004
                raise DaxTranslationError(
                    f"FILTER function requires 2 arguments, got {len(node.arguments)}"
                )
            source = self.visit(node.arguments[0])
            condition = self.visit(node.arguments[1])

            if not isinstance(condition, (exp.Expression, str)) or isinstance(condition, list):
                # Should not happen with current grammar but for type safety
                raise DaxTranslationError(
                    f"FILTER condition must be a scalar, got {type(condition)}"
                )

            if isinstance(source, exp.Table):
                return exp.select("*").from_(source).where(cast(Any, condition))
            elif isinstance(source, exp.Select):
                return (
                    exp.select("*")
                    .from_(source.subquery("filter_subq"))
                    .where(cast(Any, condition))
                )
            else:
                # It might be another expression that returns a table
                return (
                    exp.select("*")
                    .from_(cast(exp.Expression | str, source))
                    .where(cast(Any, condition))
                )

        handler = self.dialect_obj.get_table_handler(name)
        if handler:
            return handler(self, node.arguments)

        # 3. Check for dialect-specific or common scalar mappings
        if name in self.mappings:
            args = [self.visit(a) for a in node.arguments]
            return cast(exp.Expression, self.mappings[name](args))

        # 4. Fallback: Generic Anonymous function
        args = [self.visit(a) for a in node.arguments]
        return exp.Anonymous(this=name, expressions=args)

    def visit_VarDeclaration(self, node: VarDeclaration) -> exp.Expression:
        # VAR x = Expr  RETURN Body
        # Map to: WITH x AS (SELECT Expr AS value) Body

        name = node.name
        old_scope = self._variable_scope.copy()
        self._variable_scope.add(name)

        try:
            initializer = self.visit(node.initializer)

            # If initializer is just an expression (scalar), wrap it in a SELECT
            # so it can be a CTE. In DAX, vars can be tables or scalars.
            # If it's already a Select (e.g. from FILTER), use it as is.
            cte_query: exp.Query
            if isinstance(initializer, exp.Table):
                cte_query = exp.select("*").from_(initializer)
            elif not isinstance(initializer, exp.Query):
                cte_query = exp.select(
                    exp.Alias(
                        this=cast(exp.Expression, initializer),
                        alias=exp.to_identifier("value", quoted=True),
                    )
                )
            else:
                cte_query = cast(exp.Query, initializer)

            body = self.visit(node.body)

            # Ensure body is a Query so we can attach the WITH clause
            if isinstance(body, exp.Table):
                # If body is just a table reference (the variable itself or another table),
                # wrap in SELECT * FROM
                body = exp.select("*").from_(body)
            elif not isinstance(body, exp.Query):
                # If it's a scalar expression, wrap in SELECT
                body = exp.select(cast(exp.Expression, body))

            # Attach CTE
            # SQLGlot's .with_ adds to the existing WITH clause if present
            return cast(exp.Expression, body.with_(name, as_=cte_query))
        finally:
            self._variable_scope = old_scope
