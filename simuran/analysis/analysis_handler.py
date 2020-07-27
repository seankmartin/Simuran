"""This module provides functionality for performing large batch analysis."""

from indexed import IndexedOrderedDict


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

    Parameters
    ----------
    verbose : bool, optional
        Sets the value of the verbose attribute, defaults to False.

    """

    def __init__(self, verbose=False):
        """See help(AnalysisHandler)."""
        self.fns_to_run = []
        self.fn_params_list = []
        self.fn_kwargs_list = []
        self.results = IndexedOrderedDict()
        self.verbose = False

    def run_all_fns(self):
        """Run all of the established functions."""
        fn_zipped = zip(self.fns_to_run, self.fn_params_list, self.fn_kwargs_list)
        for (fn, fn_params, fn_kwargs) in fn_zipped:
            self._run_fn(fn, *fn_params, **fn_kwargs)

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
