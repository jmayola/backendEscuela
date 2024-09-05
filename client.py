import requests
import json
payload={'text': 'bi ba buzemann!',
         'nouns': ['streetlight', 'situation'],
         'states': ['solid', 'fluid']
        }
url = "http://localhost:3000"
requests.post(url, data=json.dumps(payload))


