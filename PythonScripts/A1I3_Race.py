"""
SRD
Aim 1 Indicator 3: Race
Measures calculated: (1) Percentage, (2) Majority, (3) Entropy, (4) Index of Concentration at the Extremes (ICE) for Race,
(5) Global-to-Local (State-to-County) Concentration
Years: 2020, 2010, 2000, 1990

Last Updated: March 01, 2024
"""

import pandas as pd
from librace import *

data_path = "C:\\SRD\\Data\\A1I3_Race\\RaceData\\"
res_path = "C:\\SRD\\Data\\A1I3_Race\\Result\\"

years = [2020, 2010, 2000, 1990]

for year in years:
    # Load the data
    df = pd.read_csv(data_path + f'RaceNHGIS{year}.csv')

    race = ['White', 'Black', 'Other']

    # Calculate total White, Black, and Other population
    for r in race:
        df[r] = df[f'NHis{r}'] + df[f'His{r}']

    # Ensure numeric data types for calculations
    df[['TotPop', 'White', 'Black', 'Other']] = df[['TotPop', 'White', 'Black', 'Other']].apply(pd.to_numeric, errors='coerce')

    # Calculate the percentage and proportions of each racial-ethnic group
    for r in race:
        df[f'P{r}'] = (df[r]) / df['TotPop'] * 100
        df[f'{r}_Prop'] = (df[r]) / df['TotPop']

    ## MAJORITY MINORITY RULE TYPOLOGY
    # Apply the classification function from librace library
    df['Majority'] = df.apply(classify_county, axis=1)

    ## ENTROPY
    # Apply the function from "librace" library to compute entropy for each county
    df['Ent'] = df.apply(compute_entropy, axis=1)

    # Find the maximum possible entropy (i.e., when all groups are equal)
    max_ent = -np.log(1/3)

    # Standardize entropy values to a 0-100 scale
    df['Entropy'] = (df['Ent'] / max_ent) * 100

    ## ICE FOR RACE
    df['ICERace'] = (df['White'] - df['Black']) / df['TotPop']

    ## GLOBAL-TO-LOCAL
    state_data = pd.read_csv(data_path + f'StateRaceNHGIS{year}.csv')

    # Merge the DataFrames on the 'StateFIPS' column
    merged_df = pd.merge(df, state_data, on='StateFIPS', how='left')

    st_race = ['White', 'Black']

    # Calculate total White and Black population for State
    for race in st_race:
        merged_df[f'St{race}'] = merged_df[f'StNHis{race}'] + merged_df[f'StHis{race}']

    # Ensure numeric data types for calculations
    merged_df[['StTotPop', 'StWhite', 'StBlack']] = merged_df[['StTotPop', 'StWhite', 'StBlack']].apply(pd.to_numeric, errors='coerce')

    # Calculate the percentage of each racial group by State
    for race in st_race:
        merged_df[f'PSt{race}'] = (merged_df[f'St{race}'] / merged_df['StTotPop']) * 100

    # Calculate Global-to-Local
    for race in st_race:
        merged_df[f'GL{race}'] = merged_df[f'P{race}'] - merged_df[f'PSt{race}']

    # Reorder the columns.
    desired_order = ['FIPS', 'TotPop',
                     'NHisWhite', 'NHisBlack', 'NHisOther',
                     'HisWhite', 'HisBlack', 'HisOther',
                     'White', 'Black', 'Other',
                     'PWhite', 'PBlack', 'POther',
                     'Majority', 'Entropy', 'ICERace',
                     'StTotPop', 'StNHisWhite', 'StNHisBlack',
                     'StHisWhite', 'StHisBlack',
                     'StWhite', 'StBlack',
                     'PStWhite', 'PStBlack',
                     'GLWhite', 'GLBlack'
                     ]

    result_df = merged_df.reindex(columns=desired_order)

    # Save the merged DataFrame to a new CSV file
    result_df.to_csv(res_path + f'A1I3Race{year}.csv', index=False)

    ## JOIN CSV TO COUNTY BOUNDARY FEATURE CLASS
    import arcpy
    arcpy.env.overwriteOutput = True

    db_path = "C:\\SRD\\SRD2024\\SRD2024_Final.gdb\\"
    boundary = db_path + f"Boundary\\Counties{year}"
    boundary_copy = db_path + f'A1I3_Race\\Counties{year}Copy'
    lo = f"C:\\SRD\\SRD2024\\SRD2024_Final.gdb\\A1I3_Race\\Race{year}"

    # Make a copy of boundary feature class. This is temporary file and will be deleted at the end.
    arcpy.management.CopyFeatures(boundary, boundary_copy)

    # Join csv to boundary feature class based on the matching unique identifier fields FIPS
    lyr = arcpy.management.JoinField(boundary_copy, 'FIPS', res_path + f'A1I3Race{year}.csv', 'FIPS')

    # Delete duplicate FIPS
    arcpy.DeleteField_management(lyr, ['FIPS_1'])

    # Create a feature class
    arcpy.management.CopyFeatures(lyr, lo)

    # Delete temporary feature class
    arcpy.management.Delete(boundary_copy)

    print(f'{year} complete')
