#!/bin/sh

# Naming things
CODE=${LAMBDA_CODE_DIR:-"src"}
ARTIFACT=${ARTIFACT_NAME:-"deployment.zip"}
BUILD_DIR=${CONTAINER_BUILD_DIRECTORY:-"/build"}
WORKSPACE=${CI_WORKSPACE:-$(pwd)}
REQUIREMENTS_FILE=${REQUIREMENTS_FILE:-"requirements.txt"}


## Actually doing things
mkdir -p ${BUILD_DIR}
cp -R ${WORKSPACE}/${CODE}/. ${BUILD_DIR}
cd ${BUILD_DIR}
[ -e ${REQUIREMENTS_FILE} ] && pip install -r ${REQUIREMENTS_FILE} -t ./
chmod -R 755 .
zip -r9 ${WORKSPACE}/${ARTIFACT} . -x "*.pyc" -x ${REQUIREMENTS_FILE} -x "${ARTIFACT}"
