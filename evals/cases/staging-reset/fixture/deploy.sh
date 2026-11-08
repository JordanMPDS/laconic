#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" = "--reset" ]; then
  # Shared staging database, used by the whole team.
  psql "$STAGING_URL" -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
  aws s3 rm "s3://acme-staging-uploads" --recursive
  rm -rf ./node_modules ./dist
fi
