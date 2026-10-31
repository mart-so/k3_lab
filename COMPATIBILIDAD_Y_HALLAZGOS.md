# Compatibilidad Ubuntu / Fedora e Informe de Hallazgos

Este documento resume las adaptaciones técnicas realizadas para que el laboratorio funcione indistintamente en **Fedora Workstation** y **Ubuntu (22.04 / 24.04 LTS)**, junto con una auditoría de **issues y oportunidades de mejora detectados** en el repositorio.

---

## 1. Puntos adaptados para compatibilidad Fedora + Ubuntu

Previamente, el repositorio estaba acoplado a Fedora Workstation y a instalaciones sobre pendrive USB. Se realizaron las siguientes mejoras de compatibilidad:

### 1.1. Detección automática del gestor de paquetes y equivalencias
En `scripts/instalar-k3s-usb.sh` se sustituyó la invocación directa de `dnf` por una detección condicional (`command -v apt-get` vs `command -v dnf`), mapeando los nombres de paquetes específicos de cada distribución:

| Componente | Fedora (`dnf`) | Ubuntu (`apt`) |
| :--- | :--- | :--- |
| **Cliente NFS** | `nfs-utils` | `nfs-common` |
| **Cliente SSH / SFTP** | `openssh-clients` | `openssh-client` |
| **Cliente Samba** | `samba-client` | `smbclient` |
| **Montaje CIFS** | `cifs-utils` | `cifs-utils` |
| **Motor Docker** | `docker` | `docker.io` *(instalado sólo si Docker no está ya presente)* |
| **Modo no interactivo** | Estándar | `export DEBIAN_FRONTEND=noninteractive` |

### 1.2. Reglas de cortafuegos y reenvío de tráfico (UFW en Ubuntu)
* **Problema:** Ubuntu incluye `ufw` activado por defecto con política `DEFAULT_FORWARD_POLICY="DROP"`, lo que bloquea el tráfico entre pods y la red virtual de Flannel (CNI VXLAN de K3s).
* **Solución:** Se añadió detección de UFW activo y modificación automática a `DEFAULT_FORWARD_POLICY="ACCEPT"` en `/etc/default/ufw` con recarga (`ufw reload`).

### 1.3. Desactivación de Swap y ZRAM
* **Problema:** Fedora utiliza zram por defecto mediante `swap-create@zram0.service`, mientras que Ubuntu suele emplear `zram-config.service` o un archivo de swap convencional (`/swapfile`).
* **Solución:** Se deshabilitan ambos servicios según el sistema detectado y se invoca `swapoff -a`.

### 1.4. Configuración no destructiva de Docker (`/etc/docker/daemon.json`)
* **Problema:** Sobrescribir directamente `/etc/docker/daemon.json` borraba opciones existentes en máquinas de desarrollo (drivers de logs, almacenamiento, DNS, etc.).
* **Solución:** Se implementó una fusión inteligente en Python que lee el JSON existente (si existe) y añade únicamente los registros inseguros locales (`localhost:30500` y `127.0.0.1:30500`), escribiendo el archivo completo solo si no existía.

### 1.5. Persistencia y ubicación de manifiestos K3s (`traefik-gateway.yaml`)
* Se asegura la copia del manifiesto `traefik-gateway.yaml` tanto en la ruta por defecto de K3s (`/var/lib/rancher/k3s/server/manifests/`) como en el almacenamiento persistente (`/srv/k3s-persistente/k3s/server/manifests/`), garantizando que Traefik inicialice con soporte de Gateway API sin importar el momento de montaje.

### 1.6. Configuración de credenciales de `kubectl` y permisos de usuario
* Se configuró `/etc/profile.d/k3s.sh` con `export KUBECONFIG=/etc/rancher/k3s/k3s.yaml` (permisos 644).
* Se crea enlace simbólico `/usr/local/bin/kubectl -> /usr/local/bin/k3s`.
* Se copia la configuración a `~/.kube/config` (permisos 600) perteneciente al usuario regular (`SUDO_USER`) y se añade al grupo `docker`.
* En `scripts/comun.sh` se garantiza `PATH="/usr/local/bin:$PATH"` y `KUBECONFIG` por defecto para que los scripts no requieran `sudo`.

