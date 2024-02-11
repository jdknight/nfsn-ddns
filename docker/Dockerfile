# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

# type of image to build
# - local: builds using a local nfsn-ddns, already prepated (python -m build)
# - external: builds using pypi's available version of nfsn-ddns
ARG BUILD_MODE=external

# base image
FROM alpine:latest AS base

# default cron schedule to run this utility (once per hour)
ENV NFSN_DDNS_SCHEDULE="0 */1 * * *"

# prepare required python environment
RUN apk add --no-cache python3 py3-pip
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# build steps for processing a local build
FROM base AS build_local
RUN pip install build
COPY . /build
WORKDIR /build
RUN cd /build &&\
    python -m build &&\
    cp dist/*.whl / &&\
    rm -rf /build

# build steps for processing an external build
FROM base AS build_external
RUN pip download --dest / nfsn-ddns

FROM build_${BUILD_MODE}
RUN ls -al /

# final image
FROM build_${BUILD_MODE} AS final
RUN ls -al /
RUN pip install /*.whl && rm /*.whl && nfsn-ddns --version

# configure entrypoint and default command
ADD docker/docker-cmd.sh /run/docker-cmd.sh
ADD docker/docker-entrypoint.sh /run/docker-entrypoint.sh

ENTRYPOINT [ "/run/docker-entrypoint.sh" ]
CMD [ "/run/docker-cmd.sh" ]
