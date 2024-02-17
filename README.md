# NearlyFreeSpeech.net Dynamic DNS Utility

[![pip Version](https://badgen.net/pypi/v/nfsn-ddns?label=PyPI)](https://pypi.python.org/pypi/nfsn-ddns)
[![Supported Python versions](https://badgen.net/pypi/python/nfsn-ddns?label=Python)](https://pypi.python.org/pypi/nfsn-ddns)
[![Build Status](https://github.com/jdknight/nfsn-ddns/actions/workflows/build.yml/badge.svg)](https://github.com/jdknight/nfsn-ddns/actions/workflows/build.yml)
[![Docker Status](https://github.com/jdknight/nfsn-ddns/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/jdknight/nfsn-ddns/actions/workflows/docker-publish.yml)

## Overview

The following provides a utility to update a [NearlyFreeSpeech.NET][nfsn]
DNS record with a dynamic IP address. Invoking this utility will perform the
following:

- Selecting a random provider to query for a public IP of the running host.
- Query a NearlyFreeSpeech.NET domain for a configured IP on a `A` record.
- Compare the address, and update if they do not match.
- *(optional)* Cache the detected public address set on NearlyFreeSpeech.NET
   for a couple of days (configurable) to limit API requests.

## Requirements

* [Python][python] 3.8+
* [PyYAML][pyyaml]
* [Requests][requests] 2.30.0+

## Installation

This tool can be installed using [pip][pip]:

```shell
pip install nfsn-ddns
 (or)
python -m pip install nfsn-ddns
```

## Usage

This tool can be invoked from a command line using:

```shell
nfsn-ddns --help
 (or)
python -m nfsn-ddns --help
```

## Configuration

This utility can be configured using a file, command line arguments or
environment variables. An example configuration file (`config.yaml`) is
as follows:

```
nfsn-ddns:
  api-login: <api-login>
  api-token: <api-token>
  domains:
    - <domain>
  timeout: 10
```

A user can use a combination of ways to configure this utility. For example,
most options can be configured from the command line, but some options (such
as the API token) can be configured from an environment variable:

```
export NFSN_DDNS_API_TOKEN=myapitoken
nfsn-ddns --api-login myaccount --ddns-domain ddns.example.com
```

All available configuration options are listed as follows:

<table>
<tr><th colspan="2">Essential Options</th></tr>
<tr><td width="180">API Login</td><td>

The login/account of the NearlyFreeSpeech.NET user. This is used to
authenticate API requests.

- Command line option: `--api-login`
- Configuration key: `api-login` *(str)*
- Environment variable: `NFSN_DDNS_API_LOGIN`

</td></tr>
<tr><td>API Token</td><td>

The token to use when authenticating API requests. Members can acquire an
API token by viewing their profiles and selecting `Manage API Key`. In this
page, users can request to generate an API token.

- Command line option: `--api-token`
- Configuration key: `api-token` *(str)*
- Environment variable: `NFSN_DDNS_API_TOKEN`

</td></tr>
<tr><td>DDNS Domains</td><td>

The DNS resource to update, which includes the DNS record which to update
with a dynamically detected IP address, along with its domain. For example:

```
ddns.example.com
```

Multiple domains can be provided, for users who want a DDNS record across
multiple domains (although the use of CNAME's are recommended when attempting
to updated multiple records for a single domain).

- Command line option: `--ddns-domain`
- Configuration key: `domains` *(str-list)*
- Environment variable: `NFSN_DDNS_DOMAINS` *(;-separated)*

</td></tr>
<tr><th colspan="2">Additional Options</th></tr>
<tr><td>Cache</td><td>

Configure whether a detected public IP will be cached into a local file.
his feature can be used to avoid NFSN API calls if it is believed the
public IP of a host is believed to have not changed. After a successful
verification of a configured DNS record, the detected public IP can be
stored in a cache file for future considerations. Next time this utility
runs and detects a public IP address, if the address matches that of the
cached file, no API requests to NFSN will be made. The cache will be
considered a valid source of information for configured number of days
(see "Cache Days").

By default, this setting is not enabled (except in container environments).

- Command line option: `--cache`
- Configuration key: `cache` *(bool)*
- Environment variable: `NFSN_DDNS_CACHE`

</td></tr>
<tr><td>Cache Days</td><td>

When using the cache capability, this value configures the total number of
days before the cache is considered to be stale. A stale cache will cause
this utility to perform an API request with NFSN to verify the DNS record
matches.

By default, a cache is considered valid for seven (`7`) days.

- Command line option: `--cache-days`
- Configuration key: `cache-days` *(int)*
- Environment variable: `NFSN_DDNS_CACHE_DAYS`

</td></tr>
<tr><td>Cache File</td><td>

When using the cache capability, the specific file where cached content
is stored if set by this option.

By default, the cache file location used will be the first available path
that is writable by this utility:

```
/run/nfsn-ddns/cached-ip
 (or)
/run/user/(UID)/cached-ip
 (or)
nfsn-ddns-cached-ip
```

- Command line option: `--cache-file`
- Configuration key: `cache-file`
- Environment variable: `NFSN_DDNS_CACHE_FILE`

</td></tr>
<tr><td>IP API Endpoints</td><td>

IP API endpoints are web services used to help determine the public IP
address of the instance running this utility. The detected IP will be used
to update the configured DNS record.

The endpoint used is chosen at random each run. If a given endpoint cannot
be accessed, other endpoints are used until an IP address is provided or
all endpoints have been exhausted.

The default endpoints used are as follows:

- https://api.ipify.org
- https://checkip.amazonaws.com/
- https://ifconfig.me/ip
- https://ipinfo.io/ip
- https://trackip.net/ip

Users can override what endpoints to use by configuring this option.

- Configuration key: `myip-api-endpoints` *(str-list)*
- Environment variable: `NFSN_DDNS_MYIP_API_ENDPOINTS` *(;-separated)*

</td></tr>
<tr><td>Timeout</td><td>

Configures the timeout (in seconds) until any requests to external sources
(i.e. NFSN API or IP providers) are considered timed out. The default
timeout for all requests is configured to ten (`10`) seconds.

- Command line option: `--timeout`
- Configuration key: `timeout`
- Environment variable: `NFSN_DDNS_TIMEOUT`

</td></tr>
<tr><th colspan="2">Advanced Options</th></tr>
<tr><td>NFSN API Endpoint<img width=180/></td><td>

The API endpoint for NearlyFreeSpeech.NET. In almost all cases, this
option never needs to be changed. However, the option is provided if a
use case requires a different endpoint to be used.

This value is configured to `https://api.nearlyfreespeech.net/dns` by
default.

- Configuration key: `nfsn-api-endpoint` *(str)*
- Environment variable: `NFSN_DDNS_NFSN_API_ENDPOINT`

</td></tr>
</table>

## Docker

This project supports multiple ways to use this utility inside a Docker
environment. A recommended choice is to use a pre-built image available
from GitHub's container registry.

### Pre-built image

A pre-built image can be acquired using the following command:

```
docker pull ghcr.io/jdknight/nfsn-ddns
```

Prepare a configuration environment for this container by creating a
file `/etc/nfsn-ddns` with the contents defined in [env.default][env-config]
(users can use any path or filename they desire, as long as the following
`docker run` command points to this file). Adjust these options to the
configuration desired.

The container than can be run using the following command:

```
docker run --name nfsn-ddns --detach --restart unless-stopped \
    --env-file /etc/nfsn-ddns ghcr.io/jdknight/nfsn-ddns
```

### Self-built image

Users who wish to manage their own image can do so with the Docker
definitions found inside this repository. This can be done by cloning
this repository on the host wanting to run the container. A Docker
build can be run on the

```
docker build -t ghcr.io/jdknight/nfsn-ddns --detach -f docker/Dockerfile .
```

Then running the same `docker run` call mentioned above.

### Self-managed Docker Compose

Users can also take advantage of the Docker compose definition. First, copy
the environment template (`env.default`) to `.nfsn-ddns.env`, followed by
editing required options.

```
cp env.default .nfsn-ddns.env
```

Next, load up the container using `docker compose`:

```
docker compose build
docker compose up --detach
```

Both Docker build calls will by default load a container with the
PyPI version of nfsn-ddns. Users wanting to use the local implementation
in their container can do so by performing a Docker build with the
`--build-arg local` argument.

For example:

```
docker compose build --build-arg BUILD_MODE=local
docker compose up --detach
```


[env-config]: https://github.com/jdknight/nfsn-ddns/blob/main/docker/env.default
[nfsn]: https://www.nearlyfreespeech.net/
[pip]: https://pip.pypa.io/
[python]: https://www.python.org/
[pyyaml]: https://pyyaml.org/
[requests]: https://requests.readthedocs.io/
