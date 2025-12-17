import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from functools import lru_cache
import os
import sys

# ============================================================
# 1. SETUP & DATA LOADING (MEMORY SAFE MODE)
# ============================================================

DATA_PATH = "https://www.dropbox.com/scl/fi/7xr2u9y57jdlk6jbu63m4/df_optimized_final.parquet?rlkey=eqcg33vabg722383b7p306xtn&st=xm4ljcjo&dl=1"

# We only strictly need these columns. Reading only these saves RAM.
REQUIRED_COLS = [
    "BOROUGH", "CRASH DATE", "CRASH TIME", 
    "LATITUDE", "LONGITUDE", "PERSON_INJURY", 
    "VEHICLE TYPE CODE 1", "CONTRIBUTING FACTOR VEHICLE 1", "COLLISION_ID"
]

@lru_cache(maxsize=1)
def load_data_safe():
    """Attempts to load remote data. If it fails/OOMs, returns dummy data."""
    try:
        # OPTIMIZATION: Read ONLY the columns we need.
        # This prevents loading useless text columns that waste RAM.
        print("Attempting to load Parquet...", file=sys.stderr)
        
        # NOTE: If this still crashes, the file is simply too big for the free tier.
        df = pd.read_parquet(DATA_PATH, columns=REQUIRED_COLS)
        
        # Clean Date/Time immediately
        df["CRASH DATE"] = pd.to_datetime(df["CRASH DATE"], errors="coerce")
        print(f"Loaded {len(df)} rows successfully.", file=sys.stderr)
        return df
        
    except Exception as e:
        print(f"CRITICAL ERROR: Could not load data. {e}", file=sys.stderr)
        print("Switching to DUMMY DATA mode to keep app alive.", file=sys.stderr)
        
        # Fallback: Create 5 rows of fake data so the app actually runs
        return pd.DataFrame({
            "BOROUGH": ["MANHATTAN", "BROOKLYN", "QUEENS", "BRONX", "MANHATTAN"],
            "CRASH DATE": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]),
            "CRASH TIME": ["12:00", "13:00", "14:00", "15:00", "16:00"],
            "LATITUDE": [40.7128, 40.6782, 40.7282, 40.8448, 40.7580],
            "LONGITUDE": [-74.0060, -73.9442, -73.7949, -73.8648, -73.9855],
            "PERSON_INJURY": ["Injured", "Killed", "Unspecified", "Injured", "Unspecified"],
            "VEHICLE TYPE CODE 1": ["Sedan", "SUV", "Bus", "Sedan", "Taxi"],
            "CONTRIBUTING FACTOR VEHICLE 1": ["Unspecified", "Driver Inattention", "Failure to Yield", "Unspecified", "Other"],
            "COLLISION_ID": [1, 2, 3, 4, 5]
        })

@lru_cache(maxsize=1)
def load_metadata():
    # Use the safe loader to get metadata options
    df = load_data_safe()
    
    return {
        "boroughs": sorted(df["BOROUGH"].dropna().astype(str).unique().tolist()) if "BOROUGH" in df else [],
        "years": sorted(df["CRASH DATE"].dt.year.dropna().astype(int).unique().tolist()) if "CRASH DATE" in df else [],
        "vehicle_types": sorted(df["VEHICLE TYPE CODE 1"].dropna().astype(str).unique().tolist()) if "VEHICLE TYPE CODE 1" in df else [],
        "factors": sorted(df["CONTRIBUTING FACTOR VEHICLE 1"].dropna().astype(str).unique().tolist()) if "CONTRIBUTING FACTOR VEHICLE 1" in df else [],
        "injuries": sorted(df["PERSON_INJURY"].dropna().astype(str).unique().tolist()) if "PERSON_INJURY" in df else []
    }

def apply_filters(df, boroughs, years, vehicles, factors, injuries):
    # Fast boolean indexing
    mask = pd.Series(True, index=df.index)
    if boroughs: mask &= df["BOROUGH"].isin(boroughs)
    if years:    mask &= df["CRASH DATE"].dt.year.isin(years)
    if vehicles: mask &= df["VEHICLE TYPE CODE 1"].isin(vehicles)
    if factors:  mask &= df["CONTRIBUTING FACTOR VEHICLE 1"].isin(factors)
    if injuries: mask &= df["PERSON_INJURY"].isin(injuries)
    return df[mask]

# ============================================================
# 2. APP LAYOUT
# ============================================================

meta = load_metadata()
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
server = app.server

