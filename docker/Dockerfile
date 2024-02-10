# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

# type of image to build
# - local: builds using a local nfsn-ddns, already prepated (python -m build)
# - external: builds using pypi's available version of nfsn-ddns
ARG BUILD_MODE=external

# base image
FROM alpine:latest as base

# default cron schedule to run this utility (once per hour)
ENV NFSN_DDNS_SCHEDULE="0 */1 * * *"

# prepare required python environment
RUN apk add --no-cache python3 py3-pip
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# build steps for processing a local build
FROM base as build_local
ONBUILD COPY dist/*.whl /
ONBUILD RUN pip install /*.whl && rm /*.whl

# build steps for processing an external build
FROM base as build_external
ONBUILD RUN pip install nfsn-ddns

# final image
FROM build_${BUILD_MODE}
RUN source /opt/venv/bin/activate && nfsn-ddns --version

# configure entrypoint and default command
ADD docker/docker-cmd.sh /run/docker-cmd.sh
ADD docker/docker-entrypoint.sh /run/docker-entrypoint.sh

ENTRYPOINT [ "/run/docker-entrypoint.sh" ]
CMD [ "/run/docker-cmd.sh" ]
