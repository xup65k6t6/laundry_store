
from datetime import datetime, timedelta
from dateutil import parser

def get_all_dates(start_date: datetime = datetime(2023,9,1), end_date: datetime = datetime.today()) -> list:
    """
    Generate a list of date strings within the specified date range.

    Args
    ------
    - start_date (datetime): The start date of the range.
    - end_date (datetime): The end date of the range.

    Returns
    ------
    - list: A list of date strings in the format "YYYY/MM/DD" within the specified date range.

    Example usage
    ------
    >>> start_date = datetime(2023, 10, 30)
    >>> end_date = datetime.today()
    >>> date_range = get_all_dates(start_date, end_date)
    >>> print(date_range)
    or 
    >>> date_range2 = get_all_dates("2023/10/30", "2023/11/05")
    >>> print(date_range2)
    """
    today = datetime.today()
    # Parse start_date and end_date if they are provided as strings
    if isinstance(start_date, str):
        start_date = parser.parse(start_date)
    if isinstance(end_date, str):
        end_date = parser.parse(end_date)
    if end_date > today:
        end_date = today
    # Create an empty list to store the date strings
    date_list = []

    # Iterate through the date range and add each day to the list
    current_date = start_date
    while current_date <= end_date:
        formatted_date = current_date.strftime("%Y/%m/%d")
        date_list.append(formatted_date)
        current_date += timedelta(days=1)

    return date_list

def get_first_and_last_dates(year: int, month:int) -> tuple:
    """
    Get the first and last dates of a specified year and month.

    Args
    ------
        - year (int): The year.
        - month (int): The month.

    Returns
    ------
        - tuple: A tuple containing the first date (as YYYY/MM/DD) and the last date (as YYYY/MM/DD) of the specified year and month.

    Example usage
    ------
    >>> year = 2023
    >>> month = 10
    >>> first_date, last_date = get_first_and_last_dates(year, month)
    >>> print("First Date:", first_date)
    >>> print("Last Date:", last_date)
    """
    first_date = datetime(year, month, 1)
    if month == 12:
        last_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    return first_date.strftime("%Y/%m/%d"), last_date.strftime("%Y/%m/%d")

def get_all_year_months(start_year, start_month, end_year=None, end_month=None):
    """
    Generate a list of year and month pairs within the specified date range.

    Args
    ------
        - start_year (int): The starting year.
        - start_month (int): The starting month (1 to 12).
        - end_year (int, optional): The ending year. If not provided, the current year is used.
        - end_month (int, optional): The ending month (1 to 12). If not provided, the current month is used.

    Returns
    ------
        - list: A list of year and month pairs in the format (YYYY, MM) within the specified date range.

    Example usage
    ------
    >>> start_year = 2023
    >>> start_month = 4
    >>> end_year = 2024
    >>> end_month = 2
    >>> year_months_range = get_all_year_months(start_year, start_month, end_year, end_month)
    >>> print(year_months_range)
    """
    current_year = start_year
    current_month = start_month
    year_months = []

    if end_year is None or end_month is None:
        current_date = datetime.today()
        if end_year is None:
            end_year = current_date.year
        if end_month is None:
            end_month = current_date.month

    while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
        year_months.append((current_year, current_month))
        
        if current_month == 12:
            current_year += 1
            current_month = 1
        else:
            current_month += 1

    return year_months