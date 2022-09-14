"""The base loading class in SIMURAN."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from simuran.recording import Recording

if TYPE_CHECKING:
    from pandas import DataFrame


class BaseLoader(ABC):
    """
    This abstract class defines the layout of a SIMURAN loader.

    A superclass may also define methods for loading individual
    records, as well as a full recording - such as load_spikes
    or load_signal, or load_stimulation.

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

        Parses recording.attrs, for example:
        To set recording.source_file = (
            "R_" + recording.attrs["rat_name"] +
            "S_" + recording.attrs["session_id"] + ".nwb"

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

        Parses recording.attrs, for example:
        To set recording.source_file = (
            "R_" + recording.attrs["rat_name"] +
            "S_" + recording.attrs["session_id"] + ".nwb"

        Parameters
        ----------
        recording: simuran.Recording
            The recording object to parse into.

        Returns
        -------
        None

        """
        recording.available_data = list(recording.attrs.keys())

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
        t_name = table.index.name if table.index.name is not None else "_index"
        row_as_dict[t_name] = row.name
        recording.attrs = row_as_dict
        self.parse_metadata(recording)
        return recording
