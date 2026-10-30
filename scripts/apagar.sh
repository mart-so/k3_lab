#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/comun.sh"

objetivo="${1:-todos}"
detener_motor="${2:-}"
require_kubectl

while IFS= read -r servicio; do
  if kubectl get deployment "$servicio" -n "$NAMESPACE" >/dev/null 2>&1; then
    echo "Apagando: $servicio"
    kubectl scale deployment "$servicio" -n "$NAMESPACE" --replicas=0
  fi
done < <(expandir_servicios "$objetivo")

if [[ "$detener_motor" == "--motor" ]]; then
  echo "Deteniendo K3s y sincronizando el almacenamiento..."
  sudo systemctl stop k3s
  sync
fi
