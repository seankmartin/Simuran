"""Single LFP signals."""
from simuran.base_signal import AbstractSignal


class LFP(AbstractSignal):

    def __repr__(self):
        return "LFP signal"

    def find_artf(self, sd, min_artf_freq, filt=False):
        if self.does_info_exist("mean"):
            print("Already calculated artefacts for this lfp_o_dict")
            return
        if filt:
            lfp_dict_s = self.get_filt_signal()
        else:
            lfp_dict_s = self.get_signal()

        for key, lfp in lfp_dict_s.items():
            # info is mean, sd, thr_locs, thr_vals, thr_time
            mean, std, thr_locs, thr_vals, thr_time, per_removed = lfp.find_artf(
                sd, min_artf_freq)
            self.add_info(key, mean, "mean")
            self.add_info(key, std, "std")
            self.add_info(key, thr_locs, "thr_locs")
            self.add_info(key, thr_vals, "thr_vals")
            self.add_info(key, thr_time, "thr_time")
            self.add_info(key, per_removed, "artf_removed")

    def deartf(self, sd, min_artf_freq, rep_freq=None, filt=False):
        """
        remove artifacts based on SD thresholding.

        Args:
            sd, min_artf_freq, filt, rep_freq (float, float, bool, float):
                Standard Deviation used for thresholding
                minimum artefact frequency used to determine block removal size
                True - removes artefacts from filtered signals
                replaces artefacts with sin wave of this freq


        Returns:
            OrderedDict of signals with artefacts replaced.

        """
        self.find_artf(sd, min_artf_freq, filt)

        lfp_clean_odict = OrderedDict()

        for key, lfp in self.lfp_filt_odict.items():
            clean_lfp = deepcopy(lfp)
            thr_locs = self.get_info(key, "thr_locs")

            if rep_freq is None:
                clean_lfp._samples[thr_locs] = np.mean(
                    clean_lfp._samples)
            else:
                times = lfp.get_timestamp()
                rep_sig = 0.5 * np.sin(2 * np.pi * rep_freq * times)
                clean_lfp._samples[thr_locs] = rep_sig[thr_locs]
                # clean_lfp._samples[250*60:250*120] = rep_sig[250*60:250*120]  # To artifically introduce sign at 1-2mins
            lfp_clean_odict[key] = clean_lfp

        return lfp_clean_odict
