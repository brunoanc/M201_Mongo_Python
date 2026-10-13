"""Menús e interacción con el operador del inventario."""

from pymongo.errors import PyMongoError

from inventario.errores import ErrorValidacion


def elegir_opcion(titulo, opciones):
    """Repite el menú hasta recibir una opción disponible."""
    while True:
        print(f"\n{titulo}")

        for clave, etiqueta in opciones.items():
            print(f"{clave}. {etiqueta}")

        opcion = input("Opción: ").strip()

        if opcion in opciones:
            return opcion

        print("Opción inválida.")


def pedir_usuario():
    """Solicita los campos editables de un usuario."""
    return (
        input("Email: "), input("Nombre: "), input("Apellido: "),
    )


def pedir_articulo():
    """Solicita el contenido y el responsable de un artículo."""
    return (
        input("Nombre del artículo: "), input("Descripción: "),
        input("Marca: "), input("Email del responsable: "),
    )


def mostrar_usuario(usuario):
    """Presenta los datos de un usuario."""
    print(f"\nID: {usuario['_id']}")
    print(f"Email: {usuario['email']}")
    print(f"Nombre: {usuario['nombre']} {usuario['apellido']}")
    print(f"Fecha de creación: {usuario['fecha_creado']}")


def mostrar_articulo(articulo, servicio):
    """Muestra el último responsable resolviendo su referencia."""
    usuario = servicio.responsable_articulo(articulo)
    print(f"\nID: {articulo['_id']}")
    print(f"Nombre: {articulo['nombre']}")
    print(f"Descripción: {articulo['descripcion']}")
    print(f"Marca: {articulo['marca']}")

    if usuario is None:
        print("Modificado por: usuario no encontrado.")
    else:
        print(
            f"Modificado por: {usuario['email']} "
            f"({usuario['nombre']} {usuario['apellido']})"
        )


def consultar_usuarios(servicio):
    """Lista usuarios o busca uno por email."""
    email = input("Email (Enter para listar): ").strip()
    usuarios = (
        [servicio.buscar_usuario(email)]
        if email else servicio.listar_usuarios()
    )

    if not usuarios:
        print("No hay usuarios.")

    for usuario in usuarios:
        mostrar_usuario(usuario)


def consultar_articulos(servicio):
    """Lista artículos o busca uno por ID."""
    identificador = input("ID (Enter para listar): ").strip()
    articulos = (
        [servicio.buscar_articulo(identificador)]
        if identificador else servicio.listar_articulos()
    )

    if not articulos:
        print("No hay artículos.")

    for articulo in articulos:
        mostrar_articulo(articulo, servicio)


def operar_usuarios(opcion, servicio):
    """Ejecuta la operación seleccionada del módulo de usuarios."""
    if opcion == "1":
        identificador = servicio.crear_usuario(*pedir_usuario())
        print(f"Usuario registrado. ID: {identificador}")
    elif opcion == "2":
        consultar_usuarios(servicio)
    elif opcion == "3":
        email = input("Email actual: ")
        servicio.buscar_usuario(email)
        print("Nuevos datos:")
        servicio.modificar_usuario(email, *pedir_usuario())
        print("Usuario modificado.")
    elif opcion == "4":
        servicio.eliminar_usuario(input("Email a eliminar: "))
        print("Usuario eliminado.")


def operar_articulos(opcion, servicio):
    """Ejecuta la operación seleccionada del módulo de artículos."""
    if opcion == "1":
        identificador = servicio.crear_articulo(*pedir_articulo())
        print(f"Artículo registrado. ID: {identificador}")
    elif opcion == "2":
        consultar_articulos(servicio)
    elif opcion == "3":
        identificador = input("ID a modificar: ")
        servicio.buscar_articulo(identificador)
        print("Nuevos datos:")
        servicio.modificar_articulo(identificador, *pedir_articulo())
        print("Artículo modificado.")
    elif opcion == "4":
        servicio.eliminar_articulo(input("ID a eliminar: "))
        print("Artículo eliminado.")


def submenu(titulo, operacion, servicio):
    """Mantiene abierto el módulo después de errores controlados."""
    opciones = {
        "1": "Crear", "2": "Consultar",
        "3": "Modificar", "4": "Eliminar", "0": "Volver",
    }

    while True:
        opcion = elegir_opcion(titulo, opciones)

        if opcion == "0":
            return

        try:
            operacion(opcion, servicio)
        except ErrorValidacion as error:
            print(f"Error: {error}")
        except PyMongoError:
            print("Error de MongoDB. Revisa la conexión y los datos.")


def ejecutar(servicio):
    """Abre el menú principal hasta que el operador solicita salir."""
    print("Auditoría de inventario")

    while True:
        opcion = elegir_opcion(
            "Menú principal", {"1": "Usuarios", "2": "Artículos", "0": "Salir"}
        )

        if opcion == "0":
            print("Sesión finalizada.")
            return

        if opcion == "1":
            submenu("Usuarios", operar_usuarios, servicio)
        else:
            submenu("Artículos", operar_articulos, servicio)
