import logging
import requests
import hmac
import hashlib
import os

from ipaddress import ip_address, ip_network

import functions_framework

from google.oauth2 import service_account
from googleapiclient.discovery import build


# WebHook must have application/json content-type

logging.basicConfig(level=logging.DEBUG)

@functions_framework.http
def github_pr_event(request):
    logging.info("received new github webhook")
    try:
        validate(request)
        data = request.get_json()
        if is_review_approved(data):
            cfg = Config()
            writer = SpreadSheetRowWriter(cfg)
            review_data = ReviewData(data)
            resp = writer.write(review_data.values)
            return resp, 200
        else:
            return {"speadsheet_updated": False}, 200
    except Exception as e:
        logging.error(str(e))
        return {"error": str(e)}, 500

class Config:

    def __init__(self):
        self.service_account_file = os.getenv("SERVICE_ACCOUNT_FILE", None)
        self.spreadsheet_id = os.environ["SPREADSHEET_ID"]
        self.range_ = os.environ["RANGE_"]

class SpreadSheetRowWriter:

    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, config):
        self.config = config
        if self.config.service_account_file:
            credentials = service_account.Credentials.from_service_account_file(
                    self.config.service_account_file
                    )
        else:
            credentials = None
        self.service = build("sheets", "v4", credentials=credentials)
        self.value_input_option = 'USER_ENTERED'
        self.insert_data_option = 'INSERT_ROWS'

    def write(self, values):
        value_range_body = {
                "range": self.config.range_,
                "majorDimension": "ROWS",
                "values": [values],
        }
        request = self.service.spreadsheets().values().append(
            spreadsheetId=self.config.spreadsheet_id,
            range=self.config.range_,
            valueInputOption=self.value_input_option,
            insertDataOption=self.insert_data_option,
            body=value_range_body)
        response = request.execute()
        return response


class ReviewData:

    def __init__(self, data):
        self.comma_sep_fields = os.environ["EXTRACT"]
        self.concat_char = os.environ.get("CONCAT_CHAR", "/")
        self.data = data

    @property
    def values(self):
        fields = [f.split("+") for f in self.comma_sep_fields.split(",")]
        values = []
        for l in fields:
            val = []
            for el in l:
                val.append(str(self.__extract(el)))
            values.append(self.concat_char.join(val))
        return values

    def __extract(self, field):
        current = self.data
        keys = list(reversed(field.split("->")))
        while keys:
            key = keys.pop()
            current = current[key]
        return current


class InvalidIPError(Exception):
    pass

class InvalidSignatureError(Exception):
    pass

class InvalidEventError(Exception):
    pass

def validate(request):
    # Commented these since I don't want to deal with github's rate limits
    """
    valid, sender_ip = is_ip_valid(request)
    if not valid:
        raise InvalidIPError(f'IP {sender_ip} is invalid')
    """
    if not is_signature_valid(request):
        raise InvalidSignatureError("Signature is invalid")
    if not is_event_accepted(request):
        ev = request.headers.get("X-GitHub-Event")
        raise InvalidEventError(f"{ev} is not accepted")


def is_ip_valid(request):
    sender_ip = ip_address(f'{request.access_route[0]}')
    resp = requests.get('https://api.github.com/meta')
    for ip in resp.json()['hooks']:
        if sender_ip in ip_network(ip):
            return True, sender_ip
    return False, sender_ip


def is_signature_valid(request):
    logging.debug("checking signature")

    expected_signature = hmac.new(
        key=bytes(os.environ["WEBHOOK_SECRET"], "utf-8"),
        msg=request.data,
        digestmod=hashlib.sha256
    ).hexdigest()

    _, incoming_signature = request.headers.get("X-Hub-Signature-256", "").split("=")
    return hmac.compare_digest(incoming_signature, expected_signature)


def is_event_accepted(request):
    valid_events = {"pull_request_review": True}
    ev = request.headers.get("X-GitHub-Event")
    return ev in valid_events


def is_review_approved(data):
    return data["review"]["state"] == "approved"



