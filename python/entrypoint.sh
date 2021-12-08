#!/bin/sh
# This file remains for backwards compatibility.
set -ex
# Add poetry
python3 /entrypoint.py
pid=$!
wait $pid
