
all:

generate: generate-server generate-client generate-apidoc

generate-server:
	cp zerorobot/api/app.py /tmp
	go-raml server -l python --kind flask --dir zerorobot/api --ramlfile raml/api.raml --api-file-per-method
	cp /tmp/app.py zerorobot/api/app.py

generate-client:
	go-raml client -l python --kind requests --dir zerorobot/client --ramlfile raml/api.raml --python-unmarshall-response

generate-apidoc:
	if ! pip show pdoc > /dev/null; then pip install pdoc; fi
	pdoc --html  --html-dir docs/api --all-submodules --overwrite zerorobot

test:
	nose2 --with-coverage --coverage zerorobot

test-ui:
	nose2 --with-coverage --coverage-report html --coverage zerorobot
