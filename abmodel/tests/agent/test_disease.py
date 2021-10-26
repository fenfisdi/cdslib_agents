import pytest

from pandas import DataFrame
from abmodel.agent.disease import AgentDisease
from abmodel.utils.execution_modes import ExecutionModes


class TestAgentDisease:
    """Unitary tests for AgentDisease class from disease module"""
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    @pytest.fixture()
    def fixture_generate_key_col_iterative(self):
        vul = [
            "High degree",
            "Middle degree",
            "Low degree"
            ]
        st = [
            "Initial stage",
            "Middle stage",
            "Final stage"
            ]
        data = {
            "vulnerability_group": vul,
            "disease_state": st
            }
        df = DataFrame(data)
        expected = [vul + '-' + st for (vul, st) in zip(vul, st)]
        return df, expected

    def test_generate_key_col_iterative(
            self, fixture_generate_key_col_iterative):
        """Verifies whether the column `key` is created on the input DataFrame
        and assigns correct values in iterative mode."""
        df = AgentDisease().generate_key_col(
            fixture_generate_key_col_iterative[0]
            )
        expected = fixture_generate_key_col_iterative[1]

        for i in range(len(expected)):
            assert df['key'][i] == expected[i]

    def test_generate_key_col_vectorized(
            self, fixture_generate_key_col_iterative):
        """Verifies whether the column `key` is created on the input DataFrame
        and assigns correct values in vectorized mode."""
        df = AgentDisease().generate_key_col(
            fixture_generate_key_col_iterative[0], ExecutionModes.vectorized
            )
        expected = fixture_generate_key_col_iterative[1]

        for i in range(len(expected)):
            assert df['key'][i] == expected[i]

    def test_generate_key_col_raise_Exception_error(
            self, fixture_generate_key_col_iterative):
        """Raises a ValueError when one of the columns: `disease_state` or
        `vulnerability_group` is not a column of the input DataFrame"""
        fixture_generate_key_col_iterative[0].pop("disease_state")
        error_message = (
            "df must contain: disease_state, vulnerability_group.\n"
            "disease_state must be checked"
            )

        with pytest.raises(ValueError, match=error_message):
            AgentDisease().generate_key_col(
                fixture_generate_key_col_iterative[0],
                ExecutionModes.vectorized
                )
