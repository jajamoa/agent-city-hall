import requests

region = "kendall square"
population = 100000
proposal = {
    "title": "Kendall Square",
    "description": "The Kendall Square Mixed-Use Development is a proposed 5-story, 85,000-square-foot building in Cambridge, MA, combining residential, commercial, and public green space. The project allocates 50% of the space to 35 residential units (15 one-bedroom, 15 two-bedroom, and 5 three-bedroom), 30% to retail and dining (25,500 sq. ft.), and 20% to public and rooftop green spaces (17,000 sq. ft.). It includes 20 underground parking spaces (15 for residents, 5 for commercial use) and aims to meet LEED Gold standards with solar panels and advanced stormwater management. While complying with mixed-use zoning, it requires a height variance for exceeding the 60-foot limit. Key impacts include a 15% increase in parking demand, a net gain of 6 trees, and a projected daily increase of 120 pedestrian trips. Community concerns focus on height, parking, and green space preservation, balanced against the project’s contribution to housing and commercial opportunities."
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
response = requests.post("http://172.25.184.18:5050/discuss", json=params, headers=headers)
if response.status_code != 200:
    print("Error:", response.json())
    exit()
else:
    result = response.json()
    print("Simulation result:")
    print(result)