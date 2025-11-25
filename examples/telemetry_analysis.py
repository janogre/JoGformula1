"""
Eksempel: Telemetri-analyse
Viser hvordan å hente og analysere telemetri-data som hastighet og bremsing
"""

import sys
from pathlib import Path

# Legg til src-mappen til path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastf1_app import F1RaceDataApp


def main():
    """Hovedfunksjon"""
    app = F1RaceDataApp()

    # Laster Monza 2024 race
    print("=" * 60)
    print("TELEMETRI-ANALYSE: Monza 2024 Race")
    print("=" * 60)

    app.load_session(2024, "Monza", session_type="R")

    # Hent liste over sjåfører
    if app.current_session is not None:
        drivers = app.current_session.drivers
        print(f"\nTilgjengelige sjåfører ({len(drivers)}):")
        for driver in drivers[:5]:  # Vis første 5
            print(f"  - {driver}")

        # Hent telemetri for første sjåfør
        print(f"\n{'=' * 60}")
        print(f"Telemetri-data for {drivers[0]}")
        print(f"{'=' * 60}")

        telemetry = app.get_driver_telemetry(drivers[0])

        if telemetry is not None:
            print(f"\nTelemetri inneholder {len(telemetry)} data-punkter")
            print(f"\nTilgjengelige data-kolonner:")
            for col in telemetry.columns:
                print(f"  - {col}")

            # Vis statistikk
            print(f"\nHastighets-statistikk:")
            if "Speed" in telemetry.columns:
                speed_stats = telemetry["Speed"].describe()
                print(f"  Gjennomsnittlig: {speed_stats['mean']:.1f} km/h")
                print(f"  Maks: {speed_stats['max']:.1f} km/h")
                print(f"  Min: {speed_stats['min']:.1f} km/h")

            print(f"\nThrottle-statistikk:")
            if "Throttle" in telemetry.columns:
                throttle_stats = telemetry["Throttle"].describe()
                print(f"  Gjennomsnittlig: {throttle_stats['mean']:.1f}%")
                print(f"  Maks: {throttle_stats['max']:.1f}%")

            print(f"\nBremse-statistikk:")
            if "Brake" in telemetry.columns:
                brake_stats = telemetry["Brake"].describe()
                print(f"  Gjennomsnittlig: {brake_stats['mean']:.1f}%")
                print(f"  Maks: {brake_stats['max']:.1f}%")

            # Vis første 10 rader
            print(f"\nFørste 10 telemetri-data-punkter:")
            print(telemetry.head(10).to_string())
        else:
            print("Kunne ikke hente telemetri-data")


if __name__ == "__main__":
    main()
