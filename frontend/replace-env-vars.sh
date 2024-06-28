#!/bin/sh
sed -i "s|API_URL_PLACEHOLDER|$API_URL|g" /usr/src/app/src/environments/environment.ts
