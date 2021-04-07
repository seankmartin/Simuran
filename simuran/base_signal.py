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
        The value of the signal at sample points.
        By default, this is assumed to be stored in mV.
    sampling_rate : int
        The sampling rate of the signal in Hz
    region : str
        The brain region that the signal is associated with
    group : object
        An optional value to group on.
        For example, if wires are bundled, this could indicate the bundle number.
    channel : object
        The channel id of the signal.
    channel_type : str
        The type of the signal channel, e.g. eeg.
        Default is "eeg".
    unit : astropy.unit.Unit
        An SI unit measure of the signal. This is set at load time.
    source_file : str
        The path to a source file containing the signal data.

    """

    def __init__(self):
        """See help(BaseSignal)."""
        self.timestamps = None
        self.samples = None
        self.sampling_rate = None
        self.region = None
        self.group = None
        self.channel = None
        self.channel_type = "eeg"
        self.source_file = "<unknown>"
        super().__init__()

    def load(self, *args, **kwargs):
        """Load the signal."""
        super().load()
        if not self.loaded():
            load_result = self.loader.load_signal(self.source_file, **kwargs)
            self.save_attrs(load_result)
            self.last_loaded_source = self.source_file

    def from_numpy(self, np_array, sampling_rate):
        self.samples = np_array
        self.sampling_rate = sampling_rate
        self.timestamps = [sampling_rate * i for i in range(len(self.samples))]

    def default_name(self):
        """Default name based on region."""
        name = self.channel_type
        if self.channel is not None:
            name += " {}".format(self.channel)
        if self.region is not None:
            name = "{} - {}".format(self.region, name)

        return name

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

    def get_channel(self):
        """Return the channel."""
        return self.channel

    def get_channel_type(self):
        """Return the channel type."""
        return self.channel_type

    def get_source_file(self):
        """Return the name of the source file."""
        return self.source_file

    def set_duration(self, duration):
        """Set the value of self.duration."""
        self.duration = duration

    def set_samples(self, samples):
        """Set the value of self.samples."""
        self.samples = samples

    def set_sampling_rate(self, sampling_rate):
        """Set the value of self.sampling_rate."""
        self.sampling_rate = sampling_rate

    def set_timestamps(self, timestamps):
        """Set the value of self.timestamps."""
        self.timestamps = timestamps

    def set_channel(self, channel):
        """Set the value of self.channel."""
        self.channel = channel

    def set_channel_type(self, channel_type):
        """Set the value of self.channel_type."""
        self.channel_type = channel_type

    def set_source_file(self, source_file):
        """Set the value of self.source_file."""
        self.source_file = source_file

    def set_region(self, region):
        """Set the value of self.region."""
        self.region = region
