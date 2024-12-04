import requests

region = "boston"
population = 100000
proposal = {
    "title": "Ban all plastic bags",
    "description": "This proposal aims to ban all plastic bags in retail stores."
}

params = {"region": region}
headers = {"Content-Type": "application/json"}
response = requests.post("http://172.25.184.18:5050/lookup_demographics", params=params, headers=headers)
if response.status_code != 200:
    print("Error:", response.json())
    exit()
else:
    demographics = response.json()['demographics']
    print("Demographics for region:", region)
    print(demographics)
    
params = {
    "region": region,
    "population": population,
    "proposal": proposal,
    "demographics": demographics
}
headers = {"Content-Type": "application/json"}
response = requests.post("http://localhost:5050/discuss", json=params, headers=headers)
if response.status_code != 200:
    print("Error:", response.json())
    exit()
else:
    result = response.json()
    print("Simulation result:")
    print(result)