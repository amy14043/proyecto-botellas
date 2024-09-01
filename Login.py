import flet as ft
import time
import os
import sqlite3
import hashlib
from Base_de_datos import inicializar_bd, registrar_accion, verificar_credenciales, obtener_usuarios
from Proyectos import mostrar_ventana_proyectos

def ventana_login(page: ft.Page):
    if not os.path.exists("base.db"):
        inicializar_bd()
    # Configuración de la ventana
    page.window.frameless = True
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True
    page.window.width = 450
    page.window.height = 600
    page.window.bgcolor = ft.colors.TRANSPARENT
    page.bgcolor = ft.colors.TRANSPARENT
    page.window.center()
    
    # Función para manejar el evento de inicio de sesión
    def al_iniciar_sesion(e):
        usuario = entrada_usuario.value.strip()
        contrasena = entrada_contrasena.value.strip()
        if not usuario or not contrasena:
            mensaje.value = "Los campos no pueden estar vacíos"
            mensaje.color = ft.colors.RED
        elif verificar_credenciales(usuario, contrasena):
            mensaje.value = "Inicio de sesión exitoso"
            mensaje.color = ft.colors.GREEN
            registrar_accion(usuario, "Inicio de sesión")            
            page.update()
            time.sleep(1)
            # Limpiar la página actual antes de abrir la nueva ventana
            page.clean()
            # Llamar a la función mostrar_ventana_proyectos usando la misma página y pasando el usuario
            mostrar_ventana_proyectos(page, usuario)
        else:
            mensaje.value = "Nombre de usuario o contraseña inválidos"
            mensaje.color = ft.colors.RED            
        page.update()
        time.sleep(3)
        mensaje.value = ""
        page.update()
    
    # Función para manejar el evento de creación de nuevo usuario
    def al_crear_nuevo_usuario(e):
        def registrar_nuevo_usuario(e):
            nuevo_usuario = entrada_nuevo_usuario.value.strip()
            nueva_contrasena = entrada_nueva_contrasena.value.strip()
            confirmar_contrasena = entrada_confirmar_contrasena.value.strip()
            
            if not nuevo_usuario or not nueva_contrasena or not confirmar_contrasena:
                mensaje_registro.value = "Todos los campos son obligatorios"
                mensaje_registro.color = ft.colors.RED
                
            elif nueva_contrasena != confirmar_contrasena:
                mensaje_registro.value = "Las contraseñas no coinciden"
                mensaje_registro.color = ft.colors.RED
            elif len(nueva_contrasena) < 8:
                mensaje_registro.value = "La contraseña debe tener al menos 8 caracteres"
                mensaje_registro.color = ft.colors.RED
            else:
                usuarios_existentes = [usuario[0] for usuario in obtener_usuarios()]
                if nuevo_usuario in usuarios_existentes:
                    mensaje_registro.value = "El usuario ya existe"
                    mensaje_registro.color = ft.colors.RED
                else:
                    # Hashing de la contraseña antes de guardarla
                    hashed_password = hashlib.sha256(nueva_contrasena.encode()).hexdigest()
                    with sqlite3.connect('base.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', (nuevo_usuario, hashed_password))
                        conn.commit()
                    mensaje_registro.value = "Usuario registrado con éxito"
                    mensaje_registro.color = ft.colors.GREEN
                    
                    page.update()
                    time.sleep(2)
                    modal_registro.open = False
                    page.update()
            mensaje_registro.update()

        # Componentes de la ventana de registro
        entrada_nuevo_usuario = ft.TextField(
            label="Nuevo Usuario",
            width=300,
            border_color=ft.colors.LIGHT_BLUE,
            color=ft.colors.BLACK,
            focused_color=ft.colors.BLUE
        )
        entrada_nueva_contrasena = ft.TextField(
            label="Nueva Contraseña",
            width=300,
            password=True,
            border_color=ft.colors.LIGHT_BLUE,
            color=ft.colors.BLACK,
            focused_color=ft.colors.BLUE
        )
        entrada_confirmar_contrasena = ft.TextField(
            label="Confirmar Contraseña",
            width=300,
            password=True,
            border_color=ft.colors.LIGHT_BLUE,
            color=ft.colors.BLACK,
            focused_color=ft.colors.BLUE
        )
        boton_registrar = ft.ElevatedButton(
            text="Registrar",
            on_click=registrar_nuevo_usuario,
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(
                padding=ft.Padding(15, 20, 15, 20),
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )
        mensaje_registro = ft.Text("", size=14)
        def cerrar_modal(e):
            page.dialog.open = False
            page.update()
        # Contenedor de la ventana de registro
        modal_registro = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Registrar Nuevo Usuario"),
            content=ft.Column(
                [
                    entrada_nuevo_usuario,
                    entrada_nueva_contrasena,
                    entrada_confirmar_contrasena,
                    boton_registrar,
                    mensaje_registro,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_modal)
            ],
        )

        page.dialog = modal_registro
        page.update()
    
    # Componentes de la interfaz gráfica
    entrada_usuario = ft.TextField(
        label="Usuario",
        width=300,
        border_color=ft.colors.LIGHT_BLUE,
        color=ft.colors.BLACK,
        focused_color=ft.colors.BLUE
    )
    entrada_contrasena = ft.TextField(
        label="Contraseña",
        width=300,
        password=True,
        border_color=ft.colors.LIGHT_BLUE,
        color=ft.colors.BLACK,
        focused_color=ft.colors.BLUE
    )
    boton_iniciar_sesion = ft.ElevatedButton(
        text="Iniciar sesión",
        on_click=al_iniciar_sesion,
        bgcolor=ft.colors.BLUE,
        color=ft.colors.WHITE,
        style=ft.ButtonStyle(
            padding=ft.Padding(15, 20, 15, 20),
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )
    mensaje = ft.Text("", size=14)
    boton_crear_usuario = ft.TextButton(
        text="Crear nuevo usuario",
        on_click=al_crear_nuevo_usuario,
        style=ft.ButtonStyle(
            padding=ft.Padding(10, 20, 10, 20),
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )

    # Contenedor principal
    contenedor_inicio_sesion = ft.Container(
        content=ft.Stack(
            [
                ft.Row(
                    [
                        ft.Container(),
                        ft.IconButton(ft.icons.CLOSE, on_click=lambda e: page.window.close(), tooltip="Cerrar"),
                    ],
                    alignment=ft.MainAxisAlignment.END,                    
                ),
                ft.Column(
                    [
                        ft.Text(
                            "Bienvenido",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLUE_GREY_900,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Por favor inicie sesión para continuar",
                            size=16,
                            color=ft.colors.BLUE_GREY_700,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        entrada_usuario,
                        entrada_contrasena,
                        boton_iniciar_sesion,
                        mensaje,
                        boton_crear_usuario
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                )
            ]
        ),
        padding=ft.Padding(40, 40, 40, 40),
        border_radius=15,
        bgcolor=ft.colors.LIGHT_BLUE_200,
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=5, color=ft.colors.BLACK12)
    )

    page.add(contenedor_inicio_sesion)

if __name__ == "__main__":
    ft.app(target=ventana_login)
