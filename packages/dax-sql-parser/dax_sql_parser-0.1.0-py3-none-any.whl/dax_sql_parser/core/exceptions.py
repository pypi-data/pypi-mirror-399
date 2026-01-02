class DaxError(Exception):
    """Base class for all DAX parser errors."""

    pass


class DaxParsingError(DaxError):
    """Raised when parsing fails."""

    def __init__(
        self,
        message: str,
        line: int | None = None,
        column: int | None = None,
        start_offset: int | None = None,
        end_offset: int | None = None,
    ) -> None:
        error_msg = message
        if line is not None and column is not None:
            error_msg = f"{message} at line {line}, column {column}"
        super().__init__(error_msg)
        self.line = line
        self.column = column
        self.start_offset = start_offset
        self.end_offset = end_offset


class DaxTranslationError(DaxError):
    """Raised when SQL translation fails."""

    def __init__(
        self,
        message: str,
        line: int | None = None,
        column: int | None = None,
        start_offset: int | None = None,
        end_offset: int | None = None,
    ) -> None:
        error_msg = message
        if line is not None and column is not None:
            error_msg = f"{message} at line {line}, column {column}"
        super().__init__(error_msg)
        self.line = line
        self.column = column
        self.start_offset = start_offset
        self.end_offset = end_offset


class DaxDialectNotFoundError(DaxTranslationError):
    """Raised when the requested dialect is not found."""

    pass


class DaxUnsupportedFunctionError(DaxTranslationError):
    """Raised when a DAX function is not supported by the current dialect."""

    pass


class DaxMetadataError(DaxError):
    """Base class for metadata-related errors."""

    pass


class DaxTableNotFoundError(DaxMetadataError):
    """Raised when a referenced table is not found in metadata."""

    pass


class DaxColumnNotFoundError(DaxMetadataError):
    """Raised when a referenced column is not found in metadata."""

    pass


class DaxAmbiguousColumnError(DaxMetadataError):
    """Raised when an unqualified column reference matches multiple tables."""

    pass
