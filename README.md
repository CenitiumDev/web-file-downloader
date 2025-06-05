# 📁 Web File Downloader and Organizer

## 🚀 Visión General del Proyecto

Este script de Python es una herramienta de automatización diseñada para monitorear sitios web específicos, identificar enlaces a archivos descargables y organizar automáticamente los archivos descargados en su sistema local. Es ideal para usuarios que necesitan mantener un seguimiento de documentos, informes o cualquier tipo de archivo publicado regularmente en páginas web.

El proyecto demuestra habilidades en:

- Web Scraping con requests y BeautifulSoup.
- Automatización de Tareas y gestión de flujos de trabajo.
- Manejo de Archivos y Directorios con os y shutil.
- Configuración Externa vía archivos JSON para flexibilidad.
- Gestión de Historial de Descargas para evitar duplicados.
- Argumentos de Línea de Comandos con argparse para mayor control.
- Manejo de Errores robusto para una ejecución fiable.

## ✨ Características Principales

- **Descarga Automática**: Escanea las URLs configuradas y descarga archivos con extensiones permitidas.
- **Organización Flexible**: Mueve los archivos descargados a subcarpetas organizadas por:
  - Fecha: `descargas/YYYY-MM-DD/`
  - Tipo de Archivo: `descargas/Pdf/`, `descargas/Zip/`
  - Anidado (Tipo + Fecha): `descargas/Pdf/YYYY-MM-DD/`
- **Prevención de Duplicados**: Mantiene un historial de archivos descargados.
- **Configuración Externa**: Uso de `config.json`.
- **Control por Línea de Comandos**: Opciones como `--config`, `--force-download`, etc.
- **Manejo Robusto de Errores**

## 🛠️ Tecnologías Utilizadas

- Python 3.9+
- requests
- BeautifulSoup4
- os
- shutil
- json
- argparse
- urllib.parse

## ⚙️ Configuración del Entorno

1. **Clonar el Repositorio**  
```bash
git clone https://github.com/CenitiumDev/web-file-downloader
cd web-file-downloader
```

2. **Crear y Activar un Entorno Virtual**  
```bash
python -m venv venv
# Windows
.env\Scriptsctivate
# macOS/Linux
source venv/bin/activate
```

3. **Instalar Dependencias**  
```bash
pip install requests beautifulsoup4
# o si usas requirements.txt
pip install -r requirements.txt
```

## 🚀 Uso

### Estructura del Proyecto

```
web_file_downloader/
├── venv/
├── src/
│   ├── main.py
│   └── config.py
├── config.json
├── .gitignore
├── requirements.txt
└── README.md
```

### Configurar el config.json

```json
{
  "target_urls": [
    "https://www.dane.gov.co/index.php/estadisticas-por-tema/pobreza...",
    "https://www.dane.gov.co/index.php/estadisticas-por-tema/empleo..."
  ],
  "download_base_folder": "downloads",
  "organization_rule": "type_then_date",
  "allowed_extensions": [".pdf", ".png", ".jpg", ".jpeg", ".gif", ".zip", ".xlsx", ".docx", ".pptx"],
  "request_delay_seconds": 2,
  "download_history_file": "downloaded_files_history.json"
}
```

### Ejecutar el Script

```bash
python src/main.py
python src/main.py --help
python src/main.py --force-download
python src/main.py --config my_custom_settings.json
```

## 📜 Historial de Descargas

- Evita duplicados con `downloaded_files_history.json`
- Se actualiza tras cada descarga exitosa


## 💡 Futuras Mejoras

- Soporte JavaScript con Selenium o Playwright
- Sistema de logging avanzado
- Notificaciones (email, Slack, Telegram)
- Programación con cron o Programador de Tareas
- Interfaz gráfica (Tkinter, PyQt, Streamlit)

## 🤝 Contribuciones
¡Las contribuciones son bienvenidas!  
No dudes en crear un _issue_ o _pull request_ si tienes sugerencias o mejoras.

---
