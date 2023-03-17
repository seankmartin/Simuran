def convert_filter(val):
    if val[0] == "<":
        return lambda x, y: x < y
    elif val[0] == ">":
        return lambda x, y: x > y
    elif val[0] == "=":
        return lambda x, y: x == y
    else:
        raise ValueError("Unknown filter type")