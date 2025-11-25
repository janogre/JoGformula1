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
    ):
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
            "Session Type": session.name,
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

    def get_lap_times_by_driver(self, driver: str) -> Optional[pd.DataFrame]:
        """
        Henter detaljerte rundetider for en spesifikk sjåfør

        Args:
            driver: Sjåførens navn eller 3-bokstav-kode

        Returns:
            DataFrame med rundetider
        """
        if self.current_session is None:
            print("Ingen sesjon lastet")
            return None

        try:
            driver_laps = self.current_session.laps.pick_driver(driver)
            return driver_laps[
                ["LapNumber", "LapTime", "Compound", "FreshTyre", "TyreLife"]
            ].sort_values("LapNumber")
        except Exception as e:
            print(f"Feil ved henting av rundetider: {e}")
            return None

    def get_driver_telemetry_full(
        self, driver: str, lap_number: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """
        Henter komplett telemetri-data for en sjåfør (hastighet, gass, bremsing, motorsving)

        Args:
            driver: Sjåførens navn eller 3-bokstav-kode
            lap_number: Spesifikk rundnummer (hvis None, henter raskeste runde)

        Returns:
            DataFrame med telemetri-data
        """
        if self.current_session is None:
            print("Ingen sesjon lastet")
            return None

        try:
            driver_laps = self.current_session.laps.pick_driver(driver)

            if lap_number is not None:
                lap = driver_laps[driver_laps["LapNumber"] == lap_number].iloc[0]
            else:
                lap = driver_laps.pick_fastest()

            telemetry = lap.get_telemetry()
            # Konverter til km/h hvis nødvendig
            if "Speed" in telemetry.columns:
                telemetry["Speed_kmh"] = telemetry["Speed"]

            return telemetry
        except Exception as e:
            print(f"Feil ved henting av telemetri: {e}")
            return None

    def get_position_data(self, driver: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Henter posisjonsdata (X, Y koordinater) for en sjåfør gjennom løpet

        Args:
            driver: Sjåførens navn eller 3-bokstav-kode (hvis None, henter alle)

        Returns:
            DataFrame med posisjonsdata
        """
        if self.current_session is None:
            print("Ingen sesjon lastet")
            return None

        try:
            if driver is not None:
                driver_laps = self.current_session.laps.pick_driver(driver)
                positions = []
                for _, lap in driver_laps.iterrows():
                    try:
                        telemetry = lap.get_telemetry()
                        if "X" in telemetry.columns and "Y" in telemetry.columns:
                            positions.append(
                                {
                                    "Driver": driver,
                                    "LapNumber": lap["LapNumber"],
                                    "X": telemetry["X"],
                                    "Y": telemetry["Y"],
                                }
                            )
                    except:
                        pass
                return pd.DataFrame(positions)
            else:
                # Hent for alle sjåfører
                all_positions = []
                for driver in self.current_session.drivers:
                    pos = self.get_position_data(driver)
                    if pos is not None:
                        all_positions.append(pos)
                return pd.concat(all_positions, ignore_index=True)
        except Exception as e:
            print(f"Feil ved henting av posisjonsdata: {e}")
            return None

    def get_tyre_data(self) -> Optional[pd.DataFrame]:
        """
        Henter dekkdata (type og levetid) for alle sjåfører

        Returns:
            DataFrame med dekk-informasjon
        """
        if self.current_session is None:
            print("Ingen sesjon lastet")
            return None

        try:
            laps = self.current_session.laps
            tyre_info = laps[
                ["Driver", "LapNumber", "Compound", "FreshTyre", "TyreLife"]
            ].drop_duplicates()

            # Sorter etter sjåfør og rundnummer
            return tyre_info.sort_values(["Driver", "LapNumber"])
        except Exception as e:
            print(f"Feil ved henting av dekkdata: {e}")
            return None

    def get_tyre_degradation(self, driver: str) -> Optional[pd.DataFrame]:
        """
        Analyserer dekkdegradeing for en sjåfør

        Args:
            driver: Sjåførens navn eller 3-bokstav-kode

        Returns:
            DataFrame med degradering per dekk-set
        """
        if self.current_session is None:
            print("Ingen sesjon lastet")
            return None

        try:
            driver_laps = self.current_session.laps.pick_driver(driver)

            # Grupper etter dekk-type
            degradation = []
            for compound in driver_laps["Compound"].unique():
                compound_laps = driver_laps[driver_laps["Compound"] == compound].sort_values(
                    "LapNumber"
                )
                if len(compound_laps) > 0:
                    lap_times = compound_laps["LapTime"].dt.total_seconds()
                    degradation.append(
                        {
                            "Driver": driver,
                            "Compound": compound,
                            "Num_Laps": len(compound_laps),
                            "First_Lap_Time": lap_times.iloc[0],
                            "Last_Lap_Time": lap_times.iloc[-1],
                            "Degradation": lap_times.iloc[-1] - lap_times.iloc[0],
                            "Avg_Lap_Time": lap_times.mean(),
                        }
                    )
            return pd.DataFrame(degradation)
        except Exception as e:
            print(f"Feil ved analyse av dekkdegradeing: {e}")
            return None

    def compare_drivers_lap_times(self, drivers: List[str]) -> Optional[pd.DataFrame]:
        """
        Sammenligner rundetider mellom flere sjåfører

        Args:
            drivers: Liste med sjåfører å sammenligne

        Returns:
            DataFrame med sammenlignbare data
        """
        if self.current_session is None:
            print("Ingen sesjon lastet")
            return None

        try:
            comparison = []
            for driver in drivers:
                driver_laps = self.current_session.laps.pick_driver(driver)
                if len(driver_laps) > 0:
                    fastest = driver_laps.pick_fastest()
                    avg_lap_time = (
                        driver_laps[driver_laps["IsAccurate"] == True]["LapTime"]
                        .dt.total_seconds()
                        .mean()
                    )
                    comparison.append(
                        {
                            "Driver": driver,
                            "Fastest_Lap": fastest["LapTime"],
                            "Avg_Lap_Time": pd.Timedelta(seconds=avg_lap_time),
                            "Total_Laps": len(driver_laps),
                            "DNF": driver_laps["Status"].iloc[-1] != "Finished",
                        }
                    )
            return pd.DataFrame(comparison)
        except Exception as e:
            print(f"Feil ved sammenligning av rundetider: {e}")
            return None

    def get_lap_progression(self, driver: str) -> Optional[pd.DataFrame]:
        """
        Henter rundeprogresjonen for en sjåfør gjennom løpet

        Args:
            driver: Sjåførens navn eller 3-bokstav-kode

        Returns:
            DataFrame med rundeprogresjon
        """
        if self.current_session is None:
            print("Ingen sesjon lastet")
            return None

        try:
            driver_laps = self.current_session.laps.pick_driver(driver).sort_values("LapNumber")
            return driver_laps[
                [
                    "LapNumber",
                    "LapTime",
                    "Compound",
                    "FreshTyre",
                    "TyreLife",
                    "PitInTime",
                    "PitOutTime",
                ]
            ]
        except Exception as e:
            print(f"Feil ved henting av rundeprogresjonen: {e}")
            return None
