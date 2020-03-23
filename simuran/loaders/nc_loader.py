"""This module handles interfacing with NeuroChaT."""
import os

from simuran.loaders.base_loader import BaseLoader
from neurochat.nc_lfp import NLfp
from neurochat.nc_spatial import NSpatial
from neurochat.nc_spike import NSpike
from neurochat.nc_datacontainer import NDataContainer
from neurochat.nc_utils import get_all_files_in_dir


class NCLoader(BaseLoader):
    def __init__(self, load_params={}):
        super().__init__(load_params=load_params)

    # TODO probably need to make new objects each time.
    def load_signal(self, *args, **kwargs):
        self.signal = NLfp()
        self.signal.load(*args, self.load_params["system"])
        return self.signal

    def load_spatial(self, *args, **kwargs):
        self.spatial = NSpatial()
        self.spatial.load(*args, self.load_params["system"])
        return self.spatial

    def load_single_unit(self, *args, **kwargs):
        fname, clust_name = args
        if clust_name is not None:
            self.single_unit = NSpike()
            self.single_unit.load(fname, self.load_params["system"])
            return self.single_unit
        else:
            return None

    def auto_fname_extraction(self, base, **kwargs):
        # Currently only implemented for Axona systems
        if self.load_params["system"] == "Axona":
            if os.path.isdir(base):
                set_files = get_all_files_in_dir(base, ext="set")
                if len(set_files) > 1:
                    raise ValueError(
                        "Found more than one set file, found {}".format(
                            len(set_files)))
                base = set_files[0]
            elif not os.path.isfile(base):
                raise ValueError(
                    "{} is not a file or directory".format(base))
            kwargs["re_filter"] = (
                "^" + os.path.splitext(os.path.basename(base))[0])
            kwargs["save_result"] = False
            ndc = NDataContainer(load_on_fly=True)
            cluster_names = ndc.add_axona_files_from_dir(
                os.path.dirname(base), **kwargs)
            spike_names = [s[0] for s in ndc.get_file_dict("Spike")]
            channels = kwargs.get("sig_channels", [i + 1 for i in range(32)])
            base_sig_name = ndc.get_file_dict("LFP")[0][0]
            signal_names = []
            for c in channels:
                if c != 1:
                    if os.path.exists(base_sig_name + str(c)):
                        signal_names.append(base_sig_name + str(c))
                    else:
                        raise ValueError("{} does not exist".format(
                            base_sig_name + str(c)))
                else:
                    if os.path.exists(base_sig_name):
                        signal_names.append(base_sig_name)
                    else:
                        raise ValueError("{} does not exist".format(
                            base_sig_name))

            tet_groups = kwargs.get("unit_groups", [i + 1 for i in range(16)])
            spike_names_all = []
            cluster_names_all = []
            base_tet_name = base[:-3]
            for tet in tet_groups:
                if os.path.exists(base_tet_name + str(tet)):
                    spike_names_all.append(base_tet_name + str(tet))
                    if (base_tet_name + str(tet)) in spike_names:
                        idx = spike_names.index(base_tet_name + str(tet))
                        cluster_names_all.append(cluster_names[idx])
                    else:
                        cluster_names_all.append(None)
                else:
                    raise ValueError("{} does not exist".format(
                        base_tet_name + str(tet)))

            file_locs = {
                "Spike": spike_names_all,
                "Clusters": cluster_names_all,
                "Spatial": ndc.get_file_dict("Position")[0][0],
                "Signal": signal_names,
                "Stimulation": ndc.get_file_dict("STM")[0][0],
            }
            return file_locs
        else:
            raise ValueError(
                "auto_fname_extraction only implemented for Axona")
