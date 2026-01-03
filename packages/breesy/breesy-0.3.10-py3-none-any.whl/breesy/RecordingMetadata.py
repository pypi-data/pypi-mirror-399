from pathlib import Path

from .type_hints import enforce_type_hints


class RecordingMetadata:
    """Metadata for an EEG recording."""

    name: str
    """Name of the recording"""

    file_path: Path | None
    """Path to the source file"""

    description: str | None
    """Optional description of the recording"""

    def __str__(self):
        """Return a string representation of the RecordingMetadata object."""
        return self.__repr__()

    def __repr__(self):
        """Return a string representation of the RecordingMetadata object."""
        name_repr = f"name='{self.name}'"
        description_repr = f"description='{self.description}'" if self.description else None
        filepath_repr = f"file_path='{self.file_path}'" if self.file_path else None

        all_args = [name_repr, filepath_repr, description_repr]
        args_repr = ", ".join(arg for arg in all_args if arg is not None)
        return f"RecordingMetadata({args_repr})"

    @enforce_type_hints
    def __init__(self, name: str, file_path: Path | None = None, description: str | None = None):
        """Initialize RecordingMetadata.

        :param name: Name of the recording
        :param file_path: Path to the source file
        :param description: Optional description of the recording
        """
        self.name = name
        self.file_path = file_path
        self.description = description
