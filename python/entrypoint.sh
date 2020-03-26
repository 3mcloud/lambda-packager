#!/bin/sh
set -ex

# Naming things
CODE=${LAMBDA_CODE_DIR:-"src"}
ARTIFACT=${ARTIFACT_NAME:-"deployment.zip"}
BUILD_DIR=${CONTAINER_BUILD_DIRECTORY:-"/build"}
WORKSPACE=${CI_WORKSPACE:-$(pwd)}
REQUIREMENTS_FILE=${REQUIREMENTS_FILE:-"requirements.txt"}
SETUP_FILE=${SETUP_FILE:-"setup.py"}

## Actually doing things
mkdir -p ${BUILD_DIR}
cp -R ${WORKSPACE}/${CODE}/. ${BUILD_DIR}
cd ${BUILD_DIR}
if [ -a ${SETUP_FILE} ]; then
    pip install -t ./ . 2>&1
elif [ -e ${REQUIREMENTS_FILE} ]; then
    pip install -r ${REQUIREMENTS_FILE} -t ./ 2>&1
else
    echo "No requirements found. Skipping install"
fi
chmod -R 755 .
zip -r9 ${WORKSPACE}/${ARTIFACT} . -x "*.pyc" -x ${REQUIREMENTS_FILE} -x "${ARTIFACT}"
