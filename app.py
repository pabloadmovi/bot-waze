from flask import Flask, request
import requests
import os
import re

app = Flask(__name__)

# 🔗 Acortar URLs con TinyURL
def acortar(url):
    r = requests.get("https://tinyurl.com/api-create.php", params={"url": url})
    return r.text.replace("https://", "")  # Quitamos https:// para evitar previews y títulos largos

# 📍 Extraer coordenadas escritas en texto
def extraer_coordenadas(texto):
    patron = r"-?\d+\.\d+"
    nums = re.findall(patron, texto)
    if len(nums) >= 2:
        return nums[0], nums[1]
    return None, None

# 🌍 Extraer coordenadas desde links de Google Maps
def extraer_coordenadas_de_url(texto):
    urls = re.findall(r'(https?://\S+)', texto)
    
    for url in urls:
        try:
            # Seguir redirecciones (para links cortos de Google Maps)
            r = requests.get(url, allow_redirects=True, timeout=5)
            final_url = r.url

            # Buscar coordenadas en la URL final
            patron = r"[-]?\d+\.\d+,[-]?\d+\.\d+"
            match = re.search(patron, final_url)
            if match:
                lat, lon = match.group().split(",")
                return lat, lon

        except:
            continue

    return None, None


@app.route("/webhook", methods=["POST"])
def webhook():
    lat = request.values.get("Latitude")
    lon = request.values.get("Longitude")
    texto = request.values.get("Body", "")
    num_media = int(request.values.get("NumMedia", 0))

    media_url = request.values.get("MediaUrl0") if num_media > 0 else None

    # 1️⃣ Ubicación directa de WhatsApp
    if not lat or not lon:
        lat, lon = extraer_coordenadas(texto)

    # 2️⃣ Coordenadas dentro de links de Google Maps
    if not lat or not lon:
        lat, lon = extraer_coordenadas_de_url(texto)

    if lat and lon:
        waze = f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"
        maps = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

        waze_corto = acortar(waze)
        maps_corto = acortar(maps)

        mensaje = f"""📍 Datos recibidos

📝 Nota:
{texto if texto else '—'}

🚗 Waze (abrir navegación):
{waze_corto}

🗺️ Google Maps (abrir mapa):
{maps_corto}
"""

        if media_url:
            mensaje += "\n📸 Foto recibida correctamente"

    else:
        mensaje = "Mandame una ubicación, coordenadas o link de Google Maps 📍"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{mensaje}</Message>
</Response>""", 200, {"Content-Type": "application/xml"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
