# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 17:01:23 2023

@author: fafernan2101
"""

import pandas as pd
import numpy as np 
import datetime as dt
import openpyxl
import time
import os
import shutil

#### Parameters ####

release = 223

####################


# Record the starting time
start_time = time.time()

#lv_config folder path
lv_config_path = 'C:/SCARBOROUGH/TV_Fusion/lv_config/R{}/'.format(release)

#create release folder if missing
if not os.path.exists(lv_config_path):
    os.makedirs(lv_config_path)

#references path
references = 'C:/SCARBOROUGH/TV_Fusion/lv_config/References/'

#import mapping file
dma_mapping = pd.read_csv(references + 'dma_mapping.csv')

# Define market types
mkt_types = ['LPM', 'CR', 'SM']

# Copy the excel files from References folder to release folder
for mkt_type in mkt_types:
    # Construct the file name using string formatting
    file_name = f"LV_config Prod - {mkt_type}.xlsx"
    # Copy the file from the source to the destination directory
    shutil.copy(references + file_name, lv_config_path + file_name)


#read the Files for fusion.xslx from the release folder
excel_file = pd.ExcelFile(lv_config_path + 'R{} Files for Fusion2.xlsx'.format(release))
stations = excel_file.parse("Scarborough network mappings")
buckets = excel_file.parse("Scarborough network buckets map")


# Rename column 'market' to 'DMA_CODE'
buckets = buckets.rename(columns={'market': 'DMA_CODE',
                                  'Scarb_Network_Key' : 'SCARB_KEY'})


# Remove spaces from 'SCARB_KEY' column in 'stations' and 'buckets' DataFrames
stations['SCARB_KEY'] = stations['SCARB_KEY'].str.replace(' ', '')
buckets['SCARB_KEY'] = buckets['SCARB_KEY'].str.replace(' ', '')


# Define the cable function
def cable(df):
    # Filter the rows that have the value "Cable"
    
    #global cable_rows
    cable_rows = df[df["DMA_CODE"] == "Cable"]

    # Get the unique values of the column "DMA_CODE" without counting "Cable"
    unique_values = df["DMA_CODE"].unique()
    unique_values = unique_values[unique_values != "Cable"]

    # Repeat the cable rows as many times as there are unique DMA values
    cable_rows = cable_rows.loc[cable_rows.index.repeat(len(unique_values))]

    # Replace the values of "Cable" by the unique values
    cable_rows["DMA_CODE"] = np.tile(unique_values, len(cable_rows) // len(unique_values))

    # Concatenate the original rows with the duplicated rows
    df = pd.concat([df, cable_rows], ignore_index=True)

    # Filter the rows in column 'DMA_CODE' that are present in column 'name' of 'dma_mapping'
    df = df[df["DMA_CODE"].isin(dma_mapping["name"])]

    # Sort the dataframe 'df' by 'DMA_CODE' 
    df = df.sort_values(by="DMA_CODE")

    # Add the DMA code number and market type columns
    merged = pd.merge(df, dma_mapping, how='left', left_on='DMA_CODE', right_on='name')

    # Rename columns
    merged = merged.rename(columns={'dma': 'PROCESSING_DMA_CODE',
                                    'LV_NAME': 'LINKING_VARIABLE_NAME'})
    #create columns
    merged['IS_IN_CC'] = 'X'
    merged['TRIM_SIDE']= 'E'
    merged['PCA_FLAG'] = 'Y'
    merged['SE_FLAG'] = 'Y'
    merged['OE_FLAG'] = 'Y'
    # Return the merged dataframe
    return merged


# Apply the functions to dfs 'stations' and 'buckets'
stations = cable(stations)
buckets = cable(buckets)

#create category column
stations['CONFIG_CATEGORY'] = 'TVNETW'
buckets['CONFIG_CATEGORY'] = 'BUCKETS'

#drop the duplicates in the combiation SCARB_KEY and dma name
buckets2 = buckets.drop_duplicates(["SCARB_KEY", "name"])

#Merge with stations to get the station name
buckets2 = buckets2.merge(stations[['SCARB_KEY', 'name', 'LINKING_VARIABLE_NAME']] , on=['SCARB_KEY', 'name'])

#add "_B" to the station names
buckets2['LINKING_VARIABLE_NAME'] = buckets2['LINKING_VARIABLE_NAME'].apply(lambda x: x + '_B')

#keep columns of interest
stations = stations[['type', 'PROCESSING_DMA_CODE', 'LINKING_VARIABLE_NAME', 'CONFIG_CATEGORY', 'IS_IN_CC', 'TRIM_SIDE', 'PCA_FLAG', 'SE_FLAG', 'OE_FLAG']]
buckets2 = buckets2[['type', 'PROCESSING_DMA_CODE', 'LINKING_VARIABLE_NAME', 'CONFIG_CATEGORY', 'IS_IN_CC', 'TRIM_SIDE', 'PCA_FLAG', 'SE_FLAG', 'OE_FLAG']]


# Create a new column to sort correctly later
buckets2['LINKING_VARIABLE_NAME_CLEAN'] = buckets2['LINKING_VARIABLE_NAME'].str.replace('_B$', '', regex=True)
stations['LINKING_VARIABLE_NAME_CLEAN'] = stations['LINKING_VARIABLE_NAME']

# Concatenate the DataFrames
concat_df = pd.concat([buckets2, stations], ignore_index=True)

#drop duplicates
concat_df =concat_df.drop_duplicates(subset=['PROCESSING_DMA_CODE', 'LINKING_VARIABLE_NAME'])

#  Sort 
concat_df = concat_df.sort_values(['PROCESSING_DMA_CODE','LINKING_VARIABLE_NAME_CLEAN', 'LINKING_VARIABLE_NAME']).reset_index()

# Drop the temporary column created for sorting
concat_df.drop('LINKING_VARIABLE_NAME_CLEAN', axis=1, inplace=True)

# Export concat_df
#concat_df.to_csv(lv_config_path + 'concat_df.csv' , index = False)

# create a boolean mask to select rows that ends with '_B' in column 'LINKING_VARIABLE_NAME'
mask = concat_df['LINKING_VARIABLE_NAME'].str.endswith('_B')

# create a list with columns to modify
cols = ['TRIM_SIDE', 'PCA_FLAG', 'SE_FLAG', 'OE_FLAG']

# assign an X in selected columns to rows that are before the ones containing '_B'
concat_df.loc[mask.shift(-1).fillna(False), cols] = 'X'


## Add 2 rows for each market: WEEKDAY_B and WEEKEND_B
# Get the unique values of the column PROCESSING_DMA_CODE
dma_codes = concat_df["PROCESSING_DMA_CODE"].unique()

# Create an empty list to store the new rows
new_rows = []

# Loop through each DMA code
for dma_code in dma_codes:
    # Get the type of the DMA code from the dataframe dma_mapping
    dma_type = dma_mapping[dma_mapping["dma"] == dma_code]["type"].iloc[0]
    # Create two new rows with the specified values for each column
    new_row_1 = {"LINKING_VARIABLE_NAME": "WEEKDAY_B", "PROCESSING_DMA_CODE": dma_code, "type": dma_type, "CONFIG_CATEGORY": "BUCKETS", "IS_IN_CC": "X", "TRIM_SIDE": "D", "PCA_FLAG": "Y", "SE_FLAG": "Y", "OE_FLAG": "Y"}
    new_row_2 = {"LINKING_VARIABLE_NAME": "WEEKEND_B", "PROCESSING_DMA_CODE": dma_code, "type": dma_type, "CONFIG_CATEGORY": "BUCKETS", "IS_IN_CC": "X", "TRIM_SIDE": "D", "PCA_FLAG": "Y", "SE_FLAG": "Y", "OE_FLAG": "Y"}
    # Append the new rows to the list
    new_rows.append(new_row_1)
    new_rows.append(new_row_2)


# Convert the list of new rows to a dataframe
week_rows = pd.DataFrame(new_rows)

# Concatenate the new dataframe with the original dataframe
concat_df = pd.concat([concat_df, week_rows], ignore_index=True)


# Create a function that duplicates the stations and buckets from the no-hispanic to the hispanic (e.g. copy Fresno stations to Hispanic Fresno)
def hisp_stations(df):
    # Create a boolean mask to select the values of 4 digits
    hisp_codes = df['PROCESSING_DMA_CODE'].astype(str).str.len() == 4
    # Extract the values of 4 digits and remove the final 0
    no_hisp_codes = df.loc[hisp_codes, 'PROCESSING_DMA_CODE'].astype(str).str[:-1]
    # Create another boolean mask to select the rows that match the hispanic codes without the final 0
    mask = df['PROCESSING_DMA_CODE'].astype(str).isin(no_hisp_codes)
    # Create another boolean mask to select the rows that have either 'TVNETW' or 'BUCKETS' in the column 'CONFIG_CATEGORY'
    mask2 = df['CONFIG_CATEGORY'].isin(['TVNETW', 'BUCKETS'])
    # Combine the masks using the logical operator &
    mask3 = mask & mask2
    # Extract the rows that match and add a 0 at the end in the column 'PROCESSING_DMA_CODE'
    dup_rows = df.loc[mask3].copy()
    dup_rows['PROCESSING_DMA_CODE'] = dup_rows['PROCESSING_DMA_CODE'].astype(str) + '0'
    # Convert the column 'PROCESSING_DMA_CODE' back to numeric
    dup_rows['PROCESSING_DMA_CODE'] = dup_rows['PROCESSING_DMA_CODE'].astype(int)
    # Return the DataFrame with the duplicated rows added
    return pd.concat([df, dup_rows], ignore_index=True)


# Create an empty dictionary to store dataframes
dfs = {}

# Loop through each market type
for i in mkt_types:
    # Read the corresponding CSV file and store it in the dictionary
    dfs[f'df_{i}'] = pd.read_excel(lv_config_path + f"LV_config Prod - {i}.xlsx", sheet_name="LV CONFIG")
    
    # Concatenate the dataframe with concat_df filtered by market type
    dfs[f'df_{i}'] = pd.concat([dfs[f'df_{i}'], concat_df[concat_df['type'] == i]], ignore_index=True)
    
    # Drop the 'type' column
    dfs[f'df_{i}'].drop('type', axis=1, inplace=True)
    
    # Add new columns with constant values
    dfs[f'df_{i}']['JOB_ID'] = 111
    dfs[f'df_{i}']['CREATED_BY'] = 'dataprep'
    dfs[f'df_{i}']['CREATED_DATE'] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dfs[f'df_{i}']['PROCESSING_DATA_DATE'] = dt.datetime.today().strftime("%Y-%m-%d")
    
    # Reorder the columns
    dfs[f'df_{i}'] = dfs[f'df_{i}'][['JOB_ID', 'PROCESSING_DATA_DATE', 'PROCESSING_DMA_CODE', 'LINKING_VARIABLE_NAME', 'CONFIG_CATEGORY', 'IS_IN_CC', 'TRIM_SIDE', 'PCA_FLAG', 'SE_FLAG', 'OE_FLAG', 'CREATED_BY', 'CREATED_DATE']]
    
    #apply the function hisp_stations() to each df
    dfs[f'df_{i}'] = hisp_stations(dfs[f'df_{i}'])
    
    # Sort the dfs (with specific order in CONFIG_CATEGORY)
    dfs[f'df_{i}']['CONFIG_CATEGORY'] = pd.Categorical(dfs[f'df_{i}']['CONFIG_CATEGORY'], categories=['CHAR', 'TVGENRE', 'TVNETW', 'BUCKETS'], ordered=True)
 
    dfs[f'df_{i}'] = dfs[f'df_{i}'].sort_values(['PROCESSING_DMA_CODE','CONFIG_CATEGORY','LINKING_VARIABLE_NAME'])

    
#Export to excel file - LV_CONFIG sheet:
      
# Create a loop to iterate over the market types and the names of the dataframes
for mkt_type, df_name in zip(mkt_types, dfs.keys()):
    # Create a writer object for the Excel file in append mode, using the openpyxl module as engine
    with pd.ExcelWriter(lv_config_path + f'LV_config Prod - {mkt_type}.xlsx' , engine='openpyxl', mode='a', if_sheet_exists= 'replace') as writer:
        # Load the existing Excel workbook that contains the Excel file
        writer.workbook = openpyxl.load_workbook(lv_config_path + f'LV_config Prod - {mkt_type}.xlsx')
        # Write the dataframe to the sheet LV_CONFIG, replacing the previous data if they exist
        dfs[df_name].to_excel(writer, sheet_name='LV CONFIG', index=False)
        

# Rename the files
# Define the list of old and new file names
old_names = ["LV_config Prod - CR.xlsx", "LV_config Prod - LPM.xlsx", "LV_config Prod - SM.xlsx"]
new_names = [f"LV_config Prod R{release} - Code Reader.xlsx", f"LV_config Prod R{release} - LPM.xlsx", f"LV_config Prod R{release} - Set Meter.xlsx"]

# Loop through the old and new file names
for old_name, new_name in zip(old_names, new_names):
    # Check if the new file name already exists in the path
    if os.path.exists(lv_config_path + new_name):
        # If it does, delete it using the os.remove function
        os.remove(lv_config_path + new_name)
    # Rename the file using the os.rename function
    os.rename(lv_config_path + old_name, lv_config_path + new_name)

#####   QC   #####

# Define the function qc_check that takes a dataframe as an argument
def qc_check(df):
    # Create a pivot table to count the values of each category
    table = pd.pivot_table(data=df, index=['PROCESSING_DMA_CODE'], columns=['CONFIG_CATEGORY'], values='CREATED_BY', aggfunc='count') 
    # Filter the dataframe by CONFIG_CATEGORY and TRIM_SIDE 
    df_tvnetw_x = df[(df['CONFIG_CATEGORY'] == 'TVNETW') & (df['TRIM_SIDE'] == 'X')] 
    df_buckets_e = df[(df['CONFIG_CATEGORY'] == 'BUCKETS') & (df['TRIM_SIDE'] == 'E')] 
   
    # Extract the LINKING_VARIABLE_NAME column from each filtered dataframe 
    col_tvnetw_x = df_tvnetw_x['LINKING_VARIABLE_NAME']  
    col_buckets_e = df_buckets_e['LINKING_VARIABLE_NAME']
    
    # Remove duplicates, sort columns alphabetically and reset index
    col_tvnetw_x = col_tvnetw_x.drop_duplicates().sort_values().reset_index(drop=True)
    col_buckets_e = col_buckets_e.drop_duplicates().sort_values(key=lambda x: x.str.slice(stop=-2)).reset_index(drop=True)
    
    # Concatenate the two columns into a new dataframe 
    new_df = pd.concat([col_tvnetw_x, col_buckets_e] , axis = 1) 
    # Rename the columns 
    new_df.columns = ['TVNETW_X', 'BUCKETS_E']
    # Return the pivot table and the new dataframe
    return table, new_df


# Define the excel file name
qc_file = f'QC - TV Fusion R{release}.xlsx'

# Create a writer object for the Excel file
with pd.ExcelWriter(lv_config_path + qc_file, engine='openpyxl') as writer:
    # Loop over the dataframes and the market types
    for df_name, mkt_type in zip(dfs.keys(), mkt_types):
        # Get the dataframe from the dictionary
        df = dfs[df_name]
        # Apply the qc_check function to the dataframe
        table, new_df = qc_check(df)
        # Write the table and the new_df to different sheets in the excel file
        table.to_excel(writer, sheet_name=mkt_type + ' pivot')
        new_df.to_excel(writer, sheet_name=mkt_type + ' stations', index=False)


# Record the ending time
end_time = time.time()

# Calculate the duration
duration = end_time - start_time

print(f"Execution time: {duration:.2f} seconds")