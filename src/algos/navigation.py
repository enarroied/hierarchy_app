from algos.charts import create_linear_gauge

from taipy.gui import notify


def reset_hierarchy(state, df_hierarchy):
    state.df_selected = df_hierarchy[df_hierarchy["level"] == 0].reset_index(drop=True)


def update_df_selected(state, df_hierarchy, selected_group, selected_level, parent_id):
    df_selected = df_hierarchy[
        (df_hierarchy.Group == selected_group)
        & (df_hierarchy.level == selected_level)
        & (df_hierarchy.parent_id == parent_id)
    ].reset_index(drop=True)
    state.df_selected = df_selected


def get_level_0(state):
    with state as s:
        df_hierarchy = s.df_hierarchy.copy()
        s.selected_group = "All Groups"
        s.selected_company = "All Companies"
        s.selected_level = 0
        s.total_turnover = 0
        s.total_workers = 0
        s.parent_id = None
        s.max_group_turnover = 10
        s.max_group_workers = 10

        reset_hierarchy(s, df_hierarchy)
        s.is_go_up_active = False

        s.turnover_metric = create_linear_gauge(0, 100, title="No company selected")
        s.workers_metric = create_linear_gauge(0, 100, title="No company selected")


def select_companies_from_row(
    state, df_hierarchy, group, company, level, turnover, workers, parent_id
):
    with state as s:

        s.selected_group = group
        s.selected_company = company
        s.selected_level = level
        s.total_turnover = turnover
        s.total_workers = workers
        s.parent_id = parent_id

        s.max_group_turnover = df_hierarchy[
            (df_hierarchy["Group"] == group) & (df_hierarchy["level"] == 0)
        ]["total_turnover"].iloc[0]
        s.max_group_workers = df_hierarchy[
            (df_hierarchy["Group"] == group) & (df_hierarchy["level"] == 0)
        ]["total_workers"].iloc[0]

        s.turnover_metric = create_linear_gauge(
            turnover, s.max_group_turnover, title="Turnover (company/group)"
        )
        s.workers_metric = create_linear_gauge(
            workers, s.max_group_workers, title="Workforce (company/group)"
        )

        update_df_selected(s, df_hierarchy, group, level, s.parent_id)
        s.is_go_up_active = (
            True  # If we go down or not all the way up, this is alsways True
        )


def drill_down_row(state, var, value):
    selected_row = value.get("index")
    with state as s:
        df_previous = s.df_selected.copy()
        if df_previous.loc[selected_row, "has_children"] == 0:
            notify(s, "i", "this company has no subsidiaries")
            return
        df_hierarchy = s.df_hierarchy.copy()

        s.selected_level += 1
        select_companies_from_row(
            s,
            df_hierarchy=df_hierarchy,
            group=df_previous.loc[selected_row, "Group"],
            company=df_previous.loc[selected_row, "Name"],
            level=s.selected_level,
            turnover=df_previous.loc[selected_row, "total_turnover"],
            workers=df_previous.loc[selected_row, "total_workers"],
            parent_id=df_previous.loc[selected_row, "id"],
        )


def select_grandparent(df_hierarchy, df_current):
    parent_id = df_current.loc[0, "parent_id"]
    parent_row = df_hierarchy[df_hierarchy["id"] == parent_id].iloc[0]
    grandparent_id = parent_row["parent_id"]
    grandparent_row = df_hierarchy[df_hierarchy["id"] == grandparent_id]
    gdp_index = grandparent_row.index[0]
    return gdp_index


def go_up(state):
    with state as s:
        level = s.selected_level
        if level == 1:
            get_level_0(s)
        else:
            df_hierarchy = s.df_hierarchy.copy()
            df_current = s.df_selected.copy()

            gdp_index = select_grandparent(df_hierarchy, df_current)

            s.selected_level -= 1
            select_companies_from_row(
                s,
                df_hierarchy=df_hierarchy,
                group=df_hierarchy.loc[gdp_index, "Group"],
                company=df_hierarchy.loc[gdp_index, "Name"],
                level=s.selected_level,
                turnover=df_hierarchy.loc[gdp_index, "total_turnover"],
                workers=df_hierarchy.loc[gdp_index, "total_workers"],
                parent_id=df_hierarchy.loc[gdp_index, "id"],
            )
