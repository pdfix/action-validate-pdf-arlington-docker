#!/bin/bash

# This is local docker test during build and push action.

# Colors for output into console
GREEN='\033[0;32m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print info messages
info() { echo -e "${PURPLE}$1${NC}"; }

# Function to print success messages
success() { echo -e "${GREEN}$1${NC}"; }

# Function to print error messages
error() { echo -e "${RED}ERROR: $1${NC}"; }

# init
pushd "$(dirname $0)" > /dev/null

EXIT_STATUS=0
DOCKER_IMAGE="validate-pdf-arlington:test"
PLATFORM="--platform linux/amd64"
TEMPORARY_DIRECTORY=".test"
OPENAI_API_KEY=$1

info "Building docker image..."
docker build $PLATFORM --rm -t $DOCKER_IMAGE .

if [ -d "$(pwd)/$TEMPORARY_DIRECTORY" ]; then
    rm -rf $(pwd)/$TEMPORARY_DIRECTORY
fi
mkdir -p $(pwd)/$TEMPORARY_DIRECTORY

info "List files in /usr/validation"
docker run --rm $PLATFORM -v $(pwd):/data -w /data --entrypoint ls $DOCKER_IMAGE /usr/validation/

info "Test #01: Show help"
docker run --rm $PLATFORM -v $(pwd):/data -w /data $DOCKER_IMAGE --help > /dev/null
if [ $? -eq 0 ]; then
    success "passed"
else
    error "Failed to run \"--help\" command"
    EXIT_STATUS=1
fi

info "Test #02: Extract config"
docker run --rm $PLATFORM -v $(pwd):/data -w /data $DOCKER_IMAGE config -o $TEMPORARY_DIRECTORY/config.json > /dev/null
if [ -f "$(pwd)/$TEMPORARY_DIRECTORY/config.json" ]; then
    success "passed"
else
    error "config.json not saved"
    EXIT_STATUS=1
fi

info "Test #03: Run validate pdf->html"
docker run --rm $PLATFORM -v $(pwd):/data -w /data $DOCKER_IMAGE validate --format html -i example/air_quality.pdf -o $TEMPORARY_DIRECTORY/air_quality.html > /dev/null
if [ -f "$(pwd)/$TEMPORARY_DIRECTORY/air_quality.html" ]; then
    success "passed"
else
    error "validate pdf->html failed on example/air_quality.pdf"
    EXIT_STATUS=1
fi

info "Test #04: Run validate pdf->xml"
docker run --rm $PLATFORM -v $(pwd):/data -w /data $DOCKER_IMAGE validate --format xml -i example/air_quality.pdf -o $TEMPORARY_DIRECTORY/air_quality.xml > /dev/null
if [ -f "$(pwd)/$TEMPORARY_DIRECTORY/air_quality.xml" ]; then
    success "passed"
else
    error "validate pdf->xml failed on example/air_quality.pdf"
    EXIT_STATUS=1

info "Cleaning up temporary files from tests"
rm -f $TEMPORARY_DIRECTORY/config.json
rm -f $TEMPORARY_DIRECTORY/air_quality.html
rm -f $TEMPORARY_DIRECTORY/air_quality.xml
rmdir $(pwd)/$TEMPORARY_DIRECTORY

info "Removing testing docker image"
docker rmi $DOCKER_IMAGE

popd > /dev/null

if [ $EXIT_STATUS -eq 1 ]; then
    error "One or more tests failed."
    exit 1
else
    success "All tests passed."
    exit 0
fi
