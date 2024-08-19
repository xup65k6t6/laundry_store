
import re
import sqlite3
import numpy as np
import pandas as pd

def read_df_from_db(db_path, table_name= 'sales_data'):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f""" SELECT * FROM {table_name} """,
                        con= conn,
                        parse_dates='Time')
    conn.close()
    return df

def db2excel(excel_path:str, db_path: str = None, df:pd.DataFrame = None ):
    if df is None:
        df = read_df_from_db(db_path, 'sales_data')
    df.to_excel(excel_path, sheet_name='Sheet1', index=False, )


def add_date_columns(df:pd.DataFrame):
    """
    Add date columns: Date, Year, Month, Weekday, Day
    """
    df['Date'] = df['Time'].dt.strftime("%Y/%m/%d")
    df['Year'] = df['Time'].dt.year
    df['Month'] = df['Time'].dt.month
    df['Weekday'] = df['Time'].dt.weekday
    df['Day'] = df['Time'].dt.day

    return df


def correct_datatypes(
        df:pd.DataFrame, 
        numeric_colmns: list = [],
        date_columns: list = []
        ):
    """
    Correct the data types of the columns
    """
    for col in numeric_colmns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

def split_equipment(equipment_name):
    match = re.match(r'【(\d+)([上下]?)】(.+)', equipment_name)
    if match:
        return match.groups()
    else:
        return (np.nan, np.nan, equipment_name)

def categorize_equipment(equipment_type):
    if '洗' in equipment_type:  # If it contains '洗' (wash)
        if '中' in equipment_type:
            return 'wash', 'medium'
        elif '大' in equipment_type:
            return 'wash', 'large'
        else:
            return 'wash', np.nan
    elif '烘衣' in equipment_type:
        return 'dry', 'large'
    elif '儲值 / 兌幣機' in equipment_type:
        return 'money changer', np.nan
    elif '販賣機' in equipment_type:
        return 'vending machine', np.nan
    else:
        return 'others', np.nan


def clean_equipment_column(df):
    df[['Equipment_ID', 'Equipment_Location', 'Equipment_Type']]    = df['Equipment'].apply(split_equipment).apply(pd.Series)
    df['Equipment_Location']                                        = df['Equipment_Location'].replace({'上': 'Up', '下': 'Down', '': np.nan})
    df[['Equipment_Category', 'Wash_Scale']]                        = df['Equipment_Type'].apply(categorize_equipment).apply(pd.Series)

    return df

def main():
    db_path = 'data/database.db'
    table_name = 'sales_data'
    
    df = read_df_from_db(db_path, table_name)
    db2excel(excel_path = 'data/raw_sales_data.xlsx', df = df)
    df[['Amount', 'Unit']] = df['Amount'].str.extract('(-?\d+)(\D+)') # split unit
    df = correct_datatypes(df, numeric_colmns= ['Amount'], date_columns= ['Time'])
    df = add_date_columns(df)
    df = clean_equipment_column(df)
    db2excel(excel_path = 'data/clean_sales_data.xlsx', df = df)

if __name__ == "__main__":
    main()


