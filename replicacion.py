from flask import Flask, request, jsonify
import requests
import threading
import time

app = Flask(__name__)

# Lista de servidores
SERVIDORES = ["http://localhost:5000", "http://localhost:5001"]
SYNC_INTERVAL = 10  # Cada 10 segundos

def enviar_peticion(metodo, endpoint, data=None):
    for servidor in SERVIDORES:
        try:
            url = f"{servidor}{endpoint}"
            if metodo == "GET":
                response = requests.get(url)
            elif metodo == "POST":
                response = requests.post(url, json=data)
            elif metodo == "PUT":
                response = requests.put(url, json=data)
            elif metodo == "DELETE":
                response = requests.delete(url)
            
            if response.status_code in [200, 201]:
                return response.json()
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Servidor {servidor} no disponible, probando el siguiente...")
    
    return {"error": "Ningún servidor disponible"}

@app.route("/productos", methods=["GET"])
def obtener_productos():
    return jsonify(enviar_peticion("GET", "/productos"))

@app.route("/productos", methods=["POST"])
def crear_producto():
    data = request.json
    return jsonify(enviar_peticion("POST", "/productos", data))

@app.route("/productos/<int:producto_id>", methods=["PUT"])
def actualizar_producto(producto_id):
    data = request.json
    return jsonify(enviar_peticion("PUT", f"/productos/{producto_id}", data))

@app.route("/productos/<int:producto_id>", methods=["DELETE"])
def eliminar_producto(producto_id):
    return jsonify(enviar_peticion("DELETE", f"/productos/{producto_id}"))

def sincronizar_servidores():
    while True:
        time.sleep(SYNC_INTERVAL)
        for servidor in SERVIDORES:
            try:
                response = requests.get(f"{servidor}/ultima_modificacion")
                if response.status_code == 200:
                    ultima_fecha = response.json().get("ultima_modificacion")
                    for otro_servidor in SERVIDORES:
                        if otro_servidor != servidor:
                            nuevos_datos = requests.get(f"{otro_servidor}/actualizar?desde={ultima_fecha}")
                            if nuevos_datos.status_code == 200:
                                for producto in nuevos_datos.json():
                                    requests.put(f"{servidor}/productos/{producto['id']}", json=producto)
            except requests.exceptions.ConnectionError:
                print(f"⚠️ No se pudo conectar con {servidor} para sincronizar")

if __name__ == "__main__":
    threading.Thread(target=sincronizar_servidores, daemon=True).start()
    app.run(host="0.0.0.0", port=4000)
