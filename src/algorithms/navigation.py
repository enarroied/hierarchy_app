from algorithms import create_linear_gauge


def reset_hierarchy(df_hierarchy):
    """Returns the root-level rows of the hierarchy."""
    return df_hierarchy[df_hierarchy["level"] == 0].reset_index(drop=True)


def update_df_selected(df_hierarchy, selected_group, selected_level, parent_id):
    """Returns the filtered hierarchy rows matching the given group, level and parent."""
    return df_hierarchy[
        (df_hierarchy.Group == selected_group)
        & (df_hierarchy.level == selected_level)
        & (df_hierarchy.parent_id == parent_id)
    ].reset_index(drop=True)


def get_level_0_data(df_hierarchy):
    """Returns the initial state values for the root level view."""
    return {
        "df_selected": reset_hierarchy(df_hierarchy),
        "selected_group": "All Groups",
        "selected_company": "All Companies",
        "selected_level": 0,
        "total_turnover": 0,
        "total_workers": 0,
        "parent_id": None,
        "max_group_turnover": 10,
        "max_group_workers": 10,
        "is_go_up_active": False,
        "turnover_metric": create_linear_gauge(0, 100, title="No company selected"),
        "workers_metric": create_linear_gauge(0, 100, title="No company selected"),
    }


def get_group_max_values(df_hierarchy, group):
    """Returns the max turnover and workers values for the top-level entry of a group."""
    group_root = df_hierarchy[
        (df_hierarchy["Group"] == group) & (df_hierarchy["level"] == 0)
    ]
    return group_root["total_turnover"].iloc[0], group_root["total_workers"].iloc[0]


def build_company_selection_data(
    df_hierarchy, group, level, turnover, workers, parent_id
):
    """
    Computes all derived values when a company/group row is selected.
    Returns a dict ready to be applied to state.
    """
    max_turnover, max_workers = get_group_max_values(df_hierarchy, group)

    return {
        "selected_group": group,
        "selected_level": level,
        "total_turnover": turnover,
        "total_workers": workers,
        "parent_id": parent_id,
        "max_group_turnover": max_turnover,
        "max_group_workers": max_workers,
        "df_selected": update_df_selected(df_hierarchy, group, level, parent_id),
        "is_go_up_active": True,
        "turnover_metric": create_linear_gauge(
            turnover, max_turnover, title="Turnover (company/group)"
        ),
        "workers_metric": create_linear_gauge(
            workers, max_workers, title="Workforce (company/group)"
        ),
    }


def select_grandparent(df_hierarchy, df_current):
    """Returns the index of the grandparent row in df_hierarchy."""
    parent_id = df_current.loc[0, "parent_id"]
    parent_row = df_hierarchy[df_hierarchy["id"] == parent_id].iloc[0]
    grandparent_id = parent_row["parent_id"]
    grandparent_row = df_hierarchy[df_hierarchy["id"] == grandparent_id]
    return grandparent_row.index[0]


def get_go_up_data(df_hierarchy, df_current, current_level):
    """
    Computes the state values needed when navigating one level up.
    Returns None if already at root (level 0 or 1 should use get_level_0_data instead).
    """
    gdp_index = select_grandparent(df_hierarchy, df_current)
    new_level = current_level - 1

    return build_company_selection_data(
        df_hierarchy=df_hierarchy,
        group=df_hierarchy.loc[gdp_index, "Group"],
        level=new_level,
        turnover=df_hierarchy.loc[gdp_index, "total_turnover"],
        workers=df_hierarchy.loc[gdp_index, "total_workers"],
        parent_id=df_hierarchy.loc[gdp_index, "id"],
    )
