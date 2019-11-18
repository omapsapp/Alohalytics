#!/bin/bash
# First argument - date
# Second argument - event name
gzip -d -c /home/sites/alohalytics/alohalytics_messages-${1}.gz | ./print_events | grep "${2}"
