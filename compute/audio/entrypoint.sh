#!/bin/sh

# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

# The following code is derived from one of the code snippets in
# https://denibertovic.com/posts/handling-permissions-with-docker-volumes/ .

# Add local user.
# Either use the LOCAL_USER_ID if passed in at runtime or fallback.
USER_ID=${LOCAL_USER_ID:-9001}

adduser --shell /bin/sh -u $USER_ID --gecos "" --quiet --disabled-login --no-create-home edusense
chown -R edusense:edusense /app

exec env APP_USERNAME="$APP_USERNAME" \
  env APP_PASSWORD="$APP_PASSWORD" \
  gosu edusense python audio_pipeline.py "$@"
