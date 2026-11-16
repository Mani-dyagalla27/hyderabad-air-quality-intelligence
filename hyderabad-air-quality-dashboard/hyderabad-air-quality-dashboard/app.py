from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Hyderabad Air Quality Intelligence", page_icon="🌫️", layout="wide")

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "hyderabad_air_quality.csv"

# -------------------- DESIGN SYSTEM --------------------
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp {
  background:
    radial-gradient(ellipse at 80% 0%, rgba(20,184,166,.08), transparent 34%),
    radial-gradient(ellipse at 5% 95%, rgba(59,130,246,.055), transparent 32%),
    #090c10;
  color: #edf3f8;
}
[data-testid="stHeader"] { background: rgba(9,12,16,.88); }
[data-testid="stSidebar"] {
  background: #101820;
  border-right: 1px solid #263746;
}
.block-container { max-width: 1680px; padding-top: 1.2rem; padding-bottom: 3rem; }
h1,h2,h3 { color: #f3f7fb !important; letter-spacing: -.025em; }
p, label, .stCaption { color: #aab7c5; }
hr { border-color: #273541; }
div[data-testid="stMetric"] {
  background: linear-gradient(145deg,#17212b,#111820);
  border: 1px solid #2a3948;
  border-radius: 15px;
  padding: 16px 18px;
  animation: riseIn .65s ease both;
  transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
}
div[data-testid="stMetric"]:hover {
  transform: translateY(-4px);
  border-color: rgba(45,212,191,.65);
  box-shadow: 0 12px 28px rgba(0,0,0,.25), 0 0 18px rgba(45,212,191,.09);
}
div[data-testid="stMetric"] label { color: #9fb0c0 !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #f3f7fb !important; }
section[data-testid="stSidebar"] * { color: #e3ebf2; }
section[data-testid="stSidebar"] label {
  color: #bdcbd7 !important; font-size: .82rem; font-weight: 650 !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="input"] > div,
section[data-testid="stSidebar"] [data-testid="stDateInput"] input {
  background: #1a2631 !important;
  color: #e8f0f6 !important;
  border: 1px solid #354858 !important;
  border-radius: 9px !important;
}
section[data-testid="stSidebar"] input {
  color: #e8f0f6 !important;
  -webkit-text-fill-color: #e8f0f6 !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] {
  background: #17413f !important;
  color: #b8f3e9 !important;
  border: 1px solid #28645f !important;
  border-radius: 7px !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] span { color: #b8f3e9 !important; }
div[data-baseweb="popover"], div[data-baseweb="popover"] li {
  background: #17232d !important; color: #e8f0f6 !important;
}
div[data-baseweb="popover"] li:hover { background: #263b48 !important; }
section[data-testid="stSidebar"] [data-baseweb="select"]:focus-within > div,
section[data-testid="stSidebar"] [data-baseweb="input"]:focus-within > div {
  border-color: #2dd4bf !important;
  box-shadow: 0 0 0 2px rgba(45,212,191,.12) !important;
}
div[data-testid="stPlotlyChart"] {
  border: 1px solid transparent;
  border-radius: 13px;
  animation: chartIn .8s ease both;
  transition: border-color .2s ease, filter .2s ease;
}
div[data-testid="stPlotlyChart"]:hover {
  border-color: rgba(45,212,191,.25);
  filter: drop-shadow(0 8px 18px rgba(0,0,0,.2));
}
div[data-testid="stDataFrame"] { border: 1px solid #2a3948; border-radius: 10px; }
.dashboard-status {
  display:inline-flex; align-items:center; gap:9px;
  padding:7px 11px; margin-bottom:10px;
  color:#a8bac8; background:rgba(23,34,44,.82);
  border:1px solid #2c414e; border-radius:999px;
  font-size:10px; letter-spacing:1.15px; font-weight:700;
}
.status-dot {
  width:7px;height:7px;border-radius:50%;background:#2dd4bf;
  animation: beacon 2s ease-out infinite;
}
.section-kicker {
  color:#65d9cc; font-size:11px; letter-spacing:1.5px; font-weight:750;
}
@keyframes riseIn {
  from {opacity:0;transform:translateY(14px)}
  to {opacity:1;transform:translateY(0)}
}
@keyframes chartIn {
  from {opacity:0;transform:translateY(10px) scale(.995)}
  to {opacity:1;transform:translateY(0) scale(1)}
}
@keyframes beacon {
  0% {box-shadow:0 0 0 0 rgba(45,212,191,.55)}
  70% {box-shadow:0 0 0 8px rgba(45,212,191,0)}
  100% {box-shadow:0 0 0 0 rgba(45,212,191,0)}
}
@media (prefers-reduced-motion: reduce) {
  *,*::before,*::after {animation-duration:.01ms !important;animation-iteration-count:1 !important;transition-duration:.01ms !important}
}

/* Version 5 main-canvas refinements — sidebar intentionally unchanged */
.main-insight-grid {
  display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px;
  margin: 8px 0 18px;
}
.insight-card {
  position:relative; overflow:hidden; min-height:132px;
  padding:18px 19px; border-radius:15px;
  background:linear-gradient(145deg,rgba(23,36,47,.98),rgba(15,23,31,.98));
  border:1px solid #2a414d;
  box-shadow:0 8px 24px rgba(0,0,0,.16);
  animation:riseIn .7s ease both;
  transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease;
}
.insight-card:hover {
  transform:translateY(-3px); border-color:rgba(45,212,191,.55);
  box-shadow:0 12px 30px rgba(0,0,0,.24),0 0 20px rgba(45,212,191,.07);
}
.insight-card:after {
  content:""; position:absolute; width:110px; height:110px; right:-38px; top:-45px;
  border-radius:50%; background:rgba(45,212,191,.055); filter:blur(2px);
}
.insight-label {color:#8fa7b7;font-size:10px;letter-spacing:1.35px;font-weight:750}
.insight-value {color:#f1f7fb;font-size:25px;font-weight:750;margin-top:12px;line-height:1.15}
.insight-note {color:#91a5b4;font-size:12px;margin-top:9px}
.insight-accent {color:#65d9cc}
.section-line {
  display:flex;align-items:center;gap:10px;margin:4px 0 10px;
  color:#6edbd0;font-size:10px;letter-spacing:1.5px;font-weight:800;
}
.section-line:after {content:"";height:1px;flex:1;background:linear-gradient(90deg,#29404b,transparent)}
@media(max-width:900px) {
  .main-insight-grid {grid-template-columns:1fr}
}

</style>
""", unsafe_allow_html=True)

PLOT = dict(
    template="plotly_dark",
    paper_bgcolor="#111a22",
    plot_bgcolor="#111a22",
    font=dict(color="#dce6ee", family="Arial"),
    margin=dict(l=18, r=18, t=38, b=18),
    transition=dict(duration=550, easing="cubic-in-out"),
)

POLLUTANT_COLORS = {
    "pm25": "#2dd4bf", "pm2.5": "#2dd4bf", "pm10": "#60a5fa",
    "no2": "#fbbf24", "o3": "#a78bfa", "so2": "#fb7185", "co": "#f97316"
}

@st.cache_data
def load_data(path, modified):
    data = pd.read_csv(path)
    data["date"] = pd.to_datetime(data["date"], errors="coerce", utc=True)
    data["date"] = data["date"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    data["parameter"] = data["parameter"].astype(str).str.lower().str.strip()
    data["unit"] = data["unit"].fillna("reported unit").astype(str)
    data["location"] = data["location"].astype(str).str.strip()
    for col in ["latitude", "longitude"]:
        if col in data:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    return data.dropna(subset=["date", "value", "parameter", "location"])

def apply_plot_style(fig, height=340):
    fig.update_layout(**PLOT, height=height)
    return fig

def pretty_name(value):
    return str(value).upper().replace("PM25", "PM2.5")

if not DATA_PATH.exists():
    st.error("Dataset not found. Expected: data/hyderabad_air_quality.csv")
    st.info("Keep the data folder beside app.py, then restart Streamlit.")
    st.stop()

df = load_data(str(DATA_PATH), DATA_PATH.stat().st_mtime)
if df.empty:
    st.error("No valid measurements were found in the CSV.")
    st.stop()

# -------------------- SIDEBAR --------------------
st.sidebar.markdown("## ◈ CONTROL ROOM")
st.sidebar.caption("HYDERABAD · TELANGANA · INDIA")
st.sidebar.markdown('<div class="section-kicker">01 / TIME RANGE</div>', unsafe_allow_html=True)
dmin, dmax = df["date"].min().date(), df["date"].max().date()
date_value = st.sidebar.date_input(
    "DATE WINDOW", value=(dmin, dmax), min_value=dmin, max_value=dmax,
    label_visibility="collapsed"
)
if isinstance(date_value, (tuple, list)) and len(date_value) == 2:
    start_date, end_date = date_value
else:
    start_date, end_date = dmin, dmax

st.sidebar.markdown('<div class="section-kicker">02 / POLLUTANT FILTERS</div>', unsafe_allow_html=True)
all_params = sorted(df["parameter"].dropna().unique().tolist())
defaults = [p for p in ["pm25", "pm10", "no2", "o3", "so2", "co"] if p in all_params] or all_params
selected_params = st.sidebar.multiselect("POLLUTANTS", all_params, default=defaults, label_visibility="collapsed")

st.sidebar.markdown('<div class="section-kicker">03 / STATION FILTERS</div>', unsafe_allow_html=True)
all_stations = sorted(df["location"].dropna().unique().tolist())
selected_stations = st.sidebar.multiselect(
    "MONITORING STATIONS", all_stations, default=all_stations, label_visibility="collapsed"
)

base_filtered = df[
    df["date"].dt.date.between(start_date, end_date)
    & df["parameter"].isin(selected_params)
    & df["location"].isin(selected_stations)
].copy()

if base_filtered.empty:
    st.warning("No measurements match these filters. Widen the date range or select more pollutants/stations.")
    st.stop()

focus_params = sorted(base_filtered["parameter"].unique())
default_focus = "pm25" if "pm25" in focus_params else focus_params[0]
st.sidebar.markdown('<div class="section-kicker">04 / ANALYSIS FOCUS</div>', unsafe_allow_html=True)
chosen = st.sidebar.selectbox(
    "FOCUS MEASURE", focus_params, index=focus_params.index(default_focus),
    format_func=pretty_name, label_visibility="collapsed"
)
focus = base_filtered[base_filtered["parameter"] == chosen].copy()
focus_unit = focus["unit"].mode().iloc[0] if not focus.empty else "reported unit"

# -------------------- HEADER --------------------
hleft, hright = st.columns([3.3, 1])
with hleft:
    st.markdown(
        '<div class="dashboard-status"><span class="status-dot"></span>'
        'ANALYTICS SESSION ACTIVE · OPENAQ HISTORICAL MEASUREMENTS</div>',
        unsafe_allow_html=True
    )
    st.markdown("# 🌫️ HYDERABAD AIR QUALITY")
    st.caption("ENVIRONMENTAL INTELLIGENCE  /  PUBLIC MONITORING NETWORK")
with hright:
    st.markdown(
        f"<div style='text-align:right;padding-top:16px;color:#91a5b7;font-size:12px'>"
        f"DATA WINDOW<br><b style='color:#e6eef5'>{start_date:%d %b %Y} — {end_date:%d %b %Y}</b></div>",
        unsafe_allow_html=True
    )

# -------------------- KPI STRIP --------------------
pm25_df = base_filtered[base_filtered["parameter"].isin(["pm25", "pm2.5"])]
pm10_df = base_filtered[base_filtered["parameter"] == "pm10"]
k = st.columns(4)
k[0].metric("MEASUREMENTS IN VIEW", f"{len(base_filtered):,}")
k[1].metric("MONITORING STATIONS", f"{base_filtered['location'].nunique():,}")
k[2].metric(
    "MEAN PM2.5",
    f"{pm25_df['value'].mean():.1f} {pm25_df['unit'].mode().iloc[0]}" if not pm25_df.empty else "N/A"
)
k[3].metric(
    "MEAN PM10",
    f"{pm10_df['value'].mean():.1f} {pm10_df['unit'].mode().iloc[0]}" if not pm10_df.empty else "N/A"
)

st.markdown("---")

# -------------------- NETWORK + LATEST READING --------------------
map_col, reading_col = st.columns([2.05, 1])
with map_col:
    st.markdown("### MONITORING NETWORK")
    st.caption(
        f"{focus['location'].nunique()} selected stations · latest available {pretty_name(chosen)} reading per station · "
        "hover over a marker for station, concentration and recorded date"
    )
    geo = focus.dropna(subset=["latitude", "longitude"]).copy()
    if not geo.empty:
        latest_by_station = (
            geo.sort_values("date")
               .groupby(["location", "latitude", "longitude", "unit"], as_index=False)
               .tail(1)
        )
        # Layered circles create a soft marker halo without pretending data is live.
        fig_map = go.Figure()
        fig_map.add_trace(go.Scattermapbox(
            lat=latest_by_station["latitude"], lon=latest_by_station["longitude"],
            mode="markers",
            marker=dict(size=latest_by_station["value"].clip(lower=1).pow(0.35) * 7 + 10,
                        color=latest_by_station["value"], colorscale="Turbo",
                        opacity=.20, showscale=False),
            hoverinfo="skip",
        ))
        fig_map.add_trace(go.Scattermapbox(
            lat=latest_by_station["latitude"], lon=latest_by_station["longitude"],
            mode="markers",
            marker=dict(size=latest_by_station["value"].clip(lower=1).pow(0.35) * 4 + 7,
                        color=latest_by_station["value"], colorscale="Turbo",
                        opacity=.94, showscale=True,
                        colorbar=dict(title=pretty_name(chosen), thickness=12)),
            text=latest_by_station["location"],
            customdata=latest_by_station[["value", "unit", "date"]].astype(str).values,
            hovertemplate="<b>%{text}</b><br>Reading: %{customdata[0]} %{customdata[1]}<br>Date: %{customdata[2]}<extra></extra>",
        ))
        fig_map.update_layout(
            mapbox=dict(style="carto-darkmatter", center=dict(lat=17.385, lon=78.487), zoom=9.1),
            **{**PLOT, "height": 390, "margin": dict(l=0, r=0, t=8, b=0), "showlegend": False},
        )
        st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Station coordinates are not available for the selected measure.")

with reading_col:
    st.markdown("### SELECTED MEASURE")
    latest_date = focus["date"].max()
    latest_rows = focus[focus["date"] == latest_date]
    latest_mean = latest_rows["value"].mean()
    st.markdown(
        f"""<div style="background:linear-gradient(145deg,#182630,#111820);
        border:1px solid #31505b;border-radius:16px;padding:24px;min-height:190px;
        box-shadow:0 0 26px rgba(45,212,191,.07)">
        <div style="color:#91b6c0;font-size:11px;letter-spacing:1.2px">LATEST AVAILABLE DAILY READING</div>
        <div style="font-size:46px;font-weight:750;color:#f3f8fb;margin-top:12px">{latest_mean:,.2f}</div>
        <div style="color:#9edbd4;font-size:14px">{focus_unit} · {pretty_name(chosen)}</div>
        <div style="color:#74899b;font-size:12px;margin-top:20px">Recorded {latest_date:%d %b %Y}</div>
        </div>""", unsafe_allow_html=True
    )
    st.caption("Measured concentration, not an AQI score. The latest date reflects this dataset's available records.")

# -------------------- POLLUTANT SNAPSHOT --------------------
st.markdown("### POLLUTANT SNAPSHOT")
snap_params = ["pm25", "pm10", "no2", "o3"]
snap_cols = st.columns(4)
for col, param in zip(snap_cols, snap_params):
    subset = base_filtered[base_filtered["parameter"] == param]
    if subset.empty:
        col.metric(pretty_name(param), "No data")
    else:
        u = subset["unit"].mode().iloc[0]
        col.metric(pretty_name(param), f"{subset['value'].mean():.2f} {u}")


# -------------------- AUTOMATED INSIGHTS --------------------
st.markdown('<div class="section-line">LIVE ANALYTICS / DATA-DERIVED INSIGHTS</div>', unsafe_allow_html=True)

# Every insight below is calculated from the currently selected date, pollutant and station filters.
focus_station_means = focus.groupby("location")["value"].mean().sort_values(ascending=False)
top_station_name = str(focus_station_means.index[0]) if not focus_station_means.empty else "Not available"
top_station_value = float(focus_station_means.iloc[0]) if not focus_station_means.empty else None

focus_month = focus.copy()
focus_month["month_start"] = focus_month["date"].dt.to_period("M").dt.to_timestamp()
month_means = focus_month.groupby("month_start")["value"].mean()
if not month_means.empty:
    peak_month_start = month_means.idxmax()
    peak_month_name = peak_month_start.strftime("%b %Y")
    peak_month_value = float(month_means.loc[peak_month_start])
else:
    peak_month_name, peak_month_value = "Not available", None

daily_focus = focus.groupby(pd.Grouper(key="date", freq="D"))["value"].mean().dropna()
if not daily_focus.empty:
    peak_day = daily_focus.idxmax()
    peak_day_value = float(daily_focus.max())
    peak_day_label = peak_day.strftime("%d %b %Y")
else:
    peak_day_value, peak_day_label = None, "Not available"

insight_cols = st.columns(3)
with insight_cols[0]:
    st.markdown(
        f"""<div class="insight-card">
        <div class="insight-label">HIGHEST MEAN STATION</div>
        <div class="insight-value">{top_station_name}</div>
        <div class="insight-note">{f'{top_station_value:.2f} {focus_unit} average' if top_station_value is not None else 'No station data available'}</div>
        </div>""", unsafe_allow_html=True
    )
with insight_cols[1]:
    st.markdown(
        f"""<div class="insight-card">
        <div class="insight-label">HIGHEST MONTHLY MEAN</div>
        <div class="insight-value insight-accent">{peak_month_name}</div>
        <div class="insight-note">{f'{peak_month_value:.2f} {focus_unit} average' if peak_month_value is not None else 'No monthly data available'}</div>
        </div>""", unsafe_allow_html=True
    )
with insight_cols[2]:
    st.markdown(
        f"""<div class="insight-card">
        <div class="insight-label">HIGHEST DAILY MEAN</div>
        <div class="insight-value">{f'{peak_day_value:.2f}' if peak_day_value is not None else 'N/A'}</div>
        <div class="insight-note">{peak_day_label} · {focus_unit}</div>
        </div>""", unsafe_allow_html=True
    )

st.caption(
    "These observations are calculated from the current filtered selection. "
    "They describe recorded concentrations and do not represent an official AQI category or health alert."
)

st.markdown("---")

# -------------------- DAILY TREND --------------------
st.markdown("### 01 / POLLUTION TREND")
st.caption(f"Daily mean {pretty_name(chosen)} · {focus_unit}")
trend = (
    focus.groupby(pd.Grouper(key="date", freq="D"), as_index=False)["value"]
         .mean().dropna()
)
trend_fig = go.Figure()
trend_fig.add_trace(go.Scatter(
    x=trend["date"], y=trend["value"], mode="lines",
    line=dict(color=POLLUTANT_COLORS.get(chosen, "#2dd4bf"), width=2.3),
    fill="tozeroy", fillcolor="rgba(45,212,191,.10)",
    hovertemplate="%{x|%d %b %Y}<br>%{y:.2f} " + focus_unit + "<extra></extra>"
))
trend_fig.update_layout(
    xaxis_title="Date", yaxis_title=f"{pretty_name(chosen)} ({focus_unit})",
    hovermode="x unified", height=330, **PLOT
)
st.plotly_chart(trend_fig, use_container_width=True, config={"displayModeBar": False})

# -------------------- STATION RANKING + MONTHLY PROFILE --------------------
left, right = st.columns(2)
with left:
    st.markdown("### 02 / STATION LEADERBOARD")
    station_avg = (
        focus.groupby("location", as_index=False)["value"].mean()
             .sort_values("value", ascending=True)
    )
    station_fig = px.bar(
        station_avg, x="value", y="location", orientation="h",
        text_auto=".1f", labels={"value": focus_unit, "location": "Monitoring station"},
    )
    station_fig.update_traces(
        marker=dict(color=station_avg["value"], colorscale=[[0,"#1e8f89"],[1,"#60a5fa"]]),
        textfont_color="#f4f8fb",
        hovertemplate="%{y}<br>Mean: %{x:.2f} " + focus_unit + "<extra></extra>"
    )
    station_fig.update_layout(
        xaxis_title=f"Mean {pretty_name(chosen)} ({focus_unit})",
        yaxis_title="", height=max(340, 34 * len(station_avg)), **PLOT
    )
    st.plotly_chart(station_fig, use_container_width=True, config={"displayModeBar": False})
    top_five = station_avg.sort_values("value", ascending=False).head(5).copy()
    top_five["Rank"] = range(1, len(top_five) + 1)
    top_five = top_five[["Rank", "location", "value"]].rename(
        columns={"location": "Monitoring station", "value": f"Mean ({focus_unit})"}
    )
    with st.expander("VIEW TOP 5 STATIONS"):
        st.dataframe(top_five, hide_index=True, use_container_width=True)

with right:
    st.markdown("### 03 / MONTHLY PROFILE")
    st.caption("Calendar-month averages pooled across all selected years; use Historical Comparison to inspect year-by-year differences.")
    monthly = focus.copy()
    monthly["month_no"] = monthly["date"].dt.month
    monthly["month"] = monthly["date"].dt.strftime("%b")
    monthly_avg = (
        monthly.groupby(["month_no", "month"], as_index=False)["value"]
               .mean().sort_values("month_no")
    )
    month_fig = px.bar(
        monthly_avg, x="month", y="value", text_auto=".1f",
        labels={"month": "Month", "value": focus_unit},
    )
    month_fig.update_traces(marker_color="#9b8cff", textfont_color="#f4f8fb")
    month_fig.update_layout(
        xaxis_title="Calendar month", yaxis_title=f"Mean ({focus_unit})",
        height=360, **PLOT
    )
    st.plotly_chart(month_fig, use_container_width=True, config={"displayModeBar": False})

# -------------------- MONTH x YEAR HEATMAP --------------------
st.markdown("---")
st.markdown("### 04 / POLLUTION INTENSITY HEATMAP")
st.caption(f"Monthly mean {pretty_name(chosen)} by year · same measurement unit throughout")
heat = focus.copy()
heat["year"] = heat["date"].dt.year
heat["month_num"] = heat["date"].dt.month
heat["month_name"] = heat["date"].dt.strftime("%b")
heat_agg = heat.groupby(["year", "month_num", "month_name"], as_index=False)["value"].mean()
if not heat_agg.empty:
    heat_pivot = heat_agg.pivot(index="year", columns="month_num", values="value").reindex(
        columns=range(1, 13)
    )
    heat_fig = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        y=heat_pivot.index.astype(str),
        colorscale=[[0,"#123b43"],[.35,"#1c8b83"],[.7,"#f0b84b"],[1,"#f06a62"]],
        colorbar=dict(title=focus_unit, thickness=12),
        hovertemplate="Year %{y}<br>%{x}<br>Mean: %{z:.2f} " + focus_unit + "<extra></extra>"
    ))
    heat_fig.update_layout(height=max(230, 72 * len(heat_pivot)), **PLOT)
    st.plotly_chart(heat_fig, use_container_width=True, config={"displayModeBar": False})
else:
    st.info("Not enough data to build the monthly heatmap.")

# -------------------- HISTORICAL COMPARISON --------------------
st.markdown("### 05 / HISTORICAL COMPARISON")
st.caption(f"Compare each year's monthly pattern for {pretty_name(chosen)} · {focus_unit}. Missing months are left blank, not estimated.")
history = focus.copy()
history["year"] = history["date"].dt.year.astype(str)
history["month_no"] = history["date"].dt.month
history["month"] = history["date"].dt.strftime("%b")
history_agg = (
    history.groupby(["year", "month_no", "month"], as_index=False)["value"]
           .mean().sort_values(["year", "month_no"])
)
if not history_agg.empty:
    hist_fig = px.line(
        history_agg, x="month", y="value", color="year", markers=True,
        category_orders={"month":["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]},
        labels={"month":"Month","value":focus_unit,"year":"Year"},
        color_discrete_sequence=["#2dd4bf","#60a5fa","#fbbf24","#a78bfa","#fb7185"]
    )
    hist_fig.update_layout(height=350, **PLOT, hovermode="x unified")
    st.plotly_chart(hist_fig, use_container_width=True, config={"displayModeBar": False})
else:
    st.info("Not enough history for a year-over-year comparison.")

# -------------------- POLLUTANT COMPARISON --------------------
st.markdown("### 06 / POLLUTANT COMPARISON")
st.caption("Different pollutants and units are not directly comparable. Values are grouped by reported unit.")
comparison = (
    base_filtered.groupby(["parameter", "unit"], as_index=False)["value"].mean()
                 .rename(columns={"value":"mean_value"})
)
comparison["measure"] = comparison["parameter"].map(pretty_name)
comp_fig = px.bar(
    comparison, x="measure", y="mean_value", color="unit",
    facet_col="unit", facet_col_wrap=3, text_auto=".2f",
    labels={"measure":"Pollutant","mean_value":"Mean reading","unit":"Reported unit"}
)
comp_fig.update_layout(height=350, **PLOT, showlegend=False)
comp_fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
st.plotly_chart(comp_fig, use_container_width=True, config={"displayModeBar": False})

# -------------------- DATA QUALITY + EXPORT --------------------
with st.expander("DATA QUALITY · SOURCE · RECORDS"):
    st.write(f"Full dataset: {len(df):,} rows · Current filtered view: {len(base_filtered):,} rows")
    st.write(f"Coverage: {df['date'].min():%d %b %Y} — {df['date'].max():%d %b %Y}")
    st.write(f"Distinct stations: {df['location'].nunique():,}")
    if "sensor_id" in df.columns:
        st.write(f"Distinct sensors: {df['sensor_id'].nunique():,}")
    missing_coords = (
        int(df[["latitude", "longitude"]].isna().any(axis=1).sum())
        if {"latitude", "longitude"}.issubset(df.columns) else None
    )
    if missing_coords is not None:
        st.write(f"Rows without complete coordinates: {missing_coords:,}")
    duplicate_keys = [c for c in ["date", "sensor_id", "parameter", "value"] if c in df.columns]
    duplicate_count = int(df.duplicated(subset=duplicate_keys).sum()) if duplicate_keys else int(df.duplicated().sum())
    st.write(f"Potential duplicate measurement rows: {duplicate_count:,}")
    st.write(f"Rows with valid date, value, pollutant and station after cleaning: {len(df):,}")
    if "provider" in df.columns:
        st.write("Data providers:", ", ".join(sorted(df["provider"].dropna().astype(str).unique())))
    st.caption("Missing periods are not interpolated. Extreme readings should be checked against provider metadata.")
    st.dataframe(base_filtered.sort_values("date", ascending=False).head(500), use_container_width=True)
    st.download_button(
        "EXPORT FILTERED DATA · CSV",
        base_filtered.to_csv(index=False).encode("utf-8"),
        file_name="hyderabad_air_quality_filtered.csv",
        mime="text/csv"
    )

st.caption(
    "Source: OpenAQ public measurements as retained in the project CSV. "
    "These charts show pollutant concentrations, not AQI. Station coverage and measurement availability vary over time. "
    "Station and time-period averages are descriptive; they are not population-weighted citywide exposure estimates."
)


st.caption("HYDERABAD AIR QUALITY INTELLIGENCE · FINAL PORTFOLIO BUILD")
