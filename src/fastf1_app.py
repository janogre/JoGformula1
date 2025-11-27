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

    def get_driver_abbreviations(self) -> List[str]:
        """
        Henter liste over føreres forkortelser (f.eks. VER, LEC, ALO)

        Returns:
            Sortert liste med føreres 3-bokstav-koder
        """
        if self.current_session is None:
            return []

        try:
            # Hent unike driver-forkortelser fra laps-datasettet
            laps = self.current_session.laps
            if laps is None or laps.empty:
                return []

            # "Driver" kolonnen inneholder forkortelsene (VER, LEC, ALO, etc.)
            drivers = sorted(laps["Driver"].unique().tolist())
            # Filter ut None-verdier
            drivers = [d for d in drivers if d and isinstance(d, str)]
            return sorted(drivers)
        except Exception as e:
            print(f"Feil ved henting av føreres forkortelser: {e}")
            return []

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

        try:
            driver_laps = self.current_session.laps.pick_drivers(driver)
            if driver_laps is None or driver_laps.empty:
                return None

            lap = driver_laps.pick_fastest()
            if lap is None:
                return None

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
            # Velg tilgjengelige kolonner
            cols = [col for col in ["Abbreviation", "TeamName", "Position", "Status", "Points"]
                    if col in results.columns]
            return results[cols].sort_values("Position")
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
            if fastest_lap is None:
                return None

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
            driver_laps = self.current_session.laps.pick_drivers(driver)
            if driver_laps is None or driver_laps.empty:
                return None
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
            driver_laps = self.current_session.laps.pick_drivers(driver)

            if driver_laps is None or driver_laps.empty:
                return None

            if lap_number is not None:
                lap_rows = driver_laps[driver_laps["LapNumber"] == lap_number]
                if lap_rows.empty:
                    return None
                lap = lap_rows.iloc[0]
            else:
                lap = driver_laps.pick_fastest()

            if lap is None:
                return None

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
                driver_laps = self.current_session.laps.pick_drivers(driver)
                if driver_laps is None or driver_laps.empty:
                    return None

                positions = []
                for _, lap in driver_laps.iterrows():
                    try:
                        telemetry = lap.get_telemetry()
                        if telemetry is not None and "X" in telemetry.columns and "Y" in telemetry.columns:
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
                return pd.DataFrame(positions) if positions else None
            else:
                # Hent for alle sjåfører
                all_positions = []
                for driver in self.current_session.drivers:
                    pos = self.get_position_data(driver)
                    if pos is not None:
                        all_positions.append(pos)
                return pd.concat(all_positions, ignore_index=True) if all_positions else None
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
            driver_laps = self.current_session.laps.pick_drivers(driver)
            if driver_laps is None or driver_laps.empty:
                return None

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
            return pd.DataFrame(degradation) if degradation else None
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
                driver_laps = self.current_session.laps.pick_drivers(driver)
                if driver_laps is None or len(driver_laps) == 0:
                    continue
                fastest = driver_laps.pick_fastest()
                if fastest is None:
                    continue

                try:
                    avg_lap_time = (
                        driver_laps[driver_laps["IsAccurate"] == True]["LapTime"]
                        .dt.total_seconds()
                        .mean()
                    )
                except:
                    avg_lap_time = (
                        driver_laps["LapTime"]
                        .dt.total_seconds()
                        .mean()
                    )

                # Sjekk for Status kolonne
                dnf = False
                if "Status" in driver_laps.columns:
                    dnf = driver_laps["Status"].iloc[-1] != "Finished"

                comparison.append(
                    {
                        "Driver": driver,
                        "Fastest_Lap": fastest["LapTime"],
                        "Avg_Lap_Time": pd.Timedelta(seconds=avg_lap_time),
                        "Total_Laps": len(driver_laps),
                        "DNF": dnf,
                    }
                )
            return pd.DataFrame(comparison) if comparison else None
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
            driver_laps = self.current_session.laps.pick_drivers(driver).sort_values("LapNumber")
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

    def head_to_head_lap_comparison(self, driver1: str, driver2: str) -> Optional[pd.DataFrame]:
        """
        Sammenligner lap-by-lap tider for 2 førere

        Args:
            driver1: Første sjåfør (3-bokstav-kode)
            driver2: Annen sjåfør (3-bokstav-kode)

        Returns:
            DataFrame med sammenlignbar data for begge førere
        """
        if self.current_session is None:
            return None

        try:
            laps1 = self.current_session.laps.pick_drivers(driver1)
            laps2 = self.current_session.laps.pick_drivers(driver2)

            if laps1 is None or laps1.empty or laps2 is None or laps2.empty:
                return None

            # Hent lap numbers og tider
            comp_data = []
            max_laps = max(laps1["LapNumber"].max(), laps2["LapNumber"].max())

            for lap_num in range(1, int(max_laps) + 1):
                row = {"LapNumber": lap_num}

                # Driver 1
                lap1 = laps1[laps1["LapNumber"] == lap_num]
                if not lap1.empty:
                    row[f"{driver1}_Time"] = lap1["LapTime"].iloc[0]
                    row[f"{driver1}_Compound"] = lap1["Compound"].iloc[0]
                else:
                    row[f"{driver1}_Time"] = None
                    row[f"{driver1}_Compound"] = None

                # Driver 2
                lap2 = laps2[laps2["LapNumber"] == lap_num]
                if not lap2.empty:
                    row[f"{driver2}_Time"] = lap2["LapTime"].iloc[0]
                    row[f"{driver2}_Compound"] = lap2["Compound"].iloc[0]
                else:
                    row[f"{driver2}_Time"] = None
                    row[f"{driver2}_Compound"] = None

                comp_data.append(row)

            df = pd.DataFrame(comp_data)

            # Beregn gap (i sekunder)
            df[f"Gap ({driver1} vs {driver2})"] = (
                df[f"{driver2}_Time"].dt.total_seconds() -
                df[f"{driver1}_Time"].dt.total_seconds()
            )

            return df
        except Exception as e:
            print(f"Feil ved head-to-head sammenligning: {e}")
            return None

    def get_gap_to_driver(self, driver1: str, driver2: str) -> Optional[pd.DataFrame]:
        """
        Beregner gjennomsnittlig gap mellom 2 førere over løpet

        Args:
            driver1: Første sjåfør
            driver2: Annen sjåfør

        Returns:
            DataFrame med gap-statistikk
        """
        if self.current_session is None:
            return None

        try:
            comparison = self.head_to_head_lap_comparison(driver1, driver2)
            if comparison is None or comparison.empty:
                return None

            gap_col = f"Gap ({driver1} vs {driver2})"

            # Fjern NaN-verdier
            valid_gaps = comparison[gap_col].dropna()

            if valid_gaps.empty:
                return None

            return pd.DataFrame({
                "Metric": [
                    "Average Gap",
                    "Max Gap (favors " + driver2 + ")",
                    "Min Gap (favors " + driver1 + ")",
                    "Std Dev",
                ],
                "Value": [
                    f"{valid_gaps.mean():.3f}s",
                    f"{valid_gaps.max():.3f}s",
                    f"{valid_gaps.min():.3f}s",
                    f"{valid_gaps.std():.3f}s",
                ],
            })
        except Exception as e:
            print(f"Feil ved gap-beregning: {e}")
            return None

    def head_to_head_telemetry(self, driver1: str, driver2: str, lap_number: Optional[int] = None) -> Optional[dict]:
        """
        Henter telemetri for 2 førere på samme lap for sammenligning

        Args:
            driver1: Første sjåfør
            driver2: Annen sjåfør
            lap_number: Spesifikk lap (hvis None, brukes raskeste lap for hver)

        Returns:
            Dictionary med telemetri for begge førere
        """
        if self.current_session is None:
            return None

        try:
            laps1 = self.current_session.laps.pick_drivers(driver1)
            laps2 = self.current_session.laps.pick_drivers(driver2)

            if laps1 is None or laps1.empty or laps2 is None or laps2.empty:
                return None

            result = {}

            # Get telemetry for driver1
            if lap_number is not None:
                lap1_rows = laps1[laps1["LapNumber"] == lap_number]
                if not lap1_rows.empty:
                    lap1 = lap1_rows.iloc[0]
                else:
                    lap1 = laps1.pick_fastest()
            else:
                lap1 = laps1.pick_fastest()

            if lap1 is not None:
                result[driver1] = lap1.get_telemetry()
            else:
                result[driver1] = None

            # Get telemetry for driver2
            if lap_number is not None:
                lap2_rows = laps2[laps2["LapNumber"] == lap_number]
                if not lap2_rows.empty:
                    lap2 = lap2_rows.iloc[0]
                else:
                    lap2 = laps2.pick_fastest()
            else:
                lap2 = laps2.pick_fastest()

            if lap2 is not None:
                result[driver2] = lap2.get_telemetry()
            else:
                result[driver2] = None

            return result if result.get(driver1) is not None or result.get(driver2) is not None else None
        except Exception as e:
            print(f"Feil ved henting av head-to-head telemetri: {e}")
            return None
