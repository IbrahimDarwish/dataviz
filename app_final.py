import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from functools import lru_cache
import os
import json
from io import StringIO
import sys

# ============================================================
# 1. OPTIMIZED DATA LOADING
# ============================================================

DATA_PATH = "https://www.dropbox.com/scl/fi/7xr2u9y57jdlk6jbu63m4/df_optimized_final.parquet?rlkey=eqcg33vabg722383b7p306xtn&st=xm4ljcjo&dl=1"

REQUIRED_COLS = [
    "BOROUGH", "CRASH DATE", "CRASH TIME", 
    "LATITUDE", "LONGITUDE", "PERSON_INJURY", 
    "VEHICLE TYPE CODE 1", "CONTRIBUTING FACTOR VEHICLE 1"
]

@lru_cache(maxsize=1)
def load_data_safe():
    """
    Loads data with strict memory limits for Render Free Tier.
    """
    try:
        print("Attempting to load Parquet...", file=sys.stderr)
        
        # 1. Load specific columns only
        df = pd.read_parquet(DATA_PATH, columns=REQUIRED_COLS)

        # 2. SAFETY CAP (Critical for Render)
        # Limit to 150k rows to prevent memory crashes
        if len(df) > 150000:
            print(f"Dataset too large. Trimming to 150k rows for stability...", file=sys.stderr)
            df = df.iloc[:150000].copy()

        # 3. Optimize Numbers
        df["LATITUDE"] = df["LATITUDE"].astype("float32")
        df["LONGITUDE"] = df["LONGITUDE"].astype("float32")

        # 4. Standard Date Conversion
        df["CRASH DATE"] = pd.to_datetime(df["CRASH DATE"], errors="coerce")
        
        print(f"Loaded {len(df)} rows successfully.", file=sys.stderr)
        return df
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}", file=sys.stderr)
        # Fallback dummy data
        return pd.DataFrame({
            "BOROUGH": ["MANHATTAN", "BROOKLYN"],
            "CRASH DATE": pd.to_datetime(["2023-01-01", "2023-01-02"]),
            "CRASH TIME": ["12:00", "13:00"],
            "LATITUDE": [40.7128, 40.6782],
            "LONGITUDE": [-74.0060, -73.9442],
            "PERSON_INJURY": ["Injured", "Killed"],
            "VEHICLE TYPE CODE 1": ["Sedan", "SUV"],
            "CONTRIBUTING FACTOR VEHICLE 1": ["Unspecified", "Driver Inattention"]
        })

@lru_cache(maxsize=1)
def load_metadata():
    # Load the safe dataframe
    df = load_data_safe()
    
    # --- CLEANING STEP FOR VEHICLES ---
    # Only take the Top 50 most common vehicles to hide typos/rare weird inputs
    if "VEHICLE TYPE CODE 1" in df:
        top_vehicles = df["VEHICLE TYPE CODE 1"].value_counts().head(50).index.tolist()
        vehicle_list = sorted(top_vehicles)
    else:
        vehicle_list = []

    return {
        "boroughs": sorted(df["BOROUGH"].dropna().unique().tolist()) if "BOROUGH" in df else [],
        "years": sorted(df["CRASH DATE"].dt.year.dropna().unique().tolist()) if "CRASH DATE" in df else [],
        "vehicle_types": vehicle_list, # Cleaned list
        "factors": sorted(df["CONTRIBUTING FACTOR VEHICLE 1"].dropna().unique().tolist()) if "CONTRIBUTING FACTOR VEHICLE 1" in df else [],
        "injuries": sorted(df["PERSON_INJURY"].dropna().unique().tolist()) if "PERSON_INJURY" in df else []
    }

def parse_search_query(search_query, metadata):
    """Parses natural language queries."""
    if not search_query or not search_query.strip():
        return None 

    s = search_query.lower()
    parsed_filters = {"boroughs": [], "years": [], "injuries": []}
    
    # Check Boroughs
    for b in metadata["boroughs"]:
        if b.lower() in s: parsed_filters["boroughs"].append(b)
            
    # Check Years
    for year in metadata["years"]:
        if str(year) in s: parsed_filters["years"].append(year)
            
    # Check Injuries
    injury_keywords = {
        "pedestrian": ["PEDESTRIAN"], "cyclist": ["BICYCLIST"],
        "motorist": ["PASSENGER", "DRIVER"], "killed": ["KILLED"], "injured": ["INJURED"]
    }
    for keyword, values in injury_keywords.items():
        if keyword in s:
            for val in values:
                if val in metadata["injuries"]: parsed_filters["injuries"].append(val)
    
    if any(parsed_filters.values()): return parsed_filters
    return None

