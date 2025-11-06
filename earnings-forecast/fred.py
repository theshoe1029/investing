import requests


def rf_rate() -> float:
    res = requests.get(
        "https://api.stlouisfed.org/fred/series/observations?series_id=SOFR&api_key=6316333ad7a8787ff6f03f114a35cbb3&file_type=json"
    )
    return float(res.json()["observations"][-1]["value"]) / 100
