#!/bin/bash
set -e

if [ -n "$AUTH_SERVER_PUBLIC_URL" ]; then
  export AUTH_SERVER_PUBLIC_URL="${AUTH_SERVER_PUBLIC_URL%/}"
else
  echo "AUTH_SERVER_PUBLIC_URL must be set to the public auth-server tenant URL."
  exit 1
fi

echo "AUTH_SERVER_PUBLIC_URL: $AUTH_SERVER_PUBLIC_URL"

exec "$@"
