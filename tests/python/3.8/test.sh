#!/bin/bash
/entrypoint.sh

filename=./deployment.zip
minsize=508
filesize=$(stat -c%s $filename)
echo "Size of $filename = $filesize bytes."

if (( filesize > minsize )); then
    exit 0
else
    exit 1
fi