def apply_filters(df, boroughs, years, vehicles, factors, injuries):
    mask = pd.Series(True, index=df.index)
    if boroughs: mask &= df["BOROUGH"].isin(boroughs)
    if years:    mask &= df["CRASH DATE"].dt.year.isin(years)
    if vehicles: mask &= df["VEHICLE TYPE CODE 1"].isin(vehicles)
    if factors:  mask &= df["CONTRIBUTING FACTOR VEHICLE 1"].isin(factors)
    if injuries: mask &= df["PERSON_INJURY"].isin(injuries)
    return df[mask]

# Helpers for dcc.Store
def df_to_json(df): return df.to_json(date_format="iso", orient="split")
def json_to_df(js): return pd.read_json(StringIO(js), orient="split")

# ============================================================
# 2. APP LAYOUT
# ============================================================

meta = load_metadata()
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
server = app.server

app.layout = dbc.Container([
    # --- HEADER ---
    dbc.Row(className="mb-4 pt-4", style={'border-bottom': '1px solid #444'}, children=[
        dbc.Col(html.H1([html.I(className="bi bi-car-front-fill me-3"), "NYC Collision Report"], className="text-info display-4"), width=9),
    ]),

    dbc.Row([
        # --- SIDEBAR ---
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Filter Controls", className="card-title text-warning mb-4"),
            
            dbc.Label("Borough", className="mt-2"),
            dcc.Dropdown(id="borough", options=[{"label": b, "value": b} for b in meta["boroughs"]], multi=True, value=[], className="mb-3"),

            dbc.Label("Year"),
            dcc.Dropdown(id="year", options=[{"label": y, "value": y} for y in meta["years"]], multi=True, value=[], className="mb-3"),

            dbc.Label("Vehicle Type"),
            dcc.Dropdown(id="vehicle", options=[{"label": v, "value": v} for v in meta["vehicle_types"]], multi=True, value=[], className="mb-3"),

            dbc.Label("Contributing Factor"),
            dcc.Dropdown(id="factor", options=[{"label": f, "value": f} for f in meta["factors"]], multi=True, value=[], className="mb-3"),

            dbc.Label("Person Injury Type"), 
            dcc.Dropdown(id="injury", options=[{"label": i, "value": i} for i in meta["injuries"]], multi=True, value=[], className="mb-4"),

            html.H5("Search & Actions", className="text-info mb-3"),
            dbc.Label("Search Keywords"), 
            dcc.Input(id="search", type="text", style={"width": "100%"}, placeholder="e.g., Manhattan 2023 cyclist...", className="mb-4"),

            dbc.Row([
                dbc.Col(dbc.Button("Generate Report", id="generate", color="success", className="w-100"), width=8),
                dbc.Col(dbc.Button("Reset", id="reset", color="danger", className="w-100"), width=4)
            ], className="mb-4"),
            
            dbc.Alert(id="alert", is_open=False, className="mt-3")
        ]), className="h-100 shadow-lg bg-dark", style={"min-height": "100vh"}), width=3, className="p-0"),

        # --- VISUALIZATIONS ---
        dbc.Col(html.Div([
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(id="bar"), className="shadow-sm h-100"), width=6, className="mb-4"),
                dbc.Col(dbc.Card(dcc.Graph(id="pie"), className="shadow-sm h-100"), width=6, className="mb-4"),
            ]),
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(id="line"), className="shadow-sm h-100"), width=6, className="mb-4"),
                dbc.Col(dbc.Card(dcc.Graph(id="heat"), className="shadow-sm h-100"), width=6, className="mb-4"),
            ]),
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(id="map", style={'height': '60vh'}), className="shadow-lg"), width=12),
            ])
        ], className="p-4 bg-secondary"), width=9, className="p-4")
    ], className="g-0"),

    dcc.Store(id="store")
], fluid=True)

# ============================================================
# 3. CALLBACKS
# ============================================================

# 1. Reset Button
@app.callback(
    Output("borough", "value", allow_duplicate=True),
    Output("year", "value", allow_duplicate=True),
    Output("vehicle", "value", allow_duplicate=True),
    Output("factor", "value", allow_duplicate=True),
    Output("injury", "value", allow_duplicate=True),
    Output("search", "value", allow_duplicate=True),
    Output("store", "data", allow_duplicate=True),
    Output("alert", "is_open", allow_duplicate=True),
    Input("reset", "n_clicks"),
    prevent_initial_call=True
)
def reset_all(n_clicks):
    if n_clicks: return [], [], [], [], [], "", None, False
    raise dash.exceptions.PreventUpdate

