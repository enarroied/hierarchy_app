import plotly.graph_objects as go


def create_linear_gauge(value, max_value, title):
    """
    Creates a linear gauge using Plotly.

    Parameters:
    - value (float): The current value of the metric.
    - max_value (float): The maximum value of the gauge.
    - title (str): The title of the gauge.
    - unit (str): Optional unit string for display.

    Returns:
    - fig (go.Figure): A Plotly Figure object with the gauge.
    """
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            gauge={
                "shape": "bullet",
                "axis": {"range": [0, max_value]},
                "bar": {"color": "lightgreen"},
                "threshold": {
                    "line": {"color": "red", "width": 2},
                    "thickness": 0.75,
                    "value": value,
                },
            },
        )
    )
    fig.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center"},
        height=200,
        margin=dict(l=40, r=40, t=60, b=20),
    )
    return fig
