#!/bin/bash

pytest_debug="$1"
specific_test="$2"

python3 -m pytest -s \
--cov-config=misc/coveragerc --cov=interpretability_engine --cov-report=term-missing \
${pytest_debug} \
-p no:cacheprovider \
${specific_test}
