# Debian ↔ Android Assistant Bridge

Sistema de comunicación diseñado para conectar un equipo **Debian/Linux** que ejecuta un asistente virtual con un **dispositivo Android**, permitiendo que ambos dispositivos se comuniquen a través de Internet independientemente de su ubicación física.

## Arquitectura inicial

```text
                         INTERNET
                             │
             ┌───────────────┴───────────────┐
             │                               │
             ▼                               ▼
      ┌──────────────┐                ┌──────────────┐
      │   ANDROID    │                │    DEBIAN    │
      │              │                │              │
      │ Mobile App   │                │ Assistant    │
      │              │                │ Core         │
      └──────┬───────┘                └──────┬───────┘
             │                               │
             │          WSS / TLS            │
             │                               │
             └──────────────┬────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   GATEWAY /   │
                    │    RELAY      │
                    │               │
                    │ Authentication│
                    │ Routing       │
                    │ Sessions      │
                    └───────────────┘
```

## Objetivo

El proyecto busca proporcionar una capa de comunicación entre un ordenador Debian y un dispositivo Android.

El ordenador funciona como el **núcleo de procesamiento**, mientras que el teléfono funciona como un **dispositivo de acceso e interfaz remota**.

La conexión debe funcionar aunque ambos dispositivos se encuentren en redes diferentes o en ubicaciones geográficas distintas.

### Ejemplo

```text
┌─────────────────┐                         ┌─────────────────┐
│     ANDROID     │                         │     DEBIAN      │
│                 │                         │                 │
│  Mobile App     │                         │ Assistant Core  │
│  User Interface │                         │ AI / Services   │
│                 │                         │                 │
└────────┬────────┘                         └────────┬────────┘
         │                                           │
         │                                           │
         └────────────── INTERNET ───────────────────┘
                              │
                              ▼
                       ┌────────────┐
                       │   RELAY    │
                       │   SERVER   │
                       └────────────┘
```

## Principios de diseño

### 1. Independencia geográfica

Android y Debian no necesitan encontrarse en la misma red local.

```text
Android
   │
   │ Internet
   ▼
  Relay
   ▲
   │ Internet
   │
Debian
```

### 2. Comunicación segura

La comunicación entre dispositivos utilizará conexiones cifradas mediante **TLS**.

El canal principal de comunicación será:

```text
WebSocket Secure
wss://
```

### 3. Comunicación bidireccional

El sistema debe permitir que ambos dispositivos puedan enviar información en tiempo real.

```text
ANDROID                         DEBIAN

   │                              │
   │────── message ──────────────►│
   │                              │
   │◄────── response ─────────────│
   │                              │
   │◄────── event ────────────────│
   │                              │
   │────── acknowledgement ──────►│
```

### 4. Abstracción de conexión

El núcleo del asistente no debe depender directamente de un método concreto de comunicación.

```text
                 Assistant Core
                       │
                       ▼
               Connection Manager
                       │
          ┌────────────┼────────────┐
          │            │            │
       WebSocket      USB        Local Wi-Fi
          │
          ▼
       Internet
```

El `Assistant Core` solamente debe conocer una interfaz de comunicación.

Esto permite modificar o reemplazar la tecnología de transporte sin modificar la lógica principal del asistente.

## Tecnologías iniciales

### Debian

* Debian Linux
* Python
* FastAPI
* WebSocket
* asyncio
* HTTPS
* TLS
* Git

### Android

* Android
* Kotlin
* Android SDK
* WebSocket client
* HTTPS
* TLS

### Comunicación

* TCP
* WebSocket
* WebSocket Secure (`WSS`)
* HTTPS
* TLS 1.3
* JSON

### Infraestructura

* Relay / Gateway Server
* Authentication
* Device Registration
* Session Management
* Routing

## Arquitectura de comunicación

La comunicación se divide en dos niveles.

### HTTPS

Utilizado para operaciones como:

```text
POST /auth
POST /devices/register
GET  /devices
GET  /status
POST /session
```

### WebSocket

Utilizado para comunicación persistente y eventos en tiempo real:

```text
Android
   ⇅
WebSocket
   ⇅
Relay
   ⇅
WebSocket
   ⇅
Debian
```

## Identificación de dispositivos

Cada dispositivo deberá poseer una identidad lógica dentro del sistema.

Ejemplo:

```json
{
    "device_id": "android-001",
    "type": "android",
    "platform": "android"
}
```

El equipo Debian podrá identificarse de manera equivalente:

```json
{
    "device_id": "debian-001",
    "type": "server",
    "platform": "debian"
}
```

## Seguridad

La seguridad será considerada parte fundamental de la arquitectura.

El sistema deberá contemplar:

* TLS
* autenticación
* autorización
* identificación de dispositivos
* tokens de sesión
* expiración de sesiones
* revocación de dispositivos
* protección contra conexiones no autorizadas
* validación de mensajes
* logs de conexión
* gestión segura de credenciales

El servidor Relay no debería requerir acceso directo al sistema operativo del equipo Debian.

Su función principal será:

```text
Authenticate
     ↓
Identify
     ↓
Route
     ↓
Forward
```

## Estructura prevista

```text
debian-android-bridge/
│
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── CHANGELOG.md
│
├── docs/
│   ├── architecture.md
│   ├── communication.md
│   ├── protocol.md
│   ├── security.md
│   ├── authentication.md
│   ├── deployment.md
│   └── troubleshooting.md
│
├── debian/
│   ├── assistant/
│   ├── connection/
│   ├── api/
│   └── device/
│
├── android/
│   ├── app/
│   ├── connection/
│   └── device/
│
├── relay/
│   ├── gateway/
│   ├── authentication/
│   ├── routing/
│   └── sessions/
│
├── tests/
│
└── scripts/
```

## Roadmap

### Phase 1 — Comunicación local

```text
Android ⇄ Debian
```

Implementación inicial mediante una red local para validar el protocolo.

### Phase 2 — WebSocket

```text
Android ⇄ WebSocket ⇄ Debian
```

Implementación del canal bidireccional persistente.

### Phase 3 — Seguridad

```text
Android ⇄ TLS ⇄ Debian
```

Implementación de autenticación y cifrado.

### Phase 4 — Relay

```text
Android
   ⇅
Relay
   ⇅
Debian
```

Permitir comunicación entre redes diferentes.

### Phase 5 — Identidad y sesiones

Implementación de:

* Device ID
* autenticación
* sesiones
* pairing
* tokens
* revocación

### Phase 6 — Comunicación global

Permitir que Android y Debian funcionen desde redes y ubicaciones independientes.

## Estado del proyecto

> Early Development

La arquitectura y el protocolo de comunicación se encuentran en fase de diseño y validación.
