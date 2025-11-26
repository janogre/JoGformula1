"""
Formula 1 Race Data App - Streamlit Web Interface
Interactive visualizations and analysis of F1 race data
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.fastf1_app import F1RaceDataApp
import logging
from datetime import datetime

# Disable FastF1 logging noise
logging.getLogger("fastf1").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

# Page configuration
st.set_page_config(
    page_title="F1 Race Data Analysis",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    h1 {
        color: #E10600;
    }
    h2 {
        color: #E10600;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_app():
    """Cache the F1RaceDataApp instance"""
    return F1RaceDataApp()

@st.cache_data
def load_session(year, grand_prix, session_type):
    """Cache loaded session data"""
    app = get_app()
    app.load_session(year, grand_prix, session_type)
    return app

@st.cache_data
def get_events(year):
    """Cache available events for a year"""
    app = get_app()
    return app.list_available_events(year)

# Sidebar - Session Selector
st.sidebar.title("🏁 F1 Session Selector")

current_year = datetime.now().year
year = st.sidebar.number_input(
    "Select Year:",
    min_value=2018,
    max_value=current_year,
    value=current_year,
    step=1
)

session_type_map = {"Practice 1": "FP1", "Practice 2": "FP2", "Practice 3": "FP3",
                    "Qualifying": "Q", "Race": "R"}
session_display = st.sidebar.selectbox(
    "Select Session Type:",
    list(session_type_map.keys()),
    index=4
)
session_type = session_type_map[session_display]

# Get available events
try:
    events = get_events(year)
    if events is not None:
        event_names = events["EventName"].tolist()
        selected_event = st.sidebar.selectbox(
            "Select Grand Prix:",
            event_names,
            index=len(event_names) - 1
        )
    else:
        st.sidebar.error("Could not load events")
        st.stop()
except Exception as e:
    st.sidebar.error(f"Error loading events: {e}")
    st.stop()

# Load session
try:
    with st.spinner("Loading session data..."):
        app = load_session(year, selected_event, session_type)
except Exception as e:
    st.error(f"Error loading session: {e}")
    st.stop()

# Session Information
st.title("🏎️ Formula 1 Race Data Analysis")

col1, col2, col3, col4 = st.columns(4)
session_info = app.get_session_info()

if session_info:
    with col1:
        st.metric("Event", session_info.get("Event", "N/A"))
    with col2:
        st.metric("Location", session_info.get("Location", "N/A"))
    with col3:
        st.metric("Country", session_info.get("Country", "N/A"))
    with col4:
        st.metric("Session Type", session_info.get("Session Type", "N/A"))

st.divider()

# Tabs for different analyses
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📊 Lap Times", "🏁 Telemetry", "🛣️ Track Position", "🛞 Tyre Data", "👥 Driver Comparison", "🎬 Race Replay"]
)

# ==================== TAB 1: LAP TIMES ====================
with tab1:
    st.header("Lap Times Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Get available drivers
        if app.current_session is not None:
            drivers = app.get_driver_abbreviations()
            selected_drivers = st.multiselect(
                "Select Drivers to Compare:",
                drivers,
                default=drivers[:3] if len(drivers) >= 3 else drivers
            )

            if selected_drivers:
                # Lap times comparison chart
                fig_data = []
                for driver in selected_drivers:
                    lap_times = app.get_lap_times_by_driver(driver)
                    if lap_times is not None and not lap_times.empty:
                        lap_time_sec = lap_times["LapTime"].dt.total_seconds()
                        fig_data.append({
                            "Driver": [driver] * len(lap_times),
                            "Lap": lap_times["LapNumber"].values,
                            "Time": lap_time_sec.values,
                            "Compound": lap_times["Compound"].values
                        })

                if fig_data:
                    fig = go.Figure()
                    colors = px.colors.qualitative.Plotly
                    for idx, data in enumerate(fig_data):
                        color = colors[idx % len(colors)]
                        fig.add_trace(go.Scatter(
                            x=data["Lap"],
                            y=data["Time"],
                            mode='lines+markers',
                            name=data["Driver"][0],
                            line=dict(color=color, width=2),
                            marker=dict(size=4)
                        ))

                    fig.update_layout(
                        title="Lap Times Progression",
                        xaxis_title="Lap Number",
                        yaxis_title="Lap Time (seconds)",
                        height=500,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig)

    with col2:
        # Driver comparison metrics
        if selected_drivers:
            comparison = app.compare_drivers_lap_times(selected_drivers)
            if comparison is not None and not comparison.empty:
                st.subheader("Performance Metrics")

                # Format for display
                display_data = comparison.copy()
                display_data["Fastest_Lap"] = display_data["Fastest_Lap"].astype(str)
                display_data["Avg_Lap_Time"] = display_data["Avg_Lap_Time"].astype(str)

                st.dataframe(display_data[["Driver", "Fastest_Lap", "Avg_Lap_Time", "Total_Laps", "DNF"]])

# ==================== TAB 2: TELEMETRY ====================
with tab2:
    st.header("Telemetry Analysis")

    if app.current_session is not None:
        drivers = app.get_driver_abbreviations()
        selected_driver = st.selectbox("Select Driver:", drivers, key="telemetry_driver")

        col1, col2 = st.columns([2, 1])

        with col2:
            lap_numbers = app.get_lap_times_by_driver(selected_driver)
            if lap_numbers is not None and not lap_numbers.empty:
                max_lap = lap_numbers["LapNumber"].max()
                if pd.notna(max_lap):
                    lap_num = st.number_input(
                        "Lap Number (leave blank for fastest):",
                        min_value=1,
                        max_value=int(max_lap),
                        value=None
                    )
                else:
                    lap_num = None
            else:
                lap_num = None

        with col1:
            telemetry = app.get_driver_telemetry_full(selected_driver, lap_num)

            if telemetry is not None and not telemetry.empty:
                # Create telemetry plot
                fig = go.Figure()

                if "Speed" in telemetry.columns:
                    fig.add_trace(go.Scatter(
                        y=telemetry["Speed"],
                        name="Speed (km/h)",
                        line=dict(color="blue"),
                        yaxis="y1"
                    ))

                if "Throttle" in telemetry.columns:
                    fig.add_trace(go.Scatter(
                        y=telemetry["Throttle"] * 100,
                        name="Throttle (%)",
                        line=dict(color="green", dash="dash"),
                        yaxis="y2"
                    ))

                if "Brake" in telemetry.columns:
                    fig.add_trace(go.Scatter(
                        y=telemetry["Brake"] * 100,
                        name="Brake (%)",
                        line=dict(color="red", dash="dash"),
                        yaxis="y2"
                    ))

                fig.update_layout(
                    title=f"Telemetry - {selected_driver}",
                    height=500,
                    hovermode='x unified',
                    yaxis=dict(title="Speed (km/h)", position=0),
                    yaxis2=dict(title="Throttle/Brake (%)", overlaying="y", side="right")
                )
                st.plotly_chart(fig)
            else:
                st.warning("No telemetry data available for this driver/lap")

# ==================== TAB 3: TRACK POSITION ====================
with tab3:
    st.header("Track Position Analysis")

    if app.current_session is not None:
        drivers = app.get_driver_abbreviations()
        selected_drivers_track = st.multiselect(
            "Select Drivers:",
            drivers,
            default=drivers[:3] if len(drivers) >= 3 else drivers,
            key="track_position"
        )

        if selected_drivers_track:
            fig = go.Figure()
            colors = px.colors.qualitative.Plotly

            for idx, driver in enumerate(selected_drivers_track):
                telemetry = app.get_driver_telemetry_full(driver)
                if telemetry is not None and "X" in telemetry.columns and "Y" in telemetry.columns:
                    color = colors[idx % len(colors)]
                    fig.add_trace(go.Scatter(
                        x=telemetry["X"],
                        y=telemetry["Y"],
                        mode='lines',
                        name=driver,
                        line=dict(color=color, width=2),
                        hovertemplate=f"{driver}<br>Speed: " + telemetry["Speed"].astype(str) + " km/h<extra></extra>"
                    ))

            fig.update_layout(
                title="Track Position Comparison",
                xaxis_title="X Position (m)",
                yaxis_title="Y Position (m)",
                height=600,
                hovermode='closest',
                showlegend=True
            )
            fig.update_yaxes(scaleanchor="x", scaleratio=1)
            st.plotly_chart(fig)

# ==================== TAB 4: TYRE DATA ====================
with tab4:
    st.header("Tyre Strategy and Degradation")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tyre Strategy")
        tyre_data = app.get_tyre_data()
        if tyre_data is not None and not tyre_data.empty:
            # Show tyre info for selected drivers
            if app.current_session is not None:
                drivers = app.get_driver_abbreviations()
                selected_drivers_tyre = st.multiselect(
                    "Select Drivers:",
                    drivers,
                    default=drivers[:3] if len(drivers) >= 3 else drivers,
                    key="tyre_drivers"
                )

                if selected_drivers_tyre:
                    tyre_subset = tyre_data[tyre_data["Driver"].isin(selected_drivers_tyre)]
                    st.dataframe(
                        tyre_subset[["Driver", "LapNumber", "Compound", "FreshTyre", "TyreLife"]],
                        height=400
                    )

    with col2:
        st.subheader("Tyre Degradation")
        if app.current_session is not None:
            drivers = app.get_driver_abbreviations()
            selected_driver_deg = st.selectbox(
                "Select Driver:",
                drivers,
                key="degradation_driver"
            )

            degradation = app.get_tyre_degradation(selected_driver_deg)
            if degradation is not None and not degradation.empty:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=degradation["Compound"],
                    y=degradation["Degradation"],
                    marker=dict(color=['red', 'yellow', 'cyan']),
                    text=degradation["Degradation"].round(2),
                    textposition='outside'
                ))
                fig.update_layout(
                    title=f"Tyre Degradation - {selected_driver_deg}",
                    xaxis_title="Compound",
                    yaxis_title="Degradation (seconds)",
                    height=400
                )
                st.plotly_chart(fig)

# ==================== TAB 5: DRIVER COMPARISON ====================
with tab5:
    st.header("Driver Comparison Dashboard")

    if app.current_session is not None:
        drivers = app.get_driver_abbreviations()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Select Drivers to Compare")
            comparison_drivers = st.multiselect(
                "Drivers:",
                drivers,
                default=drivers[:5] if len(drivers) >= 5 else drivers,
                key="comparison_drivers"
            )

        with col2:
            st.subheader("Performance Overview")

        if comparison_drivers:
            comparison = app.compare_drivers_lap_times(comparison_drivers)
            if comparison is not None and not comparison.empty:
                # Display metrics
                col_fastest, col_avg, col_total = st.columns(3)

                with col_fastest:
                    st.metric(
                        "Fastest Lap",
                        comparison.loc[comparison["Fastest_Lap"].idxmin()]["Driver"]
                    )

                with col_avg:
                    st.metric(
                        "Most Consistent",
                        comparison.loc[comparison["Avg_Lap_Time"].idxmin()]["Driver"]
                    )

                with col_total:
                    st.metric(
                        "Most Laps",
                        comparison.loc[comparison["Total_Laps"].idxmax()]["Driver"]
                    )

                st.divider()

                # Comparison table
                display_comparison = comparison.copy()
                display_comparison["Fastest_Lap"] = display_comparison["Fastest_Lap"].astype(str)
                display_comparison["Avg_Lap_Time"] = display_comparison["Avg_Lap_Time"].astype(str)

                st.dataframe(display_comparison)

# ==================== TAB 6: RACE REPLAY ====================
with tab6:
    st.header("🎬 Race Replay - Live Data Simulation")

    # Initialize session state for race replay
    if "race_running" not in st.session_state:
        st.session_state.race_running = False
        st.session_state.race_time = 0
        st.session_state.race_start_time = None
        st.session_state.race_time_initialized = False

    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("⏱️ Race Control")

        # Get race duration estimate
        lap_data = app.get_lap_data()
        if lap_data is not None and not lap_data.empty:
            avg_lap_time = lap_data["LapTime"].mean()
            num_laps = lap_data["LapNumber"].max()
            if pd.notna(num_laps) and pd.notna(avg_lap_time):
                race_duration_seconds = int(num_laps * avg_lap_time.total_seconds())
                race_duration_minutes = race_duration_seconds // 60

                st.write(f"**Race Duration:** {race_duration_minutes} min")

                # Start position selector
                start_minutes = st.number_input(
                    "Start at (minutes):",
                    min_value=0,
                    max_value=race_duration_minutes,
                    value=0,
                    step=1
                )

                # Only update race_time when not running
                if not st.session_state.race_running:
                    st.session_state.race_time = start_minutes * 60

                # Control buttons
                col_btn1, col_btn2, col_btn3 = st.columns(3)

                with col_btn1:
                    if st.button("▶️ Start"):
                        st.session_state.race_running = True
                        st.session_state.race_start_time = datetime.now()

                with col_btn2:
                    if st.button("⏸️ Pause"):
                        st.session_state.race_running = False

                with col_btn3:
                    if st.button("⏹️ Stop"):
                        st.session_state.race_running = False
                        st.session_state.race_time = 0

                st.divider()

                # Current time display
                if st.session_state.race_running and st.session_state.race_start_time:
                    elapsed = (datetime.now() - st.session_state.race_start_time).total_seconds()
                    st.session_state.race_time += elapsed
                    st.session_state.race_start_time = datetime.now()

                # Ensure race time doesn't exceed duration
                if st.session_state.race_time > race_duration_seconds:
                    st.session_state.race_time = race_duration_seconds
                    st.session_state.race_running = False

                minutes = int(st.session_state.race_time) // 60
                seconds = int(st.session_state.race_time) % 60

                st.metric("Current Time", f"{minutes:02d}:{seconds:02d}")

                # Manual timeline slider
                st.write("**Manual Navigation:**")
                slider_time = st.slider(
                    "Timeline:",
                    min_value=0,
                    max_value=race_duration_seconds,
                    value=int(st.session_state.race_time),
                    step=1,
                    label_visibility="collapsed"
                )

                if slider_time != st.session_state.race_time:
                    st.session_state.race_time = slider_time
                    st.session_state.race_running = False

                # Progress bar
                progress = st.session_state.race_time / race_duration_seconds
                st.progress(progress)

                st.divider()

                # Race status at current time
                st.subheader("📊 Race Status")

                if app.current_session is not None:
                    try:
                        standings = app.get_driver_standings()
                        if standings is not None and not standings.empty:
                            st.write(f"**{len(standings)} Drivers Finishing**")
                            st.dataframe(standings.head(10))
                        else:
                            st.info("No standings data available yet")
                    except Exception as e:
                        st.warning(f"Could not load standings: {e}")

                    try:
                        fastest = app.get_fastest_lap_data()
                        if fastest:
                            st.metric(
                                "Fastest Lap",
                                f"{fastest['Driver']} - {fastest['Time']}"
                            )
                        else:
                            st.info("No fastest lap data available")
                    except Exception as e:
                        st.warning(f"Could not load fastest lap: {e}")
                else:
                    st.error("Session not loaded properly")

                # Auto-refresh when racing
                if st.session_state.race_running:
                    import time
                    time.sleep(0.1)
                    st.rerun()

            else:
                st.warning("Not enough data to estimate race duration")
        else:
            st.warning("No lap data available for this session")

    with col1:
        st.subheader("📺 TV Stream")
        st.info("""
        **Your TV Display**

        Play the race video on your TV and use the controls on the right to synchronize with the data!

        The data shown will reflect what happened at that point in the race.
        """)

        # Video source input
        video_type = st.radio(
            "Video Source:",
            ["YouTube URL", "Local Video File"],
            horizontal=True
        )

        if video_type == "YouTube URL":
            youtube_url = st.text_input(
                "Enter YouTube URL:",
                placeholder="https://www.youtube.com/watch?v=..."
            )
            if youtube_url:
                if "youtube.com" in youtube_url or "youtu.be" in youtube_url:
                    try:
                        if "youtube.com" in youtube_url:
                            video_id = youtube_url.split("v=")[1].split("&")[0]
                        else:
                            video_id = youtube_url.split("/")[-1].split("?")[0]

                        embed_url = f"https://www.youtube.com/embed/{video_id}"
                        st.markdown(
                            f'<iframe width="100%" height="600" src="{embed_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>',
                            unsafe_allow_html=True
                        )
                    except:
                        st.error("Invalid YouTube URL. Please check and try again.")
                else:
                    st.error("Please enter a valid YouTube URL")
        else:
            video_file = st.file_uploader(
                "Upload video file:",
                type=["mp4", "webm", "avi", "mov"]
            )
            if video_file:
                st.video(video_file)

st.divider()
st.markdown("""
---
**F1 Race Data App** | Powered by [FastF1](https://docs.fastf1.dev/) | Made with Streamlit
""")
