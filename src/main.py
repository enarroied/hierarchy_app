import pandas as pd

import taipy.gui.builder as tgb
from taipy.gui import Gui, notify


def reset_hierarchy(state, df_hierarchy):
    state.df_selected = df_hierarchy[df_hierarchy["level"] == 0].reset_index(drop=True)


def update_df_selected(state, df_hierarchy, selected_group, selected_level, parent_id):
    df_selected = df_hierarchy[
        (df_hierarchy.Group == selected_group)
        & (df_hierarchy.level == selected_level)
        & (df_hierarchy.parent_id == parent_id)
    ].reset_index(drop=True)
    state.df_selected = df_selected


def update_values(
    state,
    group,
    company,
    level,
    turnover,
    workers,
    parent_id,
):
    with state as s:
        s.selected_group = group
        s.selected_company = company
        s.selected_level = level
        s.total_turnover = turnover
        s.total_workers = workers
        s.parent_id = parent_id


def get_level_0(state):
    with state as s:
        df_hierarchy = s.df_hierarchy.copy()
        update_values(
            s,
            group="All Groups",
            company="All Companies",
            level=0,
            turnover=0,
            workers=0,
            parent_id=None,
        )
        reset_hierarchy(s, df_hierarchy)
        s.is_go_up_active = False


def select_companies_from_row(
    state, df_hierarchy, group, company, level, turnover, workers, parent_id
):
    with state as s:
        update_values(
            s,
            group=group,
            company=company,
            level=level,
            turnover=turnover,
            workers=workers,
            parent_id=parent_id,
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

        group = df_previous.loc[selected_row, "Group"]
        company = df_previous.loc[selected_row, "Name"]
        turnover = df_previous.loc[selected_row, "total_turnover"]
        workers = df_previous.loc[selected_row, "total_workers"]
        parent_id = df_previous.loc[selected_row, "id"]

        s.selected_level += 1
        select_companies_from_row(
            s,
            df_hierarchy=df_hierarchy,
            group=group,
            company=company,
            level=s.selected_level,
            turnover=turnover,
            workers=workers,
            parent_id=parent_id,
        )


def go_up(state):
    with state as s:
        level = s.selected_level
        if level == 1:
            get_level_0(s)
        else:
            pass


def on_init(state):
    get_level_0(state)


with tgb.Page() as hierarchy_page:
    with tgb.layout("5 1"):
        tgb.text("# Hierarchy ⬆️ ⬇️ App", mode="md")
        tgb.button("Reset", on_action=get_level_0, class_name="plain fullwidth")

    tgb.html("hr")

    with tgb.part(id="selected-company"):
        with tgb.layout("1 1 1"):
            with tgb.part(class_name="card"):
                tgb.text(
                    "## **Selected** Company:", mode="md", class_name="color-primary"
                )
                tgb.text(
                    "### {selected_company}", mode="md", class_name="color-secondary"
                )
            tgb.metric("{total_turnover}", title="Turnover for Branch", type="linear")
            tgb.metric("{total_workers}", title="Workers for Branch", type="linear")

        tgb.button(
            "⬆️ Go Up One Level ⬆️",
            on_action=go_up,
            active="{is_go_up_active}",
            class_name="plain fullwidth",
        )
    tgb.table(
        data="{df_selected}",
        page_size=20,
        on_action=drill_down_row,
        columns=[
            "Group",
            "Name",
            "turnover",
            "workers",
            "total_turnover",
            "total_workers",
        ],
        filter=True,
        downloadable=True,
        number_format="%, f",
    )


if __name__ == "__main__":

    df_hierarchy = pd.read_parquet("./data/company_groups.parquet")
    df_selected = None

    selected_company = None
    selected_group = None
    selected_level = None
    total_turnover = None
    total_workers = None

    parent_id = None

    is_go_up_active = False

    gui = Gui(page=hierarchy_page)
    gui.run(
        use_reloader=True,
        title="Hierarchy ⬆️ ⬇️ App",
        dark_mode=False,
    )
