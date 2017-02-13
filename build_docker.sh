#!/usr/bin/env bash
rm -rf *.egg-info
rm -rf build
rm -rf dist
python setup.py bdist_wheel
docker build "$@"