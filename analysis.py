#%%
import os
import sqlite3
import numpy as np
import pandas as pd
import plotly.express as px

save_path = os.path.join(os.getcwd(), 'data')
db_file = os.path.join(save_path,'database.db')
conn = sqlite3.connect(db_file)
db_df = pd.read_sql(""" SELECT * FROM sales_data """,
                    con= conn,
                    parse_dates='Time')

#%%
df = db_df.copy()
df['Date'] = df['Time'].dt.strftime("%Y/%m/%d")
df['Year'] = df['Time'].dt.year
df['Month'] = df['Time'].dt.month
df['Day'] = df['Time'].dt.day
df[['Amount', 'Unit']] = df['Amount'].str.extract('(-?\d+)(\D+)')

# change dtypes
df['Amount'] = pd.to_numeric(df['Amount'], )


sales_overview = pd.pivot_table(
    data= df,
    index= 'Date',
    columns= 'Unit',
    values= 'Amount',
    aggfunc="sum",
    fill_value=0
).reset_index()
sales_overview['Earnings'] = sales_overview['元'] + sales_overview['點']

#%%
# Calculate the moving average 
window_size = 7
sales_overview['Weekly Average'] = sales_overview['Earnings'].rolling(window=7).mean()
sales_overview['Biweekly Average'] = sales_overview['Earnings'].rolling(window=14).mean()
sales_overview['Monthly Average'] = sales_overview['Earnings'].rolling(window=30).mean()

# Create a line plot with Plotly Express
fig = px.line(sales_overview, x='Date', y=['Earnings', 'Weekly Average', 'Biweekly Average', 'Monthly Average'],
              labels={'value': 'Earnings', 'variable': 'Metric'},
              title="Earnings Trend with Moving Average")
fig.show()
#%%
sales_overview_monthly = pd.pivot_table(
    data= df,
    index= ['Year', 'Month'],
    columns= 'Unit',
    values= 'Amount',
    aggfunc="sum",
    fill_value=0
).reset_index()
sales_overview_monthly['Monthly Earnings'] = sales_overview_monthly['元'] + sales_overview_monthly['點']
sales_overview_monthly['Seasonal Average'] = sales_overview_monthly['Monthly Earnings'].rolling(window=3).mean()
fig = px.line(sales_overview_monthly, x='Month', y=['Monthly Earnings', 'Seasonal Average'],
              labels={'value': 'Earnings', 'variable': 'Metric'},
              title="Earnings Trend with Moving Average")
fig.show()


#%%
conn.close()