import pandas as pd

df = pd.read_csv("app\Database\Cars_data_2024.csv", encoding="ISO-8859-1")

columns = ['Company Names', 'Cars Names', 'Engine', 'Fuel Type','Performance', 'Seats', 'Torque', 'Cars Prices']

df['Seats'] = df['Seats'].astype(str)
df['Performance'] = df['Performance'].astype(str)
df['Cars Prices'] = df['Cars Prices'].astype(str)
df['Company Names'] = df['Company Names'].astype(str)
df['Cars Names'] = df['Cars Names'].astype(str)
df['Parsed Price'] = (df['Cars Prices'].str.extract(r'(\d+)').astype(float))

df = df.dropna(subset=['Parsed Price']).reset_index(drop=True)

match_fields = ['Company Names', 'Engine', 'Fuel Type','Performance', 'Seats', 'Torque']

recommendation_cols = ['Recommendation 1', 'Recommendation 2', 'Recommendation 3','Recommendation 4', 'Recommendation 5']
recommendations_df = pd.DataFrame(columns=recommendation_cols)
recommendations_df = recommendations_df.reindex(df.index)
recommendations_df[recommendation_cols] = ""

for x, row in df.iterrows():
    if x % 100 == 0:
        print(f"Processing row {x}/{len(df)}")
    matches = (df[match_fields] == row[match_fields]).sum(axis=1)

    price_match = df['Parsed Price'].sub(row['Parsed Price']).abs() <= 10000
    matches += price_match.astype(int)

    matches[x] = -1  

    top = matches.sort_values(ascending=False).head(5).index
    top_recs = df.loc[top, ['Company Names', 'Cars Names']].astype(str).agg(' '.join, axis=1).tolist()

    while len(top_recs) < 5:
        top_recs.append("")

    recommendations_df.loc[x] = top_recs

df = pd.concat([df, recommendations_df], axis=1)

df.to_csv("Cars_data_with_recommendations.csv", index=False)

