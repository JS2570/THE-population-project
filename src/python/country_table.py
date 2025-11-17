import os
import pandas as pd
from src.python import income_status, log
from src.python.helper import SETTINGS, OUT_PATH
from src.python.Keyfitz_entropy import calculate_H_for_dataset


def load_life_table(life_table_path): return pd.read_csv(life_table_path, engine="python")


def format_country_table(income_status_df: pd.DataFrame, life_table_df: pd.DataFrame):
    '''
    format the income status table for WBLG so that it only filters for countries also in the life table
    '''
    inc = income_status_df.copy()
    life = life_table_df.copy()

    # make sure ISO3 all upper case
    inc["ISO3"] = inc["ISO3"].astype(str).str.upper().str.strip()
    life["ISO3"] = life["ISO3"].astype(str).str.upper().str.strip()

    # index of unique (iso3, iso3_suffix, year)
    idx: pd.DataFrame = (
        life[["ISO3", "ISO3_suffix", "Year"]]
        .drop_duplicates()
    )

    # merge income (iso3, year) only
    out = idx.merge(
        inc[["ISO3", "Year", "IS"]],
        on=["ISO3", "Year"],
        how="left"
    ).sort_values(["ISO3", "ISO3_suffix", "Year"])

    out["ISO3_suffix"] = out["ISO3_suffix"].fillna("")
    
    log.log("formated the country table")
    return out[["ISO3", "ISO3_suffix", "Year", "IS"]]


def generate_country_table(life_table_path, download: bool):
    income_status_df, path = income_status.generate_income_status_df(download)

    life_table_df = load_life_table(life_table_path)
    country_table_df = format_country_table(income_status_df, life_table_df)

    log.log("calcualting all keyfitz entropy using matricies (H_N) fr all country-years")
    H_df = calculate_H_for_dataset(life_table_df)



    #merge H_N values into country table
    country_table_df = country_table_df.merge(
        H_df[['ISO3', 'ISO3_suffix', 'Year', 'H_N']],
        on=["ISO3", "ISO3_suffix", "Year"],
        how="left"
    )

    
    



    log.log("merged H_N values into country table")

    path = os.path.join(OUT_PATH, "country_table.csv")
    country_table_df.to_csv(path, index=False)
    return path
