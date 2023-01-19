from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from one.api import ONE
import one
from brainbox.io.one import SpikeSortingLoader
from ibllib.atlas import AllenAtlas

from simuran.loaders.base_loader import MetadataLoader

if TYPE_CHECKING:
    from simuran import Recording


@dataclass
class OneAlyxLoader(MetadataLoader):
    """
    Load One alyx data from online/cache.

    Attributes
    ----------
    one : ONE
        The ONE alyx instance
    atlas : AllenAtlas
        The allen brain atlas to use to associate data with.
    cache_directory : str
        The path to the directory to store data in.

    """

    one: Optional["ONE"] = None
    atlas: Optional["AllenAtlas"] = None
    cache_directory: Optional[str] = None

    @classmethod
    def from_cache(cls, cache_directory: str):
        self = cls(cache_directory=cache_directory)
        self.create_cache()
        return self

    def create_cache(self):
        one_instance = ONE(
            base_url="https://openalyx.internationalbrainlab.org",
            password="international",
            silent=True,
            cache_dir=self.cache_directory,
        )
        one.params.CACHE_DIR_DEFAULT = self.cache_directory
        self.one = one_instance
        if self.atlas is None:
            self.atlas = AllenAtlas()
        self.sessions = self.one.alyx.rest("insertions", "list")
        self._probe_dict = {}
        for s in self.sessions:
            self._probe_dict.setdefault(s["session"], []).append(s["id"])

    def find_eid(self, lab, subject, details=True):
        return self.one.search(lab=lab, subject=subject, details=details)

    def describe_dataset(self, eid: str):
        return self.one.list_datasets(eid=eid, collection="alf", details=True)

    def load_recording(self, recording: "Recording") -> "Recording":
        id_ = recording.attrs.get("session")
        if id_ is None:
            id_ = recording.attrs.get("experiment_id")
        if id_ is None:
            raise KeyError("No id or experiment_id set in recording.attrs")
        recording.data = self._download_data(recording.attrs["experiment_id"])
        return recording

    def _download_data(self, eid):
        session_data = [
            "trials",
            "wheels",
            "wheelMoves",
            "licks",
            "leftCamera",
            "bodyCamera",
            "rightCamera",
            "leftROIMotionEnergy",
            "bodyROIMotionEnergy",
            "rightROIMotionEnergy",
        ]

        return_dict = {}
        for sd in session_data:
            try:
                return_dict[sd] = self.one.load_object(eid, sd, collection="alf")
            except Exception:
                continue

        for pid in self._probe_dict[eid]:
            name = self.one.alyx.rest("insertions", "list", id=pid)[0]["name"]
            return_dict[f"{name}"] = self._get_probe_data(pid)

        return_dict["full_details"] = self.one.get_details(eid, full=True)
        return return_dict

    def _get_probe_data(self, pid):
        # Alternatively, one can instantiate the spike sorting loader using the session unique identifier eid and the probe name pname
        sl = SpikeSortingLoader(pid=pid, one=self.one, atlas=self.atlas)
        spikes, clusters, channels = sl.load_spike_sorting()
        clusters = sl.merge_clusters(spikes, clusters, channels)

        return clusters
