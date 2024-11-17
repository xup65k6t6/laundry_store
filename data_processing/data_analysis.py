import pandas as pd
import plotly.express as px


from data_cleaning import read_df_from_db

def earnings_trend(df, window_size = 7):
    sales_overview = pd.pivot_table(
        data= df,
        index= 'Date',
        columns= 'Unit',
        values= 'Amount',
        aggfunc="sum",
        fill_value=0
    ).reset_index()
    sales_overview['Earnings'] = sales_overview['元'] + sales_overview['點']
    # Calculate the moving average 
    sales_overview['Weekly Average'] = sales_overview['Earnings'].rolling(window=7).mean()
    sales_overview['Biweekly Average'] = sales_overview['Earnings'].rolling(window=14).mean()
    sales_overview['Monthly Average'] = sales_overview['Earnings'].rolling(window=30).mean()

    # Create a line plot with Plotly Express
    fig = px.line(sales_overview, 
                  x='Date', 
                  y=['Earnings', 'Weekly Average', 'Biweekly Average', 'Monthly Average'],
                labels={'value': 'Earnings', 'variable': 'Metric'},
                title="Earnings Trend with Moving Average",
                # color={"Earnings"}
                )
    fig.show()

def moving_average_plot(df):
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

def yoy(df:pd.DataFrame):
    ...

def mom(df:pd.DataFrame):
    ...


def main():
    db_path = 'data/database.db'
    table_name = 'clean_sales_data'

    df = read_df_from_db(db_path, table_name)
    # in dashboard, have a filter for year/ month 


    # genearl summary 
    # YoY MoM revenue 
    # px.bar(sales_overview_monthly, 
    #        x=['Year', 'Month'], 
    #        y='Monthly Earnings',
    #             labels={'value': 'Earnings', 'variable': 'Metric'},
    #             # title="Earnings Trend with Moving Average"
    #             ).show()
    


    # time series related
    earnings_trend(df)
    moving_average_plot(df)
    # by weekday
    print('t')

    # analysis for equipment
    ## using rate (in terms of time)

    # customer analysis


if __name__ == '__main__':
    main()