app.layout = dbc.Container([
    dbc.Row(className="mb-4 pt-4", style={'border-bottom': '1px solid #444'}, children=[
        dbc.Col(html.H1([html.I(className="bi bi-car-front-fill me-3"), "NYC Collision Report"], className="text-info display-4"), width=9),
    ]),

    dbc.Row([
        # --- SIDEBAR ---
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Filters", className="card-title text-warning mb-4"),
            dbc.Label("Borough"),
            dcc.Dropdown(id="borough", options=[{"label": b, "value": b} for b in meta["boroughs"]], multi=True, className="mb-2"),
            dbc.Label("Year"),
            dcc.Dropdown(id="year", options=[{"label": y, "value": y} for y in meta["years"]], multi=True, className="mb-2"),
            dbc.Label("Vehicle"),
            dcc.Dropdown(id="vehicle", options=[{"label": v, "value": v} for v in meta["vehicle_types"]], multi=True, className="mb-2"),
            dbc.Label("Injury Type"),
            dcc.Dropdown(id="injury", options=[{"label": i, "value": i} for i in meta["injuries"]], multi=True, className="mb-4"),
            
            dbc.Button("Generate Report", id="generate", color="success", className="w-100 mb-2"),
            dbc.Button("Reset", id="reset", color="danger", className="w-100"),
            dbc.Alert(id="alert", is_open=False, className="mt-3")
        ]), className="h-100 bg-dark"), width=3),

        # --- GRAPHS ---
        dbc.Col(html.Div([
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(id="bar"), className="shadow-sm"), width=6, className="mb-4"),
                dbc.Col(dbc.Card(dcc.Graph(id="pie"), className="shadow-sm"), width=6, className="mb-4"),
            ]),
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(id="line"), className="shadow-sm"), width=6, className="mb-4"),
                dbc.Col(dbc.Card(dcc.Graph(id="heat"), className="shadow-sm"), width=6, className="mb-4"),
            ]),
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(id="map", style={'height': '50vh'}), className="shadow-lg"), width=12),
            ])
        ], className="p-4 bg-secondary"), width=9)
    ])
], fluid=True)

# ============================================================
# 3. COMBINED CALLBACK (NO DCC.STORE)
# ============================================================

@app.callback(
    Output("borough", "value"), Output("year", "value"), Output("vehicle", "value"), Output("injury", "value"),
    Input("reset", "n_clicks"), prevent_initial_call=True
)
def reset(n): return [], [], [], []

@app.callback(
    Output("bar", "figure"), Output("pie", "figure"), Output("line", "figure"),
    Output("heat", "figure"), Output("map", "figure"), Output("alert", "children"), Output("alert", "is_open"),
    
    Input("generate", "n_clicks"),
    State("borough", "value"), State("year", "value"), 
    State("vehicle", "value"), State("injury", "value"),
    prevent_initial_call=True
)
def update_dashboard(n_clicks, boroughs, years, vehicles, injuries):
    # Setup styles
    layout_style = {'plot_bgcolor': 'rgba(0,0,0,0)', 'paper_bgcolor': 'rgba(0,0,0,0)', 'font': {'color': '#DDD'}}
    def create_fig(fig, title):
        fig.update_layout(title_text=title, **layout_style)
        return fig
    empty = create_fig(px.scatter(), "No Data")

    # Load & Filter
    df = load_data_safe()
    filtered = apply_filters(df, boroughs, years, vehicles, [], injuries)
    
    if filtered.empty:
        return empty, empty, empty, empty, empty, "No records found.", True

    # 1. Bar Chart
    if "BOROUGH" in filtered:
        counts = filtered["BOROUGH"].value_counts().reset_index()
        counts.columns = ["BOROUGH", "count"]
        bar = create_fig(px.bar(counts, x="BOROUGH", y="count"), "Crashes by Borough")
    else: bar = empty

    # 2. Pie Chart
    pie = create_fig(px.pie(filtered, names="PERSON_INJURY"), "Injuries") if "PERSON_INJURY" in filtered else empty

    # 3. Line Chart
    ts = filtered.set_index("CRASH DATE").resample("ME").size()
    line = create_fig(px.line(ts), "Trend Over Time")

    # 4. Heatmap
    if "CRASH TIME" in filtered:
        heat_df = filtered.copy()
        heat_df["HOUR"] = pd.to_datetime(heat_df["CRASH TIME"], format='%H:%M', errors="coerce").dt.hour
        heat_df["DAY"] = heat_df["CRASH DATE"].dt.day_name()
        pivot = heat_df.pivot_table(index="HOUR", columns="DAY", aggfunc="size", fill_value=0)
        heat = create_fig(px.imshow(pivot), "Time Heatmap")
    else: heat = empty

    # 5. Map (Sampled)
    if "LATITUDE" in filtered:
        map_df = filtered.dropna(subset=["LATITUDE", "LONGITUDE"])
        if len(map_df) > 1000: map_df = map_df.sample(1000) # Heavy sampling for speed
        map_fig = px.scatter_mapbox(map_df, lat="LATITUDE", lon="LONGITUDE", zoom=10, mapbox_style="carto-darkmatter")
        map_fig = create_fig(map_fig, "Crash Locations")
        map_fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    else: map_fig = empty

    return bar, pie, line, heat, map_fig, f"Showing {len(filtered)} records.", True

if __name__ == '__main__':
    app.run_server(debug=False)
