.PHONY: all build install test

all:
	@echo "Possible Commands"
	@echo "\tbuild:    Builds SDK"
	@echo "\tinstall:  Installs via pip, needs to be built before installing"
	@echo "\ttest:     Only for development of SDK"

build:
	@python3 -m build

install:
	@python3 -m pip uninstall TheProtocols -y
	@cd dist; python3 -m pip install *.whl

test:
	@python3 test.py

clean:
	@rm -rfv dist
	@rm -rfv src/TheProtocols.egg-info
	@rm -rfv build
