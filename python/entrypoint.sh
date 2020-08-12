#!/bin/sh
set -ex

# To convert strings to booleans
function boolean() {
  case $1 in
    TRUE) echo true ;;
    FALSE) echo false ;;
    *) echo "Err: Unknown boolean value \"$1\"" 1>&2; exit 1 ;;
   esac
}


# Naming things
CODE=${LAMBDA_CODE_DIR:-"src"}
ARTIFACT=${ARTIFACT_NAME:-"deployment.zip"}
BUILD_DIR=${CONTAINER_BUILD_DIRECTORY:-"/build"}
WORKSPACE=${CI_WORKSPACE:-$(pwd)}
REQUIREMENTS_FILE=${REQUIREMENTS_FILE:-"requirements.txt"}
SETUP_FILE=${SETUP_FILE:-"setup.py"}
FAIL_IF_BIG=${FAIL_IF_BIG:=FALSE}
MAX_SIZE_INCLUSIVE=${MAX_SIZE:-50000000}

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

# echo ${MAX_SIZE_INCLUSIVE}
# if [[ -z "${MAX_SIZE_INCLUSIVE}" ]]; then
#     filesize=$(stat -c%s ${WORKSPACE}/${ARTIFACT})
    
#     if "$(boolean "${FAIL_IF_BIG}")" && $((filesize > MAX_SIZE_INCLUSIVE)); then
#         exit 1
#     else
#         exit 0
#     fi
# fi
