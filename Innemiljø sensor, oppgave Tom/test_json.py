import requests

r = requests.get('http://10.13.37.168/')
print(r.status_code)
#print(r.json())