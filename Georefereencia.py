import os
import folium
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from multiprocessing import Process
import webbrowser

def obtener_datos_exif(ruta_imagen):
    """Devuelve un diccionario con los datos exif de una imagen PIL. También convierte las etiquetas GPS."""
    try:
        imagen = Image.open(ruta_imagen)
        imagen.verify()
        return imagen._getexif()
    except Exception as e:
        print(f"Error al abrir la imagen {ruta_imagen}: {e}")
        return None

def obtener_exif_etiquetado(exif):
    """Devuelve un diccionario con etiquetas legibles para los datos exif."""
    etiquetado = {}
    if not exif:
        return etiquetado
    for (clave, val) in exif.items():
        etiquetado[TAGS.get(clave, clave)] = val
    return etiquetado

def obtener_geotagging(exif):
    """Extrae y convierte la información GPS de los datos exif."""
    if not exif or 'GPSInfo' not in exif:
        return None

    geotagging = {}
    for (clave, val) in GPSTAGS.items():
        if clave in exif['GPSInfo']:
            geotagging[val] = exif['GPSInfo'][clave]

    return geotagging

def obtener_coordenadas(geotags):
    """Convierte las coordenadas GPS a grados."""
    def _convertir_a_grados(valor):
        d = float(valor[0])
        m = float(valor[1])
        s = float(valor[2])
        return d + (m / 60.0) + (s / 3600.0)

    if not geotags:
        return None

    lat = _convertir_a_grados(geotags['GPSLatitude'])
    if geotags['GPSLatitudeRef'] != 'N':
        lat = 0 - lat

    lon = _convertir_a_grados(geotags['GPSLongitude'])
    if geotags['GPSLongitudeRef'] != 'E':
        lon = 0 - lon

    return (lat, lon)

def crear_mapa(carpeta_imagenes):
    """Crea un mapa de folium con marcadores de imágenes georreferenciadas."""
    mapa_osm = folium.Map(location=[0, 0], zoom_start=2)
    lista_coordenadas = []
    extensiones_imagen = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif')
    
    for archivo_imagen in os.listdir(carpeta_imagenes):
        if not archivo_imagen.lower().endswith(extensiones_imagen):
            print(f"Saltando archivo no imagen: {archivo_imagen}")
            continue
        ruta_imagen = os.path.join(carpeta_imagenes, archivo_imagen)
        datos_exif = obtener_datos_exif(ruta_imagen)
        if not datos_exif:
            print(f"No se encontraron datos EXIF para la imagen {archivo_imagen}")
            continue
        exif_etiquetado = obtener_exif_etiquetado(datos_exif)
        geotags = obtener_geotagging(exif_etiquetado)
        if not geotags:
            print(f"No se encontraron datos EXIF de geolocalización para la imagen {archivo_imagen}")
            continue
        coordenadas = obtener_coordenadas(geotags)
        if coordenadas:
            lista_coordenadas.append(coordenadas)
            # Usar ruta relativa para el popup
            ruta_relativa_imagen = os.path.relpath(ruta_imagen, start=carpeta_imagenes)
            contenido_popup = f'<b>{archivo_imagen}</b><br><img src="{ruta_relativa_imagen}" width="300" height="200">'
            folium.Marker(
                location=coordenadas,
                popup=folium.Popup(contenido_popup, max_width=300)
            ).add_to(mapa_osm)
        else:
            print(f"No se encontraron coordenadas para la imagen {archivo_imagen}")

    if lista_coordenadas:
        mapa_osm.fit_bounds([min(lista_coordenadas), max(lista_coordenadas)])
        
    return mapa_osm

def generar_mapa(carpeta_imagenes):
    """Genera el mapa y lo guarda en un archivo HTML."""
    mapa_osm = crear_mapa(carpeta_imagenes)
    ruta_mapa = os.path.join(carpeta_imagenes, 'map.html')
    mapa_osm.save(ruta_mapa)
    return ruta_mapa

def abrir_mapa_en_navegador(carpeta_imagenes):
    """Genera el mapa y lo abre en el navegador web predeterminado."""
    ruta_mapa = generar_mapa(carpeta_imagenes)
    webbrowser.open(f"file:///{ruta_mapa}")

def iniciar_abrir_mapa(carpeta_imagenes):
    """Inicia un proceso separado para abrir el mapa en el navegador web."""
    proceso = Process(target=abrir_mapa_en_navegador, args=(carpeta_imagenes,))
    proceso.start()

if __name__ == "__main__":
    directorio_trabajo = os.getcwd()
    carpeta_imagenes = os.path.join(directorio_trabajo, "imagenes_prueba")  # Reemplaza con la ruta de la carpeta de imagenes
    iniciar_abrir_mapa(carpeta_imagenes)

