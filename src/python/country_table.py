import os
import pandas as pd
from src.python import income_status
from src.python.helper import SETTINGS, OUT_PATH


def load_life_table(path):
    df = None

    # TODO

    return df


def format_country_table(income_status_df: pd.DataFrame, life_table_df: pd.DataFrame):
    df = None

    # TODO 

    return df


def generate_country_table(life_table_path):
    income_status_df, path = income_status.generate_income_status_df()

    country_table_df = income_status_df # TODO temp

    path = os.path.join(OUT_PATH, "country_table.csv")
    country_table_df.to_csv(path, index=False)
    return path
