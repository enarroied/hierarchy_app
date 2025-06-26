import pandas as pd

import taipy.gui.builder as tgb
from taipy.gui import Gui


def get_level_0(state):
    with state as s:
        df_hierarchy = s.df_hierarchy.copy()
        s.df_selected = df_hierarchy[df_hierarchy["level"] == 0].reset_index(drop=True)
        s.selected_group = "All Groups"
        s.selected_company = "All Companies"
        s.selected_level = 0
        s.total_turnover = 0
        s.total_workers = 0
        s.parent_id = None


def drill_down_row(state, var, value):
    selected_row = value.get("index")
    with state as s:
        df_previous = s.df_selected.copy()
        df_hierarchy = s.df_hierarchy.copy()
        s.selected_level += 1

        s.selected_group = df_previous.loc[selected_row, "Group"]
        s.selected_company = df_previous.loc[selected_row, "Name"]
        s.total_turnover = df_previous.loc[selected_row, "total_turnover"]
        s.total_workers = df_previous.loc[selected_row, "total_workers"]

        s.parent_id = df_previous.loc[selected_row, "id"]

        df_selected = df_hierarchy[
            (df_hierarchy.Group == s.selected_group)
            & (df_hierarchy.level == s.selected_level)
            & (df_hierarchy.parent_id == s.parent_id)
        ].reset_index(drop=True)
        s.df_selected = df_selected


def on_init(state):
    get_level_0(state)


with tgb.Page() as hierarchy_page:
    with tgb.layout("5 1"):
        tgb.text("# Hierarchy ⬆️ ⬇️ App", mode="md")
        tgb.button("Reset", on_action=get_level_0, class_name="plain fullwidth")

    tgb.html("hr")

    with tgb.layout("1 1 1"):
        tgb.part()
        tgb.part()
        tgb.part()

    tgb.table(data="{df_selected}", on_action=drill_down_row)


if __name__ == "__main__":

    df_hierarchy = pd.read_parquet("./data/company_groups.parquet")
    df_selected = None

    selected_company = None
    selected_group = None
    selected_level = None
    total_turnover = None
    total_workers = None

    parent_id = None

    gui = Gui(page=hierarchy_page)
    gui.run(
        use_reloader=True,
        title="Hierarchy ⬆️ ⬇️ App",
        dark_mode=False,
    )
