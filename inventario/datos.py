"""Conexión y operaciones de almacenamiento en MongoDB."""

from pymongo import MongoClient


class Repositorio:
    """Centraliza el acceso a las colecciones y sus índices."""

    def __init__(self, uri, nombre_base):
        self.cliente = MongoClient(
            uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000,
            socketTimeoutMS=5000,
        )
        self.base = self.cliente[nombre_base]

    def preparar(self):
        """Comprueba la conexión y crea los índices necesarios."""
        self.cliente.admin.command("ping")
        self.base.usuarios.create_index("email", unique=True)
        self.base.articulos.create_index("usuario_modifico")

    def buscar(self, coleccion, filtro):
        """Devuelve un documento o None si no existe."""
        return self.base[coleccion].find_one(filtro)

    def listar(self, coleccion):
        """Obtiene los documentos ordenados por su identificador."""
        return list(self.base[coleccion].find().sort("_id", 1))

    def crear(self, coleccion, campos):
        """Inserta un documento y devuelve su identificador."""
        return self.base[coleccion].insert_one(campos).inserted_id

    def modificar(self, coleccion, identificador, campos):
        """Actualiza campos sin reemplazar la clave del documento."""
        resultado = self.base[coleccion].update_one(
            {"_id": identificador}, {"$set": campos}
        )
        return resultado.matched_count == 1

    def eliminar(self, coleccion, identificador):
        """Elimina un documento y comunica si existía."""
        resultado = self.base[coleccion].delete_one({"_id": identificador})
        return resultado.deleted_count == 1

    def cerrar(self):
        """Libera las conexiones del cliente."""
        self.cliente.close()
