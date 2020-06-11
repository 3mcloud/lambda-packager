#!/bin/sh

# Naming things
# Assuming this is going to be the repository root
REPO_ROOT=$(pwd)
CODE=${LAMBDA_CODE_DIR:-"src"}
# Provides the ability for the src folder to still be nested.
# For copmatibility reasons this is left to blank, but if 
# you wanted the "src" directory to be retained you would
# set this to "src"
ARTIFACT_PREFIX=${ARTIFACT_CODE_PREFIX:-""}
ARTIFACT=${ARTIFACT_NAME:-"deployment.zip"}
BUILD_DIR=${CONTAINER_BUILD_DIRECTORY:-"/build"}
WORKSPACE=${CI_WORKSPACE:-$(pwd)}

# Allows package files in a different location to be copied to
# the build folder 
PKG_FILE=${NPM_PACKAGE_FILE:-${WORKSPACE}/${CODE}/"package.json"}
PKG_LOCK=${NPM_PACKAGE_LOCK:-${WORKSPACE}/${CODE}/"package-lock.json"}

## Actually doing things
mkdir -p ${BUILD_DIR}/${ARTIFACT_PREFIX}

cp -R ${WORKSPACE}/${CODE}/. ${BUILD_DIR}/${ARTIFACT_PREFIX}

cp ${PKG_FILE} ${BUILD_DIR}
cp ${PKG_LOCK} ${BUILD_DIR}

cd ${BUILD_DIR}

if [[ -f "$(basename ${PKG_FILE})" ]]; then
    npm install --production
else
    echo "No requirements found. Skipping install"
fi

# This matches the documentation
zip -r9 ${REPO_ROOT}/${ARTIFACT} . -x $(basename ${PKG_FILE}) -x $(basename ${PKG_LOCK})
