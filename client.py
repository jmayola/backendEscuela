import requests
import json

# Define el payload con los datos a enviar
payload = {
    'text': 'bi ba buzemann!',
    'nouns': ['streetlight', 'situation'],
    'states': ['solid', 'fluid']
}

# URL del servidor
url = "http://localhost:3000/user"

try:
    # Enviar la solicitud POST al servidor con el payload en formato JSON
    response = requests.get(url,headers={'Cookie':"users=MTcyOTc4NTU5NHxEWDhFQVFMX2dBQUJFQUVRQUFCTl80QUFBZ1p6ZEhKcGJtY01DZ0FJZFhObGNtNWhiV1VHYzNSeWFXNW5EQWdBQmtwMWJHbGhiZ1p6ZEhKcGJtY01Dd0FKZFhObGNsOTBlWEJsQm5OMGNtbHVad3dJQUFaaGJIVnRibTg9fDyMQ3waamZJ7ccpHQoh447o2a_oXNf9HByOvTUb-GMX"})# json=payload)

    # Comprobar si la solicitud fue exitosa
    if response.status_code == 200:
        print("Solicitud exitosa:", response.json())
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
        print("Respuesta del servidor:", response.text)

except requests.exceptions.RequestException as e:
    print(f"Error al realizar la solicitud: {e}")
