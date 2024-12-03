# API Documentation

## Overview
This backend for Agent City Hall provides two primary endpoints:

1. `/lookup_demographics` - Retrieves demographic information for a given region.
2. `/discuss` - Simulates a discussion based on demographics, population, and a proposal.

---

## API 1: **`/lookup_demographics`**

### **Description**
Retrieves demographic information for a specified region.

### **Method**
`POST`

### **Request Parameters**
- **Query String Parameters**:
  - `region` (string, required): The name of the region for which to fetch demographics. Must be provided in lowercase.

### **Response**
Returns demographic distributions for the specified region.

#### **Response Format**
```json
{
  "region": "boston",
  "demographics": {
    "age_distribution": {
      "18-25": 20,
      "26-40": 50,
      "41-60": 20,
      "60+": 10
    },
    "education_distribution": {
      "bachelor": 40,
      "high_school_or_below": 30,
      "postgraduate": 30
    },
    "gender_distribution": {
      "female": 50,
      "male": 50
    },
    "income_distribution": {
      "high_income": 20,
      "low_income": 30,
      "middle_income": 50
    },
    "occupation_distribution": {
      "blue_collar": 30,
      "retired": 10,
      "self_employed": 10,
      "white_collar": 50
    },
    "race_distribution": {
      "asian": 15,
      "black": 20,
      "hispanic": 10,
      "other": 5,
      "white": 50
    },
    "religion_distribution": {
      "christianity": 40,
      "islam": 20,
      "non_religious": 30,
      "other": 10
    }
  }
}
```

### **Error Responses**
- **400**: Missing or invalid `region` parameter.

  ```json
  {
    "error": "Region parameter is required."
  }
  ```
  
- **500**: Internal server error (e.g., if the demographics search engine fails).

  ```json
  {
    "error": "Error message here."
  }
  ```

---

## API 2: **`/discuss`**

### **Description**
Simulates a discussion based on the region, population, demographics, and a proposal.

### **Method**
`POST`

### **Request Body**
- **JSON**:
  - `region` (string, required): The name of the region.
  - `population` (integer, required): The population size for the simulation.
  - `proposal` (object, required): The proposal to discuss.
    - `title` (string, required): The title of the proposal.
    - `description` (string, required): A description of the proposal.
  - `demographics` (object, required): Demographic data, typically retrieved from the `/lookup_demographics` endpoint.

#### **Example Request**
```json
{
  "region": "boston",
  "population": 100000,
  "proposal": {
    "title": "Ban all plastic bags",
    "description": "This proposal aims to ban all plastic bags in retail stores."
  },
  "demographics": {
    "age_distribution": {
      "18-25": 20,
      "26-40": 50,
      "41-60": 20,
      "60+": 10
    },
    "gender_distribution": {
      "female": 50,
      "male": 50
    }
  }
}
```

### **Response**
Returns a summary of opinions and sample comments from simulated agents.

#### **Response Format**
```json
{
  "summary": {
    "summary_statistics": {
      "neutral": 10000,
      "oppose": 30000,
      "support": 60000
    },
    "supporter_reasons": {
      "economic_stimulus": 0.16666666666666666,
      "educational_opportunities": 0.16666666666666666,
      "infrastructure_improvement": 0.16666666666666666,
      "job_creation": 0.16666666666666666,
      "renewable_energy_initiatives": 0.16666666666666666,
      "technological_innovation": 0.16666666666666666
    },
    "opponent_reasons": {
      "community_dissatisfaction": 0.16666666666666666,
      "cultural_displacement": 0.16666666666666666,
      "environmental_destruction": 0.16666666666666666,
      "gentrification": 0.16666666666666666,
      "health_risks": 0.16666666666666666,
      "legal_uncertainty": 0.16666666666666666
    }
  },
  "comments": {
    "0": {
      "id": 0,
      "agent": {
        "age": "41-60",
        "education": "bachelor",
        "gender": "female",
        "income": "middle_income",
        "occupation": "white_collar",
        "race": "white",
        "religion": "non_religious"
      },
      "opinion": "support",
      "comment": "I fully support this initiative as it benefits the environment."
    },
    "...": "..."
  }
}
```

---

## How to Use

1. **Start the Server**:
   ```bash
   python main.py
   ```
   The server will run at `http://localhost:5050`.

2. **Fetch Demographics**:
   Use the `/lookup_demographics` API to get demographics for a specific region.

3. **Simulate a Discussion**:
   Use the `/discuss` API to run a simulation with the demographics, population size, and a proposal.

---

## Example Workflow

See test.py for an example workflow using the API endpoints.