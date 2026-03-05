import pandas as pd
import pytest

from algorithms.navigation import (
    build_company_selection_data,
    get_go_up_data,
    get_group_max_values,
    get_level_0_data,
    reset_hierarchy,
    select_grandparent,
    update_df_selected,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def df_hierarchy():
    """
    Minimal hierarchy with 3 levels:

    Level 0  id=1  "Alpha Group"   (root, no parent)
    Level 1  id=2  "Alpha Sub"     (child of id=1)
    Level 2  id=3  "Alpha Leaf"    (child of id=2)
    Level 0  id=4  "Beta Group"    (second root, no parent)
    Level 1  id=5  "Beta Sub"      (child of id=4)
    """
    return pd.DataFrame(
        [
            {
                "id": 1,
                "Name": "Alpha Group",
                "Group": "Alpha",
                "level": 0,
                "parent_id": None,
                "has_children": 1,
                "total_turnover": 1000,
                "total_workers": 500,
            },
            {
                "id": 2,
                "Name": "Alpha Sub",
                "Group": "Alpha",
                "level": 1,
                "parent_id": 1,
                "has_children": 1,
                "total_turnover": 400,
                "total_workers": 200,
            },
            {
                "id": 3,
                "Name": "Alpha Leaf",
                "Group": "Alpha",
                "level": 2,
                "parent_id": 2,
                "has_children": 0,
                "total_turnover": 100,
                "total_workers": 50,
            },
            {
                "id": 4,
                "Name": "Beta Group",
                "Group": "Beta",
                "level": 0,
                "parent_id": None,
                "has_children": 1,
                "total_turnover": 800,
                "total_workers": 300,
            },
            {
                "id": 5,
                "Name": "Beta Sub",
                "Group": "Beta",
                "level": 1,
                "parent_id": 4,
                "has_children": 0,
                "total_turnover": 200,
                "total_workers": 80,
            },
        ]
    )


# ---------------------------------------------------------------------------
# reset_hierarchy
# ---------------------------------------------------------------------------


class TestResetHierarchy:
    def test_returns_only_level_0_rows(self, df_hierarchy):
        result = reset_hierarchy(df_hierarchy)
        assert list(result["level"].unique()) == [0]

    def test_returns_all_root_groups(self, df_hierarchy):
        result = reset_hierarchy(df_hierarchy)
        assert set(result["Name"]) == {"Alpha Group", "Beta Group"}

    def test_index_is_reset(self, df_hierarchy):
        result = reset_hierarchy(df_hierarchy)
        assert list(result.index) == list(range(len(result)))

    def test_does_not_mutate_input(self, df_hierarchy):
        original_len = len(df_hierarchy)
        reset_hierarchy(df_hierarchy)
        assert len(df_hierarchy) == original_len


# ---------------------------------------------------------------------------
# update_df_selected
# ---------------------------------------------------------------------------


class TestUpdateDfSelected:
    def test_filters_by_group_level_and_parent(self, df_hierarchy):
        result = update_df_selected(
            df_hierarchy, "Alpha", selected_level=1, parent_id=1
        )
        assert len(result) == 1
        assert result.loc[0, "Name"] == "Alpha Sub"

    def test_returns_empty_for_unknown_group(self, df_hierarchy):
        result = update_df_selected(
            df_hierarchy, "Unknown", selected_level=0, parent_id=None
        )
        assert result.empty

    def test_returns_empty_for_wrong_parent(self, df_hierarchy):
        result = update_df_selected(
            df_hierarchy, "Alpha", selected_level=1, parent_id=99
        )
        assert result.empty

    def test_index_is_reset(self, df_hierarchy):
        result = update_df_selected(df_hierarchy, "Beta", selected_level=1, parent_id=4)
        assert list(result.index) == list(range(len(result)))


# ---------------------------------------------------------------------------
# get_level_0_data
# ---------------------------------------------------------------------------


class TestGetLevel0Data:
    def test_returns_dict(self, df_hierarchy):
        result = get_level_0_data(df_hierarchy)
        assert isinstance(result, dict)

    def test_contains_expected_keys(self, df_hierarchy):
        expected_keys = {
            "df_selected",
            "selected_group",
            "selected_company",
            "selected_level",
            "total_turnover",
            "total_workers",
            "parent_id",
            "max_group_turnover",
            "max_group_workers",
            "is_go_up_active",
            "turnover_metric",
            "workers_metric",
        }
        result = get_level_0_data(df_hierarchy)
        assert expected_keys.issubset(result.keys())

    def test_resets_to_level_0(self, df_hierarchy):
        result = get_level_0_data(df_hierarchy)
        assert result["selected_level"] == 0

    def test_go_up_is_inactive(self, df_hierarchy):
        result = get_level_0_data(df_hierarchy)
        assert result["is_go_up_active"] is False

    def test_totals_reset_to_zero(self, df_hierarchy):
        result = get_level_0_data(df_hierarchy)
        assert result["total_turnover"] == 0
        assert result["total_workers"] == 0

    def test_parent_id_is_none(self, df_hierarchy):
        result = get_level_0_data(df_hierarchy)
        assert result["parent_id"] is None

    def test_df_selected_contains_only_root_rows(self, df_hierarchy):
        result = get_level_0_data(df_hierarchy)
        assert set(result["df_selected"]["level"].unique()) == {0}


# ---------------------------------------------------------------------------
# get_group_max_values
# ---------------------------------------------------------------------------


class TestGetGroupMaxValues:
    def test_returns_correct_max_for_alpha(self, df_hierarchy):
        turnover, workers = get_group_max_values(df_hierarchy, "Alpha")
        assert turnover == 1000
        assert workers == 500

    def test_returns_correct_max_for_beta(self, df_hierarchy):
        turnover, workers = get_group_max_values(df_hierarchy, "Beta")
        assert turnover == 800
        assert workers == 300

    def test_raises_for_unknown_group(self, df_hierarchy):
        with pytest.raises((IndexError, KeyError)):
            get_group_max_values(df_hierarchy, "NonExistent")


# ---------------------------------------------------------------------------
# build_company_selection_data
# ---------------------------------------------------------------------------


class TestBuildCompanySelectionData:
    def test_returns_dict_with_expected_keys(self, df_hierarchy):
        result = build_company_selection_data(
            df_hierarchy,
            group="Alpha",
            level=1,
            turnover=400,
            workers=200,
            parent_id=1,
        )
        expected_keys = {
            "selected_group",
            "selected_level",
            "total_turnover",
            "total_workers",
            "parent_id",
            "max_group_turnover",
            "max_group_workers",
            "df_selected",
            "is_go_up_active",
            "turnover_metric",
            "workers_metric",
        }
        assert expected_keys.issubset(result.keys())

    def test_values_are_stored_correctly(self, df_hierarchy):
        result = build_company_selection_data(
            df_hierarchy,
            group="Alpha",
            level=1,
            turnover=400,
            workers=200,
            parent_id=1,
        )
        assert result["selected_group"] == "Alpha"
        assert result["selected_level"] == 1
        assert result["total_turnover"] == 400
        assert result["total_workers"] == 200
        assert result["parent_id"] == 1

    def test_max_values_come_from_group_root(self, df_hierarchy):
        result = build_company_selection_data(
            df_hierarchy,
            group="Alpha",
            level=1,
            turnover=400,
            workers=200,
            parent_id=1,
        )
        assert result["max_group_turnover"] == 1000
        assert result["max_group_workers"] == 500

    def test_go_up_is_always_active(self, df_hierarchy):
        result = build_company_selection_data(
            df_hierarchy,
            group="Beta",
            level=1,
            turnover=200,
            workers=80,
            parent_id=4,
        )
        assert result["is_go_up_active"] is True

    def test_df_selected_matches_level_and_parent(self, df_hierarchy):
        result = build_company_selection_data(
            df_hierarchy,
            group="Alpha",
            level=1,
            turnover=400,
            workers=200,
            parent_id=1,
        )
        df = result["df_selected"]
        assert len(df) == 1
        assert df.loc[0, "Name"] == "Alpha Sub"


# ---------------------------------------------------------------------------
# select_grandparent
# ---------------------------------------------------------------------------


class TestSelectGrandparent:
    def test_returns_grandparent_index(self, df_hierarchy):
        # df_current is at level 2 (Alpha Leaf, parent_id=2)
        df_current = df_hierarchy[df_hierarchy["id"] == 3].reset_index(drop=True)
        gdp_index = select_grandparent(df_hierarchy, df_current)
        assert df_hierarchy.loc[gdp_index, "id"] == 1

    def test_grandparent_is_level_0(self, df_hierarchy):
        df_current = df_hierarchy[df_hierarchy["id"] == 3].reset_index(drop=True)
        gdp_index = select_grandparent(df_hierarchy, df_current)
        assert df_hierarchy.loc[gdp_index, "level"] == 0


# ---------------------------------------------------------------------------
# get_go_up_data
# ---------------------------------------------------------------------------


class TestGetGoUpData:
    def test_returns_dict(self, df_hierarchy):
        df_current = df_hierarchy[df_hierarchy["id"] == 3].reset_index(drop=True)
        result = get_go_up_data(df_hierarchy, df_current, current_level=2)
        assert isinstance(result, dict)

    def test_decrements_level(self, df_hierarchy):
        df_current = df_hierarchy[df_hierarchy["id"] == 3].reset_index(drop=True)
        result = get_go_up_data(df_hierarchy, df_current, current_level=2)
        assert result["selected_level"] == 1

    def test_parent_becomes_selected_group(self, df_hierarchy):
        # Going up from level-2 Alpha Leaf should land on Alpha Sub's parent context
        df_current = df_hierarchy[df_hierarchy["id"] == 3].reset_index(drop=True)
        result = get_go_up_data(df_hierarchy, df_current, current_level=2)
        assert result["selected_group"] == "Alpha"

    def test_go_up_remains_active(self, df_hierarchy):
        df_current = df_hierarchy[df_hierarchy["id"] == 3].reset_index(drop=True)
        result = get_go_up_data(df_hierarchy, df_current, current_level=2)
        assert result["is_go_up_active"] is True
