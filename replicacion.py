from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

#Introduccir dirección de los servidores con su respectivo puerto
SERVIDORES = ["http://localhost:5000", "http://localhost:5001"]

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)  # Servidor de replicación en el puerto 4000
