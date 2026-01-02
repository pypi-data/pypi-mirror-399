#!/usr/bin/env bash

set -ex

rm -r dist

hatch build

twine upload dist/*
