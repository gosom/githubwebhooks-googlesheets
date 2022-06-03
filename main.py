import logging
import requests
import hmac
import hashlib
import os

from ipaddress import ip_address, ip_network

import functions_framework

import spreadsheet

# WebHook must have application/json content-type

logging.basicConfig(level=logging.DEBUG)

@functions_framework.http
def github_pr_event(request):
    logging.info("received new github webhook")
    try:
        validate(request)
        data = request.get_json()
        if is_review_approved(data):
            cfg = spreadsheet.Config()
            writer = spreadsheet.SpreadSheetRowWriter(cfg)
            review_data = ReviewData(data)
            resp = writer.write(review_data.values)
            return resp, 200
        else:
            return {"speadsheet_updated": False}, 200
    except Exception as e:
        logging.error(str(e))
        return {"error": str(e)}, 500


class ReviewData:

    def __init__(self, data):
        self.approved_at = data["review"]["submitted_at"]
        self.author = data["pull_request"]["user"]["login"]
        self.reviewer = data["review"]["user"]["login"]
        self.title = data["pull_request"]["title"]
        self.repo = data["repository"]["name"]

    @property
    def values(self):
        return [self.approved_at, self.repo+"/"+self.title, self.author, self.reviewer]


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



