#!/bin/bash
runsvdir /var/runit &
export GST_DEBUG=4
python3 main.py -p 5001
