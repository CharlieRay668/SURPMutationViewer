import pandas as pd

df = pd.read_csv("random_sample.csv")

df["Result"] = df["Result"].apply(lambda x : "Killed" if x == "failed" else "Survived")

df.to_csv("random_sample.csv", index=False)

df = pd.read_csv("mutation_report.csv")

df["Result"] = df["Result"].apply(lambda x : "Killed" if x == "failed" else "Survived")

df.to_csv("mutation_report.csv", index=False)