import argparse
import requests
import time

BASE_URL = "http://localhost:4000/productos"  # Ahora apunta al módulo de replicación

def verificar_conexion():
    """ Verifica si el módulo de replicación está disponible antes de iniciar. """
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Conexión con el módulo de replicación establecida.\n")
            return True
    except requests.RequestException:
        print("❌ Error: No se pudo conectar con el servidor. Asegúrate de que está en ejecución.")
        return False

def manejar_excepcion(func):
    """ Decorador para manejar errores de conexión durante la ejecución. """
    def wrapper(*args, **kwargs):
        if not verificar_conexion():
            print("❌ Error: Se perdió la conexión con el servidor.")
            return
        try:
            return func(*args, **kwargs)
        except requests.ConnectionError:
            print("❌ Error: No se pudo conectar con el servidor.")
        except requests.Timeout:
            print("⏳ Error: Tiempo de espera agotado.")
        except requests.RequestException as e:
            print(f"⚠️ Error en la solicitud: {e}")
    return wrapper

@manejar_excepcion
def obtener_productos():
    response = requests.get(BASE_URL)
    print(response.json())

@manejar_excepcion
def crear_producto(args):
    data = {
        "nombre": args.nombre,
        "descripcion": args.descripcion,
        "cantidad": args.cantidad,
        "precio": args.precio
    }
    response = requests.post(BASE_URL, json=data)
    print(response.json())

@manejar_excepcion
def actualizar_producto(args):
    data = {}
    if args.nombre: data["nombre"] = args.nombre
    if args.descripcion: data["descripcion"] = args.descripcion
    if args.cantidad: data["cantidad"] = args.cantidad
    if args.precio: data["precio"] = args.precio
    response = requests.put(f"{BASE_URL}/{args.id}", json=data)
    print(response.json())

@manejar_excepcion
def eliminar_producto(args):
    response = requests.delete(f"{BASE_URL}/{args.id}")
    print(response.json())

def input_con_salida(mensaje):
    """ Permite ingresar datos y salir escribiendo 'salir'. """
    valor = input(mensaje).strip()
    if valor.lower() == "salir":
        print("🔙 Operación cancelada. Volviendo al menú...")
        return None
    return valor

def menu():
    while True:
        print("\n📌 Opciones disponibles:")
        print("1️⃣ Listar productos")
        print("2️⃣ Crear un producto")
        print("3️⃣ Actualizar un producto")
        print("4️⃣ Eliminar un producto")
        print("5️⃣ Salir")

        opcion = input("Selecciona una opción (1-5): ").strip()

        if not verificar_conexion():
            print("❌ Se perdió la conexión con el servidor. Cerrando el cliente.")
            break

        if opcion == "1":
            obtener_productos()
        elif opcion == "2":
            print("\n✏️ Creando un nuevo producto... (Escribe 'salir' para cancelar)\n")
            nombre = input_con_salida("Nombre: ")
            if nombre is None: continue

            descripcion = input_con_salida("Descripción: ")
            if descripcion is None: continue

            cantidad = input_con_salida("Cantidad: ")
            if cantidad is None: continue

            precio = input_con_salida("Precio: ")
            if precio is None: continue

            args = argparse.Namespace(
                nombre=nombre,
                descripcion=descripcion,
                cantidad=int(cantidad),
                precio=float(precio)
            )
            crear_producto(args)

        elif opcion == "3":
            print("\n🛠️ Actualizando un producto... (Escribe 'salir' para cancelar)\n")
            id_producto = input_con_salida("ID del producto: ")
            if id_producto is None: continue

            nombre = input_con_salida("Nuevo nombre (dejar en blanco si no cambia): ")
            descripcion = input_con_salida("Nueva descripción (dejar en blanco si no cambia): ")
            cantidad = input_con_salida("Nueva cantidad (dejar en blanco si no cambia): ")
            precio = input_con_salida("Nuevo precio (dejar en blanco si no cambia): ")

            args = argparse.Namespace(
                id=int(id_producto),
                nombre=nombre or None,
                descripcion=descripcion or None,
                cantidad=int(cantidad) if cantidad else None,
                precio=float(precio) if precio else None
            )
            actualizar_producto(args)

        elif opcion == "4":
            print("\n🗑️ Eliminando un producto... (Escribe 'salir' para cancelar)\n")
            id_producto = input_con_salida("ID del producto: ")
            if id_producto is None: continue

            args = argparse.Namespace(id=int(id_producto))
            eliminar_producto(args)

        elif opcion == "5":
            print("👋 Saliendo...")
            break
        else:
            print("❌ Opción inválida, intenta de nuevo.")

if __name__ == "__main__":
    print("🔄 Verificando conexión con el servidor...")
    if verificar_conexion():
        menu()
    else:
        print("❌ No se pudo establecer conexión. Cerrando el cliente.")
