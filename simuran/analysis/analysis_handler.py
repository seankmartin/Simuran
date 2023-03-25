"""This module provides functionality for performing large batch analysis."""

import logging
from dataclasses import dataclass, field
import pickle
from typing import Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pandas as pd
from indexed import IndexedOrderedDict
from simuran.core.log_handler import log_exception
from skm_pyutils.table import df_to_file
from mpire import WorkerPool


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
    verbose: bool = False
    handle_errors: bool = False
    pickle_path: Optional[Union[str, "Path"]] = "simuran_analysis.pkl"
    results: IndexedOrderedDict = field(default_factory=IndexedOrderedDict, init=False)
    _was_error: bool = field(repr=False, default=False)

    def run(self, pbar: bool = False, n_jobs: int = 1, save_every: int = 0):
        """
        Run all of the established functions.

        Parameters
        ----------
        pbar : string or bool, optional
            Whether to have a progress bar. Options are
            False (default) no progress bar.
            True a tdqm progress bat
            "notebook" a progress for notebooks
        n_jobs : int, optional
            The number of jobs to run in parallel, by default 1
            Uses mpire.WorkerPool along with a mapping.
            For more complex multiprocessing, directly use mpire.WorkerPool.

        Returns
        -------
        None

        """
        results = []
        self._was_error = False
        for fn_, args_ in zip(self.fns_to_run, self.fn_params_list):
            with WorkerPool(n_jobs=n_jobs) as pool:
                for result in pool.imap(fn_, args_, progress_bar=pbar):
                    self._handle_result(fn_, result)
                    if save_every > 0 and len(self.results) % save_every == 0:
                        self.save_results_to_pickle()
                    results.append(result)

        if self._was_error:
            logging.warning("A handled error occurred while running analysis")
        self._was_error = False
        return results

    def reset(self):
        """Reset this object, clearing results and function list."""
        self.fns_to_run = []
        self.fn_params_list = []
        self.fn_kwargs_list = []
        self.results = IndexedOrderedDict()

    def add_analysis(self, fn, args):
        """
        Add the function fn to the list with the given args and kwargs.

        Parameters
        ----------
        fn : function
            The function to add.
        args : positional arguments
            The list of arguments to run the function with.
            See https://slimmer-ai.github.io/mpire/usage/map/map.html
            For more information on how arguments are handled.

        Returns
        -------
        None

        """
        self.fns_to_run.append(fn)
        self.fn_params_list.append(args)

    def save_results_to_table(self, filename=None, columns=None, from_dict=True):
        """
        Dump analysis results to csv file.

        Parameters
        ----------
        filename : str or Path
            The output path.

        Returns
        -------
        Dataframe
            The resulting dataframe

        """
        if from_dict:
            df = pd.DataFrame.from_dict(self.results, orient="index", columns=columns)
        else:
            df = pd.DataFrame(self.results)

        if filename is not None:
            df_to_file(df, filename)

        return df

    def save_results_to_pickle(self):
        with open(self.pickle_path, "wb") as f:
            pickle.dump(self.results, f)

    def load_results_from_pickle(self):
        with open(self.pickle_path, "rb") as f:
            self.results = pickle.load(f)

    def _handle_result(self, fn_, result):
        ctr = 1
        save_name = str(fn_.__name__)
        while save_name in self.results.keys():
            save_name = f"{str(fn_.__name__)}_{ctr}"
            ctr = ctr + 1
        self.results[save_name] = result
