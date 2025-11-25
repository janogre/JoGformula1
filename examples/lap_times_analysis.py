"""
Eksempel: Avansert rundetids-analyse
Detaljert analyse og visualisering av rundetider med sammenligninger
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib.pyplot as plt
import numpy as np
from fastf1_app import F1RaceDataApp


def plot_lap_times_detailed(app, driver: str):
    """Plotter detaljert rundetids-progresjon for en sjåfør"""
    lap_data = app.get_lap_times_by_driver(driver)
    if lap_data is None or lap_data.empty:
        print(f"Ingen data for {driver}")
        return None

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # Rundetider over tid
    lap_times_sec = lap_data["LapTime"].dt.total_seconds()
    axes[0].plot(
        lap_data["LapNumber"],
        lap_times_sec,
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=4,
        color="blue",
    )
    axes[0].set_xlabel("Rundenummer", fontsize=11)
    axes[0].set_ylabel("Rundetid (sekunder)", fontsize=11)
    axes[0].set_title(f"Rundetids-progresjon - {driver}", fontsize=13, fontweight="bold")
    axes[0].grid(True, alpha=0.3)

    # Fargekoding etter dekk-type
    compounds = lap_data["Compound"].unique()
    colors = {"SOFT": "red", "MEDIUM": "yellow", "HARD": "cyan", "INTERMEDIATE": "green", "WET": "blue"}

    for compound in compounds:
        compound_data = lap_data[lap_data["Compound"] == compound]
        compound_times = compound_data["LapTime"].dt.total_seconds()
        color = colors.get(compound, "gray")
        axes[1].scatter(
            compound_data["LapNumber"],
            compound_times,
            label=f"{compound}",
            s=100,
            color=color,
            alpha=0.7,
        )

    axes[1].set_xlabel("Rundenummer", fontsize=11)
    axes[1].set_ylabel("Rundetid (sekunder)", fontsize=11)
    axes[1].set_title(f"Dekk-strategi - {driver}", fontsize=13, fontweight="bold")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_driver_comparison(app, drivers: list):
    """Plotter sammenligning av rundetider mellom flere sjåfører"""
    if not drivers:
        print("Ingen sjåfører angitt")
        return None

    fig, ax = plt.subplots(figsize=(14, 7))

    for driver in drivers:
        lap_data = app.get_lap_times_by_driver(driver)
        if lap_data is not None and not lap_data.empty:
            lap_times_sec = lap_data["LapTime"].dt.total_seconds()
            ax.plot(
                lap_data["LapNumber"],
                lap_times_sec,
                marker="o",
                label=driver,
                linewidth=2,
                markersize=3,
            )

    ax.set_xlabel("Rundenummer", fontsize=12)
    ax.set_ylabel("Rundetid (sekunder)", fontsize=12)
    ax.set_title("Rundetids-sammenligning mellom sjåfører", fontsize=14, fontweight="bold")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_lap_times_delta(app, drivers: list, reference_driver: str):
    """Plotter tidsdifferanse relativt til en referanse-sjåfør"""
    if reference_driver not in drivers:
        print(f"{reference_driver} er ikke i listen over sjåfører")
        return None

    ref_laps = app.get_lap_times_by_driver(reference_driver)
    if ref_laps is None or ref_laps.empty:
        return None

    ref_times = ref_laps.set_index("LapNumber")["LapTime"].dt.total_seconds()

    fig, ax = plt.subplots(figsize=(14, 7))

    for driver in drivers:
        if driver == reference_driver:
            continue

        lap_data = app.get_lap_times_by_driver(driver)
        if lap_data is not None and not lap_data.empty:
            driver_times = lap_data.set_index("LapNumber")["LapTime"].dt.total_seconds()

            # Beregn delta
            delta = []
            lap_nums = []
            for lap_num in driver_times.index:
                if lap_num in ref_times.index:
                    delta.append(driver_times[lap_num] - ref_times[lap_num])
                    lap_nums.append(lap_num)

            ax.plot(lap_nums, delta, marker="o", label=driver, linewidth=2, markersize=3)

    ax.axhline(y=0, color="black", linestyle="--", linewidth=1, alpha=0.5)
    ax.set_xlabel("Rundenummer", fontsize=12)
    ax.set_ylabel(f"Tidsdifferanse vs {reference_driver} (sekunder)", fontsize=12)
    ax.set_title(f"Rundetids-differanse vs {reference_driver}", fontsize=14, fontweight="bold")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_average_lap_times(app, drivers: list):
    """Plotter gjennomsnittlige rundetider for sjåfører"""
    fig, ax = plt.subplots(figsize=(12, 6))

    avg_times = []
    driver_names = []

    for driver in drivers:
        comparison = app.compare_drivers_lap_times([driver])
        if comparison is not None and not comparison.empty:
            avg_time = comparison.iloc[0]["Avg_Lap_Time"]
            if pd.notna(avg_time):
                avg_times.append(avg_time.total_seconds())
                driver_names.append(driver)

    if avg_times:
        sorted_indices = np.argsort(avg_times)
        sorted_drivers = [driver_names[i] for i in sorted_indices]
        sorted_times = [avg_times[i] for i in sorted_indices]

        bars = ax.bar(sorted_drivers, sorted_times, color="steelblue", edgecolor="black")

        # Fargelegge raskeste
        bars[0].set_color("gold")

        ax.set_ylabel("Gjennomsnittlig rundetid (sekunder)", fontsize=12)
        ax.set_title("Gjennomsnittlige rundetider", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3, axis="y")

        plt.xticks(rotation=45)
        plt.tight_layout()

    return fig


def main():
    """Hovedfunksjon"""
    print("=" * 60)
    print("AVANSERT RUNDETIDS-ANALYSE: Monza 2024")
    print("=" * 60)

    app = F1RaceDataApp()
    app.load_session(2024, "Monza", session_type="R")

    if app.current_session is None:
        print("Kunne ikke laste sesjon")
        return

    # Hent første 5 sjåfører
    all_drivers = app.current_session.drivers[:5]

    # 1. Detaljert rundetids-progresjon
    print(f"\n1. Lager detaljert rundetids-progresjon for {all_drivers[0]}...")
    fig1 = plot_lap_times_detailed(app, all_drivers[0])
    if fig1:
        fig1.savefig(
            Path(__file__).parent.parent / "output_lap_times_detailed.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_lap_times_detailed.png'")

    # 2. Sammenligning av flere sjåfører
    print(f"\n2. Lager sammenligning av rundetider for {len(all_drivers)} sjåfører...")
    fig2 = plot_driver_comparison(app, all_drivers)
    if fig2:
        fig2.savefig(
            Path(__file__).parent.parent / "output_driver_comparison.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_driver_comparison.png'")

    # 3. Tidsdifferanse vs raskeste
    if len(all_drivers) > 1:
        reference = all_drivers[0]
        print(f"\n3. Lager tidsdifferanse-graf vs {reference}...")
        fig3 = plot_lap_times_delta(app, all_drivers, reference)
        if fig3:
            fig3.savefig(
                Path(__file__).parent.parent / "output_lap_times_delta.png",
                dpi=100,
                bbox_inches="tight",
            )
            print("   ✓ Lagret som 'output_lap_times_delta.png'")

    # 4. Gjennomsnittlige rundetider
    print(f"\n4. Lager gjennomsnittlige rundetider...")
    fig4 = plot_average_lap_times(app, all_drivers)
    if fig4:
        fig4.savefig(
            Path(__file__).parent.parent / "output_average_lap_times.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_average_lap_times.png'")

    print("\n✓ Alle visualiseringer opprettet!")


if __name__ == "__main__":
    import pandas as pd

    main()
