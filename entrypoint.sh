#!/bin/sh
set -e

export ICP_NUMBER="${ICP_NUMBER:-}"
export ICP_CHINA_ONLY="${ICP_CHINA_ONLY:-true}"

CONFIG_FILE="/usr/share/nginx/html/assets/javascripts/site-config.js"

if [ -f "$CONFIG_FILE" ]; then
  envsubst < "$CONFIG_FILE" > /tmp/site-config.js
  mv /tmp/site-config.js "$CONFIG_FILE"
fi

exec nginx -g 'daemon off;'
