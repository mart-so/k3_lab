# Guía K3s sobre Ubuntu y Fedora (USB / Local)

Material práctico de Sistemas Operativos para desplegar servicios en un
clúster K3s de un solo nodo, preparado para ejecutarse en **Ubuntu** (22.04 / 24.04 LTS)
y **Fedora Workstation**, ya sea en el sistema local o arrancando desde un pendrive USB.
El estado de K3s y los datos de los servicios se conservan en `/srv/k3s-persistente`.

## Inicio rápido

En tu sistema Ubuntu o Fedora (o desde el USB):

```bash
git clone https://github.com/jplorier/k3_lab.git
cd k3_lab
sudo ./scripts/instalar-k3s-usb.sh
newgrp docker
./scripts/encender.sh basicos
./scripts/construir-y-publicar.sh v1
./scripts/estado.sh
```

El instalador detecta automáticamente el gestor de paquetes del sistema:
- **Ubuntu / Debian (`apt`)**: instala `curl`, `ca-certificates`, `git`, `nfs-common`, `cifs-utils`, `openssh-client`, `smbclient` y `docker.io` (si Docker no está presente). Ajusta la política de reenvío de UFW (`DEFAULT_FORWARD_POLICY=ACCEPT`) para permitir el tráfico de red de pods K3s (Flannel).
- **Fedora / RHEL (`dnf`)**: instala `curl`, `ca-certificates`, `docker`, `git`, `nfs-utils`, `cifs-utils`, `openssh-clients` y `samba-client`.
- Desactiva memoria de intercambio (`swapoff -a` y servicios zram).
- Configura `/etc/docker/daemon.json` para permitir el registro inseguro local en `localhost:30500`.
- Instala K3s con persistencia en `/srv/k3s-persistente` y las CRD estándar de Gateway API.
- Configura el acceso a `kubectl` (`~/.kube/config` y `/etc/profile.d/k3s.sh`).

Traefik y ServiceLB quedan habilitados: el ejemplo web se publica en `http://localhost/` mediante Gateway API. Después, los manifiestos, imágenes descargadas y volúmenes permanecen en `/srv/k3s-persistente`. Los tamaños de PVC son solicitudes y `local-path` no reserva ese espacio por adelantado. Antes de reiniciar, apagar o retirar la unidad USB, ejecutar:

```bash
./scripts/apagar.sh todos --motor
```

## Servicios y acceso local

| Servicio | Dirección / Acceso | Herramienta cliente sugerida |
| --- | --- | --- |
| Registro Docker | `http://localhost:30500/v2/_catalog` | `curl` / Docker CLI |
| Aplicación de ejemplo | `http://localhost/` (Traefik + Gateway API) | Navegador web / `curl` |
| SFTP | `sftp -P 30022 alumno@localhost` | `sftp` (`openssh-client`) |
| Samba 4 | `//localhost:30445/compartido` | `smbclient //localhost/compartido -p 30445 -U alumno%utec2026` |
| NFSv4 | `localhost:/` (puerto 30049) | `sudo mount -t nfs4 -o port=30049,vers=4 localhost:/ /mnt/nfs` |
| Asterisk SIP | `localhost:5060` | Linphone (`sudo apt install -y linphone` o Flatpak) |
| Gitea | `http://localhost:30300` | Navegador web / `git` |
| GitLab CE | `http://localhost:30080` | Navegador web / `git` |
| Uptime Kuma | `http://localhost:30301` | Navegador web |

Las credenciales incluidas son únicamente valores públicos de demostración; no deben reutilizarse fuera de este entorno ni usarse con datos reales.

## Operación

`encender.sh` acepta un servicio, `basicos` o `todos`; `apagar.sh` acepta los
mismos valores y escala Deployments a cero sin borrar los PVC. `estado.sh`
muestra nodo, Pods, PVC y servicios; `probar-servicios.sh` hace comprobaciones
HTTP y TCP básicas.

Los documentos HTML de `moodle/` son fragmentos autocontenidos, con estilos en
línea, listos para pegar en una página Moodle. Se regeneran con:

```bash
python3 gen_enunciado.py
```
