import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def plot_time_series(df, columns, title='Time Series', y_label='Value', stacked=False, days=3):
    """
    Generates a Plotly time series figure as HTML for embedding in FastAPI.
    Plots only the last 'days' from the DataFrame (default 3 days).

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with a datetime index.
    columns : list or dict
        List of column names to plot, or dict {column_name: display_name}.
    title : str
        Plot title.
    y_label : str
        Label for the y-axis.
    stacked : bool
        If True, creates a stacked area plot. Default is False.
    days : int
        Number of days to plot from the end. Default is 3.

    Returns:
    --------
    str
        HTML string of the Plotly figure.
    """
    # Ensure the index is datetime
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)

    # Make timezone-naive if needed
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    # Filter last 'days'
    start_time = df.index.max() - pd.Timedelta(days=days)
    df_filtered = df.loc[start_time:]

    # Convert dict to list of tuples if needed
    if isinstance(columns, dict):
        cols = list(columns.items())
    else:
        cols = [(col, col) for col in columns]

    # Assign colors
    colors = px.colors.qualitative.Plotly

    # Create figure
    fig = go.Figure()

    for i, (col, name) in enumerate(cols):
        fig.add_trace(go.Scatter(
            x=df_filtered.index,
            y=df_filtered[col],
            mode='lines',
            name=name,
            line=dict(color=colors[i % len(colors)], width=2),
            stackgroup='one' if stacked else None
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Time',
        yaxis_title=y_label,
        xaxis_rangeslider_visible=True,
        legend=dict(title='Series', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        template='plotly_white'
    )

    # Return HTML string instead of showing
    return fig.to_html(full_html=False)

def plot_timeseries_average_by_time_multiple_columns(
    df: pd.DataFrame, 
    columns, 
    time_feature: str, 
    title: str = None, 
    ylabel: str = None, 
    markers=None, 
    colors=None
) -> str:
    """
    Generates a Plotly figure showing average values of columns grouped by a time feature.
    Returns HTML string for embedding in FastAPI.

    Parameters:
    - df: pandas DataFrame
    - columns: str or list of column names
    - time_feature: str, time-based feature to group by
    - title: str, optional plot title
    - ylabel: str, optional y-axis label
    - markers: list of marker symbols for each column
    - colors: list of colors for each column

    Returns:
    - HTML string of the Plotly figure
    """

    # Ensure columns is a list
    if isinstance(columns, str):
        columns = [columns]

    # Default markers and colors
    if markers is None:
        markers = ['circle'] * len(columns)
    if colors is None:
        colors = px.colors.qualitative.Plotly[:len(columns)]

    fig = go.Figure()

    for i, col in enumerate(columns):
        avg_values = df.groupby(time_feature)[col].mean()
        fig.add_trace(
            go.Scatter(
                x=avg_values.index,
                y=avg_values.values,
                mode='lines+markers',
                name=col,
                marker=dict(symbol=markers[i], color=colors[i]),
                line=dict(color=colors[i])
            )
        )

    fig.update_layout(
        title=title if title else f'Average {", ".join(columns)} by {time_feature}',
        xaxis_title=time_feature.replace('_', ' ').title(),
        yaxis_title=ylabel if ylabel else "Value",
        template='plotly_white',
        legend=dict(title='Columns')
    )

    return fig.to_html(full_html=False)

def plot_generation_composition_days(
    df: pd.DataFrame,
    generation_cols: list,
    days: int = 3,
    title: str = "Generation Composition"
) -> str:
    """
    Plots a stacked area chart for the last `days` of generation data.
    Returns HTML string for FastAPI.
    """
    if days < 1:
        days = 1
    max_days = (df.index.max() - df.index.min()).days + 1
    if days > max_days:
        days = max_days

    cutoff = df.index.max() - pd.Timedelta(days=days-1)
    filtered_df = df[df.index >= cutoff]

    # Ensure numeric
    filtered_df[generation_cols] = filtered_df[generation_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Colors
    colors = px.colors.qualitative.Plotly

    # Figure
    fig = go.Figure()
    for i, col in enumerate(generation_cols):
        fig.add_trace(go.Scatter(
            x=filtered_df.index,
            y=filtered_df[col],
            mode='lines',
            name=col,
            line=dict(width=0.5, color=colors[i % len(colors)]),
            stackgroup='one'
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Time',
        yaxis_title='Power (MW)',
        xaxis_rangeslider_visible=True,
        legend=dict(title='Source', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        template='plotly_white'
    )

    return fig.to_html(full_html=False)