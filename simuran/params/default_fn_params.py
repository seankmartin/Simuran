from skm_pyutils.py_plot import GridFig

grid_fig1 = GridFig(rows=3, cols=6, traverse_rows=False)
grid_fig2 = GridFig(rows=3, cols=6, traverse_rows=False)


def run(recording_container, idx, figures):
    arguments = {}
    if idx == 5:
        arguments["frate"] = {
            "0": [3, 1],
            "1": [10, 1]
        }
        arguments["place_field"] = {
            "0": [figures[0], 3, 1],
            "1": [figures[1], 10, 1]
        }
    else:
        arguments["frate"] = {
            "0": [3, 1],
            "1": [11, 1]
        }
        arguments["place_field"] = {
            "0": [figures[0], 3, 1],
            "1": [figures[1], 11, 1]
        }
    return arguments


save_list = []
save_list.append(("results", "frate_0"))
save_list.append(("results", "frate_1"))

import simuran.analysis.custom.nc as nc
functions = [nc.frate, nc.place_field]

output_names = ["3_1_rate", "11_1_rate"]

figs = [grid_fig1, grid_fig2]
fig_names = ["3_1_ratemap.png", "11_1_ratemap.png"]

fn_params = {
    "run": functions,
    "args": run,
    "save": save_list,
    "names": output_names,
    "figs": figs,
    "fignames": fig_names
}
