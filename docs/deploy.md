
![Banner](https://capsule-render.vercel.app/api?type=waving&color=0:3D8EFF,100:0F2847&height=180&section=header&text=Guía%20de%20Despliegue&fontSize=60&fontColor=ffffff&fontAlignY=40&desc=Sitio%20web%20de%20servicios%20de%20ciberseguridad%20construido%20con%20Django&descAlignY=60&descSize=18)

## Tabla de contenidos

- [Descripción](#-descripción)
- [Stack tecnológico](#-stack-tecnológico)
- [Requisitos previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Migraciones y base de datos](#-migraciones-y-base-de-datos)
- [Ejecutar el servidor](#-ejecutar-el-servidor)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Comandos útiles](#-comandos-útiles)
- [Buenas prácticas de contribución](#-buenas-prácticas-de-contribución)

---

## Descripción

**AzkCore** es la plataforma web de seguridad ofensiva. Incluye landing page pública, formulario de contacto, panel de autenticación y módulos internos de escaneo de red y mensajería.

Esta guía está pensada para que cualquier desarrollador del equipo pueda clonar el repositorio y tener el proyecto corriendo localmente en minutos.

---

## Stack tecnológico

| Tecnología | Versión | Uso |
|---|---|---|
| <div align="center"><img src="https://skillicons.dev/icons?i=python" /></div> | 3.14.4 | Lenguaje base |
| <div align="center"><img src="https://skillicons.dev/icons?i=django" /></div> | 6.1 | Framework backend |
|  <div align="center"><img src="https://skillicons.dev/icons?i=sqlite" /></div> | 0.5.5 | Base de datos (desarrollo) se migrara a MySQL|
| <div align="center"><img src="https://skillicons.dev/icons?i=tailwind" /></div> | -------- | Estilos de la interfaz |
| 📦 **pip / venv** | 25.1.1 | Gestión de dependencias y entornos |

---

## Requisitos previos

Antes de empezar, asegurar de tener instalado:

- **Python 3.14.4** (o superior) → [Descargar Python](https://www.python.org/downloads/)
- **pip** (viene incluido con Python)
- **Git** → [Descargar Git](https://git-scm.com/downloads)

Verificar versiones con:

```bash
python3 --version
pip --version
git --version
```

> ⚠️ En algunas distribuciones Linux el comando es `python3`, no `python`. Si `python` no funciona, usa `python3` en todos los comandos de esta guía. En windows es parecido

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/AzkOsDev/Azkcore-Tech-Site.git
cd Azkcore-Tech-Site
```

### 2. Crear y activar el entorno virtual

**Linux / macOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```
> ⚠️ En algunos casos windows restringe las ejecuciones de scripts, para que funcione debe de deshabilitar esta opcion, puede ver un tutorial de como hacerlo en el siguiente link

[Guia para deshabilitar Execution Policy (Windows)](https://www.cdmon.com/es/blog/la-ejecucion-de-scripts-esta-deshabilitada-en-este-sistema-te-contamos-como-actuar)

### 3. Instalar las dependencias

```bash
pip install -r requeriments.txt
```

---


## Migraciones y base de datos

Aplica las migraciones para crear las tablas necesarias en la base de datos:

```bash
python manage.py migrate
```

Crea un superusuario para acceder al panel de administración:

```bash
python manage.py createsuperuser
```
> **IMPORTANTE:** Los usuarios que manejara django son los mismos del login administrativo y del sitio web
---

##  Ejecutar el servidor

```bash
python manage.py runserver
```

El proyecto quedará disponible en:

```
http://127.0.0.1:8000/
```
O
```
http://localhost:8000/
```

Panel de administración de Django:

```
http://127.0.0.1:8000/admin/
http://localhost:8000/admin/
```

---

## Estructura general del proyecto

```
azkcore/
├── apps/
│   ├── accounts/           # Autenticación de usuarios
│   ├── contact/             # Formulario de contacto
│   ├── home/                 # Vistas principales del panel
│   ├── home_functions/
│   │   ├── messages/       # Mensajería interna
│   │   └── scan_network/   # Escaneo de red
│   └── landing/              # Landing page pública
├── azkcore/                  # Configuración del proyecto (settings, urls)
├── static/
│   ├── css/                  # Estilos (style.css, style-form.css)
│   ├── img/                  # Imágenes y logos
│   └── js/                   # Scripts (main.js)
├── templates/
│   ├── accounts/
│   ├── components/
│   │   ├── home/
│   │   └── landing/
│   ├── contact-form/
│   ├── home/
│   └── landing/
├── manage.py
└── requeriments.txt
```

---

## Comandos útiles e importantes

| Comando | Descripción |
|---|---|
| `python manage.py runserver` | Levanta el servidor local |
| `python manage.py makemigrations` | Genera nuevas migraciones tras cambios en modelos |
| `python manage.py migrate` | Aplica las migraciones pendientes |
| `python manage.py createsuperuser` | Crea un usuario administrador |
| `deactivate` | Sale del entorno virtual |

---

## Buenas prácticas de contribución | *TENER EN CUENTA*

1. **Nunca trabajar directo sobre `main`.** Crear una rama nueva para cada feature o fix:
   ```bash
   git switch -c feature/nombre-descriptivo
   ```
   Verificar en que rama se esta trabajando:
      ```bash
   git branch
   ```
2. Haz commits pequeños y descriptivos.
3. Antes de hacer push, verifica que el servidor corre sin errores:
   ```bash
   python manage.py runserver
   ```
4. Sube tu rama con los cambios realizados y el administrador revisara el **Pull Request** hacia `main` — **no hacer push directo a `main`**.
5. Por ultimo nunca elimines una rama sin confirmar que su contenido ya está fusionado completamente.

---

<div align="center">

Hecho con 🖤 por **AzkOsDev**

</div>