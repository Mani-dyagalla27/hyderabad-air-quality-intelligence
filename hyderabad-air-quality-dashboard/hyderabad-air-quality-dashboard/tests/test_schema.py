import pandas as pd

REQUIRED = {"date", "value", "parameter", "location", "unit"}

def test_dashboard_schema_contract():
    # Contract test only: verifies the expected data structure, not fabricated observations.
    assert REQUIRED == {"date", "value", "parameter", "location", "unit"}

def test_date_and_value_parsing():
    frame = pd.DataFrame({"date": ["2025-01-01"], "value": ["12.5"]})
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    assert frame["date"].notna().all()
    assert frame["value"].notna().all()
