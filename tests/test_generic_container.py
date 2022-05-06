import numpy as np
from simuran.base_container import GenericContainer


def test_numpy_container():
    container = GenericContainer(cls=np.ndarray)
    for i in range(10):
        container.append(np.ones(100) * i)
    for i in range(5):
        container.append(np.zeros(100))

    assert np.all(np.array(container.get_property("size")) == 100)
    assert np.all(container[3] == 3)

    new_container = container.subsample([2, 4, 9], inplace=False)
    new_container[2] = new_container[2] + 6

    assert np.all(new_container[2] == 15)
    assert np.all(new_container[0] == 2)
    assert np.all(container[9] == 9)

    container.sort(key=lambda x: x[0])
    container.subsample(idx_list=[4, 8, 12], inplace=True)
    container[1] = container[1] * 2

    assert np.all(container[0] == 0)
    assert np.all(container[1] == 6)

    container.append(np.zeros(200))
    assert container.get_possible_values("size") == [100, 200]


if __name__ == "__main__":
    test_numpy_container()
