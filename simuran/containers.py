"""This module holds containers to allow for batch processing."""
from abc import ABC, abstractmethod
import os

import numpy as np

from simuran.base_class import BaseSimuran
from simuran.base_signal import AbstractSignal
from skm_pyutils.py_path import make_path_if_not_exists
from skm_pyutils.py_save import save_mixed_dict_to_csv
from skm_pyutils.py_save import save_dicts_to_csv


class AbstractContainer(ABC):
    """TODO Put the docstring here."""

    def __init__(self):
        self.container = []
        super().__init__()

    def group_by_property(self, prop, value):
        group = []
        indices = []
        for i, val in enumerate(self):
            if getattr(val, prop) == value:
                group.append(val)
                indices.append(i)
        return group, indices

    def get_property(self, prop):
        return [getattr(val, prop) for val in self.container]

    def __getitem__(self, idx):
        return self.container[idx]

    def __len__(self):
        return len(self.container)

    def __iter__(self):
        return iter(self.container)

    def __repr__(self):
        return "{} with {} elements:\n{}".format(
            self.__class__.__name__, len(self), self.container)

    def load(self):
        for item in self:
            item.load()

    def append(self, item):
        self.container.append(item)

    def append_new(self, params):
        to_add = self._create_new(params)
        self.append(to_add)

    def save_single_data(
            self, attr_list, friendly_names=None, idx_list=None, out_dir_list=None, name_list=None):
        """
        This saves one file per object in the container.

        Currently dict, np.ndarray, and list are supported values.
        """
        if idx_list is None:
            idx_list = [i for i in range(len(self))]

        if name_list == None:
            name_list = ["sim_results" + str(i) + ".csv" for i in idx_list]

        if out_dir_list == None:
            out_dir_list = [
                os.path.join(os.getcwd(), "sim_results")
                for i in range(len(idx_list))]
        elif isinstance(out_dir_list, "str"):
            out_dir_list = [out_dir_list] * len(idx_list)

        for i in idx_list:
            data = self.data_from_attr_list(
                attr_list, idx=i, friendly_names=friendly_names)
            save_mixed_dict_to_csv(data, out_dir_list[i], name_list[i])

    def save_summary_data(self, location, attr_list, friendly_names=None):
        """
        This saves one file for the whole container, each row is an object.
        """
        attr_list = [("source_file",)] + attr_list
        if friendly_names is not None:
            friendly_names = ["Recording file", ] + friendly_names
        data_list = self.data_from_attr_list(
            attr_list, friendly_names=friendly_names)
        save_dicts_to_csv(location, data_list)

    def data_from_attr_list(self, attr_list, friendly_names=None, idx=None):
        def get_single(item, attr_list):
            if isinstance(item, BaseSimuran):
                data = item.data_dict_from_attr_list(attr_list, friendly_names)
            else:
                raise ValueError(
                    "data_from_attr_list is only called on BaseSimuran objects")
            return data

        if idx is None:
            data_out = []
            for item in self:
                data_out.append(get_single(item, attr_list))
        else:
            data_out = get_single(self[idx], attr_list)
        return data_out

    def sort(self, sort_fn, reverse=False):
        self.container = sorted(
            self.container, key=sort_fn, reverse=reverse)

    def subsample(self, idx_list=None, interactive=False, prop=None):
        if interactive:
            if prop is None:
                full_list = self.container
            else:
                full_list = self.get_property(prop)
            print("Items to sample from:")
            for i, item in enumerate(full_list):
                print("{}: {}".format(i + 1, item))
            indices = input(
                "Please enter the number of the items you want to " +
                "keep seperated by spaces. Enter empty to keep all.\n")
            if indices == "":
                return [i for i in range(len(self))]
            indices = indices.strip().split(" ")
            idx_list = [int(i) - 1 for i in indices]
        self.container = [self.container[i] for i in idx_list]
        return idx_list

    @abstractmethod
    def _create_new(self, params):
        pass


class GenericContainer(AbstractContainer):

    def __init__(self, cls):
        self.cls = cls
        super().__init__()

    def _create_new(self, params):
        new = self.cls()
        new.setup(params)
        return new