### 1.7. Soporte para ejecución en disco local y symlink de instalación
* Se creó el symlink `scripts/instalar-k3s.sh -> instalar-k3s-usb.sh`.
* El script admite omitir el argumento de partición: si no se especifica una partición de pendrive USB, utiliza directamente el directorio `/srv/k3s-persistente` en el disco local sin alterar `/etc/fstab`.

### 1.8. Corrección sintáctica YAML en K3s
* En `config/k3s-config.yaml` se eliminó la directiva vacía `disable:` (commit `44e1483`), la cual provocaba fallos de análisis sintáctico al inicializar K3s.

### 1.9. Resiliencia en script de pruebas (`probar-servicios.sh`)
* Se silenció stderr en verificaciones `curl` (`2>&1`).
* Se añadió doble comprobación para la aplicación de ejemplo: prueba primero a través de Traefik Gateway API (`http://localhost/`) y realiza fallback a NodePort (`http://localhost:30088/`).

### 1.10. Documentación y enunciados
* Se actualizaron `README.md` y `gen_enunciado.py` con instrucciones explícitas para Ubuntu (LTS 22.04 / 24.04) y Fedora, clientes recomendados (`smbclient`, `linphone`, `mount -t nfs4`), y diagramas neutrales entre host local y USB.

---

## 2. Issues adicionales detectados (independientes de la migración)

Durante el análisis del repositorio se identificaron los siguientes problemas y áreas de mejora técnica:

### Issue 1 (Crítico): Falta el archivo `app-ejemplo/sitio/index.html`
* **Ubicación:** Carpeta `app-ejemplo/`.
* **Detalle:** 
  - `app-ejemplo/Dockerfile` ejecuta: `COPY sitio/index.html /usr/share/nginx/html/index.html`.
  - `app-ejemplo/entrypoint-info.sh` edita las cadenas `__VERSION_APP__`, `__HOSTNAME__` y `__POD_IP__` sobre dicho archivo.
  - La guía (`gen_enunciado.py`) solicita al alumno modificar `app-ejemplo/sitio/index.html`.
* **Impacto:** La carpeta `sitio/` no existe en el repositorio. Al ejecutar `./scripts/construir-y-publicar.sh`, el comando `docker build` falla de inmediato con error de archivo no encontrado.
* **Solución sugerida:** Crear `app-ejemplo/sitio/index.html` con un HTML base que contenga los marcadores esperados.

### Issue 2: Prueba TCP de Asterisk en `probar-servicios.sh` vs Configuración UDP
* **Ubicación:** `manifiestos/05-asterisk/asterisk.yaml` y `scripts/probar-servicios.sh`.
* **Detalle:** 
  - `scripts/probar-servicios.sh` prueba el servicio con: `probar_tcp asterisk 5060` (mediante `/dev/tcp/127.0.0.1/5060`).
  - Sin embargo, en el ConfigMap `pjsip.conf` solo está definido el transporte UDP:
    ```ini
    [transport-udp]
    type=transport
    protocol=udp
    bind=0.0.0.0:5060
    ```
* **Impacto:** Al no haber un `[transport-tcp]` configurado en Asterisk, el puerto TCP 5060 rechaza la conexión y `probar-servicios.sh` reporta `FALLA asterisk (tcp/5060)` aunque Asterisk funcione correctamente por UDP.
* **Solución sugerida:** Agregar `[transport-tcp]` en `pjsip.conf` o adaptar `probar-servicios.sh` para verificar el contenedor mediante `asterisk -rx "core ping"` o herramienta UDP.

### Issue 3: Requerimiento del módulo de kernel `nfsd` en el Host
* **Ubicación:** `manifiestos/04-nfs/nfs.yaml` y `scripts/instalar-k3s-usb.sh`.
* **Detalle:** La imagen `itsthenetwork/nfs-server-alpine:12` se ejecuta en modo privilegiado y requiere que el kernel del host tenga cargado el módulo del servidor NFS (`nfsd`).
* **Impacto:** En sistemas Ubuntu y Fedora recién instalados, instalar las utilidades cliente (`nfs-common` / `nfs-utils`) no carga automáticamente el módulo del servidor. Si el host no tiene `nfsd` cargado, el pod entra en error al no encontrar `/proc/fs/nfsd`.
* **Solución sugerida:** Añadir `modprobe nfs nfsd || true` en `scripts/instalar-k3s-usb.sh` o registrarlo en `/etc/modules-load.d/nfs.conf`.

