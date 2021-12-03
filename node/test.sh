#!/bin/sh
LAMBDA_CODE_DIR=./tests/package ARTIFACT_NAME=package.zip /entrypoint.sh
pid=$!
wait $pid

filename=./package.zip
minsize=1000000
filesize=$(stat -c%s $filename)
echo "Size of $filename = $filesize bytes."

if (( filesize > minsize )); then
    exit 0
else
    exit 1
fi
