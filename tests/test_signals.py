import pytest
import numpy as np

import mne
from simuran.core.base_signal import BaseSignal, Eeg
from simuran.bridges.neurochat_bridge import signal_to_neurochat
from simuran.bridges.mne_bridge import convert_signals_to_mne, plot_signals
from simuran.loaders.base_loader import MetadataLoader

from copy import copy


class FakeLoader(MetadataLoader):
    def load_signal(self, source_file):
        signal = Eeg()
        signal.fake_data = source_file
        return signal


@pytest.mark.parametrize("array_size, sampling_rate", [(10000, 20)])
class TestBaseSignal:
    @pytest.fixture
    def signal(self, array_size, sampling_rate):
        np_arr = np.random.random(size=array_size)
        signal = BaseSignal.from_numpy(np_arr, sampling_rate)
        signal.samples = list(np_arr)
        signal.channel = "1"
        signal.region = "NA"
        return signal

    def test_from_numpy(self, array_size, sampling_rate, signal):
        t2 = np.arange(0, array_size / sampling_rate, 1.0 / sampling_rate)
        assert np.all(np.isclose(signal.timestamps, t2))

    def test_naming(self, signal):
        assert signal.default_name() == "NA - misc 1"

    def test_to_nc(self, array_size, sampling_rate, signal):
        lfp = signal_to_neurochat(signal)
        t2 = np.arange(0, array_size / sampling_rate, 1.0 / sampling_rate)
        assert lfp.get_channel_id() == "1"
        assert np.all(np.isclose(lfp._timestamp, t2))
        assert np.all(np.isclose(signal.samples, lfp.get_samples()))
        signal.data = lfp
        lfp2 = signal_to_neurochat(signal)
        assert np.all(np.isclose(lfp2.get_samples(), lfp.get_samples()))

    def test_range(self, signal, sampling_rate):
        r_bit = signal.in_range(1, 2)
        assert np.all(signal.samples[1 * sampling_rate : 2 * sampling_rate] == r_bit)
        r_bit = signal.in_range(1, 8, 2)
        assert np.all(
            signal.samples[1 * sampling_rate : 8 * sampling_rate : 2 * sampling_rate]
            == r_bit
        )

    def test_filter(self, signal, sampling_rate):
        filtered_data = signal.filter(1, 5, inplace=False)
        filter_by_mne = mne.filter.filter_data(signal.samples, sampling_rate, 1, 5)
        assert np.all(np.isclose(filtered_data.samples, filter_by_mne))
        assert np.any(~np.isclose(filtered_data.samples, signal.samples))
        filtered_data = signal.filter(1, 5, inplace=True)
        assert np.all(np.isclose(signal.samples, filter_by_mne))
        assert np.all(signal.filter(None, None).samples == signal.samples)

    def test_start_end(self, signal, array_size, sampling_rate):
        assert signal.get_start() == 0
        assert np.isclose(signal.get_end(), (array_size - 1) / sampling_rate)
        assert signal.get_duration() == signal.get_end()

    def test_convert_to_mne(self, signal):
        signals = [copy(signal) for _ in range(10)]
        for i in range(len(signals)):
            signals[i].channel = i
        bad_chans = [0]
        mne_signals = convert_signals_to_mne(
            signals, ch_names=None, verbose=False, bad_chans=bad_chans
        )
        assert np.all(
            np.isclose(mne_signals.get_data()[0], signal.get_samples_in_volts())
        )

    def test_plot(self, signal):
        signals = [copy(signal) for _ in range(10)]
        for signal_ in signals:
            signal_.channel_type = "eeg"
        fig = plot_signals(signals, show=False)
        assert fig != None

    def test_loading(self, signal):
        sigcal = BaseSignal()
        sigcal.loader = FakeLoader()
        sigcal.source_file = "text.txt"
        sigcal.load()
        assert sigcal.fake_data == "text.txt"
        assert sigcal.is_loaded()
        assert sigcal.channel_type == "eeg"
