### Usage

1. Create a spreadsheet on Google Sheets and find it's ID (from the url)
2. Share this with your service account's email (In GCP)
3. Setup the required environment variables

**TODO** complete me

You can hook the invocations of the webhooks and it's results on
`Repo->Settings->Webhooks->Recent Deliveries`

### Development Instructions

For local development follow the instructions below

```
pip install -r requirements.txt
```

`export $(cat .env | xargs)`

```
functions-framework --target github_pr_event --debug
```

Start `ngrok http 8000` and setup the url to the github webhook url

Make sure the webhook's content-type is `application/json` (on github)

Tip: You can replay the webhooks, useful for testing/development (from github)


### Deployement to GCP Cloud functions

**TODO**

