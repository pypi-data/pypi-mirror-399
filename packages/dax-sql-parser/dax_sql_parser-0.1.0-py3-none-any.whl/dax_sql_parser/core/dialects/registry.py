import importlib
import pkgutil
from typing import ClassVar

from ..exceptions import DaxDialectNotFoundError
from .base import BaseDialect


class DialectRegistry:
    """
    Registry for SQL dialects. Supports dynamic discovery of dialects in the dialects package.
    """

    _dialects: ClassVar[dict[str, BaseDialect]] = {}
    _discovered: ClassVar[bool] = False

    @classmethod
    def discover(cls) -> None:
        """
        Dynamically discovers and registers all Dialect classes in the current package.
        """
        if cls._discovered:
            return

        import dax_sql_parser.core.dialects as dialects_pkg  # noqa: PLC0415

        for _, name, is_pkg in pkgutil.iter_modules(dialects_pkg.__path__):
            if is_pkg or name in ("base", "registry", "common"):
                continue

            module_name = f"dax_sql_parser.core.dialects.{name}"
            module = importlib.import_module(module_name)

            for obj_name in dir(module):
                obj = getattr(module, obj_name)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, BaseDialect)
                    and obj is not BaseDialect
                ):
                    cls.register(obj())

        cls._discovered = True

    @classmethod
    def register(cls, dialect: BaseDialect) -> None:
        cls._dialects[dialect.name.lower()] = dialect

    @classmethod
    def get(cls, name: str) -> BaseDialect:
        cls.discover()
        dialect = cls._dialects.get(name.lower())
        if not dialect:
            raise DaxDialectNotFoundError(
                f"Dialect '{name}' not supported. Registered dialects: {list(cls._dialects.keys())}"
            )
        return dialect
