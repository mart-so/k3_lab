#!/usr/bin/env python3
"""Genera documentación HTML autocontenida para Moodle sobre K3s (UTEC SO).

Restricciones Moodle: CSS 100 % inline, sin <style>/<script>/SVG/display:grid,
solo contenido de <body>, salida ASCII (acentos como entidades HTML).
"""
import html
import os

AZUL, VERDE, AMBAR, ROSA, PURP, TEAL, BOSQUE = (
    "#1A5EA0", "#1D6E4F", "#8B5A0A", "#8B2450", "#4A3A9A", "#0E6E72", "#2E6010")
TXT = "#1F2328"
SUAVE = "#5B6168"
BORDE = "#D8DDE3"
FONDO_CODE = "#F3F5F7"
FUENTE = "font-family:Segoe UI,Roboto,Helvetica,Arial,sans-serif;"
MONO = "font-family:Consolas,Menlo,DejaVu Sans Mono,monospace;"


def esc(s):
    return html.escape(s, quote=False)


def tint(color, alpha="14"):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    f = 0.90 if alpha == "14" else 0.80
    mix = lambda c: int(c + (255 - c) * f)
    return "#%02X%02X%02X" % (mix(r), mix(g), mix(b))


def c(s):
    return (f'<code style="{MONO}font-size:13px;background:{FONDO_CODE};'
            f'border:1px solid {BORDE};border-radius:3px;padding:0 4px;">{esc(s)}</code>')


def b(s):
    return f'<strong>{s}</strong>'


def chip(t, color):
    return (f'<span style="display:inline-block;background:{color};color:#FFFFFF;'
            f'font-size:11.5px;padding:2px 6px;border-radius:3px;margin:2px 2px;">{t}</span>')


def caja(titulo, cuerpo, color, extra=""):
    return (f'<div style="border:2px solid {color};background:{tint(color)};border-radius:6px;'
            f'padding:6px 8px;margin:4px;{FUENTE}{extra}">'
            f'<div style="font-size:11px;font-weight:700;color:{color};letter-spacing:0.5px;">{titulo}</div>'
            f'<div style="font-size:12.5px;color:{TXT};line-height:1.4;">{cuerpo}</div></div>')


def flecha(texto="", color=SUAVE):
    return (f'<div style="text-align:center;{FUENTE}color:{color};font-size:12px;line-height:1.2;">'
            f'<div style="font-size:20px;">&rarr;</div>{texto}</div>')


class DocMoodle:
    def __init__(self):
        self.out = []
        self.w(f'<div style="max-width:980px;margin:0 auto;{FUENTE}color:{TXT};">')

    def w(self, s):
        self.out.append(s)

    def portada(self, subtitulo, titulo, bajada, color=AZUL):
        self.w(f'<div style="background:{color};color:#FFFFFF;border-radius:8px;padding:22px 24px;margin:0 0 18px 0;">'
               f'<div style="font-size:13px;letter-spacing:2px;opacity:0.85;">{esc(subtitulo)}</div>'
               f'<div style="font-size:28px;font-weight:800;line-height:1.2;margin:4px 0 6px 0;">{esc(titulo)}</div>'
               f'<div style="font-size:15.5px;opacity:0.92;line-height:1.5;">{bajada}</div></div>')

    def h2(self, num, titulo, color=AZUL):
        self.w(f'<div style="margin:34px 0 14px 0;padding:10px 16px;background:{color};'
               f'color:#FFFFFF;border-radius:6px;{FUENTE}">'
               f'<span style="font-size:13px;letter-spacing:1px;opacity:0.85;">{esc(num)}</span>'
               f'<div style="font-size:21px;font-weight:700;line-height:1.25;">{esc(titulo)}</div></div>')

    def h3(self, titulo, color=AZUL):
        self.w(f'<h3 style="{FUENTE}font-size:18px;color:{color};margin:22px 0 8px 0;'
               f'border-bottom:2px solid {tint(color, "33")};padding-bottom:4px;">{esc(titulo)}</h3>')

    def p(self, texto):
        self.w(f'<p style="{FUENTE}font-size:15px;line-height:1.6;color:{TXT};margin:8px 0;">{texto}</p>')

    def code(self, bloque, titulo=None):
        if titulo:
            self.w(f'<div style="{FUENTE}font-size:12px;color:{SUAVE};margin:12px 0 0 0;'
                   f'font-weight:600;letter-spacing:0.5px;">{esc(titulo)}</div>')
        self.w(f'<pre style="{MONO}font-size:13px;line-height:1.5;background:{FONDO_CODE};'
               f'color:{TXT};border:1px solid {BORDE};border-left:4px solid {AZUL};'
               f'border-radius:4px;padding:10px 12px;margin:6px 0 12px 0;white-space:pre-wrap;'
               f'word-wrap:break-word;overflow-x:auto;">{esc(bloque.strip(chr(10)))}</pre>')

    def nota(self, titulo, cuerpo, color=AZUL):
        self.w(f'<div style="background:{tint(color)};border-left:5px solid {color};'
               f'border-radius:4px;padding:10px 14px;margin:12px 0;{FUENTE}">'
               f'<div style="font-weight:700;color:{color};font-size:14px;margin-bottom:4px;">{esc(titulo)}</div>'
               f'<div style="font-size:14.5px;line-height:1.55;color:{TXT};">{cuerpo}</div></div>')

    def lista(self, items, ordenada=False):
        tag = "ol" if ordenada else "ul"
        self.w(f'<{tag} style="{FUENTE}font-size:15px;line-height:1.6;color:{TXT};margin:6px 0 10px 0;padding-left:26px;">')
        for it in items:
            self.w(f'<li style="margin:4px 0;">{it}</li>')
        self.w(f'</{tag}>')

    def tabla(self, cabecera, filas, color=AZUL, anchos=None):
        self.w(f'<table style="border-collapse:collapse;width:100%;margin:10px 0 16px 0;{FUENTE}font-size:14px;">')
        self.w('<tr>')
        for i, h in enumerate(cabecera):
            ancho = f"width:{anchos[i]};" if anchos else ""
            self.w(f'<th style="background:{color};color:#FFFFFF;text-align:left;padding:7px 9px;'
                   f'border:1px solid {color};{ancho}">{h}</th>')
        self.w('</tr>')
        for n, fila in enumerate(filas):
            fondo = "#FFFFFF" if n % 2 == 0 else "#F7F9FB"
            self.w('<tr>')
            for celda in fila:
                self.w(f'<td style="padding:7px 9px;border:1px solid {BORDE};background:{fondo};'
                       f'vertical-align:top;line-height:1.45;color:{TXT};">{celda}</td>')
            self.w('</tr>')
        self.w('</table>')

    def tarea(self, idn, texto):
        self.w(f'<div style="border:1px dashed {AMBAR};background:{tint(AMBAR)};border-radius:4px;'
               f'padding:8px 12px;margin:8px 0;{FUENTE}font-size:14.5px;line-height:1.55;color:{TXT};">'
               f'<span style="display:inline-block;background:{AMBAR};color:#FFFFFF;font-weight:700;'
               f'font-size:12px;padding:1px 7px;border-radius:3px;margin-right:6px;">PRÁCTICA {esc(idn)}</span>{texto}</div>')

    def informe(self, texto):
        self.w(f'<div style="border-left:4px solid {PURP};background:{tint(PURP)};padding:8px 12px;'
               f'margin:8px 0;border-radius:4px;{FUENTE}font-size:14.5px;line-height:1.55;color:{TXT};">'
               f'<span style="font-weight:700;color:{PURP};">Comprobación sugerida: </span>{texto}</div>')

    def flujo(self, pasos, color_flecha=SUAVE):
        self.w('<table style="border-collapse:collapse;width:100%;margin:10px 0 14px 0;"><tr>')
        for i, x in enumerate(pasos):
            if i % 2 == 0:
                self.w(f'<td style="vertical-align:middle;padding:0;">{x}</td>')
            else:
                self.w(f'<td style="vertical-align:middle;padding:0 2px;width:90px;">{flecha(x, color_flecha)}</td>')
        self.w('</tr></table>')

    def pregunta(self, n, q, r):
        self.w(f'<div style="border:1px solid {BORDE};border-radius:6px;padding:10px 14px;margin:10px 0;{FUENTE}">'
               f'<div style="font-size:15px;color:{TXT};line-height:1.55;"><strong style="color:{AZUL};">{n}.</strong> {q}</div>'
               f'<details style="margin-top:6px;"><summary style="cursor:pointer;color:{AZUL};font-size:14px;font-weight:600;">Ver respuesta</summary>'
               f'<div style="font-size:14.5px;line-height:1.55;color:{TXT};margin-top:6px;padding:8px 10px;'
               f'background:{tint(VERDE)};border-left:4px solid {VERDE};border-radius:4px;">{r}</div></details></div>')

    def guardar(self, ruta):
        contenido = "\n".join(self.out + ['</div>'])
        ascii_doc = contenido.encode("ascii", "xmlcharrefreplace").decode("ascii")
        os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
        with open(ruta, "w", encoding="ascii") as f:
            f.write(ascii_doc)
        print(f"Generado: {ruta} ({len(ascii_doc)} bytes)")


