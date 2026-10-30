#!/usr/bin/env bash
# Funciones compartidas por los scripts del laboratorio.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAMESPACE="lab-so"

export PATH="/usr/local/bin:$PATH"
export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"

require_kubectl() {
  command -v kubectl >/dev/null || { echo "No se encontró kubectl. Ejecute primero sudo ./scripts/instalar-k3s-usb.sh." >&2; exit 1; }
  kubectl get node >/dev/null 2>&1 || { echo "No se pudo conectar al clúster K3s con kubectl. Verifique que el servicio esté activo: sudo systemctl status k3s" >&2; exit 1; }
}

manifiesto() {
  case "$1" in
    registro) echo "$RAIZ/manifiestos/01-registro/registro.yaml" ;;
    sftp) echo "$RAIZ/manifiestos/02-sftp/sftp.yaml" ;;
    samba) echo "$RAIZ/manifiestos/03-samba/samba.yaml" ;;
    nfs) echo "$RAIZ/manifiestos/04-nfs/nfs.yaml" ;;
    asterisk) echo "$RAIZ/manifiestos/05-asterisk/asterisk.yaml" ;;
    gitea) echo "$RAIZ/manifiestos/06-gitea/gitea.yaml" ;;
    gitlab) echo "$RAIZ/manifiestos/07-gitlab/gitlab.yaml" ;;
    panel) echo "$RAIZ/manifiestos/08-panel/panel.yaml" ;;
    gateway) echo "$RAIZ/manifiestos/09-gateway/gateway.yaml" ;;
    *) echo "Servicio desconocido: $1" >&2; return 1 ;;
  esac
}

servicios_basicos=(registro sftp samba nfs asterisk gitea panel gateway)
servicios_todos=(registro sftp samba nfs asterisk gitea gitlab panel gateway)

expandir_servicios() {
  case "$1" in
    basicos) printf '%s\n' "${servicios_basicos[@]}" ;;
    todos) printf '%s\n' "${servicios_todos[@]}" ;;
    *) manifiesto "$1" >/dev/null; printf '%s\n' "$1" ;;
  esac
}
