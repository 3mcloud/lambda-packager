#!/bin/sh
# This file remains for backeards compatiability.
set -ex
# Add poetry
export PATH="/drone/src/.poetry/bin:$PATH"
python3 /entrypoint.py
wait
