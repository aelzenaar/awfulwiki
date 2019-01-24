#!/bin/bash

# Escalate!
[ "$UID" -eq 0 ] || exec sudo "$0" "$@"

if [ -e thttpd.pid ]
then
  kill $(cat thttpd.pid)
  rm thttpd.pid
fi
