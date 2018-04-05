
all: test

generate: generate-server generate-apidoc

generate-server:
	go-raml server -l python --kind flask --dir zerorobot/server --ramlfile api_spec/main.raml --no-main
	raml2html -p api_spec/main.raml > api_spec/api.html

generate-apidoc:
	if ! pip show pdoc > /dev/null; then pip install pdoc; fi
	rm -r docs/api
	pdoc --html  --html-dir docs/api --all-submodules --overwrite zerorobot

package: source_pkg bin_pkg

source_pkg:
	python3 setup.py sdist

bin_pkg:
	python3 setup.py bdist_wheel

test: clean
	pytest --cov=./ tests -v

test-ui: clean
	pytest --cov=./ --cov-report=html tests -v

# usage: make release version=0.5.0 js=development
release:
	git checkout -b $(version)
	./utils/scripts/release.sh $(version) $(js)
	git tag -s v$(version) -m "Release v$(version)"
	git commit -a -m "release  v$(version)"
	git push origin $(version)
	git push origin v$(version)

clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf


.PHONY: all generate generate-server generate-apidoc package source_pkg bin_pkg test test-ui