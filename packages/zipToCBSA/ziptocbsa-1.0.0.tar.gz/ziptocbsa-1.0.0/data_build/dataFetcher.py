from datetime import datetime, timezone
import json
import pandas as pd
import requests

# return a Pandas Dataframe of HUD USPS Crosswalk values

# Note that type is set to 1 which will return values for the ZIP to CBSA file and query is set to ALL which will return Zthe full document
url = "https://www.huduser.gov/hudapi/public/usps?type=3&query=ALL&year=2025"
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI2IiwianRpIjoiY2NhYTA0NDM1ZjlhYzJmZGRlMTU4YzVkMjNmY2M5ZDIwZDk3MTY4ZjVjZDMyZmJkMzk0NmFlZjY1MTlmZGQwYjRiMWYyZGZhMzM3YWU1ZTYiLCJpYXQiOjE3NjcwNjY5NTUuMjE4Mzg2LCJuYmYiOjE3NjcwNjY5NTUuMjE4Mzg4LCJleHAiOjIwODI1OTk3NTUuMjE0NjEyLCJzdWIiOiIxMTYwMzAiLCJzY29wZXMiOltdfQ.Bkhn1FEjpsibukEslPu6RTZr5hFwITLWsHsd7ILr5YsRKy0cnVgd8osksG3iTgAXx9pGA_F_9ztb-M95zegJZw"
headers = {"Authorization": "Bearer {0}".format(token)}

response = requests.get(url, headers = headers)

if response.status_code != 200:
	print ("Failure, see status code: {0}".format(response.status_code))
else:
	df = pd.DataFrame(response.json()["data"]["results"])
	df.to_csv('output/zip-cbsa.csv', index=False)

	num_rows = df.shape[0]

	now = datetime.now(timezone.utc).isoformat()

	data = {
		"data_version": "2025",
		"source": "HUD USPS ZIP CODE CROSSWALK",
		"generated_at": now,
		"rows": num_rows,
	}

	jsonPath = "output/metadata.json"

	try:
		with open( jsonPath, "w") as json_file:
			json.dump(data, json_file, indent=4) # Using indent for human-readable formatting
		print(f"Data successfully saved to {jsonPath}")
	except IOError as e:
		print(f"Error saving file: {e}")
