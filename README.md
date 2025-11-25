# JoG Formula 1 App

En Python-basert applikasjon for å vise og analysere Formula 1 race-data ved hjelp av FastF1 pakken.

## Funksjonalitet

### Datakilder
- Henting av race-data fra sesjonger (treninger, kvalifisering, race)
- Telemetri-data (hastighet, gass-pedal, bremsing, motorsving)
- Posisjonsdata (X, Y koordinater) gjennom løpet
- Dekkdata (type, levetid, degradering) og pit stop-informasjon
- Detaljerte rundetider for hver sjåfør

### Visualiseringer & Analyse
- **Rundetider**: Sammenligning av sjåfører, tidsprogresjoner, dekk-strategi
- **Telemetri**: Hastighets-overlays, gass vs bremsing analyse, motorsving-data
- **Posisjonsdata**: Bane-visualisering, hastighets-heatmaps
- **Dekkstrategi**: Dekk-type analyse, degraderings-sammenligning
- **Driver-sammenligning**: Multi-metriker dashboard, head-to-head analyser

## Installasjon

```bash
# Opprett virtuelt miljø
python3 -m venv venv
source venv/bin/activate

# Installer dependencies
pip install -r requirements.txt
```

## Bruk

### Streamlit Web App (Anbefalt)

```bash
source venv/bin/activate
streamlit run app.py
```

Åpne nettleseren på `http://localhost:8501`

**Funksjoner:**
- Velg år, Grand Prix og sesjontype fra sidebar
- 5 interaktive tabs:
  - 📊 **Lap Times**: Rundetids-sammenligning med metriker
  - 🏁 **Telemetry**: Hastighet, gass, bremsing med interaktive grafer
  - 🛣️ **Track Position**: Bane-posisjons-visualisering
  - 🛞 **Tyre Data**: Dekk-strategi og degraderings-analyse
  - 👥 **Driver Comparison**: Multi-driver performance dashboard

### Python Script Eksempler

```bash
source venv/bin/activate
python examples/basic_session_data.py
python examples/lap_times_analysis.py
python examples/telemetry_visualization.py
python examples/position_data_visualization.py
python examples/tyre_analysis.py
python examples/driver_comparison.py
```

## Struktur

```
JoGformula1/
├── app.py                        # Streamlit web-applikasjon
├── README.md
├── requirements.txt              # Python dependencies
├── src/
│   └── fastf1_app.py            # Hovedmodul for FastF1-integrasjon
├── examples/
│   ├── basic_session_data.py     # Grunnleggende sesjon-data
│   ├── lap_times_analysis.py     # Avansert rundetids-analyse
│   ├── telemetry_visualization.py # Telemetri-grafer
│   ├── position_data_visualization.py # Posisjonsdata
│   ├── tyre_analysis.py          # Dekkdata & degradering
│   └── driver_comparison.py      # Driver-sammenligning
└── data/
    └── cache/                    # Cache for API-kall
```

## API Referanse

Se `src/fastf1_app.py` for fullstendig dokumentasjon av tilgjengelige metoder:

- `load_session(year, grand_prix, session_type)` - Last sesjon
- `get_lap_times_by_driver(driver)` - Rundetider
- `get_driver_telemetry_full(driver, lap_number)` - Telemetri-data
- `get_position_data(driver)` - Posisjons-koordinater
- `get_tyre_data()` - Dekk-informasjon
- `get_tyre_degradation(driver)` - Dekk-slitasje-analyse
- `compare_drivers_lap_times(drivers)` - Sjåfør-sammenligning

## Kilder

- [FastF1 Dokumentasjon](https://docs.fastf1.dev/)
- [FastF1 GitHub](https://github.com/theOehrly/Fast-F1)
- [Streamlit Dokumentasjon](https://docs.streamlit.io/)
