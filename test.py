import numpy as np
import pandas as pd
import datetime
import json

def csv_to_json(filename, header=None):
    data = pd.read_csv(filename, header=header)
    data.replace({np.nan: None}, inplace=True)
    return data.to_dict(orient='records') 

# Load data
data = csv_to_json('./static/horse.csv', header=0)

print(np.random.choice([h['hospital_number'] for h in data], 3, replace=False).tolist())