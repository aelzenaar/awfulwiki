#!/bin/bash

# Escalate!
[ "$UID" -eq 0 ] || exec sudo "$0" "$@"

./kill.sh

export CVSROOT="$PWD/cvsroot"

exec /usr/local/sbin/thttpd -dd "$PWD/wiki/" -c '**.cgi' -l "$PWD/thttpd.log" -i "$PWD/thttpd.pid"

