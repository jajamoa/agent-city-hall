# Evaluation Data

This directory contains data files used for the evaluation of housing policy opinion models.

## Directory Structure

The data is organized by data source, with each source having its own directory:

```
data/
├── sf_prolific_survey/   # Survey data from Prolific participants
│   ├── raw/              # Raw CSV survey files
│   └── processed/        # Processed demographic and reaction data
│
├── sf_rezoning_plan/     # San Francisco rezoning plan data
│   ├── raw/              # Raw GeoJSON files and processing scripts
│   └── processed/        # Processed rezoning proposals
│
├── samples/              # Sample data files for testing
│
└── README.md             # This file
```

## Data Sources

### SF Prolific Survey

Contains survey responses from participants on Prolific regarding their opinions on various housing policy scenarios in San Francisco. Each participant provided demographic information and rated different housing policy scenarios.

### SF Rezoning Plan

Contains geospatial data on San Francisco zoning policies, including both current zoning and proposed rezoning plans. This data is used to create policy scenarios that survey participants respond to.

### Samples

Contains sample data files used for testing and development purposes. 