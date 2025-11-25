"""
Eksempel: Posisjonsdata-visualisering
Viser bil-posisjoner (X, Y koordinater) gjennom løpet på banen
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib.pyplot as plt
import numpy as np
from fastf1_app import F1RaceDataApp


def plot_track_positions_single_lap(app, driver: str, lap_number: int = None):
    """
    Plotter bil-posisjon på banen for en enkelt runde
    """
    telemetry = app.get_driver_telemetry_full(driver, lap_number)
    if telemetry is None or telemetry.empty:
        print(f"Ingen telemetri-data for {driver}")
        return None

    if "X" not in telemetry.columns or "Y" not in telemetry.columns:
        print(f"Ingen posisjons-data (X, Y) tilgjengelig")
        return None

    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot banen som en linje
    x = telemetry["X"]
    y = telemetry["Y"]

    # Fargelegg basert på hastighet
    if "Speed" in telemetry.columns:
        speed = telemetry["Speed"]
        scatter = ax.scatter(x, y, c=speed, cmap="RdYlGn", s=20, alpha=0.6)
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Hastighet (km/h)", fontsize=11)
    else:
        ax.plot(x, y, linewidth=2, color="blue", alpha=0.7)

    # Markér start- og sluttpunkt
    ax.plot(x.iloc[0], y.iloc[0], marker="o", markersize=15, color="green", label="Start", zorder=5)
    ax.plot(x.iloc[-1], y.iloc[-1], marker="s", markersize=15, color="red", label="Slutt", zorder=5)

    ax.set_xlabel("X-posisjon (m)", fontsize=12)
    ax.set_ylabel("Y-posisjon (m)", fontsize=12)
    ax.set_title(f"Bane-posisjon - {driver}", fontsize=14, fontweight="bold")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal")

    plt.tight_layout()
    return fig


def plot_track_comparison_multiple_drivers(app, drivers: list):
    """
    Sammenligner posisjoner på banen for flere sjåfører
    """
    fig, ax = plt.subplots(figsize=(14, 12))

    colors = ["red", "blue", "green", "orange", "purple", "brown", "pink", "gray"]

    for idx, driver in enumerate(drivers):
        telemetry = app.get_driver_telemetry_full(driver)
        if telemetry is not None and "X" in telemetry.columns and "Y" in telemetry.columns:
            x = telemetry["X"]
            y = telemetry["Y"]
            color = colors[idx % len(colors)]
            ax.plot(x, y, linewidth=1.5, label=driver, color=color, alpha=0.7)

    ax.set_xlabel("X-posisjon (m)", fontsize=12)
    ax.set_ylabel("Y-posisjon (m)", fontsize=12)
    ax.set_title("Bane-sammenligning mellom sjåfører", fontsize=14, fontweight="bold")
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal")

    plt.tight_layout()
    return fig


def plot_sector_times_visualization(app, driver: str):
    """
    Viser rundedeler (sectors) gjennom sesjonen
    """
    lap_data = app.get_lap_times_by_driver(driver)
    if lap_data is None or lap_data.empty:
        return None

    fig, ax = plt.subplots(figsize=(14, 7))

    # Hvis Sector data er tilgjengelig
    if "Sector1Time" in lap_data.columns:
        sector1 = lap_data["Sector1Time"].dt.total_seconds()
        sector2 = lap_data["Sector2Time"].dt.total_seconds()
        sector3 = lap_data["Sector3Time"].dt.total_seconds()

        x = lap_data["LapNumber"]
        width = 0.6

        ax.bar(x - width / 3, sector1, width / 3, label="Sektor 1", color="red", alpha=0.7)
        ax.bar(x, sector2, width / 3, label="Sektor 2", color="yellow", alpha=0.7)
        ax.bar(x + width / 3, sector3, width / 3, label="Sektor 3", color="green", alpha=0.7)

        ax.set_xlabel("Rundenummer", fontsize=12)
        ax.set_ylabel("Sektortid (sekunder)", fontsize=12)
        ax.set_title(f"Sektor-tider - {driver}", fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        return fig

    return None


def plot_position_on_track_heatmap(app, driver: str):
    """
    Viser hvor på banen sjåføren bruker mest tid (heatmap)
    """
    telemetry = app.get_driver_telemetry_full(driver)
    if telemetry is None or telemetry.empty:
        return None

    if "X" not in telemetry.columns or "Y" not in telemetry.columns:
        return None

    fig, ax = plt.subplots(figsize=(14, 10))

    x = telemetry["X"].values
    y = telemetry["Y"].values

    # Lag en 2D histogram (heatmap)
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=[50, 50])

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    im = ax.imshow(
        heatmap.T,
        extent=extent,
        origin="lower",
        cmap="hot",
        aspect="auto",
        interpolation="bilinear",
    )

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Tid brukt (data-punkter)", fontsize=11)

    ax.set_xlabel("X-posisjon (m)", fontsize=12)
    ax.set_ylabel("Y-posisjon (m)", fontsize=12)
    ax.set_title(f"Tidsbruk på banen - {driver}", fontsize=14, fontweight="bold")

    plt.tight_layout()
    return fig


def plot_speed_heatmap(app, driver: str):
    """
    Viser hastighets-heatmap på banen
    """
    telemetry = app.get_driver_telemetry_full(driver)
    if telemetry is None or telemetry.empty:
        return None

    if "X" not in telemetry.columns or "Y" not in telemetry.columns:
        return None

    if "Speed" not in telemetry.columns:
        return None

    fig, ax = plt.subplots(figsize=(14, 10))

    x = telemetry["X"].values
    y = telemetry["Y"].values
    speed = telemetry["Speed"].values

    scatter = ax.scatter(x, y, c=speed, cmap="viridis", s=10, alpha=0.6)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Hastighet (km/h)", fontsize=11)

    ax.set_xlabel("X-posisjon (m)", fontsize=12)
    ax.set_ylabel("Y-posisjon (m)", fontsize=12)
    ax.set_title(f"Hastighets-fordeling på banen - {driver}", fontsize=14, fontweight="bold")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def main():
    """Hovedfunksjon"""
    print("=" * 60)
    print("POSISJONSDATA-VISUALISERING: Monza 2024")
    print("=" * 60)

    app = F1RaceDataApp()
    app.load_session(2024, "Monza", session_type="R")

    if app.current_session is None:
        print("Kunne ikke laste sesjon")
        return

    all_drivers = app.current_session.drivers[:5]

    # 1. Bane-posisjon for første sjåfør
    print(f"\n1. Lager bane-posisjon visualisering for {all_drivers[0]}...")
    fig1 = plot_track_positions_single_lap(app, all_drivers[0])
    if fig1:
        fig1.savefig(
            Path(__file__).parent.parent / "output_track_position_single.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_track_position_single.png'")

    # 2. Sammenligning av flere sjåfører på banen
    print(f"\n2. Lager bane-sammenligning for {len(all_drivers)} sjåfører...")
    fig2 = plot_track_comparison_multiple_drivers(app, all_drivers)
    if fig2:
        fig2.savefig(
            Path(__file__).parent.parent / "output_track_comparison.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_track_comparison.png'")

    # 3. Hastighets-fordeling på banen
    print(f"\n3. Lager hastighets-heatmap for {all_drivers[0]}...")
    fig3 = plot_speed_heatmap(app, all_drivers[0])
    if fig3:
        fig3.savefig(
            Path(__file__).parent.parent / "output_speed_heatmap.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_speed_heatmap.png'")

    # 4. Tidsbruk på banen (heatmap)
    print(f"\n4. Lager tidsbruk-heatmap for {all_drivers[0]}...")
    fig4 = plot_position_on_track_heatmap(app, all_drivers[0])
    if fig4:
        fig4.savefig(
            Path(__file__).parent.parent / "output_time_heatmap.png",
            dpi=100,
            bbox_inches="tight",
        )
        print("   ✓ Lagret som 'output_time_heatmap.png'")

    print("\n✓ Alle posisjons-visualiseringer opprettet!")


if __name__ == "__main__":
    main()
