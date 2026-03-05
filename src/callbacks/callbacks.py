from taipy.gui import notify

from algorithms import (
    build_company_selection_data,
    get_go_up_data,
    get_level_0_data,
)


def _apply_state(state, data: dict):
    """Helper to bulk-apply a dict of values to Taipy state."""
    for key, value in data.items():
        setattr(state, key, value)


def get_level_0_callback(state):
    """Resets the view to the root hierarchy level."""
    with state as s:
        data = get_level_0_data(s.df_hierarchy.copy())
        _apply_state(s, data)


def select_companies_from_row_callback(
    state, group, company, level, turnover, workers, parent_id
):
    """Updates state after the user selects a company/group row."""
    with state as s:
        s.selected_company = company
        data = build_company_selection_data(
            df_hierarchy=s.df_hierarchy.copy(),
            group=group,
            level=level,
            turnover=turnover,
            workers=workers,
            parent_id=parent_id,
        )
        _apply_state(s, data)


def drill_down_row_callback(state, var, value):
    """Taipy table on-action callback: drills into the subsidiaries of the selected
    row."""
    selected_row = value.get("index")
    with state as s:
        df_previous = s.df_selected.copy()

        if df_previous.loc[selected_row, "has_children"] == 0:
            notify(s, "i", "this company has no subsidiaries")
            return

        select_companies_from_row_callback(
            s,
            group=df_previous.loc[selected_row, "Group"],
            company=df_previous.loc[selected_row, "Name"],
            level=s.selected_level + 1,
            turnover=df_previous.loc[selected_row, "total_turnover"],
            workers=df_previous.loc[selected_row, "total_workers"],
            parent_id=df_previous.loc[selected_row, "id"],
        )


def go_up_callback(state):
    """Navigates one level up in the company hierarchy."""
    with state as s:
        if s.selected_level == 1:
            get_level_0_callback(s)
            return

        data = get_go_up_data(
            df_hierarchy=s.df_hierarchy.copy(),
            df_current=s.df_selected.copy(),
            current_level=s.selected_level,
        )
        _apply_state(s, data)
