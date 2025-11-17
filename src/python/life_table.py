

import os
import pandas as pd
from src.python import hmd, hfd, log
from src.python.helper import SETTINGS, OUT_PATH


def merge_hmd_hfd_df(hmd_df: pd.DataFrame, hfd_df: pd.DataFrame):
    # filter only common country, year pairs
    common_df = pd.merge(
        hmd_df[["ISO3", "ISO3_suffix","Year"]].drop_duplicates(),
        hfd_df[["ISO3","ISO3_suffix","Year"]].drop_duplicates(),
        on=["ISO3","ISO3_suffix", "Year"],
        how="inner"
        )
    
    #checking for duplicates despite the check 
    dup_check = common_df.groupby(["ISO3", "ISO3_suffix", "Year"]).size()
    if (dup_check > 1).any():
        print("WARNING: Duplicates found in common_df:")
        print(dup_check[dup_check > 1])
    

    # find all rows that exist in common
    hmd_df = hmd_df.merge(common_df, on=["ISO3", "ISO3_suffix", "Year"], how="inner")
    hfd_df = hfd_df.merge(common_df, on=["ISO3", "ISO3_suffix", "Year"], how="inner")

    # restrict HMD ages between min_age and max_age, adjust acordingly (max = 110)
    hmd_df = hmd_df[hmd_df["Age"].between(SETTINGS["min_age"], SETTINGS["max_age"])]

    # building a full age grid min_age...max_age for each common (country, year)
    ages = pd.DataFrame({"Age": list(range(SETTINGS["min_age"], SETTINGS["max_age"] + 1))})
    grid = common_df.assign(_k=1).merge(ages.assign(_k=1), on="_k").drop(columns="_k")
    
    # merge lx (HMD) and asfr (HFD)
    log.log(f"hmd_df DEU TE1956 Age 15 count: {len(hmd_df[(hmd_df['ISO3']=='DEU') & (hmd_df['ISO3_suffix']=='TE') & (hmd_df['Year']==1956) & (hmd_df['Age']==15)])}")
    df = grid.merge(hmd_df, on=["ISO3", "ISO3_suffix", "Year", "Age"], how="left")
    df = df.merge(hfd_df, on=["ISO3", "ISO3_suffix","Year", "Age"], how="left")


    # reorder
    front = ["ISO3", "ISO3_suffix", "Year", "Age"]
    df = df[[*front, *[c for c in df.columns if c not in front]]]

    log.log("merged the HMD and HFD tables and separated ISO3 from the suffix")
    return df


def generate_life_table(download: bool) -> str:
    # generate formated data from HMD and HFD
    hmd_df = hmd.generate_hmd_df(download)
    hfd_df = hfd.generate_hfd_df(download)


    # merge data from HMD and HFD and export
    hmd_hfd_df = merge_hmd_hfd_df(hmd_df, hfd_df)
    path = os.path.join(OUT_PATH, "life_table.csv")
    hmd_hfd_df.to_csv(path, index=False)

    
    
   

    log.log("succesfully generated the merged life table: " + path)
    return path