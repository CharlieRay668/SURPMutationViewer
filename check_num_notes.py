import pandas as pd

df = pd.read_csv("random_sample.csv")
# Check if the "Notes" column contains any notes
num_notes = df["Notes"].notna().sum()
print(num_notes)

# extract the mutant source, mutant destination, and notes columns
human_verified = df.copy()
human_verified = human_verified.dropna(subset=["Notes"])
human_verified.to_csv("human_verified.csv", index=False)
