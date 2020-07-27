"""This module holds containers to allow for batch processing."""
from abc import ABC, abstractmethod
import os
import copy

import numpy as np

from simuran.base_class import BaseSimuran
from skm_pyutils.py_save import save_mixed_dict_to_csv
from skm_pyutils.py_save import save_dicts_to_csv


class AbstractContainer(ABC):
    """
    A abstract class container in SIMURAN, really a wrapper of a list.

    This has some extra functionality, such as retrieving
    information from each item in the container,
    or grouping items by property.

    Any subclass must implement the _create_new method,
    which just describes how a new item is added.
    For example, it could simply be return params if nothing is done.

    Attributes
    ----------
    container : list
        The underlying list being wrapped.

    """

    def __init__(self):
        """See help(AbstractContainer)."""
        self.container = []
        super().__init__()

    @abstractmethod
    def _create_new(self, params):
        """
        Create a new item to add to the container.

        Parameters
        ----------
        params : obj
            Anything needed for instantiating the object.

        """
        pass

    def load(self):
        """Iterate and load each object in the container."""
        for item in self:
            item.load()

    def append(self, item):
        """
        Append item to self.container.

        Parameters
        ----------
        item : object
            The item to append.

        Returns
        -------
        None

        """
        self.container.append(item)

    def append_new(self, params):
        """
        Append a new item to self.container using _create_new.

        Parameters
        ----------
        params : object
            Parameter object passed to _create_new.

        Returns
        -------
        None

        See Also
        --------
        simuran.base_container._create_new

        """
        to_add = self._create_new(params)
        self.append(to_add)

    def group_by_property(self, prop, value):
        """
        Return all items in the container with item.prop == value.

        Parameters
        ----------
        prop : str
            The name of the attribute to group by.
        value : object
            The value of the property to group by.

        Returns
        -------
        group : list of objects
            The items in the container satisfying the conditions.
        indices : list of int
            The index of each item in the container satisfying the conditions.

        """
        group = []
        indices = []
        for i, val in enumerate(self):
            if getattr(val, prop) == value:
                group.append(val)
                indices.append(i)
        return group, indices

    def get_property(self, prop):
        """
        Return a list as item.prop for prop in self.

        Parameters
        ----------
        prop : str
            The name of the attribute to retrieve from each item.

        Returns
        -------
        list
            The value of the property for each item in the container.

        """
        return [getattr(val, prop) for val in self.container]

    def get_possible_values(self, prop):
        used = set()
        to_return = []
        for val in self.container:
            x = getattr(val, prop)
            if x not in used:
                to_return.append(x)
                used.add(x)
        return to_return

    def save_single_data(
        self,
        attr_list,
        friendly_names=None,
        idx_list=None,
        out_dir_list=None,
        name_list=None,
    ):
        """
        Save attributes to one file per object in the container.

        Currently dict, np.ndarray, and list are supported outputs.
        save_summary_data should be preferred if all the data could fit in
        a single row for each item in the container.

        Parameters
        ----------
        attr_list : list of tuples
            The list of attributes to obtain for each object in the container
        friendly_names : list of str, optional
            What to name the values retrieved from attr_list, by default None
        idx_list : list of int, optional
            A subset of indices to get data for in the container, by default uses all
        out_dir_list : list of str, optional
            Paths to directories to save results to, by default cwd + "sim_results"
        name_list : list of str, optional
            Names of the files to save, by default "sim_results{}.csv".format(i)

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If name_list or out_dir_list is provided but not the same size as idx_list.

        See also
        --------
        simuran.base_container.data_from_attr_list

        """
        if idx_list is None:
            idx_list = [i for i in range(len(self))]

        if name_list is None:
            name_list = ["sim_results" + str(i) + ".csv" for i in idx_list]
        elif len(name_list) != len(idx_list):
            raise ValueError("Number of names must match number of items")

        if out_dir_list is None:
            out_dir_list = [
                os.path.join(os.getcwd(), "sim_results") for i in range(len(idx_list))
            ]
        elif len(out_dir_list) != len(idx_list):
            raise ValueError(
                "Number of output directories must match the number of items"
            )

        elif isinstance(out_dir_list, "str"):
            out_dir_list = [out_dir_list] * len(idx_list)

        for i in idx_list:
            data = self.data_from_attr_list(
                attr_list, idx=i, friendly_names=friendly_names
            )
            save_mixed_dict_to_csv(data, out_dir_list[i], name_list[i])

    def save_summary_data(self, location, attr_list, friendly_names=None, decimals=3):
        """
        Save attributes to one file for the whole container, each row is an object.

        Parameters
        ----------
        location : str
            Path to the location to save the data to
        attr_list : list of tuples
            Attributes to save.
        friendly_names : list of str, optional
            The names of the attributes to save, by default None
        decimals : int, optional
            The number of decimal places to save outputs with, by default 3

        Returns
        -------
        None

        See also
        --------
        simuran.base_container.data_from_attr_list

        """
        attr_list = [("source_dir",), ("source_name",)] + attr_list
        for i in range(len(self)):
            if self[i].source_file is not None:
                self[i].source_dir = os.path.dirname(self[i].source_file)
                self[i].source_name = os.path.basename(self[i].source_file)
            else:
                self[i].source_dir = None
                self[i].source_name = None
        if friendly_names is not None:
            friendly_names = ["Recording directory", "Recording name"] + friendly_names

        data_list = self.data_from_attr_list(
            attr_list, friendly_names=friendly_names, decimals=decimals
        )
        save_dicts_to_csv(location, data_list)

    def data_from_attr_list(self, attr_list, friendly_names=None, idx=None, decimals=3):
        """
        Retrieve attr_list from each item in the container.

        See simuran.base_class.data_dict_from_attr_list for the
        description of the attributes list to be provided.

        Parameters
        ----------
        attr_list : list of tuples
            The attributes to retrieve.
        friendly_names : list of str, optional
            The names for the attributes, by default None
        idx : [type], optional
            A specific index to retrieve data for, by default retrieves all
        decimals : int, optional
            The number of decimal places to save outputs with, by default 3

        Returns
        -------
        list of dict or dict
            A dict is returned if idx is not None, otherwise list of dict.
            This contains the data retrieved from the attributes list.

        Raises
        ------
        ValueError
            If friendly names is provided but not the same size as attr_list.

        See also
        --------
        simuran.base_class.data_dict_from_attr_list

        """
        if len(friendly_names) != len(attr_list):
            friendly_names = None

        def get_single(item, attr_list):
            if isinstance(item, BaseSimuran):
                data = item.data_dict_from_attr_list(attr_list, friendly_names)
                try:
                    round(data, decimals)
                except BaseException:
                    try:
                        data = np.round(data, decimals)
                    except BaseException:
                        try:
                            for key, value in data.items():
                                try:
                                    data[key] = round(value, decimals)
                                except BaseException:
                                    pass
                        except BaseException:
                            pass
            else:
                raise ValueError(
                    "data_from_attr_list is only called on BaseSimuran objects"
                )
            return data

        if idx is None:
            data_out = []
            for item in self:
                data_out.append(get_single(item, attr_list))
        else:
            data_out = get_single(self[idx], attr_list)
        return data_out

    def sort(self, key, reverse=False):
        """
        Sort the container in place.

        Parameters
        ----------
        sort_fn : function
            The function to use as the key in the sorted function
        reverse : bool, optional
            If the sorting should be applied in reverse, by default False

        Returns
        -------
        None

        """
        self.container = sorted(self.container, key=key, reverse=reverse)

    def subsample(self, idx_list=None, interactive=False, prop=None, inplace=False):
        """
        Subsample the container, optionally in place.

        Parameters
        ----------
        idx_list : list of int, optional
            The list to subsample, by default None.
            Only pass None if interactive is set to True.
        interactive : bool, optional
            Whether to launch an interactive prompt for sub-sampling, by default False
        prop : str, optional
            An attribute of the the items in the container, by default None.
            This can be used in the interactive mode to help identify the recordings.
        inplace : bool, optional
            Perform the subsampling in place, or return a copy, by default False

        Returns
        -------
        list of int, or simuran.base_container.AbstractContainer
            A container with the subsampled items if inplace is False.
            The indices of the items subsampled from the container if inplace is True

        """
        if interactive:
            if prop is None:
                full_list = self.container
            else:
                full_list = self.get_property(prop)
            print("Items to sample from:")
            for i, item in enumerate(full_list):
                print("{}: {}".format(i + 1, item))
            indices = input(
                "Please enter the number of the items you want to "
                + "keep seperated by spaces. Enter empty to keep all.\n"
            )
            if indices == "":
                return [i for i in range(len(self))]
            indices = indices.strip().split(" ")
            idx_list = [int(i) - 1 for i in indices]
        if inplace:
            self.container = [self.container[i] for i in idx_list]
            return idx_list
        else:
            new_instance = copy.copy(self)
            new_instance.container = [self.container[i] for i in idx_list]
            return new_instance

    def __getitem__(self, idx):
        """Retrive the object at the specified index from the container."""
        return self.container[idx]

    def __setitem__(self, idx, value):
        """Set the value at the specified index."""
        self.container[idx] = value

    def __len__(self):
        """Get the number of items in the container."""
        return len(self.container)

    def __iter__(self):
        """Iterate over the items in the container."""
        return iter(self.container)

    def __str__(self):
        """Call on print."""
        return "{} with {} elements:\n{}".format(
            self.__class__.__name__, len(self), self.container
        )


class GenericContainer(AbstractContainer):
    """
    A subclass of AbstractContainer where each item in the container has the same type.

    Attributes
    ----------
    cls : class
        The class of each item in the container.

    """

    def __init__(self, cls):
        """See help(GenericContainer)."""
        self.cls = cls
        super().__init__()

    def _create_new(self, params):
        """
        Create a new entry to be placed in the container.

        Parameters
        ----------
        params : object
            The parameters to use if class has a setup function,
            otherwise self.cls(*params) is called.

        Returns
        -------
        object
            The created object, has type self.cls

        """
        try:
            new = self.cls()
        except BaseException:
            new = self.cls(*params)

        if hasattr(new, "setup"):
            new.setup(params)
            return new
        else:
            return new
