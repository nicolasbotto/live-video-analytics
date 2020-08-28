#!/bin/bash
runsvdir /var/runit &
source $INTEL_OPENVINO_DIR/bin/setupvars.sh
python3 main.py -p 5001
