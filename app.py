from flask import Flask, request
import requests
import os

app = Flask(__name__)

def acortar(url):
    r = requests.get("https://tinyurl.com/api-create.php", params={"url": url})
    return r.text

@app.route("/webhook", methods=["POST"])
def webhook():
    lat = request.values.get("Latitude")
    lon = request.values.get("Longitude")

    if lat and lon:
        waze = f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"
        maps = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

        waze_corto = acortar(waze)
        maps_corto = acortar(maps)

        mensaje = f"""📍 Ubicación recibida

🚗 Waze:
{waze_corto}

🗺️ Google Maps:
{maps_corto}
"""
    else:
        mensaje = "Reenviame una ubicación de WhatsApp 📍"

    # RESPUESTA EN FORMATO TWIML
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{mensaje}</Message>
</Response>""", 200, {"Content-Type": "application/xml"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
