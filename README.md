### Introduction

This repository contains a Google Cloud Function that is listening
to Github actions webhooks. In particular in accepts Github events 
of type `pull_request_review` and if the Pull Request is accepted 
then it adds a row to a Google Sheet document.

### Usage

1. Create a spreadsheet on Google Sheets and find it's ID (from the url)
2. Share this with your service account's email (In GCP)
3. Setup the required environment variables
4. Setup your webhook in github. Make sure your select the proper event (`pull_request_reviews` on the UI)

Environment Variables:

```
WEBHOOK_SECRET="The value of the webhook secret"
SERVICE_ACCOUNT_FILE="the credentials.json" # ONLY for local development
SPREADSHEET_ID="the ID of the SpreadSheet"
RANGE_="A1:D1" # The cells that contain the data
EXTRACT="review->submitted_at,repository->name+pull_request->title,pull_request->user->login,review->user->login"
CONCAT_CHAR="/"
```

How to add `RANGE_`and `EXTRACT`

- `RANGE`: A1:D1 means that put the values below columns A1, B1, C1, D1 .
- `EXTRACT`: it extracts the defined keys from the json payload. When `+` CHAR is detected 
              it concats the left and right arguments using the `CONCAT_CHAR`


With the above config it will do:
```
1 A      B      C         D
2 Date   Title  Author    Reviewer 
```
It will create a new row (3) with data in
A3: `review->submitted_at`
B3: `repository->name/pull_request->title`
C3: `pull_request->user->login`
C4: `review->user->login`

So,

```
3 2022-06-03T20:21:59Z  githubwebhooks-googlesheets/updates README  gosom gosomdum`
```

You can hook the invocations of the webhooks and it's results on
`Repo->Settings->Webhooks->Recent Deliveries`

### Development Instructions

Use the following commands from the Makefile.

```
make deps
make local
make expose
```

Make sure the webhook's content-type is `application/json` (on github)

Tip: You can replay the webhooks, useful for testing/development (from github)


### Deployement to GCP Cloud functions

Make sure that you have enable Cloud Functions in your GCP. 

Additionally create an .env.yaml file with your settings.


```
make deploy
```

Once you deploy make sure that the cloud function is using the
`Runtime Service Account` that you gave access to Google Sheets.

Check that in the settings of your Function: 

Also make sure that you add the `url` of the cloud function in your
github webhook. You get this from the `httpsTrigger` section in the output
of `make deploy` or you can find it via the google UI.


