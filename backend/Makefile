project := grow-prod

develop:
	pip install -t lib -r requirements.txt

deploy:
	gcloud app deploy \
	  -q \
		--promote \
	  --project=$(project) \
	  app.yaml

run:
	dev_appserver.py \
		app.yaml
