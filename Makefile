
all:

generate: generate-server generate-client

generate-server:
	go-raml server -l python --kind flask --dir zerorobot/api --ramlfile raml/api.raml --api-file-per-method

generate-client:
	go-raml client -l python --kind requests --dir zerorobot/client --ramlfile raml/api.raml --python-unmarshall-response

test:
	nose2 --with-coverage

test-ui:
	nose2 --with-coverage --coverage-report html
