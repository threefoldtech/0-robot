
all: generate

generate: generate-server

generate-server:
	go-raml server -l python --kind flask --dir zerorobot/api --ramlfile raml/api.raml