def generar_enunciado_principal():
    d = DocMoodle()
    d.portada(
        "GUÍA PRÁCTICA · SISTEMAS OPERATIVOS",
        "Aprender contenedores y Kubernetes con K3s en Ubuntu y Fedora (USB / Local)",
        "Construcción, etiquetado y publicación de imágenes Docker en un registro propio dentro de K3s, "
        "y despliegue de servicios de infraestructura con almacenamiento persistente: SFTP, Samba 4, "
        "NFSv4, telefonía VoIP con Asterisk, servidores Git (Gitea y GitLab CE) y monitoreo con Uptime Kuma."
    )

    d.tabla(
        ["Objetivo", "Entorno de trabajo", "Qué vas a practicar"],
        [[
            "Aprender el ciclo de vida de imágenes y contenedores, y cómo Kubernetes declara, expone, escala y conserva servicios.",
            "Equipo o pendrive USB 3.x con Ubuntu (22.04 / 24.04 LTS) o Fedora Workstation instalado, partición o montaje persistente en "
            + c("/srv/k3s-persistente") + ", Docker, K3s y softphone SIP (Linphone).",
            "Construir y publicar imágenes, operar Deployments, Services, PVC, Traefik, Gateway API y servicios de infraestructura."
        ]],
        anchos=["28%", "42%", "30%"]
    )

    d.p("Al finalizar esta guía, vas a ser capaz de:")
    d.lista([
        "configurar Ubuntu o Fedora sobre un medio USB (o disco local) con montajes persistentes optimizados para memoria flash (" + c("noatime") + ") y sin memoria de intercambio (" + c("swap") + "/" + c("zram") + ") para ejecutar Kubernetes;",
        "comprender la arquitectura de " + b("K3s") + " (servidor único con SQLite integrado, " + c("containerd") + ", Flannel VXLAN, CoreDNS y " + c("local-path-provisioner") + ") y cómo persiste el estado del clúster en el pendrive;",
        "desplegar un " + b("registro de contenedores Docker (Registry v2)") + " dentro de K3s y configurar tanto el demonio Docker como " + c("containerd") + " para confiar en él;",
        "construir una imagen propia con " + c("docker build") + ", etiquetarla con " + c("docker tag") + ", publicarla con " + c("docker push") + " hacia el registro del clúster y desplegarla con actualizaciones progresivas (" + c("rolling updates") + ");",
        "operar tres protocolos clásicos de compartición de archivos sobre volúmenes persistentes de Kubernetes: " + b("SFTP (OpenSSH)") + ", " + b("Samba 4 (SMB/CIFS)") + " y " + b("NFSv4") + ";",
        "desplegar una central telefónica " + b("VoIP con Asterisk") + " configurada mediante " + c("ConfigMap") + " (" + c("pjsip.conf") + " y " + c("extensions.conf") + ") y realizar llamadas de prueba entre internos SIP y pruebas de eco;",
        "administrar servicios de desarrollo y monitoreo (" + b("Gitea") + ", " + b("GitLab CE") + " optimizado para poca RAM y " + b("Uptime Kuma") + ") encendiéndolos y apagándolos bajo demanda mediante scripts sin perder los datos."
    ])

    # --- VISION GENERAL ---------------------------------------------------------
    d.h2("VISIÓN GENERAL", "Arquitectura de la guía en el pendrive USB")
    d.p("Todo el entorno de práctica vive dentro de tu sistema Ubuntu o Fedora (o pendrive USB persistente). Al iniciar el entorno, "
        "el directorio " + c("/srv/k3s-persistente") + " aloja tanto la base de datos interna del clúster K3s como los "
        "volúmenes persistentes (" + c("PersistentVolumeClaims") + ") de todos los servicios:")

    d.flujo([
        caja("HOST UBUNTU / FEDORA", "Demonio Docker<br>" + c("docker build / tag / push") + "<br>Clientes: " + c("sftp") + ", " + c("smbclient") + ", " + c("mount.nfs4") + ", Linphone", AZUL),
        "NodePort / Traefik",
        caja("CLÚSTER K3S (namespace: lab-so)",
             chip("Traefik :80/:443", AZUL) + chip("Registro :30500", AZUL) + chip("SFTP :30022", VERDE) + chip("Samba :30445", TEAL) +
             chip("NFSv4 :30049", AMBAR) + chip("Asterisk :5060", ROSA) + chip("Gitea :30300", PURP) +
             chip("GitLab :30080", BOSQUE) + chip("Panel :30301", AZUL), VERDE),
        "local-path PVC",
        caja("MONTAJE PERSISTENTE USB", c("/srv/k3s-persistente/k3s") + " (estado y containerd)<br>" +
             c("/srv/k3s-persistente/pv") + " (volúmenes de cada servicio)", AMBAR)
    ])

    d.tabla(
        ["Servicio en K3s", "Imagen base", "Puerto expuesto", "Volumen persistente (PVC)", "Credenciales / Acceso inicial"],
        [
            [b("Registro Docker"), c("registry:2"), c("30500/tcp") + " (NodePort)", c("registro-pvc") + " (1 GiB)", c("http://localhost:30500/v2/_catalog")],
            [b("App de ejemplo"), c("localhost:30500/utec/mi-app:v1"), c("80/tcp") + " (ClusterIP)", "Sin estado (2 réplicas)", c("http://localhost/") + " mediante Traefik/Gateway"],
            [b("SFTP (OpenSSH)"), c("atmoz/sftp:alpine"), c("30022/tcp") + " (NodePort)", c("sftp-pvc") + " (512 MiB)", "Usuario " + c("alumno") + " / Clave " + c("utec2026")],
            [b("Samba 4 (SMB)"), c("dperson/samba:latest"), c("30445/tcp") + " (NodePort)", c("samba-pvc") + " (512 MiB)", "Recursos " + c("compartido") + " (" + c("alumno") + "/" + c("utec2026") + ") y " + c("publico")],
            [b("Servidor NFSv4"), c("itsthenetwork/nfs-server-alpine"), c("30049/tcp") + " (NodePort)", c("nfs-pvc") + " (512 MiB)", "Exportación raíz " + c("/") + " con permisos " + c("rw,no_root_squash")],
            [b("Asterisk VoIP"), c("andrius/asterisk:latest"), c("5060/udp,tcp") + " + RTP " + c("10000-10020/udp"), "Configuración mediante " + c("asterisk-config") + " (ConfigMap)", "Internos " + c("1001") + ", " + c("1002") + ", " + c("1003") + " (clave " + c("utecvoip") + ") · Pruebas: " + c("600") + ", " + c("601") + ", " + c("602")],
            [b("Gitea (Git liviano)"), c("gitea/gitea:1.22"), c("30300/tcp") + " (HTTP) y " + c("30023/tcp") + " (SSH)", c("gitea-pvc") + " (1 GiB)", "Usuario " + c("alumno") + " / Clave " + c("utec2026")],
            [b("GitLab CE"), c("gitlab/gitlab-ce:17.11.0-ce.0"), c("30080/tcp") + " (HTTP) y " + c("30024/tcp") + " (SSH)", c("gitlab-datos-pvc") + " (4 GiB)", "Usuario " + c("root") + "; clave inicial generada por GitLab"],
            [b("Panel Uptime Kuma"), c("louislam/uptime-kuma:1"), c("30301/tcp") + " (NodePort)", c("panel-pvc") + " (512 MiB)", c("http://localhost:30301")]
        ]
    )

    d.h2("ANTES DE EMPEZAR", "Usar un segundo pendrive para ampliar el espacio persistente", AMBAR)
    d.p("Si utilizás un USB para el sistema y el espacio libre no alcanza, conectá un segundo pendrive o SSD USB: será el almacenamiento persistente del clúster y no modifica la partición de arranque. <strong>Verificá muy cuidadosamente el dispositivo</strong> antes de formatearlo; el siguiente procedimiento borra solo el segundo pendrive elegido.")
    d.code("""# Identificar ambos dispositivos por tamaño, modelo y punto de montaje
lsblk -o NAME,SIZE,MODEL,FSTYPE,MOUNTPOINTS

# Ejemplo: el segundo pendrive es /dev/sdb (CONFIRMAR antes de ejecutar)
sudo umount /dev/sdb1 2>/dev/null || true
sudo wipefs -a /dev/sdb
sudo parted -s /dev/sdb mklabel gpt mkpart primary ext4 1MiB 100%
sudo mkfs.ext4 -F -L K3S_DATOS /dev/sdb1

# Instalar usando esa partición: el script registra UUID y no depende de /dev/sdb1
sudo ./scripts/instalar-k3s-usb.sh /dev/sdb1
df -h /srv/k3s-persistente""", "AMPLIACIÓN CON OTRO PENDRIVE")
    d.nota("Qué guarda el segundo pendrive", "K3s ubica su estado, imágenes y volúmenes en " + c("/srv/k3s-persistente") + ". Los PVC de " + c("local-path") + " son directorios locales: los tamaños declarados son cuotas solicitadas y no se reservan por adelantado; el consumo real aumenta con los datos escritos.", AMBAR)

    # --- PARTE 1: PREPARACION DEL USB Y K3S -------------------------------------
    d.h2("PARTE 1", "Preparación de Ubuntu / Fedora e instalación de K3s")
    d.p("Cuando ejecutamos un sistema operativo completo y un orquestador de contenedores sobre un pendrive USB o máquina local, debemos "
        "cuidar tres aspectos de arquitectura de sistemas operativos:")
    d.lista([
        b("Desgaste y latencia de memoria flash:") + " montamos la partición de datos con las opciones " + c("noatime,commit=60") + " en " + c("/etc/fstab") + " para evitar una escritura en el inodo por cada lectura de archivo y agrupar confirmaciones del journal de " + c("ext4") + ".",
        b("Desactivación de Swap y ZRAM:") + " Tanto Ubuntu como Fedora configuran mecanismos de intercambio (swapfile o zram0). El " + c("kubelet") + " de Kubernetes exige que el intercambio esté desactivado para garantizar un comportamiento determinista de los límites de memoria (" + c("cgroups") + ").",
        b("Persistencia unificada en ") + c("/srv/k3s-persistente") + ":" + " configuramos K3s mediante " + c("/etc/rancher/k3s/config.yaml") + " con " + c("data-dir: /srv/k3s-persistente/k3s") + " y " + c("default-local-storage-path: /srv/k3s-persistente/pv") + ". Así, aunque cambies de computadora, llevás todo el clúster y sus volúmenes en el bolsillo."
    ])

    d.h3("1.1. Clonar el repositorio y ejecutar el instalador automatizado")
    d.p("Si tu pendrive tiene una partición dedicada para datos, etiquetala como " + c("K3S_DATOS") + " (o pasale el dispositivo como argumento al script). Si instalaste en una única partición raíz (en USB o en disco local), el script usará directamente " + c("/srv/k3s-persistente") + " sobre esa partición:")
    d.code("""git clone https://github.com/jplorier/k3_lab.git
cd k3_lab

# Opción A: usando el directorio /srv/k3s-persistente en la partición actual
sudo ./scripts/instalar-k3s-usb.sh

# Opción B: indicando una partición dedicada del USB (por ejemplo /dev/sdb4)
# sudo ./scripts/instalar-k3s-usb.sh /dev/sdb4

# Aplicar el grupo docker a tu sesión actual sin cerrar la terminal
newgrp docker""", "TERMINAL EN UBUNTU O FEDORA")

    d.h3("1.2. Verificar los archivos de configuración aplicados")
    d.p("Inspeccioná cómo quedaron configurados K3s y su motor de contenedores para usar el montaje persistente y confiar en el registro local que correrá en el puerto " + c("30500") + ":")
    d.code("""cat /etc/rancher/k3s/config.yaml
cat /etc/rancher/k3s/registries.yaml
cat /etc/docker/daemon.json
kubectl get nodes -o wide
df -h /srv/k3s-persistente""", "VERIFICACIÓN DEL ENTORNO")

    d.tarea("TAREA 1.1", "Verificá con " + c("swapon --show") + " que no haya memoria de intercambio activa, con " + c("kubectl get nodes") + " que el nodo figure en estado " + c("Ready") + " y con " + c("kubectl get pods -n lab-so") + " que el Pod del registro local (" + c("registro") + ") ya esté en ejecución.")
    d.informe("Ejecutá " + c("kubectl get nodes -o wide") + " y " + c("df -h /srv/k3s-persistente") + "; distinguí el directorio " + c("/srv/k3s-persistente/k3s") + " de " + c("/srv/k3s-persistente/pv") + ".")

    # --- PARTE 2: DOCKER BUILD, TAG, PUSH Y REGISTRO EN K3S ---------------------
    d.h2("PARTE 2", "Construcción de imágenes Docker (build, tag, push) y Registro en K3s", VERDE)
    d.p("En lugar de subir imágenes a Docker Hub en Internet, ejecutamos nuestro propio " + b("registro de contenedores (Docker Registry v2)") + " como un Pod dentro de K3s, expuesto en " + c("localhost:30500") + " y respaldado por un volumen persistente en el USB (" + c("registro-pvc") + ").")

    d.flujo([
        caja("1. DOCKER BUILD", c("docker build -t mi-app:v1 ./app-ejemplo") + "<br>Crea las capas a partir del " + c("Dockerfile"), AZUL),
        "docker tag",
        caja("2. DOCKER TAG", c("localhost:30500/utec/mi-app:v1") + "<br>Asocia el prefijo del registro destino", AMBAR),
        "docker push",
        caja("3. REGISTRO K3S", "Pod " + c("registro") + " (:30500)<br>Guarda capas en " + c("registro-pvc"), VERDE),
        "containerd pull",
             caja("4. DESPLIEGUE K3S", "Deployment " + c("mi-app") + " (2 réplicas)<br>Expuesto en " + c("http://localhost/") + " por Traefik", PURP)
    ])

    d.h3("2.1. Inspeccionar el Dockerfile y construir la imagen (docker build)", VERDE)
    d.p("En el directorio " + c("app-ejemplo/") + " tenés una aplicación web servida con Nginx que inyecta al arrancar el nombre del Pod, su IP interna de red CNI y la versión de la imagen:")
    d.code("""cat app-ejemplo/Dockerfile
cat app-ejemplo/entrypoint-info.sh

# 1. Construir la imagen local con la etiqueta mi-app:v1
docker build --build-arg VERSION_APP=v1 -t mi-app:v1 ./app-ejemplo

# Verificar que la imagen existe en el almacén local de Docker
docker images mi-app""", "PASO 1: DOCKER BUILD")

    d.h3("2.2. Etiquetar (docker tag) y publicar (docker push) en el registro de K3s", VERDE)
    d.p("En Docker, el comando " + c("docker push") + " determina a qué servidor enviar la imagen leyendo el prefijo del nombre de la etiqueta (" + c("HOST:PUERTO/REPOSITORIO:TAG") + "). Por eso primero creamos un alias con " + c("docker tag") + " apuntando a " + c("localhost:30500") + ":")
    d.code("""# Asegurar que el registro de K3s esté encendido
./scripts/encender.sh registro

# 2. Etiquetar la imagen apuntando al registro local en el puerto 30500
docker tag mi-app:v1 localhost:30500/utec/mi-app:v1

# 3. Subir las capas al registro que corre dentro de K3s
docker push localhost:30500/utec/mi-app:v1

# 4. Consultar la API HTTP v2 del registro para comprobar que quedó almacenada
curl -s http://localhost:30500/v2/_catalog
curl -s http://localhost:30500/v2/utec/mi-app/tags/list""", "PASOS 2 Y 3: DOCKER TAG Y DOCKER PUSH")

    d.h3("2.3. Desplegar en Kubernetes y realizar una actualización progresiva (v2)", VERDE)
    d.p("Ahora apliquemos el manifiesto " + c("app-ejemplo/despliegue.yaml") + ", que crea un " + c("Deployment") + " con 2 réplicas descargando la imagen desde " + c("localhost:30500/utec/mi-app:v1") + ". La aplicación queda como " + c("ClusterIP") + ": se expone de manera controlada mediante Traefik y Gateway API.")
    d.code("""kubectl apply -f app-ejemplo/despliegue.yaml
kubectl rollout status deployment/mi-app -n lab-so
kubectl get pods -n lab-so -l app=mi-app -o wide

# Comprobar qué Pod responde en cada petición (balanceo de carga del Service)
curl -s http://localhost/ | grep -E "Versi|Pod que|IP interna"
curl -s http://localhost/ | grep -E "Versi|Pod que|IP interna""", "DESPLIEGUE DE LA VERSIÓN v1")

    d.p("También contás con el script " + c("./scripts/construir-y-publicar.sh") + " que automatiza todo el ciclo. Modificá algún texto en " + c("app-ejemplo/sitio/index.html") + " y publicá la versión " + c("v2") + ":")
    d.code("""# Construir, etiquetar, hacer push de v2 y actualizar el Deployment sin caída del servicio
./scripts/construir-y-publicar.sh v2

# Verificar en el registro que ahora conviven los tags v1 y v2
curl -s http://localhost:30500/v2/utec/mi-app/tags/list""", "ACTUALIZACIÓN A LA VERSIÓN v2")

    d.tarea("TAREA 2.1", "Modificá " + c("app-ejemplo/sitio/index.html") + " agregando los nombres de los integrantes del grupo, construí y publicá la etiqueta " + c("localhost:30500/utec/mi-app:v2") + " y actualizá el Deployment en K3s.")
    d.informe("Observá la salida de " + c("docker push") + ", la respuesta JSON de " + c("http://localhost:30500/v2/utec/mi-app/tags/list") + " y recargá " + c("http://localhost/") + " para identificar los Pod que responden.")

    d.h3("2.4. Exponer servicios HTTP con Traefik, Ingress y Gateway API", VERDE)
    d.p("K3s instala Traefik y ServiceLB por defecto. ServiceLB publica los puertos " + c("80") + " y " + c("443") + " del host; Traefik recibe el tráfico y lo balancea hacia Services internos. El instalador habilita el proveedor Gateway API de Traefik e instala sus CRD. El manifiesto " + c("manifiestos/09-gateway/gateway.yaml") + " declara un " + c("GatewayClass") + ", un " + c("Gateway") + " llamado " + c("entrada-web") + " y una " + c("HTTPRoute") + " hacia " + c("mi-app") + ".")
    d.code("""# Aplicar o revisar el punto de entrada y la ruta HTTP
./scripts/encender.sh gateway
kubectl get svc -n kube-system traefik
kubectl get gatewayclass
kubectl get gateway,httproute -n lab-so
kubectl describe httproute mi-app -n lab-so

# La ruta / llega al Service ClusterIP mi-app sin abrir un NodePort propio
curl -s http://localhost/ | grep -E "Versi|Pod que|IP interna""" , "TRAEFIK Y GATEWAY API")
    d.nota("Ingress clásico y Gateway API", "Traefik también procesa recursos " + c("Ingress") + ". En esta guía se usa Gateway API porque separa claramente la clase de controlador, el punto de entrada (Gateway) y el enrutamiento (HTTPRoute), y permite extender luego a TLS, TCPRoute o políticas de backend.", VERDE)

    # --- PARTE 3: COMPARTICION DE ARCHIVOS (SFTP, SAMBA 4, NFS) -----------------
    d.h2("PARTE 3", "Servicios de archivos persistentes: SFTP, Samba 4 y NFSv4", TEAL)
    d.p("En esta sección comparamos en la práctica los tres protocolos de red más utilizados en la industria para compartir archivos, todos ejecutándose como contenedores dentro de K3s con sus datos almacenados en el pendrive USB.")

    d.h3("3.1. Servidor SFTP (OpenSSH) en el puerto 30022", TEAL)
    d.p("SFTP opera sobre un único canal TCP cifrado con SSH (no confundir con FTPS). Nuestro despliegue utiliza un " + c("initContainer") + " para inicializar los permisos del volumen " + c("sftp-pvc") + " (UID/GID " + c("1001") + ") sin romper la jaula " + c("chroot") + " de OpenSSH:")
    d.code("""./scripts/encender.sh sftp

# Conectarse por línea de comandos (contraseña: utec2026)
sftp -P 30022 alumno@localhost <<EOF
cd datos
ls -la
put README.md README-subido-por-sftp.md
ls -la
bye
EOF""", "PRUEBA DE SFTP")

    d.h3("3.2. Servidor Samba 4 (SMB/CIFS) en el puerto 30445", TEAL)
    d.p("Samba 4 implementa el protocolo SMB/CIFS nativo de Windows y soportado en Linux y macOS. El manifiesto " + c("manifiestos/03-samba/samba.yaml") + " configura dos recursos compartidos sobre el volumen " + c("samba-pvc") + ": " + c("compartido") + " (requiere usuario " + c("alumno") + " y clave " + c("utec2026") + ") y " + c("publico") + " (acceso de invitado):")
    d.code("""./scripts/encender.sh samba

# Listar los recursos compartidos disponibles en el servidor Samba 4
smbclient -L //localhost -p 30445 -U alumno%utec2026

# Subir y listar un archivo en el recurso autenticado 'compartido'
smbclient //localhost/compartido -p 30445 -U alumno%utec2026 -c "put README.md; ls"

# Opcional: montar el recurso SMB en un directorio local del host
sudo mkdir -p /mnt/samba
sudo mount -t cifs //localhost/compartido /mnt/samba -o port=30445,username=alumno,password=utec2026,uid=$(id -u),gid=$(id -g)
ls -la /mnt/samba
sudo umount /mnt/samba""", "PRUEBA DE SAMBA 4")

    d.h3("3.3. Servidor NFSv4 en el puerto 30049", TEAL)
    d.p("NFSv4 es el estándar nativo de sistemas UNIX/Linux para montar árboles de directorios remotos a través del VFS del núcleo. A diferencia de NFSv3, NFSv4 concentra el tráfico en un único puerto TCP (" + c("2049") + ", expuesto como NodePort " + c("30049") + ") sin depender de puertos efímeros de " + c("rpc.mountd") + ":")
    d.code("""./scripts/encender.sh nfs

# Montar la exportación raíz NFSv4 en /mnt/nfs desde el host
sudo mkdir -p /mnt/nfs
sudo mount -t nfs4 -o port=30049,vers=4 localhost:/ /mnt/nfs

# Verificar el archivo de bienvenida y crear un archivo persistente
cat /mnt/nfs/LEAME-NFS.txt
echo "Escrito desde el host $(date)" | sudo tee /mnt/nfs/prueba-nfs.txt
ls -la /mnt/nfs

# Desmontar al terminar la prueba
sudo umount /mnt/nfs""", "PRUEBA DE NFSV4")

    d.tarea("TAREA 3.1", "Subí un archivo por SFTP, otro por Samba 4 y otro por NFSv4. Luego ejecutá " + c("sudo ls -la /srv/k3s-persistente/pv/") + " en la terminal y localizá en qué carpeta física del pendrive USB quedó almacenado cada uno.")
    d.informe("Compará en una tabla SFTP, Samba 4 y NFSv4 indicando: protocolo de transporte, mecanismo de autenticación, si requiere soporte en el núcleo del cliente y en qué escenario elegirías cada uno.")

    # --- PARTE 4: TELEFONIA VOIP CON ASTERISK -----------------------------------
    d.h2("PARTE 4", "Central Telefónica VoIP con Asterisk en Kubernetes", ROSA)
    d.p("La voz sobre IP (VoIP) separa la " + b("señalización") + " (protocolo SIP en el puerto " + c("5060/udp,tcp") + ", que establece y corta la llamada) del " + b("flujo multimedia de audio") + " (protocolo RTP en los puertos " + c("10000-10020/udp") + "). Como SIP incluye las direcciones IP y puertos RTP dentro de la carga útil SDP, el NAT de Kubernetes suele cortar el audio si no se configura con cuidado. Por eso en " + c("manifiestos/05-asterisk/asterisk.yaml") + " utilizamos " + c("hostNetwork: true") + " junto con " + c("rtp_symmetric=yes") + " y montamos las configuraciones mediante " + c("subPath") + " desde un " + c("ConfigMap") + ".")

    d.tabla(
        ["Número / Interno", "Función configurada en extensions.conf", "Usuario / Clave SIP"],
        [
            [c("1001"), "Interno del Alumno 1", "Usuario: " + c("1001") + " · Clave: " + c("utecvoip")],
            [c("1002"), "Interno del Alumno 2", "Usuario: " + c("1002") + " · Clave: " + c("utecvoip")],
            [c("1003"), "Interno del Alumno 3", "Usuario: " + c("1003") + " · Clave: " + c("utecvoip")],
            [c("600"), "Prueba de eco en vivo (" + c("Echo()") + "): hablás al micrófono y te escuchás en tiempo real", "Marcado desde cualquier interno"],
            [c("601"), "Mensaje de bienvenida grabado (" + c("hello-world") + " + " + c("demo-congrats") + ")", "Marcado desde cualquier interno"],
            [c("602"), "Locución automática de los dígitos " + c("2-0-2-6") + " (" + c("SayDigits(2026)") + ")", "Marcado desde cualquier interno"]
        ],
        color=ROSA
    )

    d.h3("4.1. Encender Asterisk e inspeccionar la consola CLI de la central", ROSA)
    d.code("""./scripts/encender.sh asterisk

# Ver los endpoints PJSIP configurados y el plan de marcado directamente en Asterisk
kubectl exec -n lab-so deploy/asterisk -- asterisk -rx "pjsip show endpoints"
kubectl exec -n lab-so deploy/asterisk -- asterisk -rx "dialplan show laboratorio-utec\"""", "VERIFICACIÓN DE LA CENTRAL ASTERISK")

    d.h3("4.2. Conectarse con un Softphone SIP (Linphone) y realizar llamadas", ROSA)
    d.p("Podés instalar " + b("Linphone") + " en tu sistema (" + c("sudo apt install -y linphone") + " en Ubuntu o " + c("sudo dnf install -y linphone") + " en Fedora) o usar una app SIP en tu celular conectado a la misma red:")
    d.lista([
        "Abrí Linphone y elegí " + b("Usar una cuenta SIP") + ".",
        "Completá: Usuario " + c("1001") + ", Dominio SIP " + c("localhost:5060") + " (o la IP de la PC en la LAN si llamás desde otra máquina), Contraseña " + c("utecvoip") + ", Transporte " + c("UDP") + ".",
        "Marcá el número " + c("600") + " para realizar la prueba de eco o " + c("601") + " para escuchar la grabación de bienvenida.",
        "Registrá un segundo cliente con el interno " + c("1002") + " y realizá una llamada entre " + c("1001") + " y " + c("1002") + "."
    ], ordenada=True)

    d.tarea("TAREA 4.1", "Agregá en " + c("manifiestos/05-asterisk/asterisk.yaml") + " un interno " + c("1004") + " y una extensión " + c("603") + " que diga los últimos 4 dígitos de tu cédula con " + c("SayDigits()") + ". Aplicá el cambio con " + c("kubectl apply") + " y recargá el plan de marcado con " + c("kubectl exec -n lab-so deploy/asterisk -- asterisk -rx 'dialplan reload'") + ".")
    d.informe("Consultá " + c("pjsip show endpoints") + " con al menos un interno registrado (" + c("Not in use") + " o " + c("In use") + ") y explicá por qué SIP usa dos protocolos distintos (SIP y RTP).")

    # --- PARTE 5: SERVIDORES GIT (GITEA Y GITLAB CE) + PANEL --------------------
    d.h2("PARTE 5", "Servidores Git (Gitea y GitLab CE) y Panel de Monitoreo", PURP)
    d.p("El entorno incluye dos plataformas Git completas y un sistema de monitoreo:")
    d.lista([
        b("Gitea (puerto 30300):") + " servidor Git liviano escrito en Go (~150 MB de RAM), ideal para mantener encendido todo el tiempo en un pendrive USB. Ya viene preconfigurado con el usuario administrador " + c("alumno") + " y contraseña " + c("utec2026") + ".",
        b("GitLab CE (puerto 30080):") + " la suite empresarial completa de GitLab Omnibus. Como por defecto consume más de 6 GB de RAM, en " + c("manifiestos/07-gitlab/gitlab.yaml") + " está ajustada mediante " + c("GITLAB_OMNIBUS_CONFIG") + " (" + c("puma['worker_processes'] = 0") + ", " + c("prometheus_monitoring['enable'] = false") + ") para correr en ~2.2 GB de RAM. GitLab genera la clave inicial de " + c("root") + " dentro del Pod; no queda en este repositorio.",
        b("Uptime Kuma (puerto 30301):") + " panel visual para monitorear en tiempo real que el Registro, SFTP, Samba, NFS, Asterisk y Gitea estén activos."
    ])

    d.code("""# Encender Gitea y el panel de monitoreo (livianos, incluidos en 'basicos')
./scripts/encender.sh gitea
./scripts/encender.sh panel

# Crear y subir un repositorio de prueba al servidor Gitea local
git clone http://localhost:30300/alumno/prueba.git 2>/dev/null || true

# Opcional (en PCs con 8 GB o más de RAM): encender GitLab CE
# Nota: apagá antes servicios que no uses y esperá 3 a 5 minutos en el primer arranque
./scripts/encender.sh gitlab""", "USO DE GITEA, GITLAB CE Y EL PANEL")

    d.code("""# Obtener la clave inicial de GitLab una vez que el Pod esté Ready
kubectl exec -n lab-so deploy/gitlab -- cat /etc/gitlab/initial_root_password

# Cambiala al iniciar sesión y no la copies al repositorio.""", "CLAVE INICIAL DE GITLAB")

    # --- PARTE 6: SCRIPTS DE ENCENDIDO, APAGADO Y PERSISTENCIA ------------------
    d.h2("PARTE 6", "Gestión de energía de servicios y verificación de persistencia en USB", AMBAR)
    d.p("Todos los servicios cuentan con scripts en " + c("scripts/") + " para encenderlos, apagarlos liberando memoria RAM sin borrar sus volúmenes del pendrive USB, consultar su estado y detener de forma segura el motor K3s antes de desconectar el USB:")

    d.code("""# 1. Ver el estado completo del USB, nodo, Pods, PVCs y tabla de conexiones
./scripts/estado.sh

# 2. Ejecutar las pruebas automáticas de salud de todos los servicios
./scripts/probar-servicios.sh

# 3. Apagar un servicio puntual (escala a 0 réplicas; sus datos siguen en el USB)
./scripts/apagar.sh gitlab
./scripts/apagar.sh samba

# 4. Volver a encender Samba y comprobar que los archivos subidos siguen intactos
./scripts/encender.sh samba
smbclient //localhost/compartido -p 30445 -U alumno%utec2026 -c "ls"

# 5. Al terminar la clase: apagar todos los servicios, detener K3s y ejecutar sync en el USB
./scripts/apagar.sh todos --motor""", "COMANDOS DE OPERACIÓN Y APAGADO SEGURO")

    d.nota("Cuidado al desconectar el pendrive USB",
           "Nunca retires el pendrive USB en caliente mientras los contenedores o la base de datos de K3s están escribiendo. "
           "Ejecutá siempre primero " + c("./scripts/apagar.sh todos --motor") + " o apagá el sistema desde el menú del escritorio.",
           AMBAR)

    # --- PREGUNTAS DE AUTOEVALUACION --------------------------------------------
    d.h2("AUTOEVALUACIÓN", "Preguntas de repaso de la guía", BOSQUE)
    preguntas = [
        ("¿Por qué Kubernetes exige desactivar la memoria swap (incluyendo zram / swapfile)?",
         "El planificador de Kubernetes asigna Pods a los nodos según sus solicitudes y límites de memoria RAM (" + c("requests") + " y " + c("limits") + " gobernados por " + c("cgroups") + "). Si el núcleo envía páginas de un contenedor a swap, el aislamiento de rendimiento se vuelve impredecible y un contenedor que excede su memoria tarda mucho más en ser detectado por el OOM Killer."),
        ("¿Por qué montamos la partición persistente del pendrive USB con las opciones " + c("noatime,commit=60") + "?",
         "Las memorias flash NAND de los pendrives USB tienen una cantidad limitada de ciclos de borrado/escritura y alta latencia en escrituras pequeñas aleatorias. Con " + c("noatime") + " el sistema de archivos no escribe en el disco cada vez que se lee un archivo, y con " + c("commit=60") + " agrupa las confirmaciones del journal de " + c("ext4") + " cada 60 segundos."),
        ("¿Qué hace exactamente el comando " + c("docker tag mi-app:v1 localhost:30500/utec/mi-app:v1") + "? ¿Duplica el espacio en disco?",
         "No duplica ningún byte de las capas de la imagen: solo crea una nueva referencia (puntero) al mismo identificador SHA256 de imagen que incluye en su nombre la dirección y puerto del registro de destino (" + c("localhost:30500") + ") para que " + c("docker push") + " sepa a qué servidor enviarla."),
        ("¿Por qué fue necesario configurar tanto " + c("/etc/docker/daemon.json") + " como " + c("/etc/rancher/k3s/registries.yaml") + "?",
         "Porque intervienen dos demonios distintos: el comando " + c("docker push") + " lo ejecuta el demonio de Docker (que lee " + c("/etc/docker/daemon.json") + "), mientras que cuando K3s despliega el Pod de la aplicación, quien descarga la imagen desde el registro es " + c("containerd") + " integrado en K3s (que lee " + c("/etc/rancher/k3s/registries.yaml") + ")."),
        ("¿Qué ocurre con los archivos subidos a SFTP, Samba o NFS cuando ejecutás " + c("./scripts/apagar.sh todos") + "?",
         "No se pierde nada: el script escala los " + c("Deployments") + " a " + c("0") + " réplicas, lo que detiene y elimina los Pods liberando CPU y RAM, pero conserva intactos los " + c("PersistentVolumeClaims") + " y sus directorios físicos en " + c("/srv/k3s-persistente/pv") + ". Al ejecutar " + c("./scripts/encender.sh") + ", los nuevos Pods vuelven a montar esos mismos volúmenes."),
        ("¿Por qué el despliegue de Asterisk utiliza " + c("hostNetwork: true") + " y montajes con " + c("subPath") + "?",
         "El protocolo SIP inserta direcciones IP y puertos UDP dinámicos para el audio RTP dentro de los mensajes de control SDP. Con " + c("hostNetwork: true") + " evitamos la doble traducción de direcciones (NAT) en los paquetes RTP de voz. El uso de " + c("subPath") + " permite reemplazar únicamente " + c("pjsip.conf") + ", " + c("rtp.conf") + " y " + c("extensions.conf") + " sin ocultar el resto de los archivos originales de " + c("/etc/asterisk") + ".")
    ]
    for i, (q, r) in enumerate(preguntas, 1):
        d.pregunta(i, q, r)

    d.guardar("moodle/laboratorio_k3s_so_moodle.html")


