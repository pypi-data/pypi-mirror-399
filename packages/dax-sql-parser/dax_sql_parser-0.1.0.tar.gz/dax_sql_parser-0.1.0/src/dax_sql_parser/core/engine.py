from typing import Any

from .dialects.registry import DialectRegistry
from .exceptions import DaxParsingError, DaxTranslationError
from .parser import parse_dax
from .translator import DaxToSqlTranslator


class DaxParser:
    """
    Unified entry point for DAX to SQL translation.
    """

    def __init__(
        self,
        default_dialect: str = "trino",
        schema_mapping: dict[str, str] | None = None,
        metadata: Any | None = None,
    ):
        self.default_dialect = default_dialect
        self.schema_mapping = schema_mapping or {}
        self.metadata = metadata
        self.translators: dict[str, DaxToSqlTranslator] = {}
        # Pre-initialize default translator to verify dialect exists
        self.get_translator(default_dialect)

    def get_translator(self, dialect: str) -> DaxToSqlTranslator:
        if dialect not in self.translators:
            # This will raise ValueError if dialect is not registered
            dialect_obj = DialectRegistry.get(dialect)
            self.translators[dialect] = DaxToSqlTranslator(
                dialect=dialect_obj, schema_mapping=self.schema_mapping, metadata=self.metadata
            )
        return self.translators[dialect]

    def to_sql(self, dax_query: str, dialect: str | None = None) -> str:
        """
        Parses a DAX query and translates it to SQL.
        """
        target_dialect = dialect or self.default_dialect

        try:
            ast = parse_dax(dax_query)
        except DaxParsingError:
            # Re-raise already specialized error
            raise
        except Exception as e:
            raise DaxParsingError(f"Failed to parse DAX: {e!s}") from e

        try:
            translator = self.get_translator(target_dialect)
            return translator.translate(ast)
        except DaxTranslationError:
            # Re-raise specialized translation errors (e.g., DaxDialectNotFoundError)
            raise
        except Exception as e:
            raise DaxTranslationError(
                f"Failed to translate to SQL ({target_dialect}): {e!s}"
            ) from e
