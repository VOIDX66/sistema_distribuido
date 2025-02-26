from flask import Flask, request, jsonify
import requests
import threading
import time

app = Flask(__name__)

SERVIDORES = ["http://localhost:5000", "http://localhost:5001"]
SYNC_INTERVAL = 5  # Intervalo de sincronización en segundos

def obtener_servidor_mas_actualizado():
    """Determina qué servidor tiene el último cambio registrado."""
    servidores_info = {}

    for servidor in SERVIDORES:
        try:
            response = requests.get(f"{servidor}/ultimo_cambio", timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get("servidor") and data.get("ultimo_cambio") != "2000-01-01T00:00:00":
                    servidores_info[servidor] = data["ultimo_cambio"]
        except requests.exceptions.RequestException:
            print(f"⚠️ No se pudo obtener el último cambio de {servidor}")

    if servidores_info:
        servidor_actualizado = max(servidores_info, key=servidores_info.get)
        print(f"✅ Servidor más actualizado: {servidor_actualizado}")
        return servidor_actualizado
    
    print("❌ No hay servidores con datos en sincronización.")
    return None

@app.route("/productos", methods=["GET", "POST"])
def proxy_productos():
    """Redirige solicitudes de productos al servidor más actualizado."""
    servidor = obtener_servidor_mas_actualizado()
    if not servidor:
        return jsonify({"error": "No hay servidores disponibles"}), 500

    url = f"{servidor}/productos"
    try:
        if request.method == "GET":
            response = requests.get(url, timeout=3)
        elif request.method == "POST":
            response = requests.post(url, json=request.json, timeout=3)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({"error": "No se pudo conectar con el servidor"}), 500

@app.route("/productos/<int:producto_id>", methods=["PUT", "DELETE"])
def proxy_producto_id(producto_id):
    """Redirige las solicitudes de actualización y eliminación de productos al servidor más actualizado."""
    servidor = obtener_servidor_mas_actualizado()
    if not servidor:
        return jsonify({"error": "No hay servidores disponibles"}), 500

    url = f"{servidor}/productos/{producto_id}"
    try:
        if request.method == "PUT":
            response = requests.put(url, json=request.json, timeout=3)
        elif request.method == "DELETE":
            response = requests.delete(url, timeout=3)

        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        print(f"⚠️ No se pudo conectar con {servidor}. Esperando sincronización.")
        return jsonify({"warning": "Servidor no disponible. El cambio se aplicará cuando se sincronice."}), 202

def sincronizar_servidores():
    """Sincroniza todos los servidores con los datos del más actualizado, manejando servidores caídos."""
    while True:
        time.sleep(SYNC_INTERVAL)
        servidor_fuente = obtener_servidor_mas_actualizado()
        if not servidor_fuente:
            print("⚠️ No hay servidores disponibles para sincronizar.")
            continue

        for servidor in SERVIDORES:
            if servidor != servidor_fuente:
                try:
                    print(f"\n🔄 Sincronizando {servidor} con {servidor_fuente}...")

                    # Obtener lista de productos del servidor más actualizado
                    response_fuente = requests.get(f"{servidor_fuente}/productos", timeout=3)
                    response_servidor = requests.get(f"{servidor}/productos", timeout=3)

                    if response_fuente.status_code == 200 and response_servidor.status_code == 200:
                        productos_fuente = {p[0]: p for p in response_fuente.json()}  # Diccionario {id: producto}
                        productos_servidor = {p[0] for p in response_servidor.json()}  # Conjunto de IDs

                        print(f"📥 Productos en {servidor_fuente}: {productos_fuente.keys()}")
                        print(f"📤 Productos en {servidor}: {productos_servidor}")

                        # 🔹 Actualizar o crear productos
                        for id_producto, producto in productos_fuente.items():
                            producto_dict = {
                                "id": producto[0],
                                "nombre": producto[1],
                                "descripcion": producto[2],
                                "cantidad": int(producto[3]),
                                "precio": float(producto[4]),
                                "ultima_modificacion": producto[5]
                            }

                            if id_producto in productos_servidor:
                                print(f"📝 Actualizando producto {id_producto} en {servidor}...")
                                requests.put(f"{servidor}/productos/{id_producto}", json=producto_dict, timeout=3)
                            else:
                                print(f"➕ Creando producto {id_producto} en {servidor}...")
                                requests.post(f"{servidor}/productos", json=producto_dict, timeout=3)

                        # 🔹 Manejar eliminaciones
                        productos_eliminados = productos_servidor - productos_fuente.keys()
                        for producto_id in productos_eliminados:
                            print(f"🗑️ Eliminando producto {producto_id} en {servidor}...")
                            requests.delete(f"{servidor}/productos/{producto_id}", timeout=3)

                except requests.exceptions.RequestException:
                    print(f"⚠️ No se pudo conectar con {servidor}, esperando a que vuelva.")

if __name__ == "__main__":
    print("🔄 Iniciando módulo de replicación como Proxy y sincronizador...")
    threading.Thread(target=sincronizar_servidores, daemon=True).start()
    app.run(host="0.0.0.0", port=4000)
