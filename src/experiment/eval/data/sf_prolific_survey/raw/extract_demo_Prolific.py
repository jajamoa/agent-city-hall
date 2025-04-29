import csv
import json

def extract_housing_data(csv_file_path):
    """
    Extract specific data from San Francisco Housing Survey CSV file and format it into JSON.
    
    Args:
        csv_file_path (str): Path to the CSV file
        
    Returns:
        list: List of dictionaries containing formatted data
    """
    results = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Extract the required fields
            data = {
                "id": row["Prolific ID"],
                "coordinates": {
                    "lat": None,
                    "lng": None
                },
                "agent": {
                    "age": map_age_to_number(row["What is your age?"]),
                    "Geo Mobility": map_mobility(row["Have you moved in the past year?"]),
                    "householder type": map_housing_status(row["What best describes your housing status?"]),
                    "Gross rent": map_rent_percentage(row["If you rent, what is your approximate monthly rent as a percentage of your income?"]),
                    "means of transportation": map_transportation(row["What is your primary mode of transportation? (Please select all that apply)"]),
                    "income": map_income(row["What is your annual household income?"]),
                    "occupation": row["Which of the following best describes your occupation?"]
                }
            }
            
            results.append(data)
    
    return results

def map_age_to_number(age_range):
    """Map age range to a representative number"""
    age_mapping = {
        "18-24": 21,
        "25-29": 27,
        "30-34": 32,
        "35-39": 37,
        "40-44": 42,
        "45-49": 47,
        "50-54": 52,
        "55-59": 57,
        "60-64": 62,
        "65-69": 67,
        "70-74": 72,
        "75+": 77
    }
    return age_mapping.get(age_range, 29)  # Default to 29 if not found

def map_mobility(mobility_status):
    """Map mobility status to the required format"""
    if "Same house" in mobility_status:
        return "Did not move"
    else:
        return "Moved from different state"  # Default value as per requirements

def map_housing_status(status):
    """Map housing status to the required format"""
    if "Renter" in status:
        return "Renter occupied"
    elif "Owner" in status:
        return "Owner occupied"
    else:
        return "Renter occupied"  # Default to renter occupied

def map_rent_percentage(percentage):
    """Map rent percentage to the required format"""
    percentage_mapping = {
        "Less than 15.0 percent": "Less than 15.0 percent",
        "15.0 to 19.9 percent": "15.0-19.9 percent",
        "20.0 to 24.9 percent": "20-24.9 percent",
        "25.0 to 29.9 percent": "25.0-29.9 percent",
        "30.0 to 34.9 percent": "30.0-34.9 percent",
        "35.0 percent or more": "35.0 percent or more"
    }
    return percentage_mapping.get(percentage, "20-24.9 percent")  # Default to 20-24.9 percent if not found

def map_transportation(transportation):
    """Map transportation to the required format"""
    if "Public transit" in transportation:
        return "Public transportation"
    elif "Bicycle" in transportation:
        return "Bicycle"
    elif "Walk" in transportation:
        return "Walked"
    elif "Drive" in transportation or "Car" in transportation:
        return "Car, truck, or van"
    elif "work from home" in transportation.lower() or "remote" in transportation.lower():
        return "Worked from home"
    else:
        return "Worked from home"  # Default to worked from home as per requirements

def map_income(income):
    """Map income to the required format"""
    if "$200,000 or more" in income:
        return "With income:!!$200,000 or more"
    elif "$150,000" in income:
        return "With income:!!$150,000 to $199,999"
    elif "$100,000" in income:
        return "With income:!!$100,000 to $149,999"
    elif "$50,000" in income:
        return "With income:!!$75,000 or more"
    elif "$25,000" in income:
        return "With income:!!$25,000 to $49,999"
    elif "Less than $25,000" in income:
        return "With income:!!Less than $25,000"
    else:
        return "With income:!!$75,000 or more"  # Default to $75,000 or more as per requirements

def main():
    # Define the path to your CSV file
    csv_file_path = "./response.csv" # TODO: change to the path of the csv file
    
    # Extract data
    extracted_data = extract_housing_data(csv_file_path)
    
    # Write to JSON file
    with open("responses.json", 'w', encoding='utf-8') as json_file:
        json.dump(extracted_data, json_file, indent=4)
    
    print(f"Extraction complete. Data saved to responses.json")
    print(f"Total records processed: {len(extracted_data)}")
    
    # Print the first record as an example
    if extracted_data:
        print("\nSample record:")
        print(json.dumps(extracted_data[0], indent=4))

if __name__ == "__main__":
    main()