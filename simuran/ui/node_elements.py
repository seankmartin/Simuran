import dearpygui.dearpygui as dpg


def create_file_select(label, tooltip="", output=False):
    """
    Create a file select attribute.

    Parameters
    ----------
    label : str
        The label for the file select.
    tooltip : str, optional
        The tooltip for the file select, by default ""
    output : bool, optional
        Whether the file select is an output, by default False

    Returns
    -------
    dict
        The file select attribute.

    """
    if tooltip != "":
        tooltip += " "
    attribute_type = dpg.mvNode_Attr_Output if output else dpg.mvNode_Attr_Static
    contents = [
        dict(
            type="TEXT",
            width=200,
            label=label,
        )
    ]
    return dict(
        label=label,
        attribute_type=attribute_type,
        shape=dpg.mvNode_PinShape_Triangle,
        category="File select",
        contents=contents,
        tooltip=f"{tooltip}Choose the source file by right clicking this box.",
    )


def create_parameter(label, tooltip=None, width=200, type_="TEXT"):
    """
    Create a parameter attribute.

    Parameters
    ----------
    label : str
        The label for the parameter.
    tooltip : str, optional
        The tooltip for the parameter, by default None
    width : int, optional
        The width for the parameter, by default 200
    type_ : str, optional
        either TEXT, INT, or FLOAT, by default "TEXT"

    Returns
    -------
    dict
        The parameter attribute.

    """
    if tooltip is None:
        tooltip = ""
    contents = [
        dict(
            type=type_,
            width=width,
            label=label,
        )
    ]
    return dict(
        label=label,
        attribute_type=dpg.mvNode_Attr_Static,
        category="Parameters",
        contents=contents,
        tooltip=tooltip,
    )


def create_code_block(label, tooltip="Inline Python code", width=200, height=400):
    contents = [
        dict(
            type="TEXT",
            width=width,
            height=height,
            label=label,
            tab_input=True,
            tracked=True,
            multiline=True,
        )
    ]
    return dict(
        label=label,
        attribute_type=dpg.mvNode_Attr_Output,
        shape=dpg.mvNode_PinShape_Triangle,
        category="Code",
        contents=contents,
        tooltip=tooltip,
    )


def create_input(label, hint, tooltip="Connect a source file node.", width=200):
    """
    Create an input attribute.

    Parameters
    ----------
    label : str
        The label for the parameter.
    tooltip : str, optional
        The tooltip for the parameter, by default None
    width : int, optional
        The width for the parameter, by default 200


    Returns
    -------
    dict
        The parameter attribute.

    """
    contents = [
        dict(
            type="TEXT",
            width=width,
            label=label,
            hint=hint,
            readonly=True,
        )
    ]

    return dict(
        label=label,
        attribute_type=dpg.mvNode_Attr_Input,
        shape=dpg.mvNode_PinShape_Triangle,
        category="File input",
        tooltip=tooltip,
        contents=contents,
    )
