.PHONY: default
default: help

# generate help info from comments: thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help: ## help information about make commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: deps
deps:  ## deps installs python dependencies
	pip install -r requirements.txt

.PHONY: local
local:  ## local starts the local development server
	#export $(cat .env | xargs) && 
	functions-framework --target github_pr_event --debug

.PHONY: expose
expose: ## expose exposes port 8080 via ngrok
	ngrok http 8000

