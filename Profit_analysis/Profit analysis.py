# This is the code we used to get the profit analysis: 
#Author: Emily Deuchar

#Firstly get average bids: 
import pandas as pd

# I used the data fram daily_merit_trim_asset which was created by Sean
hourly_df = pd.read_csv('daily_merit_trim_asset.csv')

# Convert the date column to a datetime object
hourly_df['begin_dateTime_mpt'] = pd.to_datetime(hourly_df['begin_dateTime_mpt'])

# Create a new column 'date' to store only the date part of 'begin_dateTime_mpt'
hourly_df['date'] = hourly_df['begin_dateTime_mpt'].dt.date

# Group by 'date' and 'asset_ID' and calculate the mean (average) block price for each combination
average_daily_prices_df = hourly_df.groupby(['date', 'asset_ID'])['block_price'].mean().reset_index()

# Save the result to a CSV file
average_daily_prices_df.to_csv('average_daily_block_prices_per_asset.csv', index=False)

#Second, calculate marginal cost and then make it into a CSV
#We used the marginal cost calculation outlined in the lit review: And got fuel cost from the Alberta government, Carbon pricing from the literature, and Variable O&M and heat rate from AESO.

#Read it into a dataframe. The data frame marginal cost was an excel file that contained all the variables listed above
Marginal_cost_df = pd.read_csv(r'Marginal_cost.csv')

#Create a variable for Fuel cost
Fuel_cost=Marginal_cost_df['Fuel_cost']
# Create a list of date ranges for each month
date_ranges = pd.date_range(start='2023-01-01', end='2023-12-31', freq='MS')

# Create a DataFrame to store the calculated values
calculation_df = pd.DataFrame(columns=['Date', 'Calculated Value'])

# Create an empty DataFrame to store the calculated values
calculation_df = pd.DataFrame(columns=['Date', 'Fuel Cost', 'Calculated Value'])

# Loop over each fuel cost
for i, fuel_cost in enumerate(Fuel_cost):
    # Extract the date range for the current month
    date_range = date_ranges[i]
    
    # Extract year and month from the date range
    year = date_range.year
    month = date_range.month
    
    # Perform the calculation for the current fuel cost
    calculated_value = (fuel_cost * 6.79) + 3.65 + 25
    
    # Append the calculated value for each day of the month
    month_dates = pd.date_range(start=date_range, end=date_range + pd.offsets.MonthEnd(), freq='D')
    
    # Create a DataFrame for the current fuel cost
    df = pd.DataFrame({
        'Date': month_dates,
        'Fuel Cost': [fuel_cost] * len(month_dates),
        'Calculated Value': [calculated_value] * len(month_dates)
    })
    
    # Concatenate the DataFrame to the main DataFrame
    calculation_df = pd.concat([calculation_df, df], axis=0)

# Reset the index
calculation_df.reset_index(drop=True, inplace=True)

# Save the result to a CSV file
calculation_df.to_csv('Marginal_cost_calculation.csv', index=False)

#Third: Create a graph that shows the average bids compared to the marginal cost
#Author: Emily Deuchar
import matplotlib.pyplot as plt

