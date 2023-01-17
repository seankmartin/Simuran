from dataclasses import dataclass

from simuran.loaders.base_loader import MetadataLoader
from one.api import ONE


@dataclass
class OneAlyxLoader(MetadataLoader):
    """
    Load One alyx data from online/cache.

    Attributes
    ----------
    one : ONE
        The ONE alyx instance

    """

    one: "ONE"

    @classmethod
    def from_local_cache(cls, cache_directory):
        one = ONE(
            base_url="https://openalyx.internationalbrainlab.org",
            password="international",
            silent=True,
            cache_dir=cache_directory,
        )
        return cls(one=one)
