#!/bin/bash

# clean up
rm htmlcov/*
rm .coverage

# no migrations coverage
PARMS=--include='*models*','*views*'

# run tests and collect coverage
coverage run --source=lfs,lfs_admin,lfs_forum manage.py test

# generate text and HTML reports
echo "----------------------------------------------------------"
echo "Coverage Results:"
coverage report $PARMS
coverage html $PARMS
echo "HTML generated in htmlcov/index.html"

