import pytest

from abmodel.models.population import BoxSize


class TestBoxSizeCase:
    """
        Verifies the functionality of the BoxSize namedtuple from population.
    """
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    @pytest.fixture
    def fixture_box_size_instance(self) -> None:
        pytest.test_BoxSize = BoxSize(0, 100, 0, 100)
        pytest.expected = [0, 100, 0, 100]
        pytest.sides = BoxSize._fields

    def test_box_size_instance(self, fixture_box_size_instance):
        """Checks whether all values of the BoxSize are correctly assigned."""
        for side, expected in zip(pytest.sides, pytest.expected):
            test_BoxSize_value = getattr(pytest.test_BoxSize, side)

            assert test_BoxSize_value == expected
