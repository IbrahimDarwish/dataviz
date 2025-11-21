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
import time
import sys # Added for visible error logging

# ============================================================
#               UTILITIES & DATA LOADING (FIXED for Render)
# ============================================================

# Replace with your confirmed, direct Google Drive/Dropbox download link.
DATA_PATH = "https://www.dropbox.com/scl/fi/3fi7m2lvixz3lqr895plh/df_joined_optimized.csv.gz?rlkey=lra2omrwxgxsuvorsftm53b55&st=y8jwgoed&dl=1" 
# --- 1. FULL DATA LOADER (Called ONLY on "Generate Report" click) ---
@lru_cache(maxsize=1)
def load_full_data():
    """Loads the entire 1GB CSV file into memory (This is the slow part)."""
    try:
        # pd.read_csv handles loading from the web URL
        df = pd.read_csv(DATA_PATH, low_memory=False)
        print("Full data loaded successfully from remote URL.", file=sys.stderr, flush=True)
        return df
    except Exception as e:
        # This error is critical and usually indicates a bad URL or network issue.
        print(f"--- FULL DATA LOAD FAILED ---", file=sys.stderr, flush=True)
        print(f"Error loading full data: {e}", file=sys.stderr, flush=True)
        print(f"--------------------------", file=sys.stderr, flush=True)
        raise FileNotFoundError("Could not load full data from remote URL.")

# --- 2. METADATA LOADER (Called on startup for dropdowns - OOM FIX) ---
@lru_cache(maxsize=1)
def load_metadata():
    """Loads a tiny chunk of data to extract metadata for dropdowns, avoiding OOM crash."""
    try:
        # Use a tiny chunksize (e.g., 10 rows) to get column values 
        # without loading the 1GB file into RAM during startup.
        reader = pd.read_csv(DATA_PATH, chunksize=10, low_memory=False)
        df_meta = next(reader)
    except Exception as e:
        print(f"Error reading initial chunk for metadata: {e}", file=sys.stderr, flush=True)
        # Return empty lists on failure so the app still loads
        return {
            "boroughs": [], "years": [], "vehicle_types": [],
            "factors": [], "injuries": []
        }

    # Use the small chunk (df_meta) to populate all dropdowns
    boroughs = sorted(df_meta["BOROUGH"].dropna().unique().tolist()) if "BOROUGH" in df_meta else []
    years = sorted(pd.to_datetime(df_meta["CRASH_DATE"], errors="coerce").dt.year.dropna().astype(int).unique().tolist()) if "CRASH_DATE" in df_meta else []
    vehicle = sorted(df_meta["VEHICLE TYPE CODE 1"].dropna().unique().tolist()) if "VEHICLE TYPE CODE 1" in df_meta else []
    factors = sorted(df_meta["CONTRIBUTING FACTOR VEHICLE 1"].dropna().unique().tolist()) if "CONTRIBUTING FACTOR VEHICLE 1" in df_meta else []
    injuries = sorted(df_meta["PERSON_INJURY"].dropna().unique().tolist()) if "PERSON_INJURY" in df_meta else []

    return {
        "boroughs": boroughs,
        "years": years,
        "vehicle_types": vehicle,
        "factors": factors,
        "injuries": injuries
    }

def parse_search_query(search_query, metadata):
    """Parses a natural language query and extracts filter values."""
    if not search_query or not search_query.strip():
        return None 

    s = search_query.lower()
    parsed_filters = {
        "boroughs": [], "years": [], "injuries": []
    }
    
    # 1. Boroughs
    for b in metadata["boroughs"]:
        if b.lower() in s:
            parsed_filters["boroughs"].append(b)
            
    # 2. Years
    for year in metadata["years"]:
        if str(year) in s:
            parsed_filters["years"].append(year)
            
    # 3. Injuries (PERSON_INJURY)
    injury_keywords = {
        "pedestrian": ["PEDESTRIAN"], 
        "cyclist": ["BICYCLIST"],
        "motorist": ["PASSENGER", "DRIVER"],
        "killed": ["KILLED"],
        "injured": ["INJURED"]
    }
    for keyword, values in injury_keywords.items():
        if keyword in s:
            for val in values:
                if val in metadata["injuries"]:
                    parsed_filters["injuries"].append(val)
    
    if any(parsed_filters.values()):
        return parsed_filters
    return None

