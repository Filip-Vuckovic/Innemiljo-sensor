import requests

data = {'data1':1, 'data2':2, 'data3':3}

r = requests.post('http://127.0.0.1:5000/api/post', json=data)
print('Status Code:', r.status_code)
print('Data received:', r.json())