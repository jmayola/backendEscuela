import requests
import json

# Define el payload con los datos a enviar
payload = {
    'text': 'bi ba buzemann!',
    'nouns': ['streetlight', 'situation'],
    'states': ['solid', 'fluid']
}

# URL del servidor
url = "http://localhost:3000"

try:
    # Enviar la solicitud POST al servidor con el payload en formato JSON
    response = requests.post(url, json=payload)

    # Comprobar si la solicitud fue exitosa
    if response.status_code == 200:
        print("Solicitud exitosa:", response.json())
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
        print("Respuesta del servidor:", response.text)

except requests.exceptions.RequestException as e:
    print(f"Error al realizar la solicitud: {e}")
