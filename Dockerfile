# Usar la imagen base de Python
FROM python:3.13

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los requisitos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto
EXPOSE 5001

# 🔥 Configurar la zona horaria dentro del contenedor (para PostgreSQL y el sistema)
ENV TZ=America/Bogota

RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# 🔄 Esperar a que PostgreSQL esté listo antes de ejecutar el script
CMD ["sh", "-c", "sleep 5 && python create_db.py && python server2.py"]
