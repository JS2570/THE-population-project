from src.python import income_status


def generate_country_table():
    income_status_df, path = income_status.generate_income_status_df()
    return path
