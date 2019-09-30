FROM golang:alpine AS builder
LABEL maintainer dohyunk@cs.cmu.edu

RUN apk add --no-cache git ca-certificates
COPY . /go/src/go.edusense.io/storage
WORKDIR /go/src/go.edusense.io/storage

RUN echo "replace go.edusense.io\storage v0.0.0 => /go/src/go.edusense.io/storage" >> go.mod
RUN CGO_ENABLED=0 GOOS=linux go build -a -o storage go.edusense.io/storage/apiserver

FROM alpine:latest
# The following gosu setup procedure is derived from
# https://github.com/tianon/gosu. LICENSE: GPL-3.0.
ENV GOSU_VERSION 1.11
RUN set -eux; \
  \
  apk add --no-cache --virtual .gosu-deps \
    ca-certificates \
    dpkg \
    gnupg \
  ; \
  \
  dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"; \
  wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch"; \
  wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc"; \
  \
# verify the signature
  export GNUPGHOME="$(mktemp -d)"; \
  gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4; \
  gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu; \
  command -v gpgconf && gpgconf --kill all || :; \
  rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc; \
  \
# clean up fetch dependencies
  apk del --no-network .gosu-deps; \
  \
  chmod +x /usr/local/bin/gosu; \
# verify that the binary works
  gosu --version; \
  gosu nobody true
# END of gosu setup

WORKDIR /app
COPY --from=builder /go/src/go.edusense.io/storage/storage storage
COPY ./entrypoint.sh .
RUN chmod +x ./entrypoint.sh ./storage

ENTRYPOINT ["/app/entrypoint.sh"]
