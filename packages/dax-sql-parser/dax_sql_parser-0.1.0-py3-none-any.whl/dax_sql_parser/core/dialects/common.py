from collections.abc import Callable

import sqlglot.expressions as exp


def get_common_mappings() -> dict[str, Callable[[list[exp.Expression]], exp.Expression]]:
    """
    Returns generic mappings (Dialect-agnostic or standard SQL).
    """
    return {
        "SUM": lambda args: exp.Sum(this=args[0]),
        "AVERAGE": lambda args: exp.Avg(this=args[0]),
        "MIN": lambda args: exp.Min(this=args[0]),
        "MAX": lambda args: exp.Max(this=args[0]),
        "COUNT": lambda args: exp.Count(this=args[0]),
        "COUNTROWS": lambda args: exp.Count(this=exp.Star()),
        "DISTINCTCOUNT": lambda args: exp.Count(this=args[0], distinct=True),
        "UPPER": lambda args: exp.Upper(this=args[0]),
        "LOWER": lambda args: exp.Lower(this=args[0]),
        "TRIM": lambda args: exp.Trim(this=args[0]),
        "LEN": lambda args: exp.Length(this=args[0]),
        "ABS": lambda args: exp.Abs(this=args[0]),
        "ROUND": lambda args: exp.Round(this=args[0], decimals=args[1] if len(args) > 1 else None),
        "COALESCE": lambda args: exp.Coalesce(this=args[0], expressions=args[1:]),
        "ISBLANK": lambda args: exp.Is(this=args[0], expression=exp.Null()),
        "CONCATENATE": lambda args: exp.Concat(expressions=[args[0], args[1]]),
    }