def apply_filters(df, boroughs, years, vehicles, factors, injuries):
    """Applies filters based ONLY on the current state of the dropdowns."""
    out = df.copy()

    if boroughs and "BOROUGH" in out:
        out = out[out["BOROUGH"].isin(boroughs)]
    if years and "CRASH_DATE" in out:
        out["CRASH_DATE"] = pd.to_datetime(out["CRASH_DATE"], errors="coerce")
        out = out[out["CRASH_DATE"].dt.year.isin(years)]
    if vehicles and "VEHICLE TYPE CODE 1" in out:
        out = out[out["VEHICLE TYPE CODE 1"].isin(vehicles)]
    if factors and "CONTRIBUTING FACTOR VEHICLE 1" in out:
        out = out[out["CONTRIBUTING FACTOR VEHICLE 1"].isin(factors)]
    if injuries and "PERSON_INJURY" in out:
        out = out[out["PERSON_INJURY"].isin(injuries)]

    return out

# Convert DF to JSON for dcc.Store
def df_to_json(df):
    return df.to_json(date_format="iso", orient="split")

def json_to_df(js):
    return pd.read_json(StringIO(js), orient="split")


# ============================================================
#               APP + LAYOUT 
# ============================================================

meta = load_metadata()

# Using SLATE theme for dark mode compatibility
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE]) 
server = app.server

# Custom index string for dropdown visibility fix (using the previous full template)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Custom CSS to fix dropdown text color for dark themes */
            .Select-control,
            .Select-option,
            .Select-value-label, 
            .Select-input, 
            .Select--single > .Select-control .Select-placeholder {
                color: black !important;
            }
            .Select--multi .Select-value {
                background-color: #f8f9fa !important;
                color: black !important;
            }
            .Select--multi .Select-value-icon {
                color: black !important;
            }
        </style>
    </head>
    <body>
        <div id="react-entry-point">
            <div class="_dash-app-content">
                {%app_entry%} 
            </div>
        </div>
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = dbc.Container([
    # ------------------ HEADER ROW ------------------
    dbc.Row(className="mb-4 pt-4", style={'border-bottom': '1px solid #444'}, children=[
        dbc.Col(
            html.H1(
                [html.I(className="bi bi-car-front-fill me-3"), "NYC Collision Report"], 
                className="text-info display-4" 
            ), 
            width=9
        ),
        dbc.Col(
            html.Div(id="last-updated", className="text-secondary"), 
            width=3, 
            className="d-flex align-items-end justify-content-end"
        )
    ]),

    dbc.Row([
        # --- FILTERS (Sidebar) ---
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Filter Controls", className="card-title text-warning mb-4"),
                    
                    # Consolidated Dropdowns into a cleaner layout
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

                    # Buttons grouped together
                    dbc.Row([
                        dbc.Col(
                            dbc.Button("Generate Report", id="generate", color="success", className="w-100"), 
                            width=8
                        ),
                        dbc.Col(
                            dbc.Button("Reset", id="reset", color="danger", className="w-100"), 
                            width=4
                        )
                    ], className="mb-4"),
                    
                    dbc.Alert(id="alert", is_open=False, className="mt-3")
                ]),
                className="h-100 shadow-lg bg-dark", 
                style={"min-height": "100vh"}
            ), 
            width=3, 
            className="p-0"
        ),

        # --- VISUALIZATIONS (Main Content Area) ---
        dbc.Col(
            html.Div([
                # Row 1: Key Charts
                dbc.Row([
                    dbc.Col(dbc.Card(dcc.Graph(id="bar"), className="shadow-sm h-100"), width=6, className="mb-4"),
                    dbc.Col(dbc.Card(dcc.Graph(id="pie"), className="shadow-sm h-100"), width=6, className="mb-4"),
                ]),
                # Row 2: Time and Distribution
                dbc.Row([
                    dbc.Col(dbc.Card(dcc.Graph(id="line"), className="shadow-sm h-100"), width=6, className="mb-4"),
                    dbc.Col(dbc.Card(dcc.Graph(id="heat"), className="shadow-sm h-100"), width=6, className="mb-4"),
                ]),
                # Row 3: Map
                dbc.Row([
                    dbc.Col(dbc.Card(dcc.Graph(id="map", style={'height': '60vh'}), className="shadow-lg"), width=12),
                ])
            ], className="p-4 bg-secondary"),
            width=9,
            className="p-4"
        )
    ], className="g-0"),

    dcc.Store(id="store")
], fluid=True)


# ============================================================
#                       CALLBACKS 
# ============================================================

# ------------------------------------------------------------
# 1. Reset Button Logic
# ------------------------------------------------------------
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
    if n_clicks:
        # Reset all dropdowns, search input, and stored data
        return [], [], [], [], [], "", None, False
    raise dash.exceptions.PreventUpdate


