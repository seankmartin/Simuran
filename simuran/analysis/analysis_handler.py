"""This module provides functionality for performing large batch analysis."""

from dataclasses import dataclass, field
import logging

from indexed import IndexedOrderedDict
from simuran.core.log_handler import log_exception
from tqdm import tqdm
from tqdm.notebook import tqdm as tqdm_notebook
import pandas as pd
from skm_pyutils.table import df_to_file


@dataclass
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

    fns_to_run: list = field(default_factory=list)
    fn_params_list: list = field(default_factory=list)
    fn_kwargs_list: list = field(default_factory=list)
    results: IndexedOrderedDict = field(default_factory=IndexedOrderedDict)
    verbose: bool = False
    handle_errors: bool = False
    _was_error: bool = field(repr=False, default=False)

    def run_all(self, pbar=False):
        """Alias for run_all_fns."""
        self.run_all_fns(pbar)

    def run_all_fns(self, pbar=False):
        """
        Run all of the established functions.

        Parameters
        ----------
        pbar : string or bool, optional
            Whether to have a progress bar. Options are
            False (default) no progress bar.
            True a tdqm progress bat
            "notebook" a progress for notebooks

        Returns
        -------
        None

        """
        self._was_error = False
        pbar_ = None
        if pbar is True:
            pbar_ = tqdm(range(len(self.fns_to_run)))
        elif pbar == "notebook":
            pbar_ = tqdm_notebook(range(len(self.fns_to_run)))  # pragma no cover

        if pbar_ is not None:
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
        self.fns_to_run = []
        self.fn_params_list = []
        self.fn_kwargs_list = []
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

    def save_results_to_table(self, filename=None):
        """
        Dump analysis results to file with pickle.

        Parameters
        ----------
        filename : str or Path
            The output path.

        Returns
        -------
        Dataframe
            The resulting dataframe

        """
        df = pd.DataFrame.from_dict(self.results, orient="index")

        if filename is not None:
            df_to_file(df, filename)

        return df

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
            print(f"Running {fn} with params {args} kwargs {kwargs}")
        if self.handle_errors:
            try:
                result = fn(*args, **kwargs)
            except BaseException as e:
                log_exception(
                    e, f"Running {fn.__name__} with args {args} and kwargs {kwargs}"
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
                save_name = f"{str(fn.__name__)}_{ctr}"
                ctr = ctr + 1
            self.results[save_name] = result
        return result
