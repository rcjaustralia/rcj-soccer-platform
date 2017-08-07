#!/usr/bin/env bash
rm -rf *.egg-info
rm -rf build
rm -rf dist
python3.6 setup.py bdist_wheel
docker build "$@" .
