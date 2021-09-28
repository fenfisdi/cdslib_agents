import pytest


from abmodel.models.population import BoxSize


class TestBoxSizeCase():
    """
        Verify the functionality of the BoxSize namedtuple in population module
        developed in the population file, using unitary test with the Python
        testing tool pytest.
    """

    def setup_method(self, method):
        print('==>')
        print(method.__doc__)

    @pytest.fixture
    def fixture_box_size_instance(self, scope = 'method'):
        pytest.test_BoxSize = BoxSize(0, 100, 0, 100)
        pytest.expected = [0, 100, 0, 100]
        pytest.sides = BoxSize._fields


    def test_box_size_instance(self, fixture_box_size_instance):
        """Check all values of the namedtuple BoxSize"""

        for side, expected in zip(pytest.sides, pytest.expected):
            test_BoxSize_value = getattr(pytest.test_BoxSize, side)
            assert test_BoxSize_value == expected
