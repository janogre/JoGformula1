"""
Eksempel: Komplett telemetri-visualisering
Viser hastighet, gass-pedal, bremsing og motorsving-data
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from fastf1_app import F1RaceDataApp


def plot_telemetry_all_parameters(app, driver: str, lap_number: int = None):
    """
    Plotter alle telemetri-parametere: hastighet, gass, bremsing, motorsving
    """
    telemetry = app.get_driver_telemetry_full(driver, lap_number)
    if telemetry is None or telemetry.empty:
        print(f"Ingen telemetri-data for {driver}")
        return None

    fig, axes = plt.subplots(4, 1, figsize=(16, 12))

    distance = telemetry["Distance"].values if "Distance" in telemetry.columns else range(len(telemetry))

    # 1. Hastighet
    if "Speed" in telemetry.columns:
        speed = telemetry["Speed"]
        axes[0].fill_between(distance, speed, alpha=0.3, color="blue")
        axes[0].plot(distance, speed, linewidth=2, color="blue")
        axes[0].set_ylabel("Hastighet (km/h)", fontsize=11, fontweight="bold")
        axes[0].set_title(f"Telemetri for {driver} - Hastighet", fontsize=12)
        axes[0].grid(True, alpha=0.3)
        axes[0].set_ylim([0, max(speed) * 1.05])

    # 2. Gass-pedal (Throttle)
    if "Throttle" in telemetry.columns:
        throttle = telemetry["Throttle"] * 100  # Konverter til prosent
        axes[1].fill_between(distance, throttle, alpha=0.3, color="green")
        axes[1].plot(distance, throttle, linewidth=2, color="green")
        axes[1].set_ylabel("Gass-pedal (%)", fontsize=11, fontweight="bold")
        axes[1].set_title("Gass-pedal", fontsize=12)
        axes[1].set_ylim([0, 105])
        axes[1].grid(True, alpha=0.3)

    # 3. Bremsing
    if "Brake" in telemetry.columns:
        brake = telemetry["Brake"] * 100  # Konverter til prosent
        axes[2].fill_between(distance, brake, alpha=0.3, color="red")
        axes[2].plot(distance, brake, linewidth=2, color="red")
        axes[2].set_ylabel("Bremsing (%)", fontsize=11, fontweight="bold")
        axes[2].set_title("Bremsing", fontsize=12)
        axes[2].set_ylim([0, 105])
        axes[2].grid(True, alpha=0.3)

    # 4. Motorsving (Steering)
    if "Steering" in telemetry.columns:
        steering = telemetry["Steering"]
        axes[3].plot(distance, steering, linewidth=1.5, color="purple")
        axes[3].fill_between(distance, steering, alpha=0.3, color="purple")
        axes[3].set_ylabel("Motorsving (°)", fontsize=11, fontweight="bold")
        axes[3].set_xlabel("Distanse (m)", fontsize=11)
        axes[3].set_title("Motorsving", fontsize=12)
        axes[3].grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_telemetry_overlay(app, drivers: list):
    """
    Plotter hastighet overlaid for flere sjåfører for sammenligning
    """
    fig, ax = plt.subplots(figsize=(16, 7))

    colors = ["blue", "red", "green", "orange", "purple", "brown"]

    for idx, driver in enumerate(drivers):
        telemetry = app.get_driver_telemetry_full(driver)
        if telemetry is not None and not telemetry.empty:
            if "Speed" in telemetry.columns and "Distance" in telemetry.columns:
                distance = telemetry["Distance"]
                speed = telemetry["Speed"]
                color = colors[idx % len(colors)]
                ax.plot(distance, speed, linewidth=2, label=driver, color=color, alpha=0.8)

    ax.set_xlabel("Distanse (m)", fontsize=12)
    ax.set_ylabel("Hastighet (km/h)", fontsize=12)
    ax.set_title("Hastighets-sammenligning mellom sjåfører", fontsize=14, fontweight="bold")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_throttle_vs_brake(app, driver: str):
    """
    Plotter gass vs bremsing for å vise kjørestil
    """
    telemetry = app.get_driver_telemetry_full(driver)
    if telemetry is None or telemetry.empty:
        return None

    if "Throttle" not in telemetry.columns or "Brake" not in telemetry.columns:
        return None

    fig, ax = plt.subplots(figsize=(14, 7))

    distance = telemetry["Distance"].values if "Distance" in telemetry.columns else range(len(telemetry))
    throttle = telemetry["Throttle"].values * 100
    brake = telemetry["Brake"].values * 100

    ax.fill_between(distance, 0, throttle, label="Gass", alpha=0.6, color="green")
    ax.fill_between(distance, 0, -brake, label="Bremsing", alpha=0.6, color="red")
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)

    ax.set_xlabel("Distanse (m)", fontsize=12)
    ax.set_ylabel("Gass/Bremsing (%)", fontsize=12)
    ax.set_title(f"Kjørestil - Gass vs Bremsing ({driver})", fontsize=14, fontweight="bold")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_speed_distribution(app, drivers: list):
    """
    Viser hastighets-fordeling for sjåfører
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    for driver in drivers:
        telemetry = app.get_driver_telemetry_full(driver)
        if telemetry is not None and "Speed" in telemetry.columns:
            ax.hist(telemetry["Speed"], bins=30, alpha=0.5, label=driver)

    ax.set_xlabel("Hastighet (km/h)", fontsize=12)
    ax.set_ylabel("Antall data-punkter", fontsize=12)
    ax.set_title("Hastighets-fordeling", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    return fig


def main():
    """Hovedfunksjon"""
    print("=" * 60)
    print("TELEMETRI-VISUALISERING: Monza 2024")
    print("=" * 60)

    app = F1RaceDataApp()
    app.load_session(2024, "Monza", session_type="R")

    if app.current_session is None:
        print("Kunne ikke laste sesjon")
        return

    all_drivers = app.current_session.drivers[:5]

    # 1. Detaljert telemetri for første sjåfør
    print(f"\n1. Lager detaljert telemetri-graf for {all_drivers[0]}...")
    fig1 = plot_telemetry_all_parameters(app, all_drivers[0])
    if fig1:
        fig1.savefig(
            Path(__file__).parent.parent / "output_telemetry_all.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_telemetry_all.png'")

    # 2. Hastighets-sammenligning
    print(f"\n2. Lager hastighets-sammenligning for {len(all_drivers)} sjåfører...")
    fig2 = plot_telemetry_overlay(app, all_drivers)
    if fig2:
        fig2.savefig(
            Path(__file__).parent.parent / "output_telemetry_speed_overlay.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_telemetry_speed_overlay.png'")

    # 3. Gass vs Bremsing
    print(f"\n3. Lager gass vs bremsing-graf for {all_drivers[0]}...")
    fig3 = plot_throttle_vs_brake(app, all_drivers[0])
    if fig3:
        fig3.savefig(
            Path(__file__).parent.parent / "output_throttle_vs_brake.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_throttle_vs_brake.png'")

    # 4. Hastighets-fordeling
    print(f"\n4. Lager hastighets-fordeling...")
    fig4 = plot_speed_distribution(app, all_drivers)
    if fig4:
        fig4.savefig(
            Path(__file__).parent.parent / "output_speed_distribution.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_speed_distribution.png'")

    print("\n✓ Alle telemetri-visualiseringer opprettet!")


if __name__ == "__main__":
    main()
