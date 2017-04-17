#!/bin/bash
set -o allexport

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

if [ -e .env ]; then
	source .env
fi
echo $OMARTESTPY_DOCKER_IMAGE_LOCAL

docker build -t $OMARTESTPY_DOCKER_IMAGE_LOCAL:$OMARTESTPY_IMAGE_VERSION . 
