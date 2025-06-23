import pandas as pd

import taipy.gui.builder as tgb
from taipy.gui import Gui


def get_level_0(state):
    with state as s:
        df_hierarchy = s.df_hierarchy.copy()
        s.df_selected = df_hierarchy[df_hierarchy["level"] == 0].reset_index(drop=True)


def drill_down_row(state, var, value):
    selected_row = value.get("index")
    print(selected_row)


def on_init(state):
    get_level_0(state)


with tgb.Page() as hierarchy_page:
    tgb.text("# Hierarchy Page", mode="md")
    tgb.html("hr")

    tgb.table(data="{df_selected}", on_action=drill_down_row)


if __name__ == "__main__":

    df_hierarchy = pd.read_parquet("./data/company_groups.parquet")
    df_selected = None

    gui = Gui(page=hierarchy_page)
    gui.run(
        use_reloader=True,
        title="Hierarchy App",
        dark_mode=False,
    )
