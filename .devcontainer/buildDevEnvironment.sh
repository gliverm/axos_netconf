#! /bin/bash
pipenv install --dev
pipenv run pre-commit install
pipenv run pre-commit autoupdate