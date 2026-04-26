#!/usr/bin/env sh
set -e

# shellcheck source=/dev/null
. /opt/venv/bin/activate

nfsn-ddns --cache --quiet "$@" \
    && rm -f /run/nfsn-ddns/unhealthy \
    || touch /run/nfsn-ddns/unhealthy
