import requests
import json
import pandas as pd


"""
SETUP URLS
"""
URL_BASE = 'http://127.0.0.1:8000/'
TK_URL = URL_BASE + 'token'
POSTS_URL = URL_BASE + 'posts/'
USERS_URL = URL_BASE + 'users/'
MATRIX_URL = URL_BASE + 'matrices/'
POINTS_URL = URL_BASE + 'points/'
SCORES_URL = URL_BASE + 'scores/'


"""
CREDENTIALS
"""
username = 'testuser'
wachtwoord = 'Welkom01!'

headers = {
    "accept": "application/json"
    }

params = {
    "username": username,
    "password": wachtwoord,
    }


"""
GET TOKEN
"""
resp = requests.post(TK_URL, headers=headers, data=params)
tk = json.loads(resp.text)['access_token']
print(tk)


"""
GET MATRICES
"""
# define headers
headers = {
    "accept" : "application/json",
    "Authorization": "Bearer " + str(tk),
    }

# get posts
resp = requests.get(MATRIX_URL, headers=headers)
matrices = resp.text
matrices = json.loads(matrices)

for matrix in matrices:
    print(matrix)
    print("-------------------------------------------------------------------------------")


"""
GET POINTS
"""
# define headers
headers = {
    "accept" : "application/json",
    "Authorization": "Bearer " + str(tk),
    }

# get posts
resp = requests.get(POINTS_URL, headers=headers)
points = resp.text
points = json.loads(points)

for point in points:
    print(point)
    print("-------------------------------------------------------------------------------")
    
    
"""
GET SCORES with points as input
"""    
# define headers
headers = {
    "accept" : "application/json",
    "Authorization": "Bearer " + str(tk),
    }

# define body with data
list_vars = ['varname', 'unit_points', 'section']

data_points = [{v: x[v] for v in list_vars} for x in points]

params = data_points

resp = requests.post(SCORES_URL, headers=headers, data=json.dumps(params))
print(resp.text)

df = pd.DataFrame(json.loads(resp.text))
df = df.sort_values(by=['total_sum'], ascending=[False])
