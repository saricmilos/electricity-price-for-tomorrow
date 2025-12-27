from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd
from pathlib import Path
import sys

# Add src folder to path to import your module
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from src.fast_api_functions import (
    plot_time_series,
    plot_timeseries_average_by_time_multiple_columns,
    plot_generation_composition_days  
)

app = FastAPI(title="Electricity Generation Plotter")

# Add CORS middleware - ADD THIS SECTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://saricmilos.com",
        "http://localhost:*",  # for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load dataset once
data_path = Path(__file__).resolve().parent.parent / "data" / "energy_clean.csv"
df = pd.read_csv(data_path, index_col=0)
if not pd.api.types.is_datetime64_any_dtype(df.index):
    df.index = pd.to_datetime(df.index)
if df.index.tz is not None:
    df.index = df.index.tz_localize(None)

columns_list = df.columns.tolist()

GENERATION_PREFIX = "generation_"

generation_columns = [
    c for c in df.columns
    if c.startswith(GENERATION_PREFIX)
    and c not in [
        "generation_load_difference",  # exclude derived columns
        "total_generation"
    ]
]

# Precompute time features
df['hour_of_day'] = df.index.hour
df['day_of_week'] = df.index.dayofweek
df['month'] = df.index.month
time_features = ["hour_of_day", "day_of_week", "month"]

# ------------------- Root -------------------
@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <head><title>Electricity Generation API</title></head>
        <body>
            <h2>Your API is up and running!</h2>
            <p>Available plotting endpoints:</p>
            <ul>
                <li><a href="/days_form">Plot by Days</a></li>
                <li><a href="/avg_form">Plot Average by Time Feature</a></li>
                <li><a href="/composition_form">Generation Composition Plot</a></li>
            </ul>
        </body>
    </html>
    """

# ------------------- Days Form -------------------
@app.get("/days_form", response_class=HTMLResponse)
def days_form():
    options_html = "".join([f'<option value="{c}">{c}</option>' for c in columns_list])
    max_days = (df.index.max() - df.index.min()).days + 1
    return f"""
    <html>
        <head><title>Plot by Days</title></head>
        <body>
            <h2>Plot by Days</h2>
            <form action="/plot" method="post">
                <label>Select columns (Ctrl+click for multiple):</label><br>
                <select name="columns" multiple size="10">{options_html}</select><br><br>

                <label>Number of days to plot:</label>
                <input type="number" name="days" value="{max_days}" min="1" max="{max_days}"><br><br>

                <label>Stacked:</label>
                <input type="checkbox" name="stacked"><br><br>

                <input type="submit" value="Plot">
            </form>
            <a href="/">⬅ Back</a>
        </body>
    </html>
    """

# ------------------- Average Form -------------------
@app.get("/avg_form", response_class=HTMLResponse)
def avg_form():
    options_html = "".join([f'<option value="{c}">{c}</option>' for c in columns_list])
    time_options_html = "".join([f'<option value="{tf}">{tf.replace("_"," ").title()}</option>' for tf in time_features])
    return f"""
    <html>
        <head><title>Average by Time Feature</title></head>
        <body>
            <h2>Plot Average by Time Feature</h2>
            <form action="/avg_plot" method="post">
                <label>Select columns (Ctrl+click for multiple):</label><br>
                <select name="columns_avg" multiple size="10">{options_html}</select><br><br>

                <label>Time Feature:</label>
                <select name="time_feature">{time_options_html}</select><br><br>

                <input type="submit" value="Plot Average">
            </form>
            <a href="/">⬅ Back</a>
        </body>
    </html>
    """

# ------------------- Composition Form -------------------
@app.get("/composition_form", response_class=HTMLResponse)
def composition_form():
    options_html = "".join(
        [f'<option value="{c}" selected>{c}</option>' for c in generation_columns]
    )

    max_days = (df.index.max() - df.index.min()).days + 1

    return f"""
    <html>
        <head><title>Generation Composition</title></head>
        <body>
            <h2>Generation Composition Plot</h2>

            <form action="/composition_plot" method="post">
                <label>Select generation sources:</label><br>
                <select name="columns_comp" multiple size="12">
                    {options_html}
                </select><br><br>

                <label>Number of days to plot:</label>
                <input type="number" name="days"
                       value="{10}" min="1" max="{max_days}"><br><br>

                <input type="submit" value="Plot Composition">
            </form>

            <a href="/">⬅ Back</a>
        </body>
    </html>
    """


# ------------------- Post Endpoints -------------------
@app.post("/plot", response_class=HTMLResponse)
def plot(columns: List[str] = Form(...), days: int = Form(3), stacked: str = Form(None)):
    title = ", ".join(columns) if len(columns) > 1 else columns[0]
    html_plot = plot_time_series(df, columns, title=title, y_label="MW", stacked=bool(stacked), days=days)
    return f"<html><body><a href='/days_form'>⬅ Back</a><br><br>{html_plot}</body></html>"

@app.post("/avg_plot", response_class=HTMLResponse)
def avg_plot(columns_avg: List[str] = Form(...), time_feature: str = Form(...)):
    title = ", ".join(columns_avg) if len(columns_avg) > 1 else columns_avg[0]
    html_plot = plot_timeseries_average_by_time_multiple_columns(df, columns_avg, time_feature, title=title, ylabel="MW")
    return f"<html><body><a href='/avg_form'>⬅ Back</a><br><br>{html_plot}</body></html>"

@app.post("/composition_plot", response_class=HTMLResponse)
def composition_plot(
    columns_comp: List[str] = Form(...),
    days: int = Form(3)
):
    # Keep only valid generation columns
    columns_comp = [c for c in columns_comp if c in generation_columns]

    if not columns_comp:
        return "<html><body><h3>No valid generation columns selected.</h3><a href='/composition_form'>⬅ Back</a></body></html>"

    html_plot = plot_generation_composition_days(df, columns_comp, days)

    return f"""
    <html>
        <head><title>Generation Composition</title></head>
        <body>
            <a href="/composition_form">⬅ Back</a><br><br>
            {html_plot}
        </body>
    </html>
    """