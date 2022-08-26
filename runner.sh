#!/bin/bash

docker run -v $(pwd)/output:/usr/src/app/output license_tracker $@
