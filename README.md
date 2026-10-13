# Auditoría de inventario

Equipo: Bruno Ancona Sala, Melissa Corpeño Molina y Erick Mauricio Lemus Martínez.

Aplicación de consola para gestionar usuarios y artículos y consultar quién
realizó la última modificación de cada artículo.

## Organización del código

| Archivo | Función |
| --- | --- |
| `main.py` | Inicia la aplicación. |
| `inventario/consola.py` | Muestra los menús y solicita datos. |
| `inventario/servicios.py` | Realiza las operaciones y valida los datos. |
| `inventario/datos.py` | Consulta y guarda los datos en MongoDB. |
| `inventario/errores.py` | Define los errores de validación. |

Esta organización separa la interfaz, las validaciones y el almacenamiento
para facilitar la lectura y el mantenimiento del código.

## Almacenamiento

Se eligió MongoDB para guardar los datos en las colecciones `usuarios` y
`articulos`. Su ventaja es que permite consultar los registros y conservarlos
al cerrar la aplicación. Como desventajas, necesita un servidor y la aplicación
debe comprobar que el usuario asociado a un artículo exista.

Guardar los datos solo en memoria sería más sencillo, pero se perderían al
cerrar el programa.

## Estrategia de claves

MongoDB asigna un `_id` único de tipo `ObjectId` a cada registro. Los usuarios
se buscan por email, que también debe ser único. Los artículos se buscan por
su `_id`.

El campo `usuario_modifico` guarda el `_id` del usuario responsable. Al modificar
un artículo, esta referencia se actualiza con el usuario indicado. No se permite
eliminar un usuario que tenga artículos asociados.

## Guía de pruebas y evidencia

Con MongoDB disponible y las dependencias instaladas, ejecuta `python main.py`.
Cada módulo permite crear, consultar, modificar y eliminar registros (CRUD).

Para comprobar el funcionamiento:

1. Registra dos usuarios, consulta sus datos y modifica uno de ellos.
2. Crea un artículo con uno de los usuarios y consúltalo por su ID.
3. Modifica el artículo usando al otro usuario como responsable. Consulta que
   aparezcan los nuevos datos y el último responsable.
4. Elimina el artículo y luego los usuarios. Comprueba que ya no aparezcan.

También deben comprobarse estos errores:

| Caso | Resultado esperado |
| --- | --- |
| Crear o modificar un artículo con nombre vacío. | Se rechaza la operación. |
| Asociar un artículo a un usuario inexistente. | Se rechaza la operación. |
| Registrar un email duplicado. | Se rechaza el registro. |
| Introducir una opción de menú o ID inválido. | Se muestra un error y se puede continuar. |

La [transcripción de consola](evidencia/ejecucion.txt) muestra ambos CRUD y los
fallos controlados ejecutados contra MongoDB real. Corresponde a una ejecución
anterior a la simplificación de los mensajes.
