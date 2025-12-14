import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import seaborn as sns

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

def plot_generation_composition(df, generation_cols, start_date=None, end_date=None, title='Generation Composition'):
    """
    Plots a stacked area chart showing the composition of generation over time.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with datetime index and generation columns.
    generation_cols : list
        List of columns representing different generation sources.
    start_date : str or pd.Timestamp, optional
        Start date for filtering data (e.g., '2024-04-27').
    end_date : str or pd.Timestamp, optional
        End date for filtering data (e.g., '2024-04-28').
    title : str
        Plot title.
    """
    # Ensure the index is datetime
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)

    # Make index timezone-naive
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    # Filter by date if provided
    filtered_df = df.copy()
    if start_date:
        start_date = pd.Timestamp(start_date)
        filtered_df = filtered_df[filtered_df.index >= start_date]
    if end_date:
        end_date = pd.Timestamp(end_date) + pd.Timedelta(days=1)
        filtered_df = filtered_df[filtered_df.index < end_date]

    if filtered_df.empty:
        print("Warning: No data available for the specified date range.")
        return

    # Ensure all generation columns are numeric
    filtered_df[generation_cols] = filtered_df[generation_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Generate colors
    colors = px.colors.qualitative.Plotly

    # Create figure
    fig = go.Figure()

    for i, col in enumerate(generation_cols):
        fig.add_trace(go.Scatter(
            x=filtered_df.index,
            y=filtered_df[col],
            mode='lines',
            name=col,
            line=dict(width=0.5, color=colors[i % len(colors)]),
            stackgroup='one'  # Enables stacking
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Time',
        yaxis_title='Power (MW)',
        xaxis_rangeslider_visible=True,
        legend=dict(title='Source', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        template='plotly_white'
    )

    fig.show()


def plot_timeseries_average_by_time(df, column, time_feature, title=None, ylabel=None, figsize=(10,5), marker='o', color=None):
    """
    Plots average values of a column grouped by a time feature (hour_of_day, day_of_week, month, etc.)

    Parameters:
    - df: pandas DataFrame with the data
    - column: str, name of the column to plot
    - time_feature: str, name of the time-based feature to group by ('hour_of_day', 'day_of_week', 'month', etc.)
    - title: str, optional title for the plot
    - ylabel: str, optional y-axis label
    - figsize: tuple, size of the figure
    - marker: str, marker style
    - color: str, line color
    """
    
    avg_values = df.groupby(time_feature)[column].mean()
    
    plt.figure(figsize=figsize)
    plt.plot(avg_values, marker=marker, color=color)
    plt.title(title if title else f'Average {column} by {time_feature}')
    plt.xlabel(time_feature.replace('_', ' ').title())
    plt.ylabel(ylabel if ylabel else column)
    plt.grid(True)
    plt.show()

def plot_timeseries_average_by_time_multiple_columns(df, columns, time_feature, title=None, ylabel=None, figsize=(10,5), markers=None, colors=None):
    """
    Plots average values of one or more columns grouped by a time feature (hour_of_day, day_of_week, month, etc.)

    Parameters:
    - df: pandas DataFrame with the data
    - columns: str or list of column names to plot
    - time_feature: str, time-based feature to group by
    - title: str, optional plot title
    - ylabel: str, optional y-axis label
    - figsize: tuple, figure size
    - markers: list of marker styles for each column
    - colors: list of colors for each column
    """
    # Ensure columns is a list
    if isinstance(columns, str):
        columns = [columns]
    
    # Default markers and colors if not provided
    if markers is None:
        markers = ['o'] * len(columns)
    if colors is None:
        colors = [None] * len(columns)
    
    plt.figure(figsize=figsize)
    
    for i, col in enumerate(columns):
        avg_values = df.groupby(time_feature)[col].mean()
        plt.plot(avg_values, marker=markers[i], color=colors[i], label=col)
    
    plt.title(title if title else f'Average {", ".join(columns)} by {time_feature}')
    plt.xlabel(time_feature.replace('_', ' ').title())
    plt.ylabel(ylabel if ylabel else "Value")
    plt.grid(True)
    plt.legend()
    plt.show()


def plot_time_heatmap(df, column, index_feature, column_feature, title=None, cmap='viridis', figsize=(12,6)):
    """
    Plots a heatmap of average values of a column, grouped by two time-based features.

    Parameters:
    - df: pandas DataFrame
    - column: str, column to plot (e.g., 'generation_solar')
    - index_feature: str, column to use as heatmap index (rows, e.g., 'hour_of_day')
    - column_feature: str, column to use as heatmap columns (e.g., 'day_of_week', 'month')
    - title: str, optional plot title
    - cmap: str, color map
    - figsize: tuple, figure size
    """
    heatmap_data = df.pivot_table(
        values=column,
        index=index_feature,
        columns=column_feature,
        aggfunc='mean'
    )
    
    plt.figure(figsize=figsize)
    sns.heatmap(heatmap_data, cmap=cmap)
    plt.title(title if title else f'Average {column}: {index_feature} vs {column_feature}')
    plt.xlabel(column_feature.replace('_', ' ').title())
    plt.ylabel(index_feature.replace('_', ' ').title())
    plt.show()

def plot_correlation_with_target(df, target_column, figsize=(12,12), cmap='coolwarm', vmin=-1, vmax=1, sort=True):
    """
    Plots a heatmap of correlation between all numerical columns and the target column.

    Parameters:
    - df: pandas DataFrame
    - target_column: str, the column to correlate against
    - figsize: tuple, figure size
    - cmap: str, colormap
    - vmin, vmax: float, limits for correlation values
    - sort: bool, whether to sort columns by correlation with target
    """
    corr_matrix = df.corr()
    
    target_corr = corr_matrix[[target_column]]
    
    if sort:
        target_corr = target_corr.sort_values(by=target_column, ascending=False)
    
    plt.figure(figsize=figsize)
    sns.heatmap(target_corr, annot=True, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.title(f'Correlation of Numerical Features with {target_column}', fontsize=16)
    plt.show()