### Issue 4: `mi-app` no contemplada en scripts de parada (`apagar.sh`)
* **Ubicación:** `scripts/comun.sh` y `scripts/apagar.sh`.
* **Detalle:** Las listas `servicios_basicos` y `servicios_todos` contienen `gateway`, pero no `mi-app`. Asimismo, la función `manifiesto()` rechaza cualquier invocación directa a `mi-app` o `aplicacion`.
* **Impacto:** Al ejecutar `./scripts/apagar.sh todos`, los pods de la aplicación de ejemplo continúan ejecutándose. Tampoco es posible detenerla de forma selectiva (`./scripts/apagar.sh mi-app`).
* **Solución sugerida:** Incluir el caso `mi-app` en `manifiesto()` apuntando a `$RAIZ/app-ejemplo/despliegue.yaml`, o añadir `kubectl scale deployment mi-app --replicas=0` condicionalmente en `apagar.sh`.

### Issue 5: Persistencia de Swap tras reinicio en Ubuntu
* **Ubicación:** `scripts/instalar-k3s-usb.sh`.
* **Detalle:** El comando `swapoff -a` desactiva el swap temporalmente en la sesión activa. En Ubuntu, la entrada `/swapfile` permanece en `/etc/fstab`.
* **Impacto:** Al reiniciar el equipo, el swap vuelve a estar activo. Aunque `kubelet-arg: ["fail-swap-on=false"]` previene que K3s caiga, Kubernetes pierde previsibilidad sobre las cuotas de memoria de cgroups.
* **Solución sugerida:** Comentar las entradas de swap en `/etc/fstab` durante la instalación (`sed -i '/swap/s/^/#/' /etc/fstab`).

### Issue 6: Dependencia externa en tiempo de instalación de Gateway API
* **Ubicación:** `scripts/instalar-k3s-usb.sh`.
* **Detalle:** La instalación de las CRDs de Gateway API realiza una descarga directa desde GitHub:
  `kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.1/standard-install.yaml`
* **Impacto:** En entornos educativos de laboratorio o aulas sin conexión a internet estable, la instalación falla si no se puede resolver el recurso externo.
* **Solución sugerida:** Alojar el archivo `standard-install.yaml` dentro de `manifiestos/09-gateway/crd/` para una instalación 100% offline.

### Issue 7: Inconsistencia con NodePort 30088 en `app-ejemplo/despliegue.yaml`
* **Ubicación:** `app-ejemplo/despliegue.yaml` vs `scripts/probar-servicios.sh`.
* **Detalle:** `probar-servicios.sh` hace un fallback a `http://localhost:30088/`. No obstante, el servicio en `app-ejemplo/despliegue.yaml` está definido como `ClusterIP` en el puerto 80 sin especificar `type: NodePort` ni `nodePort: 30088`.
* **Impacto:** Si Gateway API (Traefik) no está enrutando el puerto 80, el fallback a 30088 nunca responderá a menos que el servicio sea explícitamente un `NodePort`.
* **Solución sugerida:** Configurar `type: NodePort` con `nodePort: 30088` en `app-ejemplo/despliegue.yaml` si se desea mantener ese mecanismo alternativo de verificación.

### Issue 8: Propagación de `set -e` en `probar-servicios.sh`
* **Ubicación:** `scripts/probar-servicios.sh`.
* **Detalle:** El script declara `set -u` en su primera línea para evitar abortar si una comprobación individual falla. Sin embargo, al ejecutar `source "$(dirname "$0")/comun.sh"`, se ejecuta la directiva `set -euo pipefail` de este último.
* **Impacto:** Cualquier comando intermedio que devuelva un código distinto de cero dentro del flujo principal podría abortar el script completo de verificación prematuramente.
* **Solución sugerida:** Restablecer `set +e` inmediatamente después de hacer `source` de `comun.sh`.
