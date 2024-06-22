# TrueNAS SCALE Instructions

The following includes community-provided instructions to help users
configure a [TrueNAS SCALE][truenas-scale] instance to use this utility.
Instructions may vary over time and rely on the community to provide any
updates for this use case as it is not actively tested on.

## Setup

### NFSN API Key

Login to [NearlyFreeSpeech.net][nfsn-login] and generate an API key. Inside
the member's interface:

1. Venture to the "Profile" tab.
2. Select "Actions".
3. Select "Manage API Key".

### Preparing a TrueNAS Scale Dataset

In TrueNAS Scale, register a new dataset for this utility by performing the
following:

1. Venture to the "Datasets" page.
2. Select "Add Dataset".
3. Create a new dataset named `NFSN_DDNS_CONFIG`.

### Adding this utility as a custom application

In TrueNAS Scale, add a new custom application for this utility by performing
the following:

1. Venture to the page "Apps > Discover Apps > Custom App".
2. Configure the following options for the new application:

   - Application Name: `nfsn-ddns`
   - Image Repository: `ghcr.io/jdknight/nfsn-ddns`
   - Environment Variables:
     - `NFSN_DDNS_API_LOGIN`: `example_username`
     - `NFSN_DDNS_API_TOKEN`: `example_token`
     - `NFSN_DDNS_DOMAINS`: `ddns.example.com`
     - `NFSN_DDNS_CACHE`: `1`
     - `NFSN_DDNS_CACHE_FILE`: `/var/nfsn-ddns/cached-ip`
   - Storage: Add Host/Mount
     - Host Path: `/mnt/Pool/NFSN_DDNS_CONFIG`
     - Mount Path: `/var/nfsn-ddns`

## Testing

After configuration, perform the following to test/verify the setup:

- Check the application's logs by ensure that there are no errors reported
  and an IP was sent to NearlyFreeSpeech.net.
- Check the application's shell by invoking the following command:

  ```
  cat /var/nfsn-ddns/cached-ip
  ```
  
  The output should report the instance's public IP cached in the file.
- Log in to NearlyFreeSpeech.net and pull up the domain's DNS information.
  Ensure that the expected DDNS address (e.g. `ddns.example.com`) was
  added/updated.
- When verifying access to services on the host using the new DDNS hostname,
  ensure that any used ports configured in any firewall (e.g. port forwarding),
  verify they work with the new URL.


[nfsn-login]: https://members.nearlyfreespeech.net/login/
[truenas-scale]: https://www.truenas.com/truenas-scale/
