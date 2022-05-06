# I'm almost certain this is way too complex and not at all needed.
def _setup(self, load=True):
    """
    Set up this recording.

    Parameters
    ----------
    load : bool, optional
        Whether the information should be loaded, by default True

    Returns
    -------
    None

    """
    if self.source_file is None:
        default_base_val = None
        if self.param_handler.location is not None:
            default_base_val = os.path.dirname(self.param_handler.location)
        base = self.param_handler.get("base_fname", default_base_val)

        if base is None:
            raise ValueError("Must set a base file in Recording setup")
    else:
        base = self.source_file

    data_loader_cls = loaders_dict.get(self.param_handler.get("loader", None), None)
    if data_loader_cls is None:
        raise ValueError(
            "Unrecognised loader {}, options are {}".format(
                self.param_handler.get("loader", None), list(loaders_dict.keys())
            )
        )
    elif data_loader_cls == "params_only_no_cls":
        data_loader = None
        load = False
    else:
        data_loader = data_loader_cls(self.param_handler["loader_kwargs"])
        chans = self.get_signal_channels()
        groups = self.get_unit_groups()
        fnames, base = data_loader.auto_fname_extraction(
            base, sig_channels=chans, unit_groups=groups
        )
        if fnames is None:
            self.valid = False
            logging.warning("Invalid recording setup from {}".format(base))
            return
        self.source_file = base

    # TODO this could possibly have different classes for diff loaders
    self.signals = GenericContainer(BaseSignal)
    use_all = (
        ("signals" not in self.param_handler.keys())
        and ("units" not in self.param_handler.keys())
        and ("spatial" not in self.param_handler.keys())
    )
    if "signals" in self.param_handler.keys() or use_all:
        self.available.append("signals")
        signal_dict = self.param_handler.get("signals", None)
        if data_loader_cls == "params_only_no_cls":
            to_iter = signal_dict["num_signals"]
        else:
            to_iter = len(fnames["Signal"])
        for i in range(to_iter):
            if signal_dict is not None:
                params = split_dict(signal_dict, i)
            else:
                params = {}
            self.signals.append_new(params)
            if data_loader is not None:
                self.signals[-1].set_source_file(fnames["Signal"][i])
                self.signals[-1].set_loader(data_loader)

    if "units" in self.param_handler.keys() or use_all:
        self.units = GenericContainer(SingleUnit)
        self.available.append("units")
        units_dict = self.param_handler.get("units", None)
        if data_loader_cls == "params_only_no_cls":
            to_iter = units_dict["num_groups"]
        else:
            to_iter = len(fnames["Spike"])
        for i in range(to_iter):
            if units_dict is not None:
                params = split_dict(units_dict, i)
            else:
                params = {}
            self.units.append_new(params)
            if data_loader is not None:
                self.units[-1].set_source_file(
                    {"Spike": fnames["Spike"][i], "Clusters": fnames["Clusters"][i]}
                )
                self.units[-1].set_loader(data_loader)

    if "spatial" in self.param_handler.keys() or use_all:
        self.spatial = Spatial()
        self.available.append("spatial")
        if data_loader is not None:
            self.spatial.set_source_file(fnames["Spatial"])
            self.spatial.set_loader(data_loader)

    self._parse_source_files()

    if load:
        self.load()

    self.valid = True
