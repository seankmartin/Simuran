"""The base loading class in SIMURAN."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from pandas import DataFrame
    from simuran.recording import Recording


class BaseLoader(ABC):
    """
    This abstract class defines the layout of a SIMURAN loader.

    The abstract methods load_signal, load_single_unit,
    load_spatial, and auto_fname_extraction
    must be defined by subclasses.

    """

    @abstractmethod
    def load_recording(self, recording: "Recording") -> None:
        """
        Load the information into the recording object.

        It has metadata or source files to help loading

        Parameters
        ----------
        recording : simuran.recording.Recording
            The recording to load.

        Returns
        -------
        None

        """

    @abstractmethod
    def parse_metadata(self, recording: "Recording") -> None:
        """
        Parse the information into the recording object.

        Parses recording.metadata, for example:
        To set recording.source_file = (
            "R_" + recording.metadata["rat_name"] +
            "S_" + recording.metadata["session_id"] + ".nwb"

        Parameters
        ----------
        recording: simuran.Recording
            The recording object to parse into.

        Returns
        -------
        None

        """

    @abstractmethod
    def parse_table_row(
        self, table: "DataFrame", index: int, recording: "Recording"
    ) -> None:
        """
        Extract a recording from a table which describes all data.

        Each row is assumed to describe a recording.

        Parameters
        ----------
        table: pandas.DataFrame
            The table to parse from.
        index: pandas.DataFrame
            The index to grab from the table.
        recording: simuran.Recording
            The recording object to parse into.

        Returns
        -------
        None

        """


class MetadataLoader(BaseLoader):
    """Only load parameters"""

    def load_recording(self, recording: "Recording") -> None:
        """
        Load the information into the recording object.

        It has metadata or source files to help loading

        Parameters
        ----------
        recording : simuran.recording.Recording
            The recording to load.

        Returns
        -------
        None

        """
        pass

    def parse_metadata(self, recording: "Recording") -> None:
        """
        Parse the information into the recording object.

        Parses recording.metadata, for example:
        To set recording.source_file = (
            "R_" + recording.metadata["rat_name"] +
            "S_" + recording.metadata["session_id"] + ".nwb"

        Parameters
        ----------
        recording: simuran.Recording
            The recording object to parse into.

        Returns
        -------
        None

        """
        recording.available_data = list(recording.metadata.keys())

    def parse_table_row(
        self, table: "DataFrame", index: int, recording: Optional["Recording"] = None
    ) -> "Recording":
        """
        Extract a recording from a table which describes all data.

        Each row is assumed to describe a recording.

        Parameters
        ----------
        table: pandas.DataFrame
            The table to parse from.
        index: pandas.DataFrame
            The index to grab from the table.
        recording: simuran.Recording
            The recording object to parse into, default None
            None creates a new recording object.

        Returns
        -------
        Recording

        """
        if recording is None:
            recording = Recording()
            recording.loader = self
        row = table.iloc[index]
        row_as_dict = row.to_dict()
        row_as_dict[table.index.name] = row.name
        recording.metadata = row_as_dict
        self.parse_metadata(recording)
        return recording
