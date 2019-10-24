clean-db:
	rm db-dump/app.db

dev-server:
	python app.py --debug 1

install-deps:
	pip install -r requirements.txt

test:
	python tests.py