def generar_guia_fedora_usb():
    d = DocMoodle()
    d.portada(
        "GUÍA TÉCNICA · SISTEMAS OPERATIVOS",
        "Instalación de Fedora Workstation en Pendrive USB con Partición Persistente para K3s",
        "Procedimiento paso a paso para preparar el pendrive USB booteable con Fedora Workstation, "
        "esquema de particiones recomendado y ajustes de rendimiento para memoria flash.",
        color=VERDE
    )

    d.h2("PASO 0", "Si el USB de arranque tiene poco espacio, usar un segundo USB para K3s", AMBAR)
    d.p("No es necesario que el USB que contiene Fedora tenga 32 GB si disponés de otro pendrive o SSD USB para los datos de K3s. El segundo dispositivo se monta de forma persistente en " + c("/srv/k3s-persistente") + ". Elegílo por modelo y tamaño con " + c("lsblk") + "; no continúes si no podés identificarlo con certeza.")
    d.code("""# Ejemplo: solo después de confirmar que /dev/sdb es el USB adicional
sudo wipefs -a /dev/sdb
sudo parted -s /dev/sdb mklabel gpt mkpart primary ext4 1MiB 100%
sudo mkfs.ext4 -F -L K3S_DATOS /dev/sdb1
sudo ./scripts/instalar-k3s-usb.sh /dev/sdb1""", "USB ADICIONAL PARA DATOS")

    d.h2("PASO 1", "Requisitos y esquema de particiones recomendado en el USB", VERDE)
    d.p("Para trabajar con fluidez ejecutando contenedores y K3s desde un medio extraíble se recomienda utilizar un " + b("pendrive USB 3.1/3.2 o SSD externo USB de al menos 32 GB (ideal 64 GB)") + ".")
    d.tabla(
        ["Partición", "Tamaño sugerido (USB 64 GB)", "Sistema de archivos", "Punto de montaje / Etiqueta", "Propósito"],
        [
            [c("1 (EFI)"), "600 MiB", c("FAT32"), c("/boot/efi"), "Arranque UEFI en cualquier PC compatible"],
            [c("2 (Boot)"), "1 GiB", c("ext4"), c("/boot"), "Kernels de Fedora e imágenes initramfs"],
            [c("3 (Root)"), "25 GiB", c("ext4") + " (sin swap)", c("/"), "Sistema base Fedora Workstation y paquetes"],
            [b("4 (Datos K3s)"), "Resto (~35 GiB)", c("ext4") + " (" + c("LABEL=K3S_DATOS") + ")", c("/srv/k3s-persistente"), "Almacén de K3s, imágenes Docker y volúmenes persistentes"]
        ],
        color=VERDE
    )

    d.h2("PASO 2", "Instalación de Fedora Workstation sobre el pendrive destino", AZUL)
    d.lista([
        "Grabá la ISO de " + b("Fedora Workstation Live") + " en un pendrive instalador temporal usando " + b("Fedora Media Writer") + " o " + c("dd") + ".",
        "Conectá tanto el pendrive instalador como el pendrive USB rápido donde quedará instalado tu sistema y arrancá la PC desde el instalador.",
        "En el instalador " + b("Anaconda") + ", seleccioná " + b(" exclusivamente el pendrive destino") + " y elegí " + b("Configuración de almacenamiento personalizada") + " (usando particiones estándar " + c("ext4") + " en lugar de Btrfs para minimizar la amplificación de escritura en memorias USB económicas).",
        "Creá la cuarta partición con etiqueta " + c("K3S_DATOS") + " montada en " + c("/srv/k3s-persistente") + " (o si preferís una única partición raíz " + c("/") + ", el script " + c("instalar-k3s-usb.sh") + " creará automáticamente " + c("/srv/k3s-persistente") + " allí)."
    ], ordenada=True)

    d.h2("PASO 3", "Inicialización automática del entorno", TEAL)
    d.p("Una vez que arranques Fedora Workstation desde tu pendrive USB, abrí una terminal y ejecutá:")
    d.code("""# En Ubuntu: sudo apt update && sudo apt install -y git
# En Fedora: sudo dnf install -y git
git clone https://github.com/jplorier/k3_lab.git ~/k3_lab
cd ~/k3_lab
sudo ./scripts/instalar-k3s-usb.sh
newgrp docker
./scripts/encender.sh basicos
./scripts/estado.sh""", "PUESTA EN MARCHA INICIAL")

    d.guardar("moodle/guia_fedora_usb_moodle.html")


if __name__ == "__main__":
    generar_enunciado_principal()
    generar_guia_fedora_usb()
