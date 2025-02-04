import pandas as pd
from census import Census
from us import states
pd.options.display.max_columns = 999
pd.options.display.max_rows = 999

# Load in your API key; replace API_KEY with your actual token
key = "0996d4010c55b9cdc008ffc0308f17e845ed29b1"
c = Census(key)
# Choose relevant census dataset
dataset = c.acs5
# Assign variable codes and their corresponding labels
variables = ('NAME', 'B01001_001E', 'B01001_004E', 'B19001_001E')

labels =    ('NAME', 'Estimate!!Total', 'Estimate!!Total:!!Male:!!5 to 9 years', 'Total household income')

# Choose desired geographic aggregation level
geo = 'county subdivision:*'
# Choose filter criteria (geographic extent)
county_code = '017'
criteria = f'state:{states.MA.fips} county:{county_code}'
# Run query and store as DataFrame
r = dataset.get(variables,
          { 'for': geo,
            'in' : criteria})
df = pd.DataFrame(r).rename(columns={v: l for v, l in zip(variables, labels)})
df['Estimate!!Total:!!Male:!!5 to 9 years - Ratio'] = df['Estimate!!Total:!!Male:!!5 to 9 years'] / df['Estimate!!Total']
print(df)