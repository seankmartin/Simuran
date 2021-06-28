"""This module provides functionality for performing large batch analysis."""

import logging

from indexed import IndexedOrderedDict
from tqdm import tqdm
from skm_pyutils.py_log import log_exception
from skm_pyutils.py_save import save_mixed_dict_to_csv


class AnalysisHandler(object):
    """
    Hold functions to run and the parameters to use for them.

    Attributes
    ----------
    fns_to_run : list of functions
        The functions to run
    fn_param_list : list of tuples
        The arguments to pass to these functions.
        The arguments are passed in order, so these are positional.
    fn_kwargs_list : list of dicts
        Keyword arguments to pass to the functions to run.
    results : indexed.IndexedOrderedDict
        The results of the function calls
    verbose : bool
        Whether to print more information while running the functions.
    handle_errors : bool
        Whether to handle errors during runtime of underlying functions,
        or to crash on error.

    Parameters
    ----------
    verbose : bool, optional
        Sets the value of the verbose attribute, defaults to False.
    handle_errors : bool, optional
        Sets the value of the handle_errors attribute, defaults to False.

    """

    def __init__(self, verbose=False, handle_errors=False):
        """See help(AnalysisHandler)."""
        self.fns_to_run = []
        self.fn_params_list = []
        self.fn_kwargs_list = []
        self.results = IndexedOrderedDict()
        self.verbose = verbose
        self.handle_errors = handle_errors
        self._was_error = False

    def set_handle_errors(self, handle_errors):
        """Set the value of self.handle_errors."""
        self.handle_errors = handle_errors

    def set_verbose(self, verbose):
        """Set the value of self.verbose."""
        self.verbose = verbose

    def get_results(self):
        """Return the results."""
        return self.results

    def run_all(self):
        """Alias for run_all_fns."""
        self.run_all_fns()

    def run_all_fns(self, pbar=False):
        """Run all of the established functions."""
        self._was_error = False
        if pbar:
            pbar_ = tqdm(range(len(self.fns_to_run)))
            for i in pbar_:
                fn = self.fns_to_run[i]
                fn_params = self.fn_params_list[i]
                fn_kwargs = self.fn_kwargs_list[i]
                self._run_fn(fn, *fn_params, **fn_kwargs)
        else:
            fn_zipped = zip(self.fns_to_run, self.fn_params_list, self.fn_kwargs_list)
            for (fn, fn_params, fn_kwargs) in fn_zipped:
                self._run_fn(fn, *fn_params, **fn_kwargs)
        if self._was_error:
            logging.warning("A handled error occurred while running analysis")
        self._was_error = False

    def reset(self):
        """Reset this object, clearing results and function list."""
        self.reset_func_list()
        self.reset_results()

    def reset_func_list(self):
        """Reset all functions and parameters."""
        self.fns_to_run = []
        self.fn_params_list = []
        self.fn_kwargs_list = []

    def reset_results(self):
        """Reset the results."""
        self.results = IndexedOrderedDict()

    def add_fn(self, fn, *args, **kwargs):
        """
        Add the function fn to the list with the given args and kwargs.

        Parameters
        ----------
        fn : function
            The function to add.
        *args : positional arguments
            The positional arguments to run the function with.
        **kwargs : keyword arguments
            The keyword arguments to run the function with.

        Returns
        -------
        None

        """
        self.fns_to_run.append(fn)
        self.fn_params_list.append(args)
        self.fn_kwargs_list.append(kwargs)

    def save_results(self, output_location):
        with open(output_location, "w") as f:
            print("Saving results to {}".format(output_location))
            for k, v in self.results.items():
                f.write(k.replace(" ", "_").replace(",", "_") + "\n")
                o_str = save_mixed_dict_to_csv(v, None, save=False)
                f.write(o_str)

    def _run_fn(self, fn, *args, **kwargs):
        """
        Run the function with *args and **kwargs, not usually publicly called.

        Pass simuran_save_result as a keyword argument to control
        if the result of the function is saved or not.

        Parameters
        ----------
        fn : function
            The function to run.

        Returns
        -------
        object
            The return value of the function

        """
        if self.verbose:
            print("Running {} with params {} kwargs {}".format(fn, *args, **kwargs))
        if self.handle_errors:
            try:
                result = fn(*args, **kwargs)
            except BaseException as e:
                log_exception(
                    e,
                    "Running {} with args {} and kwargs {}".format(
                        fn.__name__, args, kwargs
                    ),
                )
                self._was_error = True
                result = "SIMURAN-ERROR"
        else:
            result = fn(*args, **kwargs)

        ctr = 1
        save_result = kwargs.get("simuran_save_result", True)
        save_name = str(fn.__name__)
        if save_result:
            while save_name in self.results.keys():
                save_name = str(fn.__name__) + "_{}".format(ctr)
                ctr = ctr + 1
            self.results[save_name] = result

        return result

    def __str__(self):
        """Call on print."""
        return "{} with functions:\n {}, args:\n {}, kwargs:\n {}".format(
            self.__class__.__name__,
            self.fns_to_run,
            self.fn_params_list,
            self.fn_kwargs_list,
        )
