# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

FROM golang:buster AS builder
LABEL maintainer dohyunk@cs.cmu.edu

RUN apt-get install -y git ca-certificates
COPY . /go/src/go.edusense.io/storage
WORKDIR /go/src/go.edusense.io/storage

RUN echo "replace go.edusense.io\storage v0.0.0 => /go/src/go.edusense.io/storage" >> go.mod
RUN CGO_ENABLED=0 GOOS=linux go build -a -o storage go.edusense.io/storage/apiserver

FROM debian:buster
# The following gosu setup procedure is derived from
# https://github.com/tianon/gosu/INSTALL.md.
RUN set -eux; \
  apt-get update; \
  apt-get install -y gosu; \
  rm -rf /var/lib/apt/lists/*; \
# verify that the binary works
  gosu nobody true
# end of gosu setup.

WORKDIR /app
COPY --from=builder /go/src/go.edusense.io/storage/storage storage
COPY ./entrypoint.sh .
RUN chmod +x ./entrypoint.sh ./storage

ENTRYPOINT ["/app/entrypoint.sh"]
