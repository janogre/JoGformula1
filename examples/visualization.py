"""
Eksempel: Visualisering av race-data
Viser hvordan å lage grafer og visualiseringer av F1-data
"""

import sys
from pathlib import Path

# Legg til src-mappen til path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib.pyplot as plt
from fastf1_app import F1RaceDataApp


def plot_lap_times_comparison(app):
    """Plotter sammenligning av rundetider"""
    laps = app.get_lap_data()
    if laps is None:
        return

    # Hent top 5 sjåfører etter antall runder
    top_drivers = laps["Driver"].value_counts().head(5).index

    fig, ax = plt.subplots(figsize=(12, 6))

    for driver in top_drivers:
        driver_laps = laps[laps["Driver"] == driver].copy()
        # Konverter LapTime til sekunder for plotting
        driver_laps["LapTime_sec"] = (
            driver_laps["LapTime"].dt.total_seconds()
        )
        ax.plot(
            driver_laps.index,
            driver_laps["LapTime_sec"],
            marker="o",
            label=driver,
            linewidth=2,
        )

    ax.set_xlabel("Runde", fontsize=12)
    ax.set_ylabel("Rundetid (sekunder)", fontsize=12)
    ax.set_title("Rundetider Sammenligning - Top 5 Sjåfører", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    return fig


def plot_telemetry_trace(app, driver):
    """Plotter telemetri-data (hastighet, gass, bremsing)"""
    telemetry = app.get_driver_telemetry(driver)
    if telemetry is None:
        return

    fig, axes = plt.subplots(3, 1, figsize=(14, 10))

    # Hastighet
    if "Speed" in telemetry.columns:
        axes[0].plot(telemetry["Speed"], linewidth=1, color="blue")
        axes[0].set_ylabel("Hastighet (km/h)", fontsize=10)
        axes[0].set_title(f"Telemetri for {driver}", fontsize=12)
        axes[0].grid(True, alpha=0.3)

    # Gass-pedal (Throttle)
    if "Throttle" in telemetry.columns:
        axes[1].plot(telemetry["Throttle"], linewidth=1, color="green")
        axes[1].set_ylabel("Gass (%)", fontsize=10)
        axes[1].set_ylim([0, 105])
        axes[1].grid(True, alpha=0.3)

    # Bremsing
    if "Brake" in telemetry.columns:
        axes[2].plot(telemetry["Brake"], linewidth=1, color="red")
        axes[2].set_ylabel("Bremsing (%)", fontsize=10)
        axes[2].set_xlabel("Data-punkt", fontsize=10)
        axes[2].set_ylim([0, 105])
        axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_driver_standings(app):
    """Plotter sluttresultat"""
    standings = app.get_driver_standings()
    if standings is None or standings.empty:
        return

    # Filtrer kun sjåfører som fullførte (har poeng)
    finished = standings[standings["Points"] > 0].head(10)

    fig, ax = plt.subplots(figsize=(12, 6))

    drivers = finished["Driver"].values
    points = finished["Points"].values

    bars = ax.barh(drivers, points, color="steelblue")

    # Fargelegge top 3
    for i, bar in enumerate(bars[:3]):
        if i == 0:
            bar.set_color("gold")
        elif i == 1:
            bar.set_color("silver")
        elif i == 2:
            bar.set_color("#CD7F32")  # bronze

    ax.set_xlabel("Poeng", fontsize=12)
    ax.set_title("Sluttresultat - Top 10", fontsize=14)
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()

    return fig


def main():
    """Hovedfunksjon"""
    print("=" * 60)
    print("VISUALISERING: Monza 2024 Race")
    print("=" * 60)

    app = F1RaceDataApp()
    app.load_session(2024, "Monza", session_type="R")

    # 1. Rundetider sammenligning
    print("\nLager visualisering: Rundetider sammenligning...")
    fig1 = plot_lap_times_comparison(app)
    if fig1:
        fig1.savefig(
            Path(__file__).parent.parent / "output_lap_times.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("  ✓ Lagret som 'output_lap_times.png'")

    # 2. Sluttresultat
    print("Lager visualisering: Sluttresultat...")
    fig2 = plot_driver_standings(app)
    if fig2:
        fig2.savefig(
            Path(__file__).parent.parent / "output_standings.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("  ✓ Lagret som 'output_standings.png'")

    # 3. Telemetri for første sjåfør
    if app.current_session is not None:
        driver = app.current_session.drivers[0]
        print(f"Lager visualisering: Telemetri for {driver}...")
        fig3 = plot_telemetry_trace(app, driver)
        if fig3:
            fig3.savefig(
                Path(__file__).parent.parent / f"output_telemetry_{driver}.png",
                dpi=100,
                bbox_inches="tight",
            )
            print(f"  ✓ Lagret som 'output_telemetry_{driver}.png'")

    print("\nVisualiseringer opprettet!")
    plt.show()


if __name__ == "__main__":
    main()
