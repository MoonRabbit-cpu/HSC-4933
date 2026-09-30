################################################
# Bryan Hernandez Rodriguez -----------        #
# IC4.py:             Pandas                   #
# Data Cleaning and Summarization with Pandas  #
################################################

#Imports
import pandas as pd
import numpy as np

df = pd.read_csv("eye_health_behavioral_risk_factors_dataset_2022_brfss.csv")
print(df.shape,
      df.dtypes,
      df.isnull().sum(), #print total number of NaN velues
      df.nunique(),
      sep="\n"
      )

print("Duplicates:", df.duplicated().sum())

df = df.dropna(axis=1, how='all') #drop columnes with no data (only NaN)
df = df.drop(columns=[c for c in df.columns if c.endswith("ID")]) # Drops columns that end in "ID"

df = df.dropna(subset=["Data_Value"]) #drop rows with no value in the column "Data_Value"
df = df.drop(columns=["Geolocation","Data_Value_Footnote_Symbol",\
                      "Data_Value_Footnote","StateAbbr","NonWeightedSample",\
                      "Geographic Level","Numerator"])
df.columns = df.columns.str.lower().str.replace(" ", "_") #Make column headers snake_case
df["error"] = (df["high_confidence_limit"] - df["low_confidence_limit"]) /2# Creates a new column "error"
df["prevalence_level"] = np.select([df["data_value"] < 5, df["data_value"] <= 7],\
                                   ["Low","Medium"],"High") #Creates prevalence level descriptor
df.to_csv("eye_health_2022_clean.csv", index=False) #save to csv the different name
print(pd.read_csv("eye_health_2022_clean.csv").shape == df.shape) #print t/f in dimensions match
print(pd.read_csv("eye_health_2022_clean.csv").shape) #print saved file dimensions
print(pd.read_csv("eye_health_2022_clean.csv").head) #print dataframe head (first 5 lines )