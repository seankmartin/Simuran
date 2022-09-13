import os
import pickle
import pytest
from simuran.recording_container import RecordingContainer
from simuran.loaders.base_loader import MetadataLoader
import pandas as pd


class FakeLoader1(MetadataLoader):
    def load_recording(self, recording):
        recording.data = "FAKE1"


class FakeLoader2(MetadataLoader):
    def load_recording(self, recording):
        recording.data = "FAKE2"


class TestRecordingContainer(object):
    @pytest.fixture
    def rc(self):
        data = {"r_1": ["t1", 55, 0], "r_2": ["t2", 10, 1]}
        columns = ["Name", "Peak", "Passed"]
        table = pd.DataFrame.from_dict(data, orient="index", columns=columns)
        loaders = [FakeLoader1(), FakeLoader2()]

        return RecordingContainer.from_table(table, loaders)

    def test_recording_container_from_table(self, rc):
        assert len(rc) == 2
        assert rc[0].attrs["_index"] == "r_1"

    def test_multiple_loaders(self, rc):
        assert rc[0].data is None
        rc.load(0)
        assert rc.last_loaded.data == "FAKE1"
        rc.load(1)
        assert rc.last_loaded.data == "FAKE2"

    def test_bulk_load(self, rc):
        rc.load_on_fly = False
        for r in rc:
            assert not r.is_loaded()

        rc.load()
        for r in rc:
            assert r.is_loaded()

        assert [r.data for r in rc] == ["FAKE1", "FAKE2"]

        for r in rc:
            r.source_file = "BLAH"

        for r in rc:
            assert not r.is_loaded()

    def test_results(self, rc):
        results = rc.get_results()
        assert len(results) == 2

    def test_source_finder(self, rc):
        rc[0].source_file = "hi"
        rc[1].source_file = "bye"

        assert rc.find_recording_with_source("hi") == 0
        assert rc.find_recording_with_source("bye") == 1
        assert rc.find_recording_with_source("hih") is None

        rc[1].source_file = "hi"
        assert rc.find_recording_with_source("hi") == [0, 1]

    def test_load_iter(self, rc):
        for r in rc.load_iter():
            assert r.is_loaded()

    def test_rc_dump(self, rc):
        rc.load_on_fly = False
        rc.load()
        rc.dump("test.pkl", results_only=False)
        with open("test.pkl", "rb") as f:
            res = pickle.load(f)
        assert res[0].data == "FAKE1"

        os.remove("test.pkl")

    def test_rc_results_save(self, rc):
        rc[0].results = {"H": 1, "B": 2}
        rc[1].results = {"H": 2, "B": 3}

        df = rc.save_results_to_table()
        assert (df.columns == ["H", "B"]).all()
        assert df.iloc[0]["H"] == 1
