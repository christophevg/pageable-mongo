tag:
	git tag ${TAG} -m "${MSG}"
	git push --tags

.python-version:
	@pyenv virtualenv $$(basename ${CURDIR}) > /dev/null 2>&1 || true
	@pyenv local $$(basename ${CURDIR})
	@pyenv version

requirements: .python-version requirements.txt
	@pip install --upgrade -r requirements.txt > /dev/null

upgrade: requirements
	@pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

dist: requirements
	rm -rf $@
	python setup.py sdist bdist_wheel

publish-test: dist
	twine upload --repository testpypi dist/*

publish: dist
	twine upload dist/*

PROJECT:=`find . -name '__init__.py' -maxdepth 2 | xargs dirname`

lint:
	@pylint ${PROJECT}

clean:
	find . | grep '\.backup' | xargs rm

.PHONY: dist docs
