#!/bin/bash
runsvdir /var/runit &
export GST_DEBUG=4
# Copy nvidia pyds module
cp /opt/nvidia/deepstream/deepstream-5.0/lib/pyds.so /app
cp /opt/nvidia/deepstream/deepstream-5.0/lib/setup.py /app
python3 setup.py
python3 main.py -p 5001