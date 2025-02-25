from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Configuración de la base de datos desde variables de entorno
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "my_db")
DB_USER = os.getenv("DB_USER", "cliente_sistema")
DB_PASSWORD = os.getenv("DB_PASSWORD", "misistema")

def conectar_bd():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)

@app.route("/productos", methods=["GET"])
def obtener_productos():
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("SELECT * FROM productos")
        productos = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(productos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/productos", methods=["POST"])
def crear_producto():
    data = request.json
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("INSERT INTO productos (nombre, descripcion, cantidad, precio) VALUES (%s, %s, %s, %s) RETURNING id",
                    (data["nombre"], data["descripcion"], data["cantidad"], data["precio"]))
        producto_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": producto_id, "message": "Producto creado"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/productos/<int:id>", methods=["PUT"])
def actualizar_producto(id):
    data = request.json
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("UPDATE productos SET nombre=%s, descripcion=%s, cantidad=%s, precio=%s WHERE id=%s",
                    (data.get("nombre"), data.get("descripcion"), data.get("cantidad"), data.get("precio"), id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Producto actualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/productos/<int:id>", methods=["DELETE"])
def eliminar_producto(id):
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("DELETE FROM productos WHERE id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Producto eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
