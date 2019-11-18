#!/bin/bash
# First argument - date
# Second argument - event name
# Don't forget to place `print_events` binary in the same folder!
gzip -d -c /home/sites/alohalytics/alohalytics_messages-${1}.gz | ./print_events | grep "${2}"
