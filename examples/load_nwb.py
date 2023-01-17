from pathlib import Path
import simuran

PATH_TO_NWB = Path("example.nwb")

recording = simuran.Recording()
recording.loader = simuran.loader("NWB")
recording.attrs["source_file"] = PATH_TO_NWB
recording.parse_metadata()
recording.load()
recording.inspect()
