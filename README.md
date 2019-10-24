## Local deployment

Install the dependencies
    make install-deps


Deploy local server

    python app.py --host 0.0.0.0 --port 5000 --debug 1
or
    make dev-server

Run Unit Tests:
    make test

Clean Database to repopulate on App Startup
    make clean-db