# ------------------------------------------------------------
# 2. Data Filtering and Autofilter Callback
# ------------------------------------------------------------
@app.callback(
    Output("store", "data"),
    Output("alert", "children"),
    Output("alert", "is_open"),
    Output("borough", "value"),
    Output("year", "value"),
    Output("injury", "value"),
    
    Input("generate", "n_clicks"),
    
    State("borough", "value"),
    State("year", "value"),
    State("vehicle", "value"),
    State("factor", "value"),
    State("injury", "value"),
    State("search", "value"),
    prevent_initial_call=True
)
def filter_data_and_autofilter(n_generate, boroughs, years, vehicles, factors, injuries, search):
    if not n_generate:
        raise dash.exceptions.PreventUpdate

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
        # CRUCIAL FIX: Load the full 1GB data ONLY here, inside the callback
        # This will trigger the slow 1GB download only when the user demands it.
        df = load_full_data()
        
        filtered = apply_filters(df, final_boroughs, final_years, vehicles, factors, final_injuries)

        msg = f"Report generated successfully: *{len(filtered)} records found.*"
        
        return (
            df_to_json(filtered), 
            msg, 
            True,
            final_boroughs,
            final_years,
            final_injuries
        )
    except FileNotFoundError as e:
        msg = str(e)
        return None, msg, True, final_boroughs, final_years, final_injuries


# ------------------------------------------------------------
# 3. Graph Update Callback
# ------------------------------------------------------------
@app.callback(
    Output("bar", "figure"),
    Output("pie", "figure"),
    Output("line", "figure"),
    Output("heat", "figure"),
    Output("map", "figure"),
    Input("store", "data")
)
def update_graphs(json_data):
    # Base layout for dark theme compatibility
    transparent_layout = {
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': '#DDD'},
    }
    
    if not json_data:
        # Return empty figures with dark theme layout
        empty = px.scatter(title="No Data Loaded/Filtered")
        empty.update_layout(**transparent_layout)
        return empty, empty, empty, empty, empty

    df = json_to_df(json_data)
    
    # Helper to apply layout
    def create_fig(fig, title):
        fig.update_layout(title_text=title, **transparent_layout)
        return fig

    # BAR: Crashes by Borough
    if "BOROUGH" in df:
        bar = px.bar(df.groupby("BOROUGH").size().reset_index(name="count"),
                     x="BOROUGH", y="count")
        bar = create_fig(bar, "Crashes by Borough")
    else:
        bar = create_fig(px.scatter(), "Crashes by Borough (Data Missing)")


    # PIE: Person Injury Types
    if "PERSON_INJURY" in df:
        pie = px.pie(df, names="PERSON_INJURY")
        pie = create_fig(pie, "Person Injury Types")
    else:
        pie = create_fig(px.scatter(), "Person Injury Types (Data Missing)")

    # LINE: Crashes Over Time
    if "CRASH_DATE" in df:
        df["CRASH_DATE"] = pd.to_datetime(df["CRASH_DATE"], errors="coerce")
        df_ts = df.dropna(subset=["CRASH_DATE"])
        ts = df_ts.set_index("CRASH_DATE").resample("ME").size()
        line = px.line(ts)
        line = create_fig(line, "Crashes Over Time")
    else:
        line = create_fig(px.scatter(), "Crashes Over Time (Data Missing)")

    # HEATMAP: Hour vs Day
    if "CRASH TIME" in df and "CRASH DATE" in df:
        df["CRASH TIME"] = pd.to_datetime(df["CRASH TIME"], errors="coerce").dt.time.astype(str) # Convert time to string to avoid datetime issues
        df["HOUR"] = pd.to_datetime(df["CRASH TIME"], format='%H:%M:%S', errors="coerce").dt.hour
        df["DAY"] = pd.to_datetime(df["CRASH DATE"], errors="coerce").dt.day_name()
        pivot = df.pivot_table(index="HOUR", columns="DAY", values="COLLISION_ID", aggfunc="count").fillna(0)
        heat = px.imshow(pivot)
        heat = create_fig(heat, "Heatmap: Hour vs Day")
    else:
        heat = create_fig(px.scatter(), "Heatmap (Data Missing)")

    # MAP: Crash Locations
    if "LATITUDE" in df and "LONGITUDE" in df and "BOROUGH" in df:
        df2 = df.dropna(subset=["LATITUDE", "LONGITUDE"])
        map_fig = px.scatter_mapbox(df2, lat="LATITUDE", lon="LONGITUDE",
                                    hover_name="BOROUGH",
                                    mapbox_style="carto-darkmatter", # Dark map style
                                    zoom=10)
        map_fig = create_fig(map_fig, "Crash Locations")
        map_fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    else:
        map_fig = create_fig(px.scatter(), "Crash Locations (Data Missing)")


    return bar, pie, line, heat, map_fig
