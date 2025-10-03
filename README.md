# Summary

The purpose of this program is to collect, process and perform analysis on the data required for this project.

The entry point of this program is the main.py, which orchestrates the data collection and formating, as well as acting as a wrapper to integrate R for further processing and analysis.

# Instructions

## .env setup

1. Create a file with the name .env within the project folder.
2. Copy the contents from the file .env.example into the .env that file you created.
3. Enter the information (ensure you have the same email and password for both [HFD](https://www.humanfertility.org/) and [HMD](https://www.mortality.org/)).

## Requirements

To ensure the python code runs, you have to install the required external packages.

Enter the following into the command terminal:

```
pip install -r requirements.txt
```

## Execution

```
NOTE: download the data from online databases and run the program afterwards

python3 main.py --download
```

```
NOTE: run the program on previously downloaded data

python3 main.py
```

```
NOTE: for more help

python3 main.py --help
```

# Notes

## Data collection

### Human Mortality Database (HMD)

- The data is collected from the [HMD](https://www.mortality.org/) website. For females only, the data is taken from [here](https://www.mortality.org/File/GetDocument/hmd.v6/zip/by_statistic/lt_female.zip). For males only, the data is taken from [here](https://www.mortality.org/File/GetDocument/hmd.v6/zip/by_statistic/lt_male.zip). For both males and females combined, the data is taken from [here](https://www.mortality.org/File/GetDocument/hmd.v6/zip/by_statistic/lt_both.zip).

### Human Fertility Database (HFD)

- The data is collected from the [HFD](https://www.humanfertility.org/Data/ZippedDataFiles) For the data collected for the HFD, the Age Specific Fertility Rate (ASFR), also refered to as the mx, is collect from [here](https://www.humanfertility.org/File/Download/Files/zip/asfr.zip).

### World Bank Country and Lending Groups (WBLG)

- The data is collected from the [WBLG](https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups). The data is taken from the [historical classification by income in XLSX format](https://ddh-openapi.worldbank.org/resources/DR0095334/download).

## TODO

1. Generate plots for Ne and T.
2. Generate metadata for data.
3. Look further into the Ne calculation (incorrect as of right now, some numbers are in the negative).