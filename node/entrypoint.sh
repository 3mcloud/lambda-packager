#!/bin/sh

# Naming things
CODE=${LAMBDA_CODE_DIR:-"src"}
ARTIFACT=${ARTIFACT_NAME:-"deployment.zip"}
BUILD_DIR=${CONTAINER_BUILD_DIRECTORY:-"/build"}
WORKSPACE=${CI_WORKSPACE:-$(pwd)}
# These really aren't overridable for an npm install, so not 
# giving the user a chance to modify it.
PKG_FILE="package.json"
PKG_LOCK="package-lock.json"

## Actually doing things
mkdir -p ${BUILD_DIR}/${CODE}
cp -R ${WORKSPACE}/${CODE}/. ${BUILD_DIR}/${CODE}
cp ${WORKSPACE}/${PKG_FILE} ${BUILD_DIR}
cp ${WORKSPACE}/${PKG_LOCK} ${BUILD_DIR}

cd ${BUILD_DIR}

if [[ -f "${PKG_FILE}" ]]; then
    npm install --production
else
    echo "No requirements found. Skipping install"
fi

zip -r9 ${WORKSPACE}/${ARTIFACT} . -x ${PKG_FILE} -x ${PKG_LOCK}
