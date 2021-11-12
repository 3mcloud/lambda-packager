#!/bin/sh
# This file remains for backeards compatiability.
set -ex
# Add poetry
export PATH="/root/.local/bin:$PATH"
python3 /entrypoint.py
wait
