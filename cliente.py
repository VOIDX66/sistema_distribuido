import argparse
import requests

BASE_URL = "http://localhost:5000/productos"

def obtener_productos():
    response = requests.get(BASE_URL)
    print(response.json())

def crear_producto(args):
    data = {"nombre": args.nombre, "descripcion": args.descripcion, "cantidad": args.cantidad, "precio": args.precio}
    response = requests.post(BASE_URL, json=data)
    print(response.json())

def actualizar_producto(args):
    data = {}
    if args.nombre: data["nombre"] = args.nombre
    if args.descripcion: data["descripcion"] = args.descripcion
    if args.cantidad: data["cantidad"] = args.cantidad
    if args.precio: data["precio"] = args.precio
    response = requests.put(f"{BASE_URL}/{args.id}", json=data)
    print(response.json())

def eliminar_producto(args):
    response = requests.delete(f"{BASE_URL}/{args.id}")
    print(response.json())

parser = argparse.ArgumentParser(description="Cliente CLI para gestionar el inventario.")
subparsers = parser.add_subparsers(dest="command")

# Comando: listar productos
subparsers.add_parser("listar", help="Listar todos los productos.")

# Comando: crear producto
crear_parser = subparsers.add_parser("crear", help="Crear un nuevo producto.")
crear_parser.add_argument("nombre", type=str, help="Nombre del producto")
crear_parser.add_argument("descripcion", type=str, help="Descripción del producto")
crear_parser.add_argument("cantidad", type=int, help="Cantidad disponible")
crear_parser.add_argument("precio", type=float, help="Precio del producto")
crear_parser.set_defaults(func=crear_producto)

# Comando: actualizar producto
actualizar_parser = subparsers.add_parser("actualizar", help="Actualizar un producto existente.")
actualizar_parser.add_argument("id", type=int, help="ID del producto a actualizar")
actualizar_parser.add_argument("--nombre", type=str, help="Nuevo nombre")
actualizar_parser.add_argument("--descripcion", type=str, help="Nueva descripción")
actualizar_parser.add_argument("--cantidad", type=int, help="Nueva cantidad")
actualizar_parser.add_argument("--precio", type=float, help="Nuevo precio")
actualizar_parser.set_defaults(func=actualizar_producto)

# Comando: eliminar producto
eliminar_parser = subparsers.add_parser("eliminar", help="Eliminar un producto por ID.")
eliminar_parser.add_argument("id", type=int, help="ID del producto a eliminar")
eliminar_parser.set_defaults(func=eliminar_producto)

# Parsear argumentos y ejecutar comando
args = parser.parse_args()
if args.command:
    if args.command == "listar":
        obtener_productos()
    else:
        args.func(args)
else:
    parser.print_help()
