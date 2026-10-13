"""CRUD y reglas de negocio de usuarios y artículos."""

from datetime import date
import re

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

from inventario.errores import ErrorValidacion


def texto_obligatorio(valor, campo):
    """Normaliza un texto y rechaza valores vacíos."""
    if not isinstance(valor, str) or not valor.strip():
        raise ErrorValidacion(f"{campo.capitalize()} no puede estar vacío.")

    return valor.strip()


def normalizar_email(email):
    """Aplica la política de emails sin distinción de mayúsculas."""
    email = texto_obligatorio(email, "email").lower()

    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ErrorValidacion("Email inválido. Ejemplo: ana@empresa.com.")

    return email


def convertir_id(identificador):
    """Acepta un ObjectId o su representación de 24 dígitos hexadecimales."""
    try:
        return ObjectId(str(identificador).strip())
    except (InvalidId, TypeError) as error:
        raise ErrorValidacion(
            "ID inválido. Usa 24 caracteres hexadecimales."
        ) from error


class Inventario:
    """Valida las operaciones antes de delegarlas al repositorio."""

    def __init__(self, repositorio):
        self.repositorio = repositorio

    def crear_usuario(self, email, nombre, apellido):
        """Registra un usuario con fecha automática e email único."""
        campos = self._campos_usuario(email, nombre, apellido)
        campos["fecha_creado"] = date.today().isoformat()

        try:
            return self.repositorio.crear("usuarios", campos)
        except DuplicateKeyError as error:
            raise ErrorValidacion("Email ya registrado.") from error

    def _campos_usuario(self, email, nombre, apellido):
        """Valida y normaliza los campos editables del usuario."""
        return {
            "email": normalizar_email(email),
            "nombre": texto_obligatorio(nombre, "nombre"),
            "apellido": texto_obligatorio(apellido, "apellido"),
        }

    def buscar_usuario(self, email):
        """Busca por email y rechaza referencias inexistentes."""
        usuario = self.repositorio.buscar(
            "usuarios", {"email": normalizar_email(email)}
        )

        if usuario is None:
            raise ErrorValidacion("Usuario no encontrado.")

        return usuario

    def listar_usuarios(self):
        """Obtiene todos los usuarios registrados."""
        return self.repositorio.listar("usuarios")

    def modificar_usuario(self, email_actual, email, nombre, apellido):
        """Cambia los datos manteniendo ObjectId y fecha de creación."""
        usuario = self.buscar_usuario(email_actual)
        campos = self._campos_usuario(email, nombre, apellido)

        try:
            actualizado = self.repositorio.modificar(
                "usuarios", usuario["_id"], campos
            )
        except DuplicateKeyError as error:
            raise ErrorValidacion("Email ya registrado.") from error

        if not actualizado:
            raise ErrorValidacion("Usuario no encontrado.")

    def eliminar_usuario(self, email):
        """Impide borrar al responsable de artículos existentes."""
        usuario = self.buscar_usuario(email)
        articulo = self.repositorio.buscar(
            "articulos", {"usuario_modifico": usuario["_id"]}
        )

        if articulo is not None:
            raise ErrorValidacion(
                "El usuario tiene artículos asociados. "
                "Reasígnalos o elimínalos primero."
            )

        if not self.repositorio.eliminar("usuarios", usuario["_id"]):
            raise ErrorValidacion("Usuario no encontrado.")

    def _campos_articulo(self, nombre, descripcion, marca, email):
        """Valida el nombre y resuelve la referencia al responsable."""
        nombre = texto_obligatorio(nombre, "nombre del artículo")
        usuario = self.buscar_usuario(email)

        return {
            "nombre": nombre,
            "descripcion": descripcion.strip(),
            "marca": marca.strip(),
            "usuario_modifico": usuario["_id"],
        }

    def crear_articulo(self, nombre, descripcion, marca, email):
        """Registra un artículo solamente si existe su responsable."""
        campos = self._campos_articulo(nombre, descripcion, marca, email)
        return self.repositorio.crear("articulos", campos)

    def buscar_articulo(self, identificador):
        """Busca un artículo por ObjectId."""
        articulo = self.repositorio.buscar(
            "articulos", {"_id": convertir_id(identificador)}
        )

        if articulo is None:
            raise ErrorValidacion("Artículo no encontrado.")

        return articulo

    def listar_articulos(self):
        """Obtiene todos los artículos registrados."""
        return self.repositorio.listar("articulos")

    def modificar_articulo(
        self, identificador, nombre, descripcion, marca, email
    ):
        """Guarda los cambios y la referencia al último responsable."""
        articulo = self.buscar_articulo(identificador)
        campos = self._campos_articulo(nombre, descripcion, marca, email)

        actualizado = self.repositorio.modificar(
            "articulos", articulo["_id"], campos
        )

        if not actualizado:
            raise ErrorValidacion("Artículo no encontrado.")

    def eliminar_articulo(self, identificador):
        """Elimina el artículo seleccionado por ID."""
        articulo = self.buscar_articulo(identificador)

        if not self.repositorio.eliminar("articulos", articulo["_id"]):
            raise ErrorValidacion("Artículo no encontrado.")

    def responsable_articulo(self, articulo):
        """Resuelve la referencia al responsable actual."""
        return self.repositorio.buscar(
            "usuarios", {"_id": articulo["usuario_modifico"]}
        )
