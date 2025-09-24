import pandas as pd
import os
from config import SETTINGS, OUTPUT_PATH, LOG_BUFFER, get_datetimestamp, log, error


def assign_data():
    # file input
    input_folder = SETTINGS["input_folder"]
    os.makedirs(input_folder, exist_ok=True)

    while True: # loop until we have both files assigned
        files = os.listdir(input_folder)
        if len(files) == 2:
            for f in files: 
                path = os.path.join(input_folder, f)
                with open(path, "r") as infile:
                    head = infile.read(200) # read first 200 characters
                    if "Life tables" in head:
                        hmd_data_path = path
                    elif "fertility rates" in head:
                        hfd_data_path = path
            if hmd_data_path and hfd_data_path:
                log("successfully located required files")
                return hmd_data_path, hfd_data_path
            else:
                error(f"files are present, but could not be identified, check contents of \"{input_folder}\" and press enter")
                input("...")
        else: 
            error(f"ensure the HFD and HMD data files are in the \"{input_folder}\" folder...")
            input("...")


# data per 100,000, so normalise lx as a probability
def format_hmd(in_dir) -> pd.DataFrame:
    data = pd.read_csv(
        in_dir, 
        sep=r"\s+", # split if more than 1 space between columns 
        engine="python",
        skiprows=2,
        dtype={"Age":"string"})
    
    # filter and format columns 
    data = data[["PopName", "Year", "Age", "lx"]] # insert all columns being filtered into output
    data.columns = (data.columns.str.strip().str.lower()) # normalise to lowercase
    data.rename(columns={"popname": "country"}, inplace=True)
    data["age"] = pd.to_numeric(data["age"].str.extract(r"(\d+)")[0], errors="coerce") # ensure numeric only for age (note that otherwise would get 100+)

    if SETTINGS["standardise_lx"]:
        # normalise lx 0-1 instead of per 100,000
        data["lx"] = pd.to_numeric(data["lx"], errors="coerce")
        lx0 = (data.loc[data["age"] == 0, ["country", "year", "lx"]].rename(columns={"lx": "lx0"}))
        data = data.merge(lx0, on=["country", "year"], how="left")
        data["lx"] = data["lx"] / data["lx0"]
        data.drop(columns="lx0", inplace=True)

    out_path = OUTPUT_PATH + "/hmd_data.csv"
    data.to_csv(out_path, index=False)
    log(f"successfully formated the data from HMD into: {os.path.basename(out_path)}")
    return data


# data per women, so no need to normalise data
def format_hfd(in_dir) -> pd.DataFrame:
    data = pd.read_csv(
        in_dir, 
        sep=r"\s+", # split if more than 1 space between columns 
        engine="python",
        skiprows=2,
        dtype={"Age":"string"})
    
    # filter and format columns 
    data = data[["Code", "Year", "Age", "ASFR"]] # insert all columns being filtered into output
    data.columns = (data.columns.str.strip().str.lower()) # normalise to lowercase
    data.rename(columns={"code": "country", "asfr": "mx"}, inplace=True)
    data["age"] = pd.to_numeric(data["age"].str.extract(r"(\d+)")[0], errors="coerce") # ensure numeric only for age (note that otherwise would get 100+)

    out_path = OUTPUT_PATH + "/hfd_data.csv"
    data.to_csv(out_path, index=False)
    log(f"successfully formated the data from HFD into: {os.path.basename(out_path)}")
    return data


def process_data(hmd_data: pd.DataFrame, hfd_data: pd.DataFrame):
    # keep only common (country, year) pairs
    common = pd.merge(
        hmd_data[["country", "year"]].drop_duplicates(),
        hfd_data[["country", "year"]].drop_duplicates(),
        on=["country", "year"],
        how="inner"
    )

    # find all rows that exist in common
    hmd = hmd_data.merge(common, on=["country", "year"], how="inner")
    hfd = hfd_data.merge(common, on=["country", "year"], how="inner")
    
    # restrict HMD ages between min_age and max_age, adjust acordingly (max = 110)
    hmd = hmd[hmd["age"].between(SETTINGS["min_age"], SETTINGS["max_age"])]

    # building a full age grid min_age...max_age for each common (country, year)
    ages = pd.DataFrame({"age": list(range(SETTINGS["min_age"], SETTINGS["max_age"] + 1))})
    grid = common.assign(_k=1).merge(ages.assign(_k=1), on="_k").drop(columns="_k")

    # merge lx (HMD) and mx (HFD)
    data = grid.merge(hmd, on=["country", "year", "age"], how="left")
    data = data.merge(hfd, on=["country", "year", "age"], how="left")

    log("successfully merged the HMD and HFD")

    # set mx = 0 outside age = 12-55
    data.loc[(data["age"] < 12) | (data["age"] > 55), "mx"] = 0.0

    # formatting into types
    data["lx"] = pd.to_numeric(data["lx"], errors="coerce")
    data["mx"] = pd.to_numeric(data["mx"], errors="coerce")

    # calculations
    data["lxmx"] = data["lx"] * data["mx"]
    data["lx_next"] = data.groupby(["country", "year"])["lx"].shift(-1)
    data["dx"] = data["lx"] - data["lx_next"]
    data["qx"] = 1 - (data["lx_next"] / data["lx"])
    data["sx"] = 1 - data["qx"]
    data["cum_lxmx"] = (
        data.groupby(["country", "year"])["lxmx"]
        .transform(lambda x: x[::-1].cumsum()[::-1])
    )
    data["vx"] = data["cum_lxmx"] / data["lx"]

    log("successfully completed calculations for additional variables")

    # delete unneeded columns used for caluculations
    data.drop(columns=["lx_next", "cum_lxmx"], inplace=True)

    # export to .csv
    out_path = OUTPUT_PATH + "/data.csv"
    data.to_csv(out_path, index=False)
    log(f"data successfully mereged, formated and exported to {os.path.basename(out_path)}")

    # TODO: possibly find a way to collapse all country variations into one
    

def write_metadata():
    path = OUTPUT_PATH + "/INFO.txt"
    with open(path, "w") as f:
        f.write(get_datetimestamp() + "\n")
        f.write("Data outputted into: " + OUTPUT_PATH + "\n\n")
        f.write(f"The minimum age filtered for is: {SETTINGS['min_age']}\n")
        f.write(f"The maximum age filtered for is: {SETTINGS['max_age']}\n")

        # TODO metadata incl. number of countries etc

        f.write("\nLOGS: \n")
        f.write("\n".join(LOG_BUFFER) + "\n")
        

def main():
    # find paths for files required
    hmd_data_path, hfd_data_path = assign_data()

    hmd_data = format_hmd(hmd_data_path)
    hfd_data = format_hfd(hfd_data_path)

    process_data(hmd_data, hfd_data)
    write_metadata()

    
if __name__ == "__main__":
    main()