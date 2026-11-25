import pandas as pd 
import numpy as np 

df = pd.read_csv("output/preprocess_results.csv")


#Read in population numbers (to get rates)
df_eth_pops=pd.read_csv("analysis/eth_denoms.csv")
df_eth_pops = df_eth_pops.rename(columns={"Age brackets": "Age group"})
df_eth_pops["Age group"] = df_eth_pops["Age group"].str.replace("Age", "", regex=False).str.strip()
df_eth_pops["Age group"] = df_eth_pops["Age group"].str.replace(" to ", "-", regex=False).str.strip()
df_eth_pops["Age group"] = df_eth_pops["Age group"].str.replace(" and over", "+", regex=False).str.strip()
decile_columns = ["Asian","Black","Mixed","Other","White"]
df_eth_pops = df_eth_pops.melt(
    id_vars=[col for col in df_eth_pops.columns if col not in decile_columns],
    value_vars=decile_columns,
    var_name="ethnicity_group",
    value_name="population",
)


# Add the combined 15-24 age band by summing its component age bands.
eth_pop_group_cols = [col for col in df_eth_pops.columns if col not in ["Age group", "population"]]
df_eth_15_24 = (
    df_eth_pops.loc[df_eth_pops["Age group"].isin(["15-17", "18-24"])]
    .groupby(eth_pop_group_cols, as_index=False)["population"]
    .sum()
)
df_eth_15_24["Age group"] = "15-24"
df_eth_pops = pd.concat([df_eth_pops, df_eth_15_24], ignore_index=True)
df_eth_pops = df_eth_pops.loc[~df_eth_pops["Age group"].isin(["15-17", "18-24"])]




#Get IMD numbers 
df_imd_pops=pd.read_csv("analysis/imd_denoms.csv")
decile_columns = [str(i) for i in range(1, 11)]
df_imd_pops = df_imd_pops.melt(
    id_vars=[col for col in df_imd_pops.columns if col not in decile_columns],
    value_vars=decile_columns,
    var_name="imd_decile",
    value_name="population",
)

df_imd_pops.imd_decile=df_imd_pops.imd_decile.astype(int)

# Add the combined 15-24 age band by summing its component age bands.
imd_pop_group_cols = [col for col in df_imd_pops.columns if col not in ["Age group", "population"]]
df_imd_15_24 = (
    df_imd_pops.loc[df_imd_pops["Age group"].isin(["15-19", "20-24"])]
    .groupby(imd_pop_group_cols, as_index=False)["population"]
    .sum()
)
df_imd_15_24["Age group"] = "15-24"
df_imd_pops = pd.concat([df_imd_pops, df_imd_15_24], ignore_index=True)
df_imd_pops = df_imd_pops.loc[~df_imd_pops["Age group"].isin(["15-19", "20-24"])]

# Add the combined 85+ age band by summing its component age bands.
df_imd_85_plus = (
    df_imd_pops.loc[df_imd_pops["Age group"].isin(["85-89", "90+"])]
    .groupby(imd_pop_group_cols, as_index=False)["population"]
    .sum()
)
df_imd_85_plus["Age group"] = "85+"
df_imd_pops = pd.concat([df_imd_pops, df_imd_85_plus], ignore_index=True)
df_imd_pops = df_imd_pops.loc[~df_imd_pops["Age group"].isin(["85-89", "90+"])]


#Clean text, for join 
df_pops = pd.read_csv("analysis/europeanpops.csv")
df_pops["AgeGroup"] = df_pops["AgeGroup"].str.replace(" years", "").str.replace("plus", "+")


df_pops = pd.concat([df_pops, pd.DataFrame({"AgeGroup":"15-24","EuropeanStandardPopulation":df_pops.loc[df_pops["AgeGroup"].isin(["15-19", "20-24"]),"EuropeanStandardPopulation"].sum()}, index=[0])], ignore_index=True)
df_pops = df_pops.loc[~df_pops["AgeGroup"].isin(["15-19", "20-24"])]


df_pops = pd.concat([df_pops, pd.DataFrame({"AgeGroup":"85+","EuropeanStandardPopulation":df_pops.loc[df_pops["AgeGroup"].isin(["85-89", "90+"]),"EuropeanStandardPopulation"].sum()}, index=[0])], ignore_index=True)
df_pops = df_pops.loc[~df_pops["AgeGroup"].isin(["85-89", "90+"])]


#Normalize the population (to max)
df_pops["EuropeanStandardPopulation"] = df_pops["EuropeanStandardPopulation"]/df_pops["EuropeanStandardPopulation"].max()
df_pops=df_pops.rename(axis=1,mapper={"EuropeanStandardPopulation":"weights"})



#The standard population tops out at 90+, so collapse the finer top age bands and drop missing ages
df = df.loc[df["age_group"].notna()].copy()
df["age_group"] = df["age_group"].replace({"90-94": "90+", "95+": "90+"})
keys = ["measure", "interval_start", "interval_end", "age_group", "sex", "imd_quintile", "ethnicity_group"]
df = df.groupby(keys, dropna=False, as_index=False)[["unique_attenders", "total_attendances"]].sum()

