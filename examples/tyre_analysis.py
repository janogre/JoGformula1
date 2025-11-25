"""
Eksempel: Dekkdata- og degradering-analyse
Analyser dekk-strategi, type og degradering gjennom løpet
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib.pyplot as plt
import numpy as np
from fastf1_app import F1RaceDataApp


def plot_tyre_strategy(app):
    """
    Viser dekk-strategi for alle sjåfører gjennom løpet
    """
    tyre_data = app.get_tyre_data()
    if tyre_data is None or tyre_data.empty:
        print("Ingen dekk-data tilgjengelig")
        return None

    fig, ax = plt.subplots(figsize=(16, 10))

    drivers = tyre_data["Driver"].unique()
    compounds = {"SOFT": "red", "MEDIUM": "yellow", "HARD": "cyan", "INTERMEDIATE": "green", "WET": "blue"}

    for idx, driver in enumerate(sorted(drivers)):
        driver_tyres = tyre_data[tyre_data["Driver"] == driver].sort_values("LapNumber")

        # Plott hver dekk-type
        for _, row in driver_tyres.iterrows():
            compound = row["Compound"]
            lap_num = row["LapNumber"]
            color = compounds.get(compound, "gray")
            ax.scatter(lap_num, idx, s=200, color=color, edgecolor="black", alpha=0.7)

    ax.set_xlabel("Rundenummer", fontsize=12)
    ax.set_ylabel("Sjåfør", fontsize=12)
    ax.set_yticks(range(len(sorted(drivers))))
    ax.set_yticklabels(sorted(drivers), fontsize=9)
    ax.set_title("Dekk-strategi gjennom løpet", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    # Legnd for dekk-type
    legend_elements = [plt.scatter([], [], s=100, color=color, edgecolor="black", label=compound)
                       for compound, color in compounds.items()]
    ax.legend(handles=legend_elements, loc="upper right")

    plt.tight_layout()
    return fig


def plot_tyre_degradation_comparison(app, drivers: list):
    """
    Sammenligner dekk-degradering mellom sjåfører
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    degradation_data = []
    driver_names = []

    for driver in drivers:
        deg = app.get_tyre_degradation(driver)
        if deg is not None and not deg.empty:
            for _, row in deg.iterrows():
                degradation_data.append({
                    "Driver": driver,
                    "Compound": row["Compound"],
                    "Degradation": row["Degradation"],
                    "Num_Laps": row["Num_Laps"],
                })
                driver_names.append(driver)

    if not degradation_data:
        print("Ingen degradering-data tilgjengelig")
        return None

    compounds = ["SOFT", "MEDIUM", "HARD"]
    x_pos = np.arange(len(drivers))
    width = 0.25

    for idx, compound in enumerate(compounds):
        values = []
        for driver in drivers:
            deg = app.get_tyre_degradation(driver)
            if deg is not None:
                comp_data = deg[deg["Compound"] == compound]
                if not comp_data.empty:
                    values.append(comp_data.iloc[0]["Degradation"])
                else:
                    values.append(0)
            else:
                values.append(0)
        ax.bar(x_pos + idx * width, values, width, label=compound)

    ax.set_xlabel("Sjåfør", fontsize=12)
    ax.set_ylabel("Degradering (sekunder)", fontsize=12)
    ax.set_title("Dekk-degradering sammenligning", fontsize=14, fontweight="bold")
    ax.set_xticks(x_pos + width)
    ax.set_xticklabels(drivers)
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    return fig


