from indexed import IndexedOrderedDict


class AnalysisHandler:
    def __init__(self):
        self.fns_to_run = []
        self.fn_params_list = []
        self.fn_kwargs_list = []
        self.results = IndexedOrderedDict()

    def run_all_fns(self):
        fn_zipped = zip(
            self.fns_to_run, self.fn_params_list, self.fn_kwargs_list)
        for (fn, fn_params, fn_kwargs) in fn_zipped:
            self._run_fn(fn, *fn_params, **fn_kwargs)

    def reset(self):
        self.reset_func_list()
        self.reset_results()

    def reset_func_list(self):
        self.fns_to_run = []
        self.fn_params_list = []
        self.fn_kwargs_list = []

    def reset_results(self):
        self.results = IndexedOrderedDict()

    def add_fn(self, fn, *args, **kwargs):
        self.fns_to_run.append(fn)
        self.fn_params_list.append(args)
        self.fn_kwargs_list.append(kwargs)

    def _run_fn(self, fn, *args, **kwargs):
        # print("Running {} with params {} kwargs {}".format(
        #     fn, *args, **kwargs))
        result = fn(*args, **kwargs)
        ctr = 0
        save_result = kwargs.get("save_result", True)
        if save_result:
            while (str(fn.__name__) + "_" + str(ctr)) in self.results.keys():
                ctr = ctr + 1
            self.results[str(fn.__name__) + "_" + str(ctr)] = result
        return result

    def __repr__(self):
        return "{} with functions:\n {}, args:\n {}, kwargs:\n {}".format(
            self.__class__.__name__, self.fns_to_run,
            self.fn_params_list, self.fn_kwargs_list)
