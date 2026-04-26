#!/usr/bin/env sh
set -e

# apply a default scheduler (run once per hour) if none is provided
if [ -z "$NFSN_DDNS_SCHEDULE" ]; then
    NFSN_DDNS_SCHEDULE="0 */1 * * *"
fi

# schedule the task in cron
echo "configuring nfsn-ddns schedule in cron: $NFSN_DDNS_SCHEDULE"

echo "SHELL=/bin/bash" | crontab -
cmd="/run/nfsn-ddns-job.sh $NFSN_DDNS_EXTRA_ARGS"
cron_entry="$NFSN_DDNS_SCHEDULE $cmd >/proc/1/fd/1 2>&1"
echo "$cron_entry" | crontab -

exec "$@"
