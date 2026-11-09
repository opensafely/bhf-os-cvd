import pandas as pd 
import numpy as np 

df = pd.read_csv("output/preprocess_results.csv")
df_pops = pd.read_csv("analysis/europeanpops.csv")


#Clean text, for join 
df_pops["AgeGroup"] = df_pops["AgeGroup"].str.replace(" years", "").str.replace("plus", "+")
#Normalize the population (to max)
df_pops["EuropeanStandardPopulation"] = df_pops["EuropeanStandardPopulation"]/df_pops["EuropeanStandardPopulation"].max()

df_pops=df_pops.rename(axis=1,mapper={"EuropeanStandardPopulation":"weights"})

#The standard population tops out at 90+, so collapse the finer top age bands and drop missing ages
df = df.loc[df["age_group"].notna()].copy()
df["age_group"] = df["age_group"].replace({"90-94": "90+", "95+": "90+"})
keys = ["measure", "interval_start", "interval_end", "age_group", "sex", "imd_quintile", "ethnicity_group"]
df = df.groupby(keys, dropna=False, as_index=False)[["unique_attenders", "total_attendances"]].sum()

#Merge
df2 = df.merge(df_pops, left_on="age_group",right_on="AgeGroup", how="left")

#Perform standardization

for grouping in ["sex","imd_quintile","ethnicity_group"]:
    df2_=df2.loc[df2[grouping].notna()]
    df2_ = df2_.groupby(["measure", "interval_start", grouping]).apply(lambda x: pd.Series({"weighted_attenders": np.average(x.unique_attenders, weights=x.weights), 
                                                                                    "weighted_attendances": np.average(x.total_attendances, weights=x.weights)}))
    df2_.to_csv(f"output/age_standardized_{grouping}.csv")




#Export
df2.to_csv("output/age_standardized_results.csv", index=False)