# 2. Data Filtering
@app.callback(
    Output("store", "data"),
    Output("alert", "children"),
    Output("alert", "is_open"),
    Output("borough", "value"),
    Output("year", "value"),
    Output("injury", "value"),
    
    Input("generate", "n_clicks"),
    State("borough", "value"), State("year", "value"),
    State("vehicle", "value"), State("factor", "value"),
    State("injury", "value"), State("search", "value"),
    prevent_initial_call=True
)
def filter_data_and_autofilter(n_generate, boroughs, years, vehicles, factors, injuries, search):
    if not n_generate: raise dash.exceptions.PreventUpdate

    metadata = load_metadata()
    parsed_search_filters = parse_search_query(search, metadata)

    final_boroughs = boroughs
    final_years = years
    final_injuries = injuries

    # Override dropdowns if search query finds specific filters
    if parsed_search_filters:
        final_boroughs = parsed_search_filters.get("boroughs", final_boroughs)
        final_years = parsed_search_filters.get("years", final_years)
        final_injuries = parsed_search_filters.get("injuries", final_injuries)

    try:
        # Load Safe Data
        df = load_data_safe()
        filtered = apply_filters(df, final_boroughs, final_years, vehicles, factors, final_injuries)

        msg = f"Report generated successfully: {len(filtered)} records found."
        
        return (
            df_to_json(filtered), 
            msg, True,
            final_boroughs, final_years, final_injuries
        )
    except Exception as e:
        return None, str(e), True, final_boroughs, final_years, final_injuries

# 3. Graph Update
@app.callback(
    Output("bar", "figure"), Output("pie", "figure"),
    Output("line", "figure"), Output("heat", "figure"),
    Output("map", "figure"),
    Input("store", "data")
)
def update_graphs(json_data):
    layout_style = {'plot_bgcolor': 'rgba(0,0,0,0)', 'paper_bgcolor': 'rgba(0,0,0,0)', 'font': {'color': '#DDD'}}
    def create_fig(fig, title):
        fig.update_layout(title_text=title, **layout_style)
        return fig
    
    if not json_data:
        empty = create_fig(px.scatter(), "No Data Loaded")
        return empty, empty, empty, empty, empty

    df = json_to_df(json_data)
    
    # BAR
    if "BOROUGH" in df:
        bar = create_fig(px.bar(df["BOROUGH"].value_counts().reset_index(), x="BOROUGH", y="count"), "Crashes by Borough")
    else: bar = create_fig(px.scatter(), "No Data")

    # PIE
    if "PERSON_INJURY" in df:
        pie = create_fig(px.pie(df, names="PERSON_INJURY"), "Person Injury Types")
    else: pie = create_fig(px.scatter(), "No Data")

    # LINE
    if "CRASH DATE" in df:
        df["CRASH DATE"] = pd.to_datetime(df["CRASH DATE"])
        ts = df.set_index("CRASH DATE").resample("ME").size()
        line = create_fig(px.line(ts), "Crashes Over Time")
    else: line = create_fig(px.scatter(), "No Data")

    # HEATMAP
    if "CRASH TIME" in df and "CRASH DATE" in df:
        df["CRASH TIME"] = pd.to_datetime(df["CRASH TIME"], errors="coerce").dt.time.astype(str)
        df["HOUR"] = pd.to_datetime(df["CRASH TIME"], format='%H:%M:%S', errors="coerce").dt.hour
        df["DAY"] = pd.to_datetime(df["CRASH DATE"], errors="coerce").dt.day_name()
        
        pivot = df.pivot_table(index="HOUR", columns="DAY", aggfunc="size", fill_value=0)
        heat = create_fig(px.imshow(pivot), "Heatmap: Hour vs Day")
    else: heat = create_fig(px.scatter(), "No Data")

    # MAP
    if "LATITUDE" in df:
        df2 = df.dropna(subset=["LATITUDE", "LONGITUDE"])
        if len(df2) > 1000: df2 = df2.sample(1000) # Sample for map speed
        map_fig = px.scatter_mapbox(df2, lat="LATITUDE", lon="LONGITUDE", zoom=10, mapbox_style="carto-darkmatter")
        map_fig = create_fig(map_fig, "Crash Locations")
        map_fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    else: map_fig = create_fig(px.scatter(), "No Data")

    return bar, pie, line, heat, map_fig

if __name__ == '__main__':
    app.run_server(debug=False)
