#!/usr/bin/env sh
set -e

# on start, always run nfsn-ddns
# shellcheck source=/dev/null
. /opt/venv/bin/activate
nfsn-ddns --cache $NFSN_DDNS_EXTRA_ARGS

# start cron to schedule invokes of nfsn-ddns
exec /usr/sbin/crond -f -L 2
