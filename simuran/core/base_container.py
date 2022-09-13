"""This module holds containers to allow for batch processing."""

from dataclasses import dataclass, field
from typing import Any, Optional, overload

import rich


@dataclass
class GenericContainer:
    """
    A container in SIMURAN, a wrapper of a list.

    This has some extra functionality, such as retrieving
    information from each item in the container,
    or grouping items by property.

    Attributes
    ----------
    container : list
        The underlying list being wrapped.

    """

    container: list = field(repr=False, default_factory=list)

    def load(self) -> None:
        ...
        """Load all items in the container."""

    @overload
    def load(self, idx: int) -> Any:
        ...
        """Load item at index idx and return it."""

    def load(self, idx: Optional[int] = None) -> Any:
        if idx is None:
            for item in self:
                item.load()
        else:
            self[idx].load()
            return self[idx]

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

    def extend(self, iterable):
        """Extend self.container"""
        self.container.extend(iterable)

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

    def split_into_groups(self, prop):
        """
        Split into groups based on property.

        Does not support mutable values (list or dict) in the property list.

        Parameters
        ----------
        prop : str
            The name of the attribute to group by.

        Returns
        -------
        dict : key : (group, index), for key in set(self.get_property(prop))

        """
        out_dict = {}
        for key in list(set(self.get_property(prop))):
            group, indices = self.group_by_property(prop, key)
            out_dict[key] = (group, indices)
        return out_dict

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
        try:
            return [getattr(val, prop) for val in self.container]
        except BaseException:
            return []

    def get_possible_values(self, prop):
        """
        Return a list of all values of val.prop for val in self.

        Parameters
        ----------
        prop : str
            The name of the attribute to retrieve values for.

        Returns
        -------
        set
            All values of prop found in the container.

        """
        return set(self.get_property(prop))

    def get_attrs(self) -> "dict[str, Any]":  # pragma no cover
        return self.__dict__

    def get_attrs_and_methods(self) -> "list[str]":  # pragma: no cover
        class_dir = dir(self)
        return [r for r in class_dir if not r.startswith("_")]

    def inspect(self, methods: bool = False, **kwargs) -> None:  # pragma: no cover
        """Note: could also try objexplore"""
        rich.inspect(self, methods=methods, **kwargs)

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
