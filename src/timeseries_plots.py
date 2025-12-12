import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import nbformat

def plot_time_series_day(df, date, columns, title=None, y_label='Value'):
    """
    Plots selected columns for a specific day when datetime is the index.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with a datetime index and numerical columns.
    date : str or pd.Timestamp
        The day to plot, e.g., '2015-01-01'.
    columns : list of str
        List of column names to plot.
    title : str, optional
        Plot title. Defaults to 'Time Series for {date}'.
    y_label : str, optional
        Label for the y-axis. Defaults to 'Value'.
    """
    # Ensure index is datetime
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)

    # Make timezone-naive if needed
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    # Filter for the specific day
    start_date = pd.Timestamp(date)
    end_date = start_date + pd.Timedelta(days=1)
    day_data = df[(df.index >= start_date) & (df.index < end_date)]

    # Generate colors automatically
    num_cols = len(columns)
    colors = cm.get_cmap('tab20', num_cols).colors

    # Plot
    plt.figure(figsize=(16,8))
    for i, col in enumerate(columns):
        plt.plot(day_data.index, day_data[col], label=col, color=colors[i], linewidth=2)

    # Set title
    if title is None:
        title = f'Time Series for {date}'
    plt.title(title, fontsize=18, weight='bold')
    plt.xlabel('Time', fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.legend(fontsize=12, loc='upper left', bbox_to_anchor=(1,1))
    plt.tight_layout()
    plt.show()

def plot_time_series(df, columns, title='Time Series', y_label='Value', stacked=False):
    """
    Plots multiple time series over time using Plotly.

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
    """
    # Ensure the index is datetime
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)

    # Make timezone-naive if needed
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    # Convert dict to list of tuples if needed
    if isinstance(columns, dict):
        cols = list(columns.items())
    else:
        cols = [(col, col) for col in columns]

    # Automatically select renderer
    try:
        pio.renderers.default = "notebook_connected"  # works in Jupyter notebooks
    except Exception:
        pio.renderers.default = "browser"  # fallback for scripts or environments without notebook support

    # Assign colors
    colors = px.colors.qualitative.Plotly

    # Create figure
    fig = go.Figure()

    for i, (col, name) in enumerate(cols):
        if stacked:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[col],
                mode='lines',
                name=name,
                line=dict(color=colors[i % len(colors)], width=2),
                stackgroup='one'
            ))
        else:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[col],
                mode='lines',
                name=name,
                line=dict(color=colors[i % len(colors)], width=2)
            ))

    fig.update_layout(
        title=title,
        xaxis_title='Time',
        yaxis_title=y_label,
        xaxis_rangeslider_visible=True,
        legend=dict(title='Series', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        template='plotly_white'
    )

    fig.show()