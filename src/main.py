import pandas as pd
from algos.navigation import drill_down_row, get_level_0, go_up

import taipy.gui.builder as tgb
from taipy.gui import Gui

with tgb.Page() as hierarchy_page:
    with tgb.layout("5 1"):
        tgb.text("# Hierarchy ⬆️ ⬇️ App", mode="md")
        tgb.button("Reset", on_action=get_level_0, class_name="plain fullwidth")

    tgb.html("hr")

    with tgb.part(id="selected-group"):
        with tgb.layout("1 1"):
            with tgb.part(class_name="card"):
                tgb.text(
                    "## **Selected** Group:", mode="md", class_name="color-primary"
                )
                tgb.text(
                    "### {selected_group}", mode="md", class_name="color-secondary"
                )
            with tgb.part(class_name="card"):
                tgb.text(
                    "## **Selected** Company:", mode="md", class_name="color-primary"
                )
                tgb.text(
                    "### {selected_company}", mode="md", class_name="color-secondary"
                )
    with tgb.part(id="company-info"):
        with tgb.layout("1 1 1"):

            with tgb.part(class_name="card"):
                tgb.text(
                    "## **Selected** Level:", mode="md", class_name="color-primary"
                )
                tgb.text(
                    "### {selected_level}", mode="md", class_name="color-secondary"
                )
            tgb.chart(figure="{turnover_metric}")
            tgb.chart(figure="{workers_metric}")

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


def on_init(state):
    get_level_0(state)


stylekit = {"color-primary": "#0f80f0", "color-secondary": "#a5bacf"}

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
    max_group_turnover = 0
    max_group_workers = 0

    turnover_metric = None
    workers_metric = None

    gui = Gui(
        page=hierarchy_page,
        css_file="./css/main.css",
    )
    gui.run(
        use_reloader=True,
        title="Hierarchy ⬆️ ⬇️ App",
        dark_mode=False,
        favicon="./img/favicon.png",
        stylekit=stylekit,
    )
