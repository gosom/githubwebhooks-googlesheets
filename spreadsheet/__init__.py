import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

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
        print(value_range_body)
        request = self.service.spreadsheets().values().append(
            spreadsheetId=self.config.spreadsheet_id,
            range=self.config.range_,
            valueInputOption=self.value_input_option,
            insertDataOption=self.insert_data_option,
            body=value_range_body)
        response = request.execute()
        return response


