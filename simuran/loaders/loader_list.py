loaders_dict = {"params_only": "params_only_no_cls"}
try:
    from simuran.loaders.nc_loader import NCLoader
    loaders_dict["nc_loader"] = NCLoader
except Exception as e:
    print("NeuroChaT is not installed")
