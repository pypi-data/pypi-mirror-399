import requests
import time
import json

class GeoEngine:
    DEFAULT_MANAGEMENT_URL = "https://api.geoengine.dev"
    DEFAULT_INGEST_URL = "http://ingest.geoengine.dev"

    def __init__(self, api_key, management_url=None, ingest_url=None):
        """
        Inicializa el cliente de GeoEngine.
        """
        if not api_key:
            raise ValueError("GeoEngine: API Key es requerida")

        self.api_key = api_key
        self.management_url = management_url or self.DEFAULT_MANAGEMENT_URL
        self.ingest_url = ingest_url or self.DEFAULT_INGEST_URL
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "User-Agent": "GeoEnginePython/1.0.0"
        }

    def send_location(self, device_id, lat, lng):
        """
        Envía una coordenada al motor de ingestión.
        """
        payload = {
            "device_id": device_id,
            "latitude": float(lat),
            "longitude": float(lng),
            "timestamp": int(time.time())
        }

        try:
            response = requests.post(
                f"{self.ingest_url}/ingest",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"GeoEngine Error: {e}")

    def create_geofence(self, name, coordinates, webhook_url):
        """
        Crea una geocerca.
        coordinates debe ser una lista de listas: [[lat, lng], [lat, lng]]
        """
        if len(coordinates) < 3:
            raise ValueError("Se requieren al menos 3 puntos")

        # Convertir [Lat, Lng] a [Lng, Lat] para GeoJSON
        polygon = [[p[1], p[0]] for p in coordinates]
        
        # Cerrar polígono
        if polygon[0] != polygon[-1]:
            polygon.append(polygon[0])

        payload = {
            "name": name,
            "webhook_url": webhook_url,
            "geojson": {
                "type": "Polygon",
                "coordinates": [polygon]
            }
        }

        try:
            response = requests.post(
                f"{self.management_url}/geofences",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if response.content:
                raise Exception(f"API Error: {response.json().get('error', response.text)}")
            raise Exception(f"Connection Error: {e}")