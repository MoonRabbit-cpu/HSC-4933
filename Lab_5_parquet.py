################################################
# Bryan Hernandez Rodriguez -----------        #
# Lab_5_parquet.py:       Pandas                   #
# Lab 5 Data conversion                        #
################################################



import pandas as pd #imports

df = pd.read_csv("Maternal_Health_Risk_Data_Set.csv") #reading the csv

df = df.loc[:, ~df.columns.duplicated()] #Drop columns that repeat an earlier column name

df = df.loc[:, ~df.T.duplicated()] #Drop columns whose contents are identical to an earlier column



df.to_parquet("Maternal_Health_Risk_Data_Set.parquet",engine="pyarrow",index=False)
# saves new parquet

