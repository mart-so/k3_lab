#!/usr/bin/env bash
set -u
source "$(dirname "$0")/comun.sh"
require_kubectl

probar_http() {
  local nombre="$1" url="$2"
  if curl --fail --silent --max-time 5 "$url" >/dev/null 2>&1; then
    echo "OK   $nombre ($url)"
  else
    echo "FALLA $nombre ($url)"
  fi
}
probar_tcp() {
  local nombre="$1" puerto="$2"
  if timeout 5 bash -c "</dev/tcp/127.0.0.1/$puerto" 2>/dev/null; then
    echo "OK   $nombre (tcp/$puerto)"
  else
    echo "FALLA $nombre (tcp/$puerto)"
  fi
}

probar_http registro http://localhost:30500/v2/
if curl --fail --silent --max-time 5 "http://localhost/" >/dev/null 2>&1; then
  echo "OK   aplicacion (http://localhost/)"
elif curl --fail --silent --max-time 5 "http://localhost:30088/" >/dev/null 2>&1; then
  echo "OK   aplicacion (http://localhost:30088/)"
else
  echo "FALLA aplicacion (http://localhost/)"
fi
probar_http gitea http://localhost:30300/
probar_http panel http://localhost:30301/
probar_tcp sftp 30022
probar_tcp samba 30445
probar_tcp nfs 30049
probar_tcp asterisk 5060
