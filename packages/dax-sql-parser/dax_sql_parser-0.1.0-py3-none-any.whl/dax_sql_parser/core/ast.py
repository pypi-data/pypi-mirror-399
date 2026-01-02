import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class NodeType(str, Enum):
    QUERY = "Query"
    TABLE_EXPRESSION = "TableExpression"
    COLUMN_REFERENCE = "ColumnReference"
    TABLE_REFERENCE = "TableReference"
    LITERAL = "Literal"
    FUNCTION_CALL = "FunctionCall"
    BINARY_EXPRESSION = "BinaryExpression"
    UNARY_EXPRESSION = "UnaryExpression"
    ORDER_CLAUSE = "OrderClause"
    ORDER_EXPRESSION = "OrderExpression"
    VAR_DECLARATION = "VarDeclaration"


@dataclass(kw_only=True)
class Node:
    """Base class for all AST nodes."""

    line: int | None = None
    column: int | None = None
    start_offset: int | None = None
    end_offset: int | None = None

    @property
    def node_type(self) -> NodeType:
        """The type of the node."""
        raise NotImplementedError("Subclasses must implement node_type")

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary for JSON serialization."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass(kw_only=True)
class Expression(Node):
    pass


@dataclass(kw_only=True)
class Literal(Expression):
    value: Any
    type_name: str  # 'STRING', 'NUMBER', 'BOOLEAN', 'BLANK'
    node_type: NodeType = NodeType.LITERAL


@dataclass(kw_only=True)
class Reference(Expression):
    pass


@dataclass(kw_only=True)
class TableReference(Reference):
    name: str
    node_type: NodeType = NodeType.TABLE_REFERENCE


@dataclass(kw_only=True)
class ColumnReference(Reference):
    column_name: str
    table_name: str | None = None
    node_type: NodeType = NodeType.COLUMN_REFERENCE

    def __str__(self) -> str:
        if self.table_name:
            return f"'{self.table_name}'[{self.column_name}]"
        return f"[{self.column_name}]"


@dataclass(kw_only=True)
class FunctionCall(Expression):
    function_name: str
    arguments: list[Expression] = field(default_factory=list)
    node_type: NodeType = NodeType.FUNCTION_CALL


@dataclass(kw_only=True)
class UnaryExpression(Expression):
    operator: str
    operand: Expression
    node_type: NodeType = NodeType.UNARY_EXPRESSION


@dataclass(kw_only=True)
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression
    node_type: NodeType = NodeType.BINARY_EXPRESSION


@dataclass(kw_only=True)
class VarDeclaration(Expression):
    name: str  # The variable name
    initializer: Expression  # The expression assigned to the variable
    body: Expression  # The RETURN expression or next VAR declaration
    node_type: NodeType = NodeType.VAR_DECLARATION


@dataclass(kw_only=True)
class OrderExpression(Node):
    expression: Expression
    direction: str = "ASC"  # ASC or DESC
    node_type: NodeType = NodeType.ORDER_EXPRESSION


@dataclass(kw_only=True)
class OrderClause(Node):
    expressions: list[OrderExpression]
    node_type: NodeType = NodeType.ORDER_CLAUSE


@dataclass(kw_only=True)
class Query(Node):
    evaluate_expression: Expression  # Usually a Table Expression
    order_by: OrderClause | None = None
    node_type: NodeType = NodeType.QUERY
