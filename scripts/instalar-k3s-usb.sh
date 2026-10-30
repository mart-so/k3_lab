#!/usr/bin/env bash
# Instala los prerrequisitos y deja K3s usando el montaje persistente (USB o disco local).
# Compatible con Ubuntu/Debian (apt) y Fedora/RHEL (dnf).
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Ejecute con sudo: sudo $0 [particion]" >&2
  exit 1
fi

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DATOS=/srv/k3s-persistente
DISPOSITIVO="${1:-}"

if [[ -n "$DISPOSITIVO" ]]; then
  [[ -b "$DISPOSITIVO" ]] || { echo "No es un dispositivo de bloques: $DISPOSITIVO" >&2; exit 1; }
  mkdir -p "$DATOS"
  uuid="$(blkid -s UUID -o value "$DISPOSITIVO")"
  [[ -n "$uuid" ]] || { echo "La partición debe tener un sistema de archivos y UUID." >&2; exit 1; }
  grep -q " $DATOS " /etc/fstab || echo "UUID=$uuid $DATOS ext4 defaults,noatime,commit=60 0 2" >> /etc/fstab
  mountpoint -q "$DATOS" || mount "$DATOS"
else
  mkdir -p "$DATOS"
fi

mkdir -p "$DATOS/k3s" "$DATOS/pv" /etc/rancher/k3s /etc/docker
install -m 0644 "$RAIZ/config/k3s-config.yaml" /etc/rancher/k3s/config.yaml
install -m 0644 "$RAIZ/config/registries.yaml" /etc/rancher/k3s/registries.yaml

# Configurar registro inseguro en Docker sin sobrescribir otras configuraciones existentes
if [[ -f /etc/docker/daemon.json ]]; then
  python3 -c "
import json
try:
    with open('/etc/docker/daemon.json', 'r') as f:
        data = json.load(f)
except Exception:
    data = {}
regs = set(data.get('insecure-registries', []))
regs.update(['localhost:30500', '127.0.0.1:30500'])
data['insecure-registries'] = sorted(list(regs))
with open('/etc/docker/daemon.json', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null || install -m 0644 "$RAIZ/config/daemon.json" /etc/docker/daemon.json
else
  install -m 0644 "$RAIZ/config/daemon.json" /etc/docker/daemon.json
fi

# Copiar manifiesto de Traefik tanto al directorio por defecto como al data-dir persistente
mkdir -p /var/lib/rancher/k3s/server/manifests "$DATOS/k3s/server/manifests"
install -m 0644 "$RAIZ/config/traefik-gateway.yaml" /var/lib/rancher/k3s/server/manifests/traefik-gateway.yaml
install -m 0644 "$RAIZ/config/traefik-gateway.yaml" "$DATOS/k3s/server/manifests/traefik-gateway.yaml"

# Instalación de paquetes según la distribución
if command -v apt-get >/dev/null; then
  echo "==> Detectado sistema Ubuntu/Debian (apt). Instalando paquetes..."
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  paquetes=(curl ca-certificates git nfs-common cifs-utils openssh-client smbclient)
  if ! command -v docker >/dev/null; then
    paquetes+=(docker.io)
  fi
  apt-get install -y "${paquetes[@]}"
  systemctl enable --now docker
  systemctl restart docker || true
  systemctl disable --now zram-config.service 2>/dev/null || true

  # Ajustar política de reenvío en UFW si está activo (necesario para CNI / Flannel en Ubuntu)
  if command -v ufw >/dev/null && ufw status 2>/dev/null | grep -qw "active"; then
    echo "==> Ajustando política de reenvío de UFW para K3s (DEFAULT_FORWARD_POLICY=ACCEPT)..."
    sed -i 's/DEFAULT_FORWARD_POLICY="DROP"/DEFAULT_FORWARD_POLICY="ACCEPT"/' /etc/default/ufw
    ufw reload || true
  fi
elif command -v dnf >/dev/null; then
  echo "==> Detectado sistema Fedora/RHEL (dnf). Instalando paquetes..."
  dnf install -y curl ca-certificates docker git nfs-utils cifs-utils openssh-clients samba-client
  systemctl enable --now docker
  systemctl restart docker || true
  systemctl disable --now swap-create@zram0.service 2>/dev/null || true
else
  echo "ADVERTENCIA: Gestor de paquetes no reconocido. Asegúrese de tener Docker, curl, git, nfs y cifs instalados." >&2
fi

# Desactivar swap
swapoff -a || true

# Instalar K3s si no está instalado
if ! command -v k3s >/dev/null; then
  echo "==> Instalando K3s..."
  curl -sfL https://get.k3s.io | sh -
else
  echo "==> K3s ya instalado. Iniciando servicio..."
  systemctl enable --now k3s
fi

# Enlace simbólico de kubectl
ln -sf /usr/local/bin/k3s /usr/local/bin/kubectl

# Esperar a que el nodo esté listo
echo "==> Esperando que K3s responda..."
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
until /usr/local/bin/k3s kubectl get nodes >/dev/null 2>&1; do sleep 2; done

echo "==> Instalando CRD de Gateway API..."
/usr/local/bin/k3s kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.1/standard-install.yaml

# Permisos y configuración de KUBECONFIG
chmod 644 /etc/rancher/k3s/k3s.yaml
echo 'export KUBECONFIG=/etc/rancher/k3s/k3s.yaml' > /etc/profile.d/k3s.sh
chmod 644 /etc/profile.d/k3s.sh

# Configurar acceso para el usuario que invocó sudo
USUARIO="${SUDO_USER:-$USER}"
if [[ -n "$USUARIO" && "$USUARIO" != "root" ]]; then
  usermod -aG docker "$USUARIO" || true
  USUARIO_HOME="$(getent passwd "$USUARIO" | cut -d: -f6)"
  if [[ -n "$USUARIO_HOME" && -d "$USUARIO_HOME" ]]; then
    mkdir -p "$USUARIO_HOME/.kube"
    install -m 0600 -o "$USUARIO" /etc/rancher/k3s/k3s.yaml "$USUARIO_HOME/.kube/config" || true
  fi
fi

echo "================================================================================"
echo "Instalación terminada exitosamente."
echo "Abra una nueva sesión (o use 'newgrp docker') y ejecute:"
echo "  ./scripts/encender.sh basicos"
echo "================================================================================"
