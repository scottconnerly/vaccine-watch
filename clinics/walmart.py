import logging
import os
from datetime import datetime, timedelta

import requests

from . import Clinic

DATE_FORMAT = "%m%d%Y"


class WalMart(Clinic):
    def get_locations(self):
        url = "https://www.walmart.com/pharmacy/v2/storefinder/stores/f17a2469-c146-7206-e044-001517f43a86?searchString={}&serviceType=covid_immunizations&filterDistance=f17a2469-c146-7206-e044-001517f43a86".format(
            os.environ["WALMART_ZIP_CODE"]
        )
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()["data"]["storesData"]["stores"]
        else:
            logging.error(
                "Bad response from Wal-Mart: Code {}: {}",
                response.status_code,
                response.text,
            )
            clinics_with_vaccine = []
            clinics_without_vaccine = []


def get_appointment_info(location_id):
    url = "https://www.walmart.com/pharmacy/v2/clinical-services/time-slots/f17a2469-c146-7206-e044-001517f43a86"
    now = datetime.now()
    headers = {
        "cookie": "auth={};CID={};".format(
            os.environ["WALMART_AUTH_HEADER"], os.environ["WALMART_CID_HEADER"]
        )
    }
    payload = {
        "startDate": now.strftime(DATE_FORMAT),
        "endDate": (now + timedelta(days=6)).strftime(DATE_FORMAT),
        "imzStoreNumber": {
            "USStoreId": location_id,
        },
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        appointment_dates = [
            b["slotDate"] for b in a.json()["data"]["slotDays"] if len(b["slots"]) > 0
        ]
        print([timestamp_to_date(date) for date in appointment_dates])
    else:
        logging.error(
            "Bad response from Wal-Mart: Code {}: {}",
            response.status_code,
            response.text,
        )
        return []


def timestamp_to_date(timestamp):
    return datetime.strptime(timestamp, DATE_FORMAT)
