"""Module to hold the abstract class setting up information held in a signal."""

from simuran.base_class import BaseSimuran


class BaseSignal(BaseSimuran):
    """
    Describes the base information for a regularly sampled signal.

    For example, LFP or EEG could be represented.

    Attributes
    ----------
    timestamps : array style object
        The timestamps of the signal sampling
    samples : array style object
        The value of the signal at sample points
    sampling_rate : int
        The sampling rate of the signal in Hz
    region : str
        The brain region that the signal is associated with
    group : object
        An optional value to group on.
        For example, if wires are bundled, this could indicate the bundle number.

    """

    def __init__(self):
        """See help(BaseSignal)."""
        self.timestamps = None
        self.samples = None
        self.sampling_rate = None
        self.region = None
        self.group = None
        super().__init__()

    def load(self, *args, **kwargs):
        """Load the signal."""
        super().load()
        if not self.loaded():
            load_result = self.loader.load_signal(self.source_file, **kwargs)
            self.save_attrs(load_result)
            self.last_loaded_source = self.source_file

    def get_duration(self):
        """Get the length of the signal in the unit of timestamps."""
        return max(self.timestamps) - min(self.timestamps)

    def get_sampling_rate(self):
        """Return the sampling rate."""
        return self.sampling_rate

    def get_timestamps(self):
        """Return the timestamps."""
        return self.timestamps

    def get_samples(self):
        """Return the samples."""
        return self.samples
