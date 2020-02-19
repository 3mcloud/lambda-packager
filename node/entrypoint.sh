#!/bin/sh

# Naming things
CODE=${LAMBDA_CODE_DIR:-"src"}
ARTIFACT=${ARTIFACT_NAME:-"deployment.zip"}
BUILD_DIR=${CONTAINER_BUILD_DIRECTORY:-"/build"}
WORKSPACE=${CI_WORKSPACE:-$(pwd)}

## Actually doing things
mkdir -p ${BUILD_DIR}
cp -R ${WORKSPACE}/${CODE}/. ${BUILD_DIR}
cd ${BUILD_DIR}
if [ -e "package.json" ]; then
    npm install
else
    echo "No requirements found. Skipping install"
fi
chmod -R 755 .
zip -r9 ${WORKSPACE}/${ARTIFACT} . -x ${REQUIREMENTS_FILE} -x "${ARTIFACT}"

