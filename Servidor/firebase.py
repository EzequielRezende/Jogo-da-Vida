import requests
import json

print(requests.get('https://jogodavida-2020-default-rtdb.firebaseio.com/jogos/idjogo.json').text)

payload  = json.dumps({'key1': 'value1', 'key2': 'value2'})
headers = {'content-type': 'application/json'}
print(requests.put('https://jogodavida-2020-default-rtdb.firebaseio.com/jogos/idjogo/teste.json', data=payload ).text)

