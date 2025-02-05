def test_main():
    import requests
    import json

    geo_info = {
    "gridConfig": {
        "cellSize": 100,
        "bounds": {
        "north": 37.8120,
        "south": 37.7080,
        "east": -122.3549,
        "west": -122.5157
        }
    },
    "heightLimits": {
        "default": 0,
        "options": [40, 65, 80, 85, 105, 130, 140, 240, 300]
    },
    "cells": {
        "10_15": {
        "heightLimit": 65,
        "category": "residential",
        "lastUpdated": "2024-02-20",
        "bbox": {
            "north": 37.7371,
            "south": 37.7261,
            "east": -122.4887,
            "west": -122.4997
        }
        },
        "10_16": {
        "heightLimit": 85,
        "category": "mixed_use",
        "lastUpdated": "2024-02-20",
        "bbox": {
            "north": 37.7371,
            "south": 37.7261,
            "east": -122.4777,
            "west": -122.4887
        }
        }
    }
    }

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
        "demographics": demographics,
        "geo_info": geo_info
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post("http://172.25.184.18:5050/discuss", json=params, headers=headers)
    if response.status_code != 200:
        print("Error:", response)
        exit()
    else:
        result = response.json()
        print("Simulation result:")
        print(result)
    
    with open('example_results.json', 'w') as f:
        json.dump(result, f, indent=4)

def test_openai():
    from src.utils import OpenAIClient
    messages = [{ "role": "user", "content": "Say this is a test" }]
    client = OpenAIClient()
    response = client.chat(messages)
    print(response)
    
if __name__ == "__main__":
    test_main()
    # test_openai()