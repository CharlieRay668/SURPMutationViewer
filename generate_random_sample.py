import pandas as pd

def isCondElseToFalse(row):
    if row["MutatorType"] == "RC-cond->true":
        if "else" in row["MutantSource"] and "else" not in row["MutantDestination"]:
            return True
    return False



df = pd.read_csv("mutation_report.csv")

survived = df[df["Result"] == "passed"]

survived["isCondElseToFalse"] = survived.apply(isCondElseToFalse, axis=1)
survived = survived[survived["isCondElseToFalse"] == False]


sample = survived.sample(n=100)

sample.to_csv("random_sample.csv", index=False)