#!/bin/bash

echo "Run flake8"
# FIXME: F821 should be remove in future (related issue https://github.com/PyCQA/pyflakes/pull/455/commits/b9267e139cb5ce0bfaa189c0ab7597afb9e90ec5#diff-8dd6768783dc8a438172318bc691ac3eR346-R353)
flake8 --ignore=E501,F821 interpretability_engine/ || exit 1
echo

flake8 --select=F401,E302 tests/ || exit 1
echo

echo "Run pylint"
pylint --rcfile=misc/pylintrc interpretability_engine/ || exit 1
echo