# Add the combined 15-24 age band by summing its component age bands.
df_group_cols = [col for col in keys if col != "age_group"]
df_15_24 = (
    df.loc[df["age_group"].isin(["15-19", "20-24"])]
    .groupby(df_group_cols, dropna=False, as_index=False)[["unique_attenders", "total_attendances"]]
    .sum()
)
df_15_24["age_group"] = "15-24"
df = pd.concat([df, df_15_24], ignore_index=True)
df = df.loc[~df["age_group"].isin(["15-19", "20-24"])]

# Add the combined 85+ age band by summing its component age bands.
df_85_plus = (
    df.loc[df["age_group"].isin(["85-89", "90+"])]
    .groupby(df_group_cols, dropna=False, as_index=False)[["unique_attenders", "total_attendances"]]
    .sum()
)
df_85_plus["age_group"] = "85+"
df = pd.concat([df, df_85_plus], ignore_index=True)
df = df.loc[~df["age_group"].isin(["85-89", "90+"])]

#Add in the year as a separate column for the join 
df["interval_start"] = pd.to_datetime(df["interval_start"])
df["year"] = df["interval_start"].dt.year


#Merge for ethnicity
df_eth=df.merge(df_eth_pops[df_eth_pops.Year==max(df_eth_pops.Year)].rename(mapper={"Age group":"age_group"},axis=1),
            on=["age_group", "ethnicity_group"], how="left")
#Get only data where we have an ethnicity
df_eth = df_eth.loc[df_eth["ethnicity_group"].notna()] 
#Calculate rates
df_eth["unique_attenders"] = np.round(df_eth["unique_attenders"] / 5) * 5
df_eth["total_attendances"] = np.round(df_eth["total_attendances"] / 5) * 5
df_eth["unique_attenders"] = np.where(df_eth["unique_attenders"]<10, 10, df_eth["unique_attenders"])
df_eth["total_attendances"] = np.where(df_eth["total_attendances"]<10, 10, df_eth["total_attendances"])
df_eth["rate_attenders"] = df_eth["unique_attenders"]/df_eth["population"]*10000
df_eth["rate_attendances"] = df_eth["total_attendances"]/df_eth["population"]*10000

#Age-standardize 
df_eth_as = df_eth.merge(df_pops, left_on="age_group",right_on="AgeGroup", how="left").groupby(["interval_start","ethnicity_group","age_group"]).apply(lambda x: pd.Series({"weighted_rate_attenders": np.average(x.rate_attenders, weights=x.weights), 
                                                                                    "weighted_rate_attendances": np.average(x.rate_attendances, weights=x.weights)})).reset_index()

#Repeat for IMD
df_imd=df.merge(df_imd_pops[df_imd_pops.Year==max(df_imd_pops.Year)].rename(mapper={"imd_decile":"imd_quintile","Age group":"age_group"},axis=1),
            on=["age_group", "imd_quintile"], how="left")
df_imd = df_imd.loc[df_imd["imd_quintile"].notna()] 



# Mask/ censor and calculate rates
df_imd["unique_attenders"] = np.round(df_imd["unique_attenders"] / 5) * 5
df_imd["total_attendances"] = np.round(df_imd["total_attendances"] / 5) * 5
df_imd["unique_attenders"] = np.where(df_imd["unique_attenders"]<10, 10, df_imd["unique_attenders"])
df_imd["total_attendances"] = np.where(df_imd["total_attendances"]<10, 10, df_imd["total_attendances"])
df_imd["rate_attenders"] = df_imd["unique_attenders"]/df_imd["population"]*10000
df_imd["rate_attendances"] = df_imd["total_attendances"]/df_imd["population"]*10000

df_imd_as = df_imd.merge(df_pops, left_on="age_group",right_on="AgeGroup", how="left").groupby(["interval_start","imd_quintile","age_group"]).apply(lambda x: pd.Series({"weighted_rate_attenders": np.average(x.rate_attenders, weights=x.weights), 
                                            "weighted_rate_attendances": np.average(x.rate_attendances, weights=x.weights)})).reset_index()

#Export
df_imd_as.to_csv("output/age_standardized_imd.csv", index=False)
df_eth_as.to_csv("output/age_standardized_eth.csv", index=False)

#Age standardize the sex 
df2 = df.merge(df_pops, left_on="age_group",right_on="AgeGroup", how="left")

for grouping in ["sex"]:#,"imd_quintile","ethnicity_group"]:
    df2_=df2.loc[df2[grouping].notna()].copy()
    df2_["unique_attenders"] = np.round(df2_["unique_attenders"] / 5) * 5
    df2_["total_attendances"] = np.round(df2_["total_attendances"] / 5) * 5
    df2_["unique_attenders"] = np.where(df2_["unique_attenders"]<10, 10, df2_["unique_attenders"])
    df2_["total_attendances"] = np.where(df2_["total_attendances"]<10, 10, df2_["total_attendances"])
    # df2_["rate_attenders"] = df2_["unique_attenders"]/df2_["population"]*10000
    # df2_["rate_attendances"] = df2_["total_attendances"]/df2_["population"]*10000
    df2_as = df2_.groupby(["measure", "interval_start", grouping]).apply(lambda x: pd.Series({"weighted_attenders": np.average(x.unique_attenders, weights=x.weights), 
                                                                                    "weighted_attendances": np.average(x.total_attendances, weights=x.weights)}))
    df2_as.to_csv(f"output/age_standardized_{grouping}.csv")
