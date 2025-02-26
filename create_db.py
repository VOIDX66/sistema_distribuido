import psycopg2
from psycopg2 import sql

# Variables de conexión
DB_USER = "cliente_sistema"
DB_PASSWORD = "misistema"
DB_HOST = "postgres_db"  # Nombre del servicio en docker-compose
DB_NAME = "my_db"

# Conectar a PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
)
cur = conn.cursor()

# Crear las tablas si no existen
cur.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    cantidad INT NOT NULL DEFAULT 0,
    precio NUMERIC(10,2) NOT NULL DEFAULT 0,
    ultima_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS sincronizacion (
    id SERIAL PRIMARY KEY,
    servidor VARCHAR(255) UNIQUE NOT NULL,
    ultimo_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Guardar cambios y cerrar conexión
conn.commit()
cur.close()
conn.close()

print("Base de datos inicializada correctamente.")
