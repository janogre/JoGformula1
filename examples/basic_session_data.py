"""
Eksempel: Grunnleggende sesjon-data
Viser hvordan å hente og vise basale data fra en F1-sesjon
"""

import sys
from pathlib import Path

# Legg til src-mappen til path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastf1_app import F1RaceDataApp


def main():
    """Hovedfunksjon"""
    app = F1RaceDataApp()

    # Eksempel 1: Laster 2024 Monza race
    print("=" * 60)
    print("EKSEMPEL 1: Laste sesjon og vise grunnleggende info")
    print("=" * 60)
    app.load_session(2024, "Monza", session_type="R")

    # Vis sesjon-informasjon
    session_info = app.get_session_info()
    if session_info:
        print("\nSesjon-informasjon:")
        for key, value in session_info.items():
            print(f"  {key}: {value}")

    # Vis raskeste runde
    print("\n" + "=" * 60)
    fastest_lap = app.get_fastest_lap_data()
    if fastest_lap:
        print("Raskeste runde:")
        for key, value in fastest_lap.items():
            print(f"  {key}: {value}")

    # Vis sluttresultat (top 10)
    print("\n" + "=" * 60)
    print("Sluttresultat (Top 10):")
    print("=" * 60)
    standings = app.get_driver_standings()
    if standings is not None:
        print(standings.head(10).to_string(index=False))

    # Vis alle tilgjengelige løp i 2024
    print("\n" + "=" * 60)
    print("EKSEMPEL 2: Alle løp i 2024 (første 5)")
    print("=" * 60)
    schedule = app.list_available_events(2024)
    if schedule is not None:
        print(schedule.head(5).to_string(index=False))

    # Eksempel 3: Analyse av run-data
    print("\n" + "=" * 60)
    print("EKSEMPEL 3: Run-data statistikk")
    print("=" * 60)
    laps = app.get_lap_data()
    if laps is not None:
        print(f"Totalt antall runder: {len(laps)}")
        print(f"Antall sjåfører: {laps['Driver'].nunique()}")
        print(f"Dekk-typer brukt: {laps['Compound'].unique()}")
        print("\nRunder per sjåfør:")
        driver_laps = laps.groupby("Driver").size().sort_values(ascending=False)
        print(driver_laps.head(10).to_string())


if __name__ == "__main__":
    main()
