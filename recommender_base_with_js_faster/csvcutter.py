import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('data/ratings.csv')

# Group by user_id and shuffle the ratings within each group
df_shuffled = df.groupby('userId', group_keys=False).apply(lambda x: x.sample(frac=1, random_state=42))

# Select the first 10 ratings for each user
df_selected = df_shuffled.groupby('userId').head(1)

# Save the result to a new CSV file
df_selected.to_csv('user_init_ratings.csv', index=False)