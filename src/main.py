import requests
from bs4 import BeautifulSoup
import os
import shutil
from datetime import datetime
import time
from urllib.parse import urljoin, urlparse
import json
import argparse

def load_config(config_path):
    """
    Carga la configuración del script desde un archivo JSON.

    Args:
        config_path (str): La ruta al archivo de configuración JSON.

    Returns:
        dict: Un diccionario con la configuración cargada.
        None: Si hay un error al cargar el archivo.
    """
    print(f"Cargando configuración desde: {config_path}")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("Configuración cargada exitosamente.")
        return config
    except FileNotFoundError:
        print(f"Error: El archivo de configuración '{config_path}' no fue encontrado.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el JSON del archivo de configuración '{config_path}': {e}")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado al cargar la configuración: {e}")
        return None


def load_download_history(history_file_path):
    """
    Carga el historial de URLs de archivos descargados desde un archivo JSON.

    Args:
        history_file_path (str): La ruta al archivo de historial JSON.

    Returns:
        set: Un conjunto de URLs de archivos que ya han sido descargados.
    """
    if os.path.exists(history_file_path):
        try:
            with open(history_file_path, 'r', encoding='utf-8') as f:
                history_list = json.load(f)
                print(f"Historial de descargas cargado desde: {history_file_path}")
                return set(history_list)
        except json.JSONDecodeError as e:
            print(f"Advertencia: Archivo de historial corrupto '{history_file_path}'. Se creará uno nuevo. Error: {e}")
            return set()
        except Exception as e:
            print(f"Advertencia: Error al cargar el historial de descargas '{history_file_path}'. Error: {e}")
            return set()
    return set()


def save_download_history(history_file_path, downloaded_urls):
    """
    Guarda el conjunto de URLs de archivos descargados en un archivo JSON.

    Args:
        history_file_path (str): La ruta al archivo de historial JSON.
        downloaded_urls (set): El conjunto de URLs de archivos descargados.
    """
    try:
        with open(history_file_path, 'w', encoding='utf-8') as f:
            json.dump(list(downloaded_urls), f, indent=4)
        print(f"Historial de descargas guardado en: {history_file_path}")
    except Exception as e:
        print(f"Error al guardar el historial de descargas en '{history_file_path}': {e}")


def get_page_content(url):
    """
    Realiza una petición HTTP GET a la URL especificada y devuelve el contenido HTML.
    Maneja posibles errores de red o de respuesta HTTP.
    """
    print(f"Intentando obtener contenido de: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"Contenido obtenido exitosamente de: {url}")
        return response.text
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP al acceder a {url}: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"Error de conexión al acceder a {url}: {e}")
    except requests.exceptions.Timeout as e:
        print(f"Tiempo de espera agotado al acceder a {url}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error desconocido de requests al acceder a {url}: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado al obtener el contenido de {url}: {e}")
    return None


def find_download_links(html_content, base_url, allowed_extensions):
    """
    Analiza el contenido HTML para encontrar enlaces de descarga de archivos
    basándose en las extensiones permitidas.
    """
    print("Buscando enlaces de descarga...")
    soup = BeautifulSoup(html_content, 'html.parser')
    found_links = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        absolute_url = urljoin(base_url, href)

        if any(absolute_url.lower().endswith(ext) for ext in allowed_extensions):
            if absolute_url not in found_links:
                found_links.append(absolute_url)
                print(f"  Enlace encontrado: {absolute_url}")

    if not found_links:
        print("No se encontraron enlaces de descarga con las extensiones permitidas en esta página.")
    return found_links