# Define a function to plot generator bids and marginal cost for a given date range
def plot_data(start_year, start_month, end_month, title):
    # Read the CSV file for generator bids into a DataFrame
    average_block_prices_df = pd.read_csv('average_daily_block_prices_per_asset.csv')

    # Convert the date column to a datetime object
    average_block_prices_df['date'] = pd.to_datetime(average_block_prices_df['date'])

    # Filter data for the specified date range
    data = average_block_prices_df[
        (average_block_prices_df['date'].dt.year == start_year) &
        (average_block_prices_df['date'].dt.month >= start_month) &
        (average_block_prices_df['date'].dt.month <= end_month)
    ]

    # Plot generator bids for each day of the specified date range
    for asset_id, group in data.groupby('asset_ID'):
        plt.scatter(group['date'], group['block_price'], label=f'Generator {asset_id}', marker='x')

    # Read the CSV file for marginal cost into a DataFrame
    marginal_cost_df = pd.read_csv('Marginal_cost_calculation.csv')
    marginal_cost_df['Date'] = pd.to_datetime(marginal_cost_df['Date'])

    # Filter marginal cost data for the specified date range
    marginal_cost_dates = marginal_cost_df[
        (marginal_cost_df['Date'].dt.year == start_year) &
        (marginal_cost_df['Date'].dt.month >= start_month) &
        (marginal_cost_df['Date'].dt.month <= end_month)
    ]

    # Plot marginal cost
    plt.scatter(marginal_cost_dates['Date'], marginal_cost_dates['Calculated Value'], color='black', marker='x', label='Marginal Cost')

    # Set plot labels and title with larger font sizes
    plt.xlabel('Year-Day-Month', fontsize=12)
    plt.ylabel('Bid Amount', fontsize=12)
    plt.title(title, fontsize=14)

    # Change the font size of legend
    plt.legend(fontsize=10)

    # Show the plot
    plt.show()

# Plot data for each quarter of the year 2023
plot_data(2023, 1, 3, 'Generator Bids from January to March 2023')
plot_data(2023, 4, 6, 'Generator Bids from April to June 2023')
plot_data(2023, 7, 9, 'Generator Bids from July to September 2023')
plot_data(2023, 10, 12, 'Generator Bids from October to December 2023')

# Fouth: Create a potential profit analysis where we take the average bid of each day and subtract it from the marginal cost: 

#Define a function to plot the difference between bid price and marginal cost for each asset
def plot_difference_by_asset(start_year, start_month, end_month, title):
    # Read the CSV file for highest daily generator bids into a DataFrame
    highest_block_prices_df = pd.read_csv('average_daily_block_prices_per_asset.csv')

    # Convert the date column to a datetime object
    highest_block_prices_df['date'] = pd.to_datetime(highest_block_prices_df['date'])

    # Filter data for the specified date range
    data = highest_block_prices_df[
        (highest_block_prices_df['date'].dt.year == start_year) &
        (highest_block_prices_df['date'].dt.month >= start_month) &
        (highest_block_prices_df['date'].dt.month <= end_month)
    ]

    # Read the CSV file for marginal cost into a DataFrame
    marginal_cost_df = pd.read_csv('Marginal_cost_calculation.csv')
    marginal_cost_df['Date'] = pd.to_datetime(marginal_cost_df['Date'])

    # Filter marginal cost data for the specified date range
    marginal_cost_dates = marginal_cost_df[
        (marginal_cost_df['Date'].dt.year == start_year) &
        (marginal_cost_df['Date'].dt.month >= start_month) &
        (marginal_cost_df['Date'].dt.month <= end_month)
    ]

    # Merge dataframes on 'Date' to get the corresponding marginal cost for each bid date
    merged_data = pd.merge(data, marginal_cost_dates, how='left', left_on='date', right_on='Date')

    # Calculate the difference between 'block_price' and 'Calculated Value' for each asset
    for asset_id, group in merged_data.groupby('asset_ID'):
        group['Difference'] = group['block_price'] - group['Calculated Value']
        plt.scatter(group['date'], group['Difference'], label=f'Asset {asset_id}', marker='x')

    # Set plot labels and title with larger font sizes
    plt.xlabel('Year-Day-Month', fontsize=12)
    plt.ylabel('Difference', fontsize=12)
    plt.title(title, fontsize=14)

    # Change the font size of legend
    plt.legend(fontsize=10) 
    # Show the plot
    plt.show()

# Plot the difference for each quarter of the year 2023
plot_difference_by_asset(2023, 1, 3, 'Difference between Bid Amount and Marginal Cost from January to March 2023')
plot_difference_by_asset(2023, 4, 6, 'Difference between Bid Amount and Marginal Cost from April to June 2023')
plot_difference_by_asset(2023, 7, 9, 'Difference between Bid Amount and Marginal Cost from July to September 2023')
plot_difference_by_asset(2023, 10, 12, 'Difference between Bid Amount and Marginal Cost from October to December 2023')