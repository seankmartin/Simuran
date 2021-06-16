"""This module handles interfacing with NeuroChaT."""
import os
import logging
from copy import deepcopy

from neurochat.nc_lfp import NLfp
from neurochat.nc_spatial import NSpatial
from neurochat.nc_spike import NSpike
from skm_pyutils.py_path import get_all_files_in_dir
from skm_pyutils.py_table import list_to_df
from astropy import units as u
from tqdm import tqdm
import numpy as np

from simuran.loaders.base_loader import BaseLoader


class NCLoader(BaseLoader):
    """Load data compatible with the NeuroChaT package."""

    def __init__(self, load_params={}):
        """Call super class initialize."""
        super().__init__(load_params=load_params)

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
        self.signal.load(*args, self.load_params["system"])
        return {
            "underlying": self.signal,
            "timestamps": self.signal.get_timestamp() * u.s,
            "samples": self.signal.get_samples() * u.mV,
            "date": self.signal.get_date(),
            "time": self.signal.get_time(),
            "channel": self.signal.get_channel_id(),
        }

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
        self.spatial.load(*args, self.load_params["system"])
        return {
            "underlying": self.spatial,
            "date": self.spatial.get_date(),
            "time": self.spatial.get_time(),
        }

    def load_single_unit(self, *args, **kwargs):
        """
        Call the NeuroChaT NSpike.load method.

        Returns
        -------
        dict
            The keys of this dictionary are saved as attributes
            in simuran.spatial.Spatial.load()

        """
        fname, clust_name = args
        if clust_name is not None:
            self.single_unit = NSpike()
            self.single_unit.load(fname, self.load_params["system"])
            waveforms = deepcopy(self.single_unit.get_waveform())
            for chan, val in waveforms.items():
                waveforms[chan] = val * u.uV
            return {
                "underlying": self.single_unit,
                "timestamps": self.single_unit.get_timestamp() * u.s,
                "unit_tags": self.single_unit.get_unit_tags(),
                "waveforms": waveforms,
                "date": self.single_unit.get_date(),
                "time": self.single_unit.get_time(),
                "available_units": self.single_unit.get_unit_list(),
                # "units_to_use": self.single_unit.get_unit_list(),
            }
        else:
            return None

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

        TODO
        ----
        Expand to support nwb and neuralynx as well as Axona.

        """
        # Currently only implemented for Axona systems
        error_on_missing = self.load_params.get("enforce_data", True)

        if self.load_params["system"] == "Axona":

            # Find the set file if a directory is passed
            if os.path.isdir(base):
                set_files = get_all_files_in_dir(base, ext="set")
                if len(set_files) == 0:
                    print("WARNING: No set files found in {}, skipping".format(base))
                    return None, None
                elif len(set_files) > 1:
                    raise ValueError(
                        "Found more than one set file, found {}".format(len(set_files))
                    )
                base = set_files[0]
            elif not os.path.isfile(base):
                raise ValueError("{} is not a file or directory".format(base))

            joined_params = {**self.load_params, **kwargs}
            cluster_extension = joined_params.get("cluster_extension", ".cut")
            clu_extension = joined_params.get("clu_extension", ".clu.X")
            pos_extension = joined_params.get("pos_extension", ".pos")
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
                for fname in get_all_files_in_dir(
                    os.path.dirname(base),
                    ext=ext,
                    return_absolute=False,
                    case_sensitive_ext=True,
                ):
                    if ext == ".txt":
                        if fname[: len(base_filename) + 1] == base_filename + "_":
                            name = os.path.join(os.path.dirname(base), fname)
                            output_list[i] = name
                            break
                    else:
                        if fname[: len(base_filename)] == base_filename:
                            name = os.path.join(os.path.dirname(base), fname)
                            output_list[i] = name
                            break
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
                "Clusters": cluster_names_all,
                "Spatial": spatial_name,
                "Signal": signal_names,
                "Stimulation": stim_name,
            }
            return file_locs, base
        else:
            raise ValueError("auto_fname_extraction only implemented for Axona")

    def index_files(self, folder, **kwargs):
        if self.load_params["system"] == "Axona":
            set_files = []
            root_folders = []
            times = []
            durations = []
            print("Finding all .set files...")
            files = get_all_files_in_dir(
                folder,
                ext=".set",
                recursive=True,
                return_absolute=True,
                case_sensitive_ext=True,
            )
            print(f"Found {len(set_files)} set files")

            for fname in tqdm(files, desc="Processing files"):
                set_files.append(os.path.basename(fname))
                root_folders.append(os.path.normpath(os.path.dirname(fname)))
                with open(fname) as f:
                    f.readline()
                    t = f.readline()[-9:-2]
                    try:
                        int(t[:2])
                        times.append(t)
                        f.readline()
                        f.readline()
                        durations.append(f.readline()[-11:-8])
                    except:
                        if len(times) != len(set_files):
                            times.append(np.nan)
                        if len(durations) != len(set_files):
                            durations.append(np.nan)

            headers = ["filename", "folder", "time", "duration"]
            in_list = [set_files, root_folders, times, durations]
            results_df = list_to_df(in_list, transpose=True, headers=headers)
            return results_df
        else:
            raise ValueError("auto_fname_extraction only implemented for Axona")
