import ast


def dict_from_string(str_):
    """
    Convert a string to a dictionary.

    Parameters
    ----------
    str_ : str
        The string to convert.

    Returns
    -------
    dict
        The dictionary.

    """
    if str_ is not None and str_ != "":
        try:
            loader_kwargs = ast.literal_eval(str_)
        except Exception as e:
            print(f"Error parsing {str_} as a dictionary")
            raise e
    else:
        loader_kwargs = {}
    return loader_kwargs
