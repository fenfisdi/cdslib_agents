import pytest
from numpy import random, histogram, array

from abmodel.utils.distributions import Distribution
from abmodel.utils.helpers.distributions import init_distribution
from abmodel.models.base import DistributionGroup, SimpleDistGroups


class TestDistributionGroup:
    """Unitary test for: DistributionGroup, SimpleDistGroups and
    ComplexDistGroups class in abmodel.models.base"""
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    @pytest.fixture()
    def fixture_DistributionGoup(self):
        name = 'group'
        dist_info_constant = {"dist_title": 'Distribution for group 1',
                                "dist_type": "constant",
                                "constant": 1}

        dist_info_None = {"dist_title": 'Distribution for group 2',
                            "dist_type": None}

        dist_info_empirical_file = {"dist_title": 'Distribution for group 3',
                                    "dist_type": "empirical",
                                    "filename": "data_empirical.txt",
                                    "kwargs": {'kernel': 'gaussian',
                                                'bandwidth': 0.1
                                                }
                                    }
        data_empirical = random.normal(0.0, 0.1, 30)
        dist_info_empirical_data = {"dist_title": 'Distribution for group 4',
                                    "dist_type": "empirical",
                                    "filename": None,
                                    "kwargs": {"data": data_empirical,
                                                'kernel': 'gaussian',
                                                'bandwidth': 0.1
                                                }
                                    }
        dist_info_weights_file = {"dist_title": 'Distribution for group 5',
                                    "dist_type": "weights",
                                    "filename": "data_weights.txt",
                                    "kwargs": {'kernel': 'gaussian',
                                                'bandwidth': 0.1}
                                }
        hist = histogram(random.normal(0.0, 0.1, 30))
        data = list(hist[1])
        X_i = [(data[i] + data[i + 1])/2 for i in range(len(data) - 1)]
        P_i = list(hist[0])
        P_i = [i/30 for i in P_i]
        data = array([X_i, P_i]).T
        dist_info_weights_data = {"dist_title": 'Distribution for group #',
                                "dist_type": "weights",
                                "filename": None,
                                "kwargs": {"data": data,
                                    'kernel': 'gaussian',
                                        'bandwidth': 0.1}
                                }
        dist_info_numpy = {"dist_title": 'Distribution for group 6',
                            "dist_type": "numpy",
                            "dist_name": 'beta',
                            "kwargs": {'a': 1, 'b': 1}
                            }

        list_dict = [dist_info_constant,
                    dist_info_None,
                    dist_info_empirical_file,
                    dist_info_empirical_data,
                    dist_info_weights_file,
                    dist_info_numpy]

        return list_dict, name

    @pytest.fixture()
    def fixture_SimpleDistGroup(self, fixture_DistributionGoup):
        group_info = [dict for dict in fixture_DistributionGoup[0]]
        counter = [i for i in range(len(fixture_DistributionGoup[0]))]
        for dict, i in zip(group_info, counter):
            dict['name'] = 'Group ' + str(i + 1)
        return group_info

    def test_DistributionGroup_from_dict(self, fixture_DistributionGoup):
        """Verifies whether DistributionGroup constructor, assigns dist_info
        and name of the groups as well as initializes `dist` distribution
        dictionary with its respective distribution type from a dictionary."""
        list_dict = fixture_DistributionGoup[0]
        counter = [str(i + 1) for i in range(len(list_dict))]
        for dict, i in zip(list_dict, counter):
            name = 'group ' + i
            print(dict)
            distribution_group = DistributionGroup(name, dict)

            cond = \
                distribution_group.dist_info["dist_type"] == \
                dict["dist_type"] and \
                distribution_group.\
                dist['Distribution for group ' + i].dist_type == \
                dict["dist_type"] and distribution_group.name == name

            assert cond == True

    def test_SimpleDistGroups_from_list(self, fixture_DistributionGoup):
        """Verifies whether DistributionGroup constructor, assigns dist_info
        and name of the groups as well as initializes `dist` distribution
        dictionary with its respective distribution type from a list of
        dictionaries."""
        list_dict = fixture_DistributionGoup[0]
        distribution_group = DistributionGroup(
                            'Groups', fixture_DistributionGoup[0]
                            )

        for i in range(len(distribution_group.dist_info)):
            names = ['group ' + str(i + 1) for i in range(len(list_dict))]
            cond = distribution_group.dist_info[i]["dist_type"] == \
                list_dict[i]["dist_type"] and \
                distribution_group.dist['Distribution for ' + \
                names[i]].dist_type == list_dict[i]["dist_type"] and \
                distribution_group.name == 'Groups'

            assert cond == True

    def test_raise_error_DistributionGroup(self, fixture_DistributionGoup):
        """Verifies whether SimpleDistGroups raise a ValueError when the
        dist_info parameter is not a dictionary or a list"""
        with pytest.raises(ValueError):
            assert DistributionGroup(
                'Error group', tuple(fixture_DistributionGoup[1])
                )

    @pytest.mark.skip(reason = "Minor problem with the constructor of"
                                "SimpleDistGroup")
    def test_SimpleDistGroups_single_dist_title_validation(
            self, fixture_SimpleDistGroup):
        """Verifies the outputs of single_dist_title_validation from
        SimpleDistGroups."""
        expected_dist_title = \
            [dict["dist_title"] for dict in fixture_SimpleDistGroup]
        Groups = SimpleDistGroups(expected_dist_title, fixture_SimpleDistGroup)

