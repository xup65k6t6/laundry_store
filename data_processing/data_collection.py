import time
import re 
import pandas as pd
import sqlite3
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys
from pathlib import Path
# Dynamically find the project root and add it to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from util.time_select import get_first_and_last_dates, get_all_dates, get_all_year_months

load_dotenv()

def get_chrome_driver():
    try:
        driver = webdriver.Chrome()
    except:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver

def get_data(driver, conn):
    start_y = 2023
    start_m = 11
    for y, m in get_all_year_months(start_year= start_y, start_month= start_m):
        start_date, end_date = get_first_and_last_dates(y, m)
        # 3. select by month 
        driver.find_element(By.ID, 'startDate').click()
        driver.find_element(By.ID, 'startDate').clear()
        driver.find_element(By.ID, 'startDate').send_keys(f"{start_date}")
        driver.find_element(By.ID, 'endDate').click()
        driver.find_element(By.ID, 'endDate').clear()
        driver.find_element(By.ID, 'endDate').send_keys(f"{end_date}")
        driver.find_element(By.ID, 'query').send_keys(Keys.RETURN)
        time.sleep(6)
        # 4. scrape every detail transactions
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for date in get_all_dates(start_date, end_date):
            if date not in str(soup) or date in cached_date:
                continue
            wait = WebDriverWait(driver = driver,timeout= 20, poll_frequency=2)
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'td[title="{date}"]')))
            element.click()
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            table = soup.find('table', id = "detailGrid")
            rows = table.find_all(
                'tr', 
                class_=re.compile(r'ui-widget-content jqgrow ui-row-ltr'), 
                # id=re.compile(r'[A-Z]{2}\d_[A-Z]{2}[\dA-Z]')
                )
            # Create a list to store the row data
            data = []
            # Extract data from the filtered rows
            for row in rows:
                row_data = [cell.get_text(strip=True) for cell in row.find_all('td')]
                data.append(row_data)
            # Create a Pandas DataFrame
            df = pd.DataFrame(data, columns=['Time', 'Equipment', 'Channel', 'Amount'])
            df['Time'] = pd.to_datetime(f'{date} ' + df['Time'], format='%Y/%m/%d %H:%M')
            df.to_sql('sales_data', conn, if_exists='append', index=False)
            conn.commit()
            driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Close"]').click()
            print(f"Saved data on {date}")
            time.sleep(5)


    # 6. Don't forget to log out (menu-logout-list logout)
    driver.find_element(By.CSS_SELECTOR, '.menu-icon').click()
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, 'div[href="/user/logout"]').click()
    driver.find_element(By.CLASS_NAME, "k-button.k-primary").click()


def main(db_path):

    my_username = os.getenv('USERNAME')
    my_password = os.getenv('PASSWORD')
    url = os.getenv('LOGIN_URL')
    # save_path = os.path.join(os.getcwd(), 'data')
    # db_file = os.path.join(save_path,'database.db')
    db_file = db_path

    driver = get_chrome_driver()
    driver.get(url)
    # driver.maximize_window()
    print(driver.title)

    # Find and fill in the login form
    username = driver.find_element(By.NAME, 'userId') 
    password = driver.find_element(By.NAME, "password") 

    username.send_keys(my_username) 
    password.send_keys(my_password) 

    # log in
    password.send_keys(Keys.RETURN)
    print('Logged In')
    # Wait for a few seconds to ensure the page loads
    time.sleep(5)

    print(driver.current_url)
    # Now that you're logged in, you can scrape data using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Your scraping code here (e.g., find and extract data from the soup)

    # 1. go into menu-icon
    driver.find_element(By.CSS_SELECTOR, '.menu-icon').click()
    time.sleep(3)
    # 2. go to revenue page
    driver.find_element(By.CSS_SELECTOR, 'div[href="/owner/revenue"]').click()
    time.sleep(3)
    print(driver.current_url)

    # cache from database by date
    # save all dates from datebase, list unique dates, exclude from scarping
    conn = sqlite3.connect(db_file)
    # Check if the table 'sales_data' exists
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales_data'")
    table_exists = cursor.fetchone() is not None
    if table_exists:
        db_df = pd.read_sql(""" SELECT * FROM sales_data """,
                            con=conn,
                            parse_dates='Time')
        cached_date = db_df['Time'].dt.strftime("%Y/%m/%d").unique().tolist()
    else:
        cached_date = []
        print("Table 'sales_data' does not exist. Skipping the operation.")

    try:
        get_data(driver=driver, conn= conn)
    except Exception as e:
        print(f"Err: {e} at line {e.__traceback__.tb_lineno}")
        pass
    finally:
        conn.close()
        # Close the browser
        driver.quit()

if __name__ == '__main__':
    main()
