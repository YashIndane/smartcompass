#!/usr/bin/python3

# For API register here -> https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml?useFullSite=true#declination
# For Manual checking   -> https://www.magnetic-declination.com/

# Computes the magnetic declination angle

from __future__ import annotations

import requests
import os

from typing import Dict

def compute_declination_angle(
    *,
    lat: float,
    long: float,
    key: str,
    model: str = "WMM",
) -> Dict:
    """Computes the declination angle for a given latitude and longtitude value.

    :param lat: Latitude value in `degrees`, ranging from -90.0 to +90.0 (type float).
    :param long: Longitude value in `degrees`, ranging from -180.0 to +180 (type float).
    :param key: API key (type str),
    :param model: The model to use, Choose from `WMM`, `WMMHR` & `IGRF` (type str).
    :return: Declination angle in degrees (type float).
    """

    BASE_URL = "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination?"

    api_response: requests.models.Response = requests.get(
        BASE_URL,
        params={
            "lat1": lat, "lon1": long, "key": key, "model": model, "resultFormat": "json"
        },
    )

    stat_code: int = api_response.status_code

    if stat_code == 200:
        declination_angle: float = api_response.json().get('result')[0]['declination']
        return {"status": "succes", "code": stat_code, "declination_angle": declination_angle}
    else:
        return {"status": "error", "code": stat_code}
