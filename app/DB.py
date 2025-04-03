# THE DATA WAS FROM
# https://data.opendatasoft.com/explore/dataset/all-vehicles-model%40public/information/?sort=modifiedon
import pandas as pd
pd.__version__ 

df = pd.read_csv("app\Database\Cars_data_2024.csv", delimiter=";")
print(df.columns)

while True:
	make = input("Brand: ").lower()
	model = input("Model: ").lower()
	year = int(input("Year made: "))

	filtered = df[
		(df["Make"].str.lower() == make) &
		(df["Year"] == year) &
		(df["baseModel"].str.lower() == model)
	]

	print(filtered[
		[
			"Make", "Model", "Year",
			"Range For Fuel Type1",
			"Range  City For Fuel Type1"
		]
	])

	reset = input("Again? (Enter to exit)")

	if not reset:
		break