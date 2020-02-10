#!/bin/sh
LAMBDA_CODE_DIR=requirements ARTIFACT_NAME=requirements.zip /entrypoint.sh

filename=./requirements.zip
minsize=1000000
filesize=$(stat -c%s $filename)
echo "Size of $filename = $filesize bytes."

if (( filesize > minsize )); then
    exit 0
else
    exit 1
fi
