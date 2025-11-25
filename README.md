# JoG Formula 1 App

En Python-basert applikasjon for å vise Formula 1 race-data ved hjelp av FastF1 pakken.

## Funksjonalitet

- Henting av race-data fra sesjonger (treninger, kvalifisering, race)
- Telemetri-data (hastighet, bremsing, gass)
- Posisjonsdata gjennom løpet
- Dekkdata og pit stop-informasjon
- Visualiseringer av race-data

## Installasjon

```bash
pip install -r requirements.txt
```

## Bruk

Eksempler på hvordan bruke applikasjonen finnes i `examples/` mappen.

## Struktur

```
JoGformula1/
├── README.md
├── requirements.txt
├── src/
│   └── fastf1_app.py          # Hovedmodul for FastF1-integrasjon
├── examples/
│   ├── basic_session_data.py   # Hent grunnleggende sesjon-data
│   ├── telemetry_analysis.py   # Analyser telemetri-data
│   └── visualization.py        # Visualisering av data
└── data/
    └── cache/                  # Cache for API-kall
```

## Kilder

- [FastF1 Dokumentasjon](https://docs.fastf1.dev/)
- [FastF1 GitHub](https://github.com/theOehrly/Fast-F1)
