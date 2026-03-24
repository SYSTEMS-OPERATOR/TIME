# This is used with `make <option>` and is used for running various
# administration operations on the code.

TEST_GAME_DIR = .test_game_dir
TESTS ?= evennia

default:
	@echo " Usage: "
	@echo "  make install - install evennia (recommended to activate virtualenv first)"
	@echo "  make installextra - install evennia with extra-requirements (activate virtualenv first)"
	@echo "  make fmt/format - run the black autoformatter on the source code"
	@echo "  make lint - run black in --check mode"
	@echo "  make test - run evennia test suite with all default values."
	@echo "  make tests=evennia.path test - run only specific test or tests."
	@echo "  make testp - run test suite using multiple cores."
	@echo "  make smoke-template - run quick TIME-EVE template smoke tests + PEP 8 checks."
	@echo "  make release - publish evennia to pypi (requires pypi credentials)

install:
	pip install -e .

installextra:
	pip install -e .
	pip install -e .[extra]

# black is configured from pyproject.toml
format:
	black evennia
	isort --profile black .

fmt: format

lint:
	black --check $(BLACK_FORMAT_CONFIGS) evennia

test:
	evennia --init $(TEST_GAME_DIR);\
	cd $(TEST_GAME_DIR);\
	evennia migrate;\
	evennia test --keepdb $(TESTS);\

testp:
	evennia --init $(TEST_GAME_DIR);\
	cd $(TEST_GAME_DIR);\
	evennia migrate;\
	evennia test --keepdb --parallel 4 $(TESTS);\

smoke-template:
	python -m pip install --upgrade pip
	python -m pip install pycodestyle
	python -m unittest \
		evennia.game_template.tests.test_template_core \
		evennia.game_template.tests.test_timeline
	python -m pycodestyle \
		evennia/game_template/server/conf/at_server_startstop.py \
		evennia/game_template/server/conf/at_initial_setup.py \
		evennia/game_template/server/conf/server_services_plugins.py \
		evennia/game_template/server/conf/portal_services_plugins.py \
		evennia/game_template/server/conf/serversession.py \
		evennia/game_template/world/timeline.py \
		evennia/game_template/tests/test_template_core.py \
		evennia/game_template/tests/test_timeline.py

version:
	echo $(VERSION)

release:
	./.release.sh
