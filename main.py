"""Punto de entrada de la aplicación de inventario."""

import os
import sys


def main():
    """Inicializa MongoDB y cierra la conexión al terminar."""
    try:
        from pymongo.errors import ConfigurationError, PyMongoError
        from inventario.consola import ejecutar
        from inventario.datos import Repositorio
        from inventario.servicios import Inventario
    except ModuleNotFoundError:
        print(
            "Instala las dependencias: "
            "python -m pip install -r requirements.txt"
        )
        return 1

    repositorio = None

    try:
        repositorio = Repositorio(
            os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017"),
            os.environ.get("MONGODB_DATABASE", "inventario"),
        )
        repositorio.preparar()
        ejecutar(Inventario(repositorio))
    except (PyMongoError, ConfigurationError, ValueError):
        print(
            "No se pudo abrir el inventario. "
            "Revisa MongoDB y la configuración."
        )
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nSesión finalizada.")
    finally:
        if repositorio is not None:
            repositorio.cerrar()

    return 0


if __name__ == "__main__":
    sys.exit(main())
