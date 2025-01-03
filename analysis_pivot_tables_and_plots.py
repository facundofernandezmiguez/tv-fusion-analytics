# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 13:02:30 2023

@author: fafernan2101
"""

########### user input ###########

#Actual release for the pivot tables:
release = '123'

# Releases you want to plot
releases_to_plot = ['222','123'] 

##################################

import os  
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
#pip install xlsxwriter


inloc = 'C:/Fusion/POV/Analysis/R'+release+'/'

market_names = 'C:/Fusion/POV/References/market_codes.csv'
categ_names_path = 'C:/Fusion/POV/References/mapping_category_codes_to_names.csv'

metrics_file = 'POV_Fusion_Metrics.csv'
penetrations_file = 'POV_Fusion_Penetrations.csv'

# Read files
market_codes = pd.read_csv(market_names)
metrics = pd.read_csv(os.path.join(inloc, metrics_file))
penetration = pd.read_csv(os.path.join(inloc, penetrations_file))


# Load the categ_names file
categ_names = pd.read_csv(categ_names_path)


######################################
#                                    #
#        Part A: Pivot Tables        #
#                                    #
######################################


######################################
#           metrics file             #
######################################

#add market column to metrics
metrics = metrics.merge(market_codes[['market', 'market name']], on='market', how='left')

#reorder columns
new_order = ['market name'] + ['market'] + [col for col in metrics.columns if col not in ['market name', 'market']]
metrics = metrics.reindex(columns=new_order)


## Create pivot table for OutputEval
# Filter the metrics DataFrame and rename it
outputeval = metrics[metrics['sec_code'] == 'OutputEval']

#make 'var_val' column numeric
col_index = outputeval.columns.get_loc('var_val')
outputeval.isetitem(col_index, pd.to_numeric(outputeval['var_val'], errors='coerce'))

# Create the pivot table
outputeval2 = outputeval.pivot_table(index=['market name', 'market'], columns='var_name', values='var_val', aggfunc='mean').round(2)


#The same for CreateRecipFused:
createrecip = metrics[metrics['sec_code'] == 'CreateRecipFused']

#make 'var_val' column numeric
createrecip.loc[:,'var_val'] = pd.to_numeric(createrecip['var_val'], errors='coerce')

# Create the pivot table
createrecip2 = createrecip.pivot_table(index=['market name', 'market'], columns='var_name', values='var_val', aggfunc='mean').round(2)

#Export the 3 dfs into one xlsx file:
writer = pd.ExcelWriter(inloc+'POV_Fusion_Metrics_Pivots_R{}.xlsx'.format(release), engine='xlsxwriter')

# Write each dataframe to a different worksheet.

###Raw Metrics Sheet:
metrics.to_excel(writer, sheet_name='RawMetrics', index=False)

###CreateRecipFused Sheet:
# Get the worksheet object for the 'CreateRecipFused' sheet.
worksheet = createrecip2.to_excel(writer, sheet_name='CreateRecipFused', index=True)
worksheet = writer.sheets['CreateRecipFused']

# Define the color scales for each column.
closeness_colors = {'type': '2_color_scale', 'min_value': '=MIN(C:C)', 'max_value': '=MAX(C:C)', 'min_color': '#F5A623', 'max_color': '#8BC34A'}
efficiency_colors = {'type': '2_color_scale', 'min_value': '=MIN(G:G)', 'max_value': '=MAX(G:G)', 'min_color': '#F5A623', 'max_color': '#8BC34A'}
overall_colors = {'type': '2_color_scale', 'min_value': '=MIN(H:H)', 'max_value': '=MAX(H:H)', 'min_color': '#F5A623', 'max_color': '#8BC34A'}
percent_colors = {'type': '2_color_scale', 'min_value': '=MIN(I:I)', 'max_value': '=MAX(I:I)', 'min_color': '#F5A623', 'max_color': '#8BC34A'}

# Apply the conditional formatting rules to each column separately.
worksheet.conditional_format('C2:C1000', closeness_colors)
worksheet.conditional_format('G2:G1000', efficiency_colors)
worksheet.conditional_format('H2:H1000', overall_colors)
worksheet.conditional_format('I2:I1000', percent_colors)

### OutputEval sheet:
worksheet = outputeval2.to_excel(writer, sheet_name='OutputEval', index=True)
worksheet = writer.sheets['OutputEval']

# Define the color scales for each column.
abs_diff_colors = {'type': '2_color_scale', 'min_value': '=MIN(C:C)', 'max_value': '=MAX(C:C)', 'min_color': '#F5A623', 'max_color': '#8BC34A'}
rtm_hz_colors = {'type': '2_color_scale', 'min_value': '=MIN(G:G)', 'max_value': '=MAX(G:G)', 'min_color': '#F5A623', 'max_color': '#8BC34A'}
rtm_vt_colors = {'type': '2_color_scale', 'min_value': '=MIN(H:H)', 'max_value': '=MAX(H:H)', 'min_color': '#F5A623', 'max_color': '#8BC34A'}
skew_corr_hz_colors = {'type': '2_color_scale', 'min_value': '=MIN(I:I)', 'max_value': '=MAX(I:I)', 'min_color': '#F5A623', 'max_color': '#8BC34A'}
skew_corr_vt_colors = {'type': '2_color_scale', 'min_value': '=MIN(J:J)', 'max_value': '=MAX(J:J)', 'min_color': '#F5A623', 'max_color': '#8BC34A'}

# Apply the conditional formatting rules to each column separately.
worksheet.conditional_format('C2:C1000', abs_diff_colors)
worksheet.conditional_format('G2:G1000', rtm_hz_colors)
worksheet.conditional_format('H2:H1000', rtm_vt_colors)
worksheet.conditional_format('I2:I1000', skew_corr_hz_colors)
worksheet.conditional_format('J2:J1000', skew_corr_vt_colors)

# Save the file.
writer.close()


######################################
#         penetration file           #
######################################

#add market column to penetration file
penetration = penetration.merge(market_codes[['market', 'market name']], on='market', how='left')
#reorder columns
new_order = ['market name'] + ['market'] + [col for col in penetration.columns if col not in ['market name', 'market']]
penetration = penetration.reindex(columns=new_order)
#first pivot
penetration_pivot = pd.pivot_table(penetration,
                                    index='market name',
                                    columns=['fused_var','fused_var_code'],
                                    values='prof_pop_recip',
                                    aggfunc='mean').round(0)

# Calculate statistics and add them as new rows
penetration_pivot.loc['Average'] = penetration_pivot.mean().round(1)
penetration_pivot.loc['Min'] = penetration_pivot.min()
penetration_pivot.loc['Max'] = penetration_pivot.max()
penetration_pivot.loc['St. Dev'] = penetration_pivot.std().round(1)

# Reorder the rows
row_order = ['Average', 'Min', 'Max', 'St. Dev'] + list(penetration_pivot.index[:-4])
penetration_pivot = penetration_pivot.reindex(row_order)

#Export the 2 dfs into one xlsx file:
writer2 = pd.ExcelWriter(inloc+'POV_Fusion_Penetrations_Pivot_R{}.xlsx'.format(release), engine='xlsxwriter')

# Write each dataframe to a different worksheet
penetration.to_excel(writer2, sheet_name='Raw_Penetration', index=False)
penetration_pivot.to_excel(writer2, sheet_name='Pivot', index=True)
# Save the file
writer2.close()

############################
# Penetrations - evolution #
############################

#    parameters:   #
mean_threshold = 2
std_threshold = 0.5
####################


#This code works when there is no more than 2 relases in the list releases_to_plot

inloc2 = 'C:/Fusion/POV/Analysis/R' # input directory

#Concatenate releases in releases_to_plot list
dfs = []
for release in releases_to_plot: # iterate each release value
    filepath = os.path.join(inloc2 +release , penetrations_file)
    df = pd.read_csv(filepath) # read the file into a dataframe
    df['release'] = release #create column release 
    dfs.append(df) # append the dataframe to the list

df_final = pd.concat(dfs) 

#calculate main statistics
result = pd.pivot_table(df_final, index=['fused_var', 'fused_var_code'], columns='release', values='prof_pop_recip', aggfunc=['mean', 'std'])

#sort the relase 
result = result.reindex(releases_to_plot, axis=1, level=1)


# Create the 'mean_change' and 'std_change' columns
result = result.assign(mean_change=result['mean'].diff(axis=1).iloc[:, 1])
result = result.assign(std_change=result['std'].diff(axis=1).iloc[:, 1])

# Define a function that returns 'increase', 'decrease' or 'no change' depending on the value of mean_change
def change1(x):
  if x > mean_threshold:
    return 'increase'
  elif x < -mean_threshold:
    return 'decrease'
  else:
    return 'no change'

# Create a new column with the result of applying the function to the mean_change column
result = result.assign(change1=result['mean_change'].apply(change1))

# Define a function that returns 'more variation', 'less variation' or 'no change' depending on the value of std_change
def change2(x):
  if x > std_threshold:
    return 'more variation'
  elif x < -std_threshold:
    return 'less variation'
  else:
    return 'no change'

# Create a new column with the result of applying the function to the std_change column
result = result.assign(change2=result['std_change'].apply(change2))

# Create a new column change with the values of change1
result['change'] = result['change1']

# Replace the values of change with the values of change2 where change1 is 'no change'
result['change'] = result['change'].where(result['change1'] != 'no change', result['change2'])

# Concatenate the values of change1 and change2 with ' and ' where both are not 'no change'
result['change'] = result['change'].where((result['change1'] == 'no change') | (result['change2'] == 'no change'), result['change1'] + ' and ' + result['change2'])



#reset index
result = result.reset_index()

#rename columns
result.columns = ['fused_var', 'fused_var_code'] + [col[0] + '_' + str(col[1]) for col in result.columns[2:]]

# add the Segment column names to the df
result = result.merge(categ_names, left_on=['fused_var', 'fused_var_code'], right_on=['id', 'SegmentNumber'])

#remove columns
result = result.drop(columns=['fused_var', 'fused_var_code','id', 'SegmentNumber'])

# Reorder columns
result = result.reindex(columns=['Segmentation', 'new_name'] + result.columns.drop(['Segmentation', 'new_name']).tolist())

#Rename columns
new_names = {'change1_': 'mean_change', 'change2_': 'std_change', 'change_': 'overall_change'}
result = result.rename(new_names, axis=1)

# count values in column overall_change
counts = result['overall_change'].value_counts()

# count values of 'no change' and total values
no_change_count = counts['no change']
total_count = counts.sum()

# calculate % of 'no change' in column
unchanged = round(no_change_count / total_count * 100 )

# create the phrase to print in df
phrase = "This file compares the releases {} and {}. The percentage of segments that remains unchanged is {}%."
phrase = phrase.format(releases_to_plot[0], releases_to_plot[1], unchanged)

#add in df
result.loc[0, 'Summary'] = phrase

# Export 
result.to_csv('C:/Fusion/POV/Analysis/graphs/penetration_summary.csv' , index = False)


######################################
#                                    #
#           Part B: Plots            #
#                                    #
######################################



###################################
#       plots penetration         #
###################################

path = 'C:/Fusion/POV/Analysis/'


# Create an empty dataframe to hold all the data
all_releases = pd.DataFrame()

appended_data = []

# Loop through all the directories in the path
for foldername in os.listdir(path):
    # Ignore the 'graphs' folder if already exists
    if foldername == 'graphs':
        continue
    # Check if the item in the directory is a folder
    if os.path.isdir(os.path.join(path, foldername)):
        # Get the last 3 letters of the folder name
        release = foldername[-3:]
        if release in releases_to_plot:
            # Define the path to the csv file
            filepath = os.path.join(path, foldername, 'POV_Fusion_Penetrations.csv')
            # Read the csv file into a dataframe
            df = pd.read_csv(filepath)
            # Add a new column with the release number
            df['release'] = release
            # Add df to the list
            appended_data.append(df)

# Concat all df of the list in one 
all_releases = pd.concat(appended_data, ignore_index=True)

# Reset the index of the dataframe
all_releases = all_releases.reset_index(drop=True)

# Create the 'graphs' folder if it does not exist
if not os.path.exists(path + 'graphs'):
    os.makedirs(path + 'graphs')
    

#Sort the df by release in time order    
# define the order for the x-axis
x_order = ['221', '122', '222', '123', '223', '124', '224']

# create a categorical variable using the desired order
cat_order = pd.CategoricalDtype(categories=x_order, ordered=True)

# convert the 'release' column to categorical
all_releases['release'] = all_releases['release'].astype(cat_order)

# sort the DataFrame by the 'release' column
all_releases = all_releases.sort_values('release')
    
    
# Reset the index of the dataframe
all_releases = all_releases.reset_index(drop=True)

# convert the 'release' column back to string
all_releases['release'] = all_releases['release'].astype(str)

#keep only the releases to plot
#all_releases = all_releases[all_releases['release'].isin(releases_to_plot)]

# Create the 'graphs' folder if it does not exist
if not os.path.exists(path + 'graphs'):
    os.makedirs(path + 'graphs')

all_releases.to_csv('all_releases_custom.csv', index = False)
'''
#Change the label of the release in case you want to do a custom comparison (e.g. 123-all mkts vs. 123-some markets)
#all_releases['release'] = all_releases['release'].replace('123', '123*')
all_releases['release'] = all_releases['release'].replace('222', '123_orig')
 '''   
# Check for missing values in the 'market' column
missing_values = all_releases['market'].isnull().sum() 
 # Print the number of missing values
print("Number of missing values in 'market' column:", missing_values)
##########
### Box Plot
##########

'''
Note that in the plot you have Option A (plot all the markets) and Option B (plot only the markets contained in market_list).
Uncomment the one that you want to use.
market_list comes from codes fetch_fusion_info.py and fetch_fusion_penetrations.py
'''

# Group the data by fused_var

grouped = all_releases.groupby('fused_var')



# Check if all releases to plot are present in the data
if not all(r in all_releases['release'].unique() for r in releases_to_plot):
    print("You are trying to plot a release not present in the data. Run the first part of the code (until 'Plots') for all the markets.")
    sys.exit()

# Import PdfPages

from matplotlib.backends.backend_pdf import PdfPages


with PdfPages('C:/Fusion/POV/Analysis/graphs/penetrations_by_category.pdf') as pdf:
    for fused_var, fused_var_group in grouped:
        # Group the data by fused_var_code
        fused_var_grouped = fused_var_group.groupby('fused_var_code')

        # Determine the number of fused_var_code groups
        ngroups = len(fused_var_grouped)

        # Create a figure with subplots for each fused_var_code
        fig, axes = plt.subplots(nrows=1, ncols=ngroups, figsize=(5*ngroups, 5), sharey=True)

        fig.suptitle(categ_names[categ_names['id'] == fused_var]['Segmentation'].iloc[0], fontsize=20)

        # Loop over the fused_var_code groups and plot the data for each
        for i, (fused_var_code, group) in enumerate(fused_var_grouped):
            # Group the data by release
            release_grouped = group.groupby('release')

            # Get the data and labels for each release
            release_data = []
            release_labels = []
            for release, release_df in release_grouped:
                if release in releases_to_plot:
                    release_data.append(release_df['prof_pop_recip'])
                    release_labels.append(release)
            # Create a boxplot for the data
            
            # Option A: Plot all the markets
            sns.boxplot(x='release', y='prof_pop_recip', data=group, ax=axes[i], palette='colorblind')
            '''
            # Option B: Plot only the markets in market_list
            sns.boxplot(x='release', y='prof_pop_recip',data=group[group['market'].isin(market_list)], ax=axes[i], palette='colorblind')
            '''
            # Set the title based on categ_names file
            match = (categ_names['id'] == fused_var) & (categ_names['SegmentNumber'] == fused_var_code)
            new_name = categ_names.loc[match, 'new_name'].values[0]
            axes[i].set_title(new_name)

            # Set the axis labels
            axes[i].set_xlabel('release')
            axes[i].set_ylabel('prof_pop_recip')
            
        # Adjust the layout
        fig.tight_layout()

        # Save the figure to the pdf file
        pdf.savefig(fig, orientation='landscape')

        # Close the figure
        plt.close(fig)

                               
######################################
#           plots metrics            #
######################################

path = 'C:/Fusion/POV/Analysis/'


# Create an empty dataframe to hold all the data
all_releases = pd.DataFrame()

# Create an empty list
appended_data = []
# Loop through all the directories in the path
for foldername in os.listdir(path):
    # Ignore the 'graphs' folder if already exists
    if foldername == 'graphs':
        continue
    # Check if the item in the directory is a folder
    if os.path.isdir(os.path.join(path, foldername)):
        # Get the last 3 letters of the folder name
        release = foldername[-3:]
        # Define the path to the csv file
        filepath = os.path.join(path, foldername, 'POV_Fusion_Metrics.csv')
        # Read the csv file into a dataframe
        df = pd.read_csv(filepath)
        # Add a new column with the release number
        df['release'] = release
        # Append the dataframe to the list
        appended_data.append(df)
# Concatenate all the dataframes in the list into one
all_releases = pd.concat(appended_data, ignore_index=True)
# Reset the index of the dataframe
all_releases = all_releases.reset_index(drop=True)



# Create the 'graphs' folder if it does not exist
if not os.path.exists(path + 'graphs'):
    os.makedirs(path + 'graphs')
    
#Sort the df by release in time order    
# define the order for the x-axis
x_order = ['221', '122', '222', '123', '223', '124', '224']

# create a categorical variable using the desired order
cat_order = pd.CategoricalDtype(categories=x_order, ordered=True)

# convert the 'release' column to categorical
all_releases['release'] = all_releases['release'].astype(cat_order)

#keep only the releases to plot
all_releases = all_releases[all_releases['release'].isin(releases_to_plot)]

# sort the DataFrame by the 'release' column
all_releases = all_releases.sort_values('release')


###########    
## Plot 1:'CLOSENESS_OF_MATCH', 'EFFICIENCY' and 'OVERALL_MATCH'
##########

var_names = ['CLOSENESS_OF_MATCH', 'EFFICIENCY', 'OVERALL_MATCH']

del all_releases['sec_code']

''' ORIGINAL PLOT
# create a boxplot for each variable
fig, axs = plt.subplots(ncols=len(var_names), figsize=(15,5))
for i, var_name in enumerate(var_names):
    sns.boxplot(x='release', y='var_val', data=all_releases[all_releases['var_name'] == var_name].astype({'var_val': float}), order=all_releases['release'].unique(), ax=axs[i])
    axs[i].set_title(var_name)

# show the plots
plt.show()
'''

#filter the outliers to plot the market names 

outliers_df = pd.DataFrame(columns=['var_name', 'release', 'var_val', 'market'])

# loop through the three variables
for var_name in ['CLOSENESS_OF_MATCH', 'EFFICIENCY', 'OVERALL_MATCH']:
    # filter the data for the current variable
    data = all_releases[all_releases['var_name'] == var_name].astype({'var_val': float})
    # calculate the whisker values
    
    q1 = data['var_val'].quantile(0.25)
    q3 = data['var_val'].quantile(0.75)
    iqr = q3 - q1
    lower_whisker = q1 - 1.5 * iqr
    upper_whisker = q3 + 1.5 * iqr
    '''
    median = data['var_val'].median()
    std = data['var_val'].std()
    lower_whisker = median - 1.3 * std
    upper_whisker = median + 1.3 * std
    '''
    # filter the data for the outliers
    outliers = data[(data['var_val'] < lower_whisker) | (data['var_val'] > upper_whisker)]
    # add the outliers to the DataFrame
    outliers_df = pd.concat([outliers_df, outliers[['var_name', 'release', 'var_val', 'market']]], ignore_index=True)

    
# reset the index of the DataFrame
outliers_df = outliers_df.reset_index(drop=True)

# loop through the outliers and remove any that are within the whisker range
for i, row in outliers_df.iterrows():
    var_name = row['var_name']
    release = row['release']
    var_val = row['var_val']
    market = row['market']
    data = all_releases[(all_releases['var_name'] == var_name) & (all_releases['release'] == release)].astype({'var_val': float})
    q1 = data['var_val'].quantile(0.25)
    q3 = data['var_val'].quantile(0.75)
    iqr = q3 - q1
    lower_whisker = q1 - 1.5 * iqr
    upper_whisker = q3 + 1.5 * iqr
    if lower_whisker <= var_val <= upper_whisker:
        outliers_df.drop(i, inplace=True)
        
# reset the index of the DataFrame again
outliers_df = outliers_df.reset_index(drop=True)

## Option A: plot all the markets in each release
# create a boxplot for each variable
fig, axs = plt.subplots(ncols=len(var_names), figsize=(15,5))
for i, var_name in enumerate(var_names):
    sns.boxplot(x='release', y='var_val', data=all_releases[all_releases['var_name'] == var_name].astype({'var_val': float}), order=all_releases['release'].unique(), ax=axs[i])
    axs[i].set_title(var_name)
    
    # add labels for outliers
    outliers = outliers_df[outliers_df['var_name'] == var_name]
    for index, row in outliers.iterrows():
        release = row['release']
        var_val = row['var_val']
        market = row['market'] 
        x_pos = list(all_releases['release'].unique()).index(release)  # get x position of boxplot
        y_pos = var_val  # get y position of outlier value
        axs[i].text(x_pos, y_pos, market, ha='left', va='center', color='black')
    
# export the plot to a PDF file
plt.savefig('C:/Fusion/POV/Analysis/graphs/efficiency_and_match_metrics.pdf', bbox_inches='tight')


# show the plots
plt.show()


##Option B: plot the markets in market_list (only the markets from the last release)
#the market_list comes from running the codes fetch_fusion_info.py and fetch_fusion_penetration.py
fig, axs = plt.subplots(ncols=len(var_names), figsize=(15,5))
for i, var_name in enumerate(var_names):
    # filter all_releases for markets in market_list
    filtered_releases = all_releases[(all_releases['var_name'] == var_name) & (all_releases['market'].isin(market_list))]
    sns.boxplot(x='release', y='var_val', data=filtered_releases.astype({'var_val': float}), order=filtered_releases['release'].unique(), ax=axs[i])
    axs[i].set_title(var_name)
    
    # add labels for outliers
    outliers = outliers_df[outliers_df['var_name'] == var_name]
    for index, row in outliers.iterrows():
        release = row['release']
        var_val = row['var_val']
        market = row['market'] 
        # only add label for markets in market_list
        if market in market_list:
            x_pos = list(filtered_releases['release'].unique()).index(release)  # get x position of boxplot
            y_pos = var_val  # get y position of outlier value
            axs[i].text(x_pos, y_pos, market, ha='left', va='center', color='black')

# export the plot to a PDF file
plt.savefig('C:/Fusion/POV/Analysis/graphs/efficiency_and_match_metrics.pdf', bbox_inches='tight')

# show the plots
plt.show()

#############
## Plot 2 : 'abs_diff_hz' and 'abs_diff_vt'
#############

# create a list of variable names
var_names = ['abs_diff_hz', 'abs_diff_vt']


''' ORIGINAL PLOT
# create a boxplot for each variable
fig, axs = plt.subplots(ncols=len(var_names), figsize=(15,5))
for i, var_name in enumerate(var_names):
    sns.boxplot(x='release', y='var_val', data=all_releases[all_releases['var_name'] == var_name].astype({'var_val': float}), order=all_releases['release'].unique(), ax=axs[i])
    axs[i].set_title(var_name)

# show the plots
plt.show()
'''

# define the order for the x-axis
x_order = ['221', '122', '222', '123', '223', '124', '224']

# create an empty DataFrame to store the outliers
outliers_df = pd.DataFrame(columns=['var_name', 'release', 'var_val', 'market'])

# create a figure with two subplots
fig, axes = plt.subplots(ncols=2, figsize=(15,6))

# loop through the variables
for i, var_name in enumerate(var_names):
    # filter the data for the current variable and remove NaN values
    data = all_releases[all_releases['var_name'] == var_name].dropna(subset=['var_val']).astype({'var_val': float})
    
    # calculate the whisker values
    q1 = data['var_val'].quantile(0.25)
    q3 = data['var_val'].quantile(0.75)
    iqr = q3 - q1
    lower_whisker = q1 - 1.5 * iqr
    upper_whisker = q3 + 1.5 * iqr
    
    # filter the data for the outliers
    outliers = data[(data['var_val'] < lower_whisker) | (data['var_val'] > upper_whisker)]
    
    # add the outliers to the DataFrame
    outliers_df = pd.concat([outliers_df, outliers[['var_name', 'release', 'var_val', 'market']]], ignore_index=True)
    
    # create a boxplot for the variable
    sns.boxplot(x='release', y='var_val', data=data, order=all_releases['release'].unique(), ax=axes[i])
    axes[i].set_title(var_name)
    
    # add labels for outliers
    for index, row in outliers.iterrows():
        release = row['release']
        var_val = row['var_val']
        market = row['market']
        x_pos = list(all_releases['release'].unique()).index(release)  # get x position of boxplot
        y_pos = var_val  # get y position of outlier value
        axes[i].text(x_pos, y_pos, market, ha='left', va='center', color='black')
    
        
# export the plot to a PDF file
plt.savefig('C:/Fusion/POV/Analysis/graphs/abbs_diff.pdf', bbox_inches='tight')

# show the plots
plt.show()

#########
## Plot 3 : regression to mean
#########

var_names = ['rtm_hz' ,	'rtm_vt']

''' ORIGINAL PLOT
# create a boxplot for each variable
fig, axs = plt.subplots(ncols=len(var_names), figsize=(15,5))
for i, var_name in enumerate(var_names):
    sns.boxplot(x='release', y='var_val', data=all_releases[all_releases['var_name'] == var_name].astype({'var_val': float}), order=all_releases['release'].unique(), ax=axs[i])
    axs[i].set_title(var_name)

# show the plots
plt.show()
'''


#filter the outliers to plot the market names 

outliers_df = pd.DataFrame(columns=['var_name', 'release', 'var_val', 'market'])

# loop through the three variables
for var_name in var_names:
    # filter the data for the current variable
    data = all_releases[all_releases['var_name'] == var_name].astype({'var_val': float})
    # calculate the whisker values
    ''' this didn't work originally: 
    q1 = data['var_val'].quantile(0.25)
    q3 = data['var_val'].quantile(0.75)
    iqr = q3 - q1
    lower_whisker = q1 - 1.5 * iqr
    upper_whisker = q3 + 1.5 * iqr
    '''
    median = data['var_val'].median()
    std = data['var_val'].std()
    lower_whisker = median - 1.3 * std
    upper_whisker = median + 1.3 * std
    # filter the data for the outliers
    outliers = data[(data['var_val'] < lower_whisker) | (data['var_val'] > upper_whisker)]
    # add the outliers to the DataFrame
    outliers_df = pd.concat([outliers_df, outliers[['var_name', 'release', 'var_val', 'market']]], ignore_index=True)

# reset the index of the DataFrame
outliers_df = outliers_df.reset_index(drop=True)

# loop through the outliers and remove any that are within the whisker range
for i, row in outliers_df.iterrows():
    var_name = row['var_name']
    release = row['release']
    var_val = row['var_val']
    market = row['market']
    data = all_releases[(all_releases['var_name'] == var_name) & (all_releases['release'] == release)].astype({'var_val': float})
    q1 = data['var_val'].quantile(0.25)
    q3 = data['var_val'].quantile(0.75)
    iqr = q3 - q1
    lower_whisker = q1 - 1.5 * iqr
    upper_whisker = q3 + 1.5 * iqr
    if lower_whisker <= var_val <= upper_whisker:
        outliers_df.drop(i, inplace=True)
        
# reset the index of the DataFrame again
outliers_df = outliers_df.reset_index(drop=True)


# create a boxplot for each variable
fig, axs = plt.subplots(ncols=len(var_names), figsize=(15,5))
for i, var_name in enumerate(var_names):
    sns.boxplot(x='release', y='var_val', data=all_releases[all_releases['var_name'] == var_name].astype({'var_val': float}), order=all_releases['release'].unique(), ax=axs[i])
    axs[i].set_title(var_name)
    
    # add labels for outliers
    outliers = outliers_df[outliers_df['var_name'] == var_name]
    for index, row in outliers.iterrows():
        release = row['release']
        var_val = row['var_val']
        market = row['market']
        x_pos = list(all_releases['release'].unique()).index(release)  # get x position of boxplot
        y_pos = var_val  # get y position of outlier value
        axs[i].text(x_pos, y_pos, market, ha='left', va='center', color='black')

# export the plot to a PDF file
plt.savefig('C:/Fusion/POV/Analysis/graphs/reg_to_mean.pdf', bbox_inches='tight')


# show the plots
plt.show()

##############
## Plot 4 : sker_corr
##############

var_names = ['skew_corr_hz' ,	'skew_corr_vt']

''' ORIGINAL PLOT
# create a boxplot for each variable
fig, axs = plt.subplots(ncols=len(var_names), figsize=(15,5))
for i, var_name in enumerate(var_names):
    sns.boxplot(x='release', y='var_val', data=all_releases[all_releases['var_name'] == var_name].astype({'var_val': float}), order=all_releases['release'].unique(), ax=axs[i])
    axs[i].set_title(var_name)

# show the plots
plt.show()


# export the plot to a PDF file
plt.savefig('C:/Fusion/POV/Analysis/graphs/skew_corr.pdf', bbox_inches='tight')
'''


#filter the outliers to plot the market names 

outliers_df = pd.DataFrame(columns=['var_name', 'release', 'var_val', 'market'])

# loop through the three variables
for var_name in var_names:
    # filter the data for the current variable
    data = all_releases[all_releases['var_name'] == var_name].astype({'var_val': float})
    # calculate the whisker values
    ''' this didn't work originally: 
    q1 = data['var_val'].quantile(0.25)
    q3 = data['var_val'].quantile(0.75)
    iqr = q3 - q1
    lower_whisker = q1 - 1.5 * iqr
    upper_whisker = q3 + 1.5 * iqr
    '''
    median = data['var_val'].median()
    std = data['var_val'].std()
    lower_whisker = median - 1.3 * std
    upper_whisker = median + 1.3 * std
    # filter the data for the outliers
    outliers = data[(data['var_val'] < lower_whisker) | (data['var_val'] > upper_whisker)]
    # add the outliers to the DataFrame
    outliers_df = pd.concat([outliers_df, outliers[['var_name', 'release', 'var_val', 'market']]], ignore_index=True)
    

# reset the index of the DataFrame
outliers_df = outliers_df.reset_index(drop=True)

# loop through the outliers and remove any that are within the whisker range
for i, row in outliers_df.iterrows():
    var_name = row['var_name']
    release = row['release']
    var_val = row['var_val']
    market = row['market']
    data = all_releases[(all_releases['var_name'] == var_name) & (all_releases['release'] == release)].astype({'var_val': float})
    q1 = data['var_val'].quantile(0.25)
    q3 = data['var_val'].quantile(0.75)
    iqr = q3 - q1
    lower_whisker = q1 - 1.5 * iqr
    upper_whisker = q3 + 1.5 * iqr
    if lower_whisker <= var_val <= upper_whisker:
        outliers_df.drop(i, inplace=True)
        
# reset the index of the DataFrame again
outliers_df = outliers_df.reset_index(drop=True)


# create a boxplot for each variable
fig, axs = plt.subplots(ncols=len(var_names), figsize=(15,5))
for i, var_name in enumerate(var_names):
    sns.boxplot(x='release', y='var_val', data=all_releases[all_releases['var_name'] == var_name].astype({'var_val': float}), order=all_releases['release'].unique(), ax=axs[i])
    axs[i].set_title(var_name)
    
    # add labels for outliers
    outliers = outliers_df[outliers_df['var_name'] == var_name]
    for index, row in outliers.iterrows():
        release = row['release']
        var_val = row['var_val']
        market = row['market']
        x_pos = list(all_releases['release'].unique()).index(release)  # get x position of boxplot
        y_pos = var_val  # get y position of outlier value
        axs[i].text(x_pos, y_pos, market, ha='left', va='center', color='black')

# export the plot to a PDF file
plt.savefig('C:/Fusion/POV/Analysis/graphs/skew_corr.pdf', bbox_inches='tight')


# show the plots
plt.show()