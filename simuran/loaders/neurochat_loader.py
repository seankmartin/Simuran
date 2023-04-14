"""This module handles interfacing with NeuroChaT."""
import datetime
import logging
import os
from collections.abc import Iterable
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from dateutil.tz import tzlocal
from neurochat.nc_lfp import NLfp
from neurochat.nc_spatial import NSpatial
from neurochat.nc_spike import NSpike
from simuran.core.base_class import NoLoader
from simuran.core.base_signal import BaseSignal
from simuran.core.param_handler import ParamHandler
from simuran.loaders.base_loader import MetadataLoader
from skm_pyutils.path import get_all_files_in_dir
from skm_pyutils.table import list_to_df
from tqdm import tqdm

if TYPE_CHECKING:
    from simuran.recording import Recording

module_logger = logging.getLogger("simuran.loaders")


class NeurochatLoader(MetadataLoader):
    """
    Load data compatible with the NeuroChaT package.

    Parameters
    ----------
    system : str
        The system to load, default is "Axona".

    Kwargs and defaults
    -------------------
    pos_extension : (".txt", ".pos")
    clu_extension : ".clu.X"
    sig_channels : None
    unit_groups : None
    stm_extension : ".stm"
    lfp_extension : ".eeg"
    cluster_extension : ".cut"
    """

    def __init__(self, system="Axona", **kwargs):
        self.system = system
        self.loader_kwargs = kwargs

    def load_recording(self, recording):
        def add_mapping_info(recording):
            mapping = recording.attrs.get("mapping")
            if not hasattr(mapping, "items"):
                return
            for first_key, map_sub in mapping.items():
                if map_sub is None:
                    recording.attrs[first_key] = None
                    continue
                if (
                    first_key not in ["signals", "spatial", "units"]
                    or first_key not in recording.data
                ):
                    continue
                for key, value in map_sub.items():
                    if isinstance(value, list):
                        for i in range(len(recording.data[first_key])):
                            setattr(recording.data[first_key][i], key, value[i])
                    else:
                        recording.attrs[f"{first_key}_{key}"] = value

        source_files = recording.attrs["source_files"]
        if recording.data is None:
            recording.data = {}
        recording.last_loaded_source = recording.source_file
        if (
            source_files.get("Signal", None) is not None
            and "Signal" in recording.available_data
        ):
            recording.data["signals"] = [
                self.load_signal(fname) for fname in source_files["Signal"]
            ]

        if (
            source_files.get("Spike", None) is not None
            and "Spike" in recording.available_data
        ):
            if source_files["Spike"] is not None:
                recording.data["units"] = []
                for spike_f, clust_f in zip(
                    source_files["Spike"], source_files["Cluster"]
                ):
                    if clust_f is not None:
                        unit = self.load_single_unit(spike_f)
                    else:
                        unit = NoLoader(source_file=spike_f)
                        unit.available_units = None
                    recording.data["units"].append(unit)
        if (
            source_files.get("Spatial", None) is not None
            and "Spatial" in recording.available_data
        ):
            recording.data["spatial"] = self.load_spatial(source_files["Spatial"])

        add_mapping_info(recording)

    def parse_metadata(self, recording: "Recording") -> None:
        if "source_file" in recording.attrs:
            source_file = Path(recording.attrs["source_file"])
        elif "directory" in recording.attrs:
            source_file = (
                Path(recording.attrs["directory"]) / recording.attrs["filename"]
            )
        else:
            source_file = recording.source_file
        recording.source_file = source_file
        recording.attrs["source_files"] = self.auto_fname_extraction(
            recording.source_file
        )[0]
        recording.available_data = list(recording.attrs["source_files"].keys())
        if "mapping" in recording.attrs:
            ph = ParamHandler(source_file=recording.attrs["mapping"], name="mapping")
            recording.attrs["mapping_file"] = recording.attrs["mapping"]
            recording.attrs["mapping"] = ph
        if "datetime" in recording.attrs:
            recording.datetime = datetime.datetime.strptime(
                recording.attrs["datetime"], "%Y-%m-%d %H:%M:%S"
            )
            recording.datetime = recording.datetime.replace(tzinfo=tzlocal())

    def load_signal(self, *args, **kwargs):
        """
        Call the NeuroChaT NLfp.load method.

        Returns
        -------
        dict
            The keys of this dictionary are saved as attributes
            in simuran.signal.BaseSignal.load()
        """
        self.signal = NLfp()
        obj = BaseSignal()
        try:
            self.signal.load(*args, self.system)
        except Exception as e:
            module_logger.warning(f"Failed to load signal with NeuroChaT due to {e}, skipping")
            return obj
        obj.data = self.signal
        obj.timestamps = self.signal.get_timestamp()
        obj.samples = self.signal.get_samples()
        obj.conversion = 0.001
        obj.date = self.signal.get_date()
        obj.time = self.signal.get_time()
        obj.channel = self.signal.get_channel_id()
        obj.sampling_rate = self.signal.get_sampling_rate()
        obj.source_file = args[0]
        obj.last_loaded_source = args[0]
        return obj

    def load_spatial(self, *args, **kwargs):
        """
        Call the NeuroChaT NSpatial.load method.

        Returns
        -------
        dict
            The keys of this dictionary are saved as attributes
            in simuran.single_unit.SingleUnit.load()
        """
        self.spatial = NSpatial()
        self.spatial.load(*args, self.system)
        obj = NoLoader()
        obj.data = self.spatial
        obj.date = self.spatial.get_date()
        obj.timestamps = self.spatial.get_time()
        obj.speed = self.spatial.get_speed()
        obj.position = (self.spatial.get_pos_x(), self.spatial.get_pos_y())
        obj.direction = self.spatial.get_direction()
        obj.source_file = args[0]
        obj.last_loaded_source = args[0]
        return obj

    def load_single_unit(self, *args, **kwargs):
        """
        Call the NeuroChaT NSpike.load method.

        Returns
        -------
        dict
            The keys of this dictionary are saved as attributes
            in simuran.spatial.Spatial.load()

        """
        self.single_unit = NSpike()
        self.single_unit.load(*args, self.system)
        obj = NoLoader()
        waveforms = deepcopy(self.single_unit.get_waveform())
        for chan, val in waveforms.items():
            waveforms[chan] = val
        obj.data = self.single_unit
        obj.timestamps = self.single_unit.get_timestamp()
        obj.unit_tags = self.single_unit.get_unit_tags()
        obj.waveforms = waveforms
        obj.date = self.single_unit.get_date()
        obj.time = self.single_unit.get_time()
        obj.available_units = self.single_unit.get_unit_list()
        obj.source_file = args[0]
        obj.last_loaded_source = args[0]
        obj.tag = int(Path(args[0]).suffix[1:])
        return obj

    def auto_fname_extraction(self, base, **kwargs):
        """
        Extract all filenames relevant to the recording from base.

        Parameters
        ----------
        base : str
            Where to start looking from.
            For Axona, this should be a .set file,
            or a directory containing exactly one .set file

        Returns
        -------
        fnames : dict
            A dictionary listing the filenames involved in loading.
        base : str
            The base file name, in Axona this is a .set file.

        """
        # Currently only implemented for Axona systems
        error_on_missing = kwargs.get("enforce_data", True)

        if self.system == "Axona":

            # Find the set file if a directory is passed
            if os.path.isdir(base):
                set_files = get_all_files_in_dir(base, ext="set")
                if len(set_files) == 0:
                    module_logger.warning(
                        "No set files found in {}, skipping".format(base)
                    )
                    return None, None
                elif len(set_files) > 1:
                    raise ValueError(
                        "Found more than one set file, found {}".format(len(set_files))
                    )
                base = set_files[0]
            elif not os.path.isfile(base):
                raise ValueError("{} is not a file or directory".format(base))

            joined_params = {
                "system": self.system,
            }
            joined_params.update(self.loader_kwargs)
            joined_params.update(**kwargs)
            cluster_extension = joined_params.get("cluster_extension", ".cut")
            clu_extension = joined_params.get("clu_extension", ".clu.X")
            pos_extension = joined_params.get("pos_extension", (".txt", ".pos"))
            lfp_extension = joined_params.get("lfp_extension", ".eeg")  # eeg or egf
            stm_extension = joined_params.get("stm_extension", ".stm")
            tet_groups = joined_params.get("unit_groups", None)
            channels = joined_params.get("sig_channels", None)

            filename = os.path.splitext(base)[0]
            base_filename = os.path.splitext(os.path.basename(base))[0]

            # Extract the tetrode and cluster data
            spike_names_all = []
            cluster_names_all = []
            if tet_groups is None:
                tet_groups = [
                    x for x in range(0, 64) if os.path.exists(filename + "." + str(x))
                ]
            if channels is None:
                channels = [
                    x
                    for x in range(2, 256)
                    if os.path.exists(filename + lfp_extension + str(x))
                ]
                if os.path.exists(filename + lfp_extension):
                    channels = [1] + channels
            for tetrode in tet_groups:
                spike_name = filename + "." + str(tetrode)
                if not os.path.isfile(spike_name):
                    e_msg = "Axona data is not available for {}".format(spike_name)
                    if error_on_missing:
                        raise ValueError(e_msg)
                    else:
                        logging.warning(e_msg)
                        return None, base

                spike_names_all.append(spike_name)

                cut_name = filename + "_" + str(tetrode) + cluster_extension
                clu_name = filename + clu_extension[:-1] + str(tetrode)
                if os.path.isfile(cut_name):
                    cluster_name = cut_name
                elif os.path.isfile(clu_name):
                    cluster_name = clu_name
                else:
                    cluster_name = None
                cluster_names_all.append(cluster_name)

            # Extract the positional data
            output_list = [None, None]
            for i, ext in enumerate([pos_extension, stm_extension]):
                if isinstance(ext, Iterable) and not isinstance(ext, str):
                    for ext_ in ext:
                        filename_ = self._grab_stim_pos_files(base, base_filename, ext_)
                        if filename_ is not None:
                            output_list[i] = filename_
                            break
                else:
                    output_list[i] = self._grab_stim_pos_files(base, base_filename, ext)
            spatial_name, stim_name = output_list

            base_sig_name = filename + lfp_extension
            signal_names = []
            for c in channels:
                if c != 1:
                    if os.path.exists(base_sig_name + str(c)):
                        signal_names.append(base_sig_name + str(c))
                    else:
                        e_msg = "{} does not exist".format(base_sig_name + str(c))
                        if error_on_missing:
                            raise ValueError(e_msg)
                        else:
                            logging.warning(e_msg)
                            return None, base
                else:
                    if os.path.exists(base_sig_name):
                        signal_names.append(base_sig_name)
                    else:
                        e_msg = "{} does not exist".format(base_sig_name)
                        if error_on_missing:
                            raise ValueError(e_msg)
                        else:
                            logging.warning(e_msg)
                            return None, base

            file_locs = {
                "Spike": spike_names_all,
                "Cluster": cluster_names_all,
                "Spatial": spatial_name,
                "Signal": signal_names,
                "Stimulation": stim_name,
            }
            return file_locs, base
        else:
            raise ValueError("auto_fname_extraction only implemented for Axona")

    def _grab_stim_pos_files(self, base, base_filename, ext):
        for fname in get_all_files_in_dir(
            os.path.dirname(base),
            ext=ext,
            return_absolute=False,
            case_sensitive_ext=True,
        ):
            if ext == ".txt":
                if fname[: len(base_filename) + 1] == f"{base_filename}_":
                    name = os.path.join(os.path.dirname(base), fname)
                    return name
            elif fname[: len(base_filename)] == base_filename:
                name = os.path.join(os.path.dirname(base), fname)
                return name

    def index_files(self, folder, **kwargs):
        """Find all available neurochat files in the given folder"""
        if self.system != "Axona":
            raise ValueError("auto_fname_extraction only implemented for Axona")
        set_files = []
        root_folders = []
        times = []
        durations = []
        dates = []
        comments = []
        module_logger.info("Finding all .set files...")
        files = get_all_files_in_dir(
            str(folder),
            ext=".set",
            recursive=True,
            return_absolute=True,
            case_sensitive_ext=True,
        )
        module_logger.info(f"Found {len(files)} set files")

        for fname in tqdm(files, desc="Processing files"):
            set_files.append(os.path.basename(fname))
            root_folders.append(os.path.normpath(os.path.dirname(fname)))
            with open(fname) as f:
                d = f.readline()
                dates.append(d.split(" ", 1)[1].strip())
                t = f.readline()[-9:-1]
                try:
                    int(t[:2])
                    times.append(t)
                except ValueError:
                    times.append(np.nan)
                f.readline()
                comment = f.readline()
                try:
                    comments.append(comment.split(" ", 1)[1].strip())
                except IndexError:
                    comments.append("")
                duration = f.readline()
                try:
                    durations.append(int(float(duration.split(" ", 1)[1].strip())))
                except Exception:
                    durations.append(np.nan)

        headers = ["directory", "filename", "date", "time", "duration", "comments"]
        in_list = [root_folders, set_files, dates, times, durations, comments]
        return list_to_df(in_list, transpose=True, headers=headers)