def plot_tyre_life_vs_laptime(app, driver: str):
    """
    Viser forholdet mellom dekk-levetid og rundetider
    """
    lap_data = app.get_lap_times_by_driver(driver)
    if lap_data is None or lap_data.empty:
        print(f"Ingen data for {driver}")
        return None

    fig, ax = plt.subplots(figsize=(14, 7))

    # Kun runder med valid dekk-levetid
    valid_data = lap_data[lap_data["TyreLife"].notna()].copy()
    if valid_data.empty:
        return None

    lap_times = valid_data["LapTime"].dt.total_seconds()
    tyre_life = valid_data["TyreLife"]

    scatter = ax.scatter(tyre_life, lap_times, s=50, alpha=0.6, c=tyre_life, cmap="RdYlGn_r")
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Dekk-levetid (runder)", fontsize=11)

    # Lineær trend
    z = np.polyfit(tyre_life, lap_times, 1)
    p = np.poly1d(z)
    ax.plot(tyre_life, p(tyre_life), "r--", linewidth=2, label="Trend")

    ax.set_xlabel("Dekk-levetid (runder)", fontsize=12)
    ax.set_ylabel("Rundetid (sekunder)", fontsize=12)
    ax.set_title(f"Dekk-levetid vs Rundetid - {driver}", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_compound_performance(app, driver: str):
    """
    Sammenligner ytelses-målingene for hver dekk-type
    """
    deg = app.get_tyre_degradation(driver)
    if deg is None or deg.empty:
        print(f"Ingen degradering-data for {driver}")
        return None

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    compounds = deg["Compound"].values
    avg_times = deg["Avg_Lap_Time"].values
    num_laps = deg["Num_Laps"].values

    # Gjennomsnittlige rundetider
    axes[0].bar(compounds, avg_times, color=["red", "yellow", "cyan", "green", "blue"])
    axes[0].set_ylabel("Gjennomsnittlig rundetid (sekunder)", fontsize=11)
    axes[0].set_title(f"Gjennomsnittlig rundetid per dekk - {driver}", fontsize=12)
    axes[0].grid(True, alpha=0.3, axis="y")

    # Antall runder per dekk
    axes[1].bar(compounds, num_laps, color=["red", "yellow", "cyan", "green", "blue"])
    axes[1].set_ylabel("Antall runder", fontsize=11)
    axes[1].set_title(f"Runder per dekk-type - {driver}", fontsize=12)
    axes[1].grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    return fig


def plot_fresh_vs_used_tyres(app, driver: str):
    """
    Sammenligner ytelses mellom nye og brukte dekk
    """
    lap_data = app.get_lap_times_by_driver(driver)
    if lap_data is None or lap_data.empty:
        return None

    # Separér nye og brukte dekk
    fresh_laps = lap_data[lap_data["FreshTyre"] == True]
    used_laps = lap_data[lap_data["FreshTyre"] == False]

    fig, ax = plt.subplots(figsize=(12, 6))

    if not fresh_laps.empty:
        fresh_times = fresh_laps["LapTime"].dt.total_seconds()
        ax.scatter(fresh_laps["LapNumber"], fresh_times, label="Nye dekk",
                  s=100, color="green", alpha=0.6, marker="o")

    if not used_laps.empty:
        used_times = used_laps["LapTime"].dt.total_seconds()
        ax.scatter(used_laps["LapNumber"], used_times, label="Brukte dekk",
                  s=100, color="red", alpha=0.6, marker="x")

    ax.set_xlabel("Rundenummer", fontsize=12)
    ax.set_ylabel("Rundetid (sekunder)", fontsize=12)
    ax.set_title(f"Nye vs Brukte dekk - {driver}", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def main():
    """Hovedfunksjon"""
    print("=" * 60)
    print("DEKKDATA-ANALYSE: Monza 2024")
    print("=" * 60)

    app = F1RaceDataApp()
    app.load_session(2024, "Monza", session_type="R")

    if app.current_session is None:
        print("Kunne ikke laste sesjon")
        return

    all_drivers = app.current_session.drivers[:5]

    # 1. Dekk-strategi for alle
    print("\n1. Lager dekk-strategi visualisering...")
    fig1 = plot_tyre_strategy(app)
    if fig1:
        fig1.savefig(
            Path(__file__).parent.parent / "output_tyre_strategy.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_tyre_strategy.png'")

    # 2. Degradering-sammenligning
    print(f"\n2. Lager degradering-sammenligning for {len(all_drivers)} sjåfører...")
    fig2 = plot_tyre_degradation_comparison(app, all_drivers)
    if fig2:
        fig2.savefig(
            Path(__file__).parent.parent / "output_tyre_degradation_comparison.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_tyre_degradation_comparison.png'")

    # 3. Dekk-levetid vs rundetider
    print(f"\n3. Lager dekk-levetid analyse for {all_drivers[0]}...")
    fig3 = plot_tyre_life_vs_laptime(app, all_drivers[0])
    if fig3:
        fig3.savefig(
            Path(__file__).parent.parent / "output_tyre_life_vs_laptime.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_tyre_life_vs_laptime.png'")

    # 4. Dekk-type ytelse
    print(f"\n4. Lager dekk-type ytelse-analyse for {all_drivers[0]}...")
    fig4 = plot_compound_performance(app, all_drivers[0])
    if fig4:
        fig4.savefig(
            Path(__file__).parent.parent / "output_compound_performance.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_compound_performance.png'")

    # 5. Nye vs brukte dekk
    print(f"\n5. Lager nye vs brukte dekk-analyse for {all_drivers[0]}...")
    fig5 = plot_fresh_vs_used_tyres(app, all_drivers[0])
    if fig5:
        fig5.savefig(
            Path(__file__).parent.parent / "output_fresh_vs_used_tyres.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_fresh_vs_used_tyres.png'")

    print("\n✓ Alle dekkdata-visualiseringer opprettet!")


if __name__ == "__main__":
    main()
