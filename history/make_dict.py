import pandas as pd
import json
df = pd.read_csv("mappings.csv")
raw = df["raw_label"] 
sentence = df["Mapping"]

map_dict = {}
for i in range(len(raw)):
	map_dict[raw[i]] = sentence[i]

with open("mapping.json", 'w') as out:
	out.write(json.dumps(map_dict))