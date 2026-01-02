from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .exceptions import DaxAmbiguousColumnError, DaxMetadataError


@dataclass
class ColumnMetadata:
    name: str
    data_type: str = "string"


@dataclass
class TableMetadata:
    name: str
    columns: dict[str, ColumnMetadata] = field(default_factory=dict)

    def add_column(self, name: str, data_type: str = "string") -> None:
        self.columns[name.upper()] = ColumnMetadata(name=name, data_type=data_type)


@dataclass
class Relationship:
    from_table: str
    from_column: str
    to_table: str
    to_column: str


@runtime_checkable
class MetadataProvider(Protocol):
    """
    Protocol for providing metadata about tables and relationships.
    """

    def get_table(self, table_name: str) -> TableMetadata | None: ...

    def get_all_tables(self) -> list[TableMetadata]: ...

    def get_relationships(self) -> list[Relationship]: ...


class DictMetadataProvider:
    """
    Simple dictionary-based implementation of MetadataProvider.
    """

    def __init__(
        self,
        tables: list[TableMetadata] | None = None,
        relationships: list[Relationship] | None = None,
    ):
        self.tables = {t.name.upper(): t for t in (tables or [])}
        self.relationships = relationships or []

    def get_table(self, table_name: str) -> TableMetadata | None:
        return self.tables.get(table_name.upper())

    def get_all_tables(self) -> list[TableMetadata]:
        return list(self.tables.values())

    def get_relationships(self) -> list[Relationship]:
        return self.relationships


class MetadataResolver:
    """
    Main entry point for resolving metadata. Wraps a MetadataProvider.
    """

    def __init__(
        self,
        provider: MetadataProvider | None = None,
        tables: list[TableMetadata] | None = None,
        relationships: list[Relationship] | None = None,
    ):
        if provider:
            self.provider = provider
        else:
            self.provider = DictMetadataProvider(tables, relationships)

    def validate(self) -> None:
        """
        Validates the consistency of the metadata.
        Raises DaxMetadataError if inconsistencies are found.
        """
        tables = {t.name.upper(): t for t in self.provider.get_all_tables()}
        relationships = self.provider.get_relationships()

        for rel in relationships:
            # Check from_table
            f_table = tables.get(rel.from_table.upper())
            if not f_table:
                raise DaxMetadataError(f"Relationship refers to missing table: '{rel.from_table}'")
            if rel.from_column.upper() not in f_table.columns:
                raise DaxMetadataError(
                    f"Relationship refers to missing column: "
                    f"'{rel.from_table}'['{rel.from_column}']"
                )

            # Check to_table
            t_table = tables.get(rel.to_table.upper())
            if not t_table:
                raise DaxMetadataError(f"Relationship refers to missing table: '{rel.to_table}'")
            if rel.to_column.upper() not in t_table.columns:
                raise DaxMetadataError(
                    f"Relationship refers to missing column: '{rel.to_table}'['{rel.to_column}']"
                )

    @property
    def tables(self) -> dict[str, TableMetadata]:
        # For backward compatibility, return a dict
        return {t.name.upper(): t for t in self.provider.get_all_tables()}

    @property
    def relationships(self) -> list[Relationship]:
        return self.provider.get_relationships()

    def resolve_column(self, column_name: str, table_name: str | None = None) -> str | None:
        """Returns the fully qualified table name for a column."""
        if table_name:
            t = self.provider.get_table(table_name)
            if t and column_name.upper() in t.columns:
                return t.name
            return table_name  # Fallback

        # Unqualified reference: search all tables
        matches = []
        for t in self.provider.get_all_tables():
            if column_name.upper() in t.columns:
                matches.append(t.name)

        if len(matches) > 1:
            raise DaxAmbiguousColumnError(
                f"Column '{column_name}' is ambiguous. "
                f"It exists in multiple tables: {', '.join(matches)}"
            )

        if len(matches) == 1:
            return matches[0]
        return None

    def get_joins(self, tables_in_query: set[str]) -> list[Relationship]:
        """Finds relationships needed to join the given tables."""
        if len(tables_in_query) <= 1:
            return []

        tables_in_query_upper = {t.upper() for t in tables_in_query}
        needed_joins = []

        for rel in self.provider.get_relationships():
            f = rel.from_table.upper()
            t = rel.to_table.upper()
            if f in tables_in_query_upper and t in tables_in_query_upper:
                needed_joins.append(rel)

        return needed_joins
