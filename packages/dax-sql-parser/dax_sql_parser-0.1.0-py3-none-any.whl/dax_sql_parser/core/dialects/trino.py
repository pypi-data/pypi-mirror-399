from collections.abc import Callable

import sqlglot.expressions as exp

from .base import BaseDialect


class TrinoDialect(BaseDialect):
    """
    Trino implementation of the DAX dialect.
    """

    @property
    def name(self) -> str:
        return "trino"

    @property
    def type_mapping(self) -> dict[str, exp.DataType.Type]:
        return {
            "decimal": exp.DataType.Type.DECIMAL,
            "double": exp.DataType.Type.DOUBLE,
            "float": exp.DataType.Type.FLOAT,
            "int": exp.DataType.Type.INT,
            "integer": exp.DataType.Type.INT,
            "string": exp.DataType.Type.VARCHAR,
            "varchar": exp.DataType.Type.VARCHAR,
            "boolean": exp.DataType.Type.BOOLEAN,
            "timestamp": exp.DataType.Type.TIMESTAMP,
            "date": exp.DataType.Type.DATE,
        }

    def get_function_mappings(self) -> dict[str, Callable[[list[exp.Expression]], exp.Expression]]:
        """
        Returns Trino-specific function mappings.
        """
        return {
            "MEDIAN": lambda args: exp.Anonymous(
                this="approx_percentile", expressions=[args[0], exp.Literal.number(0.5)]
            ),
            "GEOMEAN": lambda args: exp.Anonymous(this="geometric_mean", expressions=[args[0]]),
            "STDEV.P": lambda args: exp.Anonymous(this="stddev_pop", expressions=[args[0]]),
            "STDEV.S": lambda args: exp.Anonymous(this="stddev", expressions=[args[0]]),
            "VAR.S": lambda args: exp.Anonymous(this="variance", expressions=[args[0]]),
            "VAR.P": lambda args: exp.Anonymous(this="var_pop", expressions=[args[0]]),
            "FIND": lambda args: exp.StrPosition(this=args[1], substr=args[0]),
            "SEARCH": lambda args: exp.StrPosition(this=args[1], substr=args[0]),
            "SUBSTITUTE": lambda args: exp.Anonymous(this="replace", expressions=args),
            "LEFT": lambda args: exp.Anonymous(
                this="substring", expressions=[args[0], exp.Literal.number(1), args[1]]
            ),
            "RIGHT": lambda args: exp.Anonymous(
                this="substring",
                expressions=[
                    args[0],
                    exp.Sub(
                        this=exp.Length(this=args[0]),
                        expression=exp.Sub(this=args[1], expression=exp.Literal.number(1)),
                    ),
                ],
            ),
            "MID": lambda args: exp.Anonymous(this="substring", expressions=args),
            "IF": lambda args: exp.If(
                this=args[0],
                true=args[1],
                false=args[2] if len(args) > 2 else exp.Null(),  # noqa: PLR2004
            ),
            "DIVIDE": lambda args: exp.Anonymous(
                this="try", expressions=[exp.Div(this=args[0], expression=args[1])]
            ),
            "CONCATENATEX": lambda args: exp.GroupConcat(
                this=args[1],
                separator=args[2] if len(args) > 2 else exp.Literal.string(","),  # noqa: PLR2004
            ),
        }