def download_file(file_url, destination_folder):
    """
    Descarga un archivo de la URL especificada a la carpeta de destino.
    """
    file_name = os.path.basename(urlparse(file_url).path)

    if not file_name:
        print(f"No se pudo determinar el nombre del archivo para {file_url}. Saltando descarga.")
        return None

    file_path = os.path.join(destination_folder, file_name)

    os.makedirs(destination_folder, exist_ok=True)

    if os.path.exists(file_path):
        print(f"  El archivo '{file_name}' ya existe en '{destination_folder}'. Saltando descarga local.")
        return file_path

    print(f"  Descargando '{file_name}' de: {file_url}")
    try:
        with requests.get(file_url, stream=True, timeout=30) as r:
            r.raise_for_status()

            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"  Descarga completa: '{file_path}'")
        return file_path

    except requests.exceptions.HTTPError as e:
        print(f"  Error HTTP al descargar {file_url}: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"  Error de conexión al descargar {file_url}: {e}")
    except requests.exceptions.Timeout as e:
        print(f"  Tiempo de espera agotado al descargar {file_url}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"  Error desconocido de requests al descargar {file_url}: {e}")
    except IOError as e:
        print(f"  Error de E/S al guardar el archivo {file_path}: {e}")
    except Exception as e:
        print(f"  Ocurrió un error inesperado durante la descarga de {file_url}: {e}")

    return None


def organize_file(file_path, base_download_folder, rule_type):
    """
    Organiza un archivo descargado en una subcarpeta basada en la regla definida.
    Ahora soporta 'date', 'type', y 'type_then_date'.

    Args:
        file_path (str): La ruta actual del archivo descargado.
        base_download_folder (str): La carpeta base donde se organizarán los archivos.
        rule_type (str): La regla de organización ('date', 'type', o 'type_then_date').

    Returns:
        str or None: La nueva ruta del archivo si la organización fue exitosa,
                     de lo contrario, None.
    """
    if not file_path or not os.path.exists(file_path):
        print(f"  Advertencia: Archivo no encontrado o ruta inválida para organizar: {file_path}")
        return None

    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1].lower().replace('.', '')

    subfolder_1 = ""
    subfolder_2 = ""

    if rule_type == "date":
        today_date = datetime.now().strftime("%Y-%m-%d")
        subfolder_1 = today_date
    elif rule_type == "type":
        if file_extension:
            subfolder_1 = file_extension.capitalize()
        else:
            subfolder_1 = "Otros"
    elif rule_type == "type_then_date":
        if file_extension:
            subfolder_1 = file_extension.capitalize()
        else:
            subfolder_1 = "Otros"
        today_date = datetime.now().strftime("%Y-%m-%d")
        subfolder_2 = today_date
    else:
        print(f"  Regla de organización desconocida: '{rule_type}'. El archivo se quedará en la carpeta base.")
        return None

    if subfolder_2:
        final_destination_dir = os.path.join(base_download_folder, subfolder_1, subfolder_2)
    else:
        final_destination_dir = os.path.join(base_download_folder, subfolder_1)

    os.makedirs(final_destination_dir, exist_ok=True)
    final_file_path = os.path.join(final_destination_dir, file_name)

    counter = 1
    original_file_name_without_ext, original_ext = os.path.splitext(file_name)
    while os.path.exists(final_file_path):
        new_file_name = f"{original_file_name_without_ext}({counter}){original_ext}"
        final_file_path = os.path.join(final_destination_dir, new_file_name)
        counter += 1

    print(f"  Organizando '{file_name}' a: '{final_destination_dir}'")
    try:
        shutil.move(file_path, final_file_path)
        print(f"  Archivo movido exitosamente a: '{final_file_path}'")
        return final_file_path
    except shutil.Error as e:
        print(f"  Error de shutil al mover el archivo {file_path} a {final_file_path}: {e}")
    except OSError as e:
        print(f"  Error del sistema operativo al mover el archivo {file_path}: {e}")
    except Exception as e:
        print(f"  Ocurrió un error inesperado al organizar el archivo {file_path}: {e}")
    return None

def main():
    """
    Función principal que orquesta el proceso de descarga y organización.
    """
    parser = argparse.ArgumentParser(
        description="Automatiza la descarga y organización de archivos web.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default="config.json",
        help="""Ruta al archivo de configuración JSON.
        Ejemplo: python src/main.py -c custom_config.json"""
    )
    parser.add_argument(
        "-f", "--force-download",
        action="store_true",
        help="""Fuerza la descarga de archivos incluso si ya están en el historial.
        Útil para re-descargar o actualizar."""
    )
    args = parser.parse_args()

    config = load_config(args.config)
    if not config:
        print("No se pudo cargar la configuración. Asegúrate de que el archivo existe y es un JSON válido. Saliendo.")
        return

    TARGET_URLS = config.get("target_urls", [])
    DOWNLOAD_BASE_FOLDER = config.get("download_base_folder", "downloads")
    ORGANIZATION_RULE = config.get("organization_rule", "date")
    ALLOWED_EXTENSIONS = config.get("allowed_extensions", [])
    REQUEST_DELAY_SECONDS = config.get("request_delay_seconds", 2)
    DOWNLOAD_HISTORY_FILE = config.get("download_history_file", "downloaded_files_history.json")

    if not TARGET_URLS:
        print("Advertencia: No se han especificado URLs para monitorear en el archivo de configuración.")
        print("Asegúrate de que 'target_urls' esté definido y no esté vacío en 'config.json'. Saliendo.")
        return

    if not ALLOWED_EXTENSIONS:
        print("Advertencia: No se han especificado extensiones de archivo permitidas en el archivo de configuración.")
        print("Asegúrate de que 'allowed_extensions' esté definido y no esté vacío en 'config.json'. Saliendo.")
        return

    print("\n" + "="*50)
    print("Iniciando el proceso de automatización de descarga de archivos web.")
    print("="*50 + "\n")

    os.makedirs(DOWNLOAD_BASE_FOLDER, exist_ok=True)
    print(f"Carpeta de descargas base: '{DOWNLOAD_BASE_FOLDER}'")

    downloaded_urls_history = load_download_history(DOWNLOAD_HISTORY_FILE)
    initial_downloaded_count = len(downloaded_urls_history)
    print(f"Se encontraron {initial_downloaded_count} archivos en el historial de descargas.")
    if args.force_download:
        print("Modo de descarga forzada activado: Se re-descargarán los archivos existentes.")
    else:
        print("Modo normal: Los archivos ya en el historial serán saltados.")


    for url in TARGET_URLS:
        print(f"\n--- Procesando URL: {url} ---")
        html_content = get_page_content(url)
        if html_content:
            download_links = find_download_links(html_content, url, ALLOWED_EXTENSIONS)
            if download_links:
                print(f"Se encontraron {len(download_links)} enlaces descargables en {url}. Iniciando descargas...")
                for link in download_links:
                    if link in downloaded_urls_history and not args.force_download:
                        print(f"    Archivo ya descargado (o en historial): {link}. Saltando.")
                        continue

                    downloaded_file_path = download_file(link, DOWNLOAD_BASE_FOLDER)
                    if downloaded_file_path:
                        print(f"    Archivo listo para organizar: {downloaded_file_path}")
                        organized_path = organize_file(downloaded_file_path, DOWNLOAD_BASE_FOLDER, ORGANIZATION_RULE)
                        if organized_path:
                            print(f"    Archivo organizado en: {organized_path}")
                            downloaded_urls_history.add(link)
                        else:
                            print(f"    No se pudo organizar el archivo: {downloaded_file_path}")
                    else:
                        print(f"    No se pudo descargar el archivo de: {link}. Saltando organización.")
                    time.sleep(REQUEST_DELAY_SECONDS)
            else:
                print(f"No se encontraron archivos descargables en {url} con las extensiones permitidas.")

        else:
            print(f"No se pudo obtener el contenido de {url}. Saltando esta URL.")

        time.sleep(REQUEST_DELAY_SECONDS)

    if len(downloaded_urls_history) > initial_downloaded_count:
        print(f"\nSe han añadido {len(downloaded_urls_history) - initial_downloaded_count} nuevos archivos al historial.")
        save_download_history(DOWNLOAD_HISTORY_FILE, downloaded_urls_history)
    else:
        print("\nNo se descargaron nuevos archivos para añadir al historial en esta ejecución.")

    print("\n" + "="*50)
    print("Proceso de automatización finalizado.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()