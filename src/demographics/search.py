import json
import logging

# add data loading path
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

class DemographicsSearchEngine:
    def __init__(self):
        self.data = json.loads(open('data/demographics.json').read())
        
    def search(self, region):
        if region in self.data:
            return self.data[region]
        else:
            # log message: region not found and use default region instead
            logging.warning(f"Region not found: {region}. Using default region instead.")
            return self.data["default"]