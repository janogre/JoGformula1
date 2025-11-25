"""
Eksempel: Driver-sammenligning Dashboard
Sammenligner flere sjåfører basert på ytelses-metriker
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib.pyplot as plt
import numpy as np
from fastf1_app import F1RaceDataApp


def plot_driver_metrics_comparison(app, drivers: list):
    """
    Sammenligner flere metriker for sjåfører side-by-side
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    # 1. Raskeste runde
    ax = axes[0, 0]
    fastest_times = []
    for driver in drivers:
        lap_data = app.get_lap_times_by_driver(driver)
        if lap_data is not None and not lap_data.empty:
            fastest = lap_data["LapTime"].min()
            fastest_times.append(fastest.total_seconds())
        else:
            fastest_times.append(0)

    ax.barh(drivers, fastest_times, color="steelblue")
    ax.set_xlabel("Raskeste rundetid (sekunder)", fontsize=11)
    ax.set_title("Raskeste Runde", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    # 2. Gjennomsnittlig rundetid
    ax = axes[0, 1]
    avg_times = []
    for driver in drivers:
        comp = app.compare_drivers_lap_times([driver])
        if comp is not None and not comp.empty:
            avg_time = comp.iloc[0]["Avg_Lap_Time"]
            if pd.notna(avg_time):
                avg_times.append(avg_time.total_seconds())
            else:
                avg_times.append(0)
        else:
            avg_times.append(0)

    ax.barh(drivers, avg_times, color="orange")
    ax.set_xlabel("Gjennomsnittlig rundetid (sekunder)", fontsize=11)
    ax.set_title("Gjennomsnittlig Runde", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    # 3. Antall runder
    ax = axes[1, 0]
    lap_counts = []
    for driver in drivers:
        lap_data = app.get_lap_times_by_driver(driver)
        if lap_data is not None:
            lap_counts.append(len(lap_data))
        else:
            lap_counts.append(0)

    ax.barh(drivers, lap_counts, color="green")
    ax.set_xlabel("Antall runder fullført", fontsize=11)
    ax.set_title("Runder Fullført", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    # 4. Degradering (hvis tilgjengelig)
    ax = axes[1, 1]
    max_degradation = []
    for driver in drivers:
        deg = app.get_tyre_degradation(driver)
        if deg is not None and not deg.empty:
            max_deg = deg["Degradation"].max()
            max_degradation.append(max_deg)
        else:
            max_degradation.append(0)

    ax.barh(drivers, max_degradation, color="red")
    ax.set_xlabel("Max Degradering (sekunder)", fontsize=11)
    ax.set_title("Maksimal Dekk-degradering", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    plt.tight_layout()
    return fig


def plot_consistency_analysis(app, drivers: list):
    """
    Analyserer konsistens (stabilitet) mellom sjåfører
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    for driver in drivers:
        lap_data = app.get_lap_times_by_driver(driver)
        if lap_data is not None and not lap_data.empty:
            # Beregn standardavvik for rundetider
            lap_times = lap_data["LapTime"].dt.total_seconds()
            consistency = lap_times.std()
            ax.scatter([driver], [consistency], s=200, alpha=0.6, label=driver)

    ax.set_ylabel("Standardavvik rundetider (sekunder)", fontsize=12)
    ax.set_title("Konsistens-analyse (lavere = mer stabil)", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    return fig


def plot_performance_over_race(app, drivers: list):
    """
    Viser ytelse-progresjon gjennom løpet for sjåfører
    """
    fig, ax = plt.subplots(figsize=(16, 7))

    colors = ["red", "blue", "green", "orange", "purple", "brown"]

    for idx, driver in enumerate(drivers):
        lap_data = app.get_lap_times_by_driver(driver)
        if lap_data is not None and not lap_data.empty:
            # Beregn løpende gjennomsnitt (5-rund moving average)
            lap_times = lap_data["LapTime"].dt.total_seconds()
            moving_avg = lap_times.rolling(window=5, center=True).mean()

            color = colors[idx % len(colors)]
            ax.plot(lap_data["LapNumber"], moving_avg, linewidth=2.5, label=driver, color=color)

    ax.set_xlabel("Rundenummer", fontsize=12)
    ax.set_ylabel("Gjennom. rundetid - 5 rund MA (sekunder)", fontsize=12)
    ax.set_title("Ytelse-progresjon gjennom løpet (5-rund gjennomsnitt)", fontsize=14, fontweight="bold")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_head_to_head_comparison(app, driver1: str, driver2: str):
    """
    Direkte sammenligning mellom to sjåfører
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Hent data
    d1_laps = app.get_lap_times_by_driver(driver1)
    d2_laps = app.get_lap_times_by_driver(driver2)
    d1_comp = app.compare_drivers_lap_times([driver1])
    d2_comp = app.compare_drivers_lap_times([driver2])

    # 1. Rundetider direktesammenligning
    ax = axes[0, 0]
    if d1_laps is not None and d2_laps is not None:
        d1_times = d1_laps["LapTime"].dt.total_seconds()
        d2_times = d2_laps["LapTime"].dt.total_seconds()
        ax.plot(d1_laps["LapNumber"], d1_times, marker="o", label=driver1, linewidth=2)
        ax.plot(d2_laps["LapNumber"], d2_times, marker="s", label=driver2, linewidth=2)
        ax.set_xlabel("Rundenummer", fontsize=11)
        ax.set_ylabel("Rundetid (sekunder)", fontsize=11)
        ax.set_title("Rundetider direktesammenligning", fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)

    # 2. Raskeste runde
    ax = axes[0, 1]
    if d1_comp is not None and d2_comp is not None:
        fastest_times = [
            d1_comp.iloc[0]["Fastest_Lap"].total_seconds(),
            d2_comp.iloc[0]["Fastest_Lap"].total_seconds(),
        ]
        bars = ax.bar([driver1, driver2], fastest_times, color=["red", "blue"])
        ax.set_ylabel("Raskeste rundetid (sekunder)", fontsize=11)
        ax.set_title("Raskeste Runde", fontsize=12)
        ax.grid(True, alpha=0.3, axis="y")

    # 3. Gjennomsnittlig rundetid
    ax = axes[1, 0]
    if d1_comp is not None and d2_comp is not None:
        avg_times = [
            d1_comp.iloc[0]["Avg_Lap_Time"].total_seconds(),
            d2_comp.iloc[0]["Avg_Lap_Time"].total_seconds(),
        ]
        bars = ax.bar([driver1, driver2], avg_times, color=["red", "blue"])
        ax.set_ylabel("Gjennomsnittlig rundetid (sekunder)", fontsize=11)
        ax.set_title("Gjennomsnittlig Runde", fontsize=12)
        ax.grid(True, alpha=0.3, axis="y")

    # 4. Statistikk
    ax = axes[1, 1]
    ax.axis("off")

    stats_text = f"{driver1}:\n"
    if d1_comp is not None and not d1_comp.empty:
        stats_text += f"  Runder: {int(d1_comp.iloc[0]['Total_Laps'])}\n"
        stats_text += f"  DNF: {d1_comp.iloc[0]['DNF']}\n\n"

    stats_text += f"{driver2}:\n"
    if d2_comp is not None and not d2_comp.empty:
        stats_text += f"  Runder: {int(d2_comp.iloc[0]['Total_Laps'])}\n"
        stats_text += f"  DNF: {d2_comp.iloc[0]['DNF']}\n"

    ax.text(0.1, 0.9, stats_text, fontsize=12, verticalalignment="top",
           fontfamily="monospace", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    return fig


def main():
    """Hovedfunksjon"""
    print("=" * 60)
    print("DRIVER-SAMMENLIGNING: Monza 2024")
    print("=" * 60)

    app = F1RaceDataApp()
    app.load_session(2024, "Monza", session_type="R")

    if app.current_session is None:
        print("Kunne ikke laste sesjon")
        return

    all_drivers = app.current_session.drivers[:5]

    # 1. Ytelsesmetriker
    print(f"\n1. Lager ytelsesmetriker for {len(all_drivers)} sjåfører...")
    fig1 = plot_driver_metrics_comparison(app, all_drivers)
    if fig1:
        fig1.savefig(
            Path(__file__).parent.parent / "output_driver_metrics.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_driver_metrics.png'")

    # 2. Konsistens-analyse
    print(f"\n2. Lager konsistens-analyse...")
    fig2 = plot_consistency_analysis(app, all_drivers)
    if fig2:
        fig2.savefig(
            Path(__file__).parent.parent / "output_consistency.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_consistency.png'")

    # 3. Ytelse over race
    print(f"\n3. Lager ytelse-progresjon gjennom løpet...")
    fig3 = plot_performance_over_race(app, all_drivers)
    if fig3:
        fig3.savefig(
            Path(__file__).parent.parent / "output_performance_over_race.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_performance_over_race.png'")

    # 4. Head-to-head sammenligning
    if len(all_drivers) >= 2:
        print(f"\n4. Lager head-to-head sammenligning: {all_drivers[0]} vs {all_drivers[1]}...")
        fig4 = plot_head_to_head_comparison(app, all_drivers[0], all_drivers[1])
        if fig4:
            fig4.savefig(
                Path(__file__).parent.parent / "output_head_to_head.png",
                dpi=100,
                bbox_inches="tight",
            )
            print(f"   ✓ Lagret som 'output_head_to_head.png'")

    print("\n✓ Alle driver-sammenlignings-visualiseringer opprettet!")


if __name__ == "__main__":
    import pandas as pd

    main()
