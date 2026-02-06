from flask import Flask, request
import requests
import os
import re

app = Flask(__name__)

def acortar(url):
    r = requests.get("https://tinyurl.com/api-create.php", params={"url": url})
    return r.text

@app.route("/webhook", methods=["POST"])
def webhook():
    lat = request.values.get("Latitude")
    lon = request.values.get("Longitude")
    texto = request.values.get("Body", "")
    num_media = int(request.values.get("NumMedia", 0))

    media_url = None
    if num_media > 0:
        media_url = request.values.get("MediaUrl0")

    # 1️⃣ Ubicación directa de WhatsApp
    if not lat or not lon:
        # 2️⃣ Coordenadas escritas
        lat, lon = extraer_coordenadas(texto)

    # 3️⃣ Coordenadas dentro de link de Google Maps
    if not lat or not lon:
        lat, lon = extraer_coordenadas_de_url(texto)


@app.route("/webhook", methods=["POST"])
def webhook():
    lat = request.values.get("Latitude")
    lon = request.values.get("Longitude")

    # Si no viene ubicación, intentar leer coordenadas del texto
    if not lat or not lon:
        mensaje_usuario = request.values.get("Body", "")
        lat, lon = extraer_coordenadas(mensaje_usuario)

    if lat and lon:
        waze = f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"
        maps = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

        waze_corto = acortar(waze)
        maps_corto = acortar(maps)

        mensaje = f"""📍 Datos recibidos

📝 Nota:
{texto if texto else '—'}

🚗 Waze (abrir navegación):
{waze_corto.replace("https://", "")}

🗺️ Google Maps (abrir mapa):
{maps_corto.replace("https://", "")}
"""
    else:
        mensaje = "Mandame una ubicación de WhatsApp o coordenadas tipo: -34.90, -56.16 📍"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{mensaje}</Message>
</Response>""", 200, {"Content-Type": "application/xml"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
