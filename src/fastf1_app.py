"""
FastF1 Formula 1 Race Data App
Hovedmodul for å hente og analyse F1-data
"""

import fastf1
import pandas as pd
from typing import Optional, Dict, List
from pathlib import Path

# Sett cache-sti for FastF1
CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))


class F1RaceDataApp:
    """Hovedklasse for håndtering av F1 race-data"""

    def __init__(self):
        """Initialiserer appen"""
        self.current_session = None
        self.session_data = None

    def load_session(
        self, year: int, grand_prix: str, session_type: str = "R"
    ) -> Optional[fastf1.Session]:
        """
        Laster en F1-sesjon

        Args:
            year: Året for løpet (f.eks. 2024)
            grand_prix: Navn på Grand Prix eller løpsnummer (f.eks. "Monza", "Italian")
            session_type: Type sesjon - "FP1", "FP2", "FP3", "Q" (Qualifying), "R" (Race)

        Returns:
            Session-objekt eller None hvis feil
        """
        try:
            print(f"Laster sesjon: {year} {grand_prix} ({session_type})...")
            session = fastf1.get_session(year, grand_prix, session_type)
            session.load()
            self.current_session = session
            print(f"Sesjon lastet: {session.event['EventName']}")
            return session
        except Exception as e:
            print(f"Feil ved lasting av sesjon: {e}")
            return None

    def get_lap_data(self) -> Optional[pd.DataFrame]:
        """
        Henter run-data fra den nåværende sesjonen

        Returns:
            DataFrame med run-data
        """
        if self.current_session is None:
            print("Ingen sesjon lastet")
            return None

        return self.current_session.laps

    def get_driver_telemetry(self, driver: str) -> Optional[pd.DataFrame]:
        """
        Henter telemetri-data for en spesifikk sjåfør

        Args:
            driver: Sjåførens navn eller 3-bokstav-kode (f.eks. "VER", "Verstappen")

        Returns:
            DataFrame med telemetri-data
        """
        if self.current_session is None:
            print("Ingen sesjon lastet")
            return None

        # Finn sjåfør i sesjonen
        drivers = self.current_session.drivers
        print(f"Tilgjengelige sjåfører: {drivers}")

        try:
            lap = self.current_session.laps.pick_driver(driver).pick_fastest()
            telemetry = lap.get_telemetry()
            return telemetry
        except Exception as e:
            print(f"Feil ved henting av telemetri: {e}")
            return None

    def get_driver_standings(self) -> Optional[pd.DataFrame]:
        """
        Henter stillingsstatus etter sesjonen

        Returns:
            DataFrame med stillingsstatus
        """
        if self.current_session is None:
            print("Ingen sesjon lastet")
            return None

        try:
            results = self.current_session.results
            return results[
                ["Driver", "TeamName", "Position", "Status", "Points"]
            ].sort_values("Position")
        except Exception as e:
            print(f"Feil ved henting av stillingsstatus: {e}")
            return None

    def get_session_info(self) -> Optional[Dict]:
        """
        Henter generell informasjon om sesjonen

        Returns:
            Dictionary med sesjon-informasjon
        """
        if self.current_session is None:
            print("Ingen sesjon lastet")
            return None

        session = self.current_session
        return {
            "Event": session.event["EventName"],
            "Location": session.event["Location"],
            "Country": session.event["Country"],
            "Date": session.date,
            "Session Type": session.session_type,
            "Weather": {
                "Track Temp": session.track_status,
                "Air Temp": session.weather,
            },
        }

    def get_fastest_lap_data(self) -> Optional[Dict]:
        """
        Henter data om den raskeste runden

        Returns:
            Dictionary med info om raskeste runden
        """
        if self.current_session is None:
            print("Ingen sesjon lastet")
            return None

        try:
            fastest_lap = self.current_session.laps.pick_fastest()
            return {
                "Driver": fastest_lap["Driver"],
                "Time": fastest_lap["LapTime"],
                "Lap Number": fastest_lap["LapNumber"],
                "Compound": fastest_lap["Compound"],
            }
        except Exception as e:
            print(f"Feil ved henting av raskeste runde: {e}")
            return None

    def list_available_events(self, year: int) -> Optional[pd.DataFrame]:
        """
        Lister alle tilgjengelige løp i et år

        Args:
            year: Året (f.eks. 2024)

        Returns:
            DataFrame med oversikt over løp
        """
        try:
            schedule = fastf1.get_event_schedule(year)
            return schedule[["RoundNumber", "EventName", "Location", "Country", "EventDate"]]
        except Exception as e:
            print(f"Feil ved henting av løpsplan: {e}")
            return None
