from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Configuración de la base de datos desde variables de entorno
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "my_db")
DB_USER = os.getenv("DB_USER", "cliente_sistema")
DB_PASSWORD = os.getenv("DB_PASSWORD", "misistema")
SERVER_NAME = os.getenv("SERVER_NAME", os.uname().nodename)  # Nombre único del servidor

def conectar_bd():
    """Intenta conectar a la base de datos y muestra si la conexión fue exitosa o fallida."""
    try:
        conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        print(f"✅ Conexión exitosa a la base de datos {DB_NAME} en {DB_HOST}")
        return conn
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None

def registrar_cambio():
    """Registra en la tabla de sincronización que hubo un cambio en este servidor."""
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sincronizacion (servidor, ultimo_cambio)
            VALUES (%s, NOW())
            ON CONFLICT (servidor) DO UPDATE 
            SET ultimo_cambio = EXCLUDED.ultimo_cambio;
        """, (SERVER_NAME,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Error al registrar cambio en sincronización: {e}")

@app.route("/productos", methods=["POST"])
def crear_producto():
    """Crea un producto. Si se proporciona ID (sincronización), la respeta; si no, la base de datos la genera."""
    data = request.json
    try:
        conn = conectar_bd()
        cur = conn.cursor()

        if "id" in data:
            # 🔹 Si viene de sincronización, se usa la misma ID
            cur.execute("""
                INSERT INTO productos (id, nombre, descripcion, cantidad, precio, ultima_modificacion) 
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO UPDATE 
                SET nombre=EXCLUDED.nombre, descripcion=EXCLUDED.descripcion, 
                    cantidad=EXCLUDED.cantidad, precio=EXCLUDED.precio, 
                    ultima_modificacion=NOW()
            """, (data["id"], data["nombre"], data["descripcion"], data["cantidad"], data["precio"]))
            producto_id = data["id"]
        else:
            # 🔹 Si lo crea el usuario, la ID es automática
            cur.execute("""
                INSERT INTO productos (nombre, descripcion, cantidad, precio, ultima_modificacion) 
                VALUES (%s, %s, %s, %s, NOW()) RETURNING id
            """, (data["nombre"], data["descripcion"], data["cantidad"], data["precio"]))
            producto_id = cur.fetchone()[0]  # Obtener la ID generada automáticamente

        conn.commit()
        cur.close()
        conn.close()

        registrar_cambio()  # Registrar el cambio
        return jsonify({"id": producto_id, "message": "Producto creado"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/productos", methods=["GET"])
def obtener_productos():
    """Obtiene todos los productos almacenados en la base de datos."""
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

@app.route("/productos/<int:id>", methods=["PUT"])
def actualizar_producto(id):
    """Actualiza un producto y registra el cambio en sincronización."""
    data = request.json
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("""
            UPDATE productos 
            SET nombre=%s, descripcion=%s, cantidad=%s, precio=%s, ultima_modificacion=NOW()
            WHERE id=%s
        """, (data.get("nombre"), data.get("descripcion"), data.get("cantidad"), data.get("precio"), id))

        if cur.rowcount == 0:
            return jsonify({"error": "Producto no encontrado"}), 404

        conn.commit()
        cur.close()
        conn.close()

        registrar_cambio()  # Registrar el cambio
        return jsonify({"message": "Producto actualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/productos/<int:id>", methods=["DELETE"])
def eliminar_producto(id):
    """Elimina un producto y registra el cambio en sincronización."""
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("DELETE FROM productos WHERE id=%s", (id,))

        if cur.rowcount == 0:
            return jsonify({"error": "Producto no encontrado"}), 404

        conn.commit()
        cur.close()
        conn.close()

        registrar_cambio()  # Registrar el cambio
        return jsonify({"message": "Producto eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ultimo_cambio", methods=["GET"])
def obtener_ultimo_cambio():
    """Retorna la última fecha de modificación registrada en la tabla sincronización."""
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("SELECT servidor, MAX(ultimo_cambio) FROM sincronizacion GROUP BY servidor ORDER BY MAX(ultimo_cambio) DESC LIMIT 1;")
        resultado = cur.fetchone()
        cur.close()
        conn.close()

        if resultado:
            return jsonify({"servidor": resultado[0], "ultimo_cambio": resultado[1].isoformat()})
        else:
            return jsonify({"servidor": None, "ultimo_cambio": "2000-01-01T00:00:00"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"🔄 Iniciando servidor {SERVER_NAME}...")
    conectar_bd()  # Verificar conexión al iniciar
    app.run(host="0.0.0.0", port=5002)
