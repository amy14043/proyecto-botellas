import os
import cv2
from groundingdino.util.inference import load_model, load_image, predict, annotate
from Base_de_datos import actualizar_detectadas_probables, obtener_sensibilidad

CONFIG_PATH = "config.py"
CHECK_POINT_PATH = "modelo.pth"
TEXT_PROMPT = "pet bottle"
#BOX_THRESHOLD = 0.4
#TEXT_THRESHOLD = 0.45

model = load_model(CONFIG_PATH, CHECK_POINT_PATH)
device = "cpu"
model = model.to(device)

# Función para procesar la imagen y mostrarla en una nueva ventana
def buscar_botellas(ruta_de_imagen, ruta_procesadas, archivo, proyecto):
    
    sensibilidad = obtener_sensibilidad(archivo, proyecto)
    print(f"sensibilidad = {sensibilidad[0]}, {sensibilidad[1]}")  # A
    image_source, image = load_image(ruta_de_imagen)

    boxes, logits, phrases = predict(
        model=model,
        image=image,
        caption=TEXT_PROMPT,
        text_threshold=sensibilidad[0],
        box_threshold=sensibilidad[1],
        device=device
    )

    # Conteo de botellas PET detectadas y probables
    detecciones_seguras = sum(1 for phrase in phrases if phrase)  # Con texto
    detecciones_probables = len(boxes) - detecciones_seguras  # Sin texto
    phrases = ["Botella detectada " if phrase else phrase for phrase in phrases]
    
    annotated_frame = annotate(image_source=image_source, boxes=boxes, logits=logits, phrases=phrases)
    #guardar la imagen en la ruta destino
    ruta_destino = os.path.join(ruta_procesadas, archivo)
    if not os.path.exists(ruta_destino):
        cv2.imwrite(ruta_destino, annotated_frame)
    nombre_archivo = f"{sensibilidad[0]}_{sensibilidad[1]}_{archivo}"
    cv2.imwrite(os.path.join(ruta_procesadas, nombre_archivo), annotated_frame)

     # Actualizar el campo botellas_detectadas en la base de datos    
    actualizar_detectadas_probables( os.path.basename(ruta_de_imagen), proyecto, detecciones_seguras, detecciones_probables)