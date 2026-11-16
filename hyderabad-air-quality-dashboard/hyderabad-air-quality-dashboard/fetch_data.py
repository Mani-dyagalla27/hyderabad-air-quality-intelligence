"""Download real daily OpenAQ measurements around Hyderabad into the dashboard CSV."""
from datetime import date, timedelta
from pathlib import Path
import getpass, time, sys
import requests
import pandas as pd

BASE = "https://api.openaq.org/v3"
CENTER = "17.3850,78.4867"
RADIUS = 25000
OUT = Path(__file__).parent / "data" / "hyderabad_air_quality.csv"
START = date(2024, 1, 1)
END = date.today() - timedelta(days=1)
SESSION = requests.Session()

def get_json(path, params, key):
    response = SESSION.get(BASE + path, params=params,
                           headers={"X-API-Key": key}, timeout=45)
    if response.status_code == 429:
        time.sleep(3)
        response = SESSION.get(BASE + path, params=params,
                               headers={"X-API-Key": key}, timeout=45)
    response.raise_for_status()
    return response.json()

def get_day(item):
    # OpenAQ v3 daily records expose the interval start in period.datetimeFrom.
    period = item.get("period") or {}
    dt = (period.get("datetimeFrom") or {}).get("local")
    if not dt:
        dt = (period.get("datetimeFrom") or {}).get("utc")
    if not dt:
        dt = (item.get("datetime") or {}).get("local") or (item.get("datetime") or {}).get("utc")
    return dt

def main():
    key = getpass.getpass("OpenAQ API key (input hidden): ").strip()
    if not key:
        print("An OpenAQ API key is required. Get one from https://openaq.org/")
        sys.exit(1)

    print("Finding monitoring locations within 25 km of Hyderabad...")
    payload = get_json("/locations", {"coordinates": CENTER, "radius": RADIUS,
                                      "limit": 100, "page": 1}, key)
    locations = payload.get("results", [])
    if not locations:
        print("No locations returned. Check the API key or try again later.")
        sys.exit(2)

    rows = []
    for loc in locations:
        loc_id = loc.get("id")
        loc_name = loc.get("name", f"Location {loc_id}")
        coords = loc.get("coordinates") or {}
        sensors = loc.get("sensors") or []
        print(f"Station: {loc_name} | sensors: {len(sensors)}")
        for sensor in sensors:
            sensor_id = sensor.get("id")
            parameter = (sensor.get("parameter") or {}).get("name", "unknown")
            unit = (sensor.get("parameter") or {}).get("units", "")
            if not sensor_id:
                continue
            page = 1
            while True:
                try:
                    data = get_json(f"/sensors/{sensor_id}/days",
                                    {"date_from": START.isoformat(),
                                     "date_to": END.isoformat(),
                                     "limit": 1000, "page": page}, key)
                except requests.HTTPError as exc:
                    print(f"  Skipping sensor {sensor_id} ({parameter}): {exc}")
                    break
                results = data.get("results", [])
                if not results:
                    break
                for item in results:
                    dt = get_day(item)
                    if not dt:
                        continue
                    rows.append({
                        "date": dt,
                        "city": "Hyderabad",
                        "location": loc_name,
                        "location_id": loc_id,
                        "sensor_id": sensor_id,
                        "parameter": parameter.lower(),
                        "value": item.get("value"),
                        "unit": unit,
                        "latitude": coords.get("latitude"),
                        "longitude": coords.get("longitude"),
                        "provider": (loc.get("provider") or {}).get("name", ""),
                        "owner": (loc.get("owner") or {}).get("name", ""),
                    })
                if len(results) < 1000:
                    break
                page += 1
                time.sleep(0.15)
            time.sleep(0.12)

    if not rows:
        print("No daily readings were returned for this period. Try a different date window.")
        sys.exit(3)
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"])
    df = df.drop_duplicates(subset=["date", "sensor_id", "value"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"\nSaved {len(df):,} real daily measurements from {df['location'].nunique()} stations.")
    print(f"Date coverage: {df['date'].min()} to {df['date'].max()}")
    print(f"File: {OUT}")
    print("Note: these are pollutant concentrations, not AQI scores.")

if __name__ == "__main__":
    main()
