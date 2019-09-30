#!/bin/sh
# The following code is derived from one of the code snippets in
# https://denibertovic.com/posts/handling-permissions-with-docker-volumes/ .

# Add local user.
# Either use the LOCAL_USER_ID if passed in at runtime or fallback.
USER_ID=${LOCAL_USER_ID:-9001}

adduser --shell /bin/sh -u $USER_ID --gecos "" --quiet --disabled-login --no-create-home edusense
chown -R edusense:edusense /app

# Read secrets and then deescalate the previleges
APP_USERNAME="$(cat /run/secrets/app_username)"
APP_PASSWORD="$(cat /run/secrets/app_password)"

exec env APP_USERNAME="$APP_USERNAME" \
  env APP_PASSWORD="$APP_PASSWORD" \
  gosu edusense python audio_pipeline.py "$@"
